from celery import shared_task

from django.contrib.auth.models import User
from app_chatgpt.Chat_GPT import *
from .models import *

# 添加对上一级目录import的支持
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Python_User_Logger import *

# 每晚0时，对所有的user，更新{vip_days、user_level、current_vip_type、current_role_id、invoke_num_left_today}
@shared_task
def check_all_users_vip_expired():
    all_users = User.objects.all()

    for user in all_users:
        try:
            user_profile_obj = UserProfile.objects.get(user=user)
            print("===================\"{}\"===================".format(user.username), end="")
            # print("start check user \"{}\"'s vip info.".format(user.username), end="")
            print("\t vip start time is: {}".format(user_profile_obj.vip_start_time), end="")
            print("\t vip days is: {}".format(user_profile_obj.vip_days), end="")

            # ========================================================每日对user权限数据进行的更新================================================
            # ====== 每日vip_days -1 ======
            if user_profile_obj.vip_days>0:
                user_profile_obj.vip_days -= 1

            # ====== 每日检查是否VIP过期，过期改为free_user ======
            vip_expired = Chatgpt_Server_Config.vip_expired(user.username)
            if vip_expired:
                user_profile_obj.user_level = 1
                user_profile_obj.current_vip_type = "free_user"
                user_profile_obj.current_role_id = "default_role"

            # ====== 每日根据user_level恢复调用次数(如何剩余数量小于每日恢复数量) ======
            if user_profile_obj.gpt4_invoke_num_left_today<Chatgpt_Server_Config.GPT4_max_invokes_per_day(user_profile_obj.user_level):
                user_profile_obj.gpt4_invoke_num_left_today = Chatgpt_Server_Config.GPT4_max_invokes_per_day(user_profile_obj.user_level)
            if user_profile_obj.gpt3_invoke_num_left_today<Chatgpt_Server_Config.GPT3_max_invokes_per_day(user_profile_obj.user_level):
                user_profile_obj.gpt3_invoke_num_left_today = Chatgpt_Server_Config.GPT3_max_invokes_per_day(user_profile_obj.user_level)

            # ========================================================每日对user权限数据进行的更新================================================
            user_profile_obj.save()

            print("\t user \"{}\"'s vip is expired: [{}] ".format(user.username, vip_expired), end="")
        except Exception as e:
            print("\t error: {}".format(e))

@shared_task
def say_hello():
    print("hello")