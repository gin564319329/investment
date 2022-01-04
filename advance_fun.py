import pandas as pd
import logging
from get_market_data import GetTuShareData
from fund_tools import CalFixedInvest, CalYieldRate


class AdvOperation(GetTuShareData):

    def __init__(self, cal_tools):
        super(AdvOperation, self).__init__()
        self.cal_base = cal_tools

    def get_daily_data(self, ts_code, date_start, date_end):
        tu_data = self.get_index_daily(ts_code, date_start, date_end)
        cal_data_tu = self.gen_cal_data(tu_data)
        return cal_data_tu

    def search_code_batch(self, search_list):
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

    def get_change_ratio(self, cal_data_tu):
        st = cal_data_tu.iloc[0]['price']
        end = cal_data_tu.iloc[-1]['price']
        c_ratio = self.cal_base.cal_change_ratio(st, end)
        return c_ratio

    def get_invest_rst(self, cal_data_tu):
        weekday = 4
        fit = CalFixedInvest(cal_data_tu, money_amount=500)
        df_invest_data_w = fit.fixed_invest_by_week(weekday=weekday)
        principal_w, final_amount_w, profit_w, buy_num_w, pri_average_w = fit.cal_yield(df_invest_data_w)
        i_ratio = self.cal_base.cal_change_ratio(principal_w, final_amount_w)
        return i_ratio

    def get_ratio_batch(self, date_search_dict, ts_code_list):
        for code in ts_code_list:
            for start, end in zip(date_search_dict['date_start'], date_search_dict['date_end']):
                cal_data_tu = self.get_daily_data(code, start, end)
                ch_ratio = self.get_change_ratio(cal_data_tu)
                print('{} {} change ratio: {:.2%}'.format(cal_data_tu.iloc[-1]['year'], code, ch_ratio))
                in_ratio = self.get_invest_rst(cal_data_tu)
                print('{} {} irri profit: {:.2%}'.format(cal_data_tu.iloc[-1]['year'], code, in_ratio))

    def get_ratio_batch_by_date(self, date_search_dict, code_search_dict):
        rst_dict_date = {'year': []}
        rst_dict_ch = {'{}_涨跌幅'.format(na): [] for na in code_search_dict.get('name')}
        rst_dict_in = {'{}_定投收益'.format(na): [] for na in code_search_dict.get('name')}
        for start, end in zip(date_search_dict['date_start'], date_search_dict['date_end']):
            rst_dict_date['year'].append(end[0:4])
            for code, name in zip(code_search_dict.get('ts_code'), code_search_dict.get('name')):
                cal_data_tu = self.get_daily_data(code, start, end)
                ch_ratio = self.get_change_ratio(cal_data_tu)
                in_ratio = self.get_invest_rst(cal_data_tu)
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

    @staticmethod
    def cal_contrast(rst_df_raw):
        rst_ch_con = rst_df_raw.copy()
        rst_ch_con['最大收益指数'] = rst_df_raw.idxmax(axis=1).values
        rst_ch_con['最小收益指数'] = rst_df_raw.idxmin(axis=1).values
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
    cal_data = ad.get_daily_data('000001.SH', '20201231', '20211231')
    print(cal_data.iloc[0]['date'], cal_data.iloc[-1]['date'])
    ch_r = ad.get_change_ratio(cal_data)
    print('{:.2%}'.format(ch_r))
    in_r = ad.get_invest_rst(cal_data)
    print('irri profit: {:.2%}'.format(in_r))
