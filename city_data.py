from config import db_config
import requests
import pymysql
import sys
from collections import namedtuple
import smtplib
import json

# Define the characteristics of a city data feed
Feed = namedtuple('Feed','id resource table arguments description')
base_url = 'https://data.cityofchicago.org/resource/'

# Connect to the database
try:
    conn = pymysql.connect(host=db_config[0], user=db_config[1], passwd=db_config[2], db=db_config[3], connect_timeout=10)
except Exception as e:
    print("Unable to connect to db")
    sys.exit()

cur = conn.cursor(pymysql.cursors.DictCursor)


def get_feeds()->list:

    feed_sql = """
        SELECT
            cdf.id,
            cdf.resource,
            cdf.table,
            cdf.description
        FROM
            city_data_feeds cdf
    """

    cur.execute(feed_sql)
    response = cur.fetchall()

    feeds = [

        Feed(
            id =        r['id'],
            resource =  r['resource'],
            table =     r['table'],
            arguments = get_arguments(r['id']),
            description=r['description']
        )

        for r in response
    ]

    return feeds


def get_arguments(feed_id:int) -> dict:

    arg_sql = f"""
        SELECT
            cdfa.argument,
            cdfa.value
        FROM
            city_data_feed_arguments cdfa
        WHERE
            cdfa.data_feed_id = {feed_id}
    """

    cur.execute(arg_sql)
    response = cur.fetchall()

    arguments = {r['argument']:r['value'] for r in response}

    return arguments


def get_column_names(table)->list:

    sql = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'pershing' AND TABLE_NAME = '{table}'"
    cur.execute(sql)
    response = cur.fetchall()
    columns = [ r['COLUMN_NAME'] for r in response if r['COLUMN_NAME'] != 'id']
    return columns


def refresh_feed(feed):

    columns = get_column_names(feed.table)
    values = [f'%({col})s' for col in columns]

    columns = ', '.join(columns)
    values = ', '.join(values)

    sql = f"INSERT INTO {feed.table} ({columns}) VALUES ({values})"
    url = base_url + feed.resource

    print(feed.description)
    response = requests.get(url, params=feed.arguments)
    response = response.json()

    for r in response:
        try:
            cur.execute(sql, r)
        except:
            continue

    conn.commit()


def get_record_count(table:str):

    sql = f"SELECT count(*) as rows FROM {table}"
    cur.execute(sql)
    response = cur.fetchone()
    conn.commit()
    return response['rows']


def send_email(message):

    from config import email_config as ec

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login( ec['user'], ec['password'] )
    s.sendmail("sender_email_id", "anthony.moser@gmail.com", message)
    s.sendmail("sender_email_id", "neighbors4environmentaljustice@gmail.com", message)
    s.quit()


def get_new_records(feed:namedtuple, record_count:int)->json:

    sql = f'SELECT * FROM {feed.table} ORDER BY id DESC LIMIT {record_count}'
    cur.execute(sql)
    new_records = cur.fetchall()
    body = json.dumps(new_records, indent=4)
    return body


def handler():

    # Retrieve list of configured data feeds
    feeds = get_feeds()

    for f in feeds:

        # Check the existing number of records
        first_count = get_record_count(f.table)

        # Check the city database for new records and import them
        refresh_feed(f)

        # If new records were imported, send an email with JSON of the new records
        second_count = get_record_count(f.table)
        new_records = second_count - first_count

        if second_count != first_count:
            print(second_count - first_count, "new records added.")
            message = f'Subject: {str(new_records)} new records added from {f.description} \n\n'
            message += get_new_records(f, new_records)
            send_email(message)
        else:
            print("No new records found.")


handler()


