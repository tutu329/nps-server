# my_books/middlewares.py
from django.contrib.auth.models import User

# 添加对上一级目录import的支持
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Python_User_Logger import *

from .Chat_GPT import *
from .models import *

from .admin_update_all_users_once import *

class Chatgpt_Middleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.inited = False

    def __call__(self, request):
        if not self.inited:
            printd("===========================================================================Django db inited(0).=================================================================================")

            Chatgpt_Server_Config.gpt_server_init_from_db()

            all_users = User.objects.all()
            for user in all_users:
                printd(user.username)
            self.inited = True

            printd("=========================Chatgpt server started with status:===============================")
            printd("user level index is : {}".format(Chatgpt_Server_Config.s_user_level_index))
            printd("user level fee is : {}".format(Chatgpt_Server_Config.s_user_level_fee))
            printd("user template is : {}".format(Chatgpt_Server_Config.s_server_user_template))
            printd("server config is : {}".format(Chatgpt_Server_Config.s_user_config))

            printd("==========================================user data==========================================")
            for key, value in Chatgpt_Server_Config.s_users_data.items():
                printd("--------------------------user: {}, user_nick: {}--------------------------".format(key, value["user_nick"]))
                printd("password: {}".format(value["password"]))
                printd("user_nick: {}".format(value["user_nick"]))
                printd("gender: {}".format(value["gender"]))
                printd("user_level: {}".format(value["user_level"]))
                printd("vip_expired: {}".format(value["vip_expired"]))
                printd("vip_start_time: {}".format(value["vip_start_time"]))
                printd("roles: {}".format(value["roles"]))

            printd("==========================================role template==========================================")
            for key, value in Chatgpt_Server_Config.s_server_role_template.items():
                printd("--------------------------Role: {}, nickname: {}--------------------------".format(key, value["nickname"]))
                printd("chatgpt_para: {}".format(value["chatgpt_para"]))
                printd("can_use: {}".format(value["can_use"]))
                printd("chat_list_max: {}".format(value["chat_list_max"]))
                printd("chat_persistence: {}".format(value["chat_persistence"]))
                printd("role_prompt: {}".format(value["role_prompt"]))
                printd("active_talk_prompt: {}".format(value["active_talk_prompt"]))

            printd("===========================================================================Django db inited(1).=================================================================================")
            try:
                # ======================！！！注意：这个更新函数只能运行一次，运行完就注释掉，再运行时，必须确保不损坏已有数据！！！======================
                # ======================！！！注意：这个更新函数只能运行一次，运行完就注释掉，再运行时，必须确保不损坏已有数据！！！======================
                pass
            except Exception as e:
                print("============fatal: admin db update all users invoke(once) error============: {}".format(e))

        response = self.get_response(request)
        return response
