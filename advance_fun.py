# -*-coding:utf-8-*-

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


get_data = GetTuShareData()
cal_base = CalYieldRate()


def search_code_batch(search_list):
    df_sh = get_data.get_index_basic('', '', market='SSE')
    df_sz = get_data.get_index_basic('', '', market='SZSE')
    search_dict = {'ts_code': [], 'name': []}

    for index, s in df_sh.iterrows():
        if s['name'] in search_list:
            search_list.remove(s['name'])
            print('{}\t代码:\t {}'.format(s['name'], s['ts_code']))
            search_dict['ts_code'].append(s['ts_code'])
            search_dict['name'].append(s['name'])

    for index, s in df_sz.iterrows():
        if s['name'] in search_list:
            search_list.remove(s['name'])
            print('{}\t代码:\t {}'.format(s['name'], s['ts_code']))
            search_dict['ts_code'].append(s['ts_code'])
            search_dict['name'].append(s['name'])

    return search_dict


def get_change_ratio(ts_code, date_start, date_end):
    tu_data = get_data.get_index_daily(ts_code, date_start, date_end)
    cal_data_tu = get_data.gen_cal_data(tu_data)
    st = cal_data_tu.iloc[0]['price']
    end = cal_data_tu.iloc[-1]['price']
    c_ratio = cal_base.cal_change_ratio(st, end)
    return c_ratio


def get_invest_rst(ts_code, date_start, date_end):
    tu_data = get_data.get_index_daily(ts_code, date_start, date_end)
    cal_data_tu = get_data.gen_cal_data(tu_data)
    weekday = 4
    fit = CalFixedInvest(cal_data_tu, money_amount=500)
    df_invest_data_w = fit.fixed_invest_by_week(weekday=weekday)
    principal_w, final_amount_w, profit_w, buy_num_w, pri_average_w = fit.cal_yield(df_invest_data_w)
    i_ratio = cal_base.cal_change_ratio(principal_w, final_amount_w)
    return i_ratio


if __name__ == '__main__':
    # name_search_list = ['上证指数', '沪深300', '中证500', '上证50', '中证1000', '国证2000', '创业板指', '中证100']
    # search_rst = search_code_batch(name_search_list)
    # print(search_rst)

    date_start = '20191230'
    date_end = '20201231'
    date_start = '20171230'
    date_end = '20211031'
    # ts_code = '399300.SZ'
    # ts_code = '399905.SZ' #'000001.SH'  #'399905.SZ'
    ts_code = '399006.SZ'
    ch_ratio = get_change_ratio(ts_code, date_start, date_end)
    print('{:.2%}'.format(ch_ratio))
    in_ratio = get_invest_rst(ts_code, date_start, date_end)
    print('irri profit: {:.2%}'.format(in_ratio))
