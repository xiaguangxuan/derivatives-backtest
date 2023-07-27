# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 16:15:22 2023

@author: hasee
"""
# 导入第三方库
import pandas as pd
import numpy as np
import datetime
from dateutil import relativedelta
import os
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import ticker
plt.rcParams["font.sans-serif"]=["SimHei"] #设置字体
mpl.rcParams['axes.unicode_minus']=False
import warnings
warnings.filterwarnings('ignore')
import sys
# 加载当前路径
sys.path.append('.')
from simple_tools import filter_operator, get_data

####################### 分界线 ###############################3
def jiangqiaoxueqiu(data, knock_in, normal_rate):
    flag = 0
    if data['是否敲出'] == 1:
        rate = normal_rate * data['敲出日期'] / 12
        if data['期间最低收益率'] < knock_in:
            flag = 1
    elif data['期间最低收益率'] < knock_in:
        rate = min(data['收益率'], 0)
        flag = 1
    else:
        rate = normal_rate * month_period / 12
    return pd.Series([rate, flag])

########## 参数初始化 ###########
start_date = '2018-01-01'
end_date = '2023-07-20'

# 标的的存续期
month_period = 24
# 敲出价
knock_out = 1.00
# 敲出价格的调整步长
knock_out_unit = 0.005
# 敲入价
knock_in = 0.75
# 从第几个月开始观察
start_month = 1 
# 未发生敲入的年化收益率
normal_rate = 0.038
# 是否为降敲结构
is_jiangqiao = 1

if is_jiangqiao:
    # 生成每个观察日的敲出价, 第一次为原水平 knock_out
    knock_out = np.array([knock_out - knock_out_unit * i for i in range(month_period + 1 - start_month)])
else:
    knock_out = np.array([knock_out]* (month_period + 1 - start_month)) 

############## 导入数据与数据切片 ################
data, price_resample, time_resample, data_copy = get_data(useapi = 0, underlying = '中证1000PETTM.xlsx')
# data, price_resample, time_resample, data_copy = get_data(useapi = 1, underlying = '000852.SH', start = '2004-01-01')

data = data[start_date:end_date]

############ 分位数模块 ############
data = filter_operator(data, data_copy, lower_bound = 0, upper_bound = 1, rolling_window_width = 3)

######################################

# 买入时间平移 month_period 个月份
data['到期日'] = [data.index[i] + relativedelta.relativedelta(months = month_period) for i in range(len(data.index))]
# 将自然日的数据填补
df = pd.merge(data, price_resample, left_on = '到期日', right_index = True, how = 'left')

flag_out = pd.Series()
flag_out_time = pd.Series()
time_limit = price_resample.index[-1]
for i in df.index:
    knock_out_price = df['收盘价(元)_x'][i] * knock_out
    flag_out[i] = 0
    flag_out_time[i] = -1
    for j in range(start_month, month_period + 1):
        observation_time = i + relativedelta.relativedelta(months = j)
        if observation_time > time_limit:
            break
        observation_price = price_resample.loc[observation_time].values
        if observation_price >= knock_out_price[j - start_month]:
            flag_out[i] = 1
            flag_out_time[i] = j
            df['收盘价(元)_y'][i] = observation_price
            df['到期日'][i] = observation_time
            break

df = pd.concat([df, flag_out, flag_out_time], axis = 1)

# 每个标的存续期最小值（用于判断敲入）
min_data = [price_resample[df.index[i]:df['到期日'][i]].min().values for i in range(len(df.index))]
# 将 df 与 每个标的存续期最小值（用于判断敲入）合并
df = pd.concat([df, pd.DataFrame(min_data, index = df.index)], axis = 1)
# 之前的到期日可能存在非交易日的情况, 这里填入确切的到期日期, 并删去之前的日期
df = pd.merge(df, time_resample, left_on = '到期日', right_index = True, how = 'left').drop(columns = '到期日')
# 重命名列名称
df.columns = ['买入净值', '到期净值', '是否敲出', '敲出日期', '期间最低收盘价', '到期日']

df['收益率'] = df['到期净值']/df['买入净值'] - 1

df['期间最低收益率'] = df['期间最低收盘价']/df['买入净值'] - 1

######### 更改 apply 中计算收益的函数即可计算不同形态的收益率 ############
df[['凭证收益率', '是否敲入']] = df.apply(jiangqiaoxueqiu, axis = 1, 
                                 args = (knock_in - 1, normal_rate))

###################################################################


sns.displot(data = df[['是否敲出', '是否敲入']], x='是否敲入', col='是否敲出', height=3)

sns.displot(data = df[['是否敲出', '凭证收益率']], x='凭证收益率', col='是否敲出', height=3, stat='probability')

#sns.histplot(df['凭证收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)])

print(len(df), len(df[(df['是否敲出'] == 1) & (df['是否敲入'] == 0)]), len(df[(df['是否敲出'] == 1) & (df['是否敲入'] == 1)]), len(df[(df['是否敲出'] == 0) & (df['是否敲入'] == 0)]), len(df[(df['是否敲出'] == 0) & (df['是否敲入'] == 1)]))
print(len(df[(df['是否敲出'] == 1) & (df['是否敲入'] == 0)])/len(df), len(df[(df['是否敲出'] == 1) & (df['是否敲入'] == 1)])/len(df), len(df[(df['是否敲出'] == 0) & (df['是否敲入'] == 0)])/len(df), len(df[(df['是否敲出'] == 0) & (df['是否敲入'] == 1)])/len(df))