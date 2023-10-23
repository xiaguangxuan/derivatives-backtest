import pandas as pd
from datetime import datetime
from tqdm import tqdm
from Snowball import *
from tools import *
from getData import *
from plot import *


# 对某个雪球产品进行回测
def backtest(snowball, index_data_all):
    # 回测结果
    snowball.process_backtest(index_data_all)

    # 输出
    result_series = pd.Series((
        snowball.time_dynamic_param['start_date'],
        snowball.start_price,
        snowball.time_dynamic_param['end_date'],
        snowball.end_price,
        snowball.knockin_date,
        snowball.knockin_price,
        snowball.knockout_date,
        snowball.knockout_price,
        snowball.status,
        snowball.terminal_month,
        snowball.abs_return,
        snowball.annual_return,
        snowball.maturity_sign  
    ))
    return result_series


if __name__ == "__main__":

    ##########################################################################
    # 仅修改这部分参数设置 #####################################################
    ##########################################################################

    # ---------------------------- 雪球参数设置 ------------------------------#
    underlying = "上证50"
    underlying_code = "000016.SH"

    snowball_type = "降敲型雪球"

    # 合约期限
    option_expire_month = 24                            # 只以月度来结算，一年则调整为12个月

    # 敲入条件
    knockin_barrier = 0.8                               # 敲入条件，敲入观察日的价格/起初价格

    # 敲出条件
    knockout_barrier = 1.02                             # 敲出条件，首个敲出观察日的价格/起初价格
    knockout_freq_month = 1                             # 敲出观察频率为每月

    # 票息设置
    kickout_coupon = 0.12                               # 敲出票息，提前敲出
    regular_coupon = 0.12                               # 红利票息，持有直到到期
    observation_start_month = 3                         # 首个敲出观察日为距离观察起始日后的第x月

    # 追保设置
    margin_call = False     # 不允许追保

    # ---------------------------- 回测参数设置 ------------------------------#
    backtest_start = ensure_trading_day(datetime(2018, 1, 1, 0, 0).date())
    backtest_end = ensure_trading_day(datetime(2021, 4, 1, 0, 0).date())

    # ---------------------------- 输出路径设置 ------------------------------#
    output_path = "D:/10-国君\GTJA-intern-codes/backtest_version_V2\output"

    ##########################################################################
    ##########################################################################
    ##########################################################################

    # 生成参数 ################################################################
    # 生成固定配置
    time_fixed_param = {'option_expire_month': option_expire_month}
    knockin_param = {'knockin_barrier': knockin_barrier}
    knockout_param = {'observation_start_month': observation_start_month,
                      'knockout_barrier': knockout_barrier,
                      'knockout_freq_month': knockout_freq_month}
    coupon_param = {'kickout_coupon': kickout_coupon,
                    'regular_coupon': regular_coupon}
    profit_param = {'margin_call': margin_call}

    # 生成回测区间
    trading_datelist = get_trading_datelist()
    backtest_datelist = [i for i in trading_datelist if i >= backtest_start
                         and i <= backtest_end]


    # 输出回测结果 #########################################################
    # 获取标的价格信息 
    index_data_all = get_underlying_data(underlying, 
                                         pd.to_datetime("2010-01-01").date(), 
                                         pd.to_datetime("2023-10-01").date())

    # 初始化雪球类
    snowball = SnowballOption.create_snowball(snowball_type, underlying,
                                                     time_fixed_param, knockin_param, knockout_param, coupon_param, profit_param)
    
    # 雪球基础信息输出
    plot_bactest_info(snowball, backtest_start, backtest_end, output_path)

    # 输出结果
    output = []
    for start_date in tqdm(backtest_datelist):
        
        # 设置雪球合约时间参数
        end_date = ensure_trading_day(start_date + relativedelta(months = snowball.time_fixed_param["option_expire_month"]))
        time_dynamic_param = {'start_date': start_date,  'end_date': end_date}

        # 初始化雪球类
        snowball.set_time_param(time_dynamic_param)
        snowball.reset_state()

        # 回测
        output.append(backtest(snowball, index_data_all))

    col_names = ['初始日期',  '初始指数',  '到期日期', '到期指数', '敲入日期', 
                 '敲入点位', '敲出日期', '敲出点位', '敲入敲出状态', '敲出所需时间（月）',  
                 '绝对收益率', '年化收益率', '完成周期']
    output = pd.concat(output, axis=1).T 
    output.columns = col_names

    output.to_csv(output_path + "/output.csv")
