# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 15:53:33 2023

@author: hasee
"""


import pandas as pd
from dateutil import relativedelta
import datetime
import sys
# 加载当前路径
sys.path.append('.')

def get_data(useapi = 0, underlying = '中证500PETTM.xlsx', 
             factor = 'PE_TTM', start = '2013-01-01', 
             end = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')):
    # input:
    # useapi --> 是否使用 api
    
    # underlying --> 若不使用 api，填写表格的名称, 如默认格式'中证500PETTM.xlsx'
    # 不使用 api 只需填写 useapi 和 underlying 两个参数, 注意表格的数据规范（数据文件第一列为日期，第二列为标的收盘价，第三列为用于筛选的指标）
    
    # underlying --> 若使用 api, 填写 api 相对应的查询代码（如:'000016.SH'）
    # factor --> 用于其他指标（用于筛选的指标）, 命名需满足 Wind API 接口的要求（查询标准命名后使用）.
    # strat --> 使用 API 提取数据的开始时间
    # end --> 使用 API 提取数据的结束时间（默认设置为程序运行的前一天）
    
    # output:
    # data --> 标的收盘价序列
    # data_resample --> 按照自然日重采样后的 标的收盘价序列
    # data_copy --> 标的筛选指标序列
    
    if useapi:
        import WindPy
        WindPy.w.start()
        # Wind API 获取数据 'CLOSE' 和 需要的其他数据（筛选指标）
        # wsd(标的代码, 所选指标, 开始时间, 结束时间, ***)
        data = WindPy.w.wsd(underlying, 'CLOSE' + ',' + factor, start, end, "Fill=Previous", usedf=True)[1].dropna()
        data.index = pd.DatetimeIndex(data.index)
        data.columns = ['收盘价(元)', '筛选指标']
        data_copy = data[['筛选指标']]
        data = data[['收盘价(元)']]
        
    else:
        # 读取本地数据，数据文件与运行程序放置在同一个文件夹
        # 数据文件第一列为日期，第二列为标的收盘价，第三列为用于筛选的指标
        data = pd.read_excel('input/' + underlying, index_col=(0), usecols = range(0, 2))
        data_copy = pd.read_excel('input/' + underlying, index_col=(0), usecols = [0, 2])
        data_copy.columns = ['筛选指标']
    
    data_resample = data.copy()
    # 增加一列 '日期' 标注填充数据的真实日期, 便于判断真实的存续时间
    data_resample['日期'] = data.index
    # 调整数据频率，将交易日改为自然日，同时缺失值向后补全
    data_resample = data_resample.resample('D').asfreq().bfill()
    price_resample = data_resample[['收盘价(元)']]
    time_resample = data_resample[['日期']]

    return data, price_resample, time_resample, data_copy
######################################################

def filter_operator(data, data_copy, is_quantile = 1, lower_bound = 0, upper_bound = 1, 
                    is_rolling_window = 1, rolling_window_width = 3, fixed_window_beginning = '2005-01-01'):
    ############ 分位数模块 ############
    # input:
    # data --> 标的时间序列（时间的 benchmark）
    # data_copy --> 筛选指标的序列（涉及窗口估计，时间需要长于 data）
    # is_quantile --> 是否使用分位数进行筛选（取 0 则使用绝对的数值进行筛选）
    # lower_bound, upper_bound --> 考察的分位数范围（is_quantile 取 0 则为绝对数值的范围）
    # is_rolling_window --> 扩展窗口 还是 滚动窗口
    # rolling_window_width --> 滚动窗口的长度
    # fixed_window_beginning --> 扩展窗口的开始时间
    
    # output: 符合筛选条件的 标的时间序列
    
    # 历史分位数
    history_quantile_index = []
    # 使用分位数进行筛选还是绝对数值进行筛选
    if is_quantile:
        # 是滚动窗口
        if is_rolling_window:
            # 遍历每一个时刻
            for t in data.index:
                # 获得这一时刻的历史分位数（滚动窗口）
                history_quantile = data_copy[t - relativedelta.relativedelta(years = rolling_window_width):t]['筛选指标'].rank(pct = True)[-1]
                # 这一时刻的历史分位数介于 lower 和 upper bound 之间
                if (history_quantile <= upper_bound) & (history_quantile >= lower_bound):
                    history_quantile_index.append(t)
        # 是扩展窗口
        else:
            # 遍历每一个时刻
            for t in data.index:
                # 获得这一时刻的历史分位数（扩展窗口）
                history_quantile = data_copy[fixed_window_beginning:t]['筛选指标'].rank(pct = True)[-1]
                # 这一时刻的历史分位数介于 lower 和 upper bound 之间
                if (history_quantile <= upper_bound) & (history_quantile >= lower_bound):
                    history_quantile_index.append(t)
    else:
        for t in data.index:
            # 获得这一时刻筛选指标的绝对数值
            history_quantile = data_copy.loc[t]['筛选指标']
            # 这一时刻筛选指标的绝对数值介于 lower 和 upper bound 之间
            if (history_quantile <= upper_bound) & (history_quantile >= lower_bound):
                history_quantile_index.append(t)
                
    # 根据所需要的历史分位数，生成满足条件的时间序列
    return data.loc[history_quantile_index]
##################################################

def knock_out_stage(df, data_resample, 
                    knock_out, month_period = 12, start_month = 1):
    # input:
    # df --> 一张记录在特定交易日开仓的表格, 主要要素: index 为开仓时间; '收盘价(元)_x' 为开仓时的 标的收盘价;
    #        '收盘价(元)_y' 为不考虑敲出条件，到期时的收盘价; '到期日' 为不考虑敲出条件的到期日
    # data_resample --> 按照自然日重采样后的 标的收盘价序列
    # knock_out --> 敲出价 按百分数计
    # month_period --> 存续期
    # start_month --> 锁定期

    # output:
    # 在原始表格 df 的基础上, 考虑敲出条件, 对到期 or 敲出时的日期和收盘价进行了更新, 并增加记录了'是否敲出', '敲出月份' 两列参数

    # 记录是否敲出
    flag_out = pd.Series()
    # 记录敲出发生在第几个月
    flag_out_time = pd.Series()
    # 样本的最大索引 or 数据的上限 or 数据的截止时间
    time_limit = data_resample.index[-1]
    # 遍历每一个时点
    for i in df.index:
        # 敲出价格
        knock_out_price = df['收盘价(元)_x'][i] * knock_out
        # 设定该时点对应的默认参数，即未敲出
        flag_out[i] = 0
        flag_out_time[i] = -1
        # 遍历每一个观察日
        for j in range(start_month, month_period + 1):
            # 遍历每一个观察日（间隔为一个月）
            observation_time = i + relativedelta.relativedelta(months = j)
            # 如果观察日超过数据的最大索引，说明合约还在存续期内，弹出循环
            if observation_time > time_limit:
                break
            # 若观察日在数据的索引范围内，找到该观测值
            observation_price = data_resample.loc[observation_time].values
            # 若该观测值大于敲出价格
            if observation_price >= knock_out_price:
                # 敲出记为 1，并记录下对应的发生月份，并把相应的参数填入表格 df 进行更新，弹出循环
                flag_out[i] = 1
                flag_out_time[i] = j
                df['收盘价(元)_y'][i] = observation_price
                df['到期日'][i] = observation_time
                break
    # 将 df 与 敲出信号、第几个月敲出合并
    return pd.concat([df, flag_out, flag_out_time], axis = 1)