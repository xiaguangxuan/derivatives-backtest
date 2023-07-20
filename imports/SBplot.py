import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_01(info):
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False # 用来正常显示负号
    plt.rcParams['savefig.dpi'] = 300
    plt.style.use('fivethirtyeight')

    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111)

    underlying_name = info.underlying_name
    underlying = info.underlying_code

    bg_color = []


    if info.snowball_type in ['锁盈止损雪球','小雪球']:
        ki_ob_param_displayed = None
        ki_param_displayed = None
        margin_call_param_displayed = ['是否允许追保', '不需要']
    else:
        ki_ob_param_displayed = ['敲入观察频率', '每日']
        ki_param_displayed = ['初始敲入水平', str(info.Ki_bc * 100)+'%']
        margin_call_param_displayed = ['是否允许追保', info.margin_call]

        
    snowball_info = [ ['指数名称', underlying_name], ['指数代码',underlying], ['雪球结构', info.snowball_type], ['约定年限（月）', info.Option_expire_month], 
                        ['敲出锁定期（月）', info.Ko_forward_month],ki_param_displayed, ['敲出水平', str(info.begin_Ko_bc * 100)+'%'],
                        ki_ob_param_displayed, ['敲出观察频率','每月指定日'], 
                        ['固定收益率（年化）', '%.2f%%'%(info.Coupon * 100)], ['红利票息（年化）', '%.2f%%'%(info.Coupon_1 * 100)],
                    margin_call_param_displayed
                    ]

    while None in snowball_info:
        snowball_info.remove(None)

    if info.snowball_type == '早利雪球': 
        snowball_info = snowball_info + [['后段收益率（年化）', '%.2f%%'%(info.Coupon_adjusted_param['coupon_adjusted'] * 100)]]
        snowball_info = snowball_info + [['前段收益率月数（月）', '%d'%(info.Coupon_adjusted_param['month_to_adjust_coupon'] )]]

    if info.margin_call == True and info.snowball_type in ['锁盈止损雪球','小雪球']:
        if info.snowball_type == '小雪球':
            snowball_info = snowball_info + [['最大亏损幅度（年化）', '%.2f%%'%(info.Coupon_option * 100)]]
        elif info.snowball_type == '锁盈止损雪球':
            snowball_info = snowball_info + [['最大亏损幅度', '%.2f%%'%(info.maximum_lose * 100)]]


    if info.snowball_type in ['小雪球']:
        snowball_info = snowball_info + [['期权费率', '%.2f%%'%(info.Coupon_option * 100)]]
        
    if info.step_ratio != 0:
        snowball_info.insert(7, ['降敲水平', info.step_ratio])
        
    for auxiliary_indicator in info.auxiliary_indicators:
        snowball_info.append(['筛选条件：'+auxiliary_indicator, info.auxiliary_indicators_range[auxiliary_indicator]])
        
    for i in range(len(snowball_info)):
        bg_color.append(['w',sns.color_palette("Blues")[0]])
        
    title = ax.table(cellText=[['雪球期权信息表（回测周期：%s至%s)'%(info.Ob_ini,info.Ob_end)]],
                        loc='top', cellLoc ='center'
                        )
    title.scale(1,2.5)

    t = ax.table(cellText= snowball_info,loc='top',cellLoc='center', cellColours = bg_color, bbox=[0, 0, 1, 1])    
    t.auto_set_font_size(False)
    t.set_fontsize(13)

    ax.axis('off')
    ax.set_frame_on(False)
    plt.savefig('output/fig1.png')
    # plt.show()
        

