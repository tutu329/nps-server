from User_Session import *
from enum import Enum
from Python_User_Logger import *
from NPS_Invest_Opt_Base import *
from Data_Analysis import *
from multiprocessing import Manager, Lock
from multiprocessing import Queue as mp_Queue
from multiprocessing import Queue as mp_Queue
# from multiprocessing import Value as mp_Value     # 用起来不方便，换成Manager().Value()
from User_Process_Task import *

# class Status(Enum):
#     UNSTARTED = 0
#     CALCULATING = 1
#     RESOLVED = 2

# 用户会话状态
class NPS_User_Session():
    # user_id: 微信小程序唯一ID(open id)
    # callback_func_progress(progress数值，显示用的小数点的数量)
    def __init__(self, user_id):
        # 用户id
        self.user_id = user_id

        # 用户输入参数
        self.params = ""

        # 用户输出数据
        # 不同用户的输出文件如xxx.png，需要加入user id确保唯一性
        self._result = ""

        self._task =User_Process_Task()

        # 用户会话状态
        # 注意！ mp变量不能直接用"="进行赋值，必须用set()或者update()，否则mp变量会因为赋值变成普通变量。另外要注意不同进程的生命周期，如果FileNotFoundError或者pipe broken，可能需要依靠join等待来确保生命周期足够长。
        self.mp_status = Manager().Value(Status, Status.UNSTARTED)

        # 用户中间输出(为先进先出的queue,queue为python线程安全的数据结构。设置数量没有上限)
        self._mp_tee = mp_Queue(maxsize=0)

        # 注册用户计算进度
        # self._calculate_thread = threading.Thread(target=self.calculate_thread_func)
        self._progress = Progress()
        self._progress.set_progress_callback_func(self._callback_func_progress)

    # 进度的回调函数
    def _callback_func_progress(self, callback_progress, callback_dots_num):
        t_dots = callback_dots_num * "."
        print("\r{}% completed{}".format(round(callback_progress), t_dots), end="")
        # print("status is : {}".format(self.status))

    # 设置用户的计算输入参数
    def set_params(self, params):
        # 设置输入参数
        self.params = params

        # 设置计算预估时长
        self._progress.set(in_interval_seconds=1, in_est_total_seconds=10)

    # 开始计算
    def start_calculate(self):
        # 每个用户，正在计算时，无法并行新建计算，此时只能查询状态
        if self.mp_status!=Status.CALCULATING:
            # 设置开始计算状态
            self.mp_status.set(Status.CALCULATING)

            self._task.init(target=self.calculate_func)
            self._task.start()

    def finished_callback(self):
        pass

    def calculate_func(self, output):
        # =================注意，这里位于新的进程中，self所指向的是新进程中的clone出来的self，因此这里的状态变量都要用multiprocess的进程间共享变量==================
        # 计时器必须在这里start()以确保计时器处于本进程中。如在start_calculate()中start()，会因为task启动后主进程退出导致报错。
        self._progress.start()

        # ==================计算过程==================
        case2()
        # ==================计算过程==================

        # 组织计算结果
        self._set_result()

        # 设置计算完成状态
        self.mp_status.set(Status.RESOLVED)
        self._progress.finish()
        # =================注意，这里位于新的进程中，self所指向的是新进程中的clone出来的self，因此这里的状态变量都要用multiprocess的进程间共享变量==================

    # 获取计算进度
    def get_progress(self):
        return self._progress.get_progress()

    # 获取计算中间输出
    def pop_tee(self):
        return self._mp_tee.get()
        # t_list = []
        # for i in range(len(self._tee)) :
        #     t_list.append(self._tee.pop(0))
        # return t_list

    # 日志输出到tee
    def add_tee(self, string):
        self._mp_tee.put(string)
        # self._tee.append(string)

    # 组织计算结果
    def _set_result(self):
        pass

    # 获取计算结果输出数据
    def get_result(self):
        return self._result

    def join(self):
        self._task._join()

