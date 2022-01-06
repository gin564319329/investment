import time
import numpy as np
import pandas as pd
import logging
from get_market_data import GetTuShareData
from fund_tools import CalFixedInvest, CalYieldRate


class AdvOperation(GetTuShareData):

    def __init__(self):
        super(AdvOperation, self).__init__()
        self.cal_base = CalYieldRate()

    def get_index_daily_data(self, ts_code, date_start, date_end):
        tu_data = self.query_index_daily(ts_code, date_start, date_end)
        index_for_cal = self.gen_cal_data(tu_data)
        return index_for_cal

    def get_index_tscode_by_name(self, search_list):
        df_sh = self.query_index_basic('', '', market='SSE')
        df_sz = self.query_index_basic('', '', market='SZSE')
        search_dict = {'ts_code': [], 'name': []}

        for index, s in df_sh.iterrows():
            if s['name'] in search_list:
                search_list.remove(s['name'])
                print('{}\t代码:\t {}'.format(s['name'], s['ts_code']))
                search_dict['ts_code'].append(s['ts_code'])
                search_dict['name'].append(s['name'])

        for index, s in df_sz.iterrows():
            if s['name'] in search_list:
                search_list.remove(s['name'])
                print('{}\t代码:\t {}'.format(s['name'], s['ts_code']))
                search_dict['ts_code'].append(s['ts_code'])
                search_dict['name'].append(s['name'])

        return search_dict

    def cal_index_change_ratio(self, index_daily):
        st = index_daily.iloc[0]['price']
        end = index_daily.iloc[-1]['price']
        c_ratio = self.cal_base.cal_change_ratio(st, end)
        return c_ratio

    def cal_fixed_inv_change_ratio(self, index_daily):
        fit = CalFixedInvest(index_daily, money_amount=500)
        invest_data = fit.fixed_invest_by_week(weekday=4)
        principal_w, final_amount_w, profit_w, buy_num_w, pri_average_w = fit.cal_yield(invest_data)
        i_ratio = self.cal_base.cal_change_ratio(principal_w, final_amount_w)
        return i_ratio

    def cal_fund_change_ratio(self, fund_nav):
        st = fund_nav.iloc[-1]['adj_nav']  # accum_nav adj_nav
        end = fund_nav.iloc[0]['adj_nav']
        c_ratio = self.cal_base.cal_change_ratio(st, end)
        return c_ratio

    def gen_index_yield(self, date_query, index_query):
        """生成指数年度收益率表格"""
        index_yield = pd.DataFrame(index=date_query['query_period'])
        for start, end, per in zip(date_query['date_start'], date_query['date_end'], date_query['query_period']):
            for code, name in zip(index_query.get('ts_code'), index_query.get('name')):
                index_for_cal = self.get_index_daily_data(code, start, end)
                ch_ratio = self.cal_index_change_ratio(index_for_cal)
                in_ratio = self.cal_fixed_inv_change_ratio(index_for_cal)
                index_yield.at[per, '{}_涨幅'.format(name)] = ch_ratio
                index_yield.at[per, '{}_定投'.format(name)] = in_ratio
                print('{} {} change ratio: {:.2%}'.format(per, name, ch_ratio))
                print('{} {} irri profit: {:.2%}'.format(per, name, in_ratio))
        ch_df = index_yield[[a for a in index_yield.columns if '涨幅' in a]]
        in_df = index_yield[[a for a in index_yield.columns if '定投' in a]]
        ch_df_a = self.cal_index_minmax(ch_df, '涨幅')
        in_df_a = self.cal_index_minmax(in_df, '定投')

        return pd.concat([ch_df_a, in_df_a], axis=1)

    def append_fund_yield(self, date_query, fund_query):
        """增加基金年度收益率信息"""
        fund_yield = fund_query.copy()
        for start, end, per in zip(date_query['date_start'], date_query['date_end'], date_query['query_period']):
            for index, row in fund_query.iterrows():
                fund_nav = self.query_fund_nav(row.get('ts_code'), start, end)
                time.sleep(0.8)
                if fund_nav.empty:
                    fund_yield.at[index, per] = np.NAN
                    print('{} {} no data'.format(per, row.get('name')))
                    continue
                fund_yield.at[index, per] = self.cal_fund_change_ratio(fund_nav)
                print('{} {} fund yield rate: {:.2%}'.format(per, row.get('name'), fund_yield.at[index, per]))

        return fund_yield

    @staticmethod
    def cal_index_minmax(yield_df, key=''):
        yield_con = yield_df.copy()
        yield_con['最优{}'.format(key)] = yield_df.idxmax(axis=1).values
        yield_con['最差{}'.format(key)] = yield_df.idxmin(axis=1).values
        return yield_con


if __name__ == '__main__':
    ad = AdvOperation()
    cal_data = ad.get_index_daily_data('000001.SH', '20201231', '20211231')
    ch_r = ad.cal_index_change_ratio(cal_data)
    in_r = ad.cal_fixed_inv_change_ratio(cal_data)
    print('change rate: {:.2%}'.format(ch_r))
    print('irri rate: {:.2%}'.format(in_r))
