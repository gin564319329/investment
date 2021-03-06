from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from advance_fun import get_ts_code_by_code
from get_market_data import GetTuShareData
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

ts_code, date_start, date_end = '167508.SZ', '20200630', '20200930'
fund_nav = get_data.get_fund_nav(ts_code=ts_code)
fund_daily = get_data.get_fund_daily(ts_code, date_start, date_end)
fund_nav.to_csv('D:\\project_codes\\temp\\fund_nav.csv', index=False)

fund_e = get_data.get_fund_basic(market='O', status='L')
set(fund_e['invest_type'].tolist())
set(fund_e['fund_type'].tolist())
ss = fund_e[fund_e['fund_type'] == '商品型']

fund_append = get_data.append_fund_basic(fund_type='', market='E', save_dir=r'D:\project_codes\temp\fund_basic_e_all1'
                                                                            r'.csv')
fund_e.to_csv('D:\\project_codes\\temp\\fund_open_delist1.csv', index=False, encoding='utf_8_sig')

sc = get_ts_code_by_code(code='163406', market='E')
stn = get_data.get_stock_name('000001.SZ')

portfolio = get_data.get_fund_portfolio('167508.SZ', end_date='20200630')
folio = get_data.get_stock_name_batch(portfolio['symbol'].tolist())
fio = pd.concat([portfolio, folio['name']], axis=1)

fund_manager = get_data.get_fund_manager(ts_code)



