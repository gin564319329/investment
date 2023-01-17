import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
from data_generator import QueryTuShareData, GenCustomData
from show_rst import ShowRst
import tushare as ts
from main_analysis import save_my_fund

plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']  # 必须
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

ts.set_token('a191d192213fbcb32f37352ae88d571a7150c06f855a32aa6b1f8c16')
pro = ts.pro_api()
ind = pro.index_basic(ts_code='000001.SH', market='SSE')
f = pro.fund_basic(market='O', status='L')
nav = pro.fund_nav(ts_code='450009.OF')
sha = pro.fund_share(ts_code='161005.SZ')
s = pro.fund_portfolio(ts_code='167508.SZ', start_date='20211230', end_date='20220121')  # 167508.SZ 450009.OF
s = pro.stock_basic(ts_code='000002.SZ, 000001.SZ')

get_data = GenCustomData()
db = QueryTuShareData()

code = get_data.query_ts_code_by_code('166006')
code_rst = get_data.get_index_tscode_by_name(['科创50'])
index_code = '000688.SH'
index_info = get_data.query_index_basic(index_code, '', market='SSE')
cal_data_tu = get_data.gen_index_daily_data('000001.SH', '20220210', '20220512')
cal_data_s = cal_data_tu[cal_data_tu['weekday'] == 5]

ts_code, date_start, date_end = '163406.SZ', '20200930', '20220105'  # 450009.OF
fund_nav = get_data.query_fund_nav(ts_code, date_start, date_end)
fund_daily = get_data.query_fund_daily(ts_code, date_start, date_end)
fund_basic = get_data.query_fund_basic(fund_type=['商品型', '另类投资型'])

stn = get_data.query_stock_name('000001.SZ')
fund_manager = get_data.query_fund_manager('167508.SZ')
share = get_data.query_fund_share('167508.SZ')

code, start, end = '001763.OF', '20211230', '20220201'
portfolio = db.query_fund_portfolio(code, start_date=start, end_date=end)
portfolio1 = pro.fund_portfolio(ts_code='159642.SZ')


csv_file = r'final_data\fund_yield_rate_stock_202301.csv'
my_file = r'rst_out/my_fund_2022.xlsx'
save_file = r'rst_out\my_fund_sel.csv'
base_fund = pd.read_csv(csv_file)
fund = pd.read_excel(my_file, sheet_name=0)

base_fund = base_fund[base_fund['fund_type'].isin(('股票型', '混合型'))]
fund1 = fund[fund['fund_type'].isin(('股票型', '混合型'))]
# fund1 = fund[fund['2017'].notna()]
# fund1 = fund[fund['2017'].isna()]
# fund1 = fund[fund['net_asset'] < 100]
# fund1 = fund[fund['net_asset'] > 100]

fund1 = fund1[fund1['2022'] >= base_fund['2022'].median()]
fund1 = fund1[fund1['2021'] >= base_fund['2021'].median()]
# fund1 = fund1[fund1['2021'] >= -5]
fund1 = fund1[fund1['2020'] >= base_fund['2020'].median()]
fund1 = fund1[fund1['2019'] >= base_fund['2019'].median()]
fund1 = fund1[fund1['2018'] >= base_fund['2018'].median()]
good_fund = fund1.sort_values(by=['2022'], ascending=False)

fund1 = fund1[fund1['2022'] < base_fund['2022'].median()]
fund1 = fund1[fund1['2021'] < base_fund['2021'].median()]
fund1 = fund1[fund1['2020'] < base_fund['2020'].median()]
fund1 = fund1[fund1['2019'] < base_fund['2019'].median()]
fund1 = fund1[fund1['2018'] < base_fund['2018'].median()]
bad_fund = fund1.sort_values(by=['2022'], ascending=True)

good_fund.to_excel(save_file, index=False, encoding='utf_8_sig')


