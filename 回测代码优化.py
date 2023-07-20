#!/usr/bin/env python
# coding: utf-8

# In[1]:


# -*- coding: utf-8 -*-

"""
Created on Tue Dec 15 15:42:07 2020

@author: liuguixu revised: Fan Chen
"""

'''自动敲入敲出型雪球结构历史回测数据分析'''


'''导入lib'''

import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta as rd
import pandas as pd
from tqdm import tqdm
from matplotlib import rcParams
import sys
sys.path.append('.')
import SBplot
rcParams['font.sans-serif'] = ['SimHei']
rcParams['axes.unicode_minus'] = False

# data API
#from iFinDPy import *
#THS_iFinDLogin('xmdx092','572741')
#from WindPy import *
#w.start()
import efinance as ef
import akshare as ak

# In[2]:


'''其它数据声明'''

index_data_source = 'efinance'      # 'wind':"000905.SH" / 'ifind':'000905.SH' / 'efinance': "中证500"  / 'akshare': 'sh000905'
# 用 Wind & iFind 提取数据的开始和截止日期
startdate = '20190101'
enddate = '20230717'


'''辅助信息'''
auxiliary_indicators_range = {'PE_TTM':[0,50]}     # 等于边界的值会被保留
# auxiliary_indicators_range = {}

auxiliary_indicators = list(auxiliary_indicators_range)

'''雪球观察区间'''
# 观察起始日
Ob_ini = (dt.datetime(2015,1, 1, 0, 0)).date()            # 起始观察日，格式：(xxxx年，xx月，xx日，0时，0分)
# 观察到期日（最好保证是一个交易日）
Ob_end = (dt.datetime(2023, 7, 14, 0, 0)).date()            # 终止观察日，格式：(xxxx年，xx月，xx日，0时，0分)
# 零时间
Date_zero_point = (dt.datetime(1900, 1, 1, 0, 0)).date()        


# In[3]:


'''雪球参数设置'''

underlying = "上证50"
# underlying_code = ef.stock.get_base_info(underlying)['股票代码'] + '.SH'
underlying_code = "上证50" 
#underlying_code = '000016.SH' # ifind 和 wind 提取时使用的代码

Ki_bc = 0.95                              # 敲入条件，敲入观察日的价格/起初价格

# 产品约定年限(月) 
start_date = dt.datetime(2005, 1, 1, 0, 0).date()   # 在后面被重新赋值，遍历观测区间的所有日期
Option_expire_month = 24                            # 只以月度来结算，一年则调整为12个月

# 票息设置
Coupon = 0.1                                      # 敲出收益率
Coupon_1 = 0.005                                     # 红利票息，针对无敲入无敲出和敲出收益率不同的情形
Ko_forward_month = 3                                # 首个敲出观察日为距离观察起始日后的第x月

# 边际条件设置(后续可能会在循环里调整)
begin_Ko_bc = 1.03                                  # 敲出条件，首个敲出观察日的价格/起初价格
Ko_fre_month = 1                                    # 敲出观察频率为每月
step_ratio = -0.00                                  # 每月下调比例

# 雪球类型： plus_put(不追保雪球)/vanilla/parachute/enhance/锁盈止损雪球/小雪球/早利雪球
snowball_type =  '早利雪球' 

Coupon_option = 0
Coupon_adjusted = 0

if snowball_type == '小雪球':
    assert Coupon_option >= 0

if snowball_type == '早利雪球':
    assert Coupon_option >= 0
    
Coupon_adjusted_param = {'coupon_adjusted': 0.05,'month_to_adjust_coupon': 12}
if snowball_type == '早利雪球':
    assert Coupon_adjusted_param['coupon_adjusted'] >= 0
    
margin_call = True              # False: 不可以追保，保证金亏完即终止, 其他情况为True
maximum_lose = 1

if margin_call == False:
    maximum_lose = 1 - Ki_bc


# In[4]:


