import pymysql
import numpy as np
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=UserWarning)

def _MYSQL(query):
    conn = pymysql.connect(host='localhost', user='root',
    passwd='test127', db='scrape',
    port=3306)
    data = pd.read_sql_query(query, conn)
    conn.close()
    return data

def _MYSQL_INSERT(query):
    try:
        conn = pymysql.connect(host='localhost', user='root',
        passwd='test127', db='scrape',
        port=3306)
        mycursor  = conn.cursor()
        mycursor.execute(query)
        conn.commit()
        conn.close()
    except Exception:
        print(Exception.value)
  