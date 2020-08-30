from config import db_config
import pymysql
import sys
try:
    print ("SQL CONNECTION")
    conn = pymysql.connect(host=db_config[0], user=db_config[1], passwd=db_config[2], db=db_config[3],
                           connect_timeout=10, cursorclass=pymysql.cursors.DictCursor)
except Exception as e:
    print("Unable to connect to db")
    sys.exit()

cur = conn.cursor()