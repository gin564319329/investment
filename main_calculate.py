from get_market_data import GetTuShareData
from fund_tools import CalFixedInvest, CalYieldRate, CalTime
from show_rst import ShowRst
from advance_fun import AdvOperation
import pandas as pd
import logging

pd.set_option('display.max_columns', None)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.width', 1)
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%d %b %Y, %H:%M',
                    filename=r'.\run_fund.log',
                    filemode='a')


def save_fund_with_basic(fund_type='', market='E'):
    get_data = GetTuShareData()
    fund_basic = get_data.get_fund_basic(market=market,  fund_type=fund_type)
    fund_basic = get_data.append_fund_basic(fund_basic)
    if market == 'E':
        logging.info('Exchange fund number: {}'.format(fund_basic.shape[0]))
        fund_basic.to_csv(r'rst_out\fund_basic_exchange_a.csv', index=False, encoding='utf_8_sig')
    elif market == 'O':
        logging.info('Open fund number: {}'.format(fund_basic.shape[0]))
        fund_basic.to_csv(r'rst_out\fund_basic_open_a.csv', index=False, encoding='utf_8_sig')
    else:
        logging.warning('Error market type: {}'.format(market))
    return fund_basic


def save_index_ratio(date_query, name_list, save_dir):
    ad = AdvOperation()
    code_rst = ad.query_index_tscode_by_name(name_list)
    rst_con = ad.gen_index_yield(date_query, code_rst)
    rst_con.to_csv(save_dir, index=True, encoding='utf_8_sig')
    return rst_con


def save_fund_with_ratio(date_query, save_dir, code_list=(), fund_type='', market='E'):
    get_data = GetTuShareData()
    fund_basic = get_data.get_fund_basic(market=market, fund_type=fund_type)
    if not code_list:
        fund_query = fund_basic.copy()
    else:
        fund_query = fund_basic[fund_basic['ts_code'].isin(code_list)]
    ad = AdvOperation()
    rst_con = ad.append_fund_yield(date_query, fund_query)
    rst_con.to_csv(save_dir, index=False, encoding='utf_8_sig')
    return rst_con


def cal_invest_yield(ts_code, date_start, date_end):
    weekday = 4
    m_day = 20
    tu_data = GetTuShareData().get_index_daily(ts_code, date_start, date_end)
    cal_data_tu = GetTuShareData().gen_cal_data(tu_data)

    fit = CalFixedInvest(cal_data_tu, money_amount=500)
    fit_m = CalFixedInvest(cal_data_tu, money_amount=2000)
    df_invest_data_w = fit.fixed_invest_by_week(weekday=weekday)
    df_invest_data_m = fit_m.fixed_invest_by_month(month_day=m_day)
    principal_w, final_amount_w, profit_w, buy_num_w, pri_average_w = fit.cal_yield(df_invest_data_w)
    principal_m, final_amount_m, profit_m, buy_num_m, pri_average_m = fit.cal_yield(df_invest_data_m)
    print('week: principal: {}, final_amount: {}, profit: {}, buy_num: {}'.format(principal_w, final_amount_w, profit_w,
                                                                                  buy_num_w))
    print(
        'month: principal: {}, final_amount: {}, profit: {}, buy_num: {}'.format(principal_m, final_amount_m, profit_m,
                                                                                 buy_num_m))
    # cal_time = CalTime(date_start, date_end)
    # month_num = cal_time.cal_month_num()
    # x_ticks = cal_time.gen_ticks(month_num)
    val_arr_w = [500] * 50
    val_arr_w.append(-final_amount_w)

    val_arr_m = [2000] * 12
    val_arr_m.append(-final_amount_m)

    yr = CalYieldRate()
    rate_w = yr.cal_total_rate(principal_w, final_amount_w)
    rate_m = yr.cal_total_rate(principal_m, final_amount_m)
    rate_w_irr = yr.cal_irr_by_fixed_invest(val_arr_w, 50)
    rate_m_irr = yr.cal_irr_by_fixed_invest(val_arr_m, 12)

    show_r = ShowRst()
    ax = show_r.gen_fig()
    show_r.show_cumulative_value(ax, cal_data_tu, df_invest_data_w)
    show_r.show_average_principal(ax, pri_average_w)


if __name__ == '__main__':
    # code, start, end = '000300.SH', '20151231', '20171231'
    # cal_invest_yield(code, start, end)

    # index_name = ['上证指数', '沪深300', '中证500', '上证50', '中证1000', '国证2000', '创业板指', '中证100']
    # date_s = {'date_start': ['20111230', '20121231', '20131231', '20141231', '20151231', '20161230', '20171229',
    #                          '20181228', '20191231', '20201231', '20111230'],
    #           'date_end': ['20121231', '20131231', '20141231', '20151231', '20161231', '20171231', '20181231',
    #                        '20191231', '20201231', '20211231', '20211231'],
    #           'query_period': ['2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', 'all']}
    # index_name = ['上证指数', '沪深300', '中证500']
    date_s = {'date_start': ['20171229', '20181228', '20191231', '20201231', '20171229'],
              'date_end': ['20181231', '20191231', '20201231', '20211231', '20211231'],
              'query_period': ['2018', '2019', '2020', '2021', 'all']}
    # save_file = r'.\rst_out\index_yield_rate_t.csv'
    # rst = save_index_ratio(date_s, index_name, save_file)

    save_file = r'.\rst_out\fund_yield_rate_t1.csv'
    code = ('159934.SZ', '518880.SH', '518800.SH')
    rst = save_fund_with_ratio(date_s, save_file, code_list=code,  fund_type='')
    print(rst)
