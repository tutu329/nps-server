# 添加对上一级目录import的支持
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Python_User_Logger import *
import json

from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4

# from .Chat_GPT import *
from datetime import *

def now_2_str():
    return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')


# ==================================Django_User、UserProfile、Role、数据之间的关系===================================
# {1} Django_User <---> {1} UserProfile
# {1} UserProfile <---> {4} Role
# {1} Role <---> {1} 静态数据(nickname、...、prompt、chat_list) + 动态数据(chat_mem_from、...、stream_gen_canceled)

# =====================================================后续工作=====================================================
# 1、完善基于db的user、role基本功能
# 2、完善prompt
# 3、完善付费
# 4、部署celery(定时调用：sync_db_for_all_users()、refresh_user_vip_data_for_all_users()、active_talk_for_all_users())
# 5、关注auto_gpt

# # 获取一个已存在的UserProfile实例
# user_profile = UserProfile.objects.get(id=user_profile_id)
#
# # 创建一个新的Role实例
# new_role = Role(
#     user_profile=user_profile,
#     nickname="新角色",
#     description="这是一个新角色",
#     temperature=0.8,
#     presence_penalty=1.0,
#     frequency_penalty=1.0,
#     can_use=[True, True, True, True, True, True],
#     chat_list_max=[50, 5, 5, 5, 5, 5],
#     chat_persistence=[False, False, False, False, False, False],
#     role_prompt="",
#     active_talk_prompt="",
#     chat_list=[],
#     chat_mem_from=0,
#     chat_full_response_once="",
#     input_with_prompt_and_history=[],
#     stream_gen="",
#     stream_gen_canceled=False,
# )
#
# # 将新的Role实例保存到数据库
# new_role.save()

def gpt_create_db():
    pass

# def gpt_server_init_from_db():
#     printd("=========================Chatgpt server inited from DB===============================")
#     # user_obj = get_db_user_obj("administrator")
#     # user_profile = UserProfile.objects.get(user=user_obj)
#     Chatgpt_Server_Config.db_add_user_profile_and_role("administrator")
#     printd("-------administrator nickname is : {}--------".format(user_profile.nickname))
#     printd("-------administrator user_api_key is : {}--------".format(user_profile.user_api_key))
#     # user_profile = UserProfile(
#     #     user = user_obj,
#     #     nickname="管理员",
#     #     user_level = 0,
#     #     user_api_key=uuid4()
#     # )
#     # user_profile.save()
#     # pass

def gpt_sync_with_db():
    pass

# UserProfile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # 关联到Django内置的User模型

    nickname = models.CharField(max_length=50, default='试用用户')               # User昵称
    gender = models.CharField(max_length=10, default='男')                      # 性别
    user_level = models.IntegerField(default=2)                                 # User等级
    vip_expired = models.BooleanField(default=True)                             # VIP是否过期
    vip_start_time = models.DateTimeField(default=datetime(2020, 1, 1))         # VIP开始时间，改为不能为空(注意：这个时间是没用的，还是需要add_user时调用now_2_str())
    # vip_start_time = models.DateTimeField(blank=True, null=True)              # VIP开始时间
    vip_days = models.IntegerField(default=3)                                   # VIP剩余天数

    current_vip_type = models.CharField(max_length=50, default='evaluate_user') # User当下的VIP类型
    current_role_id = models.CharField(max_length=50, default='default_role')   # User当下的Role ID
    gpt4_invoke_num_left_today = models.IntegerField(default=1)                 # User今天剩下的GPT4调用次数。如5次带记忆，500token一次，总token数估计在7500左右（1+2+3+4+5=15，为5的三倍），成本0.06美元*7.5=3元
    gpt3_invoke_num_left_today = models.IntegerField(default=10)                 # User今天剩下的GPT3调用次数。如20次带记忆，500token一次，总token数估计在10万左右（sigma(1,20)=210，为20的10.5倍），成本0.002美元*100=1.2元

    user_api_key = models.CharField(max_length=50, default='')                  # API_key，用于用户的http调用，powerai.cc/gpt_api(username, api_key, prompt, temperature, presence_penalty, frequency_penalty)，同步、无记忆、一次性返回json数据

    def __str__(self):
        return self.nickname

