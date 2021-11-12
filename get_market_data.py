from datetime import datetime, timedelta
import numpy as np
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

    def get_fund_daily(self, ts_code, start_date, end_date):
        """获取场内基金日线行情，类似股票日行情"""
        df = self.pro.fund_nav(ts_code=ts_code, start_date=start_date, end_date=end_date)
        # df_sort = df.sort_values(by=['trade_date'], ascending=True).reset_index(drop=True)
        return df

    def get_fund_nav(self, ts_code, start_date, end_date):
        """获取公募基金净值数据 含场内与场外"""
        df = self.pro.fund_nav(ts_code=ts_code, start_date=start_date, end_date=end_date)
        return df

    def get_fund_manager(self, ts_code):
        return self.pro.fund_manager(ts_code=ts_code)

    def get_fund_basic(self, market='E', status=''):
        """交易市场: E场内 O场外（默认E）;  存续状态: D摘牌 I发行 L上市中"""
        return self.pro.fund_basic(market=market, status=status)

    def get_fund_portfolio(self, ts_code, end_date):
        """获取公募基金持仓数据，季度更新"""
        return self.pro.fund_portfolio(ts_code=ts_code, end_date=end_date)

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