def sort_occ_freq_earning(df, cal_earnings=False, margin_call = True):
    occurances_set = []
    avg_earnings_set = []
    
    if margin_call:
        states_set = ['不敲入，敲出','敲入，敲出','不敲入，不敲出','敲入，不敲出']
        for state in states_set:
            ocr_times = df[df['敲入敲出状态'] == state].shape[0]

            if cal_earnings:
                avg = '%.2f'%(round(df[df['敲入敲出状态']==state]['年化收益率'].mean(),4) * 100)  if ocr_times != 0 else '0.00'
                avg_earnings_set.append(avg)

            occurances_set.append(ocr_times)
        if sum(occurances_set) != 0:     
            freqs_set = ['%.2f'%(round((occurances_set[i]/sum(occurances_set)),4) * 100) for i in range(len(occurances_set))]
        else:
            freqs_set = [0] * len(occurances_set)
    else:
        states_set = [['不敲入，敲出'],['不敲入，不敲出'],['敲入，敲出','敲入，不敲出']]
        for state_list in states_set:
            ocr_times = df[df['敲入敲出状态'].isin(state_list)].shape[0]

            if cal_earnings:
                avg = '%.2f'%(round(df[df['敲入敲出状态'].isin(state_list)]['年化收益率'].mean(),4) * 100)  if ocr_times != 0 else '0.00'
                avg_earnings_set.append(avg)

            occurances_set.append(ocr_times)
        if sum(occurances_set) != 0:  
            freqs_set = ['%.2f'%(round((occurances_set[i]/sum(occurances_set)),4) * 100) for i in range(len(occurances_set))]
        else:
            freqs_set = [0] * len(occurances_set)
        
    return (occurances_set, freqs_set,avg_earnings_set) if cal_earnings else (occurances_set, freqs_set)


def sort_occ_freq_by_ko_month(df, df1, margin_call = True):
    states_set = [(1,4),(5,12),(13,24)]
    occurances_set = []
    states_text_set = []
    
    for state in states_set:
        occurances_set.append(df[(df['敲出所需时间（月度）']<= state[1]) & (df['敲出所需时间（月度）']>= state[0]) ].shape[0])
        states_text_set.append('敲出（月）在%d至%d之间'%(state[0],state[1]))
    
    if margin_call == False:
        states_text_set = states_text_set + ['未完全亏损，不敲出'] 
        occurances_set = occurances_set + [df1[df1['敲入敲出状态']=='不敲入，不敲出'].shape[0]]

        states_text_set = states_text_set + ['完全亏损'] 
        occurances_set = occurances_set + [df1[df1['敲入敲出状态']=='敲入，不敲出'].shape[0]]
        
    else: 
        states_text_set = states_text_set + ['不敲入，不敲出'] 
        occurances_set = occurances_set + [df1[df1['敲入敲出状态']=='不敲入，不敲出'].shape[0]]

        states_text_set = states_text_set + ['亏损'] 
        occurances_set = occurances_set + [df1[df1['敲入敲出状态']=='敲入，不敲出'].shape[0]]
        
    freqs_set = ['%.2f'%(round((occurances_set[i]/sum(occurances_set)),4) * 100) for i in range(len(occurances_set))]
    
    return states_text_set, occurances_set, freqs_set


def delete_zero_occ(states_set, occurances_set):
    states_set_pie = [] # states_set.copy()
    occurances_set_pie = [] # occurances_set.copy()
    for i, v in enumerate(occurances_set):
        if v != 0:
            states_set_pie.append(states_set[i])
            occurances_set_pie.append(occurances_set[i])
    return states_set_pie, occurances_set_pie


