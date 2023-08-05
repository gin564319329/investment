"""
财务指标、收益率基本计算公式
Author  : Jiang
"""

import numpy_financial as npf
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


def cal_total_rate(principal, final_amount):
    """
    计算总收益率
    :param principal: 本金
    :param final_amount: 最终金额
    """
    return (final_amount - principal) / principal


def cal_compound_interest(principal, rate_single, term):
    """
    计算复利
    :param principal: 本金 100
    :param rate_single: 单利 年利率 0.1
    :param term: 投资期数 10年
    """
    return principal * (1 + rate_single) ** term


def cal_annual_rate_by_value(principal, final_amount, term, num_a_year):
    """
    计算年化收益率
    formula: principal * (1+rate_t)**term = final_amount
    :param principal: 本金 100
    :param final_amount: 最终金额 500
    :param term: 投资期数 120个月
    :param num_a_year: 按月复利，一年12月
    Examples  cal_annual_rate_by_value(100, 500, 120, 12)))
    """
    return ((final_amount / principal) ** (1 / term) - 1) * num_a_year


def cal_annual_rate_by_rate(rate_all, term, num_a_year):
    return ((rate_all + 1) ** (1 / term) - 1) * num_a_year


def cal_irr_by_fixed_invest(val_arr, num_a_year):
    """定投 计算内部收益率 年化收益率
    :param val_arr 投入与收益数组
    :param num_a_year 每年期数
    :return: rate_irr 内部收益率
    :return：rate_annual 年化收益率
    Examples
    val_arr = [10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, -140000]
    """
    rate_irr = npf.irr(val_arr)
    rate_annual = pow((rate_irr + 1), num_a_year) - 1
    return rate_irr, rate_annual


def cal_change_ratio(initial_value, final_value):
    if initial_value is not None:
        return (final_value - initial_value) / initial_value
    return None


class CalTime:
    def __init__(self, date_start, date_end):
        self.date_start = date_start
        self.date_end = date_end

    def cal_month_num(self):
        month_start = datetime.strptime(self.date_start, "%Y%m%d").month
        month_end = datetime.strptime(self.date_end, "%Y%m%d").month
        year_start = datetime.strptime(self.date_start, "%Y%m%d").year
        year_end = datetime.strptime(self.date_end, "%Y%m%d").year
        return (year_end - year_start) * 12 + (month_end - month_start) + 1

    def gen_ticks(self, month_num):
        date_list = []
        for n in range(month_num):
            next_month = datetime.strptime(self.date_start, "%Y%m%d") + relativedelta(months=+n)
            date_list.append(next_month.strftime("%Y%m%d"))
        return date_list

    @staticmethod
    def trs_ymd(year, month, day):
        return date(year, month, day).strftime("%Y%m%d")


if __name__ == '__main__':
    print('复利终值: {}'.format(cal_compound_interest(100, 0.1, 10)))  # 本金100， 年利率10%，投资10年
    print('年化收益率： {}'.format(cal_annual_rate_by_value(100, 200, 10, 1)))  # 本金100， 终值300，投资10年, 按年复利，一年1年
    print('年化收益率： {}'.format(cal_annual_rate_by_value(100, 200, 120, 12)))  # 本金100， 终值300，投资120月, 按月复利，一年12月
    val = [10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, -140000]
    irr, rate_y = cal_irr_by_fixed_invest(val, 12)
    print('内部收益率: {}  年化收益率: {}'.format(irr, rate_y))
