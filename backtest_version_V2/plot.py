import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from Snowball import *

underlying_dict = {"上证50": "000016.SH"}
boolean_dict = {True: "是", False: "否"}


def plot_bactest_info(Snowball, backtest_start, backtest_end, output_path):

    plt.rcParams['font.sans-serif']=['SimHei']   # 用黑体显示中文
    plt.rcParams['axes.unicode_minus']=False     # 正常显示负号

    plt.style.use('fivethirtyeight')

    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111)

    underlying_name = Snowball.underlying
    underlying_code = underlying_dict[underlying_name]
        
    snowball_info = [ 
        ['指数名称', underlying_name], 
        ['指数代码', underlying_code], 
        ['雪球结构', Snowball.snowball_type], 
        ['约定年限（月）', Snowball.time_fixed_param["option_expire_month"]], 
        ['敲出锁定期（月）', Snowball.knockout_param["observation_start_month"]], 
        ['初始敲入水平', '%.1f%%'%(Snowball.coupon_param["regular_coupon"] * 100)],
        ['敲出水平', '%.1f%%'%(Snowball.knockout_param["knockout_barrier"] * 100)],
        ['敲入观察频率', '每日'],
        ['固定收益率（年化）', '%.2f%%'%(Snowball.coupon_param["kickout_coupon"] * 100)], 
        ['红利票息（年化）', '%.2f%%'%(Snowball.coupon_param["regular_coupon"] * 100)],
        ['是否允许追保', boolean_dict[Snowball.profit_param["margin_call"]]]
        ]

    if Snowball.snowball_type == "降敲型雪球":
        snowball_info.insert(7, ['降敲水平', '%.1f%%'%(Snowball.stepdown_ratio * 100)])
    elif Snowball.snowball_type == "限亏型雪球":
        snowball_info.insert(7, ['保护比例', '%.1f%%'%(Snowball.protect_ratio * 100)])    
    elif Snowball.snowball_type == "限亏止盈型雪球":
        snowball_info.insert(7, ['保护比例', '%.1f%%'%(Snowball.protect_ratio * 100)])    

    bg_color = []   
    for i in range(len(snowball_info)):
        bg_color.append(['w',sns.color_palette("Blues")[0]])
        
    title = ax.table(cellText=[['雪球期权信息表（回测周期：%s至%s)'%(backtest_start, backtest_end)]],loc='top', cellLoc ='center')
    title.scale(1,2.5)

    t = ax.table(cellText= snowball_info,loc='top',cellLoc='center', cellColours = bg_color, bbox=[0, 0, 1, 1])    
    t.auto_set_font_size(False)
    t.set_fontsize(13)

    ax.axis('off')
    ax.set_frame_on(False)
    plt.savefig(output_path + f"/{Snowball.snowball_type}-info.png")
    plt.close()
    return None
        