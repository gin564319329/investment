import time
import pandas as pd
import tushare as ts
from datetime import datetime, timedelta
import logging


class GetTuShareData:

    def __init__(self):
        ts.set_token('a191d192213fbcb32f37352ae88d571a7150c06f855a32aa6b1f8c16')
        self.pro = ts.pro_api()

    def query_index_daily(self, ts_code, start_date, end_date):
        df = self.pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        df_sort = df.sort_values(by=['trade_date'], ascending=True).reset_index(drop=True)
        return df_sort

    def query_index_basic(self, ts_code, name, market='CSI'):
        """获取指数列表 基础信息"""
        return self.pro.index_basic(ts_code=ts_code, name=name, market=market)

    def query_fund_basic(self, market='E', status='L', fund_type=None):
        """获取基金列表 基础信息； 交易市场: E场内 O场外（默认E）;  存续状态: D摘牌 I发行 L上市中"""
        if fund_type is None:
            fund_type = []
        fund_raw = self.pro.fund_basic(market=market, status=status)
        fund_raw = fund_raw.get(['ts_code', 'name', 'management', 'found_date', 'fund_type', 'invest_type', 'benchmark',
                                 'm_fee', 'c_fee'])
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
        nav_raw = self.pro.fund_nav(ts_code=ts_code, start_date=start_date, end_date=end_date)
        nav_sel = nav_raw.get(['ts_code', 'nav_date', 'unit_nav', 'accum_nav', 'adj_nav', 'net_asset'])
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

    def query_fund_portfolio(self, ts_code, end_date):
        """获取公募基金持仓数据，季度更新 end_date 季报日期"""
        return self.pro.fund_portfolio(ts_code=ts_code, end_date=end_date)

    def query_ts_code_by_code(self, code, market='E'):
        """查询tushare基金代码"""
        fund_bat = self.query_fund_basic(market=market, status='L')
        for ts_code in fund_bat['ts_code']:
            if code in ts_code:
                return ts_code
        logging.warning('there is no {} fund'.format(code))
        return None

    def query_stock_name(self, ts_code):
        """根据代码查询股票名称"""
        return self.pro.stock_basic(ts_code=ts_code)['name'][0]

    def query_stock_name_batch(self, ts_code_bat):
        """根据代码批量查询股票名称"""
        stock_df = pd.DataFrame(ts_code_bat.values, columns=['st_code'])
        stock_bat = stock_df.copy()
        for i, row in stock_df.iterrows():
            stock_bat.at[i, 'st_name'] = self.query_stock_name(getattr(row, 'st_code'))
        return stock_bat

    def search_net_asset(self, ts_code, start_date=''):
        nav = self.query_fund_nav(ts_code, start_date=start_date)
        if not nav['net_asset'].notnull().sum():
            return None, None
        return nav['net_asset'][nav['net_asset'].notnull()].iloc[0], nav['nav_date'][nav['net_asset'].notnull()].iloc[0]

    def append_fund_basic(self, fund_basic, start_date=''):
        """增加净资产信息"""
        fund_append = fund_basic.copy()
        for row in fund_basic.itertuples():
            print(row.Index, getattr(row, 'ts_code'))
            time.sleep(0.8)
            fund_append.loc[row.Index, 'net_asset'], fund_append.loc[row.Index, 'ann_date'] = \
                self.search_net_asset(getattr(row, 'ts_code'), start_date=start_date)
        return fund_append

    def append_fund_portfolio_name(self, ts_code, end_date):
        portfolio = self.query_fund_portfolio(ts_code, end_date)
        folio = self.query_stock_name_batch(portfolio['symbol'])
        return pd.concat([portfolio, folio['st_name']], axis=1)

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
