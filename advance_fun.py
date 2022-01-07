from fund_tools import CalFixedInvest, CalYieldRate


class AdvOperation:

    def __init__(self):
        self.cal_base = CalYieldRate()

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

    @staticmethod
    def get_newest_net_asset(fund_nav):
        if not fund_nav['net_asset'].notnull().sum():
            return None, None
        net_asset = fund_nav['net_asset'][fund_nav['net_asset'].notnull()].iloc[0]
        ann_date = fund_nav['nav_date'][fund_nav['net_asset'].notnull()].iloc[0]
        return net_asset, ann_date

    @staticmethod
    def cal_index_minmax(yield_df, key=''):
        yield_con = yield_df.copy()
        yield_con['最优{}'.format(key)] = yield_df.idxmax(axis=1).values
        yield_con['最差{}'.format(key)] = yield_df.idxmin(axis=1).values
        return yield_con

