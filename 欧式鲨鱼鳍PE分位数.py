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
from  matplotlib.ticker import PercentFormatter
plt.rcParams["font.sans-serif"]=["SimHei"] #设置字体
mpl.rcParams['axes.unicode_minus']=False
import warnings
warnings.filterwarnings('ignore')
import sys
# 加载当前路径
sys.path.append('.\imports')
from simple_tools import filter_operator, get_data


####### 保本鲨鱼型收益凭证：欧式鲨鱼鳍 ########
def oushishayuqi(data, knock_out = 0.17,
                 knock_out_rate = 0.016,
                 basic_rate = 0.00,
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
# start_date = '2017-10-17'
start_date = '2017-01-01'
end_date = '2023-07-21'
# 标的的存续期
month_period = 12
############## 导入数据与数据切片 ################
data, data_resample, data_copy = get_data(useapi = 0, underlying = '中证1000PETTM.xlsx')
# data, data_resample, data_copy = get_data(useapi = 1, underlying = '000905.SH', start = '2004-01-01')
data = data[start_date:end_date]

############ 分位数模块 ############
data = filter_operator(data, data_copy, lower_bound = 0.35, upper_bound = 0.48, rolling_window_width = 3)

######################################
# 买入时间平移 month_period 个月份
data['到期日'] = [data.index[i] + relativedelta.relativedelta(months = month_period) for i in range(len(data.index))]
# 将自然日的数据填补
df = pd.merge(data, data_resample, left_on = '到期日', right_index = True)

df.columns = ['买入净值', '到期日', '到期净值']

df['收益率'] = df['到期净值']/df['买入净值'] - 1
######### 更改 apply 中计算收益的函数即可计算不同形态欧式的收益率 ############
df[['凭证收益率', '是否敲出']] = df['收益率'].apply(oushishayuqi)

############## 绘图模块 #######################

# print(df['凭证收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)].groupby(by = pd.cut(df['凭证收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)], [0, 0.1, 0.2])).size())
# print(np.round(100 * df['凭证收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)].groupby(by = pd.cut(df['凭证收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)], [0, 0.1, 0.2])).size()/len(df[(df['是否敲出'] == 0)&(df['收益率'] > 0)]), 2))

print(len(df), len(df[df['收益率']<0]), len(df[(df['是否敲出'] == 0) & (df['收益率'] > 0)]), len(df[df['是否敲出'] == 1]))
print(round(len(df[df['收益率']<0])/len(df) * 100, 2), round(len(df[(df['是否敲出'] == 0) & (df['收益率'] > 0)])/len(df) * 100, 2), round(len(df[df['是否敲出'] == 1])/len(df) * 100, 2))
print(df['收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)].min() * 100, df['收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)].max() * 100, df['收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)].median() * 100, df['收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)].mean() * 100)

############# 绘制收益率的代码 ################
g = sns.histplot(df['凭证收益率'], binwidth = 0.01, stat = 'probability')
g.xaxis.set_major_formatter(PercentFormatter(1))
g.set_xlabel('收益率')
g.set_ylabel('概率')
g.grid()