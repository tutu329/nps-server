import redis
import time

from django.shortcuts import render
from django.http import JsonResponse

# 添加对上一级目录import的支持
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import Global
Global.init()

from Python_User_Logger import *

# 从redis获取订阅数据("channel"对应的数据)
def pull_monitor_data(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')

    # channel_list = data
    result = {}

    msg = Subscriber.get_raw_message()
    rtn_data = 999
    channel = "999"

    # redis获取到数据的判断
    if msg and msg["type"] == "pmessage":
    # if msg and msg["type"] == "message":
        rtn_data = msg["data"].decode('utf-8')
        channel = msg["channel"].decode('utf-8')
        # printd("redis data of channel {} is : {}".format(channel, rtn_data))
        # ========================添加第i个已更新数据========================
        result = {"success":True, "data":rtn_data, "channel":channel}
        # printd("true data channel is : {}".format(channel))
    else:
        # ========================添加第i个未更新数据========================
        result = {"success":False, "data":rtn_data, "channel":channel}

    return JsonResponse(result)

def monitor(request):
    return render(request, Global.get("path")+'templates/monitor.html')

# redis发布信息
class Publisher():
    _server = redis.StrictRedis(host='powerai.cc', port=6379, db=0, password="Jackseaver112279")

    @classmethod
    def publish(cls, in_channel, in_content):
        cls._server.publish(in_channel, in_content)

# redis订阅信息
class Subscriber():
    _server = redis.StrictRedis(host='powerai.cc', port=6379, db=0, password="Jackseaver112279")
    _pubsub = _server.pubsub()
    # _channel_list = [
    #     "chatgpt_queue_len_channel",
    #     "chatgpt_user_online",
    #     "chatgpt_user_info",
    #     "chatgpt_world_*",
    # ]

    @classmethod
    def init_channels(cls):
        cls._pubsub.psubscribe("chatgpt_*")
        # cls._pubsub.subscribe(cls._channel_list)

    @classmethod
    def add_channels(cls, in_channel_list):
        cls._pubsub.subscribe(in_channel_list)
        cls._channel_list += in_channel_list

    @classmethod
    def get_channels(cls):
        return cls._channel_list

    # legacy
    @classmethod
    def get_message(cls, in_channel):
        cls._pubsub.subscribe(in_channel)
        msg = cls._pubsub.get_message()
        return msg

    # 正常使用应该是: 拿回数据，然后判断是什么channel
    @classmethod
    def get_raw_message(cls):
        msg = cls._pubsub.get_message()
        return msg

    # legacy
    @classmethod
    def wait_msg(cls, in_channel, in_seconds=1.0):
        while True:
            msg = cls.get_message(in_channel)
            if msg and msg["type"]=="message":
                return msg["data"]
            time.sleep(in_seconds)

# 订阅多个channel
Subscriber.init_channels()


def main():
    print("ok")
    Publisher.publish("chatgpt_queue_len_channel", "hello world.")

if __name__ == "__main__":
    main()