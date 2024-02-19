from NPS_Invest_Opt_Base import *
from Data_Analysis import *

import json

class NPS_Case():
    def __init__(self):
        pass

    def case1(self, in_called, in_path):
        print("--------------------案例\"{}\"为全国新型电力系统--------------------".format(Get_Current_Func_Name()))
        if in_called==False:
            return

        t_simu_hours = 24
        # t_simu_hours = 720
        # t_simu_hours = 24*365
        # t_simu_hours = 24*365*10
        # t_simu_hours = 24*365*20

        t_simu_years = t_simu_hours//8760

        # =========================节点0=========================
        t_sys = Sys(
            in_share_y=True,
            in_name_id="sys1",
            in_simu_hours=t_simu_hours,
            in_rate=0.08,
            # in_spring_festival=Spring_Festival(in_bypass=False, in_start_day=10, in_stop_day=60)
            in_spring_festival=Spring_Festival(in_years=t_simu_years, in_bypass=False, in_start_day=10, in_stop_day=60),
            in_analysis_day_list=[0,90,180,270]
            # in_analysis_day_list=0
        )
        t_sys.Add_Bus()

        # 直接读取8760h标幺值数据==========
        file_path = 'D:/server/server-xls/11.xls'

        t_file = XLS_File(file_path, in_cols=[0,1,2,3], in_row_num=8761)
        # t_file = XLS_File('xls/data_analysis.xlsx', in_cols=[0,1,2,3])

        t_load1 = Load(in_sys=t_sys, in_name_id="load", in_p_nom=15*10**8)
        print(f'==============Load()================')
        t_load1.set_one_year_p(t_file.get_list("负荷"))   #负荷数据的正负一定要搞清楚，对结果影响非常大
        # t_load1.load_nom = 140000*0.9  # kW 最大允许负荷（决定了储能的放电功率空间），#泽雅+瞿溪供区
        # print(t_load1.one_year_p_list)

        # t_pv1 = NE_Plant(in_sys=t_sys, in_name_id="pv", in_p_nom=26*10**8, in_p_nom_extendable=False)   # 2020年全国光伏约2.5亿kW
        t_pv1 = NE_Plant(in_sys=t_sys, in_name_id="pv", in_p_nom=2.5*10**8, in_p_nom_extendable=True)   # 2020年全国光伏约2.5亿kW
        # t_pv1 = NE_Plant(in_sys=t_sys, in_name_id="pv", in_p_nom=2.5*10**8, in_p_nom_extendable=True)   # 2020年全国光伏约2.5亿kW
        t_pv1.marginal_cost["value"]=0.0
        t_pv1.capital_cost["value"]=1.78     # IEA 2050 中国造价
        t_pv1.set_one_year_p(t_file.get_list("光伏"))   #光伏数据，实际只需要特性

        # t_wind1 = NE_Plant(in_sys=t_sys, in_name_id="wind", in_p_nom=20*10**8, in_p_nom_extendable=False) # 2020年全国风电约3亿kW
        t_wind1 = NE_Plant(in_sys=t_sys, in_name_id="wind", in_p_nom=3*10**8, in_p_nom_extendable=True) # 2020年全国风电约3亿kW
        # t_wind1 = NE_Plant(in_sys=t_sys, in_name_id="wind", in_p_nom=3*10**8, in_p_nom_extendable=True) # 2020年全国风电约3亿kW
        t_wind1.marginal_cost["value"]=0.0
        t_wind1.capital_cost["value"]=6.367      # IEA 2050 中国造价
        t_wind1.set_one_year_p(t_file.get_list("风电"))   #光伏数据，实际只需要特性

        # 蓄电（电池储能）
        # 目前大型储能电站，2020年的萧电储能系统100MW*2h
        # 静态投资约5.86亿元（经营期15年），储能单元及安装54.0%、特殊项目费用（第一期和第二期的电池更换）19.4%、PCS系统11.15%（由于是考虑功率成本，因此含PCS 5.27%、主变1.24%（220kV主变可能不计列钱，即仅计及35kV变压器）、配电4.64%）、其他设施和工程（控制保护2%、电缆接地3%、集装箱基础1%、其他6%）12%，其他费用2%、预备费2%
        # 动态投资约5.46亿元，其中第一期和第二期电池更换费用折现共计-0.48亿元。
        # 因此，按电池和pcs的造价比例73.4:11.15，取2.54元/Wh、0.38元/W。（注意：如果考虑储能生命周期过短，可以把电池储能的Wh和W成本提高一倍或一定倍数考虑）
        # 注：计算中，按照2025年水平，价格均按50%计，取1.38元/Wh、0.24元/W（本项目不计220kV主变，后续项目最好考虑110kV及以下接入或220主变免费，即kW造价按0.4-0.5元/W左右（含pcs、35kV升压变、配电、110kV升压变，比较合理）
        # 综合效率取90%左右，因此充放电效率分别取95%、95%
        t_ess1 = Energy_Storage(t_sys, "bes",
                                in_p_charge_nom_extendable=True,
                                in_p_discharge_nom_extendable=True,
                                in_e_nom_extendable=True
                                )
        t_ess1.charge_marginal_cost["value"] = 0.0      # 考虑充电的电量边际成本为市电边际成本
        t_ess1.discharge_marginal_cost["value"] = -0.0   # 考虑放电的电量边际成本为市电边际成本
        # t_ess1.discharge_marginal_cost["value"] = -1.5   # 考虑放电的电量边际成本为市电边际成本
        t_ess1.effi_charge["value"] = 0.95
        t_ess1.effi_discharge["value"] = 0.95
        t_ess1.capital_cost_charge_p["value"] = 0.12
        t_ess1.capital_cost_discharge_p["value"] = 0.12
        t_ess1.capital_cost_e["value"] = 1.38
        # t_ess1.capital_cost_p2["value"] = 0.4    #设备换新的成本
        # t_ess1.capital_cost_e2["value"] = 1.0    #设备换新的成本
        # t_ess1.capital_cost2_year["value"] = 10       #设备更换的年限

        # 蓄电（抽蓄）
        # 目前4*300MW级的电站，一般容量为5-7h电量，2016年的1400MW宁海抽蓄动态79亿元（建设期7-8年，经营期30年），大约5600元/kW，其中机电及金属结构设备安装26%、建筑26%、施工辅助工程+环保水土7%、征地+移民补偿5%、独立费用（建设、设计）15%、预备+价差10%、建设期利息11%。）
        # 因此，取0.46元/Wh、2.80元/W。
        # 综合效率取80%左右，因此充放电效率分别取90%、90%
        t_ess2 = Energy_Storage(t_sys, "php",
                                in_p_charge_nom_extendable=True,
                                in_p_discharge_nom_extendable=True,
                                in_e_nom_extendable=True,
                                in_p_charge_nom=1.2*10**8,      # 2030年左右全国抽蓄规划将达到约1.2亿kW
                                in_p_discharge_nom=1.2*10**8,
                                in_e_nom=1.2*6*10**8
                                )
        t_ess2.charge_marginal_cost["value"] = 0.0      # 考虑充电的电量边际成本为市电边际成本
        t_ess2.discharge_marginal_cost["value"] = -0.0   # 考虑放电的电量边际成本为市电边际成本
        # t_ess2.discharge_marginal_cost["value"] = -1.5   # 考虑放电的电量边际成本为市电边际成本
        t_ess2.effi_charge["value"] = 0.9
        t_ess2.effi_discharge["value"] = 0.9
        t_ess2.capital_cost_charge_p["value"] = 1.4
        t_ess2.capital_cost_discharge_p["value"] = 1.4
        t_ess2.capital_cost_e["value"] = 0.46
        # t_ess2.capital_cost_p2["value"] = 0.4    #设备换新的成本
        # t_ess2.capital_cost_e2["value"] = 1.0    #设备换新的成本
        # t_ess2.capital_cost2_year["value"] = 10       #设备更换的年限

        # 氢储能（p_charge_nom != p_discharge）
        t_ess3 = Energy_Storage(t_sys, "hes",
                                in_p_charge_nom_extendable=True,        # p_charge_nom为电解制氢容量
                                in_p_discharge_nom_extendable=True,     # p_discharge_nom为氢燃机容量，实际即为天然气机组容量
                                in_e_nom_extendable=True,               # e_nom为地下盐穴储氢容量
                                in_p_equal=False                        # 这个参数很重要，即制氢功率和发电功率可以不相等
                                )
        t_ess3.charge_marginal_cost["value"] = 0.0          # 考虑充电的电量边际成本为市电边际成本
        t_ess3.discharge_marginal_cost["value"] = -0.0      # 考虑放电的电量边际成本为市电边际成本
        # t_ess3.discharge_marginal_cost["value"] = -1.5    # 考虑放电的电量边际成本为市电边际成本
        t_ess3.effi_charge["value"] = 0.8       # 充电效率，即制氢效率
        t_ess3.effi_discharge["value"] = 0.6    # 放电效率，即氢燃机联合循环发电效率（燃料电池效率更低一些）
        t_ess3.capital_cost_charge_p["value"] = 2.24    # 制氢造价参考盈德气体（上海）有限公司新能源研究发展总监的文献，即0.8万元/Nm3，折算后约2.2元/W。如果浙江包括2000km左右的氢管网，造价要增加240亿左右，单价看情况增加到3.0或者多少
        t_ess3.capital_cost_discharge_p["value"] = 2.2  # 燃机造价，斯林军2021.12.24：9f目前3元/W不到、9h目前2.2元/W
        t_ess3.capital_cost_e["value"] = 0.006          # 这里采用地下盐穴储氢系统，成本为电池储能容量单价的百分之一
        # t_ess3.capital_cost_p2["value"] = 0.4    #设备换新的成本
        # t_ess3.capital_cost_e2["value"] = 1.0    #设备换新的成本
        # t_ess3.capital_cost2_year["value"] = 10       #设备更换的年限

        t_gas1 = Plant(t_sys, "gas", in_p_nom=0*10**8, in_p_nom_extendable=False)  # 2020年全国气电约0.9-1.0亿kW
        # t_gas1 = Plant(t_sys, "gas", in_p_nom=1.0*10**8, in_p_nom_extendable=True)  # 2020年全国气电约0.9-1.0亿kW
        t_gas1.capital_cost["value"]=2.2
        t_gas1.marginal_cost["value"]=0.3

        t_coal1 = Plant(t_sys, "coal", in_p_nom=0.0*10**8, in_p_nom_extendable=False, in_max_pu=1.0, in_min_pu=0.3)
        # t_coal1 = Plant(t_sys, "coal", in_p_nom=4.0*10**8, in_p_nom_extendable=False, in_max_pu=1.0, in_min_pu=0.3)
        t_coal1.capital_cost["value"]=4.0
        t_coal1.marginal_cost["value"]=0.2

        # 核电，增加plant最大出力和最小出力pu的控制
        t_nuc1 = Plant(t_sys, "nuclear", in_p_nom=4.0*10**8, in_p_nom_extendable=True, in_max_pu=1.0, in_min_pu=0.9)    # 2030年全国核电规划将达到约4.0亿kW
        t_nuc1.capital_cost["value"]=12.0
        t_nuc1.marginal_cost["value"]=0.06

        t_hydro1 = Hydro_Plant(t_sys, "hydro1", in_hours_nom=2000, in_p_nom=3.0*10**8, in_p_nom_extendable=True)       # 2020年全国水电约3亿kW
        t_hydro1.capital_cost["value"]=10.0
        t_hydro1.marginal_cost["value"]=0.0

        # 吸收松弛节点
        t_slack_node1 = Absorption_Slack_Node(
            t_sys,
            in_name_id="sl_absorp",
            in_p_max=100*10**8,
            # in_p_max=10*10**8,
            in_e_max=100*10**11 * t_simu_years, # 考虑10%新能源发电量可以上送；全年最大吸收电量 kWh (全年新能源发电量为1.985亿kWh）
            # in_e_max=10*10**11,               # 考虑10%新能源发电量可以上送；全年最大吸收电量 kWh (全年新能源发电量为1.985亿kWh）
            in_marginal_cost=-0.0)              # 考虑上送电量没有成本
        t_slack_node1.e_output = True

        # 注入松弛节点
        t_slack_node2 = Injection_Slack_Node(
            t_sys,
            in_name_id="sl_inject",
            in_p_max=0*10**8,
            # in_p_max=1*140000*0.9,
            in_e_max=0*10**11 * t_simu_years,   # 全年最大注入电量 kWh  (全年负荷为3.3亿kWh，新能源全电量消纳后电量缺口为1.33亿kWh）
            # in_e_max=1*4.0*10**8,             # 全年最大注入电量 kWh  (全年负荷为3.3亿kWh，新能源全电量消纳后电量缺口为1.33亿kWh）
            in_marginal_cost=0.0)
        t_slack_node2.e_output = True

        # =========================节点1=========================
        # t_sys.Add_Bus()
        # t_link1 = Link_Base(t_sys, in_bus1_id=0, in_bus2_id=1, in_name="lk1")
        # t_p2g = Oneway_Link(t_sys, in_bus1_id=0, in_bus2_id=1, in_name="p2g1", in_effi=1.00)

        # t_load2 = Load(in_sys=t_sys, in_name_id="load2", in_hours=t_simu_hours)
        # t_load2.one_year_load_list = list(np.array(t_file.get_list("8760数据2")) * (-1000))    #负荷数据的正负一定要搞清楚，对结果影响非常大

        t_sys.do_optimize()

        # 测试e_list是否有负值
        # for i in range(len(t_ess1._var_list_values("e_list"))):
        #     if t_ess1._var_list_values("e_list")[i]<0:
        #         print("{}th: {}".format(i, t_ess1._var_list_values("e_list")[i]))

    def case2(self, in_called, in_path):
        print("--------------------案例\"{}\"为浙江省新型电力系统--------------------".format(Get_Current_Func_Name()))
        if in_called==False:
            return

        t_simu_hours = 24
        # t_simu_hours = 720
        # t_simu_hours = 24*365
        # t_simu_hours = 24*365*10
        # t_simu_hours = 24*365*20

        t_simu_years = t_simu_hours//8760

        # =========================节点0=========================
        t_sys = Sys(
            in_share_y=True,
            in_name_id="sys1",
            in_simu_hours=t_simu_hours,
            in_rate=0.08,
            # in_spring_festival=Spring_Festival(in_bypass=False, in_start_day=10, in_stop_day=60)
            in_spring_festival=Spring_Festival(in_years=t_simu_years, in_bypass=False, in_start_day=10, in_stop_day=60),
            in_analysis_day_list=[0,90,180,270]
            # in_analysis_day_list=0
        )
        t_sys.Add_Bus()

        # 直接读取8760h标幺值数据==========
        t_file = XLS_File('xls/data_analysis.xlsx', in_cols=[0,1,2,3])

        t_load1 = Load(in_sys=t_sys, in_name_id="load", in_p_nom=1.9*10**8)
        t_load1.set_one_year_p(t_file.get_list("负荷"))   #负荷数据的正负一定要搞清楚，对结果影响非常大
        # t_load1.load_nom = 140000*0.9  # kW 最大允许负荷（决定了储能的放电功率空间），#泽雅+瞿溪供区
        # print(t_load1.one_year_p_list)

        t_pv1 = NE_Plant(in_sys=t_sys, in_name_id="pv", in_p_nom=0.2750*10**8, in_p_nom_extendable=True)   # 采用2025年水平，后续与调节一起优化
        # t_pv1 = NE_Plant(in_sys=t_sys, in_name_id="pv", in_p_nom=0.5500*10**8, in_p_nom_extendable=False)   #
        t_pv1.marginal_cost["value"]=0.0
        t_pv1.capital_cost["value"]=1.78     # IEA 2050 中国造价
        t_pv1.set_one_year_p(t_file.get_list("光伏"))   #光伏数据，实际只需要特性

        t_wind1 = NE_Plant(in_sys=t_sys, in_name_id="wind", in_p_nom=0.0641*10**8, in_p_nom_extendable=True) # 采用2025年水平，后续与调节一起优化
        # t_wind1 = NE_Plant(in_sys=t_sys, in_name_id="wind", in_p_nom=0.2341*10**8, in_p_nom_extendable=False) #
        t_wind1.marginal_cost["value"]=0.0
        t_wind1.capital_cost["value"]=6.367      # IEA 2050 中国造价
        t_wind1.set_one_year_p(t_file.get_list("风电"))   #光伏数据，实际只需要特性

        # 蓄电（电池储能）
        # 目前大型储能电站，2020年的萧电储能系统100MW*2h
        # 静态投资约5.86亿元（经营期15年），储能单元及安装54.0%、特殊项目费用（第一期和第二期的电池更换）19.4%、PCS系统11.15%（由于是考虑功率成本，因此含PCS 5.27%、主变1.24%（220kV主变可能不计列钱，即仅计及35kV变压器）、配电4.64%）、其他设施和工程（控制保护2%、电缆接地3%、集装箱基础1%、其他6%）12%，其他费用2%、预备费2%
        # 动态投资约5.46亿元，其中第一期和第二期电池更换费用折现共计-0.48亿元。
        # 因此，按电池和pcs的造价比例73.4:11.15，取2.54元/Wh、0.38元/W。（注意：如果考虑储能生命周期过短，可以把电池储能的Wh和W成本提高一倍或一定倍数考虑）
        # 注：计算中，按照2025年水平，价格均按50%计，取1.38元/Wh、0.24元/W（本项目不计220kV主变，后续项目最好考虑110kV及以下接入或220主变免费，即kW造价按0.4-0.5元/W左右（含pcs、35kV升压变、配电、110kV升压变，比较合理）
        # 综合效率取90%左右，因此充放电效率分别取95%、95%
        t_ess1 = Energy_Storage(t_sys, "bes",
                                in_p_charge_nom_extendable=True,
                                in_p_discharge_nom_extendable=True,
                                in_e_nom_extendable=True,
                                in_charge_effi=0.95,
                                in_discharge_effi=0.95
                                )
        t_ess1.charge.marginal_cost["value"] = 0.0      # 考虑充电的电量边际成本为市电边际成本
        t_ess1.discharge.marginal_cost["value"] = -0.0   # 考虑放电的电量边际成本为市电边际成本
        # t_ess1.discharge_marginal_cost["value"] = -1.5   # 考虑放电的电量边际成本为市电边际成本
        t_ess1.charge.capital_cost["value"] = 0.12
        t_ess1.discharge.capital_cost["value"] = 0.12
        t_ess1.capital_cost_e["value"] = 1.38
        # t_ess1.capital_cost_p2["value"] = 0.4    #设备换新的成本
        # t_ess1.capital_cost_e2["value"] = 1.0    #设备换新的成本
        # t_ess1.capital_cost2_year["value"] = 10       #设备更换的年限

        # 蓄电（抽蓄）
        # 目前4*300MW级的电站，一般容量为5-7h电量，2016年的1400MW宁海抽蓄动态79亿元（建设期7-8年，经营期30年），大约5600元/kW，其中机电及金属结构设备安装26%、建筑26%、施工辅助工程+环保水土7%、征地+移民补偿5%、独立费用（建设、设计）15%、预备+价差10%、建设期利息11%。）
        # 因此，取0.46元/Wh、2.80元/W。
        # 综合效率取80%左右，因此充放电效率分别取90%、90%
        t_ess2 = Energy_Storage(t_sys, "php",
                                in_p_charge_nom_extendable=True,
                                in_p_discharge_nom_extendable=True,
                                in_e_nom_extendable=True,
                                in_p_charge_nom=0.0668*10**8,      # 2030年左右全国抽蓄规划将达到约1.2亿kW
                                in_p_discharge_nom=0.0668*10**8,
                                in_e_nom=0.0668*6*10**8,
                                in_charge_effi=0.9,
                                in_discharge_effi=0.9
                                )
        t_ess2.charge.marginal_cost["value"] = 0.0      # 考虑充电的电量边际成本为市电边际成本
        t_ess2.discharge.marginal_cost["value"] = -0.0   # 考虑放电的电量边际成本为市电边际成本
        # t_ess2.discharge_marginal_cost["value"] = -1.5   # 考虑放电的电量边际成本为市电边际成本
        t_ess2.charge.capital_cost["value"] = 1.4
        t_ess2.discharge.capital_cost["value"] = 1.4
        t_ess2.capital_cost_e["value"] = 0.46
        # t_ess2.capital_cost_p2["value"] = 0.4    #设备换新的成本
        # t_ess2.capital_cost_e2["value"] = 1.0    #设备换新的成本
        # t_ess2.capital_cost2_year["value"] = 10       #设备更换的年限

        # 氢储能（p_charge_nom != p_discharge）
        t_ess3 = Energy_Storage(t_sys, "hes",
                                in_p_charge_nom_extendable=True,        # p_charge_nom为电解制氢容量
                                in_p_discharge_nom_extendable=True,     # p_discharge_nom为氢燃机容量，实际即为天然气机组容量
                                in_e_nom_extendable=True,               # e_nom为地下盐穴储氢容量
                                in_p_equal=False,                       # 这个参数很重要，即制氢功率和发电功率可以不相等
                                in_charge_effi=0.8,                     # 充电效率，即制氢效率
                                in_discharge_effi=0.6                   # 放电效率，即氢燃机联合循环发电效率（燃料电池效率更低一些）
                                )
        t_ess3.charge.marginal_cost["value"] = 0.0          # 考虑充电的电量边际成本为市电边际成本
        t_ess3.discharge.marginal_cost["value"] = -0.0      # 考虑放电的电量边际成本为市电边际成本
        # t_ess3.discharge_marginal_cost["value"] = -1.5    # 考虑放电的电量边际成本为市电边际成本
        t_ess3.charge.capital_cost["value"] = 2.24    # 制氢造价参考盈德气体（上海）有限公司新能源研究发展总监的文献，即0.8万元/Nm3，折算后约2.2元/W。如果浙江包括2000km左右的氢管网，造价要增加240亿左右，单价看情况增加到3.0或者多少
        t_ess3.discharge.capital_cost["value"] = 2.2  # 燃机造价，斯林军2021.12.24：9f目前3元/W不到、9h目前2.2元/W
        t_ess3.capital_cost_e["value"] = 0.003          # 这里采用地下盐穴储氢系统，成本为电池储能容量单价的百分之一
        # t_ess3.capital_cost_p2["value"] = 0.4    #设备换新的成本
        # t_ess3.capital_cost_e2["value"] = 1.0    #设备换新的成本
        # t_ess3.capital_cost2_year["value"] = 10       #设备更换的年限

        t_gas1 = Plant(t_sys, "gas", in_p_nom=0.1496*10**8, in_p_nom_extendable=False)  # 2020年全国气电约0.9-1.0亿kW
        # t_gas1 = Plant(t_sys, "gas", in_p_nom=0.1496*10**8, in_p_nom_extendable=True)  # 2020年全国气电约0.9-1.0亿kW
        t_gas1.capital_cost["value"]=2.2
        t_gas1.marginal_cost["value"]=0.3

        # t_coal1 = Plant(t_sys, "coal", in_p_nom=0.2744*10**8, in_p_nom_extendable=False, in_max_pu=1.0, in_min_pu=0.3)
        t_coal1 = Plant(t_sys, "coal", in_p_nom=0.1000*10**8, in_p_nom_extendable=False, in_max_pu=1.0, in_min_pu=0.3)
        # t_coal1 = Plant(t_sys, "coal", in_p_nom=0.0000*10**8, in_p_nom_extendable=False, in_max_pu=1.0, in_min_pu=0.3)
        t_coal1.capital_cost["value"]=4.0
        t_coal1.marginal_cost["value"]=0.2

        # 省际受入43950MW、华东供省内7390MW，所有类型机组的加权小时数为4694h。这里，由于协议性较强，采用水电模型控发电量，边际成本为0.
        t_hydro1 = Hydro_Plant(t_sys, "swap", in_hours_nom=4694, in_p_nom=0.5134*10**8, in_p_nom_extendable=False)       #
        t_hydro1.capital_cost["value"]=10.0
        t_hydro1.marginal_cost["value"]=0.0

        # 生物质3000MW，所有类型机组的加权小时数为5500h，因此，最小出力暂按0.5考虑
        t_coal3 = Plant(t_sys, "bio", in_p_nom=0.0300*10**8, in_p_nom_extendable=False, in_max_pu=1.0, in_min_pu=0.5)
        t_coal3.capital_cost["value"]=4.0
        t_coal3.marginal_cost["value"]=0.2      #暂用煤电的成本

        # 核电，增加plant最大出力和最小出力pu的控制。核电燃料棒过期后必须更换，因此压出力并不能降低核电燃料成本。丁晓宇说技术调峰能力甚至可能到50%
        t_nuc1 = Plant(t_sys, "nuclear", in_p_nom=0.3741*10**8, in_p_nom_extendable=False, in_max_pu=1.0, in_min_pu=0.9)    #
        t_nuc1.capital_cost["value"]=12.0
        t_nuc1.marginal_cost["value"]=0.06

        t_hydro2 = Hydro_Plant(t_sys, "hydro1", in_hours_nom=2300, in_p_nom=0.0730*10**8, in_p_nom_extendable=False)       #
        t_hydro2.capital_cost["value"]=10.0
        t_hydro2.marginal_cost["value"]=0.0

        # 吸收松弛节点
        t_slack_node1 = Absorption_Slack_Node(
            t_sys,
            in_name_id="sl_absorp",
            in_p_max=0.8*10**8,
            # in_p_max=10*10**8,
            in_e_max=0.8*2*10**11 * t_simu_years, # 考虑10%新能源发电量可以上送；全年最大吸收电量 kWh (全年新能源发电量为1.985亿kWh）
            # in_e_max=10*10**11,               # 考虑10%新能源发电量可以上送；全年最大吸收电量 kWh (全年新能源发电量为1.985亿kWh）
            in_marginal_cost=-0.0)              # 考虑上送电量没有成本
        t_slack_node1.e_output = True

        # 注入松弛节点
        t_slack_node2 = Injection_Slack_Node(
            t_sys,
            in_name_id="sl_inject",
            in_p_max=0*10**8,
            # in_p_max=1*140000*0.9,
            in_e_max=0*10**11 * t_simu_years,   # 全年最大注入电量 kWh  (全年负荷为3.3亿kWh，新能源全电量消纳后电量缺口为1.33亿kWh）
            # in_e_max=1*4.0*10**8,             # 全年最大注入电量 kWh  (全年负荷为3.3亿kWh，新能源全电量消纳后电量缺口为1.33亿kWh）
            in_marginal_cost=0.0)
        t_slack_node2.e_output = True

        # =========================节点1=========================
        # t_sys.Add_Bus()
        # t_link1 = Link_Base(t_sys, in_bus1_id=0, in_bus2_id=1, in_name="lk1")
        # t_p2g = Oneway_Link(t_sys, in_bus1_id=0, in_bus2_id=1, in_name="p2g1", in_effi=1.00)

        # t_load2 = Load(in_sys=t_sys, in_name_id="load2", in_hours=t_simu_hours)
        # t_load2.one_year_load_list = list(np.array(t_file.get_list("8760数据2")) * (-1000))    #负荷数据的正负一定要搞清楚，对结果影响非常大

        t_sys.do_optimize()

        # 测试e_list是否有负值
        # for i in range(len(t_ess1._var_list_values("e_list"))):
        #     if t_ess1._var_list_values("e_list")[i]<0:
        #         print("{}th: {}".format(i, t_ess1._var_list_values("e_list")[i]))

    def case31(self, in_called, in_path):
        print("--------------------案例\"{}\"为浙江华电衢州风光水储多能互补方案研究 724MW--------------------".format(Get_Current_Func_Name()))
        if in_called==False:
            return

        # t_simu_hours = 24
        # t_simu_hours = 720
        # t_simu_hours = 24*365
        # t_simu_hours = 24*365*10
        t_simu_hours = 24*365*20

        t_simu_years = t_simu_hours//8760

        # =========================节点0=========================
        t_sys = Sys(
            in_share_y=True,
            in_name_id="sys1",
            in_simu_hours=t_simu_hours,
            in_rate=0.08,
            in_investor="government",
            # in_spring_festival=Spring_Festival(in_bypass=False, in_start_day=10, in_stop_day=60)
            in_spring_festival=Spring_Festival(in_years=t_simu_years, in_bypass=False, in_start_day=10, in_stop_day=60),
            in_analysis_day_list=[0,90,180,270]
            # in_analysis_day_list=0
        )

        # 直接读取8760h标幺值数据==========
        t_file = XLS_File('xls/data_analysis_hd.xlsx', in_cols=[0,1,2,3,4])

        t_load1 = Load(in_sys=t_sys, in_name_id="load", in_p_nom=0) # kW
        t_load1.set_one_year_p()   # 设定p_nom为0的恒定负荷，这里因为是校核新能源对送出通道的影响，还不涉及负荷，因此负荷设置为0。负荷数据的正负一定要搞清楚，对结果影响非常大

        # t_pv1 = NE_Plant(in_sys=t_sys, in_name_id="pv", in_p_nom=345000, in_p_nom_extendable=False)   # kW
        t_pv1 = NE_Plant(in_sys=t_sys, in_name_id="pv", in_p_nom=680000, in_p_nom_extendable=False)   # kW  测算了345MW-800MW之间的光伏，630MW光伏需要新建储能，620MW不需要
        # t_pv1.marginal_cost["value"]=0.0
        # t_pv1.capital_cost["value"]=1.78     # IEA 2050 中国造价
        t_pv1.set_one_year_p(t_file.get_list("光伏"), in_is_pu=True)   #光伏数据，实际只需要特性

        t_wind1 = NE_Plant(in_sys=t_sys, in_name_id="wind", in_p_nom=68000, in_p_nom_extendable=False) # kW
        # t_wind1.marginal_cost["value"]=0.0
        # t_wind1.capital_cost["value"]=6.367      # IEA 2050 中国造价
        t_wind1.set_one_year_p(t_file.get_list("风电"), in_is_pu=True)   #光伏数据，实际只需要特性

        # 蓄电（电池储能）
        # 目前大型储能电站，2020年的萧电储能系统100MW*2h
        # 静态投资约5.86亿元（经营期15年），储能单元及安装54.0%、特殊项目费用（第一期和第二期的电池更换）19.4%、PCS系统11.15%（由于是考虑功率成本，因此含PCS 5.27%、主变1.24%（220kV主变可能不计列钱，即仅计及35kV变压器）、配电4.64%）、其他设施和工程（控制保护2%、电缆接地3%、集装箱基础1%、其他6%）12%，其他费用2%、预备费2%
        # 动态投资约5.46亿元，其中第一期和第二期电池更换费用折现共计-0.48亿元。
        # 因此，按电池和pcs的造价比例73.4:11.15，取2.54元/Wh、0.38元/W。（注意：如果考虑储能生命周期过短，可以把电池储能的Wh和W成本提高一倍或一定倍数考虑）
        # 注：计算中，按照2025年水平，价格均按50%计，取1.38元/Wh、0.24元/W（本项目不计220kV主变，后续项目最好考虑110kV及以下接入或220主变免费，即kW造价按0.4-0.5元/W左右（含pcs、35kV升压变、配电、110kV升压变，比较合理）
        # 综合效率取90%左右，因此充放电效率分别取95%、95%
        t_ess1 = Energy_Storage(t_sys, "bes",
                                in_p_charge_nom_extendable=True,
                                in_p_discharge_nom_extendable=True,
                                in_e_nom_extendable=True,
                                in_charge_effi=0.95,
                                in_discharge_effi=0.95
                                )
        t_ess1.charge.marginal_cost["value"] = -0.5      # 考虑0.5元/kWh，储能1kWh损耗0.1kWh
        t_ess1.discharge.marginal_cost["value"] = -0.5
        # t_ess1.discharge_marginal_cost["value"] = -1.5
        t_ess1.charge.capital_cost["value"] = 0.12
        t_ess1.discharge.capital_cost["value"] = 0.12
        t_ess1.capital_cost_e["value"] = 1.38
        # t_ess1.capital_cost_p2["value"] = 0.4    #设备换新的成本
        # t_ess1.capital_cost_e2["value"] = 1.0    #设备换新的成本
        # t_ess1.capital_cost2_year["value"] = 10       #设备更换的年限

        # 蓄电（抽蓄）
        # 目前4*300MW级的电站，一般容量为5-7h电量，2016年的1400MW宁海抽蓄动态79亿元（建设期7-8年，经营期30年），大约5600元/kW，其中机电及金属结构设备安装26%、建筑26%、施工辅助工程+环保水土7%、征地+移民补偿5%、独立费用（建设、设计）15%、预备+价差10%、建设期利息11%。）
        # 因此，取0.46元/Wh、2.80元/W。
        # 综合效率取80%左右，因此充放电效率分别取90%、90%
        # t_ess2 = Energy_Storage(t_sys, "php",
        #                         in_p_charge_nom_extendable=True,
        #                         in_p_discharge_nom_extendable=True,
        #                         in_e_nom_extendable=True,
        #                         in_p_charge_nom=0,      # kW
        #                         in_p_discharge_nom=0,
        #                         in_e_nom=0,
        #                         in_charge_effi=0.9,
        #                         in_discharge_effi=0.9
        #                         )
        t_ess2 = Energy_Storage(t_sys, "php",
                                in_p_charge_nom_extendable=False,
                                in_p_discharge_nom_extendable=False,
                                in_e_nom_extendable=False,
                                in_p_charge_nom=298000,      # kW
                                in_p_discharge_nom=298000,
                                in_e_nom=298000*4,
                                in_charge_effi=0.9,
                                in_discharge_effi=0.9
                                )
        t_ess2.charge.marginal_cost["value"] = -0.5      # 考虑0.5元/kWh，储能1kWh损耗0.1kWh
        t_ess2.discharge.marginal_cost["value"] = -0.5
        # t_ess2.discharge_marginal_cost["value"] = -1.5
        t_ess2.charge.capital_cost["value"] = 1.4
        t_ess2.discharge.capital_cost["value"] = 1.4
        t_ess2.capital_cost_e["value"] = 0.46
        # t_ess2.capital_cost_p2["value"] = 0.4    #设备换新的成本
        # t_ess2.capital_cost_e2["value"] = 1.0    #设备换新的成本
        # t_ess2.capital_cost2_year["value"] = 10       #设备更换的年限

        # 氢储能（p_charge_nom != p_discharge）
        t_ess3 = Energy_Storage(t_sys, "hes",
                                in_p_charge_nom_extendable=True,        # p_charge_nom为电解制氢容量
                                in_p_discharge_nom_extendable=True,     # p_discharge_nom为氢燃机容量，实际即为天然气机组容量
                                in_e_nom_extendable=True,               # e_nom为地下盐穴储氢容量
                                in_p_equal=False,                       # 这个参数很重要，即制氢功率和发电功率可以不相等
                                in_charge_effi=0.8,                     # 充电效率，即制氢效率
                                in_discharge_effi=0.6                   # 放电效率，即氢燃机联合循环发电效率（燃料电池效率更低一些）
                                )
        t_ess3.charge.marginal_cost["value"] = -0.5       # 考虑0.5元/kWh，储能1kWh损耗0.1kWh
        t_ess3.discharge.marginal_cost["value"] = -0.5
        # t_ess3.discharge_marginal_cost["value"] = -1.5
        t_ess3.charge.capital_cost["value"] = 2.24    # 制氢造价参考盈德气体（上海）有限公司新能源研究发展总监的文献，即0.8万元/Nm3，折算后约2.2元/W。如果浙江包括2000km左右的氢管网，造价要增加240亿左右，单价看情况增加到3.0或者多少
        t_ess3.discharge.capital_cost["value"] = 2.2  # 燃机造价，斯林军2021.12.24：9f目前3元/W不到、9h目前2.2元/W
        t_ess3.capital_cost_e["value"] = 0.003          # 这里采用地下盐穴储氢系统，成本为电池储能容量单价的百分之一
        # t_ess3.capital_cost_p2["value"] = 0.4    #设备换新的成本
        # t_ess3.capital_cost_e2["value"] = 1.0    #设备换新的成本
        # t_ess3.capital_cost2_year["value"] = 10       #设备更换的年限

        t_hydro1 = NE_Plant(in_sys=t_sys, in_name_id="hydro1", in_p_nom=342000, in_p_nom_extendable=False) # kW
        t_hydro1.set_one_year_p(t_file.get_list("水电"), in_is_pu=True)   #光伏数据，实际只需要特性

        # t_hydro1 = Hydro_Plant(t_sys, "hydro1", in_hours_nom=2000, in_p_nom=400000, in_p_nom_extendable=False)       # kW
        # t_hydro1.capital_cost["value"]=10.0
        # t_hydro1.marginal_cost["value"]=0.0

        # 吸收松弛节点
        t_slack_node1 = Absorption_Slack_Node(
            t_sys,
            in_name_id="sl_absorp",
            in_p_max=724000,    # kW
            in_e_max=724000*8760 * t_simu_years,    # 这里配合负荷为0，设置了700MW的功率限额
            in_marginal_cost=-0.0)                  # 考虑上送电量没有成本
        t_slack_node1.e_output = True

        # 注入松弛节点
        t_slack_node2 = Injection_Slack_Node(
            t_sys,
            in_name_id="sl_inject",
            in_p_max=0,
            in_e_max=0*8760 * t_simu_years,
            # in_p_max=350000,
            # in_e_max=350000*8760 * t_simu_years,
            in_marginal_cost=0.0)                   # 考虑注入电量没有成本
        t_slack_node2.e_output = True

        t_sys.do_optimize()

    def case32(self, in_called, in_path="xls/"):
        print("--------------------案例\"{}\"为浙江华电衢州风光水储多能互补方案研究 2*724MW--------------------".format(Get_Current_Func_Name()))
        if in_called==False:
            return

        t_simu_hours = 24
        # t_simu_hours = 720
        # t_simu_hours = 24*365
        # t_simu_hours = 24*365*10
        # t_simu_hours = 24*365*20

        t_simu_years = t_simu_hours//8760

        # =========================节点0=========================
        t_sys = Sys(
            in_share_y=True,
            in_name_id="sys1",
            in_simu_hours=t_simu_hours,
            in_rate=0.08,
            in_investor="government",
            # in_spring_festival=Spring_Festival(in_bypass=False, in_start_day=10, in_stop_day=60)
            in_spring_festival=Spring_Festival(in_years=t_simu_years, in_bypass=False, in_start_day=10, in_stop_day=60),
            in_analysis_day_list=[0,90,180,270]
            # in_analysis_day_list=0
        )
        t_sys.Add_Bus()

        # 直接读取8760h标幺值数据==========
        t_file = XLS_File(in_path+'data_analysis_hd.xlsx', in_cols=[0,1,2,3,4])

        t_load1 = Load(in_sys=t_sys, in_name_id="load", in_p_nom=0) # kW
        t_load1.set_one_year_p()   # 设定p_nom为0的恒定负荷，这里因为是校核新能源对送出通道的影响，还不涉及负荷，因此负荷设置为0。负荷数据的正负一定要搞清楚，对结果影响非常大

        # t_pv1 = NE_Plant(in_sys=t_sys, in_name_id="pv", in_p_nom=345000, in_p_nom_extendable=False)   # kW
        # t_pv1 = NE_Plant(in_sys=t_sys, in_name_id="pv", in_p_nom=0, in_p_nom_extendable=True)   # kW  测算了345MW-800MW之间的光伏，630MW光伏需要新建储能，620MW不需要
        t_pv1 = NE_Plant(in_sys=t_sys, in_name_id="pv", in_p_nom=30000+680000+724000, in_p_nom_extendable=False)   # kW  测算了345MW-800MW之间的光伏，630MW光伏需要新建储能，620MW不需要
        # t_pv1.marginal_cost["value"]=0.0
        # t_pv1.capital_cost["value"]=1.78     # IEA 2050 中国造价
        t_pv1.set_one_year_p(t_file.get_list("光伏"), in_is_pu=True)   #光伏数据，实际只需要特性

        t_wind1 = NE_Plant(in_sys=t_sys, in_name_id="wind", in_p_nom=68000, in_p_nom_extendable=False) # kW
        # t_wind1.marginal_cost["value"]=0.0
        # t_wind1.capital_cost["value"]=6.367      # IEA 2050 中国造价
        t_wind1.set_one_year_p(t_file.get_list("风电"), in_is_pu=True)   #光伏数据，实际只需要特性

        # 蓄电（电池储能）
        # 目前大型储能电站，2020年的萧电储能系统100MW*2h
        # 静态投资约5.86亿元（经营期15年），储能单元及安装54.0%、特殊项目费用（第一期和第二期的电池更换）19.4%、PCS系统11.15%（由于是考虑功率成本，因此含PCS 5.27%、主变1.24%（220kV主变可能不计列钱，即仅计及35kV变压器）、配电4.64%）、其他设施和工程（控制保护2%、电缆接地3%、集装箱基础1%、其他6%）12%，其他费用2%、预备费2%
        # 动态投资约5.46亿元，其中第一期和第二期电池更换费用折现共计-0.48亿元。
        # 因此，按电池和pcs的造价比例73.4:11.15，取2.54元/Wh、0.38元/W。（注意：如果考虑储能生命周期过短，可以把电池储能的Wh和W成本提高一倍或一定倍数考虑）
        # 注：计算中，按照2025年水平，价格均按50%计，取1.38元/Wh、0.24元/W（本项目不计220kV主变，后续项目最好考虑110kV及以下接入或220主变免费，即kW造价按0.4-0.5元/W左右（含pcs、35kV升压变、配电、110kV升压变，比较合理）
        # 综合效率取90%左右，因此充放电效率分别取95%、95%
        t_ess1 = Energy_Storage(t_sys, "bes",
                                in_p_charge_nom_extendable=True,
                                in_p_discharge_nom_extendable=True,
                                in_e_nom_extendable=True,
                                in_charge_effi=0.95,
                                in_discharge_effi=0.95
                                )
        t_ess1.charge.marginal_cost["value"] = -0.5      # 考虑0.5元/kWh，储能1kWh损耗0.1kWh
        t_ess1.discharge.marginal_cost["value"] = -0.5
        # t_ess1.discharge_marginal_cost["value"] = -1.5
        t_ess1.charge.capital_cost["value"] = 0.12
        t_ess1.discharge.capital_cost["value"] = 0.12
        t_ess1.capital_cost_e["value"] = 1.38
        # t_ess1.capital_cost_p2["value"] = 0.4    #设备换新的成本
        # t_ess1.capital_cost_e2["value"] = 1.0    #设备换新的成本
        # t_ess1.capital_cost2_year["value"] = 10       #设备更换的年限

        # 蓄电（抽蓄）
        # 目前4*300MW级的电站，一般容量为5-7h电量，2016年的1400MW宁海抽蓄动态79亿元（建设期7-8年，经营期30年），大约5600元/kW，其中机电及金属结构设备安装26%、建筑26%、施工辅助工程+环保水土7%、征地+移民补偿5%、独立费用（建设、设计）15%、预备+价差10%、建设期利息11%。）
        # 因此，取0.46元/Wh、2.80元/W。
        # 综合效率取80%左右，因此充放电效率分别取90%、90%
        # t_ess2 = Energy_Storage(t_sys, "php",
        #                         in_p_charge_nom_extendable=True,
        #                         in_p_discharge_nom_extendable=True,
        #                         in_e_nom_extendable=True,
        #                         in_p_charge_nom=0,      # kW
        #                         in_p_discharge_nom=0,
        #                         in_e_nom=0,
        #                         in_charge_effi=0.9,
        #                         in_discharge_effi=0.9
        #                         )
        t_ess2 = Energy_Storage(t_sys, "php",
                                in_p_charge_nom_extendable=False,
                                in_p_discharge_nom_extendable=False,
                                in_e_nom_extendable=False,
                                in_p_charge_nom=298000,      # kW
                                in_p_discharge_nom=298000,
                                in_e_nom=298000*4,
                                in_charge_effi=0.9,
                                in_discharge_effi=0.9
                                )
        t_ess2.charge.marginal_cost["value"] = -0.5      # 考虑0.5元/kWh，储能1kWh损耗0.1kWh
        t_ess2.discharge.marginal_cost["value"] = -0.5
        # t_ess2.discharge_marginal_cost["value"] = -1.5
        t_ess2.charge.capital_cost["value"] = 1.4
        t_ess2.discharge.capital_cost["value"] = 1.4
        t_ess2.capital_cost_e["value"] = 0.46
        # t_ess2.capital_cost_p2["value"] = 0.4    #设备换新的成本
        # t_ess2.capital_cost_e2["value"] = 1.0    #设备换新的成本
        # t_ess2.capital_cost2_year["value"] = 10       #设备更换的年限

        # 氢储能（p_charge_nom != p_discharge）
        t_ess3 = Energy_Storage(t_sys, "hes",
                                in_p_charge_nom_extendable=True,        # p_charge_nom为电解制氢容量
                                in_p_discharge_nom_extendable=True,     # p_discharge_nom为氢燃机容量，实际即为天然气机组容量
                                in_e_nom_extendable=True,               # e_nom为地下盐穴储氢容量
                                in_p_equal=False,                       # 这个参数很重要，即制氢功率和发电功率可以不相等
                                in_charge_effi=0.8,                     # 充电效率，即制氢效率
                                in_discharge_effi=0.6                   # 放电效率，即氢燃机联合循环发电效率（燃料电池效率更低一些）
                                )
        t_ess3.charge.marginal_cost["value"] = -0.5       # 考虑0.5元/kWh，储能1kWh损耗0.1kWh
        t_ess3.discharge.marginal_cost["value"] = -0.5
        # t_ess3.discharge_marginal_cost["value"] = -1.5
        t_ess3.charge.capital_cost["value"] = 2.24    # 制氢造价参考盈德气体（上海）有限公司新能源研究发展总监的文献，即0.8万元/Nm3，折算后约2.2元/W。如果浙江包括2000km左右的氢管网，造价要增加240亿左右，单价看情况增加到3.0或者多少
        t_ess3.discharge.capital_cost["value"] = 2.2  # 燃机造价，斯林军2021.12.24：9f目前3元/W不到、9h目前2.2元/W
        t_ess3.capital_cost_e["value"] = 0.003          # 这里采用地下盐穴储氢系统，成本为电池储能容量单价的百分之一
        # t_ess3.capital_cost_p2["value"] = 0.4    #设备换新的成本
        # t_ess3.capital_cost_e2["value"] = 1.0    #设备换新的成本
        # t_ess3.capital_cost2_year["value"] = 10       #设备更换的年限

        t_hydro1 = NE_Plant(in_sys=t_sys, in_name_id="hydro1", in_p_nom=342000, in_p_nom_extendable=False) # kW
        t_hydro1.set_one_year_p(t_file.get_list("水电"), in_is_pu=True)   #光伏数据，实际只需要特性

        # t_hydro1 = Hydro_Plant(t_sys, "hydro1", in_hours_nom=2000, in_p_nom=400000, in_p_nom_extendable=False)       # kW
        # t_hydro1.capital_cost["value"]=10.0
        # t_hydro1.marginal_cost["value"]=0.0

        # 吸收松弛节点
        t_slack_node1 = Absorption_Slack_Node(
            t_sys,
            in_name_id="sl_absorp",
            in_p_max=2*724000,    # kW
            in_e_max=2*724000*8760 * t_simu_years,    # 这里配合负荷为0，设置了700MW的功率限额
            in_marginal_cost=-0.0)                  # 考虑上送电量没有成本
        t_slack_node1.e_output = True

        # 注入松弛节点
        t_slack_node2 = Injection_Slack_Node(
            t_sys,
            in_name_id="sl_inject",
            in_p_max=0,
            in_e_max=0*8760 * t_simu_years,
            # in_p_max=350000,
            # in_e_max=350000*8760 * t_simu_years,
            in_marginal_cost=0.0)                   # 考虑注入电量没有成本
        t_slack_node2.e_output = True

        t_sys.do_optimize()

    def case4(self, in_called, in_path, in_lambda=0):
        print("--------------------案例\"{}\"为杭州泛亚运碳电协同微电网群方案研究--------------------".format(Get_Current_Func_Name()))
        if in_called==False:
            return

        # t_simu_hours = 24
        # t_simu_hours = 720
        # t_simu_hours = 24*365
        # t_simu_hours = 24*365*2
        t_simu_hours = 24*365*8
        # t_simu_hours = 24*365*10
        # t_simu_hours = 24*365*20

        t_simu_years = t_simu_hours//8760
        if t_simu_years<1 :
            t_simu_years = 1
        print("t_simu_years is : ", t_simu_years)

        # =========================节点0=========================
        t_sys = Sys(
            in_share_y=True,
            in_name_id="sys1",
            in_simu_hours=t_simu_hours,
            in_rate=0.08,
            # in_spring_festival=Spring_Festival(in_bypass=False, in_start_day=10, in_stop_day=60)
            in_spring_festival=Spring_Festival(in_years=t_simu_years, in_bypass=False, in_start_day=10, in_stop_day=60),
            # in_investor="government", # 本案例为用户财务测算
            in_investor="user_finance", # 本案例为用户财务测算
            in_investor_user_discount=0.1,
            in_analysis_day_list=[0,90,180,270]
            # in_analysis_day_list=0
        )

        # ===IEA 2050 NZE 解读===\用户侧储能测算及分时电价\（分时电价表格）国网浙江省电力有限公司关于2022年6月代理工商业用户购电价格的公告.pdf
        # 大工业用户1-10kV、1.0倍
        t_peak =1.2757
        t_high =1.0655
        t_low =0.3407
        t_sys.tariff_list = [
            t_low , t_low , t_low , t_low , t_low , t_low ,
            t_low , t_low , t_high, t_peak, t_peak, t_high,
            t_high, t_low , t_low , t_peak, t_peak, t_high,
            t_high, t_high, t_high, t_high, t_low , t_low ]


        t_sys.pic_output = True

        # min(生命周期净利润/初期投资)中，利润为负数，投资为正数。最优lambda也为负数，如最优lambda=-1.5，表明利润/投资的最大值为1.5
        # 改变fp_lambda的值，直到目标函数由负数无限接近0时，此时fp_lambda值即为原目标函数最优值
        t_sys.fp_lambda = in_lambda
        # t_sys.fp_lambda = -1.85
        t_sys.Add_Bus()

        # t_sys.print_objfunc = True

        # 直接读取8760h标幺值数据==========
        t_file = XLS_File('static/xls/data_analysis_xs.xlsx', in_cols=[0,1,2,3])

        # t_load1 = Load(in_sys=t_sys, in_name_id="load", in_p_nom=2033) # kW
        # t_load1.set_one_year_p(t_file.get_list("欣美"))   #负荷数据的正负一定要搞清楚，对结果影响非常大
        t_load1 = Load(in_sys=t_sys, in_name_id="load", in_p_nom=2526) # kW
        t_load1.set_one_year_p(t_file.get_list("杭可"))   #负荷数据的正负一定要搞清楚，对结果影响非常大
        # t_load1 = Load(in_sys=t_sys, in_name_id="load", in_p_nom=3042) # kW
        # t_load1.set_one_year_p(t_file.get_list("友成"))   #负荷数据的正负一定要搞清楚，对结果影响非常大

        # 欣美的负荷数据中已经含了光伏出力
        # t_pv1 = NE_Plant(in_sys=t_sys, in_name_id="pv", in_p_nom=195000, in_p_nom_extendable=False)   # kW
        # # t_pv1.marginal_cost["value"]=0.0
        # # t_pv1.capital_cost["value"]=1.78     # IEA 2050 中国造价
        # t_pv1.set_one_year_p(t_file.get_list("光伏"), in_is_pu=True)   #光伏数据，实际只需要特性

        # 蓄电（电池储能）
        # 目前大型储能电站，2020年的萧电储能系统100MW*2h
        # 静态投资约5.86亿元（经营期15年），储能单元及安装54.0%、特殊项目费用（第一期和第二期的电池更换）19.4%、PCS系统11.15%（由于是考虑功率成本，因此含PCS 5.27%、主变1.24%（220kV主变可能不计列钱，即仅计及35kV变压器）、配电4.64%）、其他设施和工程（控制保护2%、电缆接地3%、集装箱基础1%、其他6%）12%，其他费用2%、预备费2%
        # 动态投资约5.46亿元，其中第一期和第二期电池更换费用折现共计-0.48亿元。
        # 因此，按电池和pcs的造价比例73.4:11.15，取2.54元/Wh、0.38元/W。（注意：如果考虑储能生命周期过短，可以把电池储能的Wh和W成本提高一倍或一定倍数考虑）
        # 注：计算中，按照2025年水平，价格均按50%计，取1.38元/Wh、0.24元/W（本项目不计220kV主变，后续项目最好考虑110kV及以下接入或220主变免费，即kW造价按0.4-0.5元/W左右（含pcs、35kV升压变、配电、110kV升压变，比较合理）
        # 综合效率取90%左右，因此充放电效率分别取95%、95%

        t_ess1 = Energy_Storage(t_sys, "bes",
                                in_p_charge_nom_extendable=True,
                                in_p_discharge_nom_extendable=True,
                                in_e_nom_extendable=True,
                                in_charge_effi=0.95,
                                in_discharge_effi=0.95
                                )
        # t_ess1.charge_marginal_cost["value"] = 0.0          # 计算社会效益时，储能与用户转移支付，成本为0
        # t_ess1.discharge_marginal_cost["value"] = -0.0      # 计算社会效益时，储能与用户转移支付，成本为0
        t_ess1.charge.marginal_cost["value"] = 0.0          # 计算财务效益时，采用内部的用户电价price_list，marginal_cost即燃料成本为0
        t_ess1.discharge.marginal_cost["value"] = -0.0      # 计算财务效益时，采用内部的用户电价price_list，marginal_cost即燃料成本为0
        t_ess1.charge.capital_cost["value"] = 0.12
        t_ess1.discharge.capital_cost["value"] = 0.12
        t_ess1.capital_cost_e["value"] = 1.38

        # t_ess1.capital_cost_p2["value"] = 0.4    #设备换新的成本
        # t_ess1.capital_cost_e2["value"] = 1.0    #设备换新的成本
        # t_ess1.capital_cost2_year["value"] = 10       #设备更换的年限

        # 财务效益
        # t_sub1 = Plant(t_sys, "sub1", in_p_nom=3250, in_p_nom_extendable=False)

        # 社会效益
        # t_sub1 = Plant(t_sys, "sub1", in_p_nom=1600, in_p_nom_extendable=True)
        # t_sub1.capital_cost["value"]=5.0
        # t_sub1.marginal_cost["value"]=0.45+0.2

        # t_sub2 = Plant(t_sys, "sub2", in_p_nom_extendable=True)
        # t_sub2.capital_cost["value"]=5.0
        # t_sub2.marginal_cost["value"]=0.45+0.2

        # ===slack节点仅用作强制的、无成本的功率调节===（有成本的用plant模拟）
        # 吸收松弛节点
        t_slack_node1 = Absorption_Slack_Node(
            t_sys,
            in_name_id="sl_absorp",
            in_p_max=1500,    # kW
            in_p_nom_extendable=False,
            in_e_max=1500*8760 * t_simu_years,      # 设置了1.5MW的功率限额
            # in_marginal_cost=0)                     # government, 这里必须若考虑新能源倒送成本，则应为负值，即乘以负的功率，成本为正
            in_marginal_cost=-0.0)                     # user_finance，这里必须若考虑新能源倒送成本，则应为负值，即乘以负的功率，成本为正(mc=-0.1,能够有效的防止财务盈利储能在尖峰放电时功率超过负荷)
            # in_marginal_cost=-0.1)                     # user_finance，这里必须若考虑新能源倒送成本，则应为负值，即乘以负的功率，成本为正(mc=-0.1,能够有效的防止财务盈利储能在尖峰放电时功率超过负荷)
        t_slack_node1.e_output = True

        # 注入松弛节点
        t_slack_node2 = Injection_Slack_Node(
            t_sys,
            in_name_id="sl_inject",
            in_p_max=3250,
            in_p_nom_extendable=False,
            in_e_max=3250*8760 * t_simu_years,
            # in_marginal_cost=0)                     # government, 考虑的注入电量影子成本，输配电价暂考虑0.2元/kWh
            in_marginal_cost=0.0)                   # user_finance, 考虑的注入电量成本，计算光伏、储能等项目的财务成本时，用户向电网购电成本应为正值
            # in_marginal_cost=0.3)                   # user_finance, 考虑的注入电量成本，计算光伏、储能等项目的财务成本时，用户向电网购电成本应为正值
        t_slack_node2.e_output = True

        t_sys.do_optimize()

        return value(t_sys.model.OBJ_FUNC)

    def case5(self, in_called, in_path, in_lambda=0):
        print("--------------------案例\"{}\"为2022.7绍兴局用户侧储能研究--------------------".format(Get_Current_Func_Name()))
        if in_called==False:
            return

        # t_simu_hours = 24
        # t_simu_hours = 720
        # t_simu_hours = 24*365
        # t_simu_hours = 24*365*2
        t_simu_hours = 24*365*8
        # t_simu_hours = 24*365*10
        # t_simu_hours = 24*365*20

        t_simu_years = t_simu_hours//8760
        if t_simu_years<1 :
            t_simu_years = 1
        print("t_simu_years is : ", t_simu_years)

        # =========================节点0=========================
        t_sys = Sys(
            in_share_y=True,
            in_name_id="sys1",
            in_simu_hours=t_simu_hours,
            in_rate=0.08,
            # in_spring_festival=Spring_Festival(in_bypass=False, in_start_day=10, in_stop_day=60)
            in_spring_festival=Spring_Festival(in_years=t_simu_years, in_bypass=False, in_start_day=10, in_stop_day=60),
            # in_investor="government", # 本案例为社会效益测算
            in_investor="user_finance", # 本案例为用户财务测算
            in_user_finance_strategy="max_profit",
            # in_user_finance_strategy="max_rate"
            in_investor_user_discount=0.1,
            in_analysis_day_list=[0,90,180,270]
            # in_analysis_day_list=0
        )

        # ===IEA 2050 NZE 解读===\用户侧储能测算及分时电价\（分时电价表格）国网浙江省电力有限公司关于2022年6月代理工商业用户购电价格的公告.pdf
        # 大工业用户1-10kV、1.0倍
        t_peak =1.2757
        t_high =1.0655
        t_low =0.3407
        t_sys.tariff_list = [
            t_low , t_low , t_low , t_low , t_low , t_low ,
            t_low , t_low , t_high, t_peak, t_peak, t_high,
            t_high, t_low , t_low , t_peak, t_peak, t_high,
            t_high, t_high, t_high, t_high, t_low , t_low ]


        t_sys.pic_output = True

        # min(生命周期净利润/初期投资)中，利润为负数，投资为正数。最优lambda也为负数，如最优lambda=-1.5，表明利润/投资的最大值为1.5
        # 改变fp_lambda的值，直到目标函数由负数无限接近0时，此时fp_lambda值即为原目标函数最优值
        t_sys.fp_lambda = in_lambda
        # t_sys.fp_lambda = -1.85
        t_sys.Add_Bus()

        # t_sys.print_objfunc = True

        # 直接读取8760h标幺值数据==========
        t_file = XLS_File('static/xls/shaoxing.xls', in_cols=[0])

        # t_load1 = Load(in_sys=t_sys, in_name_id="load", in_p_nom=2033) # kW
        # t_load1.set_one_year_p(t_file.get_list("欣美"))   #负荷数据的正负一定要搞清楚，对结果影响非常大
        t_load1 = Load(in_sys=t_sys, in_name_id="load", in_p_nom=1436) # kW
        t_load1.set_one_year_p(t_file.get_list("负荷"))   #负荷数据的正负一定要搞清楚，对结果影响非常大
        # t_load1 = Load(in_sys=t_sys, in_name_id="load", in_p_nom=3042) # kW
        # t_load1.set_one_year_p(t_file.get_list("友成"))   #负荷数据的正负一定要搞清楚，对结果影响非常大

        # 欣美的负荷数据中已经含了光伏出力
        # t_pv1 = NE_Plant(in_sys=t_sys, in_name_id="pv", in_p_nom=195000, in_p_nom_extendable=False)   # kW
        # # t_pv1.marginal_cost["value"]=0.0
        # # t_pv1.capital_cost["value"]=1.78     # IEA 2050 中国造价
        # t_pv1.set_one_year_p(t_file.get_list("光伏"), in_is_pu=True)   #光伏数据，实际只需要特性

        # 蓄电（电池储能）
        # 目前大型储能电站，2020年的萧电储能系统100MW*2h
        # 静态投资约5.86亿元（经营期15年），储能单元及安装54.0%、特殊项目费用（第一期和第二期的电池更换）19.4%、PCS系统11.15%（由于是考虑功率成本，因此含PCS 5.27%、主变1.24%（220kV主变可能不计列钱，即仅计及35kV变压器）、配电4.64%）、其他设施和工程（控制保护2%、电缆接地3%、集装箱基础1%、其他6%）12%，其他费用2%、预备费2%
        # 动态投资约5.46亿元，其中第一期和第二期电池更换费用折现共计-0.48亿元。
        # 因此，按电池和pcs的造价比例73.4:11.15，取2.54元/Wh、0.38元/W。（注意：如果考虑储能生命周期过短，可以把电池储能的Wh和W成本提高一倍或一定倍数考虑）
        # 注：计算中，按照2025年水平，价格均按50%计，取1.38元/Wh、0.24元/W（本项目不计220kV主变，后续项目最好考虑110kV及以下接入或220主变免费，即kW造价按0.4-0.5元/W左右（含pcs、35kV升压变、配电、110kV升压变，比较合理）
        # 综合效率取90%左右，因此充放电效率分别取95%、95%

        t_ess1 = Energy_Storage(t_sys, "bes",
                                in_p_charge_nom_extendable=True,
                                in_p_discharge_nom_extendable=True,
                                in_e_nom_extendable=True,
                                in_charge_effi=0.95,
                                in_discharge_effi=0.95
                                )
        # t_ess1.charge_marginal_cost["value"] = 0.0          # 计算社会效益时，储能与用户转移支付，成本为0
        # t_ess1.discharge_marginal_cost["value"] = -0.0      # 计算社会效益时，储能与用户转移支付，成本为0
        t_ess1.charge.marginal_cost["value"] = 0.0          # 计算财务效益时，采用内部的用户电价price_list，marginal_cost即燃料成本为0
        t_ess1.discharge.marginal_cost["value"] = -0.0      # 计算财务效益时，采用内部的用户电价price_list，marginal_cost即燃料成本为0
        t_ess1.charge.capital_cost["value"] = 0.2           # 参照萧电储能（不换电池的造价）
        t_ess1.discharge.capital_cost["value"] = 0.2        # 参照萧电储能（不换电池的造价）
        t_ess1.capital_cost_e["value"] = 1.5                # 参照萧电储能（不换电池的造价）

        # t_ess1.capital_cost_p2["value"] = 0.4    #设备换新的成本
        # t_ess1.capital_cost_e2["value"] = 1.0    #设备换新的成本
        # t_ess1.capital_cost2_year["value"] = 10       #设备更换的年限

        # 财务效益
        # t_sub1 = Plant(t_sys, "sub1", in_p_nom=3250, in_p_nom_extendable=False)

        # 社会效益
        # t_sub1 = Plant(t_sys, "sub1", in_p_nom=1600, in_p_nom_extendable=True)
        # t_sub1.capital_cost["value"]=5.0
        # t_sub1.marginal_cost["value"]=0.45+0.2

        # t_sub2 = Plant(t_sys, "sub2", in_p_nom_extendable=True)
        # t_sub2.capital_cost["value"]=5.0
        # t_sub2.marginal_cost["value"]=0.45+0.2

        # ===slack节点仅用作强制的、无成本的功率调节===（有成本的用plant模拟）
        # 吸收松弛节点
        t_slack_node1 = Absorption_Slack_Node(
            t_sys,
            in_name_id="sl_absorp",
            in_p_max=1800,    # kW
            in_p_nom_extendable=False,
            in_e_max=1800*8760 * t_simu_years,      # 储能放电如果上送，没有钱。若简单化，则可以设置0MW的功率限额
            # in_marginal_cost=0),
            in_marginal_cost=-1.2757 ,              # 设置1.8MW上送，但是边际成本按尖峰电价考虑
            # in_marginal_cost=-0.1)                     # user_finance，这里必须若考虑新能源倒送成本，则应为负值，即乘以负的功率，成本为正(mc=-0.1,能够有效的防止财务盈利储能在尖峰放电时功率超过负荷)
        )
        t_slack_node1.e_output = True

        # 注入松弛节点
        t_slack_node2 = Injection_Slack_Node(
            t_sys,
            in_name_id="sl_inject",
            in_p_max=1800*0.9,                              # 用户配变容量为1800kVA
            in_p_nom_extendable=False,
            in_e_max=1800*0.9*8760 * t_simu_years,
            # in_marginal_cost=0)
            in_marginal_cost=0.0)
            # in_marginal_cost=0.3)
        t_slack_node2.e_output = True

        t_sys.do_optimize()

        return value(t_sys.model.OBJ_FUNC)

    def case6(self, in_called, in_path, in_lambda=0):
        print("--------------------案例\"{}\"为2022.7.15 绍兴局35kV用户侧储能研究--------------------".format(Get_Current_Func_Name()))
        if in_called==False:
            return

        # t_simu_hours = 24
        # t_simu_hours = 720
        t_simu_hours = 24*365
        # t_simu_hours = 24*365*2
        # t_simu_hours = 24*365*8
        # t_simu_hours = 24*365*10
        # t_simu_hours = 24*365*20

        t_simu_years = t_simu_hours//8760
        if t_simu_years<1 :
            t_simu_years = 1
        print("t_simu_years is : ", t_simu_years)

        # =========================节点0=========================
        t_sys = Sys(
            in_share_y=True,
            in_name_id="sys1",
            in_simu_hours=t_simu_hours,
            in_rate=0.08,
            # in_spring_festival=Spring_Festival(in_bypass=False, in_start_day=10, in_stop_day=60)
            in_spring_festival=Spring_Festival(in_years=t_simu_years, in_bypass=False, in_start_day=10, in_stop_day=60),
            # in_investor="government", # 本案例为社会效益测算
            in_investor="user_finance", # 本案例为用户财务测算
            # in_user_finance_strategy="max_profit",
            in_user_finance_strategy="max_rate",
            in_investor_user_discount=0.1,
            in_analysis_day_list=[0,90,180,270]
            # in_analysis_day_list=0
        )

        # ===IEA 2050 NZE 解读===\用户侧储能测算及分时电价\（分时电价表格）国网浙江省电力有限公司关于2022年6月代理工商业用户购电价格的公告.pdf
        # 大工业用户1-10kV、1.0倍
        t_peak =1.2757
        t_high =1.0655
        t_low =0.3407
        t_sys.tariff_list = [
            t_low , t_low , t_low , t_low , t_low , t_low ,
            t_low , t_low , t_high, t_peak, t_peak, t_high,
            t_high, t_low , t_low , t_peak, t_peak, t_high,
            t_high, t_high, t_high, t_high, t_low , t_low ]


        t_sys.pic_output = True

        # min(生命周期净利润/初期投资)中，利润为负数，投资为正数。最优lambda也为负数，如最优lambda=-1.5，表明利润/投资的最大值为1.5
        # 改变fp_lambda的值，直到目标函数由负数无限接近0时，此时fp_lambda值即为原目标函数最优值
        t_sys.fp_lambda = in_lambda
        # t_sys.fp_lambda = -1.85
        t_sys.Add_Bus()

        # t_sys.print_objfunc = True

        # 直接读取8760h标幺值数据==========
        t_file = XLS_File('static/xls/shaoxing-35kV.xls', in_cols=[0, 1], in_row_num=8761)

        # t_load1 = Load(in_sys=t_sys, in_name_id="load", in_p_nom=2033) # kW
        # t_load1.set_one_year_p(t_file.get_list("欣美"))   #负荷数据的正负一定要搞清楚，对结果影响非常大
        t_load1 = Load(in_sys=t_sys, in_name_id="load", in_p_nom=8376.9) # kW
        t_load1.set_one_year_p(t_file.get_list("电负荷"))   #负荷数据的正负一定要搞清楚，对结果影响非常大
        # t_load1 = Load(in_sys=t_sys, in_name_id="load", in_p_nom=3042) # kW
        # t_load1.set_one_year_p(t_file.get_list("友成"))   #负荷数据的正负一定要搞清楚，对结果影响非常大

        # 欣美的负荷数据中已经含了光伏出力
        t_pv1 = NE_Plant(in_sys=t_sys, in_name_id="pv", in_p_nom=9300, in_p_nom_extendable=False)   # kW
        # t_pv1.marginal_cost["value"]=0.0
        # t_pv1.capital_cost["value"]=1.78     # IEA 2050 中国造价
        t_pv1.set_one_year_p(t_file.get_list("光伏"), in_is_pu=True)   #光伏数据，实际只需要特性

        # 蓄电（电池储能）
        # 目前大型储能电站，2020年的萧电储能系统100MW*2h
        # 静态投资约5.86亿元（经营期15年），储能单元及安装54.0%、特殊项目费用（第一期和第二期的电池更换）19.4%、PCS系统11.15%（由于是考虑功率成本，因此含PCS 5.27%、主变1.24%（220kV主变可能不计列钱，即仅计及35kV变压器）、配电4.64%）、其他设施和工程（控制保护2%、电缆接地3%、集装箱基础1%、其他6%）12%，其他费用2%、预备费2%
        # 动态投资约5.46亿元，其中第一期和第二期电池更换费用折现共计-0.48亿元。
        # 因此，按电池和pcs的造价比例73.4:11.15，取2.54元/Wh、0.38元/W。（注意：如果考虑储能生命周期过短，可以把电池储能的Wh和W成本提高一倍或一定倍数考虑）
        # 注：计算中，按照2025年水平，价格均按50%计，取1.38元/Wh、0.24元/W（本项目不计220kV主变，后续项目最好考虑110kV及以下接入或220主变免费，即kW造价按0.4-0.5元/W左右（含pcs、35kV升压变、配电、110kV升压变，比较合理）
        # 综合效率取90%左右，因此充放电效率分别取95%、95%

        t_ess1 = Energy_Storage(t_sys, "bes",
                                in_p_charge_nom_extendable=True,
                                in_p_discharge_nom_extendable=True,
                                in_e_nom_extendable=True,
                                in_charge_effi=0.95,
                                in_discharge_effi=0.95
                                )
        # t_ess1.charge_marginal_cost["value"] = 0.0          # 计算社会效益时，储能与用户转移支付，成本为0
        # t_ess1.discharge_marginal_cost["value"] = -0.0      # 计算社会效益时，储能与用户转移支付，成本为0
        t_ess1.charge.marginal_cost["value"] = 0.0          # 计算财务效益时，采用内部的用户电价price_list，marginal_cost即燃料成本为0
        t_ess1.discharge.marginal_cost["value"] = -0.0      # 计算财务效益时，采用内部的用户电价price_list，marginal_cost即燃料成本为0
        t_ess1.charge.capital_cost["value"] = 0.2           # 参照萧电储能（不换电池的造价）
        t_ess1.discharge.capital_cost["value"] = 0.2        # 参照萧电储能（不换电池的造价）
        t_ess1.capital_cost_e["value"] = 1.5                # 参照萧电储能（不换电池的造价）

        # t_ess1.capital_cost_p2["value"] = 0.4    #设备换新的成本
        # t_ess1.capital_cost_e2["value"] = 1.0    #设备换新的成本
        # t_ess1.capital_cost2_year["value"] = 10       #设备更换的年限

        # 财务效益
        # t_sub1 = Plant(t_sys, "sub1", in_p_nom=3250, in_p_nom_extendable=False)

        # 社会效益
        # t_sub1 = Plant(t_sys, "sub1", in_p_nom=1600, in_p_nom_extendable=True)
        # t_sub1.capital_cost["value"]=5.0
        # t_sub1.marginal_cost["value"]=0.45+0.2

        # t_sub2 = Plant(t_sys, "sub2", in_p_nom_extendable=True)
        # t_sub2.capital_cost["value"]=5.0
        # t_sub2.marginal_cost["value"]=0.45+0.2

        # ===slack节点仅用作强制的、无成本的功率调节===（有成本的用plant模拟）
        # 吸收松弛节点
        t_slack_node1 = Absorption_Slack_Node(
            t_sys,
            in_name_id="sl_absorp",
            in_p_max=8376.9,    # kW
            in_p_nom_extendable=False,
            in_e_max=8376.9*8760 * t_simu_years,      # 储能放电如果上送，没有钱。若简单化，则可以设置0MW的功率限额
            # in_marginal_cost=0),
            in_marginal_cost=-1.2757 ,              # 设置1.8MW上送，但是边际成本按尖峰电价考虑
            # in_marginal_cost=-0.1)                     # user_finance，这里必须若考虑新能源倒送成本，则应为负值，即乘以负的功率，成本为正(mc=-0.1,能够有效的防止财务盈利储能在尖峰放电时功率超过负荷)
        )
        t_slack_node1.e_output = True

        # 注入松弛节点
        t_slack_node2 = Injection_Slack_Node(
            t_sys,
            in_name_id="sl_inject",
            in_p_max=12500*0.9,                              # 用户配变容量为1800kVA
            in_p_nom_extendable=False,
            in_e_max=12500*0.9*8760 * t_simu_years,
            # in_marginal_cost=0)
            in_marginal_cost=0.0)
            # in_marginal_cost=0.3)
        t_slack_node2.e_output = True

        t_sys.do_optimize()

        return value(t_sys.model.OBJ_FUNC)

    def case7(self, in_called, in_path):
        print("--------------------案例\"{}\"为xxx研究--------------------".format(Get_Current_Func_Name()))
        if in_called==False:
            return

