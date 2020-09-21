import argparse
from purpleair import *


try:
    pt = PurpleTwitter(default_img='aqi_levels.jpg')
except Exception as e:
    print("Failed to initialize Twitter client", e)


def main(mode):

    sensors = get_sensors()
    print(f"Checking {len(sensors)} sensors")

    update_readings(sensors)
    alerts = []
    warnings = []

    # Get sensor readings, update database, categorize alerts
    for each in sensors:
        sensor = sensors[each]
        sensor.confirm_context()

        if sensor.offline is False:
            sensor.insert_reading()

            if sensor.reading.aqi_level.color != sensor.status:

                alerts.append(sensor)
                sensor.update_status()

            if sensor.status != 'Green':
                warnings.append(sensor)

    print("Warnings: ", warnings)
    print("Alerts", alerts)

    if mode == 'status':
        tweet_network_status(sensors)

    if mode == 'alerts':
        tweet_alerts(alerts)

    if mode == 'warnings':
        tweet_warnings(warnings)

    if mode == 'readings':
        pass


def tweet_network_status(sensors):
    try:
        img = screenshot()
    except Exception as e:
        print("Failed to capture screenshot: ", e)
        img = pt.default_img

    intro = "CURRENT PM2.5 AQI (10 MIN AVG)"
    lines = [f"\n {sensors[each].twitter_label}: {sensors[each].reading.ten_minute_aqi} ({sensors[each].status})"
             for each in sensors
             if sensors[each].send_tweets is True and sensors[each].offline is False]

    tweets = split_tweets(intro, lines)
    pt.send_tweets(tweets, img)


def tweet_alerts(alerts):

    for sensor in alerts:

        if sensor.status == 'Green':
            alert = f"""
{sensor.twitter_label} has returned to status GREEN.
Current AQI: {sensor.reading.ten_minute_aqi}
\n\n{sensor.reading.aqi_level.description} """
        else:
            alert = \
            f"""
AIR QUALITY ALERT: {sensor.twitter_label} 
Status: {sensor.status}
Current AQI: {sensor.reading.ten_minute_aqi}
\n\n{sensor.reading.aqi_level.description} """

        pt.send_tweets([alert], previous_tweet=sensor.twitter_thread)

        if sensor.status == 'Green':
            sensor.update_thread(None)
        elif pt.last_tweet is not None:
            sensor.update_thread(pt.last_tweet)


def tweet_warnings(warnings):
    try:
        img = screenshot()
    except Exception as e:
        print("Failed to capture screenshot: ", e)
        img = pt.default_img

    intro = "These warnings are still in effect: "
    lines = [f"\n {warnings[each].twitter_label}: {warnings[each].reading.ten_minute_aqi} ({warnings[each].status})"
             for each in warnings
             if warnings[each].send_tweets]

    tweets = split_tweets(intro, lines)
    pt.send_tweets(tweets, img)


help = """
Options: status, alerts, warnings, readings.
Default: 'readings' takes readings from all sensors and stops.

For all twitter-enabled sensors, 
'status' tweets a list of current 10 min avg and AQI color,
'alerts' tweets any sensors that have changed AQI color level,
'warnings' tweets a list of all sensors not in status green.   
"""

parser = argparse.ArgumentParser(description='Take readings and generate tweets from PurpleAir sensors.', formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--mode', type=str, help=help, default='readings')
parser.add_argument('--add_sensors', type=str)
args = parser.parse_args()

if args.add_sensors:
    new_sensors = args.add_sensors.split(',')
    for n in new_sensors:
        print(n)

main(args.mode)
