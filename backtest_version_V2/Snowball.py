# -*- coding: utf-8 -*-

"""
Created on Tue Dec 15 15:42:07 2020
Revised on Wed Oct 18 10:57:30 2023

@author: liuguixu 
Revised by: Fan Chen
Revised by: Junyi Wang on restructuring code

"""

"""多种雪球结构历史回测数据分析"""


from dateutil.relativedelta import relativedelta
from tools import *
from getData import *


class BaseSnowball(object):
    def __init__(
        self,
        snowball_type,
        underlying,
        time_fixed_param,
        knockin_param,
        knockout_param,
        coupon_param,
        profit_param,
    ):
        self.underlying = underlying  # 标的代码
        self.snowball_type = snowball_type  # 雪球类型
        self.time_fixed_param = time_fixed_param  # 敲入参数：包括敲入条件
        self.knockin_param = knockin_param  # 敲入参数：包括敲入条件
        self.knockout_param = knockout_param  # 敲出参数：包括首个敲出观察日，敲出条件，敲出观察频率，每月下调比例
        self.coupon_param = coupon_param  # 票息参数：包括敲出票息与红利票息
        self.profit_param = profit_param  # 不可追保则最大损失1 (即全部保证金)

        self.knockin_price = None  # 标的敲入价格
        self.knockout_price = None  # 标的敲出价格
        self.knockin_date = None  # 标的敲入日期
        self.knockout_date = None  # 标的敲出日期
        self.terminal_month = None  # 合约终止月份
        self.status = None  # 合约状态
        self.maturity_sign = True  # 到期指示(回测数据足够覆盖至到期，但是不意味着不提前敲出)

    def set_time_param(self, time_dynamic_param):
        self.time_dynamic_param = time_dynamic_param  # 日期参数：包括合约起始日期,合约长度与期权到期日

    def reset_state(self):
        """重设状态"""
        self.knockin_price = None
        self.knockout_price = None
        self.knockin_date = None
        self.knockout_date = None
        self.terminal_month = None
        self.status = None

    def process_backtest(self, index_data_all):
        """回测"""
        index_data_selected = self.get_index_data_selected(
            index_data_all
        )  # 该雪球产品回测用到的数据
        self.determine_knockin(index_data_selected)
        self.determine_knockout(index_data_selected)
        self.calculate_return()
        return None

    def get_index_data_selected(self, index_data_all):
        """选取回测区间内的标的数据"""
        date_range = [
            i
            for i in index_data_all.index
            if i >= self.time_dynamic_param["start_date"]
            and i <= self.time_dynamic_param["end_date"]
        ]
        index_data_selected = index_data_all.loc[date_range]
        return index_data_selected

    def determine_knockin(self, index_data_selected):
        """判断在回测区间内是否敲入，每日敲入观察，时间区间为：合约起始日期之后的第二天 至 到期日"""
        start_date = self.time_dynamic_param["start_date"]
        end_date = self.time_dynamic_param["end_date"]

        self.start_price = index_data_selected.loc[start_date, "close"]  # 起始日标的价格
        self.end_price = index_data_selected.loc[end_date, "close"]  # 结束日标的价格
        observation_period = [
            i
            for i in list(index_data_selected.index)
            if i > start_date and i <= end_date
        ]  # 回测区间

        for current_date in observation_period:
            current_price = index_data_selected.loc[current_date, "close"]
            if current_price <= round(
                self.start_price * self.knockin_param["knockin_barrier"], 2
            ):  # 发生敲入
                self.knockin_date = current_date
                self.knockin_price = current_price
                return None
        self.knockin_date = None
        self.knockin_price = None
        return None

    def determine_knockout(self, index_data_selected):
        """每月敲出观察"""
        for current_month in range(
            self.knockout_param["observation_start_month"],
            self.time_fixed_param["option_expire_month"] + 1,
        ):
            if_knockout = self.process_knockout_for_month(
                current_month, index_data_selected
            )
            if if_knockout:
                break
        return None

    def process_knockout_for_month(self, current_month, index_data_selected):
        """判断给定月份是否满足敲出条件"""
        current_date = self.time_dynamic_param["start_date"] + relativedelta(
            months=current_month * self.knockout_param["knockout_freq_month"]
        )
        current_date = ensure_trading_day(current_date)

        if current_date <= self.time_dynamic_param["end_date"]:
            current_price = index_data_selected.loc[current_date, "close"]  # 当前标的价格
            is_knockout = current_price >= round(
                self.start_price * self.knockout_param["knockout_barrier"], 2
            )  # 判断是否敲出
            is_valid_knockin = (
                self.knockin_date and self.knockin_date < current_date
            )  # 判断敲入是否发生在current_date之前

            if is_knockout and (self.knockin_date is None or is_valid_knockin):
                self.terminal_month = current_month
                self.knockout_price = current_price
                self.knockout_date = current_date
                return True
        return False

    def calculate_return(self):
        """计算不同敲入敲出情况下的收益"""
        if self.knockin_date == None and self.knockout_date == None:
            self.case_no_event()
        elif self.knockin_date != None and self.knockout_date == None:
            self.case_knockin_only()
        elif self.knockin_date == None and self.knockout_date != None:
            self.case_knockout_only()
        elif self.knockin_date != None and self.knockout_date != None:
            self.case_knockin_and_knockout()

    def case_no_event(self):
        self.status = "未敲入，未敲出"
        regular_coupon = self.coupon_param["regular_coupon"]
        self.abs_return = (
            regular_coupon * self.time_fixed_param["option_expire_month"] / 12
        )
        self.annual_return = regular_coupon
        return None

    def case_knockout_only(self):
        self.status = "未敲入，敲出"
        kickout_coupon = self.coupon_param["kickout_coupon"]
        self.abs_return = kickout_coupon * self.terminal_month / 12
        self.annual_return = kickout_coupon
        return None

    def case_knockin_only(self):
        self.status = "敲入，未敲出"
        start_price = self.start_price
        end_price = self.end_price
        self.abs_return = max(end_price / start_price - 1, -1)
        self.annual_return = (
            self.abs_return * 12 / self.time_fixed_param["option_expire_month"]
        )
        return None

    def case_knockin_and_knockout(self):
        """敲入且敲出"""
        self.status = "敲入，敲出"
        kickout_coupon = self.coupon_param["kickout_coupon"]
        self.abs_return = kickout_coupon * self.terminal_month / 12
        self.annual_return = kickout_coupon
        return None


