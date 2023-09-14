from NPS_Invest_Opt_Base import *
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import pandas as pd
from datetime import *
import matplotlib

import Global

# 防止后台plt弹出：main thread is not in main loop之类的错误
matplotlib.use('Agg')

def data_frame(in_data_list):
    t_len = len(in_data_list)
    t_data = {
        'y': in_data_list
        # 'x': range(t_len)
    }
    t_df_data = pd.DataFrame(t_data)
    return t_df_data


class Data_Analysis():
    if is_win():
        fontproperties = FontProperties(fname="c:\\windows\\fonts\\simhei.ttf", size=15)

    if is_mac():
        fontproperties = FontProperties(fname="/System/Library/Fonts/STHeiti Light.ttc", size=15)

    def __init__(self, in_list, in_open_id="", in_start_date=date(2020,1,1), in_hour_per_data=1.0, in_name="", in_unit="MW"):
        self.data_list = in_list
        self.name = in_name
        self.unit = in_unit
        self.start_date = in_start_date
        self.hour_per_data = in_hour_per_data    # 数据采集间隔为多少h，通常为1.0h（365*24个点）、0.25h(365*24*4个点)
        self._open_id = in_open_id

    def draw_dist(self, in_list, in_name="数据1"):
        # 此设置为使图形能显示带特殊格式的字符
        plt.rcParams['axes.unicode_minus'] = False

        # 设置字体
        font = Data_Analysis.fontproperties

        f = plt.figure(figsize=(20, 10))
        ax1 = f.add_subplot()
        # f, axes = plt.subplots(1, figsize=(15, 15))

        ax1.set_ylabel("频  次", fontproperties=font)
        ax1.set_xlabel("{}分布".format(in_name), fontproperties=font)
        sns.set(style="white", palette="muted", color_codes=True)
        sns.distplot(in_list, color="g", rug=True, kde=False, ax=ax1)    # bins为直方图中有几个盒子
        # sns.distplot(in_list, color="g", rug=True, kde=False, ax=ax1, bins=15)    # bins为直方图中有几个盒子

        ax2 = ax1.twinx()
        ax2.set_ylabel("密  度", fontproperties=font)
        sns.kdeplot(in_list, color="g", shade=False, ax=ax2)
        # sns.distplot(t_continuous_zero_list, color="g", kde=True, kde_kws={"shade": True})

        # ax2.set_ylim(ymin=0, ymax=max(self.data_list))
        # ax2.set_ylabel("count")

        # ax2.set_ylabel("y1-y2", fontproperties=FontProperties(fname="C:\Windows\Fonts\simsun.ttc", size=45))
        # plt.yticks(fontproperties=font)
        plt.tight_layout()  # 自动解决标题超出显示范围的问题

        sns.despine(left=True, bottom=False)

    @staticmethod
    def list_substract(in_list1, in_list2):
        return list(np.array(in_list1)-np.array(in_list2))

    @staticmethod
    def draw_lists(in_lists, in_open_id="", in_dpi=128, in_pic_name=0, in_names=0, in_start=0, in_stop=0, in_alphas=0, in_share_y=False):
        print("draw_lists in_pic_name is : ", in_pic_name)
        t_len = len(in_lists)
        t_limit_top = 0
        t_limit_bottom = 0
        if in_stop == 0:
            t_steps = len(in_lists[0])
        else:
            t_steps = in_stop

        for i in range(t_len):
            t_limit_top = max(t_limit_top, max(in_lists[i]))
            t_limit_bottom = min(t_limit_bottom, min(in_lists[i]))

        # try:
        # 捕获subplots在main thread外运行的错误（其实能够正常绘图并存盘）
        print("draw_lists dpi is {}.".format(in_dpi))
        f, axes = plt.subplots(t_len, 1, figsize=(20, 5 * t_len), dpi=in_dpi, sharex=True, sharey=in_share_y)
        # f, axes = plt.subplots(t_len, 1, figsize=(20, 5 * t_len), dpi=128, sharex=True, sharey=in_share_y)

        for i in range(t_len):
            ax = plt.subplot(t_len, 1, i + 1)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_visible(False)

            if in_names!=0:
                ax.set_title(in_names[i], fontproperties=Data_Analysis.fontproperties)
                # ax.set_xlabel(in_names[i], fontproperties=Data_Analysis.fontproperties)

            if in_share_y == True:
                plt.ylim(t_limit_bottom, t_limit_top)

            # 绘制时序曲线
            plt.plot(in_lists[i][in_start:t_steps], color="skyblue")

            if in_alphas != 0:
                plt.fill_between(x=range(len(in_lists[i][in_start:t_steps])), y1=in_lists[i][in_start:t_steps], color="skyblue", alpha=in_alphas[i])
            else:
                plt.fill_between(x=range(len(in_lists[i][in_start:t_steps])), y1=in_lists[i][in_start:t_steps], color="skyblue", alpha=0.5)

        if in_pic_name!=0:
            # plt.suptitle("时序数据对比", fontproperties=Data_Analysis.fontproperties)
            t_name = Global.get("path")+"static/pic/{}_openid({}).png".format(in_pic_name, in_open_id)
            print(t_name+" saving...", flush=True)
            plt.savefig(t_name)
            print(t_name+" saved successfully.", flush=True)

        # except:
        #     print("plt.subplots警告: Starting a Matplotlib GUI outside of the main thread will likely fail.")

    @staticmethod
    def draw_2d_jointplot(in_list1, in_list2, in_name1="数据1", in_name2="数据2"):
        # 此设置为使图形能显示带特殊格式的字符
        plt.rcParams['axes.unicode_minus'] = False

        # 设置字体
        font = Data_Analysis.fontproperties
        f = plt.figure(figsize=(20, 10))

        def t_kdeplot(x, y):
            sns.kdeplot(x, y, cbar=True, shade_lowest=False, cmap="Greens", space=0, ratio=15, shade=True)
        grid = sns.JointGrid(x=in_list1, y=in_list2)
        grid = grid.plot_joint(t_kdeplot)

        # 绘制横边图
        ax1=grid.ax_marg_x
        sns.distplot(in_list1, color="g", kde=True, ax=ax1)    # bins为直方图中有几个盒子
        # ax12 = ax1.twinx()
        # sns.kdeplot(in_list1, color="g", shade=False, ax=ax12)

        # 绘制竖边图
        ax2=grid.ax_marg_y
        sns.distplot(in_list2, color="g", kde=True, ax=ax2, vertical=True)    # bins为直方图中有几个盒子
        # ax22 = ax2.twinx()
        # sns.kdeplot(in_list2, color="g", shade=False, ax=ax22, vertical=True)

        grid.fig.set_figwidth(sqrt(max(in_list1)/max(in_list2))*10)
        grid.fig.set_figheight(10)
        grid.set_axis_labels("{}分布".format(in_name1), "{}分布".format(in_name2), fontproperties=font)

        plt.tight_layout()  # 自动解决标题超出显示范围的问题
        sns.set(style="white", palette="muted", color_codes=True)
        sns.despine(left=True, bottom=True)

    @staticmethod
    def draw_2d_kde(in_list1, in_list2, in_name1="数据1", in_name2="数据2"):
        # 此设置为使图形能显示带特殊格式的字符
        plt.rcParams['axes.unicode_minus'] = False

        # 设置字体
        font = Data_Analysis.fontproperties

        f = plt.figure(figsize=(20, 10))
        # ax1 = f.add_subplot()
        # ax1.set_ylabel("{}分布".format(in_name2), fontproperties=font)
        # ax1.set_xlabel("{}分布".format(in_name1), fontproperties=font)
        # sns.kdeplot(x=in_list1, y=in_list2, shade_lowest=True, cmap="Greens", shade=True, cbar=True, ax=ax1)   # shade_lowest为最底下是否上色（用于多图并列）；cmap为递进色系列（如"Greens"、"Blues"）； cbar为右侧比色卡
        grid = sns.jointplot(x=in_list1, y=in_list2, kind="kde", cbar=True, shade_lowest=False, cmap="Greens", space=0, ratio=10, shade=True, marginal_kws={"rug":True,"shade":True,"color":"b"})   # shade_lowest为最底下是否上色（用于多图并列）；cmap为递进色系列（如"Greens"、"Blues"）； cbar为右侧比色卡
        grid.fig.set_figwidth(sqrt(max(in_list1)/max(in_list2))*10)
        grid.fig.set_figheight(10)
        grid.set_axis_labels("{}分布".format(in_name1), "{}分布".format(in_name2), fontproperties=font)
        # ax2 = ax1.twinx()
        # ax2.set_ylabel("{}分布".format(in_name1), fontproperties=font)
        # ax2.set_xlabel("{}分布".format(in_name2), fontproperties=font)
        # sns.kdeplot(x=in_list2, y=in_list1, shade_lowest=False, cmap="Blues", shade=True, cbar=True, ax=ax2)   # shade_lowest为最底下是否上色（用于多图并列）；cmap为递进色系列（如"Greens"、"Blues"）； cbar为右侧比色卡

        plt.tight_layout()  # 自动解决标题超出显示范围的问题
        sns.set(style="white", palette="muted", color_codes=True)
        sns.despine(left=True, bottom=True)

    def get_cumulative_list(self):
        t_list =[]
        t_cumu = 0
        for i in range(len(self.data_list)):
            t_cumu = t_cumu + self.data_list[i]
            t_list.append(t_cumu)
        return t_list

    def draw_cumulation(self, in_name=0):
        t_name=""
        if in_name!=0:
            t_name = in_name
        t_list = self.get_cumulative_list()
        Data_Analysis.draw_lists(in_open_id=self._open_id, in_lists=[t_list], in_names=[t_name])

    def draw_continuous_zero_dist(self, in_min_percent=0.0):
        self.draw_dist(self.get_continuous_zero_list(in_min_percent=in_min_percent), in_name="{}连续零值统计".format(self.name))

    # 将self.data_list中的0变为1，非0变为0.
    def get_zero_list(self, in_min_percent=0.0, in_value=0):
        t_list  = []
        t_max = self.max()

        t_value=in_value
        if t_value==0 :
            t_value =  t_max

        for i in range(len(self.data_list)):
            if self.data_list[i] <= in_min_percent * t_max :
                t_list.append(t_value)
            else:
                t_list.append(0)
        return t_list

    # 获取为0时宽的最大值
    def get_max_zero_width(self, in_min_percent=0.0):
        t_zero_list = self.get_zero_list(in_min_percent=in_min_percent)
        t_max_zero_width = 0
        t_temp  = 0

        if len(t_zero_list)<=1:
            return 0

        for i in range(len(t_zero_list)) :
            if i>0:
                if t_zero_list[i]!=0 and t_zero_list[i-1]!=0:
                    t_temp = t_temp + 1
                else:
                    t_temp = 0
                t_max_zero_width  = max(t_max_zero_width, t_temp)
        return (t_max_zero_width+1)*self.hour_per_data

    # 获取为0时宽在[max-acceptalbe_hours, max]的所有day
    def get_max_zero_width_days(self, in_min_percent=0.0, in_acceptable_hours=0):
        max_zero_width = self.get_max_zero_width(in_min_percent=in_min_percent)
        t_max_day_list = []

        t_max_zero_width = 0
        t_temp  = 0
        t_last_append = False

        t_zero_list = self.get_zero_list(in_min_percent=in_min_percent)
        if len(t_zero_list)<=1:
            return "not found"

        for i in range(len(t_zero_list)) :
            if i>0:
                if t_zero_list[i]!=0 and t_zero_list[i-1]!=0:
                    t_temp = t_temp + 1
                else:
                    t_temp = 0
                # 若为0的时宽在[max-acceptalbe_hours, max]之间，则输出到list。
                # 要注意，必须剔除当前在[max-acceptalbe_hours, max]之间、下一步也在[max-acceptalbe_hours, max]之间的点，否则重复统计了。
                if max_zero_width-1-in_acceptable_hours <= t_temp and t_temp <= max_zero_width-1:
                    if t_last_append==False:
                        t_max_day_list.append(self.start_date+timedelta(hours=i*self.hour_per_data))
                        t_last_append = True
                else:
                    t_last_append = False

        return t_max_day_list

    # 将连续为0的点统计成列表，用于从统计分布图中看出连续为0的时宽水平
    def get_continuous_zero_list(self, in_min_percent=0.0):
        t_continuous_zero_list = []

        t_temp  = 0
        t_last_append = False

        t_zero_list = self.get_zero_list(in_min_percent=in_min_percent)
        if len(t_zero_list)<=1:
            return t_continuous_zero_list

        for i in range(len(t_zero_list)) :
            if i>0:
                if t_zero_list[i]!=0 and t_zero_list[i-1]!=0:
                    t_temp = t_temp + 1
                if t_zero_list[i]==0 and t_zero_list[i-1]!=0:
                    t_continuous_zero_list.append(t_temp+1)
                    t_temp = 0
        return t_continuous_zero_list

    def print(self):
        print("------------------------------{}-------------------------------".format(self.name))
        print("max is {:8.2f} {}, at {}".format(self.max(), self.unit, self.max_day()))
        print("min is {:8.2f} {}, at {}".format(self.min(), self.unit, self.min_day()))
        print("max delta up   is {:7.1%}, at {}".format(self.max_up_rate(), self.max_up_rate_day()))
        print("max delta down is {:7.1%}, at {}".format(self.max_down_rate(), self.max_down_rate_day()))
        print("sum is {:.2f} {}h".format(self.sum(), self.unit))
        print("utilization hours is {:.0f}h".format(self.util_hours()))

    def max(self):
        return max(self.data_list)

    def max_day(self):
        t_max = self.max()
        t_date = self.start_date
        for i in range(len(self.data_list)):
            if t_max==self.data_list[i]:
                t_date = t_date + timedelta(hours=i*self.hour_per_data)
                break
        return t_date

    def min(self):
        return min(self.data_list)

    def min_day(self):
        t_min = self.min()
        t_date = self.start_date
        for i in range(len(self.data_list)):
            if t_min==self.data_list[i]:
                t_date = t_date + timedelta(hours=i*self.hour_per_data)
                break
        return t_date

    def sum(self):
        return sum(self.data_list)

    def max_up_rate(self):
        t_list = self.data_list

        t_max = max(t_list)
        if t_max==0:
            return 0
        t_max_up = 0
        for i in range(len(t_list)):
            if len(t_list)>1 and i<len(t_list)-1 :
                t_max_up = max(t_max_up, t_list[i+1] - t_list[i])
        return t_max_up/t_max

    def max_up_rate_day(self):
        t_list = self.data_list
        t_max = self.max()
        if t_max==0:
            return 0

        t_max_up_rate = self.max_up_rate()
        t_date = self.start_date
        for i in range(len(t_list)):
            if len(t_list)>1 and i<len(t_list)-1 :
                if t_max_up_rate == (t_list[i+1] - t_list[i])/t_max :
                    t_date = t_date + timedelta(hours=i*self.hour_per_data)
                    break
        return t_date

    def max_down_rate(self):
        t_list = self.data_list

        t_max = max(t_list)
        if t_max==0:
            return 0
        t_max_down = 0
        for i in range(len(t_list)):
            if len(t_list)>1 and i<len(t_list)-1 :
                t_max_down = min(t_max_down, t_list[i+1] - t_list[i])
        return t_max_down/t_max

    def max_down_rate_day(self):
        t_list = self.data_list
        t_max = self.max()
        if t_max==0:
            return 0

        t_max_down_rate = self.max_down_rate()
        t_date = self.start_date
        for i in range(len(t_list)):
            if len(t_list)>1 and i<len(t_list)-1 :
                if t_max_down_rate == (t_list[i+1] - t_list[i])/t_max :
                    t_date = t_date + timedelta(hours=i*self.hour_per_data)
                    break
        return t_date

    def util_hours(self):
        if self.max()==0:
            return 0
        else:
            return self.sum()/self.max()

