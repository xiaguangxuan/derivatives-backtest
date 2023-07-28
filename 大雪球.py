# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 08:59:22 2023

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
sys.path.append('./imports')
from simple_tools import filter_operator, get_data, knock_out_stage

####################### 分界线 ###############################3
def daxueqiu(data, knock_in, normal_rate):
    # flag 记录是否发生敲入事件
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
end_date = '2023-07-07'
# 标的的存续期
month_period = 24
# 敲出价格
knock_out = 1.02
# 敲入价格
knock_in = 0.8
# 从第几个月开始观察
start_month = 2 
# 未发生敲入的年化收益率
normal_rate = 0.1104

############## 导入数据与数据切片 ################
data, price_resample, time_resample, data_copy = get_data(useapi = 0, underlying = '中证1000PETTM.xlsx')
data = data[start_date:end_date]

############ 分位数模块 ############
data = filter_operator(data, data_copy, lower_bound = 0, upper_bound = 1, rolling_window_width = 3)

######################################

# 买入时间平移 month_period 个月份
data['到期日'] = [data.index[i] + relativedelta.relativedelta(months = month_period) for i in range(len(data.index))]
# 将自然日的数据填补
df = pd.merge(data, price_resample, left_on = '到期日', right_index = True, how = 'left')

############## 判断是否敲出 ##################
df = knock_out_stage(df, price_resample, knock_out, month_period, start_month)
########################################
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
df[['凭证收益率', '是否敲入']] = df.apply(daxueqiu, axis = 1, 
                                 args = (knock_in - 1, normal_rate))
####################################################################
sns.displot(data = df[['是否敲出', '是否敲入']], x='是否敲入', col='是否敲出', height=3)

sns.displot(data = df[['是否敲出', '凭证收益率']], x='凭证收益率', col='是否敲出', height=3, stat='probability')

#sns.histplot(df['凭证收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)])