def fractional_programming_iteration(in_lambda=-1.0, in_iter_num=10, in_min_tolerance=10000, in_min=-5.0, in_max=1.0):
    t_iter_num = in_iter_num                # 迭代次数
    t_min_tolerance = in_min_tolerance      # 可接受的近零值，先超过迭代次数或先达到可接受近零值即退出

    t_lambda = in_lambda                    # lambda
    t_max = in_max                          # 迭代上界
    t_min = in_min                          # 迭代下届

    # 首先明确上下界是否ok（目标函数等于0，表明无界或不可行）
    t_max_ok = (Call_Class_Funcs(NPS_Case, in_case="case6", in_path=Global.get("path")+"static/xls/", in_lambda=t_max) !=0)         # 判断G()的lambda上界是否有解
    t_min_ok = (Call_Class_Funcs(NPS_Case, in_case="case6", in_path=Global.get("path")+"static/xls/", in_lambda=t_min) !=0)         # 判断G()的lambda下界是否有解

    # 如果上下界都不ok，则直接返回（无解）
    if (t_max_ok==False) and (t_min_ok==False) :
        return None

    t_record = {}
    t_result_list = []
    for i in range(t_iter_num) :
        t_objvalue = Call_Class_Funcs(NPS_Case, in_case="case6", in_path=Global.get("path")+"static/xls/", in_lambda=t_lambda)
        # 如果G()的迭代值接近0并可接受，则认为当前lambda即为原F()的最优值
        if (abs(t_objvalue) < t_min_tolerance) and (t_objvalue!=0) :
            return t_lambda

        t_record["lambda"] = t_lambda
        t_record["min"] = t_min
        t_record["max"] = t_max

        # 如果：迭代结果>0，则当前lambda作为ok的下界
        if t_objvalue > 0:
            t_min = t_lambda
            t_lambda = (t_min+t_max)/2.0
            t_min_ok = True
        # 如果：迭代结果<0，则当前lambda作为ok的上界
        elif t_objvalue < 0:
            t_max = t_lambda
            t_lambda = (t_min+t_max)/2.0
            t_max_ok = True
        # 如果：迭代结果==0（即unbound或者infeasible），则检测上下界，哪个不ok，则当前lambda就作为哪个方向的界
        elif t_objvalue==0:
            if t_min_ok==True:
                t_max = t_lambda
                t_lambda = (t_min+t_max)/2.0
            elif t_max_ok==True:
                t_min = t_lambda
                t_lambda = (t_min+t_max)/2.0

        t_record["objvalue"] = t_objvalue
        t_result_list.append(copy.copy(t_record))

        for item in t_result_list:
            print("=======", item, "========")

    for item in t_result_list :
        print("=======", item, "========")

    # 返回可以接受的lambda
    return t_lambda

