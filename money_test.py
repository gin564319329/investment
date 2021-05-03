from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def get_raw_data(index_id='0000300', date_start="20000101", date_end="20200320"):
    data_api = "http://quotes.money.163.com/service/chddata.html?code={}&start={}&end={}&fields=TCLOSE;HIGH;LOW;TOPEN;" \
               "LCLOSE;CHG;PCHG;VOTURNOVER;VATURNOVER".format(index_id, date_start, date_end)
    data_info = pd.read_csv(data_api, encoding='gb2312')
    # data = data_info.loc[(data_info.index > datetime.strptime(date_start, "%Y%m%d").strftime("%Y-%d-%m"))
    #                      & (data_info.index < datetime.strptime(date_end, "%Y%m%d").strftime("%Y-%d-%m"))]
    data_info = data_info.sort_values(by=['日期'], ascending=True).reset_index(drop=True)
    return data_info


def gen_cal_data(raw_data):
    cal_data = pd.DataFrame()
    cal_data['date'] = raw_data['日期']
    weekday_list = []
    day_list = []
    month_list = []
    year_list = []
    for da in raw_data['日期']:
        weekday_list.append(datetime.strptime(da, "%Y-%m-%d").weekday() + 1)
        day_list.append(datetime.strptime(da, "%Y-%m-%d").day)
        month_list.append(datetime.strptime(da, "%Y-%m-%d").month)
        year_list.append(datetime.strptime(da, "%Y-%m-%d").year)
    cal_data['year'] = year_list
    cal_data['month'] = month_list
    cal_data['day'] = day_list
    cal_data['weekday'] = weekday_list
    cal_data['price'] = raw_data['收盘价']
    return cal_data


def fixed_invest_by_week(weekday, df_market_data, money_amount):
    """未考虑节假日"""
    df_invest_data = df_market_data[df_market_data['weekday'] == weekday].copy()
    df_invest_data['money'] = money_amount
    df_invest_data['share'] = money_amount / df_invest_data['price']
    return df_invest_data


def fixed_invest_by_month(month_day, df_market_data, money_amount):
    day_invest_list = []
    df_invest_data = pd.DataFrame()
    for year in df_market_data['year'].drop_duplicates():
        year_invest_data = df_market_data[df_market_data['year'] == year].copy()
        for month in year_invest_data['month'].drop_duplicates():
            select_trade_day(day_invest_list, year_invest_data, month, month_day)

    df_invest_data['price'] = day_invest_list
    df_invest_data['money'] = money_amount
    df_invest_data['share'] = money_amount / df_invest_data['price']
    return df_invest_data


def select_trade_day(day_invest_list, year_invest_data, month, month_day):
    """月定投日-非交易日处理"""
    month_invest_data = year_invest_data[year_invest_data['month'] == month]
    day_invest_data = month_invest_data[month_invest_data['day'] == month_day].copy()
    if month_day in month_invest_data['day'].values:
        day_invest_list.append(float(day_invest_data['price'].values))
    else:
        df_sup_day = month_invest_data['day'].values - month_day
        if df_sup_day[df_sup_day < 0].size > 0:
            sup_day = df_sup_day[df_sup_day < 0].max() + month_day
        else:
            sup_day = df_sup_day[df_sup_day > 0].min() + month_day
        day_invest_data = month_invest_data[month_invest_data['day'] == sup_day].copy()
        day_invest_list.append(float(day_invest_data['price'].values))


def cal_yield(df_invest_data):
    principal = df_invest_data['money'].sum()
    final_price = df_invest_data.iloc[-1]['price']
    final_amount = df_invest_data['share'].sum() * final_price
    profit = final_amount - principal
    buy_num = df_invest_data['money'].size
    return principal, final_amount, profit, buy_num


def cal_month_num(date_start, date_end):
    month_start = datetime.strptime(date_start, "%Y%m%d").month
    month_end = datetime.strptime(date_end, "%Y%m%d").month
    year_start = datetime.strptime(date_start, "%Y%m%d").year
    year_end = datetime.strptime(date_end, "%Y%m%d").year
    return (year_end - year_start) * 12 + (month_end - month_start) + 1

if __name__ == '__main__':
    index_id = '0000300'
    date_start = '20200226'
    date_end = '20210101'
    print(cal_month_num(date_start, date_end))
    weekday = 3
    m_day = 20
    raw_data = get_raw_data(index_id, date_start, date_end)
    cal_data = gen_cal_data(raw_data)
    df_invest_data = fixed_invest_by_week(weekday, cal_data, 500)
    df_invest_data_m = fixed_invest_by_month(m_day, cal_data, 500)
    principal, final_amount, profit, buy_num = cal_yield(df_invest_data)
    principal_m, final_amount_m, profit_m, buy_num_m = cal_yield(df_invest_data_m)
    print('principal: {}, final_amount: {}, profit: {}, buy_num: {}'.format(principal, final_amount, profit, buy_num))
    print('principal: {}, final_amount: {}, profit: {}, buy_num: {}'.format(principal_m, final_amount_m, profit_m,
                                                                            buy_num_m))


import pymysql.cursors
conn = pymysql.connect(host='127.0.0.1',
                             user='root',
                             password='jxxyxsb321',
                             database='gin_db',
                             charset='utf8')

cursor = conn.cursor()
sql = """
CREATE TABLE USER1 (
id INT auto_increment PRIMARY KEY ,
name CHAR(10) NOT NULL UNIQUE,
age TINYINT NOT NULL
)ENGINE=innodb DEFAULT CHARSET=utf8;
"""
cursor.execute(sql)
cursor.close()
conn.close()
