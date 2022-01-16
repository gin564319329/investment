from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from advance_fun import AdvOperation
from get_market_data import QueryTuShareData, GetCustomData
from fund_tools import CalFixedInvest, CalYieldRate, CalTime
from show_rst import ShowRst
import time
import requests
from bs4 import BeautifulSoup
import re
import tushare as ts


plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']  # 必须
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

ts.set_token('a191d192213fbcb32f37352ae88d571a7150c06f855a32aa6b1f8c16')
pro = ts.pro_api()
# pro.index_basic(ts_code='000001.SH', market='SSE')
# f = pro.fund_basic(market='O', status='L')
# f.to_csv(r'rst_out\fund_open_raw.csv', index=False, encoding='utf_8_sig')
# pro.fund_nav(ts_code='450009.OF')
# pro.fund_share(ts_code='161005.SZ')
s = pro.fund_portfolio(ts_code='167508.SZ', ann_date='', start_date='20210630', end_date='20220101')  # 167508.SZ 450009.OF
# pro.stock_basic(ts_code='000002.SZ, 000001.SZ')
# stock_total = pro.stock_basic(ts_code='')
# stock_total1 = stock_total.drop(['symbol'], axis=1)
# stock_total1.to_csv(r'rst_out\stock_total.csv', index=False, encoding='utf_8_sig')

get_data = GetCustomData()

# index_code = '000300.SH'
# index_info = get_data.query_index_basic(index_code, '', market='SSE')
# print(index_info)
#
# ts_code, date_start, date_end = '163406.SZ', '20200930', '20220105'  # 450009.OF
# fund_nav = get_data.query_fund_nav(ts_code, date_start, date_end)
# fund_daily = get_data.query_fund_daily(ts_code, date_start, date_end)
#
# fund_basic = get_data.query_fund_basic(fund_type=['商品型', '另类投资型'])
# print(fund_basic)
#
# sc = get_data.query_ts_code_by_code(code='163406', market='E')
# stn = get_data.query_stock_name('000001.SZ')
# fund_manager = get_data.query_fund_manager('167508.SZ')
# share = get_data.query_fund_share('167508.SZ')


fo = pd.read_csv(r'rst_out\fio_open.csv')
fe = pd.read_csv(r'rst_out\fio_exchange.csv')
fa = pd.concat([fo, fe], axis=0, ignore_index=True)
fa.to_csv(r'rst_out\fio_all.csv', index=False, encoding='utf_8_sig')

fdo = pd.read_csv(r'rst_out\fund_basic_open_total_a.csv')
fdo1 = fdo[fdo['fund_type'].isin(['股票型', '混合型'])]
fdo2 = fdo1[fdo1['2017'].notna()]
fdo3 = fdo2[fdo2['net_asset']<80]
fdo4 = fdo2[fdo2['2021'] >= 0]
fdo5 = fdo4[fdo4['2020'] >= fdo2['2020'].median()]
fdo5 = fdo5[fdo5['2019'] >= fdo2['2019'].median()]
fdo5 = fdo5[fdo5['2018'] >= fdo2['2018'].median()]
fdo6 = fdo5.sort_values(by=['2021'], ascending=False)
fdo7 = fdo6[fdo6['net_asset']<80]

