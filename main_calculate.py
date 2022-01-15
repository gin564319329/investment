from get_market_data import QueryTuShareData, GetCustomData
from fund_tools import CalFixedInvest, CalYieldRate, CalTime
from advance_fun import AdvOperation
from show_rst import ShowRst
import time
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
                    filename=r'rst_out/run_fund.log',
                    filemode='a')


def save_fund_with_basic(save_dir, date_query, date_sel='20210101', market='E', fund_type=None, input_file=None):
    get_data = GetCustomData()
    # fund_basic = get_data.query_fund_basic(market=market, fund_type=fund_type)
    # fund_basic = fund_basic[fund_basic['invest_type'].isnull()]
    fund_basic = get_data.append_fund_basic(date_query, date_sel=date_sel, market=market, fund_type=fund_type,
                                            input_file=input_file)
    logging.info('{} fund number: {}'.format(market, fund_basic.shape[0]))
    fund_basic.to_csv(save_dir, index=False, encoding='utf_8_sig')
    return fund_basic


def save_fund_portfolio(start_date, end_date, save_dir, basic_file='', portfolio_file=''):
    """根据基金basic总表，循环查询append portfolio"""
    portfolio_total = pd.DataFrame()
    get_data = GetCustomData()
    if not basic_file:
        fund_basic = get_data.query_fund_basic(market='E', fund_type=['股票型', '混合型'])
    else:
        fund_basic = pd.read_csv(basic_file)
        fund_basic = fund_basic[fund_basic['fund_type'].isin(['股票型', '混合型'])]
    for i, row in fund_basic.iterrows():
        print('start query: {} {} portfolio data'.format(i, row.get('ts_code')))
        time.sleep(0.9)
        fio = get_data.append_fund_portfolio_name(row.get('ts_code'), start_date, end_date, portfolio_file)
        portfolio_total = portfolio_total.append(fio, ignore_index=True)
        if fio.empty:
            print('No {} portfolio data'.format(row.get('ts_code')))
    portfolio_total.to_csv(save_dir, index=False, encoding='utf_8_sig')
    return portfolio_total


def save_index_ratio(date_query, name_list, save_dir):
    get_data = GetCustomData()
    code_rst = get_data.get_index_tscode_by_name(name_list)
    rst_con = get_data.gen_index_yield(date_query, code_rst)
    rst_con.to_csv(save_dir, index=True, encoding='utf_8_sig')
    return rst_con


def cal_invest_yield(ts_code, date_start, date_end):
    get_data = GetCustomData()
    weekday = 4
    m_day = 20
    cal_data_tu = get_data.get_index_daily_data(ts_code, date_start, date_end)

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
    ax = show_r.gen_one_ax()
    show_r.show_cumulative_value(ax, cal_data_tu, df_invest_data_w)
    show_r.show_average_principal(ax, pri_average_w)


def analysis_fund_fio(portfolio_dir=r'final_data\fio_all.csv'):
    op = AdvOperation()
    sco = op.count_fund_major_stocks(portfolio_dir=portfolio_dir)
    sco_c = sco.iloc[200:250]
    show_r = ShowRst()
    show_r.show_fund_major_stocks(sco_c)


if __name__ == '__main__':

    # code, start, end = '000300.SH', '20151231', '20171231'
    # cal_invest_yield(code, start, end)

    # fund_type = ['股票型', '混合型', '债券型', '货币市场型', '商品型', '另类投资型']
    index_name = ['上证指数', '沪深300', '中证500', '上证50', '中证1000', '国证2000', '创业板指', '中证100']
    date_q = {'date_start': ['20111230', '20121231', '20131231', '20141231', '20151231', '20161230', '20171229',
                             '20181228', '20191231', '20201231', '20111230'],
              'date_end': ['20121231', '20131231', '20141231', '20151231', '20161231', '20171231', '20181231',
                           '20191231', '20201231', '20211231', '20211231'],
              'query_period': ['2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', 'all']}
    # index_name = ['上证指数', '沪深300', '中证500']
    # date_q = {'date_start': ['20171229', '20181228', '20191231', '20201231', '20171229'],
    #           'date_end': ['20181231', '20191231', '20201231', '20211231', '20211231'],
    #           'query_period': ['2018', '2019', '2020', '2021', 'all']}
    # save_file = r'.\rst_out\index_yield_rate_tt.csv'
    # rst = save_index_ratio(date_q, index_name, save_file)

    # save_file = r'.\rst_out\fund_yield_rate_t1.csv'
    # save_file = r'rst_out\fund_basic_exchange_total_a.csv'
    # save_file = r'rst_out\fund_basic_open_total_a.csv'
    save_file = r'rst_out\fio_open.csv'
    # save_file = r'rst_out\fund_basic_exchange_all.csv'
    # i_file = r'rst_out\fund_basic_open_a.csv'
    i_file = r'rst_out\stock_total.csv'
    # code = ('159934.SZ', '518880.SH', '518800.SH')
    code, start, end = '167508.SZ', '20210930', '20220101'
    b_file = r'rst_out\fund_basic_open_a.csv'

    # fund_all = save_fund_with_basic(save_file, date_q, date_sel='20210101', market='E', fund_type=None,
    #                                 input_file=i_file)

    # portfolio_t = save_fund_portfolio(start, end, save_file, basic_file=b_file, portfolio_file=i_file)

    analysis_fund_fio()




