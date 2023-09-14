from django.contrib import admin

# 导出Blog模型
from .models import Persistent_User_Info
from .models import Persistent_Task
from .models import Persistent_Params_of_Investment_Opt
# Register your models here.

# 在后台系统中注册Blog模型
admin.site.register(Persistent_User_Info)
admin.site.register(Persistent_Task)
admin.site.register(Persistent_Params_of_Investment_Opt)