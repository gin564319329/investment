from data_generator import GenCustomData, GenFixedInvest
from show_rst import ShowRst
import time
import pandas as pd
import logging
import basic_calculator as yc
import data_calculator as dca
from basic_calculator import CalTime

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

get_data = GenCustomData()


def save_tu_fund_raw(save_dir):
    fund_info = get_data.gen_raw_fund_list()
    logging.info('fund number: {}'.format(fund_info.shape[0]))
    fund_info.to_csv(save_dir, index=False, encoding='utf_8_sig')
    return fund_info


def save_tu_fund_append(period_query, save_dir, found_date_sel='20210601', fund_type=('股票型', '混合型'), market=None,
                        query_file=None):
    """保存tushare基金 基础信息以及扩展信息， 包括 basic信息，规模信息 net_asset 基金年度收益率信息"""
    if query_file is None:
        fund = None
    elif market is None:
        fund = pd.read_csv(query_file)
        fund = fund[fund['fund_type'].isin(fund_type)]
    else:
        fund = pd.read_csv(query_file)
        fund = fund[fund['fund_type'].isin(fund_type)][fund['market'] == market]

    fund_info = get_data.append_fund_basic(period_query, found_date_sel, market, fund_type, fund)
    logging.info('fund number: {}'.format(fund_info.shape[0]))
    fund_info.to_csv(save_dir, index=False, encoding='utf_8_sig')
    return fund_info


def save_my_fund(period_query, save_dir, my_file, query_file=None):
    """ save my selective fund: append info - fund manager, net asset info..."""
    my_fund = pd.read_excel(my_file, dtype={'code': str})
    if query_file is None:
        query_info = None
    else:
        query_info = pd.read_csv(query_file)
    my_fund_basic = get_data.gen_self_fund_list(my_fund, query_basic=query_info)
    my_fund_append = get_data.append_fund_basic(period_query, fund_basic=my_fund_basic)
    logging.info('my fund number: {}'.format(my_fund_append.shape[0]))
    my_fund_append.to_excel(save_dir, index=False, encoding='utf_8_sig')
    return my_fund_append


def save_fund_portfolio(start_date, end_date, save_dir, market='E', found_date=20210601, query_fund='', query_stock=''):
    """根据基金query_fund_basic.csv总表，循环查询append portfolio"""
    portfolio_total = pd.DataFrame()
    ann_num = 0
    if not query_fund:
        fund = get_data.query_fund_basic(market=market, fund_type=['股票型', '混合型'])
    else:
        fund = pd.read_csv(query_fund)
        fund = fund[fund['fund_type'].isin(['股票型', '混合型'])][fund['market'] == market][fund['found_date'] <= found_date]
    for i, row in fund.iterrows():
        ts_code = row.get('ts_code')
        print('start query: {} {} portfolio data'.format(i, ts_code))
        time.sleep(0.88)
        fio = get_data.append_fund_portfolio_name(ts_code, row.get('name'), start_date, end_date, query_stock)
        if fio.empty:
            print('No {} portfolio data'.format(ts_code))
        else:
            portfolio_total = pd.concat([portfolio_total, fio], axis=0, ignore_index=True)
            ann_num += 1
            print('{} ann date: {}'.format(ts_code, fio.get('end_date').drop_duplicates().tolist()))
    portfolio_total.to_csv(save_dir, index=False, encoding='utf_8_sig')
    print('announce fund number: {}'.format(ann_num))
    return portfolio_total


def save_stock_list(save_dir):
    stock_total = get_data.gen_all_stock_list()
    stock_total.to_csv(save_dir, index=False, encoding='utf_8_sig')


def save_index_ratio(date_query, name_list, save_dir):
    code_rst = get_data.get_index_tscode_by_name(name_list)
    rst_con = get_data.gen_index_yield(date_query, code_rst)
    rst_con.to_csv(save_dir, index=True, encoding='utf_8_sig')
    return rst_con


def analysis_invest_yield(ts_code, date_start, date_end, weekday=4, m_day=20):
    cal_data_tu = get_data.gen_index_daily_data(ts_code, date_start, date_end)
    fix = GenFixedInvest(cal_data_tu, money_amount=500)
    fix_m = GenFixedInvest(cal_data_tu, money_amount=2000)
    invest_data_w = fix.gen_data_week_fixed_invest(weekday=weekday)
    invest_data_m = fix_m.gen_data_month_fixed_invest(month_day=m_day)
    principal_w, final_amount_w, profit_w, buy_num_w, pri_average_w = dca.cal_invest_profit(invest_data_w)
    principal_m, final_amount_m, profit_m, buy_num_m, pri_average_m = dca.cal_invest_profit(invest_data_m)
    print('week: principal: {}, final_amount: {}, profit: {}, buy_num: {}'.format(principal_w, final_amount_w, profit_w,
                                                                                  buy_num_w))
    print(
        'month: principal: {}, final_amount: {}, profit: {}, buy_num: {}'.format(principal_m, final_amount_m, profit_m,
                                                                                 buy_num_m))
    show_r = ShowRst()
    ax = show_r.gen_one_ax()
    show_r.show_cumulative_value(ax, cal_data_tu, invest_data_w, pri_average_w)

    # cal_time = CalTime(date_start, date_end)
    # month_num = cal_time.cal_month_num()
    # x_ticks = cal_time.gen_ticks(month_num)
    val_arr_w = [500] * 50
    val_arr_w.append(-final_amount_w)
    val_arr_m = [2000] * 12
    val_arr_m.append(-final_amount_m)
    rate_w = yc.cal_total_rate(principal_w, final_amount_w)
    rate_m = yc.cal_total_rate(principal_m, final_amount_m)
    rate_w_irr = yc.cal_irr_by_fixed_invest(val_arr_w, 50)
    rate_m_irr = yc.cal_irr_by_fixed_invest(val_arr_m, 12)


