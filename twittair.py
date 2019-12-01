from config import db_config, twitter_config as tc, home_directory
import pymysql
import sys
from collections import namedtuple
import tweepy
import aqi
from grab_screenshot import screenshot
import purpleair


try:
    # print ("SQL CONNECTION")
    conn = pymysql.connect(host=db_config[0], user=db_config[1], passwd=db_config[2], db=db_config[3],
                           connect_timeout=10)
except Exception as e:
    print("Unable to connect to db")
    sys.exit()


cur = conn.cursor()
Reading = namedtuple('Reading', 'id label field A B avg time pct_diff aqi aqi_level')
AQI_level = namedtuple('AQI_level', 'lower upper color description')

# Authenticate to Twitter
auth = tweepy.OAuthHandler(tc['CONSUMER_KEY'], tc['CONSUMER_SECRET'])
auth.set_access_token(tc['ACCESS_TOKEN'], tc['ACCESS_TOKEN_SECRET'])

# Create API object
api = tweepy.API(auth)

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")


def get_aqi_level(myaqi)->namedtuple:

    aqi_levels = [
        AQI_level(lower=0, upper=51, color='Green', description='Air quality is considered satisfactory, and air pollution poses little or no risk.'),
        AQI_level(lower=51, upper=101, color='Yellow',
                  description='Air quality is acceptable; however, if they are exposed for 24 hours there may be a moderate health concern for a very small number of people who are unusually sensitive to air pollution.'),
        AQI_level(lower=101, upper=151, color='Orange',
                  description='Members of sensitive groups may experience health effects if they are exposed for 24 hours. The general public is not likely to be affected with 24 hours of exposure.'),
        AQI_level(lower=151, upper=201, color='Red',
                  description='Everyone may begin to experience health effects if they are exposed for 24 hours; members of sensitive groups may experience more serious health effects with 24 hours of exposure.'),
        AQI_level(lower=201, upper=300, color='Purple', description='Everyone may begin to experience health effects if they are exposed for 24 hours.')
    ]

    for level in aqi_levels:
        if level.lower <= myaqi < level.upper:
            return level


def get_reading(field:str, monitor_id:int):

    sql = """
        SELECT
            ch_a.label,
            ch_a.""" + field + """,
            ch_b.""" + field + """,
            FROM_UNIXTIME(ch_a.recorded_at)
        FROM
            air_quality ch_a
        JOIN
            air_quality ch_b
        ON
            ch_a.recorded_at = ch_b.recorded_at
            AND ch_b.id = ch_a.id + 1
        WHERE
            ch_a.id = %(monitor_id)s
            AND ch_a.LastSeen > UNIX_TIMESTAMP(NOW() - INTERVAL 20 MINUTE)
        ORDER BY
            ch_a.recorded_at DESC
        LIMIT 1
    """

    bind = {
        "field": field,
        "monitor_id": monitor_id
    }

    cur.execute(sql, bind)
    response = cur.fetchone()

    try:
        # If one channel or the other is malfunctioning and reading zero, take the AQI value of the good channel
        if response[1] == 0:
            myaqi = aqi.to_iaqi(aqi.POLLUTANT_PM25, response[2], algo=aqi.ALGO_EPA)
        if response[2] == 0:
            myaqi = aqi.to_iaqi(aqi.POLLUTANT_PM25, response[1], algo=aqi.ALGO_EPA)

        # If they both have values, average them
        if response[1] > 0 and response[2] > 0:
            myaqi = aqi.to_iaqi(aqi.POLLUTANT_PM25, (response[1] + response[2])/2, algo=aqi.ALGO_EPA)

        data = Reading(
            id=         monitor_id,
            label=      response[0],
            field=      field,
            A=          response[1],
            B=          response[2],
            avg=        ( response[1] + response[2] )/2,
            time=       response[3],
            pct_diff=   (response[1] - response[2]) / response[1],
            aqi=        myaqi,
            aqi_level=  get_aqi_level(myaqi)
        )
    except:
        data = None

    return data


