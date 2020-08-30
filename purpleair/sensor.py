import aqi
from .db import cur, conn
from decimal import *

class PurpleAirSensor:

    id = 0
    reading = None
    context = {
        "name": None,
        "location_type": None,
        "latitude": None,
        "longitude": None,
        "altitude": None,
        "channel_state": None,
        "channel_flags": None
    }
    context_id =  0
    twitter_label = None
    send_tweets = 0
    twitter_thread = None

    status = None
    last_seen = None

    def __init__(self, data:dict):
        self.id             = data.get('id')
        self.context_id     = data.get('context_id', None)
        self.context        = { field: data.get(field, None) for field in self.context }
        self.twitter_label  = data.get('twitter_label', None)
        self.send_tweets    = data.get('send_tweets', None)
        self.twitter_thread = data.get('twitter_thread', None)

    def confirm_context(self):
        if self.context_changed():
            self.update_context()
            self.insert_context()

    def context_changed(self):
        return self.context != self.reading.context

    def update_context(self):
        # The new context comes from the latest sensor reading
        new_context = self.reading.context

        # Confirm that there are no missing values
        for n in new_context:
            if new_context[n] is None:
                raise Exception('Missing context')

        self.context = self.reading.context

    def insert_context(self):
        insert_context_sql = \
            f"""
            INSERT INTO
                contexts(
                    sensor_id, 
                    name, 
                    location_type, 
                    latitude, 
                    longitude, 
                    altitude, 
                    channel_state,
                    channel_flags, 
                    context_created
                )
            VALUES
                ( 
                    {self.id}, 
                    "{self.context['name']}", 
                    "{self.context['location_type']}", 
                    {self.context['latitude']},
                    {self.context['longitude']}, 
                    {self.context['altitude']}, 
                    "{self.context['channel_state']}", 
                    "{self.context['channel_flags']}", 
                    NOW() 
                )
            """

        get_new_context_id_sql = \
            f"""
            SELECT
                max(id) as context_id
            FROM
                contexts
            WHERE
                sensor_id = {self.id}
            """

        cur.execute(insert_context_sql)
        conn.commit()

        cur.execute(get_new_context_id_sql)
        response = cur.fetchone()
        self.context_id = response['context_id']

        set_new_context_id_sql = \
            f"""
            UPDATE
                sensors
            SET
                context_id = {self.context_id}
            WHERE
                id = {self.id}
            """
        cur.execute(set_new_context_id_sql)
        conn.commit()

    def insert_reading(self):

        values = {
            "sensor_id":        self.id,
            "context_id":       self.context_id,
            "pm1.0":            self.reading.pm['1.0'],
            "pm2.5":            self.reading.pm['2.5'],
            "pm2.5_10minute":   self.reading.pm['2.5_10minute'],
            "pm2.5_30minute":   self.reading.pm['2.5_30minute'],
            "pm2.5_60minute":   self.reading.pm['2.5_60minute'],
            "pm2.5_6hour":      self.reading.pm['2.5_6hour'],
            "pm2.5_24hour":     self.reading.pm['2.5_24hour'],
            "pm10.0":           self.reading.pm['10.0'],
            "0.3_um_count":     self.reading.um_count['0.3'],
            "0.5_um_count":     self.reading.um_count['0.5'],
            "1.0_um_count":     self.reading.um_count['1.0'],
            "2.5_um_count":     self.reading.um_count['2.5'],
            "5.0_um_count":     self.reading.um_count['5.0'],
            "10.0_um_count":    self.reading.um_count['10.0'],
            "humidity":         self.reading.humidity,
            "temperature":      self.reading.temperature,
            "pressure":         self.reading.pressure,
            "voc":              self.reading.voc,
            "ozone1":           self.reading.ozone1,
            "ten_minute_aqi":   self.reading.ten_minute_aqi,
            "aqi_level":        self.reading.aqi_level.color,
            "time_stamp":       self.reading.time_stamp
        }

        insert_sql = \
            f"""
            INSERT INTO
                readings(
                    `sensor_id`,
                    `context_id`,
                    `pm1.0`,
                    `pm2.5`,
                    `pm2.5_10minute`,
                    `pm2.5_30minute`,
                    `pm2.5_60minute`,
                    `pm2.5_6hour`,
                    `pm2.5_24hour`,
                    `pm10.0`,
                    `0.3_um_count`,
                    `0.5_um_count`,
                    `1.0_um_count`,
                    `2.5_um_count`,
                    `5.0_um_count`,
                    `10.0_um_count`,
                    `humidity`,
                    `temperature`,
                    `pressure`,
                    `voc`,
                    `ozone1`,
                    `ten_minute_aqi`,
                    `aqi_level`,
                    `time_stamp`)
            VALUES
                (
                %(sensor_id)s,
                %(context_id)s,
                %(pm1.0)s,
                %(pm2.5)s,
                %(pm2.5_10minute)s,
                %(pm2.5_30minute)s,
                %(pm2.5_60minute)s,
                %(pm2.5_6hour)s,
                %(pm2.5_24hour)s,
                %(pm10.0)s,
                %(0.3_um_count)s,
                %(0.5_um_count)s,
                %(1.0_um_count)s,
                %(2.5_um_count)s,
                %(5.0_um_count)s,
                %(10.0_um_count)s,
                %(humidity)s,
                %(temperature)s,
                %(pressure)s,
                %(voc)s,
                %(ozone1)s,
                %(ten_minute_aqi)s,
                %(aqi_level)s,
                %(time_stamp)s
                )
            """
        cur.execute(insert_sql, values)
        conn.commit()

    def update_status(self):

        if self.status != self.reading.aqi_level.color:
            self.status = self.reading.aqi_level.color
            sql = f"""
                UPDATE
                    sensors
                SET
                    status = "{self.status}",
                    last_status_change = NOW()
                WHERE
                    id = {self.id}
            """
            cur.execute(sql)
            conn.commit()