def analysis_fund_fio(fio_dir, save_count, count=2):
    sco = dca.count_fund_major_stocks(fio_dir, save_count, count)
    ShowRst().show_fund_major_stocks(sco.iloc[0:51])
    # ShowRst().show_fund_major_stocks(sco.iloc[51:101])
    # ShowRst().show_fund_major_stocks(sco.iloc[101:151])


def select_good_fund(yield_rate_file, fund_type=('股票型', '混合型'), max_net_asset=80):
    fund = pd.read_csv(yield_rate_file)
    fund = fund[fund['fund_type'].isin(fund_type)]
    fund1 = fund[fund['2017'].notna()]
    fund1 = fund1[fund1['net_asset'] < max_net_asset]

    fund1 = fund1[fund1['2022'] >= fund['2022'].median()]
    fund1 = fund1[fund1['2021'] >= fund['2021'].median()]
    # fund1 = fund1[fund1['2021'] >= -5]
    fund1 = fund1[fund1['2020'] >= fund['2020'].median()]
    fund1 = fund1[fund1['2019'] >= fund['2019'].median()]
    fund1 = fund1[fund1['2018'] >= fund['2018'].median()]
    good_fund = fund1.sort_values(by=['2022'], ascending=False)
    if good_fund.shape[0] > 0:
        good_fund.to_csv(r'rst_out\good_fund_sel.csv', index=False, encoding='utf_8_sig')
        logging.info('eligible fund selection done!')
    else:
        logging.warning('there is no eligible fund!')


if __name__ == '__main__':
    save_file = r'.\rst_out\query_fund_basic.csv'
    # save_tu_fund_raw(save_file)

    save_file = r'.\rst_out\query_stock_list.csv'
    # save_stock_list(save_file)

    code, start, end = '000300.SH', '20151231', '20171231'
    # analysis_invest_yield(code, start, end, weekday=4, m_day=20)

    index_name = ['上证指数', '沪深300', '中证500', '上证50', '中证1000', '国证2000', '创业板指', '中证100', '科创50']
    # index_name = ['上证指数', '沪深300', '中证500']
    period_q = {'date_start': ['20111230', '20121231', '20131231', '20141231', '20151231', '20161230', '20171229',
                               '20181228', '20191231', '20201231', '20211231', '20111230'],
                'date_end': ['20121231', '20131231', '20141231', '20151231', '20161231', '20171231', '20181231',
                             '20191231', '20201231', '20211231', '20221231', '20221231'],
                'query_period': ['2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019',
                                 '2020', '2021', '2022', 'all']}
    save_file = r'.\rst_out\index_yield_rate_2023.csv'
    # rst = save_index_ratio(period_q, index_name, save_file)

    # query_type = ('股票型', '混合型', '债券型', '货币市场型', '商品型', '另类投资型')
    query_type = ['债券型']
    # query_type = ('股票型', '混合型', '商品型', '另类投资型')
    query_basic_file = r'final_data/query_db/query_fund_basic.csv'
    # save_file = r'rst_out\fund_yield_rate_stock_202301.csv'
    save_file = r'rst_out\fund_yield_rate_bond_O_202301.csv'
    # fund_all = save_tu_fund_append(period_q, save_file, found_date_sel='20200201', market='O', fund_type=query_type,
    #                                query_file=query_basic_file)

    # period_q = {'date_start': ['20211231'],
    #             'date_end': ['20221231'],
    #             'query_period': ['2022']}
    period_q = {'date_start': ['20161230', '20171229', '20181228', '20191231', '20201231', '20211231',  '20161230'],
                'date_end': ['20171231', '20181231', '20191231', '20201231', '20211231', '20221231', '20221231'],
                'query_period': ['2017', '2018', '2019', '2020', '2021', '2022', 'all']}
    save_file = r'rst_out\my_fund_2022.xlsx'
    my_fund_file = r'final_data\query_db\my_fund_raw.xlsx'
    query_basic_f = r'final_data\query_db\query_fund_basic.csv'
    # query_basic_f = None
    fund_ab = save_my_fund(period_q, save_file, my_fund_file, query_basic_f)

    query_stock_file = r'final_data\query_db\query_stock_list.csv'
    query_fund_file = r'rst_out\my_fund_2022.csv'
    # query_fund_file = r'final_data\query_db\query_fund_basic.csv'
    save_fio_file = r'rst_out\fio_all_20211231.csv'
    save_count_file = r'rst_out\fio_count_all_20211231.csv'
    # portfolio_t = save_fund_portfolio('20211230', '20220201', save_fio_file, market='E', found_date=20210601,
    #                                   query_fund=query_fund_file, query_stock=query_stock_file)
    # analysis_fund_fio(save_fio_file, save_count_file, count=1)

    fund_file = r'rst_out\exchange_fund_yield_rate_202301.csv'
    # select_good_fund(fund_file, fund_type=('股票型', '混合型'), max_net_asset=100)