def plot_02(info):
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False # 用来正常显示负号

    plt.style.use('fivethirtyeight')
    states_set = ['不敲入，敲出','敲入，敲出','不敲入，不敲出','敲入，不敲出']
    occurances_set_benchmark = []
    avg_earning_set_benchmark = []

    df1 = info.df[info.df['完成周期'] == 1]
    df2 = info.df[info.df['完成周期'] == 0]

    df1_raw = info.df_raw[info.df_raw['完成周期'] == 1]

    for state in states_set:
        occurances_set_benchmark.append(df1_raw[df1_raw['敲入敲出状态']==state].shape[0])
        avg_earning_set_benchmark.append('%.2f'%(round(df1_raw[df1_raw['敲入敲出状态']==state]['年化收益率'].mean(),4) * 100))

    avg_earning_set_benchmark = np.array(avg_earning_set_benchmark)
    avg_earning_set_benchmark[avg_earning_set_benchmark =='nan'] = '%.2f'%(0)
    states_set = ['不敲入，敲出','敲入，敲出','不敲入，不敲出','敲入，不敲出']

    occurances_set_benchmark, freqs_set_benchmark, avg_earnings_set_benchmark =  sort_occ_freq_earning(
        df1_raw,cal_earnings=True)
    occurances_set, freqs_set, avg_earnings_set = sort_occ_freq_earning(
        df1,cal_earnings=True)
        
    ref_100p = ' (100.00) ' if info.auxiliary_indicators != [] else ''


    if info.auxiliary_indicators != [] :
        freqs_set = [str(freqs_set[i]) + ' (%s) '%freqs_set_benchmark[i] for i in range(len(occurances_set))]
        avg_earnings_set = [avg_earnings_set[i] + ' (%s) '%avg_earnings_set_benchmark[i] for i in range(len(occurances_set))]


    fig = plt.figure(figsize=(12,10))
    ax1 = fig.add_subplot(121)

    states_set_pie, occurances_set_pie = delete_zero_occ(states_set, occurances_set)

    ax1.pie(occurances_set_pie, colors = sns.color_palette("Blues"), labels=states_set_pie, autopct='%2.2f%%',        labeldistance = 1.1,
            pctdistance = 0.85, # 数值标签相对圆心的距离位置
    #         shadow = True, # 添加阴影
            radius = 1,  # 饼图的相对半径
            startangle = 90,  # 绘图的起始角度
            counterclock = False,
            textprops={'fontsize': 10}
        )  # 时针方向 )

    for i in range(4):
        ax1.text(0, 0.2-0.15*i, '%s: %d 例'%(states_set[i],occurances_set[i]), ha='center', fontsize=10)


    table_data = list(zip(*([states_set]+[occurances_set]+[freqs_set] + [list(avg_earnings_set)])))
    table_data.insert(0,['状态','次数','概率（%）','平均收益率（年化，%）'])

    ref_return = ' (%.2f) '%(round(df1_raw['年化收益率'].mean(),4) * 100) if info.auxiliary_indicators != [] else ''

    table_data.insert(6,['总计',sum(occurances_set),'100.00' + ref_100p,'%.2f'%(round(df1['年化收益率'].mean(),4) * 100)+ ref_return])


    t1 = ax1.table(cellText= table_data,colWidths=[0.16,0.1,0.18,0.24],loc='bottom')    
    t1.auto_set_font_size(False)
    t1.set_fontsize(10)
    t1.scale(1.8,2.5)

    states_set = [(1,4),(5,12),(13,24)]

    states_text_set, occurances_set_benchmark, freqs_set_benchmark = sort_occ_freq_by_ko_month(df1_raw, df1)
    _, occurances_set, freqs_set = sort_occ_freq_by_ko_month(df1, df1)

    if info.auxiliary_indicators != [] :
        freqs_set = [str(freqs_set[i]) + ' (%s) '%freqs_set_benchmark[i] for i in range(len(occurances_set))]    

    ax2 = fig.add_subplot(122)

    states_text_set_pie, occurances_set_pie = delete_zero_occ(states_text_set, occurances_set)
    ax2.pie(occurances_set_pie, colors = sns.color_palette("Blues"), labels=states_text_set_pie, autopct='%2.2f%%',        labeldistance = 1.1,
            pctdistance = 0.85, # 数值标签相对圆心的距离位置
    #         shadow = True, # 添加阴影
            radius = 1,  # 饼图的相对半径
            startangle = 90,  # 绘图的起始角度
            counterclock = False,
            textprops={'fontsize': 10}
        )  # 时针方向 )


    table_data = list(zip(*([states_text_set]+[occurances_set]+[freqs_set])))
    table_data.insert(0,['状态','次数','概率（%）'])

    table_data.insert(6,['总计',sum(occurances_set),'100.00'+ref_100p]) 

    t2 = ax2.table(cellText= table_data,colWidths=[0.24,0.1,0.17],loc='bottom')    
    t2.auto_set_font_size(False)
    t2.set_fontsize(10)
    t2.scale(1.8,2.5)

    circle1 = plt.Circle((0,0), 0.7, color='white')
    circle2 = plt.Circle((0,0), 0.7, color='white')

    ax1.add_patch(circle1)
    ax2.add_patch(circle2)

    # Add data values to pie chart
    for i in range(5):
        ax2.text(0, 0.2-0.15*i, '%s: %d 例'%(states_text_set[i],occurances_set[i]), ha='center', fontsize=10)

    if info.auxiliary_indicators != []:
        ax1.text(-1.4, -2.3, '注：1. 括号内发生概率为无筛选策略时发生的概率，作为参考；\n    2. 完整周期意即当前数据足以覆盖雪球期权约定期限，否则归为非完整周期类。', ha='left', fontsize=12)

    ax1.set_title('敲入敲出分布（完整周期）')
    ax2.set_title('敲出时间分布（完整周期）')

    plt.tight_layout()
    plt.savefig('output/fig2.png')
   # plt.show()
    return df1, df2


