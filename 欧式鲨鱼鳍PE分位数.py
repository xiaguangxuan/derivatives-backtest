# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 11:17:47 2023

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


####### 保本鲨鱼型收益凭证：欧式鲨鱼鳍 ########
def oushishayuqi(data, knock_out = 0.1,
                 knock_out_rate = 0.035,
                 basic_rate = 0.005,
                 participation_rate = 1):# data 为最后一天的收益率
    flag = 0
    # 这里的收益率还可以单独设计
    if data > knock_out:
        rate = knock_out_rate
        flag = 1
    else:
        rate = basic_rate + (data > 0) * participation_rate * data
    return pd.Series([rate, flag]) # 使用 Series 能将两列值赋值到 df 中，否则值会以元组形式压缩成一列

########## 参数初始化 ###########
# 回测开始时间与结束时间
start_date = '2018-01-01'
end_date = '2023-07-17'
# 标的的存续期
month_period = 12
############## 导入数据与数据切片 ################
data, data_resample, data_copy = get_data(useapi = 0, underlying = '中证1000PETTM.xlsx')
# data, data_resample, data_copy = get_data(useapi = 1, underlying = '000852.SH')
data = data[start_date:end_date]

############ 分位数模块 ############
data = filter_operator(data, data_copy, lower_bound = 0.1, upper_bound = 0.5, rolling_window_width = 3)

######################################
# 买入时间平移 month_period 个月份
data['到期日'] = [data.index[i] + relativedelta.relativedelta(months = month_period) for i in range(len(data.index))]
# 将自然日的数据填补
df = pd.merge(data, data_resample, left_on = '到期日', right_index = True)

df.columns = ['买入净值', '到期日', '到期净值']

df['收益率'] = df['到期净值']/df['买入净值'] - 1
######### 更改 apply 中计算收益的函数即可计算不同形态欧式的收益率 ############
df[['凭证收益率', '是否敲出']] = df['收益率'].apply(oushishayuqi)
df.to_csv('output/欧式鲨鱼鳍.csv')
############## 绘图模块 #######################

# sns.histplot(df['凭证收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)])

# print(df['凭证收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)].groupby(by = pd.cut(df['凭证收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)], np.arange(0.005, 0.12, 0.02))).size())
# print(df['凭证收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)].groupby(by = pd.cut(df['凭证收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)], np.arange(0.005, 0.12, 0.02))).size()/len(df[(df['是否敲出'] == 0)&(df['收益率'] > 0)]))

# sns.histplot(df['收益率'])

# print(len(df[df['收益率']<0]), len(df[(df['是否敲出'] == 0) & (df['收益率'] > 0)]), len(df[df['是否敲出'] == 1]))
# print(len(df), len(df[df['收益率']<0])/len(df), len(df[(df['是否敲出'] == 0) & (df['收益率'] > 0)])/len(df), len(df[df['是否敲出'] == 1])/len(df))