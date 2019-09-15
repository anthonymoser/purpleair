from config import db_config
import json
import pymysql
import sys
import aqi

try:
    print("SQL CONNECTION")
    conn = pymysql.connect(host=db_config[0], user=db_config[1], passwd=db_config[2], db=db_config[3],
                           connect_timeout=10)
except:
    print("Unable to connect to db")
    sys.exit()

cur = conn.cursor()


def get_reading(monitor):

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
            AND aq1.AQI IS NULL
            AND aq1.recorded_at - aq1.lastseen < 1000; 
        """

    cur.execute(sql, monitor)
    conn.commit()
    response = cur.fetchall()

    print("Processing ", len(response), " readings")
    sql2 = """
        UPDATE
            air_quality aq
        SET
            AQI = %(aqi)s
        WHERE
            aq.record_id = %(record_id)s 
            OR aq.record_id = %(record_id)s + 1
    """
    updates = []

    for r in response:

        myaqi = aqi.to_iaqi(aqi.POLLUTANT_PM25, r[0], algo=aqi.ALGO_EPA)
        update = {
            "aqi": myaqi,
            "record_id": r[3]
        }
        print(update)
        updates.append(update)
        cur.execute(sql2, update)
        conn.commit()

    # print("Updating values")
    # cur.executemany(sql2, updates)
    # conn.commit()


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


def handler():

    monitors = get_monitors()

    for m in monitors:
        print("Processing monitor: ", m)
        get_reading(m[0])


handler()
