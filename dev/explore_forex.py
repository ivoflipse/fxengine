import psycopg2 as db_driver
import pandas.io.sql as psql
import pandas as pd
import numpy as np
# from qsforex.data import average_spreads
conn = db_driver.connect(host="localhost",
                         dbname="forex",
                         user="oxylo",
                         password="root")


def get_data(market, start_date, end_date, start_hour, end_hour, conn):
    """ Get data from Postgresql database.
    """
    print "Loading historical data...",
    query = """SELECT dtime, rate_open, rate_high, rate_low, rate_close
               FROM tbl_forexite
               INNER JOIN tbl_currency_pair CP ON ticker_id = CP.id
               WHERE CP.ticker = %(market)s
               AND dtime BETWEEN %(start_date)s AND %(end_date)s
               AND EXTRACT(hour from dtime) BETWEEN %(start_hour)s AND %(end_hour)s
               """
    df = psql.read_sql(query, conn,
                       params={'market': market,
                               'start_date': start_date,
                               'end_date': end_date,
                               'start_hour': start_hour,
                               'end_hour': end_hour})
    print "OK"
    return df.set_index('dtime')


def create_columns_names(label, n):
    """ Returns a list with n subsequent labels, i.e. ['label0', 'label1', ... 'labeln-1']
    """
    col_names = [label + str(colnr) for colnr in range(n)]
    return col_names


def recover_missing_categories(df):
    """
    Returns given df recovering missing combinations of the index columns.

    Parameters:
    ----------
    df: dataframe with (multi)index.
    """
    levels = df.index.levels
    names = df.index.names
    m = pd.MultiIndex.from_product(levels, names=names)
    df = df.reindex(m)
    return df

# input variables:
market = 'EURZAR'
price = 'rate_open'
start_date = '2015-11-01 00:00:00'
end_date = '2016-04-30 23:59:00'
start_hour = -99
end_hour = 99
sampling_interval = '15Min'
pattern_length = 3
show_results_per = 'W'

currency_pairs = ["AUDCAD", "AUDCHF", "AUDJPY", "AUDNZD", "AUDUSD",
                  "CADCHF", "CADJPY", "CHFJPY", "EURAUD", "EURCAD",
                  "EURCHF", "EURGBP", "EURJPY", "EURNZD", "EURRUB",
                  "EURSGD", "EURUSD", "EURZAR", "GBPAUD", "GBPCAD",
                  "GBPCHF", "GBPJPY", "GBPNZD", "GBPUSD", "NZDCAD",
                  "NZDCHF", "NZDJPY", "NZDUSD", "USDCAD", "USDCHF",
                  "USDCZK", "USDDKK", "USDHUF", "USDJPY", "USDNOK",
                  "USDPLN", "USDRUB", "USDSEK", "USDSGD", "USDTRY",
                  "USDZAR", "XAGEUR", "XAGUSD", "XAUEUR", "XAUUSD",
                  "USDHKD", "USDMXN", "EURHKD", "EURMXN", "EURTRY"]

output_df = pd.DataFrame()


for currenncy_pair in currency_pairs:
    print "------- currency pair %s -------" % currenncy_pair
    df = get_data(currenncy_pair, start_date, end_date, start_hour, end_hour, conn)
    # df.to_csv('/home/pieter/projects/quantfxengine/dev/outfile.csv', sep=';', index=True)
    df_resampled = df.resample(rule=sampling_interval).first().dropna(axis=0, how='any')

    rates = pd.DataFrame(df_resampled[price]).to_period(freq=show_results_per)

    for colnr in range(pattern_length):
        rates[colnr] = rates[price].shift(-colnr - 1)

        delta_headers = create_columns_names('delta', pattern_length)
    pip_headers = create_columns_names('pip', pattern_length)
    differences = rates.diff(periods=1, axis=1).iloc[:-pattern_length, 1:]
    differences.columns = delta_headers

    out_temp = (differences > 0).copy(deep=True)
    differences.columns = pip_headers
    out = pd.concat([differences, out_temp], axis=1)

    out['ones'] = 1
    out.reset_index(inplace=True)
    out2 = out.groupby(['dtime'] + delta_headers).sum()
    pips_change = 10000 * out2[pip_headers].div(out2.ones, axis='index')
    ones_and_pips_change = pd.concat([out2['ones'], pips_change[pip_headers[-1]]], axis=1)

    recovered = recover_missing_categories(ones_and_pips_change)

    last_delta = delta_headers[-1]
    recovered.reset_index(last_delta, inplace=True)
    result = recovered.pivot(columns=last_delta)
    result.columns = ['ntimes_down', 'ntimes_up', 'pips_down', 'pips_up']

    new_level_order = range(1, pattern_length) + [0]

    prob_up = result['ntimes_up'] / (result['ntimes_down'] + result['ntimes_up'])
    result['prob_up'] = 100 * prob_up.map(lambda x: round(x, 3))
    result = result.reorder_levels(order=new_level_order, axis=0)
    result.sortlevel(level=0, axis=0, inplace=True)
    result['difference'] = result['ntimes_up'] - result['ntimes_down']

    grp = result.groupby(level=delta_headers[:-1])
    end_result = pd.concat([grp['difference'].agg([np.mean, np.std, 'count']),
                           grp['pips_down'].agg([np.mean, np.std]),
                           grp['pips_up'].agg([np.mean, np.std]),
                           grp['prob_up'].agg([np.mean, np.std])], axis=1)
    end_result.columns = ['n_up_minus_down', 'std_ntimes', 'count', 'pips_down', 'std_pdown', 'pips_up', 'std_pup',
                          'prob_up', 'std_prob']
    end_result['t_value'] = end_result['n_up_minus_down'] / (end_result['std_ntimes'] / end_result['count'].map(lambda x: np.sqrt(x)))

    end_result['currency_pair'] = currenncy_pair

    selection = end_result[((np.abs(end_result['t_value']) > 3) & (np.abs(end_result['prob_up'] - 50) > 5))]
    output_df = pd.concat([output_df, selection])

writer = pd.ExcelWriter('output.xlsx')
output_df.to_excel(writer, 'uitvoer')
writer.save()
