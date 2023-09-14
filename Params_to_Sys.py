from NPS_Invest_Opt_Base import *
from User_Session import *

# 110kV变电站向上级电网购电的结算价格（是省局每年调整的一个内部价格，各县不一样且存在劫富济贫，萧山局2020年是0.52158元/kWh）（2021.6.30来自萧山局朱主任）
# 变电站单位MW造价：新建110kV站4500-5000万元，扩建110kV站50MVA主变500万元（2021.6.30来自朱凯进）。
# 煤电机组（这里若作为网电，则边际成本取0.15元/kWh，综合造价0元/W；若非网电，浙江上网电价0.3746元/kWh，综合造价3.2元/W。最小出力pu为0.4）
# 光伏机组（边际成本取0元/kWh，综合造价4.0元/W）(低压接入3.6，高压接入3.8-4.0，来源于王铖)
# 风电机组（边际成本取0元/kWh，综合造价5.0元/W）
# 核电机组（浙江上网电价为0.4，边际成考虑接近0，综合造价12元/W）
# 燃机机组（上网电价0.6，边际成本考虑0.3，综合造价2.2元/W）
# 锅炉（边际成本取0.3元/kWh，设备造价0.2元/W左右）
# 电冷水机（边际成本取0.3元/kWh，设备造价0.2元/W左右）
# CHP机组(天然气内燃机CHP，边际成本取1.0元/kWh，设备造价3.5元/W左右)
# 热泵（边际成本取0.3元/kWh，设备造价1元/W左右）
# 蓄热（设备造价取0.2元/Wh）
# 冰蓄冷（设备造价取0.2元/Wh）