def get_readings(field:str, monitors:list)->list:

    readings = []

    for m in monitors:

        reading = get_reading(field, m)

        if reading:

            # If Channel A and Channel B are more than 30% different, don't include, the monitor may be malfunctioning
            if reading.pct_diff > .3 and reading.A > 20 and reading.B > 0:
                print("This monitor may be malfuctioning")
                print(reading)
                continue
            else:
                readings.append(reading)

    return readings


def get_monitors()->list:

    sql = """
        SELECT
            id
        FROM
            air_monitors
        WHERE
            channel='A'
    """

    cur.execute(sql)
    monitors = cur.fetchall()
    return monitors


def split_tweets(intro:str, lines:list)->list:
    # Splits updates into chunks of 260 characters or less
    tweets = []
    message = intro + " "

    for line in lines:

        if len(message + line) > 260:
            tweets.append(message)
            message = intro + line
        else:
            message += line

    tweets.append(message)
    return tweets


def send_tweets(tweets:list, img:str = (home_directory + 'air_levels.jpg'), previous_tweet:str = None):

    for t in tweets:

        if previous_tweet:
            api.update_with_media(filename=img, status=t, in_reply_to_status_id=previous_tweet)
        else:
            api.update_with_media(filename=img, status=t)

        previous_tweet = get_last_tweet()


def get_last_tweet():

    last_tweet = api.user_timeline('@swsideair', count=1)
    return last_tweet[0].id


def set_thread(monitor_id:int, tweet_id:str = None):

    sql = """
        UPDATE
            air_monitors
        SET
            thread = %s
        WHERE
            id = %s
    """
    cur.execute(sql, (tweet_id, monitor_id))
    conn.commit()


def get_thread(monitor_id:int)->str:

    sql = """
        SELECT
            thread
        FROM
            air_monitors
        WHERE
            id = %s
    """
    cur.execute(sql, monitor_id)
    conn.commit()
    tweet_id = cur.fetchone()
    print(tweet_id)
    return tweet_id[0]


def compose_alert_tweet(reading:namedtuple)->str:

    if reading.aqi_level.color == 'Green':
        msg = reading.label + " has returned to status GREEN."
        msg += "\n" + "Current AQI: " + str(reading.aqi)
        msg += "\n\n" + reading.aqi_level.description

    else:
        msg = "AIR QUALITY ALERT: \n" + reading.label
        msg += "\n" + "Status: " + reading.aqi_level.color
        msg += "\n" + "Current AQI: " + str(reading.aqi)
        msg += "\n\n" + reading.aqi_level.description

    return msg


def check_monitor_status(reading):

    sql = """
        SELECT
            status
        FROM
            air_monitors
        WHERE
            id = %s
    """

    cur.execute(sql, reading.id)
    conn.commit()
    status = cur.fetchone()

    if status[0] != reading.aqi_level.color:
        update_monitor_status(reading)
        update_status_log(reading, status[0])
        return True
    else:
        return False


def update_status_log(reading:namedtuple, old_status:str):

    sql = """
        INSERT INTO
            status_log(monitor_id, time, old_status, new_status, AQI)
        VALUES (
            %(monitor_id)s,
            UNIX_TIMESTAMP(NOW()),
            %(old_status)s, 
            %(new_status)s,
            %(aqi)s 
            )
    """
    bind = {
        "monitor_id": reading.id,
        "old_status": old_status,
        "new_status": reading.aqi_level.color,
        "aqi":        reading.aqi
    }

    cur.execute(sql, bind)
    conn.commit()


def update_monitor_status(reading):

    sql = """
        UPDATE
            air_monitors
        SET
            status = %s,
            last_status_change = UNIX_TIMESTAMP(NOW())
        WHERE
            id = %s
    """

    cur.execute(sql, (reading.aqi_level.color, reading.id))
    conn.commit()


def get_regular_update(readings:list)->list:

    lines = [ "\n" + r.label + ": " + str(r.aqi) + " (" + str(r.aqi_level.color) + ")"
              for r in readings if r is not None
              and r.aqi_level is not None ]
    return lines


