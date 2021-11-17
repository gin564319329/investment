from datetime import datetime, timedelta
import numpy as np
import time
import pandas as pd
import matplotlib.pyplot as plt
import tushare as ts
from datetime import datetime, timedelta


class GetCsvData:
    def __init__(self):
        pass

    @staticmethod
    def get_k_data_by_163(index_id='0000300', date_start="20000101", date_end="20200320"):
        data_api = "http://quotes.money.163.com/service/chddata.html?code={}&start={}&end={}&fields=TCLOSE;HIGH;LOW;TOPEN;" \
                   "LCLOSE;CHG;PCHG;VOTURNOVER;VATURNOVER".format(index_id, date_start, date_end)
        data_info = pd.read_csv(data_api, encoding='gb2312')
        # data = data_info.loc[(data_info.index > datetime.strptime(date_start, "%Y%m%d").strftime("%Y-%d-%m"))
        #                      & (data_info.index < datetime.strptime(date_end, "%Y%m%d").strftime("%Y-%d-%m"))]
        data_info = data_info.sort_values(by=['日期'], ascending=True).reset_index(drop=True)
        return data_info

    @staticmethod
    def gen_cal_data(raw_data):
        cal_data = pd.DataFrame()
        cal_data['date'] = raw_data['日期']
        weekday_list = []
        day_list = []
        month_list = []
        year_list = []
        for da in raw_data['日期']:
            weekday_list.append(datetime.strptime(da, "%Y-%m-%d").weekday() + 1)
            day_list.append(datetime.strptime(da, "%Y-%m-%d").day)
            month_list.append(datetime.strptime(da, "%Y-%m-%d").month)
            year_list.append(datetime.strptime(da, "%Y-%m-%d").year)
        cal_data['year'] = year_list
        cal_data['month'] = month_list
        cal_data['day'] = day_list
        cal_data['weekday'] = weekday_list
        cal_data['price'] = raw_data['收盘价']
        return cal_data


class GetTuShareData:

    def __init__(self):
        ts.set_token('a191d192213fbcb32f37352ae88d571a7150c06f855a32aa6b1f8c16')
        self.pro = ts.pro_api()

    def get_index_daily(self, ts_code, start_date, end_date):
        df = self.pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        df_sort = df.sort_values(by=['trade_date'], ascending=True).reset_index(drop=True)
        # df_sort.to_csv('D:\\2 Project codes\\investment\\data\\300_pro.csv')
        return df_sort

    def get_index_basic(self, ts_code, name, market):
        return self.pro.index_basic(ts_code=ts_code, name=name, market=market)

    def get_fund_basic(self, market='E', status='L'):
        """交易市场: E场内 O场外（默认E）;  存续状态: D摘牌 I发行 L上市中"""
        fund_raw = self.pro.fund_basic(market=market, status=status)
        return fund_raw.get(['ts_code', 'name', 'management', 'found_date', 'fund_type', 'invest_type', 'benchmark'])

    def get_fund_daily(self, ts_code, start_date='', end_date=''):
        """获取场内基金日线行情，类似股票日行情"""
        df = self.pro.fund_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        df_sort = df.sort_values(by=['trade_date'], ascending=True).reset_index(drop=True)
        return df_sort

    def get_fund_nav(self, ts_code, start_date='', end_date=''):
        """获取公募基金净值数据 含场内与场外"""
        nav_raw = self.pro.fund_nav(ts_code=ts_code, start_date=start_date, end_date=end_date)
        nav_sel = nav_raw.get(['ts_code', 'nav_date', 'unit_nav', 'accum_nav', 'adj_nav', 'net_asset'])
        if nav_raw.empty:
            return nav_sel
        if nav_sel['net_asset'][0] is None:
            return nav_sel.drop_duplicates(["nav_date"], keep="last")
        nav_sel_copy = nav_sel.copy()
        nav_sel_copy['net_asset'] = (nav_sel['net_asset']/1e8).round(2)
        return nav_sel_copy.drop_duplicates(["nav_date"], keep="last")

    def get_fund_manager(self, ts_code):
        return self.pro.fund_manager(ts_code=ts_code)

    def get_fund_share(self, ts_code):
        """获取基金规模数据，包含上海和深圳ETF基金 fd_share 基金份额 亿份"""
        fund_share = self.pro.fund_share(ts_code=ts_code)
        share_y = fund_share['fd_share']/1e4
        fund_share['fd_share'] = share_y.round(decimals=2)
        return fund_share.get(['ts_code', 'trade_date', 'fd_share'])

    def get_fund_portfolio(self, ts_code, end_date):
        """获取公募基金持仓数据，季度更新 end_date 季报日期"""
        return self.pro.fund_portfolio(ts_code=ts_code, end_date=end_date)

    def get_stock_name(self, ts_code):
        """根据代码查询股票名称"""
        return self.pro.stock_basic(ts_code=ts_code)['name']

    def get_stock_name_batch(self, ts_code_list):
        """根据代码批量查询股票名称"""
        stock_dict = {'ts_code': [], 'name': []}
        for code in ts_code_list:
            stock_dict.get('ts_code').append(code)
            stock_dict.get('name').append(self.pro.stock_basic(ts_code=code)['name'][0])
        return pd.DataFrame().from_dict(stock_dict)

    def search_net_asset(self, ts_code, start_date=''):
        nav = self.get_fund_nav(ts_code, start_date=start_date)
        if not nav['net_asset'].notnull().sum():
            return None, None
        return nav['net_asset'][nav['net_asset'].notnull()].iloc[0], nav['nav_date'][nav['net_asset'].notnull()].iloc[0]

    def append_fund_basic(self, fund_type='', start_date='', market='E', save_dir=''):
        fund_e = self.get_fund_basic(market=market)
        if not fund_type:
            fund_sel = fund_e.copy()
        else:
            fund_sel = fund_e[fund_e['fund_type'] == fund_type]
        fund_append = fund_sel.copy()
        for row in fund_sel.itertuples():
            print(row.Index, getattr(row, 'ts_code'))
            time.sleep(0.8)
            fund_append.loc[row.Index, 'net_asset'],  fund_append.loc[row.Index, 'ann_date'] = \
                self.search_net_asset(getattr(row, 'ts_code'), start_date=start_date)
        fund_append.to_csv(save_dir, encoding='utf_8_sig')
        return fund_append

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


if __name__ == '__main__':
    index_id = '0000300'
    date_start = '20200101'
    date_end = '20211031'
    gd = GetCsvData()
    raw_data_t = gd.get_k_data_by_163(index_id, date_start, date_end)
    cal_data_t = gd.gen_cal_data(raw_data_t)