class Reading:

    context = {
        "name": None,
        "location_type": None,
        "latitude": None,
        "longitude": None,
        "altitude": None,
        "channel_state": None,
        "channel_flags": None
    }

    pm = {
        "1.0": None,
        "2.5": None,
        "2.5_10minute": None,
        "2.5_30minute": None,
        "2.5_60minute": None,
        "2.5_6hour": None,
        "2.5_24hour": None,
        "10.0": None,
    }

    um_count = {
        "0.3": None,
        "0.5": None,
        "1.0": None,
        "2.5": None,
        "5.0": None,
        "10.0": None,
    }

    confidence      = None
    humidity        = None
    temperature     = None
    pressure        = None
    voc             = None
    ozone1          = None
    ten_minute_aqi  = None
    aqi_level       = None
    last_seen       = None
    time_stamp      = None

    def __init__(self, data:dict):
        self.sensor_id      = data.get('sensor_index', None)
        self.last_seen      = data.get('last_seen', None)
        self.confidence     = data.get('confidence', None)
        self.humidity       = data.get('humidity', None)
        self.temperature    = data.get('temperature', None)
        self.pressure       = data.get('pressure', None)
        self.voc            = data.get('voc', None)
        self.ozone1         = data.get('ozone1', None)

        self.context        = { field: data[field] for field in self.context }
        self.pm             = { field: data[f'pm{field}'] for field in self.pm }
        self.um_count       = { field: data[f'{field}_um_count'] for field in self.um_count }

        self.ten_minute_aqi = aqi.to_iaqi(aqi.POLLUTANT_PM25, self.pm['2.5_10minute'], algo=aqi.ALGO_EPA)
        self.aqi_level      = get_aqi_level(self.ten_minute_aqi)
        self.time_stamp     = data.get('time_stamp', None)

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class AQILevel:
    lower:int = 0
    upper:int = 0
    color:str = None
    description:str = None

    def __init__(self, data):
        self.lower = data.get('lower')
        self.upper = data.get('upper')
        self.color = data.get('color')
        self.description = data.get('description')

level_data = [
    {
        "lower": 0,
        "upper": 51,
        "color": "Green",
        "description": "Air quality is considered satisfactory, and air pollution poses little or no risk."
    },
    {
        "lower": 51,
        "upper": 101,
        "color": "Yellow",
        "description": "Air quality is acceptable; however, if they are exposed for 24 hours there may be a moderate health concern for a very small number of people who are unusually sensitive to air pollution."
    },
    {
        "lower": 101,
        "upper": 151,
        "color": "Orange",
        "description": "Members of sensitive groups may experience health effects if they are exposed for 24 hours. The general public is not likely to be affected with 24 hours of exposure."
    },
    {
        "lower": 151,
        "upper": 201,
        "color": "Red",
        "description": "Everyone may begin to experience health effects if they are exposed for 24 hours; members of sensitive groups may experience more serious health effects with 24 hours of exposure."
    },
    {
        "lower": 201,
        "upper": 300,
        "color": "Purple",
        "description": "Everyone may begin to experience health effects if they are exposed for 24 hours."
    },

]

aqi_levels = [AQILevel(level) for level in level_data]

def get_aqi_level(aqi_number):
    for level in aqi_levels:
        if level.lower <= aqi_number < level.upper:
            return level