'''雪球参数形成固定配置'''
time_param = {'start_date':start_date, 'Option_expire_month':Option_expire_month}
Ki_param = {'Ki_bc':Ki_bc}
Ko_param = {'Ko_forward_month':Ko_forward_month, 'begin_Ko_bc':begin_Ko_bc, 
            'Ko_fre_month':Ko_fre_month, 'step_ratio':step_ratio}
Coupon_param = {'Coupon':Coupon, 'Coupon_1':Coupon_1}
Profit_param = {'maximum_lose': maximum_lose}

if snowball_type ==  'parachute':
    last_ko = float(input('请输入该降落伞雪球最后一期敲出参数:'))
    Ko_param['last_ko'] = last_ko
    
if snowball_type ==  'enhance':
    enhance_ratio = float(input('请输入该增强型雪球上涨参与率:'))
    Profit_param['enhance_ratio'] = enhance_ratio
    


# In[5]:


'''数据读取、清洗函数'''
 
def read_PE_data(underlying, show_data_info=False):
    under_dict = {'sh000852': 'zz1000pe', '中证1000': 'zz1000pe', '上证50': '000016.sh_pettm'}
    PE_data = pd.read_excel('./input/%s.xlsx'%(under_dict[underlying]))
    PE_data.dropna(inplace=True)
    PE_data = PE_data.sort_values(by='时间')
    PE_data.drop(columns =['代码'], inplace = True)
    PE_data.drop(columns =['简称'], inplace = True)
    PE_data.set_index('时间',drop=True,inplace=True)
    if index_data_source == 'wind':
        PE_data = w.wsd(underlying, "pe_ttm", startdate, enddate, "Fill=Previous", usedf=True)[1]
        if show_data_info:
            print('读取PE_TTM数据完成，辅助数据PE_TTM有效日期为 %s 至 %s '%(PE_data.index[0],PE_data.index[-1]))
            print(PE_data)
    elif index_data_source == 'ifind':
        PE_data = THS_DS(underlying,'ths_pe_ttm_index','100,100','block:history', startdate, enddate).data
        PE_data.set_index('time', drop = True, inplace = True)
        PE_data = PE_data[['ths_pe_ttm_index']]
        PE_data.columns = ['PE_TTM']
        if show_data_info:
            print('读取PE_TTM数据完成，辅助数据PE_TTM有效日期为 %s 至 %s '%(PE_data.index[0],PE_data.index[-1]))
            print(PE_data)
    return PE_data

def read_PB_data(underlying, show_data_info=False):
    if index_data_source == 'wind':
        PB_data = w.wsd(underlying, "pb_lyr", startdate, enddate, "Fill=Previous", usedf=True)[1]
        if show_data_info:
            print('读取PB数据完成，辅助数据PB有效日期为 %s 至 %s '%(PE_data.index[0],PE_data.index[-1]))
            print(PE_data)
    elif index_data_source == 'ifind':
        PB_data = THS_DS(underlying,'ths_pb_index','107,100','block:history', startdate, enddate).data
        PE_data.set_index('time', drop = True, inplace = True)
        PE_data = PE_data[['ths_pb_index']]
        PE_data.columns = ['PB_LYR']
        if show_data_info:
            print('读取PB数据完成，辅助数据PB有效日期为 %s 至 %s '%(PE_data.index[0],PE_data.index[-1]))
            print(PB_data)
    return PB_data


def read_ERP_data(underlying, show_data_info=False):
    under_dict = {'sh000852': 'zz1000', 'sh000905': 'zz500', '中证1000': 'zz1000'}
    col_name = under_dict[underlying]
    ERP_data = pd.read_csv('./data/%s.csv'%('erp'))
    ERP_data = ERP_data.rename(columns = {'Unnamed: 0': '时间'})
    ERP_data = ERP_data.loc[:,['时间',col_name]]
    ERP_data.dropna(inplace=True)
    ERP_data.set_index('时间',inplace = True)
    if show_data_info:
        print('读取ERP数据完成，辅助数据ERP有效日期为 %s 至 %s '%(ERP_data.index[0],ERP_data.index[-1]))
        print(ERP_data)
    return ERP_data