# Role
class Role(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    role_id = models.CharField(max_length=50, default='default_role')   # Role ID
    nickname = models.CharField(max_length=50, default='默认角色')       # Role角色昵称
    description = models.TextField(blank=True)                          # Role角色描述
    temperature = models.FloatField(default=0.8)                        # [ 0, 2],default:1, GPT的严谨程度(越小越稳定、越大越多变)。platform.openai.com/docs/api-reference/chat/create可能有误，实际取[0,1]。
    presence_penalty = models.FloatField(default=1.0)                   # [-2, 2],default:0, GPT的出现惩罚(越小主题越少)。platform.openai.com/docs/api-reference/chat/create可能有误，实际取[0,2]。
    frequency_penalty = models.FloatField(default=1.0)                  # [-2, 2],default:0, GPT的重复惩罚(越小重复越多)。platform.openai.com/docs/api-reference/chat/create可能有误，实际取[0,2]。
    prompt = models.TextField(blank=True)                               # GPT的常规提示语
    active_talk_prompt = models.TextField(blank=True)                   # GPT主动发言的提示语，如User空闲时，提示GPT："你说一句表明你很想我的话"，然后将GPT回复置入chat_list即聊天历史记录中
    chat_list = models.JSONField(default=list)                          # GPT和user的chat记录，最大长度由s_role_config中对应role的chat_list_max控制

    def __str__(self):
        return self.nickname

class Payment_Record(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    order_id = models.CharField(max_length=50, default='')
    payment_type = models.CharField(max_length=50, default='')
    amount = models.FloatField(default=0.00)
    time = models.DateTimeField(default=datetime(2020, 1, 1))

    def __str__(self):
        return str(self.order_id)

# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)  # 关联到Django内置的User模型
#     password = models.CharField(max_length=100, blank=True)
#     user_nick = models.CharField(max_length=50, default='普通用户')
#     gender = models.CharField(max_length=10, default='男')
#     user_level = models.IntegerField(default=1)
#     vip_expired = models.BooleanField(default=False)
#     vip_start_time = models.DateTimeField(blank=True, null=True)
#     vip_days = models.IntegerField(default=90)
#
#     def __str__(self):
#         return self.user_nick

# class Role(models.Model):
#     user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
#     nickname = models.CharField(max_length=50, default='默认角色')
#     description = models.TextField(blank=True)
#     temperature = models.FloatField(default=0.8)
#     presence_penalty = models.FloatField(default=1.0)
#     frequency_penalty = models.FloatField(default=1.0)
#     can_use = models.JSONField(default=[True, True, True, True, True, True])
#     chat_list_max = models.JSONField(default=[50, 5, 5, 5, 5, 5])
#     chat_persistence = models.JSONField(default=[False, False, False, False, False, False])
#     role_prompt = models.TextField(blank=True)
#     active_talk_prompt = models.TextField(blank=True)
#     chat_list = models.JSONField(default=list)
#     chat_mem_from = models.IntegerField(default=0)
#     chat_full_response_once = models.TextField(blank=True)
#     input_with_prompt_and_history = models.JSONField(default=list)
#     stream_gen = models.TextField(null=True, blank=True)
#     stream_gen_canceled = models.BooleanField(default=False)
#
#     def __str__(self):
#         return self.nickname

# def main1():
#     from app_chatgpt.chatgpt_model import UserProfile, Role  # 请将'app_chatgpt'替换为你的应用名称
#     from django.utils import timezone
#     import datetime
#
#     # 添加用户信息
#     def add_user_profile():
#         user_profile = UserProfile(
#             password='some_password',
#             user_nick='普通用户',
#             gender='男',
#             user_level=1,
#             vip_expired=False,
#             vip_start_time=timezone.now(),
#             vip_days=90,
#         )
#         user_profile.save()
#
#     # 删除用户信息
#     def delete_user_profile(user_profile_id):
#         user_profile = UserProfile.objects.get(pk=user_profile_id)
#         user_profile.delete()
#
#     # 更新用户信息
#     def update_user_profile(user_profile_id):
#         user_profile = UserProfile.objects.get(pk=user_profile_id)
#         user_profile.password = 'new_password'
#         user_profile.user_level = 2
#         user_profile.vip_days = 180
#         user_profile.save()
#
#     # # 示例：添加、删除和更新操作
#     # user_profile_id = None
#     #
#     # # 添加用户信息
#     # print("Adding user profile...")
#     # add_user_profile()
#     # user_profile = UserProfile.objects.last()  # 获取刚添加的用户信息
#     # user_profile_id = user_profile.pk
#     # print(f"User profile with id {user_profile_id} added.")
#     #
#     # # 更新用户信息
#     # print("Updating user profile...")
#     # update_user_profile(user_profile_id)
#     # print(f"User profile with id {user_profile_id} updated.")
#     #
#     # # 删除用户信息
#     # print("Deleting user profile...")
#     # delete_user_profile(user_profile_id)
#     # print(f"User profile with id {user_profile_id} deleted.")
#
#     #==================================================================
#     # 添加角色信息
#     def add_role_to_user_profile(user_profile_id):
#         user_profile = UserProfile.objects.get(pk=user_profile_id)
#         role = Role(
#             user_profile=user_profile,
#             nickname='新角色',
#             description='这是一个新角色的描述。',
#             # 根据你的模型定义，为其他字段添加相应的值
#         )
#         role.save()
#
#     # 删除角色信息
#     def delete_role_from_user_profile(role_id):
#         role = Role.objects.get(pk=role_id)
#         role.delete()
#
#     # 更新角色信息
#     def update_role_in_user_profile(role_id):
#         role = Role.objects.get(pk=role_id)
#         role.nickname = '更新后的角色'
#         role.description = '这是一个更新后的角色描述。'
#         # 根据你的模型定义，更新其他字段的值
#         role.save()
#
#     # # 示例：添加、删除和更新操作
#     # user_profile_id = 1  # 假设这是一个已存在的 UserProfile 的 ID
#     # role_id = None
#     #
#     # # 添加角色信息
#     # print("Adding role to user profile...")
#     # add_role_to_user_profile(user_profile_id)
#     # role = Role.objects.last()  # 获取刚添加的角色信息
#     # role_id = role.pk
#     # print(f"Role with id {role_id} added to user profile with id {user_profile_id}.")
#     #
#     # # 更新角色信息
#     # print("Updating role in user profile...")
#     # update_role_in_user_profile(role_id)
#     # print(f"Role with id {role_id} updated.")
#     #
#     # # 删除角色信息
#     # print("Deleting role from user profile...")
#     # delete_role_from_user_profile(role_id)
#     # print(f"Role with id {role_id} deleted.")


# users_test =    {
#     "default_user" :{
#         "password" :"",
#         "user_nick": "普通用户",
#         "gender": "男",
#         "user_level": 1,                                                # db: 用户等级
#         "vip_expired": False,                                           # db: vip是否过期
#         "vip_start_time" :"",                             # db: vip起始时间(续费可以更新该时间)
#         "vip_days" :90,                                                  # db: vip天数
#
#         "roles" :{
#             "default_role": {  # 默认角色
#                 "nickname": "默认角色",
#                 "description": "",
#                 "chatgpt_para":  # 调用gpt的参数
#                     {"temperature": 0.8, "presence_penalty": 1.0, "frequency_penalty": 1.0},
#                 "can_use":  # 是否: 可用
#                     [True, True, True, True, True, True],
#                 "chat_list_max":  # 是否: 聊天记忆
#                     [50, 5, 5, 5, 5, 5],
#                 "chat_persistence":  # 是否: db持久化
#                     [False, False, False, False, False, False],
#                 "role_prompt":
#                     "",
#                 "active_talk_prompt":
#                     "",
#                 "chat_list": [],  # chat记录，最大长度由chat_list_max控制
#                 "chat_mem_from": 0,
#                 "chat_full_response_once": "",  # role一次完整回复的string，用于形成chat_memory
#                 "input_with_prompt_and_history": [],  # 下一次input（组装了prompt和chat_list）
#                 "stream_gen": None,
#                 "stream_gen_canceled": False,
#             },
#         },
#     }
# }

# def main_test():
#     # print_dict()
#     # print("users: {}".format(users))
#     users2 = json.loads(json.dumps(users_test))
#     users2["default_user"]["roles"]["default_role"]["chat_list"] =["hi"]
#     print("users2 json: {}".format(json.dumps(users2, indent=2, ensure_ascii=False)))
#     print("users2: {}".format(users2))
#     print("users==users2: {}".format(users_test == users2))
#     print("the variable is: ", users2["default_user"]["roles"]["default_role"]["stream_gen"])

def main():
    print("hi")

if __name__ == "__main__" :
    main()