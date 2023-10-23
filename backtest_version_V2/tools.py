import pandas as pd
from getData import *

trading_datelist = get_trading_datelist()


def ensure_trading_day(current_date):
    """
    Args:
        current_date (datetime): date
    Returns:
        datetime: current or next trading day
    """
    if type(current_date) == str:
        current_date = pd.to_datetime(current_date).date()

    if current_date in trading_datelist:
        return current_date
    else:
        next_date = next(date for date in trading_datelist if date > current_date)
        return next_date
    