def print_03(info, df1):
    # 完整观测周期胜率计算
    tests_amount = df1.shape[0]
    win_ratio = df1['得到高票息'].mean()

    # 敲出
    ko_ratio = df1['敲出'].mean()

    # nko_nki
    nko_nki_ratio = (df1['敲入敲出状态']== '不敲入，不敲出').sum() / tests_amount

    ko_mean = df1['敲出所需时间（月度）'].mean()

    # 结果显示统计

    # 计算胜率
    win_ratio = df1['得到高票息'].mean()

    # 亏损概率
    lose_ratio = (df1['敲入敲出状态']=='敲入，不敲出').mean() 

    # OTM 不赚不亏
    # df = df[(df['敲入敲出状态']=='ki_nko') & (df['终止指数']>=(df['初始指数']*Ki_bc))]
    # OTM_no_pay_ratio = len(df1)/len(df)

    print('回测时间为{}至{}'.format(info.Ob_ini.strftime('%Y-%m-%d'),info.Ob_end.strftime('%Y-%m-%d')))
    print('完整周期的雪球，发行时间为{}至{}'.format(df1.index[0],df1.index[-1]))
    print('这些雪球的盈利概率为 {0:.2%}，敲出概率为 {1:.2%}，亏损概率为 {2:.2%}'.format(win_ratio,ko_ratio,lose_ratio))
    print('平均敲出所需时间为 %.2f 月'%(ko_mean))

    # print('若为普通雪球，PB<{0:.2}的胜率为{1:.2%}，亏PB>={2:.2}的胜率为{3:.2%}'.format(PB_barrier,small_PB_win_ratio,PB_barrier,large_PB_win_ratio))
    # print('若为OTM雪球，该雪球的盈利概率为{0:.2%}，收益为0概率为{1:.2%}，亏损概率为{2:.2%}'.format(win_ratio,OTM_no_pay_ratio,1-OTM_no_pay_ratio-win_ratio))


