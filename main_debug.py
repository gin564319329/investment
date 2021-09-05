from get_market_data import GetCsvData, GetTuShareData
from fund_tools import CalFixedInvest, CalYieldRate, CalTime
from show_rst import ShowRst


index_id = '0000300'
date_start = '20200101'
date_end = '20201231'
gd = GetCsvData()
raw_data = gd.get_k_data_by_163(index_id, date_start, date_end)
cal_data = gd.gen_cal_data(raw_data)
fi = CalFixedInvest(cal_data, money_amount=500)
df_invest_data = fi.fixed_invest_by_week(weekday=4)
df_invest_data_m = fi.fixed_invest_by_month(month_day=20)
principal, final_amount, profit, buy_num, pri_average = fi.cal_yield(df_invest_data)
principal_m, final_amount_m, profit_m, buy_num_m, pri_average_m = fi.cal_yield(df_invest_data_m)
print('week: principal: {}, final_amount: {}, profit: {}, buy_num: {}'.format(principal, final_amount, profit, buy_num))
print('month: principal: {}, final_amount: {}, profit: {}, buy_num: {}'.format(principal_m, final_amount_m, profit_m, buy_num_m))