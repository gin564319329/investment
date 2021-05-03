import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib


def request_url(url, params=None, proxies=None):
    rsp = requests.get(url, params=params, proxies=proxies)
    # print(rsp.url)
    return rsp.text


def get_one_fund_raw_info(url, code, page, per, s_date, e_date):
    params = {'type': 'lsjz', 'code': code, 'page': page, 'per': per, 'sdate': s_date, 'edate': e_date}
    raw_html = request_url(url, params)
    soup = BeautifulSoup(raw_html, 'html.parser')
    return raw_html, soup


def get_one_fund_format_info(code, per=10, s_date='', e_date=''):
    base_url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx'
    raw_html_p1, soup_p1 = get_one_fund_raw_info(base_url, code, 1, per, s_date, e_date)
    # 获取总页数
    pattern = re.compile(r'pages:(.*),')
    pages = int(re.search(pattern, raw_html_p1).group(1))
    # 获取表头
    heads = []
    for head in soup_p1.findAll("th"):
        heads.append(head.contents[0])

    # 从第1页开始抓取所有页面数据
    record_list = []
    for page in range(1, pages+1):
        raw_html, soup = get_one_fund_raw_info(base_url, code, page, per, s_date, e_date)
        for row in soup.findAll("tbody")[0].findAll("tr"):
            row_records = []
            for record in row.findAll('td'):
                val = record.contents
                if not val:
                    row_records.append(np.nan)
                else:
                    row_records.append(val[0])
            record_list.append(row_records)

    record_df = pd.DataFrame(data=record_list, columns=heads)
    record_df['净值日期'] = record_df['净值日期'].astype(str)
    record_df['净值日期'] = pd.to_datetime(record_df['净值日期'], format='%Y/%m/%d')
    record_df['单位净值'] = record_df['单位净值'].astype(float)
    record_df['累计净值'] = record_df['累计净值'].astype(float)
    record_df['日增长率'] = record_df['日增长率'].str.strip('%').astype(float)
    # 按照日期升序排序并重建索引
    record_df = record_df.sort_values(by='净值日期', axis=0, ascending=True).reset_index(drop=True)

    return record_df


def set_plot_style():
    # 指定默认字体
    matplotlib.rcParams['font.sans-serif'] = ['SimHei']
    matplotlib.rcParams['font.family'] = 'sans-serif'
    # 解决负号'-'显示为方块的问题
    matplotlib.rcParams['axes.unicode_minus'] = False


def show_cumulative_value(net_value_date,  net_asset_value, accumulative_net_value, daily_growth_rate):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(net_value_date, net_asset_value)
    ax1.plot(net_value_date, accumulative_net_value)
    ax1.set_ylabel('净值数据')
    ax1.set_xlabel('日期')
    plt.legend(labels=['单位净值', '累计净值'], prop={'size': 13}, loc='upper left')
    ax2 = ax1.twinx()
    ax2.plot(net_value_date, daily_growth_rate, 'r')
    ax2.set_ylabel('日增长率（%）')
    plt.legend(['growth_rate'], loc='upper right')
    plt.title('基金净值数据')
    plt.show()


def show_bonus(net_value_date, net_asset_value, accumulative_net_value):
    bonus = accumulative_net_value - net_asset_value
    plt.figure()
    plt.plot(net_value_date, bonus)
    plt.xlabel('日期')
    plt.ylabel('累计净值-单位净值')
    plt.title('基金“分红”信息')
    plt.show()


if __name__ == "__main__":
    fund_data = get_one_fund_format_info('161725', per=49, s_date='2018-01-01', e_date='2018-12-31')
    set_plot_style()
    show_cumulative_value(fund_data['净值日期'], fund_data['单位净值'], fund_data['累计净值'], fund_data['日增长率'])
    show_bonus(fund_data['净值日期'], fund_data['单位净值'], fund_data['累计净值'])

    # 日增长率分析
    print('日增长率缺失：', sum(np.isnan(fund_data['日增长率'])))
    print('日增长率为正的天数：', sum(fund_data['日增长率'] > 0))
    print('日增长率为负（包含0）的天数：', sum(fund_data['日增长率'] <= 0))

# 最大回撤
# def cal_draw_down(x_max, x_min):
#     return (x_max - x_min) / x_max

# max_draw_down = cal_draw_down(x_max=2.2079, x_min=1.8955)
# print('万家社会责任：{:7.2%}'.format(max_draw_down))
#
# max_draw_down = cal_draw_down(x_max=2.7871, x_min=2.3246)
# print('中欧成长：{:10.2%}'.format(max_draw_down))
#
# max_draw_down = cal_draw_down(x_max=2.0182, x_min=1.7984)
# print('中欧趋势：{:10.2%}'.format(max_draw_down))
#
# max_draw_down = cal_draw_down(x_max=2.1612, x_min=1.8321)
# print('交银瑞丰：{:10.2%}'.format(max_draw_down))
#
# max_draw_down = cal_draw_down(x_max=4.1490, x_min=3.7090)
# print('富国天惠：{:10.2%}'.format(max_draw_down))
#
# max_draw_down = cal_draw_down(x_max=5.2680, x_min=4.5900)
# print('南方天元：{:10.2%}'.format(max_draw_down))
#
# max_draw_down = cal_draw_down(x_max=2.2727, x_min=2.1107)
# print('兴全合润：{:10.2%}'.format(max_draw_down))
#
# max_draw_down = cal_draw_down(x_max=3.7840, x_min=3.6620)
# print('兴全轻资：{:10.2%}'.format(max_draw_down))
#
# max_draw_down = cal_draw_down(x_max=1.1160, x_min=1.0703)
# print('兴全趋势：{:10.2%}'.format(max_draw_down))
#
# max_draw_down = cal_draw_down(x_max=10.7389, x_min=8.0329 + 0.9)
# print('易方达中小盘：{:7.2%}'.format(max_draw_down))
#
# max_draw_down = cal_draw_down(x_max=3.5287, x_min=2.9570)
# print('易方达蓝筹：{:9.2%}'.format(max_draw_down))
