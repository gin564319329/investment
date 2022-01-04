from get_market_data import GetTuShareData
from fund_tools import CalFixedInvest, CalYieldRate, CalTime
from show_rst import ShowRst
from advance_fun import AdvOperation
import pandas as pd
import logging

pd.set_option('display.max_columns', None)
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%d %b %Y, %H:%M',
                    filename=r'.\run_fund.log',
                    filemode='a')


def get_multi_fund_set(fund_type='', market='E'):
    get_data = GetTuShareData()
    # fund_basic = get_data.get_fund_basic(market=market)

    fund_basic = get_data.append_fund_basic(fund_type=fund_type, market=market)
    if market == 'E':
        logging.info('Exchange fund number: {}'.format(fund_basic.shape[0]))
        fund_basic.to_csv(r'rst_out\fund_basic_exchange_a.csv', index=False, encoding='utf_8_sig')
    elif market == 'O':
        logging.info('Open fund number: {}'.format(fund_basic.shape[0]))
        fund_basic.to_csv(r'rst_out\fund_basic_open_a.csv', index=False, encoding='utf_8_sig')
    else:
        logging.warning('Error market type: {}'.format(market))


def cal_index_ratio_batch(name_search_list):
    ad = AdvOperation(CalYieldRate())
    search_rst = ad.search_code_batch(name_search_list)
    date_search = {'date_start': ['20111230', '20121231', '20131231', '20141231', '20151231', '20161230', '20171229',
                                  '20181228', '20191231', '20201231', '20111230'],
                   'date_end': ['20121231', '20131231', '20141231', '20151231', '20161231', '20171231', '20181231',
                                '20191231', '20201231', '20211231', '20211231']}
    rst_con = ad.get_ratio_batch_by_date(date_search, search_rst)
    rst_con.to_csv(r'.\rst_out\inv_value_ratio.csv', index=False, encoding='utf_8_sig')


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
    # name_search = ['上证指数', '沪深300', '中证500', '上证50', '中证1000', '国证2000', '创业板指', '中证100']
    # name_search = ['上证指数', '沪深300', '中证500']
    # cal_index_ratio_batch(name_search)

    # code, start, end = '000300.SH', '20151231', '20171231'
    # cal_invest_yield(code, start, end)

    # code, start, end = '167508.SZ', '20200630', '20200930'

    get_multi_fund_set(market='O')
