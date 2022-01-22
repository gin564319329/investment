from get_market_data import QueryTuShareData, GetCustomData, SaveQueryDB
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
logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s %(message)s',
#                     datefmt='%d %b %Y, %H:%M',
#                     filename=r'rst_out/run_fund.log',
#                     filemode='a')

get_data = GetCustomData()


def save_tu_fund_ab(period_query, save_dir, found_date_sel='20210101', market='E', fund_type=None, input_file=None):
    """保存tushare基金 基础信息以及扩展信息， 包括 basic信息，规模信息 net_asset 基金年度收益率信息"""
    if input_file is None:
        fund = None
    else:
        fund = pd.read_csv(input_file)
    fund_info = get_data.append_fund_basic(period_query, found_date_sel, market, fund_type, fund)
    logging.info('fund number: {}'.format(fund_info.shape[0]))
    fund_info.to_csv(save_dir, index=False, encoding='utf_8_sig')
    return fund_info


def save_fund_portfolio(start_date, end_date, save_dir, basic_file='', portfolio_file=''):
    """根据基金basic总表，循环查询append portfolio"""
    portfolio_total = pd.DataFrame()
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
        else:
            print('{} ann date: {}'.format(row.get('ts_code'), fio.get('end_date').drop_duplicates().tolist()))
    portfolio_total.to_csv(save_dir, index=False, encoding='utf_8_sig')
    return portfolio_total


def save_index_ratio(date_query, name_list, save_dir):
    code_rst = get_data.get_index_tscode_by_name(name_list)
    rst_con = get_data.gen_index_yield(date_query, code_rst)
    rst_con.to_csv(save_dir, index=True, encoding='utf_8_sig')
    return rst_con


def cal_invest_yield(ts_code, date_start, date_end):
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


def save_my_fund_ab(period_query, save_dir, my_file, query_file=None):
    """ save my selective fund: append info - fund manager, net asset info..."""
    my_fund = pd.read_excel(my_file, dtype={'code': str})
    if query_file is None:
        query_info = None
    else:
        query_info = pd.read_csv(query_file)
    my_fund_basic = get_data.self_fund_pro(my_fund, query_basic=query_info)
    my_fund_append = get_data.append_fund_basic(period_query, fund_basic=my_fund_basic)
    logging.info('my fund number: {}'.format(my_fund_append.shape[0]))
    my_fund_append.to_csv(save_dir, index=False, encoding='utf_8_sig')


if __name__ == '__main__':
    # code, start, end = '000300.SH', '20151231', '20171231'
    # cal_invest_yield(code, start, end)

    # fund_type = ['股票型', '混合型', '债券型', '货币市场型', '商品型', '另类投资型']
    # index_name = ['上证指数', '沪深300', '中证500', '上证50', '中证1000', '国证2000', '创业板指', '中证100']
    # index_name = ['上证指数', '沪深300', '中证500']
    # period_q = {'date_start': ['20111230', '20121231', '20131231', '20141231', '20151231', '20161230', '20171229',
    #                            '20181228', '20191231', '20201231', '20111230'],
    #             'date_end': ['20121231', '20131231', '20141231', '20151231', '20161231', '20171231', '20181231',
    #                          '20191231', '20201231', '20211231', '20211231'],
    #             'query_period': ['2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019',
    #                              '2020', '2021', 'all']}
    period_q = {'date_start': ['20161230', '20171229', '20181228', '20191231', '20201231', '20211231', '20161230'],
                'date_end': ['20171231', '20181231', '20191231', '20201231', '20211231', '20220119', '20220119'],
                'query_period': ['2017', '2018', '2019', '2020', '2021', '2022', 'all']}

    # save_file = r'.\rst_out\index_yield_rate_tt.csv'
    # rst = save_index_ratio(period_q, index_name, save_file)

    # save_file = r'rst_out\fund_basic_exchange_total_a.csv'
    # save_file = r'rst_out\fund_basic_open_total_a.csv'
    # i_fund_file = r'rst_out\fund_basic_open_a.csv'
    # fund_all = save_tu_fund_ab(period_q, save_file, input_file=i_fund_file)

    # period_q = {'date_start': ['20211231'],
    #             'date_end': ['20220119'],
    #             'query_period': ['2022']}
    # save_file = r'rst_out\my_fund_total_t.csv'
    # my_fund_file = r'rst_out\my_fund_raw.xlsx'
    # query_basic_f = r'final_data\query_db\query_fund_basic.csv'
    # save_my_fund_ab(period_q, save_file, my_fund_file, query_basic_f)

    start, end = '20211230', '20220201'
    i_stock_file = r'final_data\query_db\stock_total.csv'
    b_file = r'rst_out\fund_basic_exchange_all.csv'
    b_file = r'rst_out\my_fund_total.csv'
    save_file = r'rst_out\fio_exchange_t.csv'
    portfolio_t = save_fund_portfolio(start, end, save_file, basic_file=b_file, portfolio_file=i_stock_file)
    analysis_fund_fio()

