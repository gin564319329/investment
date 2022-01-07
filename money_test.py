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


ts.set_token('a191d192213fbcb32f37352ae88d571a7150c06f855a32aa6b1f8c16')
pro = ts.pro_api()
pro.index_basic(ts_code='000001.SH', market='SSE')
pro.fund_basic(market='E', status='L')
pro.fund_nav(ts_code='161005.SZ')
pro.fund_share(ts_code='161005.SZ')


pd.set_option('display.max_columns', None)
get_data = GetCustomData()

index_code = '000300.SH'
index_info = get_data.query_index_basic(index_code, '', market='SSE')
print(index_info)

ts_code, date_start, date_end = '161005.SZ', '20200930', '20220105'
fund_nav = get_data.query_fund_nav(ts_code, date_start, date_end)
fund_daily = get_data.query_fund_daily(ts_code, date_start, date_end)
# fund_nav.to_csv(r'rst_out\fund_nav.csv', index=False)

fund_basic = get_data.query_fund_basic(fund_type=['商品型', '另类投资型'])
print(fund_basic)

sc = get_data.query_ts_code_by_code(code='163406', market='E')
stn = get_data.query_stock_name('000001.SZ')
fund_manager = get_data.query_fund_manager('167508.SZ')
share = get_data.query_fund_share('167508.SZ')

fio1 = get_data.append_fund_portfolio_name('167508.SZ', end_date='20200630')








