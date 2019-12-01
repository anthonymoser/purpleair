from config import db_config
import requests
import json
import pymysql
import sys
import aqi
from datetime import datetime


try:
    # print ("SQL CONNECTION")
    conn = pymysql.connect(host=db_config[0], user=db_config[1], passwd=db_config[2], db=db_config[3],
                           connect_timeout=10)
except Exception as e:
    print("Unable to connect to db")
    sys.exit()

cur = conn.cursor()


def get_reading(monitor):

    base_url = "http://www.purpleair.com/json?show="
    r = requests.get(base_url + str(monitor))
    # print(json.dumps(r.json(), sort_keys=True, indent=4, separators=(',', ': ')))

    try:
        reading = r.json()
        return reading['results']
    except Exception as e:
        print(e)
        print("Failed to get reading from ", monitor)
        return None


def get_monitors():

    sql = """
        SELECT
            id
        FROM
            air_monitors
        WHERE
            channel = "A"
    """

    cur.execute(sql)
    monitors = cur.fetchall()
    return monitors


def insert_reading(reading):

    channel1 = """
        INSERT INTO
            air_quality(recorded_at, AGE, DEVICE_BRIGHTNESS, DEVICE_LOCATIONTYPE, \
                        Hidden, ID, Label, LastSeen, LastUpdateCheck, Lat, Lon, PM2_5Value, RSSI, Stats, \
                        THINGSPEAK_PRIMARY_ID, THINGSPEAK_PRIMARY_ID_READ_KEY, THINGSPEAK_SECONDARY_ID, THINGSPEAK_SECONDARY_ID_READ_KEY, \
                        Type, Uptime, Version, humidity, is_owner, pressure, temp_f, aqi, current_pm_2_5, 10_min_avg, 30_min_avg, 60_min_avg, 6_hr_avg, 24_hr_avg, 1_wk_avg)
        VALUES(
            UNIX_TIMESTAMP(NOW()),
            %(AGE)s,
            %(DEVICE_BRIGHTNESS)s,
            %(DEVICE_LOCATIONTYPE)s,
            %(Hidden)s,
            %(ID)s,
            %(Label)s,
            %(LastSeen)s,
            %(LastUpdateCheck)s,
            %(Lat)s,
            %(Lon)s,
            %(PM2_5Value)s,
            %(RSSI)s,
            %(Stats)s,
            %(THINGSPEAK_PRIMARY_ID)s,
            %(THINGSPEAK_PRIMARY_ID_READ_KEY)s,
            %(THINGSPEAK_SECONDARY_ID)s,
            %(THINGSPEAK_SECONDARY_ID_READ_KEY)s,
            %(Type)s,
            %(Uptime)s,
            %(Version)s,
            %(humidity)s,
            %(isOwner)s,
            %(pressure)s,
            %(temp_f)s,
            %(aqi)s,
            %(v)s,
            %(v1)s,
            %(v2)s,
            %(v3)s,
            %(v4)s,
            %(v5)s,
            %(v6)s
        )
    """

    channel2 = """
            INSERT INTO
                air_quality(recorded_at, AGE, Hidden, ID, Label, LastSeen, Lat, Lon, PM2_5Value, ParentID, Stats, \
                            THINGSPEAK_PRIMARY_ID, THINGSPEAK_PRIMARY_ID_READ_KEY, THINGSPEAK_SECONDARY_ID, THINGSPEAK_SECONDARY_ID_READ_KEY, \
                            is_owner, aqi, current_pm_2_5, 10_min_avg, 30_min_avg, 60_min_avg, 6_hr_avg, 24_hr_avg, 1_wk_avg)
            VALUES(
                UNIX_TIMESTAMP(NOW()),
                %(AGE)s,
                %(Hidden)s,
                %(ID)s,
                %(Label)s,
                %(LastSeen)s,
                %(Lat)s,
                %(Lon)s,
                %(PM2_5Value)s,
                %(ParentID)s,
                %(Stats)s,
                %(THINGSPEAK_PRIMARY_ID)s,
                %(THINGSPEAK_PRIMARY_ID_READ_KEY)s,
                %(THINGSPEAK_SECONDARY_ID)s,
                %(THINGSPEAK_SECONDARY_ID_READ_KEY)s,
                %(isOwner)s,
                %(aqi)s,
                %(v)s,
                %(v1)s,
                %(v2)s,
                %(v3)s,
                %(v4)s,
                %(v5)s,
                %(v6)s
            )
        """

    for r in reading:

        try:
            stats = json.loads(r['Stats'])
            r['v']  = stats['v']
            r['v1'] = stats['v1']
            r['v2'] = stats['v2']
            r['v3'] = stats['v3']
            r['v4'] = stats['v4']
            r['v5'] = stats['v5']
            r['v6'] = stats['v6']
            r['aqi']= aqi.to_iaqi(aqi.POLLUTANT_PM25, stats['v'], algo=aqi.ALGO_EPA)

            print(r['Label'], r['aqi'])

            # print(json.dumps(r, sort_keys=True, indent=4, separators=(',', ': ')))

            sql = channel2 if "ParentID" in r else channel1

            try:
                cur.execute(sql, r)
                conn.commit()
              #  print("Reading inserted")
            except Exception as e:
                print("Unable to insert reading")
                print(e)
        except Exception as e:
            print("Failed to insert readings")
            print(r)
            print(e)

def handler():

    monitors = get_monitors()
    print("Refreshing monitor data")

    for m in monitors:

        reading = get_reading(m[0])

        if reading:
            insert_reading(reading)

