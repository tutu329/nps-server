import uvicorn
import argparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from sse_starlette.sse import ServerSentEvent, EventSourceResponse

from pydantic import BaseModel
from typing import Any, Dict, List, Literal, Optional, Union

from NPS_Invest_Opt_Base import *
from Data_Analysis import *
import Global

class Stream_Response(BaseModel):
    delta: str
    finish_reason: Optional[Literal['stop', 'length']]

def calulate(in_paras):
    rate = in_paras['rate']

    pv_nom = in_paras['pv_nom0']        # kW
    pv_price = in_paras['pv_cost']  # 元/W
    pv_extent = in_paras['pv_optimize']

    wind_nom = in_paras['wind_nom0']    # kW
    wind_price = in_paras['wind_cost']  # 元/W
    wind_extent = in_paras['wind_optimize']

    bes_W_price = in_paras['storage_w_cost']  # 元/W
    bes_Wh_price = in_paras['storage_wh_cost']  # 元/Wh


    elec_up_max = in_paras['up_flow_max_proportion']
    elec_down_max = in_paras['down_flow_max_proportion']

    max_load_p = in_paras['load_max']  # kW
    max_load_kWh = in_paras['load_electricity']  # kWh, 年负荷电量

    t_simu_years = in_paras['simu_years']
    t_simu_hours = 8760 * t_simu_years

    # =========================节点0=========================
    t_sys = Sys(
        in_name_id='nps_project_0',
        in_dpi=64,
        in_share_y=True,
        in_simu_hours=t_simu_hours,
        in_rate=rate,
        in_spring_festival=Spring_Festival(in_years=t_simu_years, in_bypass=False, in_start_day=10, in_stop_day=60),
        in_investor="government",
        # in_investor="user_finance", # 本案例为用户财务测算
        # in_investor_user_discount=0.1,  # "user_finance"时的电价折扣
        # in_analysis_day_list=[0]
        in_analysis_day_list=[0, 90, 180, 270]  # 输出的典型日时间清单（第0天、第90天...）
        # in_analysis_day_list=0
    )
    t_sys.Add_Elec_Bus(in_if_reference_bus=True)  # 参考节点

    # t_sys.print_objfunc = True

    # ============负荷============
    file_path = 'c:/server/server-xls/data_analysis_multi.xlsx'
    t_file = XLS_File(file_path, in_cols=[0, 1, 2], in_row_num=8761)
    # t_file = XLS_File('static/xls/data_analysis_multi.xlsx', in_cols=[0,1,2], in_row_num=8761)
    t_load1 = Load(in_sys=t_sys, in_name_id="elec load", in_p_nom=max_load_p)  # kW
    t_load1.set_one_year_p(t_file.get_list("负荷"))  # 负荷数据的正负一定要搞清楚，对结果影响非常大


    # ============光伏============
    t_pv1 = NE_Plant(in_sys=t_sys, in_name_id="pv", in_p_nom=pv_nom, in_p_nom_extendable=pv_extent)  # kW
    # t_pv1 = NE_Plant(in_sys=t_sys, in_name_id="pv", in_p_nom=pv_nom, in_p_nom_extendable=False)   # kW
    # t_pv1.marginal_cost["value"]=0.0
    t_pv1.capital_cost["value"] = pv_price  # 元/W
    t_pv1.set_one_year_p(t_file.get_list("光伏"), in_is_pu=True)  # 光伏数据，实际只需要特性

    # ============风电============
    t_wind1 = NE_Plant(in_sys=t_sys, in_name_id="wind", in_p_nom=wind_nom, in_p_nom_extendable=wind_extent)  # kW
    # t_wind1 = NE_Plant(in_sys=t_sys, in_name_id="wind", in_p_nom=wind_nom, in_p_nom_extendable=False)    # kW
    # t_wind1.marginal_cost["value"]=0.0
    t_wind1.capital_cost["value"] = wind_price  # 元/W
    # t_wind1.capital_cost["value"]=6.367      # IEA 2050 中国造价
    t_wind1.set_one_year_p(t_file.get_list("风电"), in_is_pu=True)  # 光伏数据，实际只需要特性

    # ============储能============
    # 目前大型储能电站，2020年的萧电储能系统100MW*2h
    # 静态投资约5.86亿元（经营期15年），储能单元及安装54.0%、特殊项目费用（第一期和第二期的电池更换）19.4%、PCS系统11.15%（由于是考虑功率成本，因此含PCS 5.27%、主变1.24%（220kV主变可能不计列钱，即仅计及35kV变压器）、配电4.64%）、其他设施和工程（控制保护2%、电缆接地3%、集装箱基础1%、其他6%）12%，其他费用2%、预备费2%
    # 动态投资约5.46亿元，其中第一期和第二期电池更换费用折现共计-0.48亿元。
    # 因此，按电池和pcs的造价比例73.4:11.15，取2.54元/Wh、0.38元/W。（注意：如果考虑储能生命周期过短，可以把电池储能的Wh和W成本提高一倍或一定倍数考虑）
    # 注：计算中，按照2025年水平，价格均按50%计，取1.38元/Wh、0.24元/W（本项目不计220kV主变，后续项目最好考虑110kV及以下接入或220主变免费，即kW造价按0.4-0.5元/W左右（含pcs、35kV升压变、配电、110kV升压变，比较合理）
    # 综合效率取90%左右，因此充放电效率分别取95%、95%
    t_ess1 = Energy_Storage(t_sys, "bes",
                            in_p_charge_nom_extendable=True,
                            in_p_discharge_nom_extendable=True,
                            in_p_equal=True,
                            in_e_nom_extendable=True,
                            in_charge_effi=0.95,
                            in_discharge_effi=0.95
                            # discharge_effi必须在Energy_Storage初始化时输入（受component的constraint_effi初始化影响）
                            )
    # t_ess1.charge_marginal_cost["value"] = 0.0          # 计算社会效益时，储能与用户转移支付，成本为0
    # t_ess1.discharge_marginal_cost["value"] = -0.0      # 计算社会效益时，储能与用户转移支付，成本为0
    t_ess1.charge.marginal_cost["value"] = 0.0  # 计算财务效益时，采用内部的用户电价price_list，marginal_cost即燃料成本为0
    t_ess1.discharge.marginal_cost["value"] = -0.0  # 计算财务效益时，采用内部的用户电价price_list，marginal_cost即燃料成本为0

    t_ess1.charge.capital_cost["value"] = bes_W_price  # 元/W
    t_ess1.discharge.capital_cost["value"] = bes_W_price  # 元/W
    t_ess1.capital_cost_e["value"] = bes_Wh_price  # 元/Wh

    # ===slack节点仅用作强制的、无成本的功率调节===（有成本的用plant模拟）
    # 吸收松弛节点
    t_slack_node1 = Absorption_Slack_Node(
        t_sys,
        in_name_id="sl_absorp",
        in_p_max=max_load_p * 100,  # kW，放大100倍，意思是没有限制
        in_p_nom_extendable=False,
        in_e_max=max_load_kWh * elec_up_max * t_simu_years,  # 设置了用电量20%的上送限额
        # in_e_max=max_load_kWh * 0.2 * t_simu_years,         # 设置了用电量20%的上送限额
        # in_e_max=0*8760 * t_simu_years,         # 设置了1.5MW的功率限额
        # in_marginal_cost=0)                     # government, 这里必须若考虑新能源倒送成本，则应为负值，即乘以负的功率，成本为正
        in_marginal_cost=-0)  # user_finance，这里必须若考虑新能源倒送成本，则应为负值，即乘以负的功率，成本为正(mc=-0.1,能够有效的防止财务盈利储能在尖峰放电时功率超过负荷)
    t_slack_node1.e_output = True

    # 注入松弛节点
    t_slack_node2 = Injection_Slack_Node(
        t_sys,
        in_name_id="sl_inject",
        in_p_max=max_load_p * 100,  # kW，放大100倍，意思是没有限制
        in_p_nom_extendable=False,
        in_e_max=max_load_kWh * elec_down_max * t_simu_years,  # 设置了用电量10%的下送限额
        # in_e_max=max_load_kWh * 0.1 * t_simu_years,         # 设置了用电量10%的下送限额
        # in_e_max=0*8760 * t_simu_years,
        # in_marginal_cost=0)                     # government, 考虑的注入电量影子成本，输配电价暂考虑0.2元/kWh
        in_marginal_cost=0.2)  # user_finance, 考虑的注入电量成本，计算光伏、储能等项目的财务成本时，用户向电网购电成本应为正值
    t_slack_node2.e_output = True

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

    t_sys.do_optimize()

    return t_sys._get_table_for_report_output()

def start_server(http_address: str, port: int):
    app = FastAPI()
    app.add_middleware(CORSMiddleware,
                       allow_origins=["*"],
                       allow_credentials=True,
                       allow_methods=["*"],
                       allow_headers=["*"])
    @app.post("/cal")
    def cal(arg_dict: dict):
        print(f'NPS_Invest_Opt_Server收到请求，请求参数为: \n{arg_dict}')

        print(f'开始计算...')
        rtn_table = calulate(arg_dict)
        print(f'计算完成.')

        response = rtn_table
        return response

    print(f'API服务器已启动, url: {http_address}:{port} ...')
    uvicorn.run(app=app, host=http_address, port=port, workers=1)

def main():
    parser = argparse.ArgumentParser(description=f'API Service for NPS_Invest_Opt_Server.')
    parser.add_argument('--host', '-H', help='host to listen', default='0.0.0.0')
    parser.add_argument('--port', '-P', help='port of this service', default=18001)
    args = parser.parse_args()

    start_server(args.host, int(args.port))

if __name__ == '__main__':
    main()