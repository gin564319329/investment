"""
主程序： 调用utils各工具，保存生成各类自定义分析数据、已确定策略的基金筛选等
Author  : Jiang
"""

from utils.data_generator import GenCustomData
from utils.show_rst import ShowRst
from utils import data_statistics
import time
import os
import pandas as pd
import logging


logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s %(message)s',
#                     datefmt='%d %b %Y, %H:%M',
#                     filename=r'rst_out/run_fund.log',
#                     filemode='a')
get_data = GenCustomData()


def save_fund_raw(save_dir):
    """保存当前市场所有基金 基础信息 包括开放型与封闭型"""
    fund_total = get_data.gen_raw_fund_list()
    logging.info('fund number: {}'.format(fund_total.shape[0]))
    fund_total.to_csv(save_dir, index=False, encoding='utf_8_sig')
    return fund_total


def save_stock_list(save_dir):
    """保存当前市场所有股票 基础信息"""
    stock_total = get_data.gen_all_stock_list()
    logging.info('stock number: {}'.format(stock_total.shape[0]))
    stock_total.to_csv(save_dir, index=False, encoding='utf_8_sig')
    return stock_total


def save_fund_append(period_query, save_dir, found_date_sel='20210601', fund_type=('股票型', '混合型'), market=None,
                     query_file=None):
    """保存当前市场，按条件筛选基金的基础信息以及扩展信息，包括basic信息，规模信息 net_asset 基金年度收益率信息"""
    if query_file is None:
        fund = None
    elif market is None:
        fund = pd.read_csv(query_file)
        fund = fund[fund['fund_type'].isin(fund_type)]
    else:
        fund = pd.read_csv(query_file)
        fund = fund[fund['fund_type'].isin(fund_type)][fund['market'] == market]

    fund_info = get_data.append_fund_basic(period_query, found_date_sel, market, fund_type, fund)
    logging.info('select append fund number: {}'.format(fund_info.shape[0]))
    fund_info.to_csv(save_dir, index=False, encoding='utf_8_sig')
    return fund_info


def save_my_fund(period_query, save_dir, my_file, query_file=None):
    """ save my selective fund: append info - fund manager, net asset info..."""
    my_fund = pd.read_excel(my_file, sheet_name=0, dtype={'code': str})
    if query_file is None:
        query_info = None
    else:
        query_info = pd.read_csv(query_file)
    my_fund_basic = get_data.gen_self_fund_list(my_fund, query_basic=query_info)
    my_fund_append = get_data.append_fund_basic(period_query, fund_basic=my_fund_basic)
    my_fund_append.to_excel(save_dir, index=False, encoding='utf_8_sig')
    # my_fund_append.to_csv(save_dir, index=False, encoding='utf_8_sig')
    return my_fund_append


def save_fund_portfolio(start_date, end_date, save_dir, market='E', found_date=20210601, query_fund='', query_stock=''):
    """根据基金query_fund_basic.csv总表，循环查询append portfolio"""
    portfolio_total = pd.DataFrame()
    ann_num = 0
    if not query_fund:
        fund = get_data.query_fund_basic(market='E', fund_type=['股票型', '混合型'])
        fund = fund[fund['found_date'] <= found_date]
    elif not market:
        fund = pd.read_csv(query_fund)
        fund = fund[fund['fund_type'].isin(['股票型', '混合型'])][fund['found_date'] <= found_date]
    else:
        fund = pd.read_csv(query_fund)
        fund = fund[fund['fund_type'].isin(['股票型', '混合型'])][fund['market'] == market][fund['found_date'] <= found_date]
    for i, row in fund.iterrows():
        ts_code = row.get('ts_code')
        print('start query: {} {} portfolio data'.format(i, ts_code))
        time.sleep(0.89)
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


def save_index_ratio(date_query, name_list, save_dir):
    code_rst = get_data.get_index_tscode_by_name(name_list)
    rst_con = get_data.gen_index_yield(date_query, code_rst)
    rst_con.to_csv(save_dir, index=True, encoding='utf_8_sig')
    return rst_con


def analysis_fund_fio(fio_dir, save_count, count=2):
    sco = data_statistics.get_fund_major_stocks(fio_dir, save_count, count)
    ShowRst().show_fund_major_stocks(sco.iloc[0:51])
    # ShowRst().show_fund_major_stocks(sco.iloc[51:101])
    # ShowRst().show_fund_major_stocks(sco.iloc[101:151])