def read_ERP_percentile_data(underlying, show_data_info=False):
    under_dict = {'sh000852': 'zz1000', 'sh000905': 'zz500', '中证1000': 'zz1000pe'}
    col_name = under_dict[underlying]
    ERP_data = pd.read_csv('./data/%s.csv'%('erp'))
    ERP_data = ERP_data.rename(columns = {'Unnamed: 0': '时间'})
    ERP_data = ERP_data.loc[:,['时间',col_name]]
    ERP_data.dropna(inplace=True)
    ERP_data.set_index('时间',inplace = True)
    ERP_data['percentile'] = ERP_data[col_name].rolling(252).rank(pct=True)
    ERP_data = ERP_data.loc[:, ['percentile']]
    if show_data_info:
        print(ERP_data)
    return ERP_data


def fetching_data(underlying, index_data_source='wind',show_data_info=False):
    if index_data_source == 'wind':
        index_data = w.wsd(underlying, "close", startdate, enddate, "Fill=Previous", usedf=True)[1]
        
        '''index_data = pd.read_excel('./data/%s.xlsx'%(underlying))
        index_data = index_data.loc[:,['日期','收盘价(元)']]
        index_data['收盘价(元)'] = index_data['收盘价(元)'].round(2)
        correct_time_type = type(pd.to_datetime('1970-01-01 08:00:00')) # 正常的日历类型应该为correct_time_type
        if_correct_time_type = [type(index_data.loc[i,'日期'])==correct_time_type for i in range(index_data.shape[0])] # 记录bool组
        print('[Message from function: fetching_data] 即将清除无效日期数据————总共清除%d组'%(if_correct_time_type.count(False)))
        index_data = index_data[if_correct_time_type] # mask运算，只保留True的位置
        index_data.set_index('日期',drop=True,inplace=True)'''    
        
    elif index_data_source == 'ifind':
        index_data = THS_HQ(underlying, 'close','', startdate, enddate).data[['time', 'close']]
        index_data.set_index('time', drop = True, inplace = True)
    
    elif index_data_source == 'efinance':
        index_data = ef.stock.get_quote_history(underlying)
        index_data = index_data.loc[:,['日期','收盘']]
        index_data.set_index('日期',drop=True,inplace=True)
    
    elif index_data_source == 'akshare':
        index_data = ak.fund_etf_hist_sina(symbol = underlying) 
        index_data = index_data.loc[:,['date','close']]
        index_data.set_index('date',drop=True,inplace=True)
        
        
    if show_data_info:
        print(index_data)
        
    return index_data


# In[6]:


'''交易日和时间数据格式转换函数'''
def convert_time_type(index_data, index_data_source):
    ''' 日期在index位置上，更改数据时间的类型，转换成python可以处理的datetime类型'''
    Date_info = index_data.index                # 指数时间记录
    if index_data_source == 'wind': 
        Date_info = Date_info.tolist()
    elif index_data_source == 'efinance':
        Date_info = [dt.datetime.strptime(Date_info[i], "%Y-%m-%d").date() for i in range(len(Date_info))]
    elif index_data_source == 'akshare':
        Date_info = Date_info.tolist()
    elif index_data_source == 'ifind':
        Date_info = [dt.datetime.strptime(Date_info[i], "%Y-%m-%d").date() for i in range(len(Date_info))]
        
    return Date_info


def last_trading_day(base_time, Date_info):  # 包含当前的日期
    cur_time = base_time
    assert cur_time >= Date_info[0]
    while cur_time not in Date_info: 
        cur_time -= rd(days=1)
    return cur_time, list(Date_info).index(cur_time)


def next_trading_day(base_time, Date_info):
    cur_time = base_time
    assert cur_time <= Date_info[-1]
    while cur_time not in Date_info: 
        cur_time += rd(days=1)
    return cur_time, list(Date_info).index(cur_time)
# index 类似在做列表查询的功能，index返回就是和列表第一天的差值（中间的天数）


