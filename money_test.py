from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from get_market_data import GetCsvData, GetTuShareData
from fund_tools import CalFixedInvest, CalYieldRate, CalTime
from show_rst import ShowRst

import requests
from bs4 import BeautifulSoup
import re
import matplotlib
import tushare as ts

pd.set_option('display.max_columns', None)

ts.set_token('a191d192213fbcb32f37352ae88d571a7150c06f855a32aa6b1f8c16')
pro = ts.pro_api()


df = pro.fund_share(ts_code='150018.SZ')

#多只基金
df = pro.fund_share(ts_code='150018.SZ,150008.SZ')

date_start = '20151231'
date_end = '20171231'
ts_code = '162605.SZ'
# ts_code = '000300.SH'
# ts_code = '399905.SZ'
weekday = 4
m_day = 20
get_data = GetTuShareData()
tu_data = get_data.get_fund_daily(ts_code, date_start, date_end)
tu_basic = get_data.get_fund_basic(market='O', status='D')

tu_basic.to_csv('D:\\project_codes\\temp\\fund_open_delist.csv', index=False, encoding='utf_8_sig')

tu_data.to_csv('D:\\project_codes\\temp\\tushare.csv', index=False)
tu_data.to_excel('D:\\project_codes\\temp\\tuexc.xls', index=False)
df = pro.fund_nav(ts_code=ts_code)
df1 = get_data.get_fund_nav(ts_code, date_start, date_end)
port = pro.fund_portfolio('001753.OF', ann_date='20180823', end_date='20180630')
portfolio = get_data.get_fund_portfolio(ts_code)
tu_ma = GetTuShareData().get_fund_manager(ts_code)
print(tu_ma)
fu_basic = GetTuShareData().get_fund_basic(market='O', status='L')
fu_e = GetTuShareData().get_fund_basic(market='E', status='L')
print(fu_basic)

js = fu_basic[fu_basic['management']=='景顺长城基金']
jse = fu_e[fu_e['management']=='景顺长城基金']


df= pd.DataFrame.from_dict({'sd': 34})
df.to_excel()