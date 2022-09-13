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
from main_calculate import save_index_ratio, save_my_fund_ab

plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']  # 必须
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

ts.set_token('a191d192213fbcb32f37352ae88d571a7150c06f855a32aa6b1f8c16')
pro = ts.pro_api()
pro.index_basic(ts_code='000001.SH', market='SSE')
# f = pro.fund_basic(market='O', status='L')
# f.to_csv(r'rst_out\fund_open_raw.csv', index=False, encoding='utf_8_sig')
# pro.fund_nav(ts_code='450009.OF')
# pro.fund_share(ts_code='161005.SZ')
s = pro.fund_portfolio(ts_code='167508.SZ', start_date='20211230', end_date='20220121')  # 167508.SZ 450009.OF
# pro.stock_basic(ts_code='000002.SZ, 000001.SZ')
# stock_total = pro.stock_basic(ts_code='')
# stock_total1 = stock_total.drop(['symbol'], axis=1)
# stock_total1.to_csv(r'rst_out\stock_total.csv', index=False, encoding='utf_8_sig')

get_data = GetCustomData()
db = QueryTuShareData()

code = get_data.query_ts_code_by_code('166006')
# code_rst = get_data.get_index_tscode_by_name(['科创50'])
index_code = '000688.SH'
# index_info = get_data.query_index_basic(index_code, '', market='SSE')
# df_cal_data = get_data.get_index_daily_data(index_code, '20190101', '20220301')
cal_data_tu = get_data.get_index_daily_data('000001.SH', '20220210', '20220512')
cal_data_s = cal_data_tu[cal_data_tu['weekday'] == 5]
# fig = plt.figure()
# ax1 = fig.add_subplot(111)
# ax1.plot(s.get('date'), s.get('price'))
# ticks = df_cal_data['date'].tolist()[::20]
# ax1.set_xticks(ticks)
# ax1.set_xticklabels(ticks, rotation=45)
# plt.grid(axis='y')
# plt.show()

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

code, start, end = '001763.OF', '20211230', '20220201'
portfolio = db.query_fund_portfolio(code, start_date=start, end_date=end)

fo = pd.read_csv(r'rst_out\fio_open_20211231.csv')
fe = pd.read_csv(r'rst_out\fio_exchange_20211231.csv')
fa = pd.concat([fo, fe], axis=0, ignore_index=True)
fa.to_csv(r'rst_out\fio_all_20211231.csv', index=False, encoding='utf_8_sig')

fdo = pd.read_csv(r'rst_out\fund_basic_open_total_a.csv')
fdo1 = fdo[fdo['fund_type'].isin(['股票型', '混合型'])]
fdo2 = fdo1[fdo1['2017'].notna()]
fdo3 = fdo2[fdo2['net_asset'] < 80]
fdo4 = fdo2[fdo2['2021'] >= 0]
fdo5 = fdo4[fdo4['2020'] >= fdo2['2020'].median()]
fdo5 = fdo5[fdo5['2019'] >= fdo2['2019'].median()]
fdo5 = fdo5[fdo5['2018'] >= fdo2['2018'].median()]
fdo6 = fdo5.sort_values(by=['2021'], ascending=False)
fdo7 = fdo6[fdo6['net_asset'] < 80]

fdo7.to_csv(r'rst_out\fund_sel.csv', index=False, encoding='utf_8_sig')

fdo = pd.read_excel(r'rst_out\fund_self.xlsx', dtype={'code': str})

index_name = ['上证指数', '沪深300', '中证500', '上证50', '中证1000', '国证2000', '创业板指', '中证100']
period_q = {'date_start': ['20211231'],
            'date_end': ['20220219'],
            'query_period': ['2022']}

save_file = r'.\rst_out\index_yield_rate_1.csv'
rst = save_index_ratio(period_q, index_name, save_file)

save_file = r'rst_out\my_fund_total_01.csv'
my_fund_file = r'final_data\query_db\my_fund_raw.xlsx'
query_basic_f = r'final_data\query_db\query_fund_basic.csv'
fund_ab = save_my_fund_ab(period_q, save_file, my_fund_file, query_basic_f)
f_s = fund_ab[fund_ab['fund_type'].isin(['股票型', '混合型'])]
f_c = f_s.drop(['ts_code', 'management', 'found_date', 'fund_type', 'invest_type', 'benchmark',
                'm_fee', 'c_fee', 'manager', 'ann_date'], axis=1)
# fc1 = f_c[['name', '2022']]
f_c.median()
fsort = f_c.sort_values(by=['2022'], ascending=False)

p_fund = r'.\rst_out\fund_basic_open_total_a.csv'
f = pd.read_csv(p_fund)
f.median()
f.mean()
