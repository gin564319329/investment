"""
主程序： 调用utils各工具，进行投资实验，投资策略尝试 回测等
Author  : Jiang
"""

from utils.data_generator import GenCustomData, GenFixedInvest
from utils.show_rst import ShowRst
from utils import financial_calculator as cal
from utils import data_statistics

get_data = GenCustomData()


def analysis_invest_yield(ts_code, date_start, date_end, weekday=4, m_day=20):
    """对比按月定投与按周定投收益情况"""
    cal_data_tu = get_data.gen_index_daily_data(ts_code, date_start, date_end)
    fix = GenFixedInvest(cal_data_tu, money_amount=500)
    fix_m = GenFixedInvest(cal_data_tu, money_amount=2000)
    invest_data_w = fix.gen_data_week_fixed_invest(weekday=weekday)
    invest_data_m = fix_m.gen_data_month_fixed_invest(month_day=m_day)
    principal_w, final_amount_w, profit_w, buy_num_w, pri_average_w = data_statistics.get_invest_profit(invest_data_w)
    principal_m, final_amount_m, profit_m, buy_num_m, pri_average_m = data_statistics.get_invest_profit(invest_data_m)
    print('week: principal: {}, final_amount: {}, profit: {}, buy_num: {}'.format(principal_w, final_amount_w, profit_w,
                                                                                  buy_num_w))
    print(
        'month: principal: {}, final_amount: {}, profit: {}, buy_num: {}'.format(principal_m, final_amount_m, profit_m,
                                                                                 buy_num_m))
    show_r = ShowRst()
    ax = show_r.gen_one_ax()
    show_r.show_cumulative_value(ax, cal_data_tu, invest_data_w, pri_average_w)

    # cal_time = cal.CalTime(date_start, date_end)
    # month_num = cal_time.cal_month_num()
    # x_ticks = cal_time.gen_ticks(month_num)
    val_arr_w = [500] * 50
    val_arr_w.append(-final_amount_w)
    val_arr_m = [2000] * 12
    val_arr_m.append(-final_amount_m)
    rate_w = cal.cal_total_rate(principal_w, final_amount_w)
    rate_m = cal.cal_total_rate(principal_m, final_amount_m)
    rate_w_irr = cal.cal_irr_by_fixed_invest(val_arr_w, 50)
    rate_m_irr = cal.cal_irr_by_fixed_invest(val_arr_m, 12)


if __name__ == "__main__":
    code, start, end = '000300.SH', '20151231', '20171231'
    analysis_invest_yield(code, start, end, weekday=4, m_day=20)
