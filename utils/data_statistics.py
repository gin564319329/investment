"""
count invest, fund and index evaluation info based on market data and financial_calculator.py
Author  : Jiang
"""

import pandas as pd
import utils.financial_calculator as cal


def get_index_change_ratio(index_daily):
    if index_daily.empty:
        return None
    st = index_daily.iloc[0]['price']
    end = index_daily.iloc[-1]['price']
    c_ratio = cal.cal_change_ratio(st, end)
    return c_ratio


def get_fixed_inv_change_ratio(invest_data):
    principal_w, final_amount_w, profit_w, buy_num_w, pri_average_w = get_invest_profit(invest_data)
    i_ratio = cal.cal_change_ratio(principal_w, final_amount_w)
    return i_ratio


def get_fund_change_ratio(fund_nav):
    st = fund_nav.iloc[-1]['adj_nav']  # accum_nav adj_nav
    end = fund_nav.iloc[0]['adj_nav']
    c_ratio = cal.cal_change_ratio(st, end)
    return c_ratio


def get_invest_profit(df_invest_data):
    if df_invest_data.empty:
        return None, None, None, None, None
    principal = df_invest_data['money'].sum()
    final_price = df_invest_data.iloc[-1]['price']
    final_amount = df_invest_data['share'].sum() * final_price
    profit = final_amount - principal
    buy_num = df_invest_data['money'].size
    pri_average = principal / df_invest_data['share'].sum()
    return principal, final_amount, profit, buy_num, pri_average


def get_index_minmax(yield_df, key=''):
    yield_con = yield_df.copy()
    yield_con['最优{}'.format(key)] = yield_df.idxmax(axis=1).values
    yield_con['最差{}'.format(key)] = yield_df.idxmin(axis=1).values
    return yield_con


def get_newest_net_asset(fund_nav):
    if not fund_nav['net_asset'].notnull().sum():
        return None, None
    net_asset = fund_nav['net_asset'][fund_nav['net_asset'].notnull()].iloc[0]
    ann_date = fund_nav['nav_date'][fund_nav['net_asset'].notnull()].iloc[0]
    return net_asset, ann_date


def get_fund_major_stocks(portfolio_dir, save_count, count=2):
    port_o = pd.read_csv(portfolio_dir)
    s_count = port_o['stock_name'].value_counts()
    s_c = s_count[s_count.values >= count]
    s_c_dict = {'stock_name': s_c.index.tolist(), 'hold_num': s_c.tolist()}
    s_c_df = pd.DataFrame.from_dict(s_c_dict)
    if save_count:
        s_c_df.to_csv(save_count, index=False, encoding='utf_8_sig')
    return s_c_df


def get_cb_convert_ratio(cb_concat_data):
    """计算可转债转股溢价率 双低值等"""
    """转股溢价率＝转债价格／转股价值 - 1 ；     转股价值＝100 * 正股价／转股价"""
    cb_value = 100 * cb_concat_data['stk_close'] / cb_concat_data['conv_price']
    cb_over_rate = (cb_concat_data['close'] / cb_value - 1) * 100  # 按百分号里的值计算
    double_low = cb_concat_data['close'] + cb_over_rate
    return cb_value, cb_over_rate, double_low


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    sco = get_fund_major_stocks(portfolio_dir=r'..\data\rst_out\fio_all_202212.csv',
                                save_count=r'..\data\rst_out\fio_count_o1.csv')
    print(sco)
