import matplotlib.pyplot as plt


def set_plot_style():
    # 指定默认字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['font.family'] = 'sans-serif'
    # 解决负号'-'显示为方块的问题
    plt.rcParams['axes.unicode_minus'] = False


class ShowRst:

    def __init__(self):
        set_plot_style()

    @staticmethod
    def gen_one_ax():
        fig = plt.figure()
        ax = fig.add_subplot(111)
        return ax

    @staticmethod
    def show_cumulative_value(ax1, df_cal_data, df_invest_data):
        ax1.plot(df_cal_data['date'], df_cal_data['price'])
        ax1.plot(df_invest_data['date'], df_invest_data['price'], 'r.')
        ax1.set_ylabel('累计净值')
        ax1.set_xlabel('日期')
        ticks = df_cal_data['date'].tolist()[::20]
        ax1.set_xticks(ticks)
        ax1.set_xticklabels(ticks, rotation=45)
        plt.legend(labels=['指数', '定投'], prop={'size': 11}, loc='best')
        plt.title('定投净值曲线')
        plt.grid(axis='y')
        plt.show()

    @staticmethod
    def show_average_principal(ax1, pri_average):
        ax1.axhline(y=pri_average, ls='--', c='g')

    @staticmethod
    def show_fund_major_stocks(sc_df):
        plt.figure()
        plt.bar(sc_df['stock_name'], sc_df['hold_num'])
        plt.ylabel('持仓基金数目')
        plt.title('偏股型公募基金重仓股统计')
        plt.xticks(rotation=-60, size=7)
        plt.tight_layout()
        plt.show()







