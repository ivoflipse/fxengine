import psycopg2 as db_driver
import pandas.io.sql as psql
import pandas as pd
from datetime import date
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from pandas.tools.plotting import lag_plot
# from qsforex.data import average_spreads
conn = db_driver.connect(host="localhost",
                         dbname="forex",
                         user="oxylo",
                         password="root")


def get_data(name, start_date, end_date, conn):
    print "Loading historical data...",
    query = """SELECT dtime, rate_open, rate_high, rate_low, rate_close
               FROM tbl_forexite
               INNER JOIN tbl_currency_pair CP ON ticker_id = CP.id
               WHERE CP.ticker = %(p)s
               AND dtime BETWEEN %(start)s AND %(end)s
               """
    df = psql.read_sql(query, conn,
                       params={'p': name,
                               'start': start_date,
                               'end': end_date})
    print "OK"
    return df.set_index('dtime')

df = get_data('EURUSD', '2002-01-02 00:00:00', '2015-12-31 23:59:00', conn)
print "Ready reading data... writing to csv."
df.to_csv('/home/pieter/projects/quantfxengine/dev/outfile.csv', sep=';', index=True)
