import pandas as pd
import efinance as ef
import akshare as ak
from datetime import datetime

underlying_dict = {"上证50": "000016.SH"}


def fetching_data(underlying, index_data_source='wind',show_data_info=False):
    if index_data_source == 'wind_file':
        index_data = pd.read_excel('./data/%s.xlsx'%(underlying))
        index_data = index_data.loc[:,['日期','收盘价(元)']]
        index_data['收盘价(元)'] = index_data['收盘价(元)'].round(2)
        correct_time_type = type(pd.to_datetime('1970-01-01 08:00:00')) # 正常的日历类型应该为correct_time_type
        if_correct_time_type = [type(index_data.loc[i,'日期'])==correct_time_type for i in range(index_data.shape[0])] # 记录bool组
        print('[Message from function: fetching_data] 即将清除无效日期数据————总共清除%d组'%(if_correct_time_type.count(False)))
        index_data = index_data[if_correct_time_type] # mask运算，只保留True的位置
        index_data.set_index('日期',drop=True,inplace=True)
    
    elif index_data_source == 'efinance':
        index_data = ef.stock.get_quote_history(underlying)
        index_data = index_data.loc[:,['日期','收盘']]
        index_data.set_index('日期',drop=True,inplace=True)
    
    elif index_data_source == 'akshare':
        index_data = ak.fund_etf_hist_sina(symbol=underlying) 
        index_data = index_data.loc[:,['date','close']]
        index_data.set_index('date',drop=True,inplace=True)
        
    if show_data_info:
        print(index_data)
        
    return index_data


def get_underlying_data(underlying, start_date, end_date, data_source="wind"):
    '''underlying暂时为单个数据源，date为datetime格式'''
    if type(underlying) == str:
        if data_source == "wind":
            import WindPy
            WindPy.w.start()
            index_data = WindPy.w.wsd(underlying_dict[underlying], 'CLOSE', start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d'), "Fill=Previous", usedf=True)[1].dropna()
            # index_data.index = index_data.index.map(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
            index_data.columns = ['close']
            return index_data 
        elif data_source == "efinance":
            index_data = ef.stock.get_quote_history(stock_codes = underlying, beg=start_date.strftime('%Y%m%d'), end=end_date.strftime('%Y%m%d'))
            index_data = index_data.loc[:, ['日期','收盘']]
            index_data.columns = ['date', 'close']
            index_data = index_data.set_index('date', drop=True)
            index_data.index = index_data.index.map(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
            return index_data
        
    elif type(underlying) == list:
        print("标的列表--待开发")
        return None


def get_trading_datelist():
    underlying = "上证50"
    index_data_source = "efinance"
    index_data = fetching_data(underlying, index_data_source,show_data_info=False)
    trading_datelist = [pd.to_datetime(x).date() for x in index_data.index]
    return trading_datelist