def main():
    t_file = XLS_File('xls/data_analysis_test.xlsx', in_cols=[0, 1, 2, 3])  # 泽雅瞿溪供区
    t_load = t_file.get_list("负荷")
    t_pv = t_file.get_list("光伏")
    t_wind = t_file.get_list("风电")
    t_load_pv = Data_Analysis.list_substract(t_load, t_pv)
    t_load_pv_wind = Data_Analysis.list_substract(t_load_pv, t_wind)

    t_data_pv = Data_Analysis(t_pv, in_hour_per_data=1.0, in_name="PV", in_unit="MW")
    t_data_pv.print()
    t_data_load = Data_Analysis(t_load, in_name="Load", in_unit="MW")
    t_data_load.print()
    Data_Analysis([0,50,100,0]).print()

    # Data_Analysis.draw_lists(in_lists=[t_load, t_pv], in_names=["负荷", "光伏"], in_pic_name="data_analysis", in_alphas=[0.5, 0.5], in_share_y=True)
    Data_Analysis.draw_lists(in_lists=[t_load, t_pv, t_load_pv], in_names=["负荷", "光伏", "负荷-光伏"], in_pic_name="data_analysis", in_start=720*3, in_stop=720+720*3)
    # Data_Analysis.draw_lists(in_lists=[t_load, t_pv, t_load_pv], in_names=["负荷", "光伏", "负荷-光伏"], in_pic_name="data_analysis", in_start=720*7, in_stop=720+720*7)

    # 统计连续为0的水平
    Data_Analysis(t_pv, in_name="PV").draw_continuous_zero_dist(in_min_percent=0.05)
    Data_Analysis(t_load, in_name="Load").draw_continuous_zero_dist(in_min_percent=0.05)
    Data_Analysis.draw_2d_jointplot(in_list1=t_pv, in_list2=t_load, in_name1="PV", in_name2="Load")
    Data_Analysis.draw_2d_kde(in_list1=t_pv, in_list2=t_load, in_name1="PV", in_name2="Load")
    t_data_load_pv = Data_Analysis(t_load_pv, in_name="Load-PV")
    t_data_load_pv.draw_cumulation(in_name="负荷-光伏的累积")
    t_data_load_pv_wind = Data_Analysis(t_load_pv_wind, in_name="Load-PV-Wind")
    t_data_load_pv_wind.draw_cumulation(in_name="负荷-光伏-风电的累积")
    print("min(Load-PV) is {}".format(min(t_data_load_pv.get_cumulative_list())))
    print("max(Load-PV) is {}".format(max(t_data_load_pv.get_cumulative_list())))
    print("min(Load-PV-Wind) is {}".format(min(t_data_load_pv_wind.get_cumulative_list())))
    print("max(Load-PV-Wind) is {}".format(max(t_data_load_pv_wind.get_cumulative_list())))

    t_list = t_data_pv.get_zero_list(in_min_percent=0.1)
    print("max zero width is {}".format(t_data_pv.get_max_zero_width(in_min_percent=0.05)))
    t_max_days  = t_data_pv.get_max_zero_width_days(in_min_percent=0.05, in_acceptable_hours=.0)
    for i  in range(len(t_max_days)):
        print("max zero width day includes {}".format(t_max_days[i]))

    # print(date(2020,1,1)+timedelta(hours=6000))
    plt.show()

if __name__ == "__main__" :
    main()