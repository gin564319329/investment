"""
Query basic market data based on tuShare API
Generate advanced market data based on QueryTuShareData class
Author  : Jiang
"""

import time
import pandas as pd
import tushare as ts
import logging
import numpy as np
import os
from datetime import date, datetime
import data_statistics as dca


class QueryTuShareData:

    def __init__(self):
        ts.set_token('a191d192213fbcb32f37352ae88d571a7150c06f855a32aa6b1f8c16')
        self.pro = ts.pro_api()

    def query_index_daily(self, ts_code, start_date, end_date):
        """查询指数日线交易信息 可以获取包括开盘价 收盘价 成交量等"""
        df = self.pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        df_sort = df.sort_values(by=['trade_date'], ascending=True).reset_index(drop=True)
        return df_sort

    def query_index_basic(self, ts_code, name, market='CSI'):
        """查询指数基础信息"""
        return self.pro.index_basic(ts_code=ts_code, name=name, market=market)

    def query_fund_basic(self, market='E', status='L', fund_type=None):
        """获取基金列表 基础信息； 交易市场: E场内 O场外（默认E）;  存续状态: D摘牌 I发行 L上市中"""
        if fund_type is None:
            fund_type = []
        if market == 'E':
            fund_raw = self.pro.fund_basic(**{"market": market, "status": status},
                                           fields=['ts_code', 'name', 'management', 'found_date', 'fund_type',
                                                   'invest_type', 'benchmark', 'm_fee', 'c_fee', 'market'])
        elif market == 'O':
            fund_part1 = self.pro.fund_basic(**{"market": market, "offset": 0, "limit": 10000, "status": status},
                                             fields=['ts_code', 'name', 'management', 'found_date', 'fund_type',
                                                     'invest_type', 'benchmark', 'm_fee', 'c_fee', 'market'])
            fund_part2 = self.pro.fund_basic(**{"market": market, "offset": 10000, "limit": 10000, "status": status},
                                             fields=['ts_code', 'name', 'management', 'found_date', 'fund_type',
                                                     'invest_type', 'benchmark', 'm_fee', 'c_fee', 'market'])
            fund_raw = pd.concat([fund_part1, fund_part2], axis=0)
        else:
            return None
        logging.info('query {} fund total number: {}'.format(market, fund_raw.shape[0]))
        if not fund_type:
            fund_sel = fund_raw.copy()
        else:
            fund_sel = fund_raw[fund_raw['fund_type'].isin(fund_type)]
        return fund_sel

    def query_fund_daily(self, ts_code, start_date='', end_date=''):
        """获取场内基金日线行情，类似股票日行情"""
        df = self.pro.fund_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        df_sort = df.sort_values(by=['trade_date'], ascending=True).reset_index(drop=True)
        return df_sort

    def query_fund_nav(self, ts_code, start_date='', end_date=''):
        """获取公募基金净值数据 含场内与场外"""
        try:
            nav_raw = self.pro.fund_nav(ts_code=ts_code, start_date=start_date, end_date=end_date)
            nav_sel = nav_raw.get(['ts_code', 'nav_date', 'unit_nav', 'accum_nav', 'adj_nav', 'net_asset'])
        except Exception as terror:
            logging.error('-- Tushare System Error: {}'.format(terror))
            nav_raw, nav_sel = pd.DataFrame(), pd.DataFrame()
        if nav_raw.empty:
            return nav_sel
        if nav_sel['net_asset'][0] is None:
            return nav_sel.drop_duplicates(["nav_date"], keep="last")
        nav_sel_copy = nav_sel.copy()
        nav_sel_copy['net_asset'] = (nav_sel['net_asset'] / 1e8).round(2)
        return nav_sel_copy.drop_duplicates(["nav_date"], keep="last")

    def query_fund_manager(self, ts_code):
        return self.pro.fund_manager(ts_code=ts_code)

    def query_fund_share(self, ts_code):
        """获取基金规模数据，包含上海和深圳ETF基金 fd_share 基金份额 亿份"""
        fund_share = self.pro.fund_share(ts_code=ts_code)
        share_y = fund_share['fd_share'] / 1e4
        fund_share['fd_share'] = share_y.round(decimals=2)
        return fund_share.get(['ts_code', 'trade_date', 'fd_share'])

    def query_fund_portfolio(self, ts_code, start_date='', end_date=''):
        """获取公募基金持仓数据，季度更新 end_date 季报日期"""
        return self.pro.fund_portfolio(ts_code=ts_code, start_date=start_date, end_date=end_date)

    def query_ts_code_by_code(self, code, market='E', fund_db=None):
        """查询tushare基金代码"""
        if fund_db is None:
            fund_db = self.query_fund_basic(market=market, status='L')
        for ts_code in fund_db['ts_code']:
            if code in ts_code:
                return ts_code
        logging.warning('there is no {} fund'.format(code))
        return None

    def query_stock_name(self, ts_code=''):
        """根据代码查询股票名称 ts_code=''为查询所有股票列表"""
        return self.pro.stock_basic(ts_code=ts_code)

    def query_stock_daily(self, ts_code, query_date):
        """查询股票日线行情数据"""
        return self.pro.daily(ts_code=ts_code, start_date=query_date, end_date=query_date)