def select_good_fund(query_fund, base_fund, save_sel_file, fund_type=('股票型', '混合型'), max_net_asset=80):
    base = pd.read_csv(base_fund)
    base = base[base['fund_type'].isin(fund_type)]
    if os.path.basename(query_fund).endswith('csv'):
        query = pd.read_csv(query_fund)
    elif os.path.basename(query_fund).endswith('xlsx'):
        query = pd.read_excel(query_fund, sheet_name=0)
    else:
        logging.error('wrong file type!')
        return
    query = query[query['fund_type'].isin(fund_type)]
    query = query[query['2017'].notna()]
    query = query[query['net_asset'] < max_net_asset]

    query = query[query['2022'] >= base['2022'].median()]
    query = query[query['2021'] >= base['2021'].median()]
    # fund1 = fund1[fund1['2021'] >= -5]
    query = query[query['2020'] >= base['2020'].median()]
    query = query[query['2019'] >= base['2019'].median()]
    query = query[query['2018'] >= base['2018'].median()]
    good_fund = query.sort_values(by=['2022'], ascending=False)
    if good_fund.shape[0] > 0:
        good_fund.to_csv(save_sel_file, index=False, encoding='utf_8_sig')
        logging.info('eligible fund selection done!')
    else:
        logging.warning('there is no eligible fund!')


if __name__ == '__main__':
    """保存当前市场所有基金"""
    raw_fund = r'data/rst_out\query_fund_basic.csv'
    # save_fund_raw(raw_fund)

    """保存当前市场所有股票"""
    raw_stock = r'data/rst_out\query_stock_list.csv'
    # save_stock_list(raw_stock)

    """保存各宽基指数年度涨跌幅"""
    # index_name = ['上证指数', '沪深300', '中证500', '上证50', '中证1000', '国证2000', '创业板指', '中证100', '科创50']
    index_name = ['上证指数', '沪深300', '中证500']
    period_q = {'date_start': ['20111230', '20121231', '20131231', '20141231', '20151231', '20161230', '20171229',
                               '20181228', '20191231', '20201231', '20211231', '20221230', '20111230'],
                'date_end': ['20121231', '20131231', '20141231', '20151231', '20161231', '20171231', '20181231',
                             '20191231', '20201231', '20211231', '20221231', '20231231', '20231231'],
                'query_period': ['2012', '2013', '2014', '2015', '2016', '2017', '2018',
                                 '2019', '2020', '2021', '2022', '2023', 'all']}
    # period_q = {'date_start': ['20171229', '20181228', '20191231', '20201231', '20211231'],
    #             'date_end': ['20230121', '20230121', '20230121', '20230121', '20230121'],
    #             'query_period': ['last 5 year', 'last 4 year', 'last 3 year', 'last 2 year', 'last 1 year']}
    index_file = r'data/rst_out\index_yield_rate_2023.csv'
    # rst = save_index_ratio(period_q, index_name, index_file)

    """保存当前市场，按条件筛选基金的基础信息以及扩展信息（涨跌幅等）"""
    # query_type = ('股票型', '混合型', '债券型', '货币市场型', '商品型', '另类投资型')
    # query_type = ['债券型']
    query_type = ('股票型', '混合型')
    found_date = '20190101'
    query_basic_file = r'data/final_data/query_db/query_fund_basic.csv'
    # append_fund = r'data/rst_out\yield_rate_fond_fund_last202301.csv'
    append_fund = r'data/rst_out\yield_rate_stock_fund_last20230804.csv'
    # fund_all = save_fund_append(period_q, append_fund, found_date, fund_type=query_type, query_file=query_basic_file)

    """保存我的自选基金的基础信息以及扩展信息（涨跌幅等）"""
    period_q = {
        'date_start': ['20161230', '20171229', '20181228', '20191231', '20201231', '20211231', '20221230', '20161230'],
        'date_end': ['20171231', '20181231', '20191231', '20201231', '20211231', '20221231', '20231231', '20231231'],
        'query_period': ['2017', '2018', '2019', '2020', '2021', '2022', '2023', 'all']}
    save_file = r'data/rst_out\my_fund_202308.xlsx'
    my_fund_file = r'data/final_data\query_db\my_fund_raw.xlsx'
    query_basic_f = r'data/final_data\query_db\query_fund_basic.csv'
    # fund_ab = save_my_fund(period_q, save_file, my_fund_file, query_basic_f)

    """保存基金持仓股票数据"""
    query_stock_file = r'data/final_data\query_db\query_stock_list.csv'
    # query_fund_file = r'rst_out\my_fund_2023.csv'
    query_fund_file = r'data/final_data\query_db\query_fund_basic.csv'
    save_fio_file = r'data/rst_out\fio_all_202212.csv'
    save_count_file = r'data/rst_out\fio_count_all_202212.csv'
    # portfolio_t = save_fund_portfolio('20221228', '20230130', save_fio_file, market='', found_date=20220601,
    #                                   query_fund=query_fund_file, query_stock=query_stock_file)
    # analysis_fund_fio(save_fio_file, save_count_file, count=1)

    b_fund_file = r'data/final_data\yield_rate_stock_fund_202301.csv'
    q_fund_file = r'data/final_data\yield_rate_stock_fund_202301.csv'
    # q_fund_file = r'final_data/my_fund_202301.xlsx'
    save_file = r'data/rst_out\good_my_fund.csv'
    # select_good_fund(q_fund_file, b_fund_file, save_file, fund_type=('股票型', '混合型'), max_net_asset=100)
