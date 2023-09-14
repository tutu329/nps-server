from multiprocessing import Process, Lock, Manager, freeze_support
from threading import Thread
import threading
from enum import Enum
from NPS_Case import *
from Stop_Thread import *

from Python_User_Logger import *
from NPS_Invest_Opt_Base import *
from Data_Analysis import *
from User_Session import *

import time

class Status(Enum):
    UNSTARTED = 0
    PROCESSING = 1
    FINISHED_WAITING_CLOSE = 2
    TO_CLOSE = 3
    CLOSED = 4
    KILLED = 5

# 注意：mod_wsgi在windows下，只能采用winnt模式，只能有1个进程，因此新建的进程一定会挂起，因此process方案在mod_wsgi下不可行！！！
# 用户任务的独立线程/进程（针对pyomo可能无法在非主线程执行计算的情况，封装User_Task类，与具体的thread或process实现隔离，方便切换策略）
# ======本类目前为一个task一个进程，每个task的输出方式包括：1）用具有唯一性的文件（用带user_id的文件名），2）用进程间共享的Manager()======
class User_Process_Task():
    S_DEBUG = False
    def __init__(self, **kwargs):
    # 参数: target (注意：target函数必须是包含mp_result_dict的函数，即新封装的函数，而不能是已有函数，因为mp_result_dict为强制传入的额外参数，供共享用)
    # 参数: name (调用的函数名称)
    # 参数: task_timeout=0 (task完成后超时timeout秒后退出, 0则不超时)
        self._initialized = False
        self._task = 0
        self._task_name = ""
        self._task_timeout = 0

        print("thread is : \"{}\"".format(threading.current_thread().name))
        print("-----1-----")
        freeze_support()
        print("-----2-----")
        self._mp_result_dict = Manager().dict()                         #进程共享的dict，必须用update()赋值，否则赋值会无效
        print("-----3-----")
        self._mp_status = Manager().Value(Status, Status.UNSTARTED)  #进程共享的变量，必须用set()赋值，否则赋值后会变为普通变量
        print("-----4-----")
        self._mp_lock = Lock()

        print("-----5-----")

        # self.callback_func = 0
        # self.callback_args = 0

        self.init(**kwargs)     # 这里是传**kwargs而不是kwargs
        print("-----6-----")
        # print(**kwargs)
        # print(kwargs)

    # 必要的初始化，向Process()注册target函数和参数
    def init(self, **kwargs):
        if not self._initialized :
            if len(kwargs) > 0:
                # 向Process()传送(output, target, kwargs)
                if kwargs.get("task_timeout") :
                    self._task_timeout = kwargs.pop("task_timeout")
                if kwargs.get("name") :
                    self._task_name = kwargs.pop("name")
                if kwargs.get("target") :
                    t_target_func = kwargs.pop("target")
                else:
                    self._debug_print("param \"target\" not found.")
                    return

                with self._mp_lock :
                    self._task = Process(
                        args=tuple((self._mp_result_dict,)),    # 将进程间共享的out_dict传给target函数
                        target=t_target_func,                   # target函数地址
                        kwargs=kwargs,                          # target函数的参数
                    )
                self._initialized = True

    # callback暂时不需要（可以用于后台主动向前端推送计算结果）
    # def set_callback(self, **kwargs):
    #     self.callback_func = kwargs.pop("target")
    #     self.callback_args = kwargs.values()

    # 启动task
    def start(self):
        if self._initialized :
            with self._mp_lock:
                self._mp_status.set(Status.PROCESSING)
            self._task.start()

            t_thread = Thread(target=self._waiting_thread)
            t_thread.start()

    def _waiting_thread(self):
        self._task.join()
        with self._mp_lock:
            self._mp_status.set(Status.FINISHED_WAITING_CLOSE)

        t_time = time.perf_counter()

        # 一直waiting close
        while True:
            with self._mp_lock:
                if self._mp_status.get()== Status.TO_CLOSE:
                    # 如果前端已完成结果查询、已通知TO_CLOSE，则退出
                    break
            if self._task_timeout > 0:
                # 如果设置了超时，则超时后不管是否有请求，都退出
                if time.perf_counter() - t_time >= self._task_timeout:
                    with self._mp_lock:
                        self._mp_status.set(Status.TO_CLOSE)
                    break
            time.sleep(0.2)
            print("status is {}".format(self._mp_status.get()))

        with self._mp_lock:
            self._mp_status.set(Status.CLOSED)
            self._debug_print("Task closed.")

    def _join(self):
        if self._initialized :
            self._task.join()

    # 用于前端查询处理情况
    def get_status(self):
        with self._mp_lock:
            return self._mp_status.get()

    # 用于前端查询处理结果
    def get_result(self):
        with self._mp_lock:
            return self._mp_result_dict

    # 用于前端查询完处理结果后，释放资源
    def close(self):
        with self._mp_lock:
            if self._mp_status.get()==Status.FINISHED_WAITING_CLOSE:
                self._mp_status.set(Status.TO_CLOSE)
                self._task.close()

    # kill Process()的进程，似乎不起作用
    def kill(self):
        self._task.kill()

    def _debug_print(self, *args, **kwargs):
        if User_Process_Task.S_DEBUG:
            print("【User_Process_Task DEBUG】{}:".format(self._task_name), end=" ")
            print(*args, **kwargs)