class GenCustomData(QueryTuShareData):

    def __init__(self):
        super(GenCustomData, self).__init__()
        self.op = dca

    def gen_index_daily_data(self, ts_code, date_start, date_end):
        """获取指数日线交易收盘点位信息，并包括年月日、星期"""
        tu_data = self.query_index_daily(ts_code, date_start, date_end)
        index_for_cal = self.gen_cal_data(tu_data)
        return index_for_cal

    def get_index_tscode_by_name(self, search_list):
        df_sh = self.query_index_basic('', '', market='SSE')
        df_sz = self.query_index_basic('', '', market='SZSE')
        ts_dict = {'ts_code': [], 'name': []}

        for index, s in df_sh.iterrows():
            if s['name'] in search_list:
                search_list.remove(s['name'])
                print('{}\t代码:\t {}'.format(s['name'], s['ts_code']))
                ts_dict['ts_code'].append(s['ts_code'])
                ts_dict['name'].append(s['name'])

        for index, s in df_sz.iterrows():
            if s['name'] in search_list:
                search_list.remove(s['name'])
                print('{}\t代码:\t {}'.format(s['name'], s['ts_code']))
                ts_dict['ts_code'].append(s['ts_code'])
                ts_dict['name'].append(s['name'])
        return ts_dict

    @staticmethod
    def gen_cal_data(raw_data):
        cal_data = pd.DataFrame()
        cal_data['date'] = raw_data['trade_date']
        weekday_list = []
        day_list = []
        month_list = []
        year_list = []
        for da in raw_data['trade_date']:
            weekday_list.append(datetime.strptime(da, "%Y%m%d").weekday() + 1)
            day_list.append(datetime.strptime(da, "%Y%m%d").day)
            month_list.append(datetime.strptime(da, "%Y%m%d").month)
            year_list.append(datetime.strptime(da, "%Y%m%d").year)
        cal_data['year'] = year_list
        cal_data['month'] = month_list
        cal_data['day'] = day_list
        cal_data['weekday'] = weekday_list
        cal_data['price'] = raw_data['close']
        return cal_data

    def gen_index_yield(self, date_query, index_query):
        """生成指数年度收益率及定投收益率表格"""
        index_yield = pd.DataFrame(index=date_query['query_period'])
        for start, end, per in zip(date_query['date_start'], date_query['date_end'], date_query['query_period']):
            for code, name in zip(index_query.get('ts_code'), index_query.get('name')):
                index_data = self.gen_index_daily_data(code, start, end)
                fix = GenFixedInvest(index_data, money_amount=500)
                invest_data = fix.gen_data_week_fixed_invest(weekday=4)
                ch_ratio = self.op.get_index_change_ratio(index_data)
                in_ratio = self.op.get_fixed_inv_change_ratio(invest_data)
                index_yield.at[per, '{}_涨幅'.format(name)] = ch_ratio
                index_yield.at[per, '{}_定投'.format(name)] = in_ratio
                if ch_ratio is not None and in_ratio is not None:
                    print('{} {} change ratio: {:.2%}'.format(per, name, ch_ratio))
                    print('{} {} irri profit: {:.2%}'.format(per, name, in_ratio))
                else:
                    print('None {} {} change ratio is {}'.format(per, name, in_ratio))
        ch_df = index_yield[[a for a in index_yield.columns if '涨幅' in a]]
        in_df = index_yield[[a for a in index_yield.columns if '定投' in a]]
        ch_df_a = self.op.get_index_minmax(ch_df, '涨幅')
        in_df_a = self.op.get_index_minmax(in_df, '定投')

        return pd.concat([ch_df_a, in_df_a], axis=1)

    def gen_raw_fund_list(self):
        """generate fund basic info list: exchange and open """
        fund_e = self.query_fund_basic(market='E')
        fund_o = self.query_fund_basic(market='O')
        return pd.concat([fund_e, fund_o], axis=0)

    def append_fund_basic(self, period_query, found_date_sel='20220101', market='E', fund_type=None, fund_basic=None):
        """增加fund_basic 规模信息 net_asset 亿元 基金年度收益率信息 基金经理"""
        if fund_basic is None:
            fund_basic = self.query_fund_basic(market=market, fund_type=fund_type)
        fund_b_sel = fund_basic[fund_basic['found_date'].astype('str') < found_date_sel]
        fund_b_sel.reset_index(drop=True, inplace=True)
        fund_append = fund_b_sel.copy()
        for index, row in fund_b_sel.iterrows():
            manager = self.query_fund_manager(row.get('ts_code'))
            fund_append.at[index, 'manager'] = ' '.join(manager[manager['end_date'].isnull()].get('name').tolist())
            time.sleep(0.65)
            fund_nav = self.query_fund_nav(row.get('ts_code'), start_date=period_query['date_start'][0])
            if fund_nav is None:
                logging.warning('No.{} {} fail to query: is None'.format(index, row.get('ts_code')))
                continue
            if fund_nav.empty:
                logging.warning('No.{} {} fail to query: is empty'.format(index, row.get('ts_code')))
                continue
            print('---append {} {} {}'.format(index, row.get('ts_code'), row.get('name')))
            fund_append.at[index, 'net_asset'], fund_append.at[index, 'ann_date'] = \
                self.op.get_newest_net_asset(fund_nav)
            for start, end, per in zip(period_query['date_start'], period_query['date_end'],
                                       period_query['query_period']):
                fund_nav_t = fund_nav[fund_nav['nav_date'].astype('str') >= start]
                fund_nav_sel = fund_nav_t[fund_nav_t['nav_date'].astype('str') <= end]
                if fund_nav_sel.empty:
                    fund_append.at[index, per] = np.NAN
                    print('{} {} no data'.format(per, row.get('name')))
                    continue
                fund_append.at[index, per] = self.op.get_fund_change_ratio(fund_nav_sel)
                print('{} {} fund yield rate: {:.2%}'.format(per, row.get('name'), fund_append.at[index, per]))

        return fund_append

    def append_fund_portfolio_name(self, fund_code, fund_name, start_date, end_date, input_file=''):
        """根据基金代码append基金持仓股票名称
        end_date 截止日期
        symbol 股票代码
        mkv	持有股票市值(亿元) - 根据原始数据换算
        amount 持有股票数量（万股）- 根据原始数据换算
        stk_float_ratio 占流通股本比例(%)"""
        try:
            portfolio = self.query_fund_portfolio(fund_code, start_date=start_date, end_date=end_date)
        except Exception as terr:
            print('fail to query {} fund_portfolio: {}'.format(fund_code, terr))
            return pd.DataFrame()
        if not input_file:
            stock_db = self.query_stock_name()
        else:
            stock_db = pd.read_csv(input_file)
        stock_bat = portfolio.copy()
        for i, row in portfolio.iterrows():
            stock_name = stock_db[stock_db['ts_code'] == row.get('symbol')].get('name')
            if stock_name.empty:
                print('fail to query {} name'.format(row.get('symbol')))
                stock_bat.at[i, 'stock_name'] = ''
                continue
            stock_bat.at[i, 'stock_name'] = stock_name.iloc[0]
        stock_bat['mkv'] = stock_bat['mkv'] / 1e8
        stock_bat['amount'] = stock_bat['amount'] / 1e4
        stock_bat['fund_name'] = fund_name
        return stock_bat.drop(['ann_date', 'stk_mkv_ratio'], axis=1)

    @staticmethod
    def append_portfolio_offline(portfolio_file='', fund_file=''):
        portfolio = pd.read_csv(portfolio_file)
        fund_db = pd.read_csv(fund_file)
        port_a = portfolio.copy()
        for i, row in portfolio.iterrows():
            fund_name = fund_db[fund_db['ts_code'] == row.get('ts_code')].get('name')
            try:
                port_a.at[i, 'fund_name'] = fund_name.iloc[0]
            except Exception as trr:
                print(' fail to append {} {} name: {}'.format(i, row.get('ts_code'), trr))
                port_a.at[i, 'fund_name'] = None
        return port_a

    def gen_self_fund_list(self, my_fund, query_basic=None):
        """process my self fund: add fund manager, net asset info..."""
        if query_basic is None:
            query_basic = self.gen_raw_fund_list()
        my_fund_a = pd.DataFrame(columns=query_basic.columns)
        for i, row in my_fund.iterrows():
            ts_code = self.query_ts_code_by_code(row.get('code'), fund_db=query_basic)
            if ts_code is not None:
                my_fund_a.loc[i, :] = query_basic[query_basic['ts_code'] == ts_code].values
            else:
                logging.error('error code: {}'.format(row.get('code')))
        return my_fund_a

    def gen_all_stock_list(self):
        """generate all market stock list: status L"""
        stock_total = self.query_stock_name(ts_code='')
        stock_total = stock_total.drop(['symbol'], axis=1)
        return stock_total


