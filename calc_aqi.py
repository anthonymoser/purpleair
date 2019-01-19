from config import db_config
import json
import pymysql
import sys
import aqi

try:
    print "SQL CONNECTION"
    conn = pymysql.connect(host=db_config[0], user=db_config[1], passwd=db_config[2], db=db_config[3],
                           connect_timeout=10)
except:
    print "Unable to connect to db"
    sys.exit()

cur = conn.cursor()


def get_reading(monitor):

    print " "
    print "Monitor ID: ", monitor

    sql = """
        SELECT
            (aq1.PM2_5Value + aq2.PM2_5Value) / 2 as channel_avg,
            aq1.label,
            from_unixtime(aq1.recorded_at),
            aq1.record_id
        FROM
            air_quality aq1
        JOIN
            air_quality aq2
        ON
            aq1.record_id + 1 = aq2.record_id
        WHERE
            aq1.ID = %s
        AND
            aq1.AQI IS NULL
        """

    cur.execute(sql, monitor)
    conn.commit()

    response = cur.fetchall()
    print response[0][1]

    sql2 = """
        UPDATE
            air_quality aq
        SET
            AQI = %s
        WHERE
            ( aq.record_id = %s OR aq.record_id = %s + 1)
    """

    for r in response:

        myaqi = aqi.to_iaqi(aqi.POLLUTANT_PM25, r[0], algo=aqi.ALGO_EPA)
        cur.execute(sql2, (myaqi, r[3], r[3]))
        conn.commit()

        print "Time: ", r[2], "AQI: ", myaqi


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


def handler():

    monitors = get_monitors()

    for m in monitors:

        get_reading(m[0])

    # myaqi = aqi.to_iaqi(aqi.POLLUTANT_PM25, '12', algo=aqi.ALGO_EPA)
    # print myaqi

handler()