def main_shaoxing_35kV():
    Global.PATH = ""
    print(Global.get("path")+"static/xls/")

    # 净利润最大
    # Call_Class_Funcs(NPS_Case, in_case="case6", in_path=Global.get("path")+"static/xls/")

    # 收益率最大
    t_result_lambda = fractional_programming_iteration(in_lambda=-1.5, in_iter_num=20, in_min_tolerance=100000, in_min=-3.0, in_max=1.0)
    print("lambda where G()==0 is : {:.5f}".format(t_result_lambda))

def create_case6_sys():
        print("--------------------案例\"{}\"为2022.7.15 绍兴局35kV用户侧储能研究--------------------".format(Get_Current_Func_Name()))

        # t_simu_hours = 24
        # t_simu_hours = 720
        t_simu_hours = 24*365
        # t_simu_hours = 24*365*2
        # t_simu_hours = 24*365*8
        # t_simu_hours = 24*365*10
        # t_simu_hours = 24*365*20

        t_simu_years = t_simu_hours//8760
        if t_simu_years<1 :
            t_simu_years = 1
        print("t_simu_years is : ", t_simu_years)

        # =========================节点0=========================
        t_sys = Sys(
            in_share_y=True,
            in_name_id="sys1",
            in_simu_hours=t_simu_hours,
            in_rate=0.08,
            # in_spring_festival=Spring_Festival(in_bypass=False, in_start_day=10, in_stop_day=60)
            in_spring_festival=Spring_Festival(in_years=t_simu_years, in_bypass=False, in_start_day=10, in_stop_day=60),
            # in_investor="government", # 本案例为社会效益测算
            in_investor="user_finance", # 本案例为用户财务测算
            # in_user_finance_strategy="max_profit",
            # in_user_finance_strategy="max_rate",
            in_investor_user_discount=0.1,
            in_analysis_day_list=[0,90,180,270]
            # in_analysis_day_list=0
        )

        # ===IEA 2050 NZE 解读===\用户侧储能测算及分时电价\（分时电价表格）国网浙江省电力有限公司关于2022年6月代理工商业用户购电价格的公告.pdf
        # 大工业用户1-10kV、1.0倍
        t_peak =1.2757
        t_high =1.0655
        t_low =0.3407
        t_sys.tariff_list = [
            t_low , t_low , t_low , t_low , t_low , t_low ,
            t_low , t_low , t_high, t_peak, t_peak, t_high,
            t_high, t_low , t_low , t_peak, t_peak, t_high,
            t_high, t_high, t_high, t_high, t_low , t_low ]


        t_sys.pic_output = True

        # min(生命周期净利润/初期投资)中，利润为负数，投资为正数。最优lambda也为负数，如最优lambda=-1.5，表明利润/投资的最大值为1.5
        # 改变fp_lambda的值，直到目标函数由负数无限接近0时，此时fp_lambda值即为原目标函数最优值

        # t_sys.fp_lambda = in_lambda

        # t_sys.fp_lambda = -1.85
        t_sys.Add_Bus()

        # t_sys.print_objfunc = True

        # 直接读取8760h标幺值数据==========
        t_file = XLS_File('D:/server/server-xls/shaoxing-35kV.xls', in_cols=[0, 1], in_row_num=8761)
        print(f'{t_file.get_list("电负荷")}')
        print(f'{t_file.get_list("光伏")}')

        # t_file = XLS_File('static/xls/shaoxing-35kV.xls', in_cols=[0, 1], in_row_num=8761)

        # t_load1 = Load(in_sys=t_sys, in_name_id="load", in_p_nom=2033) # kW
        # t_load1.set_one_year_p(t_file.get_list("欣美"))   #负荷数据的正负一定要搞清楚，对结果影响非常大
        t_load1 = Load(in_sys=t_sys, in_name_id="load", in_p_nom=8376.9) # kW
        t_load1.set_one_year_p(t_file.get_list("电负荷"))   #负荷数据的正负一定要搞清楚，对结果影响非常大
        # t_load1 = Load(in_sys=t_sys, in_name_id="load", in_p_nom=3042) # kW
        # t_load1.set_one_year_p(t_file.get_list("友成"))   #负荷数据的正负一定要搞清楚，对结果影响非常大

        # 欣美的负荷数据中已经含了光伏出力
        t_pv1 = NE_Plant(in_sys=t_sys, in_name_id="pv", in_p_nom=9300, in_p_nom_extendable=False)   # kW
        # t_pv1.marginal_cost["value"]=0.0
        # t_pv1.capital_cost["value"]=1.78     # IEA 2050 中国造价
        t_pv1.set_one_year_p(t_file.get_list("光伏"), in_is_pu=True)   #光伏数据，实际只需要特性

        # 蓄电（电池储能）
        # 目前大型储能电站，2020年的萧电储能系统100MW*2h
        # 静态投资约5.86亿元（经营期15年），储能单元及安装54.0%、特殊项目费用（第一期和第二期的电池更换）19.4%、PCS系统11.15%（由于是考虑功率成本，因此含PCS 5.27%、主变1.24%（220kV主变可能不计列钱，即仅计及35kV变压器）、配电4.64%）、其他设施和工程（控制保护2%、电缆接地3%、集装箱基础1%、其他6%）12%，其他费用2%、预备费2%
        # 动态投资约5.46亿元，其中第一期和第二期电池更换费用折现共计-0.48亿元。
        # 因此，按电池和pcs的造价比例73.4:11.15，取2.54元/Wh、0.38元/W。（注意：如果考虑储能生命周期过短，可以把电池储能的Wh和W成本提高一倍或一定倍数考虑）
        # 注：计算中，按照2025年水平，价格均按50%计，取1.38元/Wh、0.24元/W（本项目不计220kV主变，后续项目最好考虑110kV及以下接入或220主变免费，即kW造价按0.4-0.5元/W左右（含pcs、35kV升压变、配电、110kV升压变，比较合理）
        # 综合效率取90%左右，因此充放电效率分别取95%、95%

        t_ess1 = Energy_Storage(t_sys, "bes",
                                in_p_charge_nom_extendable=True,
                                in_p_discharge_nom_extendable=True,
                                in_e_nom_extendable=True,
                                in_charge_effi=0.95,
                                in_discharge_effi=0.95
                                )
        # t_ess1.charge_marginal_cost["value"] = 0.0          # 计算社会效益时，储能与用户转移支付，成本为0
        # t_ess1.discharge_marginal_cost["value"] = -0.0      # 计算社会效益时，储能与用户转移支付，成本为0
        t_ess1.charge.marginal_cost["value"] = 0.0          # 计算财务效益时，采用内部的用户电价price_list，marginal_cost即燃料成本为0
        t_ess1.discharge.marginal_cost["value"] = -0.0      # 计算财务效益时，采用内部的用户电价price_list，marginal_cost即燃料成本为0
        t_ess1.charge.capital_cost["value"] = 0.2           # 参照萧电储能（不换电池的造价）
        t_ess1.discharge.capital_cost["value"] = 0.2        # 参照萧电储能（不换电池的造价）
        t_ess1.capital_cost_e["value"] = 1.5                # 参照萧电储能（不换电池的造价）

        # t_ess1.capital_cost_p2["value"] = 0.4    #设备换新的成本
        # t_ess1.capital_cost_e2["value"] = 1.0    #设备换新的成本
        # t_ess1.capital_cost2_year["value"] = 10       #设备更换的年限

        # 财务效益
        # t_sub1 = Plant(t_sys, "sub1", in_p_nom=3250, in_p_nom_extendable=False)

        # 社会效益
        # t_sub1 = Plant(t_sys, "sub1", in_p_nom=1600, in_p_nom_extendable=True)
        # t_sub1.capital_cost["value"]=5.0
        # t_sub1.marginal_cost["value"]=0.45+0.2

        # t_sub2 = Plant(t_sys, "sub2", in_p_nom_extendable=True)
        # t_sub2.capital_cost["value"]=5.0
        # t_sub2.marginal_cost["value"]=0.45+0.2

        # ===slack节点仅用作强制的、无成本的功率调节===（有成本的用plant模拟）
        # 吸收松弛节点
        t_slack_node1 = Absorption_Slack_Node(
            t_sys,
            in_name_id="sl_absorp",
            in_p_max=8376.9,    # kW
            in_p_nom_extendable=False,
            in_e_max=8376.9*8760 * t_simu_years,      # 储能放电如果上送，没有钱。若简单化，则可以设置0MW的功率限额
            # in_marginal_cost=0),
            in_marginal_cost=-1.2757 ,              # 设置1.8MW上送，但是边际成本按尖峰电价考虑
            # in_marginal_cost=-0.1)                     # user_finance，这里必须若考虑新能源倒送成本，则应为负值，即乘以负的功率，成本为正(mc=-0.1,能够有效的防止财务盈利储能在尖峰放电时功率超过负荷)
        )
        t_slack_node1.e_output = True

        # 注入松弛节点
        t_slack_node2 = Injection_Slack_Node(
            t_sys,
            in_name_id="sl_inject",
            in_p_max=12500*0.9,                              # 用户配变容量为1800kVA
            in_p_nom_extendable=False,
            in_e_max=12500*0.9*8760 * t_simu_years,
            # in_marginal_cost=0)
            in_marginal_cost=0.0)
            # in_marginal_cost=0.3)
        t_slack_node2.e_output = True

        # t_sys.do_optimize()

        return t_sys
        # return value(t_sys.model.OBJ_FUNC)

