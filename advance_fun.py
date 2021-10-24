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
from IPython.display import display


get_data = GetTuShareData()
cal_base = CalYieldRate()


def get_daily_data(ts_code, date_start, date_end):
    tu_data = get_data.get_index_daily(ts_code, date_start, date_end)
    cal_data_tu = get_data.gen_cal_data(tu_data)
    return cal_data_tu


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


def get_change_ratio(cal_data_tu):
    st = cal_data_tu.iloc[0]['price']
    end = cal_data_tu.iloc[-1]['price']
    c_ratio = cal_base.cal_change_ratio(st, end)
    return c_ratio


def get_invest_rst(cal_data_tu):
    weekday = 4
    fit = CalFixedInvest(cal_data_tu, money_amount=500)
    df_invest_data_w = fit.fixed_invest_by_week(weekday=weekday)
    principal_w, final_amount_w, profit_w, buy_num_w, pri_average_w = fit.cal_yield(df_invest_data_w)
    i_ratio = cal_base.cal_change_ratio(principal_w, final_amount_w)
    return i_ratio


def get_ratio_batch(date_search_dict, ts_code_list):
    for code in ts_code_list:
        for start, end in zip(date_search_dict['date_start'], date_search_dict['date_end']):
            cal_data_tu = get_daily_data(code, start, end)
            ch_ratio = get_change_ratio(cal_data_tu)
            print('{} {} change ratio: {:.2%}'.format(cal_data_tu.iloc[-1]['year'], code, ch_ratio))
            in_ratio = get_invest_rst(cal_data_tu)
            print('{} {} irri profit: {:.2%}'.format(cal_data_tu.iloc[-1]['year'], code, in_ratio))


def get_ratio_batch_by_date(date_search_dict, code_search_dict):
    rst_dict_date = {'year': []}
    rst_dict_ch = {'{}_涨跌幅'.format(na): [] for na in code_search_dict.get('name')}
    rst_dict_in = {'{}_定投收益'.format(na): [] for na in code_search_dict.get('name')}
    for start, end in zip(date_search_dict['date_start'], date_search_dict['date_end']):
        rst_dict_date['year'].append(end[0:4])
        for code, name in zip(code_search_dict.get('ts_code'), code_search_dict.get('name')):
            cal_data_tu = get_daily_data(code, start, end)
            ch_ratio = get_change_ratio(cal_data_tu)
            in_ratio = get_invest_rst(cal_data_tu)
            rst_dict_ch['{}_涨跌幅'.format(name)].append(ch_ratio)
            rst_dict_in['{}_定投收益'.format(name)].append(in_ratio)
            print('{} {} change ratio: {:.2%}'.format(cal_data_tu.iloc[-1]['year'], name, ch_ratio))
            print('{} {} irri profit: {:.2%}'.format(cal_data_tu.iloc[-1]['year'], name, in_ratio))
    rst_dict_date['year'][-1] = 'all'
    rst_data = pd.DataFrame(rst_dict_date)
    rst_df_ch = pd.concat([rst_data, pd.DataFrame(rst_dict_ch)], axis=1)
    rst_df_in = pd.concat([rst_data, pd.DataFrame(rst_dict_in)], axis=1)
    rst_df = pd.concat([rst_data, pd.DataFrame(rst_dict_ch), pd.DataFrame(rst_dict_in)], axis=1)
    return rst_df, rst_df_ch, rst_df_in


def cal_contrast(rst_df_raw):
    rst_ch_con = rst_df_raw.copy()
    rst_ch_con['最大收益指数'] = rst_df_raw.iloc[:, 1:].idxmax(axis=1).values
    rst_ch_con['最小收益指数'] = rst_df_raw.iloc[:, 1:].idxmin(axis=1).values
    return rst_ch_con


if __name__ == '__main__':
    # name_search_list = ['上证指数', '沪深300', '中证500', '上证50', '中证1000', '国证2000', '创业板指', '中证100']
    name_search_list = ['上证指数', '上证50', '沪深300', '中证500', '创业板指']
    search_rst = search_code_batch(name_search_list)
    print(search_rst)

    # date_start = '20201230'
    # date_end = '20211231'
    # # ts_code = '399300.SZ'
    # # ts_code = '399905.SZ' #'000001.SH'  #'399905.SZ'
    # # ts_code = '399006.SZ'
    # ts_code = '000001.SH'
    # cal_data_tu = get_daily_data(ts_code, date_start, date_end)
    # print(cal_data_tu.iloc[0]['date'], cal_data_tu.iloc[-1]['date'])
    # ch_ratio = get_change_ratio(cal_data_tu)
    # print('{:.2%}'.format(ch_ratio))
    # in_ratio = get_invest_rst(cal_data_tu)
    # print('irri profit: {:.2%}'.format(in_ratio))

    code_search = ['000001.SH', '000300.SH', '000905.SH']
    date_search = dict()
    date_search['date_start'] = ['20111230', '20121231', '20131231', '20141231', '20151231', '20161230', '20171229',
                                 '20181228', '20191231', '20201231', '20111230']
    date_search['date_end'] = ['20121231', '20131231', '20141231', '20151231', '20161231', '20171231', '20181231',
                               '20191231', '20201231', '20211022', '20211022']
    # date_search['date_start'] = ['20161230', '20171229', '20181228']
    # date_search['date_end'] = ['20171231', '20181231', '20191231']
    rst, rst_ch, rst_in = get_ratio_batch_by_date(date_search, search_rst)
    rst_ch_con = cal_contrast(rst_ch)
    rst_in_con = cal_contrast(rst_in)

    rst.to_csv('D:\\project_codes\\investment\\ratio_rst.csv', index=False, encoding='utf_8_sig')
    rst_ch_con.to_csv('D:\\project_codes\\investment\\ratio_rst_ch.csv', index=False, encoding='utf_8_sig')
    rst_in_con.to_csv('D:\\project_codes\\investment\\ratio_rst_in.csv', index=False, encoding='utf_8_sig')

    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 1)
    print(rst)
    print(rst_ch_con)
    print(rst_in_con)


