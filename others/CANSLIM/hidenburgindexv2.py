# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib as mpl
# import akshare as ak
# from dateutil import relativedelta
# from WindPy import *
# w.start()
# import datetime
# plt.rcParams["font.sans-serif"]=["SimHei"] #设置字体
# mpl.rcParams['axes.unicode_minus']=False
# import warnings
# warnings.filterwarnings('ignore')
# import sys
# # 加载当前路径
# sys.path.append('.')

# ##################### 读取股票数据 ####################
# data = pd.read_csv('./data/A股行情数据.csv', index_col = (0), dtype={'代码': str, '年月': str}, usecols = [0, 1, 4, 5, 7, 12])
# data['年月'] = data['日期'].apply(lambda x: x[:-3].replace('-', ''))
# value = data.groupby(['代码', '年月'])[['成交额']].mean()
# high = data.groupby(['代码', '年月'])[['最高']].max()
# low = data.groupby(['代码', '年月'])[['最低']].min()
# data = high.join(low)
# highest = data['最高'].groupby('代码').rolling(12, min_periods=1).max()
# lowest = data['最低'].groupby('代码').rolling(12, min_periods=1).min()
# data = data.reset_index()
# data['12月最高'] = highest.values
# data['12月最低'] = lowest.values

# ################## 获得每一天对应的样本股数据 ######################
# # Wind 下载数据
# # pool_information = pd.read_excel('./data/000905.SH-成分进出记录-20230720.xlsx').sort_values('日期', ignore_index = 1)
# # 调用 Wind 接口

# index_list = "801010.SI,801030.SI,801040.SI,801050.SI,801080.SI,801110.SI,801120.SI,801130.SI,801140.SI,801150.SI,801160.SI,801170.SI,801180.SI,801200.SI,801210.SI,801230.SI,801710.SI,801720.SI,801730.SI,801740.SI,801750.SI,801760.SI,801770.SI,801780.SI,801790.SI,801880.SI,801890.SI,801950.SI,801960.SI,801970.SI,801980.SI".split(',')
# index_name = w.wss("801010.SI,801030.SI,801040.SI,801050.SI,801080.SI,801110.SI,801120.SI,801130.SI,801140.SI,801150.SI,801160.SI,801170.SI,801180.SI,801200.SI,801210.SI,801230.SI,801710.SI,801720.SI,801730.SI,801740.SI,801750.SI,801760.SI,801770.SI,801780.SI,801790.SI,801880.SI,801890.SI,801950.SI,801960.SI,801970.SI,801980.SI", "sec_name", "", usedf=True)[1]

# # index_list = "CI005001.WI,CI005002.WI,CI005003.WI,CI005004.WI,CI005005.WI,CI005006.WI,CI005007.WI,CI005008.WI,CI005009.WI,CI005010.WI,CI005011.WI,CI005012.WI,CI005013.WI,CI005014.WI,CI005015.WI,CI005016.WI,CI005017.WI,CI005018.WI,CI005019.WI,CI005020.WI,CI005021.WI,CI005022.WI,CI005023.WI,CI005024.WI,CI005025.WI,CI005026.WI,CI005027.WI,CI005028.WI,CI005029.WI,CI005030.WI".split(',')
# # index_name = w.wss("CI005001.WI,CI005002.WI,CI005003.WI,CI005004.WI,CI005005.WI,CI005006.WI,CI005007.WI,CI005008.WI,CI005009.WI,CI005010.WI,CI005011.WI,CI005012.WI,CI005013.WI,CI005014.WI,CI005015.WI,CI005016.WI,CI005017.WI,CI005018.WI,CI005019.WI,CI005020.WI,CI005021.WI,CI005022.WI,CI005023.WI,CI005024.WI,CI005025.WI,CI005026.WI,CI005027.WI,CI005028.WI,CI005029.WI,CI005030.WI", "sec_name", "", usedf=True)[1]
# # index_time = w.wss("CI005001.WI,CI005002.WI,CI005003.WI,CI005004.WI,CI005005.WI,CI005006.WI,CI005007.WI,CI005008.WI,CI005009.WI,CI005010.WI,CI005011.WI,CI005012.WI,CI005013.WI,CI005014.WI,CI005015.WI,CI005016.WI,CI005017.WI,CI005018.WI,CI005019.WI,CI005020.WI,CI005021.WI,CI005022.WI,CI005023.WI,CI005024.WI,CI005025.WI,CI005026.WI,CI005027.WI,CI005028.WI,CI005029.WI,CI005030.WI", "ipo_date", "", usedf=True)[1]
# for index_code in index_list:
#     pool_information = w.wset("indexhistory", "startdate=1900-06-01;enddate=2023-07-31;windcode=" + index_code + ";field=tradeDate,tradeCode,tradeName,tradeStatus", usedf=True)[1]
#     pool_information.columns = ['日期', '代码', '简称', '纳入/剔除']
#     pool_information = pool_information.sort_values('日期', ignore_index = 1)
#     code_list = sorted(list(set(pool_information['代码'].str.slice(stop=-3))))
#     # 适应 Akshare 数据库 
#     pool_information['代码'] = pool_information['代码'].str.slice(stop=-3)