def plot_04(info, df2):
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False # 用来正常显示负号
    plt.style.use('fivethirtyeight')

    states_set = ['不敲入，敲出','敲入，敲出','不敲入，不敲出','敲入，不敲出']
    occurances_set = []

    for state in states_set:
        occurances_set.append(df2[df2['敲入敲出状态']==state].shape[0])
        
    if sum(occurances_set) != 0:
        fig = plt.figure(figsize=(8,8))
        ax = fig.add_subplot(121)
        states_set_pie, occurances_set_pie = delete_zero_occ(states_set, occurances_set)
        
        ax.pie(occurances_set_pie, colors = sns.color_palette("Blues"), labels=states_set_pie, autopct='%2.2f%%',        labeldistance = 1.1,
                pctdistance = 0.85, # 数值标签相对圆心的距离位置
        #         shadow = True, # 添加阴影
                radius = 1,  # 饼图的相对半径
                startangle = 90,  # 绘图的起始角度
                counterclock = False,
                textprops={'fontsize': 10}
            )  # 时针方向 )

        circle = plt.Circle((0,0), 0.7, color='white')
        fig = plt.gcf()
        fig.gca().add_artist(circle)

        # Add data values to pie chart
        for i in range(4):
            ax.text(0, 0.2-0.15*i, '%s: %d 例'%(states_set[i],occurances_set[i]), ha='center', fontsize=10)

        freq_data = ['%.2f'%(round((occurances_set[i]/sum(occurances_set)),4) * 100) for i in range(len(occurances_set))]
        table_data = list(zip(*([states_set]+[occurances_set]+[freq_data])))
        table_data.insert(0,['状态','次数','概率（%）'])
        table_data.insert(6,['总计',sum(occurances_set),'100.00'])

        t2 = ax.table(cellText= table_data,colWidths=[0.15,0.1,0.12],loc='bottom')    
        t2.auto_set_font_size(False)
        t2.set_fontsize(10)
        t2.scale(2.6,2.5)

        plt.title('敲入敲出分布（非完整周期）')
        plt.tight_layout()
        plt.savefig('output/fig3.png')
        # plt.show()

        print('非完整周期的雪球，发行时间为{}至{}'.format(df2.index[0],df2.index[-1]))

    else:
        print('没有非完整周期的雪球，无结果输出！')


