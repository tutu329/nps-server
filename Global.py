import sys
import platform
import io
import logging

def log(*args, **kwargs):
    logging.debug(*args, **kwargs)

# 本项目的全局变量和设置
def init():  # 初始化
    global _dict

    # Global参数的初始化
    _dict = {
        "path": "",
        "stream": sys.stdout,
        "default_stdout": sys.stdout,
        "test_count": 0,
    }

    # 设置全局path
    if platform.system()=="Windows" :
        _dict["path"]= "C:/server/nps-server/"
    else:
        _dict["path"] = ""


    # stdout编码
    # sys.stdout.reconfigure(encoding='GBK')                    # after python3.7
    # sys.stdout.reconfigure(encoding='utf-8')                    # after python3.7
    # sys.stdout=codecs.getwriter("utf-8")(sys.stdout.buffer)     # before python3.7

# 用于测试线程操作是不是重复了
def test_count():
    _dict["test_count"] = _dict["test_count"] + 1
    return _dict["test_count"]

def std_file():
    # ============输出重定向到nps_log.txt============
    print("stdout changed to \"nps_log.txt\".", flush=True)
    set_std(log_filename=_dict["path"] + "nps_log.txt")
    # logging.basicConfig(filename=_dict["path"] + "nps_log.txt")
    # logging.debug("stdout changed to \"nps_log.txt\".")

def std_stream(in_stream=0):
    # 如果是后台，将print等重定向到文件（解决apache日志乱码等问题）
    if platform.system()=="Windows" :
        # ============输出重定向到Global.get("stream")============
        print("stdout changed to io.StringIO().", flush=True)
        if in_stream==0:
            _dict["default_stdout"].write("redirected to io.StringIO\n")
            set_std(log_filename=io.StringIO())
        else:
            _dict["default_stdout"].write("redirected to in_stream\n")
            set_std(log_filename=in_stream)


# 将print等重定向到文件（解决apache日志乱码等问题）
def set_std(log_filename, err_filename=0):
    if type(log_filename)==type(io.StringIO()):   # type()只考虑本类，instance()子类也算
        _dict["stream"] = log_filename
        sys.stdout = log_filename
    else:
        t_file = open(log_filename, "w+")
        _dict["stream"] = t_file
        sys.stdout = t_file

    if err_filename!=0 :
        _err_file = open(err_filename, "w+")
        sys.stderr = _err_file

def set(key, value):
    """ 定义一个全局变量 """
    _dict[key] = value

def get(key):
    return _dict.get(key)

# 用原有的标准输出print
def stdout(*args, **kwargs):
    _dict["default_stdout"].write(*args, **kwargs)

# 主文件中
# import Global
#
# Global._init()  # 先必须在主模块初始化（只在Main模块需要一次即可）
#
# # 定义跨模块全局变量
# Global.set('uuid', uuid)
# Global.set('token', token)

# 其他文件中
# import Global
#
# # 不需要再初始化了
# ROOT = Global.get('uuid')
# CODE = Global.get('token')