def case2():
    print("--------------------案例\"{}\"为冷热电氢系统测试分析--------------------".format(Get_Current_Func_Name()))
    # if in_called==False:
    #     return

    # t_simu_hours = 1
    t_simu_hours = 24
    # t_simu_hours = 720
    # t_simu_hours = 24*365
    # t_simu_hours = 24*365*2
    # t_simu_hours = 24*365*10
    # t_simu_hours = 24*365*25

    t_simu_years = t_simu_hours//8760

    # =========================节点0=========================
    t_sys = Sys(
        in_share_y=True,
        in_name_id="sys1",
        in_simu_hours=t_simu_hours,
        in_rate=0.08,
        in_spring_festival=Spring_Festival(in_years=t_simu_years, in_bypass=False, in_start_day=10, in_stop_day=60),
        in_investor="government",
        # in_investor="user_finance", # 本案例为用户财务测算
        in_investor_user_discount=0.1,  # "user_finance"时的电价折扣
        in_analysis_day_list=[0,90,180,270]
        # in_analysis_day_list=0
    )
    # t_sys.Add_Elec_Bus()
    t_sys.Add_Elec_Bus(in_if_reference_bus=True)

    # t_sys.print_objfunc = True

    # ============负荷============
    t_file = XLS_File('xls/data_analysis_multi.xlsx', in_cols=[0,1,2], in_row_num=8761)
    t_load1 = Load(in_sys=t_sys, in_name_id="elec load", in_p_nom=1000) # kW
    t_load1.set_one_year_p(t_file.get_list("负荷"))   #负荷数据的正负一定要搞清楚，对结果影响非常大

    # ============一次能源============
    # t_source = Primary_Energy(t_sys, "gas1")

    # ============发电============
    # 财务效益
    # t_diesel1 = Plant(t_sys, "diesel1", in_p_nom=1000, in_p_nom_extendable=False)

    # 社会效益
    # t_diesel1 = Plant(t_sys, "coal1", in_p_nom=500, in_p_nom_extendable=True)      #对容量进行优化，且存量3393kW不计投资
    # t_diesel1.p_max_pu["value"]=1.0
    # t_diesel1.p_min_pu["value"]=0.15
    # t_diesel1.capital_cost["value"]=1.0     # 美元/W
    # t_diesel1.marginal_cost["value"]=0.242  # 美元/kWh

    # ============光伏============
    t_pv1 = NE_Plant(in_sys=t_sys, in_name_id="pv", in_p_nom=0, in_p_nom_extendable=True)
    t_pv1.marginal_cost["value"]=0.0
    t_pv1.capital_cost["value"]=4.0     # 元/W
    t_pv1.set_one_year_p(t_file.get_list("光伏"), in_is_pu=True)   #光伏数据，实际只需要特性

    # ============风电============
    # t_wind1 = NE_Plant(in_sys=t_sys, in_name_id="wind", in_p_nom=1200, in_p_nom_extendable=True)    #对容量进行优化，且存量1200kW不计投资
    # t_wind1.marginal_cost["value"]=0.0
    # t_wind1.capital_cost["value"]=6.367      # IEA 2050 中国造价
    # t_wind1.set_one_year_p(t_file.get_list("风电"), in_is_pu=True)   #光伏数据，实际只需要特性

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
                            in_e_nom_extendable=True,
                            in_charge_effi = 0.95,
                            in_discharge_effi = 0.95    # discharge_effi必须在Energy_Storage初始化时输入（受component的constraint_effi初始化影响）
                            )
    # t_ess1.charge_marginal_cost["value"] = 0.0          # 计算社会效益时，储能与用户转移支付，成本为0
    # t_ess1.discharge_marginal_cost["value"] = -0.0      # 计算社会效益时，储能与用户转移支付，成本为0
    t_ess1.charge.marginal_cost["value"] = 0.0          # 计算财务效益时，采用内部的用户电价price_list，marginal_cost即燃料成本为0
    t_ess1.discharge.marginal_cost["value"] = -0.0      # 计算财务效益时，采用内部的用户电价price_list，marginal_cost即燃料成本为0
    t_ess1.charge.capital_cost["value"] = 0.12          # 元/W
    t_ess1.discharge.capital_cost["value"] = 0.12       # 元/W
    t_ess1.capital_cost_e["value"] = 1.38               # 元/Wh
    # t_ess1.capital_cost_p2["value"] = 0.4    #设备换新的成本
    # t_ess1.capital_cost_e2["value"] = 1.0    #设备换新的成本
    # t_ess1.capital_cost2_year["value"] = 10       #设备更换的年限

    # ===slack节点仅用作强制的、无成本的功率调节===（有成本的用plant模拟）
    # 吸收松弛节点
    t_slack_node1 = Absorption_Slack_Node(
        t_sys,
        in_name_id="sl_absorp",
        in_p_max=0,    # kW
        in_p_nom_extendable=False,
        in_e_max=0*8760 * t_simu_years,         # 设置了1.5MW的功率限额
        # in_marginal_cost=0)                     # government, 这里必须若考虑新能源倒送成本，则应为负值，即乘以负的功率，成本为正
        in_marginal_cost=-0)                     # user_finance，这里必须若考虑新能源倒送成本，则应为负值，即乘以负的功率，成本为正(mc=-0.1,能够有效的防止财务盈利储能在尖峰放电时功率超过负荷)
    t_slack_node1.e_output = True

    # 注入松弛节点
    t_slack_node2 = Injection_Slack_Node(
        t_sys,
        in_name_id="sl_inject",
        in_p_max=0,
        in_p_nom_extendable=False,
        in_e_max=0*8760 * t_simu_years,
        # in_marginal_cost=0)                     # government, 考虑的注入电量影子成本，输配电价暂考虑0.2元/kWh
        in_marginal_cost=0)                   # user_finance, 考虑的注入电量成本，计算光伏、储能等项目的财务成本时，用户向电网购电成本应为正值
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

    # =========================heat 节点1=========================
    t_sys.Add_Bus()
    # 电锅炉
    t_p2heat = Oneway_Link(t_sys,
                        in_p_nom=0,
                        in_p_nom_extendable=True,
                        in_capital_cost=0.2,
                        in_bus0_id=0,
                        in_bus1_id=1,
                        in_name="elec boiler",
                        in_effi=0.95,
                        in_p_max_pu=1.0,
                        in_p_min_pu=0.0,
                        )

    t_load2 = Load(in_sys=t_sys, in_name_id="heat load", in_p_nom=1500)
    t_load2.set_one_year_p(t_file.get_list("负荷"))   #负荷数据的正负一定要搞清楚，对结果影响非常大

    # =========================gas 节点2=========================
    t_sys.Add_Bus()
    # 一次能源天然气
    t_gas = Primary_Energy_Supply(t_sys, in_name_id="gas", in_marginal_cost=0.3)      # 天然气若3元/方，由于1方天然气热值10kWh，因此大约为0.3元/kWh

    # 燃机
    t_gas2p = Oneway_Link(t_sys,
                        in_p_nom=0,
                        in_p_nom_extendable=True,
                        in_capital_cost=2.2,
                        in_bus0_id=2,
                        in_bus1_id=0,
                        in_name="gas turbine",
                        in_effi=0.5,
                        in_p_max_pu=1.0,
                        in_p_min_pu=0.0,
                        )

    t_chp = Cogeneration(t_sys,
                        in_p_nom=0,
                        in_p_nom_extendable=True,
                        in_capital_cost=1.75,       # CHP造价3.5元/W，由于是折算到电功率，因此这里可能填1.75
                        in_ratio_12=1.0,            # 热电比
                        in_bus0_id=2,
                        in_bus1_id=1,
                        in_bus2_id=0,
                        in_name="CHP",
                        in_effi=0.8,
                        in_p_max_pu=1.0,
                        in_p_min_pu=0.0
                        )

    t_sys.Add_Elec_Bus()
    t_line1 = Elec_Branch(t_sys, in_name="line1", in_bus0_id=0, in_bus1_id=3, in_reactance_pu=0.000097 * 100 / (525 * 525 / 100))
    t_elec_load1 = Load(in_sys=t_sys, in_name_id="elec load 1", in_p_nom=3000)
    t_elec_load1.set_one_year_p(t_file.get_list("负荷"))   #负荷数据的正负一定要搞清楚，对结果影响非常大

    t_sys.Add_Elec_Bus()
    t_line2 = Elec_Branch(t_sys, in_name="line2", in_bus0_id=0, in_bus1_id=4, in_reactance_pu=0.000097 * 100 / (525 * 525 / 100))
    t_elec_load2 = Load(in_sys=t_sys, in_name_id="elec load 2", in_p_nom=1500)
    t_elec_load2.set_one_year_p(t_file.get_list("负荷"))   #负荷数据的正负一定要搞清楚，对结果影响非常大

    t_line3 = Elec_Branch(t_sys, in_name="line3", in_bus0_id=3, in_bus1_id=4, in_reactance_pu=0.000097 * 100 / (525 * 525 / 100))
    # t_line3 = Elec_Branch(t_sys, in_name="line3", in_bus0_id=4, in_bus1_id=3, in_reactance_pu=10)

    # 该线路电抗为标准输入水平
    # t_line1 = Elec_Branch(t_sys, in_name="line1", in_bus0_id=0, in_bus1_id=3, in_reactance_pu=0.000097 * 100 / (525 * 525 / 100))  # 100km的1回500kV 4*630mm2线路

    t_sys.do_optimize()

# 测试
def main():
    user1 = NPS_User_Session(329)
    print("user id is [{}] status is [{}]".format(user1.user_id, user1.mp_status))
    user1.start_calculate()
    print("user id is [{}] status is [{}]".format(user1.user_id, user1.mp_status))
    user1.join()
    print("user id is [{}] status is [{}]".format(user1.user_id, user1.mp_status.get()))

if __name__ == "__main__" :
    main()