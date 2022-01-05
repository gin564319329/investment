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
        tu_data = self.get_index_daily(ts_code, date_start, date_end)
        index_for_cal = self.gen_cal_data(tu_data)
        return index_for_cal

    def query_index_tscode_by_name(self, search_list):
        df_sh = self.get_index_basic('', '', market='SSE')
        df_sz = self.get_index_basic('', '', market='SZSE')
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

    def get_index_yield(self, date_search_dict, code_search_dict):
        rst_dict_date = {'year': []}
        rst_dict_ch = {'{}_涨跌幅'.format(na): [] for na in code_search_dict.get('name')}
        rst_dict_in = {'{}_定投收益'.format(na): [] for na in code_search_dict.get('name')}
        for start, end in zip(date_search_dict['date_start'], date_search_dict['date_end']):
            rst_dict_date['year'].append(end[0:4])
            for code, name in zip(code_search_dict.get('ts_code'), code_search_dict.get('name')):
                cal_data_tu = self.get_index_daily_data(code, start, end)
                ch_ratio = self.cal_index_change_ratio(cal_data_tu)
                in_ratio = self.cal_fixed_inv_change_ratio(cal_data_tu)
                rst_dict_ch['{}_涨跌幅'.format(name)].append(ch_ratio)
                rst_dict_in['{}_定投收益'.format(name)].append(in_ratio)
                print('{} {} change ratio: {:.2%}'.format(cal_data_tu.iloc[-1]['year'], name, ch_ratio))
                print('{} {} irri profit: {:.2%}'.format(cal_data_tu.iloc[-1]['year'], name, in_ratio))
        rst_dict_date['year'][-1] = 'all'
        rst_data = pd.DataFrame(rst_dict_date)
        rst_df_ch = pd.DataFrame(rst_dict_ch)
        rst_df_in = pd.DataFrame(rst_dict_in)
        rst_t = pd.concat([rst_data, self.cal_contrast(rst_df_ch), self.cal_contrast(rst_df_in)], axis=1)

        return rst_t

    def get_fund_yield(self, date_query, fund_query):
        rst_date = {'year': []}
        rst_change = {'{}'.format(na): [] for na in fund_query.get('ts_code')}
        for start, end in zip(date_query['date_start'], date_query['date_end']):
            rst_date['year'].append(end[0:4])
            for code, name in zip(fund_query.get('ts_code'), fund_query.get('name')):
                fund_nav = self.get_fund_nav(code, start, end)
                if fund_nav.empty:
                    rst_change['{}'.format(code)].append(np.NAN)
                    print('{} {} no data'.format(end[0:4], name))
                    continue
                ch_ratio = self.cal_fund_change_ratio(fund_nav)
                rst_change['{}'.format(code)].append(ch_ratio)
                print('{} {} change ratio: {:.2%}'.format(end[0:4], name, ch_ratio))
        rst_date['year'][-1] = 'all'
        rst_data = pd.DataFrame(rst_date)
        rst_df_ch = pd.DataFrame(rst_change)

        return pd.concat([rst_data, self.cal_contrast(rst_df_ch)], axis=1)

    def get_fund_yield_year(self, date_query, fund_query):
        fund_yield = fund_query.copy()
        for start, end, per in zip(date_query['date_start'], date_query['date_end'], date_query['query_period']):
            for index, row in fund_query.iterrows():
                fund_nav = self.get_fund_nav(row.get('ts_code'), start, end)
                if fund_nav.empty:
                    fund_yield.at[index, per] = np.NAN
                    print('{} {} no data'.format(per, row.get('name')))
                    continue
                fund_yield.at[index, per] = self.cal_fund_change_ratio(fund_nav)
                print('{} {} fund yield rate: {:.2%}'.format(per, row.get('name'), fund_yield.at[index, per]))

        return fund_yield

    @staticmethod
    def cal_contrast(rst_df_raw):
        rst_ch_con = rst_df_raw.copy()
        rst_ch_con['最大收益'] = rst_df_raw.idxmax(axis=1).values
        rst_ch_con['最小收益'] = rst_df_raw.idxmin(axis=1).values
        return rst_ch_con

    def get_ts_code_by_code(self, code, market='E'):
        """查询tushare基金代码"""
        fund_bat = self.get_fund_basic(market=market, status='L')
        for ts_code in fund_bat['ts_code']:
            if code in ts_code:
                return ts_code
        logging.warning('there is no {} fund'.format(code))
        return None

    @staticmethod
    def dis_pd_style():
        pd.set_option('display.unicode.ambiguous_as_wide', True)
        pd.set_option('display.unicode.east_asian_width', True)
        pd.set_option('display.width', 1)


if __name__ == '__main__':
    ad = AdvOperation(CalYieldRate())
    cal_data = ad.get_index_daily_data('000001.SH', '20201231', '20211231')
    print(cal_data.iloc[0]['date'], cal_data.iloc[-1]['date'])
    ch_r = ad.cal_index_change_ratio(cal_data)
    print('{:.2%}'.format(ch_r))
    in_r = ad.cal_fixed_inv_change_ratio(cal_data)
    print('irri profit: {:.2%}'.format(in_r))