def plot_05(info):
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False # 用来正常显示负号
    plt.style.use('fivethirtyeight')

    states_set = ['不敲入，敲出','敲入，敲出','不敲入，不敲出','敲入，不敲出']
    occurances_set_benchmark = []
    avg_earning_set_benchmark = []

    mask = (info.df_raw['完成周期'] == 1 )|(info.df_raw['敲入敲出状态'].isin(['敲入，敲出','不敲入，敲出']))
    df1_raw = info.df_raw[mask]
    df2_raw = info.df_raw[~mask]

    for state in states_set:
        occurances_set_benchmark.append(info.df_raw[info.df_raw['敲入敲出状态']==state].shape[0])
        avg_earning_set_benchmark.append('%.2f'%(round(info.df_raw[info.df_raw['敲入敲出状态']==state]['年化收益率'].mean(),4) * 100))

    avg_earning_set_benchmark = np.array(avg_earning_set_benchmark)
    avg_earning_set_benchmark[avg_earning_set_benchmark =='nan'] = '%.2f'%(0)
    ref_100p = ' (100.00) ' if info.auxiliary_indicators != [] else ''
    states_set = ['敲出','敲出','不敲出','不敲出',]if info.snowball_type in ['锁盈止损雪球','小雪球'] else ['不敲入，敲出','敲入，敲出','不敲入，不敲出','敲入，不敲出',] 

    mask = (info.df['完成周期'] == 1 )|(info.df['敲入敲出状态'].isin(['敲入，敲出','不敲入，敲出']))
    df1 = info.df[mask]
    df2 = info.df[~mask]
        
    if df1.shape[0] != 0:
        
        occurances_set_benchmark, freqs_set_benchmark, avg_earnings_set_benchmark =  sort_occ_freq_earning(
            df1_raw,cal_earnings=True)
        occurances_set, freqs_set, avg_earnings_set = sort_occ_freq_earning(
            df1,cal_earnings=True)
        
        if info.auxiliary_indicators != [] :
            freqs_set = [freqs_set[i] + ' (%s) '%freqs_set_benchmark[i] for i in range(len(occurances_set))]
            avg_earnings_set = [avg_earnings_set[i] + ' (%s) '%avg_earnings_set_benchmark[i] for i in range(len(occurances_set))]


        fig = plt.figure(figsize=(12,10))
        ax1 = fig.add_subplot(121)
        
        states_set_pie, occurances_set_pie = delete_zero_occ(states_set, occurances_set)

        ax1.pie(occurances_set_pie, colors = sns.color_palette("Blues"), labels=states_set_pie, autopct='%2.2f%%',        labeldistance = 1.1,
                pctdistance = 0.85, # 数值标签相对圆心的距离位置
        #         shadow = True, # 添加阴影
                radius = 1,  # 饼图的相对半径
                startangle = 90,  # 绘图的起始角度
                counterclock = False,
                textprops={'fontsize': 10}
            )  # 时针方向 )

        for i in range(4):
            if occurances_set[i] == 0 and info.snowball_type in ['锁盈止损雪球','小雪球']:
                continue
            ax1.text(0, 0.2-0.15*i, '%s: %d 例'%(states_set[i],occurances_set[i]), ha='center', fontsize=10)
                

        table_data = list(zip(*([states_set]+[occurances_set]+[freqs_set] + [list(avg_earnings_set)])))
        table_data.insert(0,['状态','次数','概率（%）','平均收益率（年化，%）'])

        ref_return = ' (%.2f) '%(round(df1_raw['年化收益率'].mean(),4) * 100) if info.auxiliary_indicators != [] else ''
        
        table_data.insert(1,['已完结合约总计',sum(occurances_set),'100.00' + ref_100p,'%.2f'%(round(df1['年化收益率'].mean(),4) * 100)+ ref_return])
        
        table_data = table_data[:2]+[table_data[3]]+ [table_data[5]] if info.snowball_type in ['锁盈止损雪球','小雪球'] else    table_data          
        
        occurances_set_benchmark, freqs_set_benchmark, avg_earnings_set_benchmark =  sort_occ_freq_earning(
            df2_raw,cal_earnings=True)
        occurances_set, freqs_set, avg_earnings_set = sort_occ_freq_earning(
            df2,cal_earnings=True)
        
        if info.auxiliary_indicators != [] :
            freqs_set = [freqs_set[i] + ' (%s) '%freqs_set_benchmark[i] for i in range(len(occurances_set))]
            
        table_data_exist = list(zip(*([states_set]+[occurances_set]+[freqs_set] + [['-','-','-','-']])))                                                                  
        table_data_exist = table_data_exist[2:]
        table_data_exist.insert(0,['','','',''])
        table_data_exist.insert(1,['存续期合约总计',sum(occurances_set),'100.00'+ref_100p,'-'])
        
        table_data_exist = table_data_exist[:2]+[table_data_exist[3]] if info.snowball_type in ['锁盈止损雪球','小雪球'] else table_data_exist
        
        t1 = ax1.table(cellText= table_data + table_data_exist,colWidths=[0.22,0.1,0.23,0.28],loc='bottom')    
        t1.auto_set_font_size(False)
        t1.set_fontsize(10)
        t1.scale(1.8,2.5)
                        
        states_set = [(1,4),(5,12),(13,24)]

        states_text_set, occurances_set_benchmark, freqs_set_benchmark = sort_occ_freq_by_ko_month(df1_raw, df1)
        _, occurances_set, freqs_set = sort_occ_freq_by_ko_month(df1, df1)

        if info.auxiliary_indicators != [] :
            freqs_set = [freqs_set[i] + ' (%s) '%freqs_set_benchmark[i] for i in range(len(occurances_set))]    

        ax2 = fig.add_subplot(122)

        states_text_set_pie, occurances_set_pie = delete_zero_occ(states_text_set, occurances_set)
        ax2.pie(occurances_set_pie, colors = sns.color_palette("Blues"), labels=states_text_set_pie, autopct='%2.2f%%',        labeldistance = 1.1,
                pctdistance = 0.85, # 数值标签相对圆心的距离位置
        #         shadow = True, # 添加阴影
                radius = 1,  # 饼图的相对半径
                startangle = 90,  # 绘图的起始角度
                counterclock = False,
                textprops={'fontsize': 10}
            )  # 时针方向 )


        table_data = list(zip(*([states_text_set]+[occurances_set]+[freqs_set])))
        table_data.insert(0,['状态','次数','概率（%）'])
        table_data.insert(1,['已完结合约总计',sum(occurances_set),'100.00'+ref_100p])
        table_data = table_data[:5]+[table_data[6]] if info.snowball_type in ['锁盈止损雪球','小雪球'] else table_data
            
        t2 = ax2.table(cellText= table_data,colWidths=[0.32,0.1,0.25],loc='bottom')    
        t2.auto_set_font_size(False)
        t2.set_fontsize(10)
        t2.scale(1.8,2.5)

        circle1 = plt.Circle((0,0), 0.7, color='white')
        circle2 = plt.Circle((0,0), 0.7, color='white')

        ax1.add_patch(circle1)
        ax2.add_patch(circle2)

        # Add data values to pie chart
        y_axis_loc = 0.3
        for i in range(5):
            if occurances_set[i] == 0 and info.snowball_type in ['锁盈止损雪球','小雪球']:
                continue
            y_axis_loc -= 0.15
            ax2.text(0, y_axis_loc, '%s: %d 例'%(states_text_set[i],occurances_set[i]), ha='center', fontsize=10)

        if info.auxiliary_indicators != []:
            ax1.text(-1.4, -2.9, '注：括号内发生概率为无筛选策略时发生的概率，作为参考；\n    ', ha='left', fontsize=12)
    # 2. 完整周期意即当前数据足以覆盖雪球期权约定期限，否则归为非完整周期类。
        ax1.set_title('敲入敲出分布（已完结合约）')
        ax2.set_title('敲出时间分布（已完结合约）')

        plt.tight_layout()
        plt.savefig('output/fig4.png')
        # plt.show()

    else:
        print('没有满足条件的已完结的雪球！')
    return df1_raw, df2_raw


