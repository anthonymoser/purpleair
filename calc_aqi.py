from config import db_config
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
            aq1.entry_id,
            ROUND((aq1.`PM2.5` + aq2.`PM2.5`) / 2, 2) as channel_avg
        FROM
            purpleair_primary aq1
        JOIN
            purpleair_primary aq2
        ON
            aq1.entry_id = aq2.entry_id
            AND aq1.monitor_id + 1 = aq2.monitor_id
        WHERE
            aq1.monitor_id = %s
            AND aq1.AQI IS NULL
        LIMIT 1000
        """

    cur.execute(sql, monitor)
    conn.commit()
    response = cur.fetchall()

    print("Processing ", len(response), " readings")
    sql2 = """
        UPDATE
            purpleair_primary pp
        SET
            AQI = %(aqi)s
        WHERE
            pp.entry_id = %(entry_id)s 
            AND monitor_id IN (%(monitor_id)s, %(monitor_id)s + 1)
    """

    for r in response:

        try:
            myaqi = aqi.to_iaqi(aqi.POLLUTANT_PM25, r[1], algo=aqi.ALGO_EPA)
            update = {
                "aqi": myaqi,
                "entry_id": r[0],
                "monitor_id": monitor
            }
            print(update)
            # updates.append(update)
            cur.execute(sql2, update)
            conn.commit()
        except Exception as e:
            print("Error with row", r)
            print(e)

    return len(response)
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
        r = 1000
        while r == 1000:
            r = get_reading(m[0])


handler()