def get_alerts(readings):

    # This alert system starts a thread of alerts for a given monitor when it hits Orange, ending when it returns to Green.

    triggers = ['Green', 'Orange', 'Red', 'Purple']

    for r in readings:

        changed = check_monitor_status(r)

        if changed and r.aqi_level.color in triggers:

            alert = compose_alert_tweet(r)
            thread = get_thread(r.id)

            # If there's a previous alert tweet for this monitor, tweet this as a reply
            if thread:

                send_tweets([alert], previous_tweet=thread)

                # If this is a return to Green, end the thread by setting the last tweet ID to null
                if r.aqi_level.color == 'Green':
                    tweet_id = None
                else:
                    tweet_id = get_last_tweet()

                # Update the last tweet ID of the thread
                set_thread(monitor_id=r.id, tweet_id=tweet_id)

            # If there's no previous alert, and this isn't a return to Green, send it as a new tweet.
            # This means if a monitor goes to Yellow and then back to Green without ever hitting Orange, there will be no alerts.
            else:
                if r.aqi_level.color != 'Green':
                    alert = compose_alert_tweet(r)
                    send_tweets([alert])
                    set_thread(monitor_id=r.id, tweet_id=get_last_tweet())


def get_current_warnings()->list:

    sql = """
        SELECT
            id
        FROM
            air_monitors
        WHERE
            status IN('Orange', 'Red', 'Purple')
            AND status IS NOT NULL
            AND last_status_change > UNIX_TIMESTAMP(NOW() - INTERVAL 2 DAY)
    """

    cur.execute(sql)
    monitors = cur.fetchall()

    field = 'current_pm_2_5'
    readings = get_readings(field, monitors)

    lines = [ "\n" + r.label + " (" + r.aqi_level.color + ") AQI: " + str(r.aqi) for r in readings]
    return lines


def get_all_measurements(monitor_id):

    fields = ['current_pm_2_5', '10_min_avg', '30_min_avg', '60_min_avg', '6_hr_avg', '24_hr_avg', '1_wk_avg']
    lines = []

    for f in fields:
        reading = get_reading(f, monitor_id)
        if reading:
            # If Channel A and Channel B are more than 30% different, don't include, the monitor may be malfunctioning
            if reading.pct_diff > .3 and reading.A > 20:
                continue
            else:
                lines.append("\n" + f + ": " + str(reading.aqi))

    return lines


def monitor_summary(monitor_id):

    reading = get_reading('current_pm_2_5', monitor_id)
    if reading:
        msg = "AQI Averages For " + reading.label+ ": "
        body = get_all_measurements(monitor_id)
        for b in body:
            msg += b
    else:
        msg = None

    return msg


def main():

    # Takes two command line arguments:
    # 'mode': update, alert, current_warnings
    # 'field': name of the measurement window to use (current_pm_2_5, 10_min_avg, 30_min_avg, 60_min_avg, 6_hr_avg, 24_avg, 1_week_avg)

    mode = sys.argv[1]
    try:
        field = sys.argv[2]
    except:
        field = "10_min_avg"


    img = screenshot()  # Obtain screenshot
    purpleair.handler() # Refresh Sensor Data

    monitors = get_monitors()
    readings = get_readings(field, monitors)

    if mode == "update":

        if field not in ['current_pm_2_5', '10_min_avg']:
            img = home_directory + 'air_levels.jpg'

        intro = "CURRENT PM2.5 AQI (" + field + "): "
        body = get_regular_update(readings)
        tweets = split_tweets(intro, body)
        for t in tweets:
            print(t)
        send_tweets(tweets, img)

    if mode == "alert":
        get_alerts(readings)

    if mode == "current_warnings":
        intro = "These warnings are still in effect (" + field + "):"
        body = get_current_warnings()
        if body:
            if field != 'current_pm_2_5':
                img = home_directory + 'air_levels.jpg'
            tweets = split_tweets(intro, body)
            for t in tweets:
                print(t)
            send_tweets(tweets, img)

    if mode == "averages":

        tweets = []

        for m in monitors:
            summary = monitor_summary(m)
            if summary:
                tweets.append(summary)

        for t in tweets:
            print(t)
            print("\n")

        send_tweets(tweets)

main()