def main():
    Global.PATH = ""
    print(Global.get("path")+"static/xls/")

    # 净利润最大
    # Call_Class_Funcs(NPSR_Case, in_case="case6", in_path=Global.get("path")+"static/xls/")

    # 收益率最大
    (rtn_sys, rtn_lambda, rtn_objvalue, rtn_result_list) = Sys_Base.do_fractional_programming_iteration(in_sys_create_func=create_case6_sys, in_lambda=-1.5, in_iter_num=20, in_min_tolerance=100000, in_min=-3.0, in_max=1.0)
    print("lambda where G()==0 is : {:.5f}".format(rtn_lambda))
    for i in rtn_result_list :
        print(i)

def main_test():
    import io,sys
    stream = io.StringIO()
    out = sys.stdout
    sys.stdout = stream
    print("abcdef1")
    print("abcdef2")
    print("abcdef3")

    stream.seek(0)
    stream.readlines()
    # out.write("len is {}\n".format(stream.tell()))
    # stream.seek(0)
    stream.truncate()

    print("abcdef4")
    stream.seek(0)
    out.write("{}".format(stream.readline()))
    # out.write("len is {}\n".format(stream.tell()))
    # out.write("ok\n")

    # stream.seek(0)
    # stream.flush()
    # s = stream.readlines()
    # out.write("len is {}\n".format(stream.tell()))
    #
    # for i in s :
    #     out.write("{}".format(i))

