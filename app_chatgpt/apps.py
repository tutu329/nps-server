# apps.py用于放置app启动完毕后的初始化代码，且django是直接调用apps.py，任何其他py都不行

from django.apps import AppConfig
# from django.contrib.auth.models import User


class Chatgpt_Appconfig(AppConfig):
    name = "app_chatgpt"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # print("Initializing Chatgpt_Appconfig...", end="")
        # print("self.name =", self.name, end="")
        # print("self.label =", self.label, end="")
        # print("self.module.__name__ =", self.module.__name__)

    def ready(self):
        try:
            print("=============Django App \"{}\" are ready, but db is not ready.============".format(Chatgpt_Appconfig.name), end="")

            # 这里主要用于设置signals
            # import app_chatgpt.signals

        except Exception as e:
            print("Error in Chatgpt_Appconfig.ready():", e)