# 与open-id绑定的一对一对象
class User_Job():
    def __init__(self):
        self._task = 0
        self._stream = 0
        self._custom_data_dict = {}  # 如{ "电负荷" : elec_load_list, "热负荷" : heat_load_list }

    def update_task(self, in_task_obj):
        self._task = in_task_obj

    def update_stream(self, in_stream_obj):
        self._stream = in_stream_obj

    def update_custom_data_dict(self, in_custom_data_dict_obj):
        self._custom_data_dict = in_custom_data_dict_obj

    def get_task(self):
        return self._task

    def get_stream(self):
        return self._stream

    def get_custom_data_dict(self):
        return self._custom_data_dict

# ===============================检测：用户自定义的8760h和分时电价excel文件是否有误================================
def import_user_8760h_excel(in_filename, in_open_id) :
    rtn_names = []
    t_rows = [8760,8760,8760,8760,8760,8760,24]
    t_names = [
        {"name":"电负荷","rows":8760, "verbose":"elec_load"},
        {"name":"光伏","rows":8760, "verbose":"pv"},
        {"name":"风电","rows":8760, "verbose":"wind"},
        {"name":"水电","rows":8760, "verbose":"hydro"},
        {"name":"热负荷","rows":8760, "verbose":"heat_load"},
        {"name":"冷负荷","rows":8760, "verbose":"cold_load"},
        {"name":"分时电价","rows":24, "verbose":"price"},
    ]
    t_file = XLS_File(Global.get("path")+'static/upload/'+in_filename, in_cols=range(len(t_names)), in_row_num=8761) # 电负荷、光伏、风电、水电、热负荷、冷负荷、分时电价
    if t_file!=None :

        # ======================= 向 User_Session 的dict中，注册job信息 =======================
        t_dict = {}

        # 从excel读取数据 ，并检查数据长度是否合理
        for t_name in t_names :
            # print("name is {}".format(t_name))
            t_list = t_file.get_list(t_name["name"])
            if t_list!=None:
                if len(t_list)!=t_name["rows"] :
                    print("{} rows wrong, is {} ，is not {}".format(t_name["verbose"], len(t_list), t_name["rows"]))
                    return "{} 数据长度错误，仅为 {} 不为 {}".format(t_name["name"], len(t_list), t_name["rows"])

                rtn_names.append(t_name["name"])
                t_dict[t_name["name"]] = t_list

        # 尝试新注册job，由session返回已存在的job或新的job引用
        s_users_session = WX_Users_Session()
        t_job = s_users_session.Get_User_Data_by_ID(in_open_id, in_try_user_data_obj=User_Job())
        t_job.update_custom_data_dict(in_custom_data_dict_obj=t_dict)

        print("user_8760h data imported.")
        # print("imported dict为: {}".format(s_users_session.Get_User_Data(in_open_id).get_custom_data_dict().keys()))
        for key in s_users_session.Get_User_Data_by_ID(in_open_id).get_custom_data_dict() :
            print("imported data len is: {}, first data is : {}".format(
                len(s_users_session.Get_User_Data_by_ID(in_open_id).get_custom_data_dict()[key]),
                s_users_session.Get_User_Data_by_ID(in_open_id).get_custom_data_dict()[key][0]
            ))
        # print("导入dict为: {}".format(s_users_session.Get_User_Data_by_ID(in_open_id).get_custom_data_dict()))
        # ======================= 向 User_Session 的dict中，注册job信息 =======================

        if len(rtn_names)==0:
            return "文件中没有有效数据"
        else:
            t_string = ""
            for i in rtn_names :
                t_string = t_string + "\"" + i + "\""+ "、"
            t_string = t_string[0:len(t_string)-3]  # 去除最后一个"、"
            return "成功导入 "+t_string
    else:
        return "打开文件错误"