def main_test2():
    print("===========================案例库===========================")
    global print_node_para_detail
    global print_model
    global print_opt_list
    global pic_output
    global print_pyomo_result
    print_node_para_detail= False
    print_model= True
    print_opt_list= False
    pic_output = True
    print_pyomo_result = True

    # Call_Class_Funcs(NPS_Case, in_case="")  # 显示所有案例的说明文字

    class my_class():
        def __init__(self):
            self.name = "class name"
            self.family = "class family"
        def output(self):
            print(self.name)
            print(self.family)

    # in_data = {
    #     "users":  [ {"name": "jack", "family": "seaver"},
    #                 {"name": "mike", "family": "seaver"} ],
    #     "session": { "user id":0, "session id":0, "status":"computing"},
    #     "cookie": {"session id":0, "cookie status":"running"}
    # }
    # # in_data = my_class()
    # print("data is : {}".format(indent_string(in_data)))
    # json_stream = json.dumps(in_data, indent=2)
    # print("dumped json stream is : {}".format(json_stream))
    # out_data = json.loads(json_stream)
    # print("data loaded from json stream is : {}".format(out_data))
import pandas as pd
def main_t():
    p = pd.read_excel("1.xls", sheet_name=0, usecols=range(7), nrows=8761)
    # p = pd.read_excel("1.xls", sheet_name=0, usecols=range(7), nrows=8761)
    print(p)
    a = p["电负荷"]
    print(len(a))
    # t = p[in_title_name]

    a = list(a)
    print(len(a))
    b=[]
    for i in range(len(a)) :
        if a[i]==a[i] :
            b.append(a[i])
        else:
            print(i, a[i])
            b.append(0)
    # a = [a_ for a_ in a if a_ == a_]  # 删除nan
    print(len(b))
    print(b)

    print("start")
    for i in range(len(b)) :
        if b[i]==b[i] :
            pass
        else:
            print(i, b[i])


if __name__ == "__main__" :
    # main_test()
    # main_t()
    # main_shaoxing_35kV()
    # main()
    # Call_Class_Funcs(NPS_Case, in_case="case1")
    nps = NPS_Case()
    nps.case1(in_called=True, in_path='')