class GenFixedInvest:

    def __init__(self, df_market_data, money_amount):
        self.market_data = df_market_data
        self.money_a = money_amount

    def gen_data_week_fixed_invest(self, weekday):
        """未考虑节假日"""
        df_invest_data = self.market_data[self.market_data['weekday'] == weekday].copy()
        df_invest_data['money'] = self.money_a
        df_invest_data['share'] = self.money_a / df_invest_data['price']
        return df_invest_data

    def gen_data_month_fixed_invest(self, month_day):
        date_list = []
        day_invest_list = []
        df_invest_data = pd.DataFrame()
        for year in self.market_data['year'].drop_duplicates():
            year_invest_data = self.market_data[self.market_data['year'] == year].copy()
            for month in year_invest_data['month'].drop_duplicates():
                self.select_trade_day(date_list, day_invest_list, year_invest_data, year, month, month_day)
        df_invest_data['date'] = date_list
        df_invest_data['price'] = day_invest_list
        df_invest_data['money'] = self.money_a
        df_invest_data['share'] = self.money_a / df_invest_data['price']
        return df_invest_data

    @staticmethod
    def select_trade_day(date_list, day_invest_list, year_invest_data, year, month, month_day):
        """月定投日-非交易日处理"""
        month_invest_data = year_invest_data[year_invest_data['month'] == month]
        day_invest_data = month_invest_data[month_invest_data['day'] == month_day].copy()
        if month_day in month_invest_data['day'].values:
            day_invest_list.append(float(day_invest_data['price'].values))
            date_list.append(date(year, month, month_day).strftime("%Y%m%d"))
        else:
            df_sup_day = month_invest_data['day'].values - month_day
            if df_sup_day[df_sup_day < 0].size > 0:
                sup_day = df_sup_day[df_sup_day < 0].max() + month_day
            else:
                sup_day = df_sup_day[df_sup_day > 0].min() + month_day
            day_invest_data = month_invest_data[month_invest_data['day'] == sup_day].copy()
            day_invest_list.append(float(day_invest_data['price'].values))
            date_list.append(date(year, month, sup_day).strftime("%Y%m%d"))


if __name__ == '__main__':
    cus_data = GenCustomData()
    # index_data = cus_data.get_index_daily_data('000001.SH', '20201231', '20211231')
    # ch_r = cus_data.op.cal_index_change_ratio(index_data)
    # in_r = cus_data.op.cal_fixed_inv_change_ratio(index_data)
    # print('change rate: {:.2%}'.format(ch_r))
    # print('irri rate: {:.2%}'.format(in_r))

    # fund_b = r'rst_out\fund_basic_exchange_raw.csv'
    # portfolio_raw = r'rst_out\fio_exchange.csv'
    # port_e = cus_data.append_portfolio_offline(portfolio_raw, fund_b)
    # port_e.to_csv(r'rst_out\fio_append_f2.csv', index=False, encoding='utf_8_sig')
