import requests
from config import sensor_fields, purpleair_api_key
from .db import *
from .sensor import PurpleAirSensor, Reading
from decimal import Decimal
import time


def get_sensors()->dict:

    sql = """
        SELECT
            s.id, 
            s.context_id,
            s.status,
            s.last_seen,
            s.offline,
            c.name,
            c.location_type,
            c.latitude, 
            c.longitude, 
            c.altitude, 
            c.channel_state, 
            c.channel_flags,
            t.send_tweets,
            t.twitter_label,
            t.thread as twitter_thread
        FROM
            sensors s
        LEFT JOIN
            contexts c
        ON
            s.context_id = c.id
        LEFT JOIN
            twitter_sensors t
        ON
            t.sensor_id = s.id
    """

    cur.execute(sql)
    conn.commit()

    response = cur.fetchall()
    return { r['id']: PurpleAirSensor(r) for r in response }


def update_readings(sensors: dict):

    data = get_data(sensors)
    readings = parse_data(data)

    for r in readings:

        sensor = sensors[r.sensor_id]

        sensor.reading = r
        sensor.last_seen = r.last_seen
        sensor.update_last_seen()

        # If it's been more than 20 minutes since the sensor updated PurpleAir, mark it offline
        if sensor.last_seen < time.time() - 1200 and sensor.offline is False:
            sensor.mark_offline_as(True)

        # If it's been less than five minutes since the latest sensor update but the sensor is marked offline, change it online
        elif sensor.last_seen > time.time() - 300 and sensor.offline is True:
            sensor.mark_offline_as(False)


def get_data(sensors: dict):
    sensor_ids = [str(sensors[s].id) for s in sensors]
    sensor_ids = ','.join(sensor_ids)

    url = 'https://api.purpleair.com/v1/sensors'
    headers = {"x-api-key": purpleair_api_key}
    try:
        params = {
            "fields": ','.join(sensor_fields),
            "show_only": sensor_ids
        }
        response = requests.get(url, params=params, headers=headers)
    except KeyError as e:
        del(sensor_fields[e])
        get_data(sensors)

    return response.json()


def parse_data(response: dict) -> list:

    fields = response['fields']
    location_types = response['location_types']
    channel_states = response['channel_states']
    channel_flags = response['channel_flags']
    data = response['data']
    readings = []

    for d in data:
        sensor_data = dict(zip(fields, d))

        # Convert location type, channel states and channel flags from list indices to strings
        sensor_data['location_type'] = location_types[sensor_data['location_type']]
        sensor_data['channel_state'] = channel_states[sensor_data['channel_state']]
        sensor_data['channel_flags'] = channel_flags[sensor_data['channel_flags']]
        sensor_data['time_stamp'] = response['time_stamp']
        sensor_data['latitude'] = round(Decimal(sensor_data['latitude']), 4)
        sensor_data['longitude'] = round(Decimal(sensor_data['longitude']), 4)

        # Format sensor data into an instance of the Reading class
        readings.append(Reading(sensor_data))

    return readings


def add_sensors(sensor_list:list):

    for id in sensor_list:
        try:
            insert_sensor(id)
        except Exception as e:
            print(f'Failed to insert {id}.\n{e}')
            continue

    sensors = get_sensors()
    new_sensors = { id: sensors[id] for id in sensors if id in sensor_list}
    update_readings(new_sensors)

    for id in new_sensors:
        new_sensors[id].confirm_context()
        add_to_twitter(id)


def insert_sensor(sensor_id):
    sql = f"""
    INSERT IGNORE INTO 
        sensors(id)
    VALUES
        ({sensor_id})
    """
    cur.execute(sql)
    conn.commit()


def add_to_twitter(sensor_id):
    sql = f"""
        INSERT IGNORE INTO 
            twitter_sensors
        SELECT
            s.id as sensor_id,
            c.name as twitter_label,
            1 as send_tweets,
            null as thread
        FROM
            sensors s
        JOIN
            contexts c
        ON
            s.context_id = c.id
        LEFT JOIN
            twitter_sensors tw
        ON
            tw.sensor_id = s.id
        WHERE
            s.id = {sensor_id}"""
    cur.execute(sql)
    conn.commit()


