import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from getData import *


''' 交易日和时间数据格式转换函数 '''

trading_datelist = get_trading_datelist()

def convert_time_type(index_data, index_data_source):
    ''' 日期在index位置上，更改数据时间的类型，转换成python可以处理的datetime类型'''
    Date_info = index_data.index                # 指数时间记录
    if index_data_source == 'wind_file':
        date_info = (Date_info).strftime("%Y-%m-%d %H:%M:%S")   
        Date_info = [datetime.strptime(date_info[i], "%Y-%m-%d %H:%M:%S").date() for i in range(len(date_info))]
    elif index_data_source == 'efinance':
        Date_info = [datetime.strptime(Date_info[i], "%Y-%m-%d").date() for i in range(len(Date_info))]
    elif index_data_source == 'akshare':
        Date_info = Date_info.tolist()
    return Date_info


def is_trading_day(current_date):
    if type(current_date) != str:
        current_date = str(current_date)[:10]
    return current_date in trading_datelist
    

def last_trading_day(current_date):  # 包含当前的日期
    if type(current_date) != str:
        current_date = str(current_date)[:10]

    if current_date in trading_datelist:
        return trading_datelist[trading_datelist.index(current_date)-1]
    else:
        return [i for i in trading_datelist if i < current_date][-1]


def next_trading_day(current_date):
    if type(current_date) == str:
        current_date = pd.to_datetime(current_date).date()

    if current_date in trading_datelist:
        next_date = trading_datelist[trading_datelist.index(current_date)+1]
    else:
        next_date = [i for i in trading_datelist if i > current_date][0]
    return next_date


def ensure_trading_day(current_date):
    if type(current_date) == str:
        current_date = pd.to_datetime(current_date).date()

    if current_date in trading_datelist:
        return current_date
    else:
        next_date = next(date for date in trading_datelist if date > current_date)
        return next_date


