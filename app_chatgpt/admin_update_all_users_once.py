from django.contrib.auth.models import User
from .models import *

# ======================！！！注意：这个更新函数只能运行一次，运行完就注释掉，再运行时，必须确保不损坏已有数据！！！======================
def add_field_for_all_users():
    # 获取所有User对象
    users = User.objects.all()

    # 更新每个User对象的age属性
    for user_obj in users:
        user_profile_obj = UserProfile.objects.get(user=user_obj)

        user_profile_obj.current_vip_type = 'free_user'  # 根据需要设置年龄值
        user_profile_obj.current_role_id = 'default_role'  # 根据需要设置年龄值
        user_profile_obj.save()
    # ======================！！！注意：这个更新函数只能运行一次，运行完就注释掉，再运行时，必须确保不损坏已有数据！！！======================

def main():
    pass
    # 本文件无法直接调用，必须在app_chatgpt的middlewares.py中调用(db启动后调用一次，然后注释掉)

if __name__ == "__main__" :
    main()