class ClassicSnowball(BaseSnowball):
    """经典雪球"""

    def __init__(
        self,
        underlying,
        time_fixed_param,
        knockin_param,
        knockout_param,
        coupon_param,
        profit_param,
    ):
        super().__init__(
            "经典雪球",
            underlying,
            time_fixed_param,
            knockin_param,
            knockout_param,
            coupon_param,
            profit_param,
        )


class StepdownSnowball(BaseSnowball):
    """降敲型雪球"""

    def __init__(
        self,
        underlying,
        time_fixed_param,
        knockin_param,
        knockout_param,
        coupon_param,
        profit_param,
    ):
        """初始化"""
        super().__init__(
            "降敲型雪球",
            underlying,
            time_fixed_param,
            knockin_param,
            knockout_param,
            coupon_param,
            profit_param,
        )
        self.stepdown_ratio = float(
            input("请输入该降敲型雪球敲出条件每月下调比例:")
        )  # e.g. 输入 0.005 即每月下调 0.5%
        self.original_knockout_barrier = self.knockout_param["knockout_barrier"]

    def update_knockout_param(self, current_month):
        """每月更新敲出条件"""
        self.knockout_param["knockout_barrier"] = (
            self.original_knockout_barrier - current_month * self.stepdown_ratio
        )
        return None

    def determine_knockout(self, index_data_selected):
        """每月敲出观察"""
        for current_month in range(
            self.knockout_param["observation_start_month"],
            self.time_fixed_param["option_expire_month"] + 1,
        ):
            self.update_knockout_param(current_month)
            if_knockout = super(StepdownSnowball, self).process_knockout_for_month(
                current_month, index_data_selected
            )
            if if_knockout:
                break
        return None


class SnowballOption:
    @staticmethod
    def create_snowball(snowball_type, *args, **kwargs):
        if snowball_type == "经典雪球":
            return ClassicSnowball(*args, **kwargs)
        elif snowball_type == "降敲型雪球":
            return StepdownSnowball(*args, **kwargs)
        else:
            raise ValueError(f"Unknown snowball_type: {snowball_type}")
