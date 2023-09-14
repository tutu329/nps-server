import os
from copy import deepcopy
import inspect
import platform
import logging
import getpass
import threading
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import numpy as np
import json

def indent_string(in_dict):
    return json.dumps(in_dict, indent=2, ensure_ascii=False)    # ensure_ascii=False解决中文乱码问题

def is_win():
    return platform.system()=="Windows"

def is_mac():
    return platform.system()=="Darwin"

# 按每行固定数量打印list
def print_list(in_list, in_cols_num, in_float_dot_num=4, in_num=10):
    for i in range(len(in_list)):
        if i % in_cols_num == 0:
            print("[", i // in_cols_num, "] ", end="")
        if isinstance(in_list[i],float):    # 用type()有时候就不行
            print('{0:>{1}.{2}f}'.format(in_list[i], in_num, in_float_dot_num), " ", end="")
        else:
            print(in_list[i], " ", end="")
        if (i + 1) % in_cols_num == 0:
            print("")
    print("")

# 将一个list重复到一定的长度
# in_list:如len=24
# in_conv_len:如len=8760
def list_convolution(in_list, in_conv_len):
    list_len = len(in_list)

    # print("卷积次数：", in_conv_len//list_len+1)
    # print("差值：", (in_conv_len//list_len+1)*list_len-in_conv_len,"hours")
    in_list = in_list * (in_conv_len // list_len + 1)

    # print("卷积结果：")
    # print_list(in_list, in_cols_num=list_len)

    # print("截取后结果：")
    # print(len(in_list))
    # print((in_conv_len//list_len+1)*list_len-in_conv_len)
    in_list = in_list[:len(in_list) - ((in_conv_len // list_len + 1) * list_len - in_conv_len)]
    # print_list(in_list, in_cols_num=list_len)
    return in_list

# list和list的点积
# def list_sumproduct(in_list1, in_list2) :
#     return (np.mat(in_list1)*np.mat(in_list2).T)[0,0]

# list和list的点积(如果长度不相等，取短的长度)
def list_sumproduct(in_list1, in_list2) :
    t_sum = 0
    t_len = min(len(in_list1), len(in_list2))
    return sum(np.array(in_list1[:t_len]) * np.array(in_list2[:t_len]))

class XLS_File():
    def __init__(self, in_file_name, in_cols, in_row_num):
        self.pd_data = pd.read_excel(in_file_name, sheet_name=0, usecols=in_cols, nrows=in_row_num)
        # self.pd_data.dropna(inplace=True)

    def get_list(self, in_title_name):
        try:
            t_a = self.pd_data[in_title_name]
        except:
            return None
        a = list(t_a)
        b = []

        # 数据清洗
        for item in a :
            if item==item:
                # 数据正常，不为nan（不为空格）
                b.append(item)
            else:
                # 数据为 nan（为空格）
                b.append(0)

        # a = [a_ for a_ in a if a_ == a_]    # 删除nan
        return b
        # a = list(self.pd_data[in_title_name]).copy()
        # a = [a_ for a_ in a if a_ == a_]    # 删除nan
        # return a.copy()

def is_None_or_Nan(in_value):
    if in_value is None:
        return True
    if math.isnan(in_value):
        return True
    return False

# image流数据与json_utf8字符串的转换
class Tools():
    def __init__(self):
        pass

    def imagefile_to_json_utf8_string(self,in_file_name):
        t_img_file = open(in_file_name, 'rb')

        t_buffer = t_img_file.read()
        import base64
        t_base64_bytes = base64.b64encode(t_buffer)  # t_base64_bytes是二进制流
        return t_base64_bytes.decode("utf-8")  # t_base64_string是可以json的utf8字符串


# 用"#"连接多个字符串形成的长字符串
class Encoded_String():
    s_separator = "\n"

    def __init__(self, in_string=""):
        self._strings = in_string

    def __str__(self):
        return self._strings

    def get_string_list(self):
        return self._strings.split(Encoded_String.s_separator)

    def add_string(self, in_string):
        if self._strings != "" :
            self._strings = self._strings + Encoded_String.s_separator + in_string
        else :
            self._strings = in_string

# 显示进度的类
class Progress():
    def start(self):
        self._m_started = True
        logging.basicConfig()
        logging.getLogger('apscheduler').setLevel(logging.ERROR)
        self._m_progress = 0.0
        self._m_timer.start()

    def finish(self):
        self._m_progress = 0.0
        self._m_started = False
        self._m_timer.shutdown()
        self._m_progress_callback_func(100, 1)

    def pause(self):
        self._m_timer.pause()

    def resume(self):
        self._m_timer.resume()

    def set_progress_callback_func(self, in_progress_callback_func):
        self._m_progress_callback_func = in_progress_callback_func

    def get_progress(self):
        return round(self._m_progress)

    def __init__(self, in_interval_seconds=1, in_est_total_seconds=10):
        self._m_progress = 0.0     # 0~100
        self._m_est_total_seconds = round(in_est_total_seconds)
        self._m_interval = round(in_interval_seconds)
        self._m_dots_num = 1

        self._m_job_id_list = []
        self._m_timer = BackgroundScheduler()
        # 这里add_job返回的job对象不需要deepcopy，因为源码自身表明可以直接append
        self._m_job_id_list.append(self._m_timer.add_job(self._internal_callback_progress, trigger='interval', seconds=self._m_interval))
        self._m_progress_callback_func = 0

        # 根据估计总时间，设定每一次增长的进度量
        self.m_progress_each = 100.0 * self._m_interval / self._m_est_total_seconds

        self._m_started = False

    def set(self, in_interval_seconds, in_est_total_seconds):
        self._m_interval = round(in_interval_seconds)
        self._m_est_total_seconds = round(in_est_total_seconds)

        # 根据估计总时间，设定每一次增长的进度量
        self.m_progress_each = 100.0 * self._m_interval / self._m_est_total_seconds

    # 添加回调函数，回传参数为(self.m_progress,)

    def _internal_callback_progress(self):
        self._m_dots_num = (self._m_dots_num + 1) % 10000
        t_dots_num = self._m_dots_num % 4
        t_dots = t_dots_num * "."
        # print("\r{}% completed{}".format(round(self.m_progress), t_dots), end="")
        if round(self._m_progress + self.m_progress_each) < 100 :
            self._m_progress = self._m_progress + self.m_progress_each if self.m_progress_each <= 10 else 10
        else :
            self._m_progress = 99

        if self._m_progress_callback_func != 0:
            self._m_progress_callback_func(self._m_progress, t_dots_num)

# 日志管理类
class Python_User_Logger():
    s_if_print = False
    s_logger = 0
    s_system = ""
    s_user = ""
    s_log_index = 0
    # Python中，dict、list为动态变量，赋值是引用；数字、字符串是静态变量，赋值是copy
    # 【注意】，并发量大时，可能需要对Energy_Invest_Opt_Factory._g_user_opt_obj_dict加线程锁
    s_user_log_obj_dict_ref = 0

    @staticmethod
    def set_user_log_obj_dict_read_only_ref(in_user_log_obj_ref):
        Python_User_Logger.s_user_log_obj_dict_ref = in_user_log_obj_ref

    @staticmethod
    def program_start():
        if Python_User_Logger.s_if_print :
            pass
            # print("-----------------------------------------START------------------------------------------------")
            # print("Print mode is on, Log mode is off.")
        else:
            if Python_User_Logger.s_logger==0:
                # Python_User_Logger.s_logger.debug("-----------------------------------------START------------------------------------------------")
                # print("-----------------------------------------START------------------------------------------------", end="")
                # print("Print mode is off, Log mode is on.", end="")
                # print("This log file is located at : {}".format(os.getcwd() + "/python_user.log"), end="")

                Python_User_Logger.s_user = getpass.getuser()
                Python_User_Logger.s_logger = logging.getLogger("python_user_log") #静态变量，用于从logging.getLogger()返回唯一引用
                Python_User_Logger.s_logger.setLevel(logging.DEBUG)
                Python_User_Logger.s_system = platform.system()
                if Python_User_Logger.s_system=="Darwin":
                    t_log_file = logging.FileHandler("python_user.log")
                elif Python_User_Logger.s_system=="Windows":
                    t_log_file = logging.FileHandler("python_user.log")
                t_log_file.setLevel(logging.DEBUG)
                t_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
                # t_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
                t_log_file.setFormatter(t_formatter)
                Python_User_Logger.s_logger.addHandler(t_log_file)
                # Python_User_Logger.s_logger.debug(" ")
                Python_User_Logger.s_logger.debug(r"'"+Python_User_Logger.s_system+r"'"+" user \'"+Python_User_Logger.s_user+"\' invokes \'"+__file__+'\'.')

    @staticmethod
    def program_exit():
        if Python_User_Logger.s_if_print :
            print("------------------------------------------END-------------------------------------------------\n")
        else:
            Python_User_Logger.s_logger.debug(r"'"+Python_User_Logger.s_system+r"'"+" user \'"+Python_User_Logger.s_user+"\' exits \'"+__file__+'\'.')
            Python_User_Logger.s_logger.debug("------------------------------------------END-------------------------------------------------\n")

    @staticmethod
    def get_debug_func():
        def debug_func(msg, *args, **kwargs):
            if Python_User_Logger.s_logger==0:
                Python_User_Logger.program_start()
            Python_User_Logger.s_logger.debug(str(msg), *args, **kwargs)
            # 同时把日志分发（push）给所有client
            if Python_User_Logger.s_user_log_obj_dict_ref != 0 :
                for (k,v) in Python_User_Logger.s_user_log_obj_dict_ref.items():
                    v.append(deepcopy(str(msg)))
        if Python_User_Logger.s_if_print:
            return print
        else:
            return debug_func

    @staticmethod
    def log_num_list(in_list, in_list_name, in_format="{: >4.0f}", in_comma=", ", in_start="【", in_end="】", in_end_format="\n"):
        Python_User_Logger.get_debug_func()(in_list_name+" = "+in_start, end="")
        t_num = 0
        for i in range(len(in_list)) :
            if (t_num % 5 == 0) and ( t_num!=0 ) :
                Python_User_Logger.get_debug_func()("|", end="")
            Python_User_Logger.get_debug_func()((in_format+in_comma).format(in_list[i]), end="")
            t_num = t_num + 1
        Python_User_Logger.get_debug_func()(in_end, end=in_end_format)

    @staticmethod
    def get_id_debug_func():
        def id_debug_func(msg, *args, **kwargs):
            if Python_User_Logger.s_logger==0:
                Python_User_Logger.program_start()
            Python_User_Logger.s_logger.debug("===============["+str(Python_User_Logger.s_log_index)+"]===============\n"+str(msg), *args, **kwargs)
            Python_User_Logger.s_logger.debug("\n")
            Python_User_Logger.s_log_index = Python_User_Logger.s_log_index + 1
            # 同时把日志分发（push）给所有client
            if Python_User_Logger.s_user_log_obj_dict_ref != 0 :
                for (k,v) in Python_User_Logger.s_user_log_obj_dict_ref.items():
                    v.append(deepcopy(str(msg)))
        if Python_User_Logger.s_if_print:
            return print
        else:
            return id_debug_func

    @staticmethod
    def log_func_in():
        t_func_name = inspect.stack()[1][3]
        if Python_User_Logger.s_if_print:
            print("----------------------{}() {}----------------------".format(t_func_name, "↓↓↓"))
        else:
            Python_User_Logger.s_logger.debug("----------------------{}() {}----------------------".format(t_func_name, "↓↓↓"))

    @staticmethod
    def log_func_out():
        t_func_name = inspect.stack()[1][3]
        if Python_User_Logger.s_if_print :
            print("----------------------{}() {}----------------------".format(t_func_name, "↑↑↑"))
        else:
            Python_User_Logger.s_logger.debug("----------------------{}() {}----------------------".format(t_func_name, "↑↑↑"))

    @staticmethod
    def get_current_func_name():
        return inspect.stack()[1][3]

printd = Python_User_Logger.get_debug_func()
def printd_dict(in_dict):
    printd(json.dumps(in_dict, indent=2, ensure_ascii=False))
def print_dict(in_dict):
    print(json.dumps(in_dict, indent=2, ensure_ascii=False))