# In[7]:


class Snowball_Option(object):
    def __init__(self, snowball_type, underlying, time_param, Ki_param, Ko_param, 
                 Coupon_param, Profit_param):
        self.underlying = underlying
        self.snowball_type = snowball_type
        self.time_param = time_param
        self.Ki_param = Ki_param
        self.Ko_param = Ko_param
        self.Coupon_param = Coupon_param
        self.Profit_param = Profit_param
        self.start_index = None
        self.stop_index = None
        self.terminal_month = None 
        
    def update_param(self, current_month):
        # 更新敲出线
        # 降落伞雪球的情况
        if self.snowball_type == 'parachute' and current_month == self.time_param['Option_expire_month']:
            self.Ko_param['Ko_bc'] = self.Ko_param['last_ko']
        # 降敲雪球的情况
        else:
            self.Ko_param['Ko_bc'] = self.Ko_param['begin_Ko_bc']               + self.Ko_param['step_ratio'] * (current_month - self.Ko_param['Ko_forward_month'])
        return 0
        
    def Snowball_Knockin_Determine(self, Date_info, Index_info, start_i, stop_i):
        for j in range(start_i + 1, stop_i + 1):   #【每日】敲入判定，【注意：从开始的第二天开始判定到结束的后一天，到期日】
            if Index_info[j] < round(self.start_index * self.Ki_param['Ki_bc'],2):  # 如果观测窗口有敲入
                return Date_info[j], Index_info[j]

        return Date_zero_point, 0 # 如果之前都没有判别到的话 敲入时间定为零时间  # j为敲入点位或最后一个观测点位，意思是未敲入

    def Snowball_Knockout_Determine(self, Date_info, Index_info, start_i, stop_i, Time_stop):
        # 返回敲出时刻和敲出价格
        for cur_mon in range(self.Ko_param['Ko_forward_month'], self.time_param['Option_expire_month'] + 1):
            self.update_param(cur_mon)      
            Time_ko = self.time_param['start_date'] + rd(months = cur_mon * Ko_fre_month)
            try:
                Time_ko = next_trading_day(Time_ko, Date_info)[0]
            except:
                break# 问题，最后一个expire date 不是交易日，就被 break 了
                
            if Time_ko <= self.time_param['stop_date']:  # time_stop 其实是期权到期日，但是不能超过观察日前的最后一个交易日 time_stop已经是一个交易日
                # 查询当前时间和当前价格
                Time_ko_i = list(Date_info).index(Time_ko)       # 敲出指针
                Time_ko_index = Index_info[Time_ko_i]      # 敲出价格
                # 当前价格如果高于敲出价，记录下敲出的月份和敲出的价格
                if Time_ko_index >= round(self.start_index * self.Ko_param['Ko_bc'],2):
                    self.terminal_month = cur_mon
                    self.stop_index = Time_ko_index
                    return Time_ko, Time_ko_index
                # 下面这一部分似乎可以去掉 #
            else:
                # 否则（观察日超出），敲出月份为空，Time_stop = Time_start + rd(months = Option_expire_month)，到期日的价格
                self.terminal_month = None
                self.stop_index = Index_info[Date_info.index(Time_stop)]
                
                break
        self.terminal_month = cur_mon # 引入了Ko_fre_month，但是似乎都没有按照观察频率对结果进行调整
        
        return Date_zero_point, 0


# In[8]:


def sort_result(snowball_object, Ki_date, Ko_date, if_ki_ko_sign, ko_month_num, profit_annual, profit_abs):
    # Ki_date & Ko_date 记录敲入敲出时间
    if Ki_date == Date_zero_point and Ko_date == Date_zero_point: # 未敲入未敲出
        if_ki_ko_sign.append('nki_nko')
        ko_month_num.append(None)   

        if snowball_object.snowball_type == '早利雪球':
            # 早利雪球收益的计算似乎有些问题，terminal_month 是最终敲出时存续了多少个月
            # 不理解的另一点：未敲入未敲出为什么还要判断这些东西？直接拿调整后的 low_coupon 呐
            months_high_coupon = min(snowball_object.terminal_month, Coupon_adjusted_param['month_to_adjust_coupon'])
            months_low_coupon = max(snowball_object.terminal_month - months_high_coupon,0)
            
            profit_abs.append(Coupon_1*months_high_coupon/12 + Coupon_adjusted_param['coupon_adjusted'] * months_low_coupon/12)
            
        else:
            # Coupon_1 未敲出票息
            profit_abs.append(Coupon_1*snowball_object.terminal_month/12)
        # 根据存续期调整的年化票息
        profit_annual.append(profit_abs[-1] / snowball_object.terminal_month * 12)
        

    elif Ki_date != Date_zero_point and Ki_date < Ko_date:      # 敲入之后才敲出
        if_ki_ko_sign.append('ki_ko')
        ko_month_num.append(snowball_object.terminal_month)

        if snowball_object.snowball_type == '早利雪球':
            # 还是收益的计算上好像有问题
            # 判断存续期和一阶段高票息直接的大小关系，个人认为这就足够了
            months_high_coupon = min(snowball_object.terminal_month, Coupon_adjusted_param['month_to_adjust_coupon'])
            months_low_coupon = max(snowball_object.terminal_month - months_high_coupon, 0)
            
            profit_abs.append(Coupon_1*months_high_coupon/12 + Coupon_adjusted_param['coupon_adjusted'] * months_low_coupon/12)
            
        else:
            profit_abs.append(Coupon_1*snowball_object.terminal_month/12)
            
        profit_annual.append(profit_abs[-1] / snowball_object.terminal_month * 12)

    elif Ko_date != Date_zero_point:  # 敲出，或敲出之后才有敲入                        
        if_ki_ko_sign.append('nki_ko')
        ko_month_num.append(snowball_object.terminal_month)
        
        if snowball_object.snowball_type == '早利雪球':
            # 同样的问题
            months_high_coupon = min(snowball_object.terminal_month, Coupon_adjusted_param['month_to_adjust_coupon'])
            months_low_coupon = max(snowball_object.terminal_month - months_high_coupon, 0)
            
            profit_abs.append(Coupon_1*months_high_coupon/12 + Coupon_adjusted_param['coupon_adjusted'] * months_low_coupon/12)
            
        else:
            profit_abs.append(Coupon_1*snowball_object.terminal_month/12)
            
        profit_annual.append(profit_abs[-1] / snowball_object.terminal_month * 12)

    else:
        if_ki_ko_sign.append('ki_nko')    # 敲入无敲出
        ko_month_num.append(None)
        Time_stop_index = snowball_object.stop_index
        Time_start_index = snowball_object.start_index
        Ki_bc = snowball_object.Ki_param['Ki_bc']
        Option_expire_month = snowball_object.time_param['Option_expire_month']

        if snowball_object.Profit_param['maximum_lose'] != None :
            profit_abs.append(min(max(Time_stop_index / Time_start_index - 1, - maximum_lose),0))   # 最多只亏损到保证金
            profit_annual.append(min(max(Time_stop_index / Time_start_index - 1,- maximum_lose),0)* 12 / Option_expire_month)   # 75% 保本
        elif snowball_object.snowball_type == '小雪球':
            profit_annual.append(-Coupon_option)
            profit_abs.append(-Coupon_option*snowball_object.terminal_month/12)
        else:
            profit_abs.append(min(Time_stop_index / Time_start_index - 1,0))
            profit_annual.append(min(Time_stop_index / Time_start_index - 1,0)* 12 / Option_expire_month)
            
    # 这里对 pd.Series(if_ki_ko_sign[-1]).isin(['ki_nko','nki_nko']).values做了修改
    if snowball_object.snowball_type ==  'enhance' and pd.Series(if_ki_ko_sign[-1]).isin(['ki_ko','nki_ko']).values:
        # 在原有收益基础上加了增强部分
        profit_abs[-1] += (snowball_object.stop_index / snowball_object.start_index - 1) * snowball_object.Profit_param['enhance_ratio']
        profit_annual[-1] = profit_abs[-1] * snowball_object.terminal_month/12
        
    return if_ki_ko_sign, ko_month_num, profit_annual, profit_abs