#========================注意========================
# sys的标准输入是
# cc: 元/W、元/Wh
# mc: 元/kWh
# 目标函数：万元
#========================注意========================
def Params_to_Sys(in_params, in_open_id, tee=False, in_investor="government"):
    t_simu_hours = in_params["simu_hours"]
    t_simu_years = t_simu_hours // 8760
    t_sys_name_id = in_params["task"]

    t_params = copy.copy(in_params)
    # 将所有capital_cost除以1000.0
    for key in t_params :
        if "capital_cost" in key :
            t_params[key] = t_params[key]/1000.0

    # 节点对应关系，节点名：节点ID，如"elec":0
    t_bus_dict = {}

    print("objective_function_type is \"{}\"".format(in_investor))
    # print("fp_lambda is \"{}\"".format(in_fp_lambda))


    t_sys = Sys(
        # in_lambda=in_fp_lambda,
        in_remote_user_open_id=in_open_id,
        tee=tee,
        in_dpi=64,
        in_share_y=True,
        in_name_id=t_sys_name_id,
        in_simu_hours=t_simu_hours,
        in_rate=0.08,
        in_spring_festival=Spring_Festival(in_years=t_simu_years, in_bypass=False, in_start_day=10, in_stop_day=60),
        in_investor=in_investor,
        in_investor_user_discount=0.1,  # "user_finance"时的电价折扣
        in_analysis_day_list=[0]
    )



    # 获取用户自定义数据dict
    s_users_session = WX_Users_Session()
    t_job = s_users_session.Get_User_Data_by_ID(in_open_id)

    # 缺省的参数文件server.xlsx
    t_file = XLS_File(Global.get("path")+"server.xlsx", in_cols=[0, 1, 2, 3, 4, 5, 6], in_row_num=8761) # 负荷、光伏、风电、水电、热负荷、冷负荷

    # 从用户自定义数据导入
    if t_job != None and t_job.get_custom_data_dict().get("分时电价") != None and t_params["load_type"]=="custom":
        t_list = t_job.get_custom_data_dict().get("分时电价")
        t_sys.tariff_list = t_list
        print("use imported custom price data with first value is :{}".format(t_job.get_custom_data_dict().get("分时电价")[0]))
    else:
        t_sys.tariff_list = t_file.get_list("分时电价")[0:24]
        print("use server price data.")

    print("tariff_list finally is :")
    for i in t_sys.tariff_list :
        print(i)

    # =========================电节点=========================
    t_sys.Add_Elec_Bus(in_if_reference_bus=True)
    t_bus_dict["elec"] = t_sys.Current_Bus_ID()


    # ============负荷============
    #===============================临时================================
    # t_file = XLS_File(Global.get("path")+"static/xls/data_analysis_xs.xlsx", in_cols=[0, 1, 2, 3, 4, 5]) # 负荷、光伏、风电、水电、热负荷、冷负荷
    #===============================临时================================
    if t_params.get("elec_load_max"):
        t_load1 = Load(in_sys=t_sys, in_name_id="elec load", in_p_nom=t_params["elec_load_max"]*1000.0)  # kW

        if t_job!=None and t_job.get_custom_data_dict().get("电负荷") != None and t_params["load_type"]=="custom":
            t_list = t_job.get_custom_data_dict().get("电负荷")
            t_load1.set_one_year_p(t_job.get_custom_data_dict().get("电负荷"))
            print("use imported custom elec_load with first value is :{}".format(t_job.get_custom_data_dict().get("电负荷")[0]))
        else:
            if t_params["load_type"]=="industry":
                t_load1.set_one_year_p()    # 设置为p_nom的直线负荷
                print("use server industry elec_load.")
            else:
                t_load1.set_one_year_p(t_file.get_list("电负荷"))  # 负荷数据的正负一定要搞清楚，对结果影响非常大
                print("use server city elec_load.")
            # ===============================临时================================
            # t_load1.set_one_year_p(t_file.get_list("杭可"))  # 负荷数据的正负一定要搞清楚，对结果影响非常大
            #===============================临时================================

    # ============风电============
    if t_params.get("wind_p_nom")==None or t_params.get("wind_p_nom_extendable")==None :
        pass
    else:
        # 如果容量不优化、且存量容量为0，则不建模
        if not (t_params["wind_p_nom"]==0 and t_params["wind_p_nom_extendable"]==False) :
            t_wind1 = NE_Plant(in_sys=t_sys, in_name_id="wind", in_p_nom=t_params["wind_p_nom"]*1000.0, in_p_nom_extendable=t_params["wind_p_nom_extendable"], in_p_nom_max=t_params["wind_p_nom_max"]*1000.0)
            t_wind1.capital_cost["value"]=t_params["wind_capital_cost"]
            # t_wind1.set_one_year_p(t_file.get_list("风电"), in_is_pu=True)   #风电数据，实际只需要特性

            # 从用户自定义数据导入
            if t_job != None and t_job.get_custom_data_dict().get("风电") != None and t_params["load_type"]=="custom":
                t_list = t_job.get_custom_data_dict().get("风电")
                t_wind1.set_one_year_p(t_job.get_custom_data_dict().get("风电"))
                print("use imported custom wind data with first value is :{}".format(t_job.get_custom_data_dict().get("风电")[0]))
            else:
                t_wind1.set_one_year_p(t_file.get_list("风电"))  # 负荷数据的正负一定要搞清楚，对结果影响非常大
                print("use server wind data.")

    # ============光伏============
    if t_params.get("pv_p_nom")==None or t_params.get("pv_p_nom_extendable")==None:
        pass
    else:
        # 如果容量不优化、且存量容量为0，则不建模
        if not (t_params["pv_p_nom"]==0 and t_params["pv_p_nom_extendable"]==False) :
            t_pv1 = NE_Plant(in_sys=t_sys, in_name_id="pv", in_p_nom=t_params["pv_p_nom"]*1000.0, in_p_nom_extendable=t_params["pv_p_nom_extendable"], in_p_nom_max=t_params["pv_p_nom_max"]*1000.0)
            t_pv1.capital_cost["value"]=t_params["pv_capital_cost"]
            # t_pv1.set_one_year_p(t_file.get_list("光伏"), in_is_pu=True)   #光伏数据，实际只需要特性

            # 从用户自定义数据导入
            if t_job != None and t_job.get_custom_data_dict().get("光伏") != None and t_params["load_type"]=="custom":
                t_list = t_job.get_custom_data_dict().get("光伏")
                t_pv1.set_one_year_p(t_job.get_custom_data_dict().get("光伏"))
                print("use imported custom pv data with first value is :{}".format(t_job.get_custom_data_dict().get("光伏")[0]))
            else:
                t_pv1.set_one_year_p(t_file.get_list("光伏"))  # 负荷数据的正负一定要搞清楚，对结果影响非常大
                print("use server pv data.")

    # ============水电============
    if t_params.get("hydro_p_nom")==None or t_params.get("hydro_p_nom_extendable")==None:
        pass
    else:
        # 如果容量不优化、且存量容量为0，则不建模
        if not (t_params["hydro_p_nom"]==0 and t_params["hydro_p_nom_extendable"]==False) :
            if t_params["hydro_type"]=="定发电量" :
                t_hydro1 = Hydro_Plant(in_sys=t_sys, in_name_id="hydro", in_hours_nom=t_params["hydro_hours_max"], in_p_nom=t_params["hydro_p_nom"]*1000.0, in_p_nom_extendable=t_params["hydro_p_nom_extendable"])
                t_hydro1.capital_cost["value"]=t_params["hydro_capital_cost"]
            elif t_params["hydro_type"]=="定特性" :
                t_hydro1 = NE_Plant(in_sys=t_sys, in_name_id="hydro", in_p_nom=t_params["hydro_p_nom"]*1000.0, in_p_nom_extendable=t_params["hydro_p_nom_extendable"])
                t_hydro1.capital_cost["value"]=t_params["hydro_capital_cost"]
                # t_hydro1.set_one_year_p(t_file.get_list("水电"), in_is_pu=True)   #水电数据，实际只需要特性

                # 从用户自定义数据导入
                if t_job != None and t_job.get_custom_data_dict().get("水电") != None and t_params["load_type"]=="custom":
                    t_list = t_job.get_custom_data_dict().get("水电")
                    t_hydro1.set_one_year_p(t_job.get_custom_data_dict().get("水电"))
                    print("use imported custom hydro data with first value is :{}".format(t_job.get_custom_data_dict().get("水电")[0]))
                else:
                    t_hydro1.set_one_year_p(t_file.get_list("水电"))  # 负荷数据的正负一定要搞清楚，对结果影响非常大
                    print("use server hydro data.")

            else:
                pass

    # ============煤电============
    if t_params.get("coal_p_nom")==None or t_params.get("coal_p_nom_extendable")==None:
        # print(t_params.get("coal_p_nom"))
        # print(t_params.get("coal_p_nom_extendable"))
        # print("==================hihihihihihihihihihihi==================hihihihihihihihihihihi")
        pass
    else:
        # 如果容量不优化、且存量容量为0，则不建模
        if not (t_params["coal_p_nom"] == 0 and t_params["coal_p_nom_extendable"] == False):
            # print("==================hihihihihihihihihihihi==================hihihihihihihihihihihi")
            print(indent_string(t_params))
            t_coal1 = Plant(in_sys=t_sys, in_name_id="coal", in_p_nom=t_params["coal_p_nom"]*1000.0, in_p_nom_extendable=t_params["coal_p_nom_extendable"])
            t_coal1.marginal_cost["value"]=t_params["coal_marginal_cost"]
            t_coal1.capital_cost["value"]=t_params["coal_capital_cost"]
            t_coal1.p_max_pu["value"]=t_params["coal_p_max_pu"]
            t_coal1.p_min_pu["value"]=t_params["coal_p_min_pu"]

    # ============核电============
    if t_params.get("nuclear_p_nom")==None or t_params.get("nuclear_p_nom_extendable")==None:
        pass
    else:
        # 如果容量不优化、且存量容量为0，则不建模
        if not (t_params["nuclear_p_nom"] == 0 and t_params["nuclear_p_nom_extendable"] == False):
            t_nuclear1 = Plant(in_sys=t_sys, in_name_id="nuclear", in_p_nom=t_params["nuclear_p_nom"]*1000.0, in_p_nom_extendable=t_params["nuclear_p_nom_extendable"])
            t_nuclear1.marginal_cost["value"]=t_params["nuclear_marginal_cost"]
            t_nuclear1.capital_cost["value"]=t_params["nuclear_capital_cost"]
            t_nuclear1.p_max_pu["value"]=t_params["nuclear_p_max_pu"]
            t_nuclear1.p_min_pu["value"]=t_params["nuclear_p_min_pu"]

    # ============柴发============
    if t_params.get("diesel_p_nom")==None or t_params.get("diesel_p_nom_extendable")==None:
        pass
    else:
        # 如果容量不优化、且存量容量为0，则不建模
        if not (t_params["diesel_p_nom"] == 0 and t_params["diesel_p_nom_extendable"] == False):
            t_diesel1 = Plant(in_sys=t_sys, in_name_id="diesel", in_p_nom=t_params["diesel_p_nom"]*1000.0, in_p_nom_extendable=t_params["diesel_p_nom_extendable"])
            t_diesel1.marginal_cost["value"]=t_params["diesel_marginal_cost"]
            t_diesel1.capital_cost["value"]=t_params["diesel_capital_cost"]
            t_diesel1.p_max_pu["value"]=t_params["diesel_p_max_pu"]
            t_diesel1.p_min_pu["value"]=t_params["diesel_p_min_pu"]

    # ============抽蓄============
    if t_params.get("php_p_nom")==None or t_params.get("php_pe_nom_extendable")==None:
        pass
    else:
        # 如果容量不优化、且存量容量为0，则不建模
        if not (t_params["php_p_nom"] == 0 and t_params["php_pe_nom_extendable"] == False):
            t_php1 = Energy_Storage(t_sys, "php",
                                    in_p_charge_nom_extendable=t_params["php_pe_nom_extendable"],
                                    in_p_discharge_nom_extendable=t_params["php_pe_nom_extendable"],
                                    in_e_nom_extendable=t_params["php_pe_nom_extendable"],
                                    in_charge_effi=t_params["php_charge_effi"],
                                    in_discharge_effi=t_params["php_discharge_effi"],
                                    in_bus0_id=t_bus_dict["elec"],
                                    in_bus1_id=t_bus_dict["elec"],
                                    in_p_charge_nom=t_params["php_p_nom"]*1000,
                                    in_p_discharge_nom=t_params["php_p_nom"]*1000,
                                    in_e_nom=t_params["php_e_nom"]*1000
                                    # discharge_effi必须在Energy_Storage初始化时输入（受component的constraint_effi初始化影响）
                                    )
            t_php1.charge.capital_cost["value"] = t_params["php_p_capital_cost"] / 2.0
            t_php1.discharge.capital_cost["value"] = t_params["php_p_capital_cost"] / 2.0
            t_php1.capital_cost_e["value"] = t_params["php_e_capital_cost"]

    # ============蓄电系统============
    if t_params.get("elec_storage_p_nom")==None or t_params.get("elec_storage_pe_nom_extendable")==None:
        pass
    else:
        # 如果容量不优化、且存量容量为0，则不建模
        if not (t_params["elec_storage_p_nom"] == 0 and t_params["elec_storage_pe_nom_extendable"] == False):
            t_bes1 = Energy_Storage(t_sys, "bes",
                                    in_p_charge_nom_extendable=t_params["elec_storage_pe_nom_extendable"],
                                    in_p_discharge_nom_extendable=t_params["elec_storage_pe_nom_extendable"],
                                    in_e_nom_extendable=t_params["elec_storage_pe_nom_extendable"],
                                    in_charge_effi=t_params["elec_storage_charge_effi"],
                                    in_discharge_effi=t_params["elec_storage_discharge_effi"],
                                    in_bus0_id=t_bus_dict["elec"],
                                    in_bus1_id=t_bus_dict["elec"],
                                    in_p_charge_nom=t_params["elec_storage_p_nom"]*1000,
                                    in_p_discharge_nom=t_params["elec_storage_p_nom"]*1000,
                                    in_e_nom=t_params["elec_storage_e_nom"]*1000
                                    # discharge_effi必须在Energy_Storage初始化时输入（受component的constraint_effi初始化影响）
                                    )
            t_bes1.charge.capital_cost["value"] = t_params["elec_storage_p_capital_cost"] / 2.0
            t_bes1.discharge.capital_cost["value"] = t_params["elec_storage_p_capital_cost"] / 2.0
            t_bes1.capital_cost_e["value"] = t_params["elec_storage_e_capital_cost"]

    # ============电蓄氢、放电系统============
    if t_params.get("hydrogen_storage_p_nom")==None or t_params.get("hydrogen_storage_pe_nom_extendable")==None:
        pass
    else:
        # 如果容量不优化、且存量容量为0，则不建模
        if not (t_params["hydrogen_storage_p_nom"] == 0 and t_params["hydrogen_storage_pe_nom_extendable"] == False):
            t_hes1 = Energy_Storage(t_sys, "hes",
                                    in_p_charge_nom_extendable=t_params["hydrogen_storage_pe_nom_extendable"],
                                    in_p_discharge_nom_extendable=t_params["hydrogen_storage_pe_nom_extendable"],
                                    in_e_nom_extendable=t_params["hydrogen_storage_pe_nom_extendable"],
                                    in_charge_effi=t_params["hydrogen_storage_charge_effi"],
                                    in_discharge_effi=t_params["hydrogen_storage_discharge_effi"],
                                    in_bus0_id=t_bus_dict["elec"],
                                    in_bus1_id=t_bus_dict["elec"],
                                    in_p_charge_nom=t_params["hydrogen_storage_p_nom"]*1000,
                                    in_p_discharge_nom=t_params["hydrogen_storage_p_nom"]*1000,
                                    in_e_nom=t_params["hydrogen_storage_e_nom"]*1000
                                    # discharge_effi必须在Energy_Storage初始化时输入（受component的constraint_effi初始化影响）
                                    )
            t_hes1.charge.capital_cost["value"] = t_params["hydrogen_storage_charge_p_capital_cost"]
            t_hes1.discharge.capital_cost["value"] = t_params["hydrogen_storage_discharge_p_capital_cost"]
            t_hes1.capital_cost_e["value"] = t_params["hydrogen_storage_e_capital_cost"]

    # ================松弛节点=======================
    if t_simu_hours>=8760:
        t_slack_hours = 8760 * t_simu_years
    else:
        t_slack_hours = t_simu_hours
    # 吸收节点(p<0)
    if t_params.get("slack_absorp_p_max")!=None :
        t_slack_node1 = Absorption_Slack_Node(
            t_sys,
            in_name_id="absorp",
            in_p_max=t_params["slack_absorp_p_max"]*1000,                   # kW
            in_e_max=t_params["slack_absorp_p_max"]*1000 * t_slack_hours,   #
            in_marginal_cost=t_params["slack_absorp_marginal_cost"])   # 这里若考虑新能源倒送成本，则应为负值，即乘以负的功率，成本为正
        t_slack_node1.e_output = True

    # 注入节点(p>0)
    if t_params.get("slack_inject_p_max")!=None :
        t_slack_node2 = Injection_Slack_Node(
            t_sys,
            in_name_id="inject",
            in_p_max=t_params["slack_inject_p_max"]*1000,                   # kW
            in_e_max=t_params["slack_inject_p_max"]*1000 * t_slack_hours,   #
            in_marginal_cost=t_params["slack_inject_marginal_cost"])   # 这里若考虑网电成本，则应为正值，即乘以正的功率，成本为正
        t_slack_node2.e_output = True

    # =========================heat 节点1=========================
    if t_params.get("heat_load_max")!=None:
        if t_params["heat_load_max"]!=0 :
            t_sys.Add_Bus() # Bus_ID++
            t_bus_dict["heat"] = t_sys.Current_Bus_ID()

            t_heat_load = Load(in_sys=t_sys, in_name_id="heat load", in_p_nom=t_params["heat_load_max"]*1000.0)  # kW
            # if t_params["load_type"] == "industry":
            #     t_heat_load.set_one_year_p()  # 设置为p_nom的直线负荷
            # else:
            #     t_heat_load.set_one_year_p(t_file.get_list("热负荷"))  # 负荷数据的正负一定要搞清楚，对结果影响非常大

            if t_job != None and t_job.get_custom_data_dict().get("热负荷") != None and t_params["load_type"]=="custom":
                t_list = t_job.get_custom_data_dict().get("热负荷")
                t_heat_load.set_one_year_p(t_job.get_custom_data_dict().get("热负荷"))
                print("use imported custom heat_load with first value is :{}".format(
                    t_job.get_custom_data_dict().get("热负荷")[0]))
            else:
                if t_params["load_type"] == "industry":
                    t_heat_load.set_one_year_p()  # 设置为p_nom的直线负荷
                    print("use server industry heat_load.")
                else:
                    t_heat_load.set_one_year_p(t_file.get_list("热负荷"))  # 负荷数据的正负一定要搞清楚，对结果影响非常大
                    print("use server city heat_load.")

            # ============电锅炉====================
            if t_params.get("elec_heater_p_nom")==None or t_params.get("elec_heater_p_nom_extendable")==None:
                pass
            else:
                # 如果容量不优化、且存量容量为0，则不建模
                if not (t_params["elec_heater_p_nom"]==0 and t_params["elec_heater_p_nom_extendable"]==False) :
                    t_elec_boiler1 = Oneway_Link(t_sys,
                                           in_p_nom=t_params["elec_heater_p_nom"]*1000,
                                           in_p_nom_extendable=t_params["elec_heater_p_nom_extendable"],
                                           in_capital_cost=t_params["elec_heater_capital_cost"],
                                           in_bus0_id=t_bus_dict["elec"],
                                           in_bus1_id=t_bus_dict["heat"],
                                           in_name="elec boiler",
                                           in_effi=t_params["elec_heater_effi"]
                                           )

            # ============电蓄热、放热系统============
            if t_params.get("heat_storage_p_nom")==None or t_params.get("heat_storage_pe_nom_extendable")==None:
                pass
            else:
                # 如果容量不优化、且存量容量为0，则不建模
                if not (t_params["heat_storage_p_nom"] == 0 and t_params["heat_storage_pe_nom_extendable"] == False):
                    t_tes1 = Energy_Storage(t_sys, "tes",
                                            in_p_charge_nom_extendable=t_params["heat_storage_pe_nom_extendable"],
                                            in_p_discharge_nom_extendable=t_params["heat_storage_pe_nom_extendable"],
                                            in_e_nom_extendable=t_params["heat_storage_pe_nom_extendable"],
                                            in_charge_effi=t_params["heat_storage_charge_effi"],
                                            in_discharge_effi=t_params["heat_storage_discharge_effi"],
                                            in_bus0_id=t_bus_dict["elec"],
                                            in_bus1_id=t_bus_dict["heat"],
                                            in_p_charge_nom = t_params["heat_storage_p_nom"] * 1000,
                                            in_p_discharge_nom = t_params["heat_storage_p_nom"] * 1000,
                                            in_e_nom = t_params["heat_storage_e_nom"] * 1000
                    # discharge_effi必须在Energy_Storage初始化时输入（受component的constraint_effi初始化影响）
                                            )
                    t_tes1.charge.capital_cost["value"] = t_params["heat_storage_p_capital_cost"]
                    t_tes1.discharge.capital_cost["value"] = t_params["heat_storage_p_capital_cost"]
                    t_tes1.capital_cost_e["value"] = t_params["heat_storage_e_capital_cost"]

    # =========================cold 节点1=========================
    if t_params.get("cold_load_max"):
        if t_params["cold_load_max"]!=0 :
            t_sys.Add_Bus() # Bus_ID++
            t_bus_dict["cold"] = t_sys.Current_Bus_ID()

            t_cold_load = Load(in_sys=t_sys, in_name_id="cold load", in_p_nom=t_params["cold_load_max"]*1000.0)  # kW
            # if t_params["load_type"] == "industry":
            #     t_cold_load.set_one_year_p()  # 设置为p_nom的直线负荷
            # else:
            #     t_cold_load.set_one_year_p(t_file.get_list("冷负荷"))  # 负荷数据的正负一定要搞清楚，对结果影响非常大

            if t_job != None and t_job.get_custom_data_dict().get("冷负荷") != None and t_params["load_type"]=="custom":
                t_list = t_job.get_custom_data_dict().get("冷负荷")
                t_cold_load.set_one_year_p(t_job.get_custom_data_dict().get("冷负荷"))
                print("use imported custom cold_load with first value is :{}".format(t_job.get_custom_data_dict().get("冷负荷")[0]))
            else:
                if t_params["load_type"] == "industry":
                    t_cold_load.set_one_year_p()  # 设置为p_nom的直线负荷
                    print("use server industry cold_load.")
                else:
                    t_cold_load.set_one_year_p(t_file.get_list("冷负荷"))  # 负荷数据的正负一定要搞清楚，对结果影响非常大
                    print("use server city cold_load.")

            # ============电制冷====================
            if t_params.get("elec_cooler_p_nom")==None or t_params.get("elec_cooler_p_nom_extendable")==None:
                pass
            else:
                # 如果容量不优化、且存量容量为0，则不建模
                if not (t_params["elec_cooler_p_nom"]==0 and t_params["elec_cooler_p_nom_extendable"]==False) :
                    t_elec_cooler1 = Oneway_Link(t_sys,
                                           in_p_nom=t_params["elec_cooler_p_nom"] * 1000,
                                           in_p_nom_extendable=t_params["elec_cooler_p_nom_extendable"],
                                           in_capital_cost=t_params["elec_cooler_capital_cost"],
                                           in_bus0_id=t_bus_dict["elec"],
                                           in_bus1_id=t_bus_dict["cold"],
                                           in_name="elec cooler",
                                           in_effi=t_params["elec_cooler_effi"]
                                           )

            # ============电蓄冷、放冷系统============
            if t_params.get("cold_storage_p_nom")==None or t_params.get("cold_storage_pe_nom_extendable")==None:
                pass
            else:
                # 如果容量不优化、且存量容量为0，则不建模
                if not (t_params["cold_storage_p_nom"] == 0 and t_params["cold_storage_pe_nom_extendable"] == False):
                    t_ces1 = Energy_Storage(t_sys, "ces",
                                            in_p_charge_nom_extendable=t_params["cold_storage_pe_nom_extendable"],
                                            in_p_discharge_nom_extendable=t_params["cold_storage_pe_nom_extendable"],
                                            in_e_nom_extendable=t_params["cold_storage_pe_nom_extendable"],
                                            in_charge_effi=t_params["cold_storage_charge_effi"],
                                            in_discharge_effi=t_params["cold_storage_discharge_effi"],
                                            in_bus0_id=t_bus_dict["elec"],
                                            in_bus1_id=t_bus_dict["cold"],
                                            in_p_charge_nom = t_params["cold_storage_p_nom"] * 1000,
                                            in_p_discharge_nom = t_params["cold_storage_p_nom"] * 1000,
                                            in_e_nom = t_params["cold_storage_e_nom"] * 1000
                                            # discharge_effi必须在Energy_Storage初始化时输入（受component的constraint_effi初始化影响）
                                            )
                    t_ces1.charge.capital_cost["value"] = t_params["cold_storage_p_capital_cost"]
                    t_ces1.discharge.capital_cost["value"] = t_params["cold_storage_p_capital_cost"]
                    t_ces1.capital_cost_e["value"] = t_params["cold_storage_e_capital_cost"]

    # 有热负荷和冷负荷才有的设备
    if t_bus_dict.get("heat")==None or t_bus_dict.get("cold")==None:
        pass
    else:
        # 热泵机组
        if t_params.get("heatpump_p_nom")==None or t_params.get("heatpump_p_nom_extendable")==None:
            pass
        else:
            # 如果容量不优化、且存量容量为0，则不建模
            if not (t_params["heatpump_p_nom"] == 0 and t_params["heatpump_p_nom_extendable"] == False):
                t_heatpump1 = Cogeneration(t_sys,
                                     in_p_nom=t_params["heatpump_p_nom"] * 1000,
                                     in_p_nom_extendable=t_params["heatpump_p_nom_extendable"],
                                     in_capital_cost=t_params["heatpump_capital_cost"],
                                     in_ratio_12=t_params["heatpump_ratio12"],  # 冷热比
                                     in_bus0_id=t_bus_dict["elec"],
                                     in_bus1_id=t_bus_dict["cold"],
                                     in_bus2_id=t_bus_dict["heat"],
                                     in_name="heatpump",
                                     in_effi=t_params["heatpump_effi"],
                                     )

    # =========================gas 节点2=========================
    if t_params.get("gas_price"):
        if t_params["gas_price"]!=0 :
            t_sys.Add_Bus()
            t_bus_dict["gas"] = t_sys.Current_Bus_ID() 
            # 一次能源天然气
            t_gas = Primary_Energy_Supply(t_sys, in_name_id="gas supply", in_marginal_cost=t_params["gas_price"])  # 天然气若3元/方，由于1方天然气热值10kWh，因此大约为0.3元/kWh

            # 燃机
            if t_params.get("gas_p_nom")==None or t_params.get("gas_p_nom_extendable")==None:
                pass
            else:
                # 如果容量不优化、且存量容量为0，则不建模
                if not (t_params["gas_p_nom"]==0 and t_params["gas_p_nom_extendable"]==False) :
                    t_gas2p = Oneway_Link(t_sys,
                                          in_p_nom=t_params["gas_p_nom"] * 1000,
                                          in_p_nom_extendable=t_params["gas_p_nom_extendable"],
                                          in_capital_cost=t_params["gas_capital_cost"],
                                          in_bus0_id=t_bus_dict["gas"],
                                          in_bus1_id=t_bus_dict["elec"],
                                          in_name="gas turbine",
                                          in_effi=t_params["gas_effi"],
                                          in_p_max_pu=t_params["gas_p_max_pu"],
                                          in_p_min_pu=t_params["gas_p_min_pu"],
                                          )

            # 有热负荷和天然气才有的设备
            if t_bus_dict.get("heat")==None or t_bus_dict.get("gas")==None:
                pass
            else:
                # 天然气锅炉
                if t_params.get("gas_boiler_p_nom")==None or t_params.get("gas_boiler_p_nom_extendable")==None:
                    pass
                else:
                    # 如果容量不优化、且存量容量为0，则不建模
                    if not (t_params["gas_boiler_p_nom"]==0 and t_params["gas_boiler_p_nom_extendable"]==False) :
                        t_gas_boiler = Oneway_Link(t_sys,
                                              in_p_nom=t_params["gas_boiler_p_nom"] * 1000,
                                              in_p_nom_extendable=t_params["gas_boiler_p_nom_extendable"],
                                              in_capital_cost=t_params["gas_boiler_capital_cost"],
                                              in_bus0_id=t_bus_dict["gas"],
                                              in_bus1_id=t_bus_dict["heat"],
                                              in_name="gas boiler",
                                              in_effi=t_params["gas_boiler_effi"]
                                              )

                # 天然气热电联产
                if t_params.get("chp_p_nom")==None or t_params.get("chp_p_nom_extendable")==None:
                    pass
                else:
                    # 如果容量不优化、且存量容量为0，则不建模
                    if not (t_params["chp_p_nom"]==0 and t_params["chp_p_nom_extendable"]==False) :
                        t_chp = Cogeneration(t_sys,
                                             in_p_nom=t_params["chp_p_nom"] * 1000,
                                             in_p_nom_extendable=t_params["chp_p_nom_extendable"],
                                             in_capital_cost=t_params["chp_capital_cost"],  # CHP造价3.5元/W，由于是折算到电功率，因此这里可能填1.75
                                             in_ratio_12=t_params["chp_ratio12"],  # 热电比
                                             in_bus0_id=t_bus_dict["gas"],
                                             in_bus1_id=t_bus_dict["heat"],
                                             in_bus2_id=t_bus_dict["elec"],
                                             in_name="CHP",
                                             in_effi=t_params["chp_effi"],
                                             in_p_max_pu=t_params["chp_p_max_pu"],
                                             in_p_min_pu=t_params["chp_p_min_pu"]
                                             )

    # t_sys.Add_Elec_Bus()
    # t_bus_dict["elec1"] = t_sys.Current_Bus_ID()

    # t_line1 = Elec_Branch(t_sys, in_name="line1", in_bus0_id=0, in_bus1_id=3, in_reactance_pu=0.000097 * 100 / (525 * 525 / 100))
    # t_elec_load1 = Load(in_sys=t_sys, in_name_id="elec load 1", in_p_nom=3000)
    # t_elec_load1.set_one_year_p(t_file.get_list("负荷"))  # 负荷数据的正负一定要搞清楚，对结果影响非常大

    # t_sys.Add_Elec_Bus()
    # t_bus_dict["elec2"] = t_sys.Current_Bus_ID()

    # t_line2 = Elec_Branch(t_sys, in_name="line2", in_bus0_id=0, in_bus1_id=4, in_reactance_pu=0.000097 * 100 / (525 * 525 / 100))
    # t_elec_load2 = Load(in_sys=t_sys, in_name_id="elec load 2", in_p_nom=1500)
    # t_elec_load2.set_one_year_p(t_file.get_list("负荷"))  # 负荷数据的正负一定要搞清楚，对结果影响非常大

    # t_line3 = Elec_Branch(t_sys, in_name="line3", in_bus0_id=3, in_bus1_id=4, in_reactance_pu=0.000097 * 100 / (525 * 525 / 100))

    return t_sys