#     pool_in_information = pool_information[pool_information['纳入/剔除'] == '纳入']
#     pool_out_information = pool_information[pool_information['纳入/剔除'] == '剔除']

#     add_in = dict()
#     move_out = dict()

#     for name, group in pool_in_information.groupby('日期')['代码']:
#         add_in[name] = set(group)

#     for name, group in pool_out_information.groupby('日期')['代码']:
#         move_out[name] = set(group)

#     t = list(add_in.keys()) + list(move_out.keys())
#     t = sorted(list(set(t)))
#     population_pool = {t[0]: list(add_in[t[0]])}
#     flag = 0
#     for i in range(1, len(t)):
#         if (t[i] in add_in) & (t[i] in move_out):
#             population_pool[t[i]] = list((set(population_pool[t[i - 1]]) | add_in[t[i]]) - move_out[t[i]])
#         elif t[i] in add_in:
#             population_pool[t[i]] = list(set(population_pool[t[i - 1]]) | add_in[t[i]])
#         elif t[i] in move_out:
#             population_pool[t[i]] = list(set(population_pool[t[i - 1]]) - move_out[t[i]])
#         if (flag == 0) & (len(population_pool[t[i]]) > 10):
#             # flag = max(t[i].strftime('%Y-%m-%d'), str(index_time.loc[index_code].values[0]), '2010-01-01')
#             flag = max(t[i].strftime('%Y-%m-%d'), '2010-01-01')

#     # 如果没有更新到今天
#     if datetime.date.today().strftime('%Y-%m-%d') != t[-1]:
#         # 给今天赋予一个空值，后期填补至今天
#         population_pool[datetime.date.today().strftime('%Y-%m-%d')] = np.nan

#     population_pool_series = pd.Series(population_pool)
#     population_pool_series.index = pd.DatetimeIndex(population_pool_series.index)

#     # 获得每月最后一个交易日的信息
#     last_trade_date = w.tdays(flag, "2023-07-31", "Period=M", usedf=0).Data[0]
#     idx = population_pool_series.index
#     idx = idx.append(pd.DatetimeIndex(last_trade_date))
#     idx = idx.drop_duplicates()
#     population_pool_series = population_pool_series.reindex(idx)
#     population_pool_series = population_pool_series.sort_index()
#     # 更改日期，填补空值
#     population_pool_series = population_pool_series.ffill()

#     trade_month = [t.strftime('%Y%m') for t in last_trade_date]
#     HindenburgIndex = pd.Series()
#     for i in range(len(last_trade_date)):
#         value_month = value.loc[population_pool_series[last_trade_date[i]]].query('年月 == "' +  trade_month[i]  +  '"')
#         value_rank = value_month.rank(pct = True)
#         # 处于行业前 30%
#         fliter = value_rank[value_rank >= 0.7].dropna()
#         # 样本池子
#         sample_pool = fliter.index.droplevel(1)
        
#         # sample_year_data = data[(data['代码'].isin(sample_pool)) & (data['年月'] == trade_month[i])]
        
#         sample_month_data = data[(data['代码'].isin(sample_pool)) & (data['年月'] == trade_month[i])]

#         sign1 = sample_month_data['最低'].values == sample_month_data['12月最低'].values
#         NewLowNum = np.sum(sign1)
#         # 可以对计算 max 的数据再次切片，剔除已经是 min 的标的
#         sign2 = sample_month_data['最高'].values == sample_month_data['12月最高'].values
#         NewHighNum = np.sum(sign2) - np.sum(sign1 & sign2)
        
#         HindenburgIndex[last_trade_date[i]] = (NewHighNum - NewLowNum) / len(sample_pool)
#         print(i)

#     # mkt = w.wsd(index_code, "close", flag, "2023-07-31", "Period=M;Fill=Previous", usedf=True)[1]
#     # ax = HindenburgIndex.plot(figsize = (15, 7), color = 'silver')
#     # ax1 = ax.twinx() 
#     # mkt.plot(ax = ax1)
#     # plt.legend(index_name.loc[index_code])

#     mkt = w.wsd(index_code, "close", flag, "2023-07-31", "Period=M;Fill=Previous", usedf=True)[1]
#     fig, ax = plt.subplots(figsize = (15, 7))
#     ax.fill_between(HindenburgIndex.index, 0, HindenburgIndex.values, facecolor = 'silver')
#     ax1 = ax.twinx() 
#     mkt.plot(ax = ax1)
#     ax.grid(axis = 'y', linestyle='--')
#     plt.legend(index_name.loc[index_code])

#     plt.savefig('./output/'+ str(index_name.loc[index_code].values[0]) + '.pdf')
#     plt.close()