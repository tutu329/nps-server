import threading
import sys
from Python_User_Logger import *

#============================== WX_Users类为线程安全 ===================================

# 微信小程序用户的session管理
class WX_Users_Session():
    # 用户字典 {
    # "user_id1" : user_data1,
    # "user_id2" : user_data2
    # }
    S_DEBUG = False
    _s_users_dict = {}              # 如{"open_id":job_obj}, job_obj = {"task":task_obj, "stream":stream_obj}
    _s_lock = threading.RLock()     # 需采用递归锁（可重入锁），如父函数锁了，子函数也要锁，普通Lock就会死锁

    def __init__(self):
        pass

    # 线程安全的StringIO读取(自动刷新读写指针)
    def readlines(self, in_string_io):
        with WX_Users_Session._s_lock :
            in_string_io.seek(0)  # 指向缓冲的起点
            t_str_list = in_string_io.readlines()  # read缓冲中所有数据，转为string的list
            in_string_io.seek(0)  # 指向缓冲的起点，即重新开始输入数据
            in_string_io.truncate()  # 终点变为0
        return t_str_list

    # 本进程的_s_lock上锁
    def RLock(self):
        WX_Users_Session._s_lock.acquire()

    # 本进程的_s_lock解锁
    def RLock_Release(self):
        WX_Users_Session._s_lock.release()

    # 尝试添加数据引用，返回ID唯一的数据引用
    def Get_User_Data_by_ID(self, in_user_id, in_try_user_data_obj=None):
        with WX_Users_Session._s_lock :
            if WX_Users_Session._s_users_dict.get(in_user_id)!=None :
                # 有用户数据引用，不更新
                # WX_Users_Session._s_users_dict[in_user_id] = in_singleton_user_data
                return WX_Users_Session._s_users_dict[in_user_id]
            else :
                # 没有用户数据引用，则更新
                WX_Users_Session._s_users_dict[in_user_id] = in_try_user_data_obj
                return WX_Users_Session._s_users_dict[in_user_id]

    # # 查询用户data
    # def Get_User_Data(self, in_user_id):
    #     with WX_Users_Session._s_lock :
    #         # 1)没有该用户，则返回None
    #         # 2)有该用户，返回0或者data
    #         return WX_Users_Session._s_users_dict.get(in_user_id)

    # 用户是否有任务在执行
    def Task_Processing(self, in_user_id):
        with WX_Users_Session._s_lock :
            if self.Get_User_Data_by_ID(in_user_id)!=None and self.Get_User_Data_by_ID(in_user_id)!=0 :
                return True
            else:
                return False

    # 是否包含该用户
    def Logined(self, in_user_id):
        with WX_Users_Session._s_lock :
            return in_user_id in WX_Users_Session._s_users_dict

    # 输出所有用户ID
    def print_users(self):
        with WX_Users_Session._s_lock :
            self._debug_print(WX_Users_Session._s_users_dict)

    # 前端访问过
    # def Access(self, in_user_id):
    #     self.Register_User_Data(in_user_id=in_user_id)

    def _debug_print(self, *args, **kwargs):
        if WX_Users_Session.S_DEBUG:
            print("【WX_Users DEBUG】: ", end=" ", flush=True)
            print(*args, **kwargs)

# 测试
def main():
    WX_Users_Session.S_DEBUG = True

    users = WX_Users_Session()
    users.Get_User_Data_by_ID("0", 100)
    users.Get_User_Data_by_ID("1", 200)
    users.Get_User_Data_by_ID("2", 300)
    users.Get_User_Data_by_ID("2", 400)
    users.Get_User_Data_by_ID("3")
    users.Get_User_Data_by_ID("2")
    # users.Access("2")
    # users.Access("6")
    users.print_users()
    print("the user's data is : {}".format(users.Get_User_Data_by_ID("5")))
    print("the user has logined : {}".format(users.Logined("5")))

    # 测试对象ref数量（创建时为+1，被赋值后+1，被作为函数参数时+2，离开域时-1）
    # print("user data is : {}".format(sys.getrefcount(users.Get_User_Data_by_ID("2"))))

if __name__ == "__main__" :
    main()