# 注意：用User_Thread_Task调用pyomo计算任务，在本文件main()中运行会报错（ValueError: signal only works in main thread），但在view中运行正常。
class User_Thread_Task():
    S_DEBUG = False
    def __init__(self, **kwargs):
    # 参数: target (注意：target函数必须是包含mp_result_dict的函数，即新封装的函数，而不能是已有函数，因为mp_result_dict为强制传入的额外参数，供共享用)
    # 参数: name (调用的函数名称)
    # 参数: task_timeout=0 (task完成后超时timeout秒后退出, 0则不超时)
        self._initialized = False
        self._task = 0
        self._waiting_thread = 0
        self._task_name = ""
        self._task_timeout = 0

        # print("thread is : \"{}\"".format(threading.current_thread().name))
        self._result_dict = {}                  #线程共享的dict，必须用update()赋值，否则赋值会无效
        self._status = "Status.UNSTARTED"         #线程共享的变量，必须用set()赋值，否则赋值后会变为普通变量

        # 注册用户计算进度
        self._progress = Progress()
        self._progress.set_progress_callback_func(self._callback_func_progress)
        self.interval_seconds = 1
        self.est_total_seconds = 10

        # 本实例的线程lock
        self._lock = threading.Lock()

        # self.callback_func = 0
        # self.callback_args = 0

        self.init(**kwargs)     # 这里是传**kwargs而不是kwargs
        # print(**kwargs)
        # print(kwargs)

    # 进度的回调函数
    def _callback_func_progress(self, callback_progress, callback_dots_num):
        t_dots = callback_dots_num * "."
        if User_Thread_Task.S_DEBUG :
            print("\r", end="", flush=True)
        self._debug_print("{}% completed{}".format(round(callback_progress), t_dots), end="", flush=True)

    # 必要的初始化，向Process()注册target函数和参数
    def init(self, **kwargs):
        if not self._initialized :
            if len(kwargs) > 0:
                # 向Process()传送(output, target, kwargs)
                if kwargs.get("task_timeout") :
                    self._task_timeout = kwargs.pop("task_timeout")
                if kwargs.get("name") :
                    self._task_name = kwargs.pop("name")
                if kwargs.get("interval_seconds"):
                    self.interval_seconds = kwargs.pop("interval_seconds")
                if kwargs.get("est_total_seconds"):
                    self.est_total_seconds = kwargs.pop("est_total_seconds")
                if kwargs.get("target") :
                    t_target_func = kwargs.pop("target")
                else:
                    self._debug_print("【error】 param of \"target\" not found.", flush=True)
                    return

                # 设置计时器的刷新频率(秒）和估计总用时(秒)
                self._progress.set(in_interval_seconds=self.interval_seconds, in_est_total_seconds=self.est_total_seconds)

                with self._lock :
                    self._task = Thread(
                        name=self._task_name,
                        args=tuple((self._result_dict,)),       # 将进程间共享的out_dict传给target函数
                        target=t_target_func,                   # target函数地址
                        kwargs=kwargs,                          # target函数的参数
                    )
                self._initialized = True

    # callback暂时不需要（可以用于后台主动向前端推送计算结果）
    # def set_callback(self, **kwargs):
    #     self.callback_func = kwargs.pop("target")
    #     self.callback_args = kwargs.values()

    # 启动task
    def start(self):
        if self._initialized :
            self._progress.start()

            with self._lock:
                self._status = "Status.PROCESSING"
            self._task.start()

            self._waiting_thread = Thread(target=self._waiting_thread_func)
            self._waiting_thread.start()

    def _waiting_thread_func(self):
        self._task.join()

        with self._lock:
            if self._status != "Status.KILLED" :
                self._status = "Status.FINISHED_WAITING_CLOSE"

        self._progress.finish()

        t_time = time.perf_counter()

        # 一直waiting close
        while True:
            with self._lock:
                if self._status == "Status.TO_CLOSE" or self._status == "Status.KILLED":
                    # 如果前端已完成结果查询、已通知TO_CLOSE，则退出
                    break
            if self._task_timeout > 0:
                # 如果设置了超时，则超时后不管是否有请求，都退出
                if time.perf_counter() - t_time >= self._task_timeout:
                    with self._lock:
                        self._status = "Status.TO_CLOSE"

            time.sleep(0.2)
            self._debug_print("{}".format(self._status), flush=True)

        with self._lock:
            self._status = "Status.CLOSED"
            self._debug_print("{}".format(self._status), flush=True)

    def _join(self):
        if self._initialized :
            self._task.join()

    # 用于前端查询处理情况
    def get_status(self):
        with self._lock:
            return self._status

    # 查询result（通常是父线程中调用）
    def get_result_dict(self):
        with self._lock:
            return self._result_dict

    # 更新result（通常是子线程target func中调用）
    # 该函数：子线程访问不到(因为没有User_Thread_Task实例引用)，只能子线程调用out_result_dict.update(...)
    # def update_result_dict(self, in_result_dict):
    #     with self._lock:
    #         self._result_dict.update(in_result_dict)

    # 强制停止线程
    def kill(self):
        self._debug_print("{尝试强制停止}", flush=True)
        with self._lock:
            if self._status == "Status.FINISHED_WAITING_CLOSE" :
                Stop_Thread(self._waiting_thread)
                self._debug_print("{任务已经停止}", flush=True)
                return

        with self._lock:
            if self._status == "Status.PROCESSING" :
                Stop_Thread(self._task)
                self._debug_print("{任务已经停止}", flush=True)
                self._status = "Status.KILLED"
                self._progress.finish()
                return

    # 用于前端查询完处理结果后，释放资源
    def close(self):
        with self._lock:
            if self._status=="Status.FINISHED_WAITING_CLOSE":
                self._status="Status.TO_CLOSE"
                # self._task._stop()

    # 获取计算进度
    def get_progress(self):
        return self._progress.get_progress()

    def _debug_print(self, *args, **kwargs):
        if User_Thread_Task.S_DEBUG:
            print("【User_Thread_Task \"{}\" DEBUG】: ".format(self._task_name), end=" ", flush=True)
            print(*args, **kwargs)