# In[9]:


'''获取信息'''
index_data = fetching_data(underlying_code, index_data_source)
Date_info = convert_time_type(index_data, index_data_source)  # 交易日信息【类型：列表】

# assert Date_info[-1] >= Ob_end and Date_info[0] <= Ob_ini  # 声明数据集包含观测区间，否则报错

Index_info = list(index_data.iloc[:,0])         # 指数价格记录

'''获取辅助信息'''
auxiliary_indicators_data = dict()

if 'PE_TTM' in auxiliary_indicators:
    auxiliary_indicators_data['PE_TTM'] = read_PE_data(underlying_code)
    
if 'PB' in auxiliary_indicators:
    auxiliary_indicators_data['PB'] = read_PB_data(underlying_code)    

if 'ERP' in auxiliary_indicators:
    auxiliary_indicators_data['ERP'] = read_ERP_data(underlying)

if 'ERP_percentile' in auxiliary_indicators:
    auxiliary_indicators_data['ERP_percentile'] = read_ERP_percentile_data(underlying)


# In[10]:

'''计算时间参数'''

# 实际起始日期和指针
Time_ini, Time_ini_i = next_trading_day(Ob_ini, Date_info) # 实际起始【观察】指针落在观察日期开始之后的第一个交易日  # 总观察窗口的实际起始指针【关于Date_info列表】

Time_end, _ = last_trading_day(Ob_end, Date_info) 
Time_end_bound, _ = last_trading_day(Date_info[-1] - rd(months = Ko_forward_month), Date_info) 

Time_end = min(Time_end_bound, Time_end)

Time_end_i = Date_info.index(Time_end)

# 其余时间信息设置
Time_counter = Time_end_i - Time_ini_i + 1             # 观察窗口总体个数


# In[11]:


'''输出结果初始化'''
Date_stop_info = list()                                # 到期日期记录
Ki_date = list()                                       # 敲入日期记录
Ko_date = list()                                       # 敲出日期记录
Ki_index = list()                                      # 敲入日期指针记录                                      
Ko_index = list()                                      # 敲出日期指针记录
max_drawdown_info = list()                             # 最大回撤信息

if_ki_ko_sign = list()                                 # 敲入敲出指示 'ki_ko','ki_nko', 'nki_ko', 'nki_nko'

ko_month_num = list()                                  # 敲出所需时间（月度）
rolling_vol = list()                                   # 滚动波动率
Date_stop_info = list()                                # 终止日期信息
Index_stop_info = list()                               # 终止日期指针信息

profit_abs = list()                                    # 绝对收益
profit_annual = list()                                 # 年化收益

maturity_sign = list()                                 # 到期指示(回测数据足够覆盖至到期，但是不意味着不提前敲出)

auxiliary_indicators_info = dict()

for auxiliary_indicator in auxiliary_indicators:
    auxiliary_indicators_info[auxiliary_indicator] = []


# In[12]:


'''滚动观察窗口，计算结果'''

