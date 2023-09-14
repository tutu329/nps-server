import pandas as pd
import math
import numpy as np
import scipy
# from Python_User_Logger import *
from Python_User_Logger import *

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
# plt.switch_backend('agg')   # 服务器端须启用这行！！通过更换plt的后端，解决main thread is not in main loop错误

# ==============================================中文字体设置=======================================================
# 下面语句后面一旦出现sns.set，都会覆盖该语句对于字体的设置，须非常注意！！
# 且其他所有的：改配置文件、plt设置、甚至配置utf8（python3已经不需要），都不需要！！！
# sns.set(style="white", font="STHeiti Light.ttc")       # 设置中文字体（注意要搜索所有的sns.set()，都要增加font="SimHei"才行！！）
# plt.rcParams['axes.unicode_minus'] = False  # 设置中文字体后，显示解决保存图像是负号'-'显示为方块的问题
# ==============================================中文字体设置=======================================================

import threading

class Relational_Plots() :
    def __init__(self):
        self.lock = threading.Lock()

    def d1(self):#draw_kdeplot(self):
        sns.set(style="dark")
        rs = np.random.RandomState(50)

        # Set up the matplotlib figure
        f, axes = plt.subplots(3, 3, figsize=(9, 9), sharex=True, sharey=True)

        # Rotate the starting point around the cubehelix hue circle
        for ax, s in zip(axes.flat, np.linspace(0, 3, 10)):
            # Create a cubehelix colormap to use with kdeplot
            cmap = sns.cubehelix_palette(start=s, light=1, as_cmap=True)

            # Generate and plot a random bivariate dataset
            x, y = rs.randn(2, 50)
            sns.kdeplot(x, y, cmap=cmap, shade=True, cut=5, ax=ax)
            ax.set(xlim=(-3, 3), ylim=(-3, 3))

        f.tight_layout()

    def d2(self):#draw_distplot(self):
        sns.set(style="white", palette="muted", color_codes=True)
        rs = np.random.RandomState(10)

        # Set up the matplotlib figure
        f, axes = plt.subplots(2, 2, figsize=(7, 7), sharex=True)
        sns.despine(left=True)

        # Generate a random univariate dataset
        d = rs.normal(size=100)

        # Plot a simple histogram with binsize determined automatically
        sns.distplot(d, kde=False, color="b", ax=axes[0, 0])

        # Plot a kernel density estimate and rug plot
        sns.distplot(d, hist=False, rug=True, color="r", ax=axes[0, 1])

        # Plot a filled kernel density estimate
        sns.distplot(d, hist=False, color="g", kde_kws={"shade": True}, ax=axes[1, 0])

        # Plot a histogram and kernel density estimate
        sns.distplot(d, color="m", ax=axes[1, 1])

        plt.setp(axes, yticks=[])
        plt.tight_layout()

    def d3(self):#draw_jointplot(self):
        sns.set(style="ticks")

        rs = np.random.RandomState(11)
        x = rs.gamma(2, size=1000)
        y = -.5 * x + rs.normal(size=1000)

        sns.jointplot(x, y, kind="hex", color="#4CB391")

    def d4(self):#draw_barplot(self):
        # Initialize the matplotlib figure
        f, ax = plt.subplots(figsize=(6, 15))

        # Load the example car crash dataset
        crashes = sns.load_dataset("car_crashes").sort_values("total", ascending=False)

        # Plot the total crashes
        sns.set_color_codes("pastel")
        sns.barplot(x="total", y="abbrev", data=crashes,
                    label="Total", color="b")

        # Plot the crashes where alcohol was involved
        sns.set_color_codes("muted")
        sns.barplot(x="alcohol", y="abbrev", data=crashes,
                    label="Alcohol-involved", color="b")

        # Add a legend and informative axis label
        ax.legend(ncol=2, loc="lower right", frameon=True)
        ax.set(xlim=(0, 24), ylabel="",
               xlabel="Automobile collisions per billion miles")
        sns.despine(left=True, bottom=True)


    def draw_load1(self, in_list, in_hours, in_bar_label="负荷", in_x=0, in_y=0, in_x_label="x", in_y_label="y"):
        t_len = len(in_list)
        t_data = {
            'y' : in_list,
            'x' : range(t_len)
        }

        t_df_data = pd.DataFrame(t_data)

        # Initialize the matplotlib figure
        f, ax = plt.subplots(figsize=(16, 9))

        # Load the example car crash dataset
        # crashes = sns.load_dataset("car_crashes").sort_values("total", ascending=False)

        # Plot the total crashes
        sns.set_color_codes("pastel")
        # data = sns.load_dataset("tips")

        # g = np.tile(list("AB"), 50)
        #
        # pal = sns.cubehelix_palette(10, rot=-.25, light=.7)
        # g = sns.FacetGrid(t_df_data, row="g", hue="g", aspect=15, height=.5, palette=pal)

        # Draw the densities in a few steps
        # g.map(sns.kdeplot, "x", clip_on=False, shade=True, alpha=1, lw=1.5, bw=.2)
        # g.map(sns.kdeplot, "x", clip_on=False, color="w", lw=2, bw=.2)
        # g.map(sns.lineplot, "t_df_data")
        # g.map(plt.axhline, y=0, lw=2, clip_on=False)


        # print(data.columns)
        if t_len < 1000 :
            sns.barplot(x="x", y="y", data=t_df_data, label=in_bar_label, color="b")
            sns.kdeplot(in_list, shade=True, color="r", vertical=True)
        elif t_len < 3000 :
            t_df_data = t_df_data.rolling(10).max()
            # sns.barplot(x="x", y="y", data=t_df_data, label=in_bar_label, color="b")
            sns.lineplot(data=t_df_data, shade=True)
        elif t_len < 5000 :
            t_df_data = t_df_data.rolling(7).max()
            sns.lineplot(data=t_df_data)
        else :
            t_df_data = t_df_data.rolling(37).max()
            sns.barplot(x="x", y="y", data=t_df_data, label=in_bar_label, color="b")
            # sns.kdeplot(in_list)
            # sns.lineplot(data=t_df_data)
            # sns.kdeplot(data=t_df_data)
        # sns.jointplot(in_x, in_y, kind="hex", color="#4CB391")

        # Plot the crashes where alcohol was involved
        # sns.set_color_codes("muted")
        # sns.barplot(x="alcohol", y="abbrev", data=data,
        #             label="Alcohol-involved", color="b")

        # Add a legend and informative axis label
        ax.legend(ncol=2, loc="lower right", frameon=True)
        ax.set(xlim=(0, in_hours), ylabel=in_y_label, xlabel=in_x_label)

        # 左、右、下的坐标轴都可见
        sns.despine(left=False, right=False, bottom=False)


        # # Set the subplots to overlap
        # g.fig.subplots_adjust(hspace=-.25)
        #
        # # Remove axes details that don't play well with overlap
        # g.set_titles("")
        # g.set(yticks=[])
        # g.despine(bottom=True, left=True)

    def d5(self):#draw_joint_kernel_density_estimate(self):
        # sns.set(style="white")

        # Generate a random correlated bivariate dataset
        rs = np.random.RandomState(5)
        mean = [0, 0]
        cov = [(1, .5), (.5, 1)]
        x1, x2 = rs.multivariate_normal(mean, cov, 500).T
        x1 = pd.Series(x1, name="变量1")
        x2 = pd.Series(x2, name="$X_2$")

        # Show the joint distribution using kernel density estimation
        g = sns.jointplot(x1, x2, kind="kde", height=7, space=0)


    def d7(self):#draw_wide_form_dataset(self):
        sns.set(style="whitegrid")

        rs = np.random.RandomState(365)
        values = rs.randn(365, 4).cumsum(axis=0)
        dates = pd.date_range("1 1 2016", periods=365, freq="D")
        data = pd.DataFrame(values, dates, columns=["A", "B", "C", "D"])
        data = data.rolling(7).mean()

        sns.lineplot(data=data, palette="tab10", linewidth=2.5)

    def draw_load(self, in_heat_list, in_cold_list, in_rolling_hours=24, in_rolling_method="max"):
        t_heat_max = max(in_heat_list)
        t_cold_max = max(in_cold_list)
        t_max_in_list = max(t_heat_max, t_cold_max)
        t_df_heat = pd.DataFrame({
            'value' : in_heat_list,
            'type' : "heat"
        })

        t_df_cold = pd.DataFrame({
            'value' : in_cold_list,
            'type' : "cold"
        })

        if in_rolling_method == "max" :
            t_df_heat = t_df_heat.rolling(in_rolling_hours).max()
            t_df_cold = t_df_cold.rolling(in_rolling_hours).max()
        elif in_rolling_method == "mean" :
            t_df_heat = t_df_heat.rolling(in_rolling_hours).mean()
            t_df_cold = t_df_cold.rolling(in_rolling_hours).mean()

        # Prepare Data
        x = range(len(in_heat_list))
        y1 = t_df_heat['value']
        y2 = t_df_cold['value']
        mycolors = ['tab:red', 'tab:blue', 'tab:green', 'tab:orange', 'tab:brown', 'tab:grey', 'tab:pink', 'tab:olive']
        columns = ['cold', 'heat']
        # Draw Plot
        fig, ax = plt.subplots(1, 1, figsize=(16, 9), dpi=80)
        ax.fill_between(x, y1=y1, y2=0, label=columns[1], alpha=0.5, color=mycolors[0], linewidth=1)
        ax.fill_between(x, y1=y2, y2=0, label=columns[0], alpha=0.5, color=mycolors[1], linewidth=1)
        # Decorations
        t_y_max = math.ceil(t_max_in_list / 10) * 10
        t_y_delta = t_y_max / 10
        # ax.set_title('区域冷热负荷（8760h）', fontsize=16)
        ax.set(ylim=[0, t_y_max])
        ax.legend(fontsize=12, loc="lower right", frameon=True)
        plt.xticks(x[::168], fontsize=10, horizontalalignment='center', rotation=90)
        plt.yticks(np.arange(t_y_delta, t_y_max, t_y_delta), fontsize=10)
        plt.xlim(-10, x[-1])
        # Draw Tick lines
        for y in np.arange(t_y_delta, t_y_max, t_y_delta):
            plt.hlines(y, xmin=0, xmax=len(x), colors='black', alpha=0.2, linestyles="--", lw=0.5)
        # Lighten borders
        plt.gca().spines["top"].set_alpha(0)
        plt.gca().spines["bottom"].set_alpha(.2)
        plt.gca().spines["right"].set_alpha(0)
        plt.gca().spines["left"].set_alpha(0)
        plt.show()

    def draw_p_output(self, in_file_name, in_name_list, in_lists, in_rolling_hours=0, in_start_time=0, in_rolling_method="max", in_plot_method="line", in_kde=False):
        self.lock.acquire()

        t_dataframe = pd.DataFrame()

        t_snapshot_len = 0

        # 组织dataframe数据
        for i in range(len(in_name_list)) :
            t_list = in_lists[i]
            t_snapshot_len = len(in_lists[i])
            if in_rolling_hours > 0 :
                # 压缩数据
                if in_rolling_method == "max":
                    t_list = pd.DataFrame(in_lists[i]).rolling(in_rolling_hours).max()[0].tolist()
                elif in_rolling_method == "mean":
                    t_list = pd.DataFrame(in_lists[i]).rolling(in_rolling_hours).mean()[0].tolist()

            t_dataframe = pd.concat( [t_dataframe, pd.DataFrame({
                'y' : t_list,
                'type' : in_name_list[i],
                'x' : range(len(t_list))
            }) ] )

        # Initialize the FacetGrid object
        if is_win(): 
            sns.set(style="white", rc={"axes.facecolor": (0, 0, 0, 0)}, font="c:\\windows\\fonts\\simhei.ttf")

        if is_mac():
            sns.set(style="white", rc={"axes.facecolor": (0, 0, 0, 0)}, font="/System/Library/Fonts/STHeiti Light.ttc")

        t_palette = sns.cubehelix_palette(len(in_name_list), rot=-.75, start=.5, reverse=True)
        # sns.palplot(sns.color_palette("hls", 8))
        # t_palette = sns.cubehelix_palette(len(in_name_list), rot=-.25, light=.7)
        # t_palette = sns.color_palette("hls", len(in_name_list))
        # g = sns.FacetGrid(df, row="g", hue="g", aspect=15, height=.5, palette=pal)


        # 绘制所有的子图
        # 'row'为一行行排开，'col'为一列列排开，增加了'hue'则palette才有效
        if in_kde == False :
            t_sub_height = 1
            g = sns.FacetGrid(t_dataframe, row='type', hue='type', aspect=15, height=t_sub_height, palette=t_palette)
            if in_plot_method=="line":
                g.map(plt.fill_between, 'x', 'y')
            elif in_plot_method=="bar":
                g.map(sns.barplot, 'x', 'y')
            # if t_snapshot_len > 50:
            #     g.map(plt.fill_between, 'x', 'y')
            # else:
            #     g.map(sns.barplot, 'x', 'y')

        else :
            t_sub_height = 2
            g = sns.FacetGrid(t_dataframe, row='type', hue='type', aspect=3, height=t_sub_height, palette=t_palette)
            g.map(sns.distplot, 'y', kde_kws={"shade": True}, rug_kws={"height": 0.01, "color":"red"}, norm_hist=False, hist=False, rug=True)
            # g.map(sns.distplot, 'y', bins=in_hours_list, kde_kws={"shade": True}, rug_kws={"height": 0.01, "color":"red"}, norm_hist=False, hist=False, rug=True)

        # g.add_legend(loc="lower right")
        # g.map(plt.axhline, y=0, lw=2, clip_on=False)

        # Define and use a simple function to label the plot in axes coordinates
        # 绘制利用小时数（注：label是map（）回调的'type'列中的对应数据，是固定的。 data必须是我们让map传入的'y'列数据）

        def t_draw_subcontent_func(data, color, label):
            ax = plt.gca()
            ax.text(0.96, 0.5, label, fontweight="bold", fontsize=8, color=color, ha="left", va="center", transform=ax.transAxes)
            # ax.text(0.96, 0.5, label, fontweight="bold", fontsize=10, color=color, ha="left", va="center", transform=ax.transAxes)

        g.map(t_draw_subcontent_func, 'y')

        # Set the subplots to overlap
        g.fig.subplots_adjust(hspace=-.25)

        # Remove axes details that don't play well with overlap
        g.set_titles("")    #每个子图的title，必须去掉
        # g.set_xlabels("")
        # g.ax.tick_params(axis='y',labelsize=8) # y轴
        # g.ax.set_xticklabels(ax.get_xticklabels(), rotation=-90)
        # g.ax.set_title('Correlation between features', fontsize=18, position=(0.5, 1.05))

        if in_kde == False :
            if t_snapshot_len>720:
                g.set_axis_labels(x_var="optimized power dispatching ({}h)".format(t_snapshot_len))
            else:
                g.set_axis_labels(x_var="optimized power dispatching ({}h, month {})".format(t_snapshot_len, in_start_time//30+1))
            g.set_xticklabels(fontsize=8)
            g.set(yticks=[])    # Y轴不显示刻度
        else :
            g.set_axis_labels(x_var="Kernel Density Estimate of power dispatching ({}h)".format(t_snapshot_len))
            g.set_xticklabels(fontsize=8)   # X轴显示刻度
            g.set_yticklabels(fontsize=6)   # Y轴显示刻度
        g.despine(bottom=True, left=True)

        g.fig.savefig(in_file_name+".png", dpi=100, transparent=False)
        # f.savefig('sns_style_origin.jpg', dpi=100, bbox_inches='tight')

        self.lock.release()

    def d6(self):#draw_overlapping_densities(self):
        sns.set(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

        # Create the data
        rs = np.random.RandomState(1979)
        x = rs.randn(500)
        g = np.tile(list("ABCDEFGHIJ"), 50)
        print(g)
        df = pd.DataFrame(dict(x=x, g=g))
        print(df)
        m = df.g.map(ord)
        print(m)
        df["x"] += m

        # Initialize the FacetGrid object
        pal = sns.cubehelix_palette(10, rot=-.25, light=.7)
        print(pal)
        g = sns.FacetGrid(df, row="g", hue="g", aspect=15, height=.5, palette=pal)
        print(g)
        # Draw the densities in a few steps
        # g.map(plt.plot, "x")
        g.map(sns.kdeplot, "x", clip_on=False, shade=True, alpha=1, lw=1.5, bw=.2)
        g.map(sns.kdeplot, "x", clip_on=False, color="w", lw=2, bw=.2)
        g.map(plt.axhline, y=0, lw=2, clip_on=False)

        # Define and use a simple function to label the plot in axes coordinates
        def label(x, color, label):
            ax = plt.gca()
            ax.text(0, .2, label, fontweight="bold", color=color,
                    ha="left", va="center", transform=ax.transAxes)

        g.map(label, "x")

        # Set the subplots to overlap
        g.fig.subplots_adjust(hspace=-.25)

        # Remove axes details that don't play well with overlap
        g.set_titles("")
        g.set(yticks=[])
        g.despine(bottom=True, left=True)

def main():
    plot = Relational_Plots()
    plot.d1()
    # import seaborn as sns; sns.set(style="ticks", color_codes=True)
    # tips = sns.load_dataset("tips")
    # g = sns.FacetGrid(tips, col="smoker", row="sex",
    #                   margin_titles=True)
    # g = (g.map(plt.scatter, "total_bill", "tip", color="m", )
    #      .set(xlim=(0, 60), ylim=(0, 12),
    #           xticks=[10, 30, 50], yticks=[2, 6, 10])
    #      .fig.subplots_adjust(wspace=.05, hspace=.05))

    # plt.close()
    plt.show()



if __name__ == "__main__" :
    main()