# func的第一个参数必须是，比User_Task()的初始化参数多出来的一个参数如mp_result_dict(用于进程间通信的dict)
def exam_task1(mp_result_dict, i, x):
    case2()
    mp_result_dict.update({"user":{"name": "func1", "value":x}})
    time.sleep(3)

# def task1_callback(result):
#     print("func1 callback finished.")
#     print("func1 output is : {}".format(result))

def case2():
    print("--------------------案例\"{}\"为冷热电氢系统测试分析--------------------".format(Get_Current_Func_Name()))
    # if in_called==False:
    #     return

    # t_simu_hours = 1
    # t_simu_hours = 24
    # t_simu_hours = 720
    t_simu_hours = 24*365
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

# func的第一个参数必须是，比User_Task()的初始化参数多出来的一个参数如mp_result_dict(用于进程间通信的dict)
def exam_task2(mp_result_dict, i, x):
    # case2()
    mp_result_dict.update({"game1": "eldur ring", "game2": "king of fighter"})
    time.sleep(2)

def task1(mt):
    print("task1 entered")
    case2()

def task3(mt, in_klass, in_case, in_path):
    Call_Class_Funcs(in_klass=NPS_Case, in_case="case32", in_path=Global.get("path") + "xls/")

# example
def main1():
    import Global
    Global.init()

    User_Process_Task.S_DEBUG = True

    t_task1 = User_Process_Task()
    print("------------------------task1 status is : {}------------------------".format(t_task1.get_status()))
    t_task1.init(name="task1", target=task1, in_klass=NPS_Case, in_case="case32", in_path=Global.get("path") + "xls/", task_timeout=2)         # 必须要有target参数指定调用的函数, task_timeout=0时一直waiting
    # t_task1.init(name="task1", target=exam_task1, x=[4, 5, 6], i=23, task_timeout=2)         # 必须要有target参数指定调用的函数, task_timeout=0时一直waiting
    # t_task1.init(target=exam_task1, x=[4, 5, 6], i=23, callback=task1_callback)         # 必须要有target参数指定调用的函数
    t_task1.start()
    print("just started------------------------task1 status is : {}------------------------".format(t_task1.get_status()))

    # t_task2 = User_Process_Task(name="task2", target=exam_task2, i=30, x=[1, 2, 3], task_timeout=2)  # 必须要有target参数指定调用的函数
    # t_task2.start()

    # 通常设置callback，而不用join()来等待task的完成（是阻塞等待）
    # t_task1.join()
    # t_task2.join()
    # print("------------------------task1 status is : {}------------------------".format(t_task1.get_status()))

    # 模仿前端polling发现task已经完成后，取回结果数据，并close task
    print("------------------------task1 status is : {}------------------------".format(t_task1.get_status()))
    time.sleep(4)
    t_result = t_task1.get_result()
    print("task1 result is : {}".format(t_result))
    print("------------------------task1 status is : {}------------------------".format(t_task1.get_status()))
    # t_task1.close()
    # t_task2.close()
    print("------------------------task1 status is : {}------------------------".format(t_task1.get_status()))
    # print("------------------------task2 status is : {}------------------------".format(t_task2.get_status()))
    time.sleep(1)
    print("------------------------task1 status is : {}------------------------".format(t_task1.get_status()))
    # print("------------------------task2 status is : {}------------------------".format(t_task2.get_status()))

def main():
    import Global
    Global.init()

    User_Thread_Task.S_DEBUG = True

    t_task1 = User_Thread_Task()
    t_task1.init(name="task1", target=task1, task_timeout=2, est_total_seconds=600)         # 必须要有target参数指定调用的函数, task_timeout=0时一直waiting
    # t_task1.init(name="task1", target=task3, in_klass=NPS_Case, in_case="case32", in_path=Global.get("path") + "xls/", task_timeout=2)         # 必须要有target参数指定调用的函数, task_timeout=0时一直waiting
    t_task1.start()
    time.sleep(4)
    t_result = t_task1.get_result_dict()
    print("task1 result is : {}".format(t_result))
    print("------------------------task1 status is : {}------------------------".format(t_task1.get_status()))
    print("------------------------task1 status is : {}------------------------".format(t_task1.get_status()))
    time.sleep(1)
    print("------------------------task1 status is : {}------------------------".format(t_task1.get_status()))


if __name__ == "__main__" :
    main()