for i in tqdm(range(Time_ini_i, Time_end_i + 1)):

    Time_start = Date_info[i]
    
    indicators = []
    for auxiliary_indicator in auxiliary_indicators:
        aux_indi_data = auxiliary_indicators_data[auxiliary_indicator]
        # 读取 Wind 数据
        if index_data_source == 'wind':
            indicator = aux_indi_data[aux_indi_data.index == Time_start].iloc[0,0]
        else:
            indicator = aux_indi_data[aux_indi_data.index == str(Time_start)].iloc[0,0]
        auxiliary_indicators_info[auxiliary_indicator].append(indicator)
    
    time_param['start_date'] = Time_start
    snowball = Snowball_Option(snowball_type, underlying, time_param, Ki_param, Ko_param, Coupon_param, Profit_param)
    
    # 滚动观察窗口信息
    snowball.time_param['start_date'] = Date_info[i]    # 滚动观察窗口的实际起始时间
    snowball.start_index = Index_info[i]  # 滚动观察窗口的起始指数

    Time_stop = Time_start + rd(months = Option_expire_month) # 到期时间

    # 分两种情况讨论滚动窗口终止时间（增加）
    if Time_stop <= Date_info[-1]:                  # 回测数据覆盖存续期间      
        Time_stop = next_trading_day(Time_stop,Date_info)[0]
        maturity_sign.append(1)   
    else:   # 回测数据不足总期限，但至少有三个月
        Time_stop = last_trading_day(Ob_end,Date_info)[0] # 终止时间【期权可能仍然存续】为截止观察日前的最后一个交易日
        maturity_sign.append(0)
                 
        
    snowball.time_param['stop_date'] = Time_stop     
    Time_stop_i = list(Date_info).index(Time_stop)       # 滚动观察窗口的实际终止指针
    Time_stop_index = Index_info[Time_stop_i]      # 滚动观察窗口的实际终止点位
    snowball.stop_index = Time_stop_index
    
    # 该滚动观察窗口敲入判定
    Ki_date_index = snowball.Snowball_Knockin_Determine(Date_info, Index_info, i, Time_stop_i)
    Ki_date.append(Ki_date_index[0])
    Ki_index.append(Ki_date_index[1])

        
    # 该滚动观察窗口敲出判定
    Ko_date_index = snowball.Snowball_Knockout_Determine(Date_info, Index_info, i, Time_stop_i, Time_stop)
    Ko_date.append(Ko_date_index[0])
    Ko_index.append(Ko_date_index[1])
    
    
    # 该滚动观察窗口敲入敲出统计和收益率计算
    if_ki_ko_sign, ko_month_num, profit_annual, profit_abs = sort_result(snowball, Ki_date[-1],Ko_date[-1], if_ki_ko_sign, ko_month_num, profit_annual, profit_abs)
                
    
    # 波动率计算
    # vol = stat.stdev(Index_info[i + 1 : Time_stop_i] / Index_info[i : Time_stop_i - 1] - 1) * np.sqrt(Time_stop_i - i)
    vol = 0
    rolling_vol.append(vol)
    
    # 最大回撤计算(期初至实际结束日期)
#     max_drawdown = min(Index_info[i:Time_ko_i])/Time_start_index - 1 # ? 如果未敲出怎么办
#     max_drawdown_info.append(max_drawdown)
    
    # 终止信息记录
    Date_stop_info.append(Time_stop)
    Index_stop_info.append(Time_stop_index)


# In[13]:


'''将结果写入excel'''
df = pd.DataFrame(index = Date_info[Time_ini_i:i+1])
df['初始指数'] = Index_info[Time_ini_i:i+1]
df['到期日期'] = Date_stop_info

mask = dict()


# df['到期日期'] = Date_stop_info
df['终止指数'] = Index_stop_info 
df['敲入日期'] = Ki_date
df['敲入点位'] = Ki_index
df['敲出日期'] = Ko_date
df['敲出点位'] = Ko_index
df['敲入敲出状态'] = if_ki_ko_sign
df['敲出所需时间（月度）'] = ko_month_num
df['完成周期'] = maturity_sign
df['绝对收益率'] = profit_abs
df['年化收益率'] = profit_annual

# df['波动率'] = rolling_vol

mask = df['敲入敲出状态'].isin(['nki_ko','ki_ko']) | ((df['敲入敲出状态'] == 'nki_nko') & (df['完成周期']==1))
df['得到高票息'] = np.zeros_like(Date_stop_info)
df.loc[mask,'得到高票息'] = 1

df['敲出'] = np.zeros_like(Date_stop_info)
df.loc[df['敲入敲出状态'].isin(['nki_ko','ki_ko']),'敲出'] = 1

