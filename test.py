#!/usr/bin/env python3
# coding: utf-8
import sys,os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
print("Python Info: ",sys.version,sys.path)
print("Current working directory: ",os.getcwd())

import matplotlib as mpl
mpl.rcParams['font.family'] = 'simhei' #用来正常显示中文标签
mpl.rcParams['axes.unicode_minus']=False #用来正常显示负号

sys.path.append('./imports')
import hello as myhello

myhello.hello()


data = pd.read_csv('input/zz1000.csv',index_col='日期')

# 定义一个函数来处理每个单元格
def remove_comma_and_convert_to_float(value):
    value_without_comma = value.replace(',', '')
    return float(value_without_comma)

# 使用 applymap() 对每个单元格应用函数
data = data.applymap(remove_comma_and_convert_to_float)

data = data.reindex(columns=['开盘价(元)','收盘价(元)','最低价(元)','最高价(元)'])
data.columns = ['open','close','low','high']

data['close'].plot()


plt.savefig('output/fig1.png')


