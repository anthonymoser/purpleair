from config import db_config
import requests
import json
import pprint
import pymysql
import sys


try:
    print "SQL CONNECTION"
    conn = pymysql.connect(host=db_config[0], user=db_config[1], passwd=db_config[2], db=db_config[3],
                           connect_timeout=10)
except:
    print "Unable to connect to db"
    sys.exit()

cur = conn.cursor()


def get_reading(monitor):

    base_url = "http://purpleair.com/json?show="

    print "Getting sensor reading from monitor ", monitor
    r = requests.get(base_url + str(monitor))

    print r
    print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',', ': '))

    reading = r.json()
    return reading['results']


def get_monitors():

    sql = """
        SELECT
            id
        FROM
            air_monitors
        WHERE
            right(label,2) != " B"
    """

    cur.execute(sql)
    monitors = cur.fetchall()
    return monitors


def insert_reading(reading):

    sql = """
        INSERT INTO
            air_quality(recorded_at, AGE, A_H, DEVICE_BRIGHTNESS, DEVICE_FIRMWAREVERSION, DEVICE_LOCATIONTYPE, \
                        Flag, Hidden, ID, Label, LastSeen, LastUpdateCheck, Lat, Lon, PM2_5Value, ParentID, RSSI, State, Stats, \
                        THINGSPEAK_PRIMARY_ID, THINGSPEAK_PRIMARY_ID_READ_KEY, THINGSPEAK_SECONDARY_ID, THINGSPEAK_SECONDARY_ID_READ_KEY, \
                        Type, Uptime, Version, humidity, is_owner, pressure, temp_f)
        VALUES(
            UNIX_TIMESTAMP(NOW()),
            %(AGE)s,
            %(A_H)s,
            %(DEVICE_BRIGHTNESS)s,
            %(DEVICE_FIRMWAREVERSION)s,
            %(DEVICE_LOCATIONTYPE)s,
            %(Flag)s,
            %(Hidden)s,
            %(ID)s,
            %(Label)s,
            %(LastSeen)s,
            %(LastUpdateCheck)s,
            %(Lat)s,
            %(Lon)s,
            %(PM2_5Value)s,
            %(ParentID)s,
            %(RSSI)s,
            %(State)s,
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
            %(temp_f)s
        )
    """

    for r in reading:

        print json.dumps(r, sort_keys=True, indent=4, separators=(',', ': '))

        try:
            cur.execute(sql, r)
            conn.commit()
        except Exception as e:
            print "Unable to insert reading"
            print e


def handler():

    monitors = get_monitors()

    for m in monitors:

        print "Getting readings from monitor ", m[0]
        reading = get_reading(m[0])
        insert_reading(reading)


handler()
