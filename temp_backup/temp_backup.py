import pandas as pd
from datetime import datetime


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


if __name__ == '__main__':
    index_id = '0000300'
    date_start = '20200101'
    date_end = '20211031'
    gd = GetCsvData()
    raw_data_t = gd.get_k_data_by_163(index_id, date_start, date_end)
    cal_data_t = gd.gen_cal_data(raw_data_t)
