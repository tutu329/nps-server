import os
from datetime import timedelta
from celery import Celery
from celery.schedules import crontab

# 为 'celer' 程序设置默认的Django设置模块。

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nps.settings')

# app = Celery('nps')


# app = Celery('nps', broker='redis://127.0.0.1:6379/1', backend='redis://127.0.0.1:6379/0')
# 无密码时，密码前的:也不需要
app = Celery('nps', broker='redis://:Jackseaver112279@127.0.0.1:6379/1', backend='redis://:Jackseaver112279@127.0.0.1:6379/0')
# app = Celery('take_out', broker='redis://127.0.0.1:6379/4', backend='redis://127.0.0.1:6379/5')

# 使用字符串使程序可以不加载任何其他配置模块。
app.config_from_object('django.conf:settings', namespace='CELERY')

# 加载所有注册过的任务应用。
app.autodiscover_tasks()

app.conf.update(
    CELERYBEAT_SCHEDULE={
        # 'say_hello': {
        #     'task': 'app_chatgpt.tasks.say_hello',
        #     'schedule': crontab(minute=0, hour=0),   # 每天0点0分执行
            # 'schedule': timedelta(minutes=1),
            # 'args': (),
        # },
        'check_all_users_vip_expired': {
            'task': 'app_chatgpt.tasks.check_all_users_vip_expired',
            # 'schedule': timedelta(minutes=1),
            'schedule': crontab(minute=0, hour=0),   # 每天0点0分执行
            'args': (),
        },
        # 'send_message': {
        #     'task': 'wechat_app.tasks.send_batch_msg',
        #     'schedule': crontab(minute=5, hour=11),    # 每天中午11点05分执行一次群发消息
        #     'args': (),
        # }
    }
)

# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')