def plot_06(info, df1_raw, df2_raw):
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False # 用来正常显示负号
    plt.style.use('fivethirtyeight')

    ref_100p = ' (100.00) ' if info.auxiliary_indicators != [] else ''
    states_set = ['敲出','未完全亏损，不敲出','完全亏损']
    # latenet_states_set = [['不敲入，敲出'],['不敲入，不敲出'],['敲入，敲出','敲入，不敲出']]

    mask = (info.df['完成周期'] == 1 ) | (info.df['敲入敲出状态'].isin(['敲入，敲出','敲入，不敲出','不敲入，敲出']))
    df1 = info.df[mask]
    df2 = info.df[~mask]
        
    if df1.shape[0] != 0:
        
        occurances_set_benchmark, freqs_set_benchmark, avg_earnings_set_benchmark =  sort_occ_freq_earning(
            df1_raw,cal_earnings=True,margin_call = False)
        occurances_set, freqs_set, avg_earnings_set = sort_occ_freq_earning(
            df1,cal_earnings=True,margin_call = False)
        print(occurances_set)
        if info.auxiliary_indicators != [] :
            freqs_set = [freqs_set[i] + ' (%s) '%freqs_set_benchmark[i] for i in range(len(occurances_set))]
            avg_earnings_set = [avg_earnings_set[i] + ' (%s) '%avg_earnings_set_benchmark[i] for i in range(len(occurances_set))]


        fig = plt.figure(figsize=(12,10))
        ax1 = fig.add_subplot(121)

        states_set_pie, occurances_set_pie = delete_zero_occ(states_set, occurances_set)

        ax1.pie(occurances_set_pie, colors = sns.color_palette("Blues"), labels=states_set_pie, autopct='%2.2f%%',        labeldistance = 1.1,
                pctdistance = 0.85, # 数值标签相对圆心的距离位置
        #         shadow = True, # 添加阴影
                radius = 1,  # 饼图的相对半径
                startangle = 90,  # 绘图的起始角度
                counterclock = False,
                textprops={'fontsize': 10}
            )  # 时针方向 )

        for i in range(3):
            ax1.text(0, 0.2-0.15*i, '%s: %d 例'%(states_set[i],occurances_set[i]), ha='center', fontsize=10)


        table_data = list(zip(*([states_set]+[occurances_set]+[freqs_set] + [list(avg_earnings_set)])))
        table_data.insert(0,['状态','次数','概率（%）','平均收益率（年化，%）'])

        ref_return = ' (%.2f) '%(round(df1_raw['年化收益率'].mean(),4) * 100) if info.auxiliary_indicators != [] else ''
        
        table_data.insert(1,['已完结合约总计',sum(occurances_set),'100.00' + ref_100p,'%.2f'%(round(df1['年化收益率'].mean(),4) * 100)+ ref_return])
                                                                    
        occurances_set_benchmark, freqs_set_benchmark, avg_earnings_set_benchmark =  sort_occ_freq_earning(
            df2_raw,cal_earnings=True,margin_call = False)
        occurances_set, freqs_set, avg_earnings_set = sort_occ_freq_earning(
            df2,cal_earnings=True,margin_call = False)
        
        if info.auxiliary_indicators != [] :
            freqs_set = [freqs_set[i] + ' (%s) '%freqs_set_benchmark[i] for i in range(len(occurances_set))]
            
        table_data_exist = list(zip(*([states_set]+[occurances_set]+[freqs_set] + [['-','-','-','-']])))                                                                  
        table_data_exist = [table_data_exist[1]]
        table_data_exist.insert(0,['','','',''])
        table_data_exist.insert(1,['存续期合约总计',sum(occurances_set),'100.00'+ref_100p,'-'])

        t1 = ax1.table(cellText= table_data + table_data_exist,colWidths=[0.22,0.1,0.23,0.28],loc='bottom')    
        t1.auto_set_font_size(False)
        t1.set_fontsize(10)
        t1.scale(1.8,2.5)
                        
        states_set = [(1,4),(5,12),(13,24)]

        states_text_set, occurances_set_benchmark, freqs_set_benchmark = sort_occ_freq_by_ko_month(df1_raw, df1)
        _, occurances_set, freqs_set = sort_occ_freq_by_ko_month(df1, df1)

        if info.auxiliary_indicators != [] :
            freqs_set = [freqs_set[i] + ' (%s) '%freqs_set_benchmark[i] for i in range(len(occurances_set))]    

        ax2 = fig.add_subplot(122)

        states_text_set_pie, occurances_set_pie = delete_zero_occ(states_text_set, occurances_set)
        ax2.pie(occurances_set_pie, colors = sns.color_palette("Blues"), labels=states_text_set_pie, autopct='%2.2f%%',        labeldistance = 1.1,
                pctdistance = 0.85, # 数值标签相对圆心的距离位置
        #         shadow = True, # 添加阴影
                radius = 1,  # 饼图的相对半径
                startangle = 90,  # 绘图的起始角度
                counterclock = False,
                textprops={'fontsize': 10}
            )  # 时针方向 )


        table_data = list(zip(*([states_text_set]+[occurances_set]+[freqs_set])))
        table_data.insert(0,['状态','次数','概率（%）'])
        table_data.insert(1,['已完结合约总计',sum(occurances_set),'100.00'+ref_100p])
        
        
        t2 = ax2.table(cellText= table_data,colWidths=[0.32,0.1,0.25],loc='bottom')    
        t2.auto_set_font_size(False)
        t2.set_fontsize(10)
        t2.scale(1.8,2.5)

        circle1 = plt.Circle((0,0), 0.7, color='white')
        circle2 = plt.Circle((0,0), 0.7, color='white')

        ax1.add_patch(circle1)
        ax2.add_patch(circle2)

        # Add data values to pie chart
        for i in range(4):
            ax2.text(0, 0.2-0.15*i, '%s: %d 例'%(states_text_set[i],occurances_set[i]), ha='center', fontsize=10)

        if info.auxiliary_indicators != []:
            ax1.text(-1.4, -2.9, '注：1. 括号内发生概率为无筛选策略时发生的概率，作为参考；\n    2. 完整周期意即当前数据足以覆盖雪球期权约定期限，否则归为非完整周期类。', ha='left', fontsize=12)

        ax1.set_title('敲入敲出分布（已完结合约）')
        ax2.set_title('敲出时间分布（已完结合约）')

        plt.tight_layout()
        plt.savefig('output/fig5.png')
        # plt.show()

    else:
        print('没有满足条件的已完结的雪球！')
