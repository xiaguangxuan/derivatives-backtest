import pandas as pd
from datetime import datetime

import efinance as ef
import WindPy
WindPy.w.start()

underlying_dict = {
    "上证50": "000016.SH",
    "沪深300": "000300.SH",
    "中证500": "000905.SH",
    "中证1000": "000852.SH",
}

root_path = "D:/10-国君/GTJA-intern-codes"


def get_underlying_data(underlying, start_date, end_date, data_source="wind"):
    """
    Args:
        underlying (str): underlying name
        start_date (datetime): start date
        end_date (datetime): end date
        data_source (str, optional): index data source. Defaults to "wind".
    Returns:
        df: underlying index price data
    """
    if type(underlying) == str:
        if data_source == "wind":
            index_data = WindPy.w.wsd(
                underlying_dict[underlying],
                "CLOSE",
                start_date.strftime("%Y%m%d"),
                end_date.strftime("%Y%m%d"),
                "Fill=Previous",
                usedf=True,
            )[1].dropna()
            index_data.columns = ["close"]
            return index_data
        elif data_source == "efinance":
            index_data = ef.stock.get_quote_history(
                stock_codes=underlying,
                beg=start_date.strftime("%Y%m%d"),
                end=end_date.strftime("%Y%m%d"),
            )
            index_data = index_data.loc[:, ["日期", "收盘"]]
            index_data.columns = ["date", "close"]
            index_data = index_data.set_index("date", drop=True)
            index_data.index = index_data.index.map(
                lambda x: datetime.strptime(x, "%Y-%m-%d").date()
            )
            return index_data
        
    elif type(underlying) == list:
        print("标的列表--待开发")
        return None


def get_trading_datelist():
    trading_date_df = pd.read_csv(f"{root_path}/backtest_version_V2/basic_data/trading_datelist.csv", index_col=0)
    trading_date_df["date"] = trading_date_df["date"].apply(lambda x: pd.to_datetime(x).date())
    trading_datelist = list(trading_date_df["date"])
    return trading_datelist


def update_trading_datelist():
    trading_datelist = WindPy.w.tdays("20100101", "20241231").Data[0]
    trading_date_df = pd.DataFrame(trading_datelist)
    trading_date_df.columns = ["date"]
    trading_date_df.to_csv(f"{root_path}/backtest_version_V2/basic_data/trading_datelist.csv")
    return None


if __name__ == "__main__":
    update_trading_datelist()