df.loc[df['敲入敲出状态']=='ki_ko','敲入敲出状态'] = '敲入，敲出'
df.loc[df['敲入敲出状态']=='nki_ko','敲入敲出状态'] = '不敲入，敲出'
df.loc[df['敲入敲出状态']=='ki_nko','敲入敲出状态'] = '敲入，不敲出'
df.loc[df['敲入敲出状态']=='nki_nko','敲入敲出状态'] = '不敲入，不敲出'

for auxiliary_indicator in auxiliary_indicators:
    df[auxiliary_indicator] = auxiliary_indicators_info[auxiliary_indicator]
    value_range = (auxiliary_indicators_range[auxiliary_indicator][0],auxiliary_indicators_range[auxiliary_indicator][1])
    mask[auxiliary_indicator] = (df[auxiliary_indicator]>= value_range[0]) & (df[auxiliary_indicator]<= value_range[1])

df_raw = df[:]
for auxiliary_indicator in auxiliary_indicators:
    df = df[mask[auxiliary_indicator]]

# writer = pd.ExcelWriter('./output/snowball-{}-{}-{}-{}-{}-{}.xlsx'.format(
#         underlying,begin_Ko_bc,Ki_bc,Option_expire_month,Ko_forward_month,step_ratio))

# df_raw.to_excel(writer, sheet_name='全数据', index=False)
df_raw.to_csv('output/snowball-{}-{}-{}-{}-{}-{}.csv'.format(
        underlying,begin_Ko_bc,Ki_bc,Option_expire_month,Ko_forward_month,step_ratio))
#writer.to_()


# In[14]:


class SBplot_Info(object):
    def __init__(self, snowball_type, Ki_bc, margin_call, Option_expire_month, Ko_forward_month, begin_Ko_bc,
                 Coupon, Coupon_1, Coupon_option, maximum_lose, step_ratio, auxiliary_indicators,
                 auxiliary_indicators_range, Ob_ini, Ob_end, Coupon_adjusted_param, underlying, underlying_code,
                 df, df_raw):
        self.snowball_type = snowball_type
        self.Ki_bc = Ki_bc
        self.margin_call = margin_call
        self.Option_expire_month = Option_expire_month
        self.Ko_forward_month = Ko_forward_month
        self.begin_Ko_bc = begin_Ko_bc
        self.Coupon = Coupon
        self.Coupon_1 = Coupon_1
        self.Coupon_option = Coupon_option
        self.maximum_lose = maximum_lose
        self.step_ratio = step_ratio
        self.auxiliary_indicators = auxiliary_indicators
        self.auxiliary_indicators_range = auxiliary_indicators_range
        self.Ob_ini = Ob_ini
        self.Ob_end = Ob_end
        self.Coupon_adjusted_param = Coupon_adjusted_param
        self.underlying_name = underlying
        self.underlying_code = underlying_code
        self.df = df
        self.df_raw = df_raw


info = SBplot_Info(snowball_type, Ki_bc, margin_call, Option_expire_month, Ko_forward_month, begin_Ko_bc,
                   Coupon, Coupon_1, Coupon_option, maximum_lose, step_ratio, auxiliary_indicators,
                   auxiliary_indicators_range, Ob_ini, Ob_end, Coupon_adjusted_param, underlying, underlying_code,
                   df, df_raw)


# In[15]:


# 雪球期权信息表
SBplot.plot_01(info)


# In[16]:


# 敲入敲出分布（完整周期）
# 统计风格：严格
# 无策略数据统计
df1, df2 = SBplot.plot_02(info)      # 必须接收df1才能进行print_03，接收df2才能plot_04


# In[17]:


# 完整观测周期胜率计算
SBplot.print_03(info, df1)


# In[18]:


# 敲入敲出分布（非完整周期）
SBplot.plot_04(info, df2)


# In[19]:


# 统计风格：传统
# 无策略数据统计
df1_raw, df2_raw = SBplot.plot_05(info)      # 必须接收df1_raw, df2_raw才能plot_06


# In[20]:


# 不追保结构的可视化
SBplot.plot_06(info, df1_raw, df2_raw)

