from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from advance_fun import get_ts_code_by_code
from get_market_data import GetCsvData, GetTuShareData
from fund_tools import CalFixedInvest, CalYieldRate, CalTime
from show_rst import ShowRst
import time
import requests
from bs4 import BeautifulSoup
import re
import matplotlib
import tushare as ts

pd.set_option('display.max_columns', None)
get_data = GetTuShareData()
# ts_share = get_data.get_fund_share(ts_code='163412.SZ')

fund_e = get_data.get_fund_basic(market='E', status='L')
set(fund_e['invest_type'].tolist())
set(fund_e['fund_type'].tolist())
ss = fund_e[fund_e['fund_type'] == '商品型']

get_data.append_fund_basic(fund_type='', save_dir='D:\\project_codes\\fund_basic_e_all.csv')




# print(ts_share)

# date = 20210930
# date_list = ts_share['trade_date'].tolist()
# for date in date_list:
#     nav = get_data.get_fund_nav(ts_code='163412.SZ', start_date=date, end_date=date)
#     if nav.empty:
#         print('date error')
#     print(nav)
# print(nav)


# sc = get_ts_code_by_code(code='163406', market='E')
# print(sc)

# ts.set_token('a191d192213fbcb32f37352ae88d571a7150c06f855a32aa6b1f8c16')
# pro = ts.pro_api()
# df = pro.fund_share(ts_code='150018.SZ')
# date_start = '20151231'
# date_end = '20171231'
# ts_code = '162605.SZ'
# # ts_code = '000300.SH'
# # ts_code = '399905.SZ'
# weekday = 4
# m_day = 20



# ss = get_data.get_stock_name('167508.SZ')
# print(ss[0])

# portfolio = get_data.get_fund_portfolio('167508.SZ', end_date='20200630')
# folio = get_data.get_stock_name_batch(portfolio['symbol'].tolist())
# fio = pd.concat([portfolio, folio['name']], axis=1)

# tu_data = get_data.get_fund_daily(ts_code, date_start, date_end)
# tu_basic = get_data.get_fund_basic(market='E', status='L')
#
# tu_basic.to_csv('D:\\project_codes\\temp\\fund_open_delist.csv', index=False, encoding='utf_8_sig')
#
# tu_data.to_csv('D:\\project_codes\\temp\\tushare.csv', index=False)
# tu_data.to_excel('D:\\project_codes\\temp\\tuexc.xls', index=False)
# df = pro.fund_nav(ts_code=ts_code)
#
# df1 = get_data.get_fund_nav(ts_code, date_start, date_end)
# df = pro.fund_portfolio(ts_code='001753.OF', end_date='')
# portfolio = get_data.get_fund_portfolio('167508.SZ', '')
#
# tu_ma = GetTuShareData().get_fund_manager(ts_code)
# print(tu_ma)
# fu_basic = GetTuShareData().get_fund_basic(market='O', status='L')
# fu_e = GetTuShareData().get_fund_basic(market='E', status='L')
# print(fu_basic)
#
# js = fu_basic[fu_basic['management']=='景顺长城基金']
# jse = fu_e[fu_e['management']=='景顺长城基金']
#
#
# df= pd.DataFrame.from_dict({'sd': 34})
# df.to_excel()
#
#

