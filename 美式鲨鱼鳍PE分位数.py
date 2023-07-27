# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 11:29:59 2023

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
from  matplotlib.ticker import PercentFormatter
warnings.filterwarnings('ignore')
import sys
# 加载当前路径
sys.path.append('.\imports')
from simple_tools import filter_operator, get_data

####################### 分界线 ###############################3
def meishishayuqi(data, knock_out = 0.17,
                  knock_out_rate = 0.016,
                  basic_rate = 0.00,
                  participation_rate = 1):# data 为最后一天的收益率 & 期间最高收益率
    flag = 0
    # 这里的收益率还可以单独设计
    if data['期间最高收益率'] > knock_out:
        rate = knock_out_rate
        flag = 1
    else:
        rate = basic_rate + (data['收益率'] > 0) * participation_rate * data['收益率']
    return pd.Series([rate, flag]) # 使用 Series 能将两列值赋值到 df 中，否则值会以元组形式压缩成一列

########## 参数初始化 ###########
# 回测开始时间与结束时间
start_date = '2007-01-01'
# start_date = '2017-01-01'
end_date = '2023-07-21'
# 标的的存续期
month_period = 12
############## 导入数据与数据切片 ################
data, data_resample, data_copy = get_data(useapi = 0, underlying = '中证1000PETTM.xlsx')
# data, data_resample, data_copy = get_data(useapi = 1, underlying = '000016.SH', start = '2004-01-01')

data = data[start_date:end_date]

############ 分位数模块 ############
data = filter_operator(data, data_copy, lower_bound = 0.10, upper_bound = 0.20, rolling_window_width = 3)

######################################
# 买入时间平移 month_period 个月份
data['到期日'] = [data.index[i] + relativedelta.relativedelta(months = month_period) for i in range(len(data.index))]
# 将自然日的数据填补
df = pd.merge(data, data_resample, left_on = '到期日', right_index = True)
# 每个标的存续期最大值（用于判断敲出）
max_data = [data_resample[data.index[i]:data['到期日'][i]].max() for i in range(len(data.index))]

df = pd.merge(df, pd.DataFrame(max_data, index = data['到期日']), left_on = '到期日', right_index = True).drop_duplicates()

df.columns = ['买入净值', '到期日', '到期净值', '期间最高收盘价']

df['收益率'] = df['到期净值']/df['买入净值'] - 1

df['期间最高收益率'] = df['期间最高收盘价']/df['买入净值'] - 1

######### 更改 apply 中计算收益的函数即可计算不同形态美式鲨鱼鳍的收益率 ############
df[['凭证收益率', '是否敲出']] = df[['收益率', '期间最高收益率']].apply(meishishayuqi, axis = 1)

############## 绘图模块 #######################

#sns.histplot(df['是否敲出'], stat = 'probability')

#df['凭证收益率'].groupby(by = df['是否敲出']).count()

#sns.displot(data = df[['是否敲出', '凭证收益率']], x='凭证收益率', col='是否敲出', height=3, stat='probability')

# print(df['凭证收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)].groupby(by = pd.cut(df['凭证收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)], np.arange(0.005, 0.12, 0.02))).size())
# print(df['凭证收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)].groupby(by = pd.cut(df['凭证收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)], np.arange(0.005, 0.12, 0.02))).size()/len(df[(df['是否敲出'] == 0)&(df['收益率'] > 0)]))

# g = sns.histplot(df['收益率'])
# g.xaxis.set_major_formatter(PercentFormatter(1))
# plt.show()

# f = sns.histplot(df['收益率'], stat="density", cumulative=True, element="step", fill=False, bins = 500)
# f.xaxis.set_major_formatter(PercentFormatter(1))
# f.set_ylabel('累计概率')
# f.grid()
# plt.show()

print(len(df[(df['是否敲出'] == 1) & (df['收益率']<= 0)])/len(df), len(df[(df['是否敲出'] == 0) & (df['收益率']<= 0)])/len(df), len(df[(df['是否敲出'] == 1) & (df['收益率']> 0) & (df['收益率']< 0.17)])/len(df), len(df[(df['是否敲出'] == 0) & (df['收益率']> 0)])/len(df), len(df[(df['是否敲出'] == 1) & (df['收益率']>=0.17)])/len(df))


print(len(df), len(df[(df['是否敲出'] == 0) & (df['收益率']<= 0)]), len(df[(df['是否敲出'] == 0) & (df['收益率'] > 0)]), len(df[df['是否敲出'] == 1]))
print(len(df[(df['是否敲出'] == 0) & (df['收益率']<= 0)])/len(df), len(df[(df['是否敲出'] == 0) & (df['收益率'] > 0)])/len(df), len(df[df['是否敲出'] == 1])/len(df))

print(df['收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)].min(), df['收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)].max(), df['收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)].median(), df['收益率'][(df['是否敲出'] == 0)&(df['收益率'] > 0)].mean())