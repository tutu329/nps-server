# 添加对上一级目录import的支持
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Python_User_Logger import *
from redis_monitor import *

import threading
import time, datetime
from queue import Queue
from uuid import uuid1, uuid4

# =====================================================chatGPT请求队列==============================================
# new bing查询结果：chatgpt api concurrency limit，根据我找到的信息，ChatGPT API的并发访问限制取决于用户的账户类型。
# 免费试用用户的并发访问限制为每分钟20个请求，每分钟40000个令牌。按量付费用户（前48小时）的并发访问限制为每分钟60个请求，每分钟60000个令牌。
# 按量付费用户（48小时后）的并发访问限制为每分钟3500个请求，每分钟90000个令牌。但是，我没有找到关于ChatGPT Plus订阅用户对于ChatGPT API并发访问限制的具体信息。

# 通过chatgpt api构建自己的服务系统，由于chatgpt api并发访问有限制，需要建立自己服务的gpt访问队列。
# 请帮我用python实现一个发起chatgpt api请求的队列管理的class，
# 具体要求包括，
# 1]不用管调用gpt的细节，
# 2]管理类的queue是静态变量、线程安全，
# 3]管理类的函数是classmethod，
# 4]队列中每次调用间隔是200ms，
# 5]如果队列为空则管理类每过1秒查询队列是否为空，如果不为空再进行200ms一次的调用，
# 6]user向队列申请调用时，返回给user目前队列还有多少请求尚未执行。

class Concurrent_Requests_Manage():
    _queue = Queue()
    _lock = threading.Lock()
    _tasks = {}              # 用于存放基于event_id的task字典（用于client判断是否成功完成了GPT申请）

    @classmethod
    def _process_queue(cls):
        while True:
            if not cls._queue.empty():
                with cls._lock:
                    callback, args, kwargs, event_data = cls._queue.get()
                event_data["result"]=callback(*args, **kwargs)  # 使用回调函数处理GPT API调用
                event_data["ev"].set()
                printd("===============ev set() with id({})====================".format(event_data["id"]))
                # 在redis中发布queue_length
                Publisher.publish("chatgpt_queue_len_channel", cls._queue.qsize())
                # 我的账户的限制：
                # GPT3.5流量限制为3500次/min(58次/s)，即调用间隔>17.1ms;
                # GPT4流量限制为200次/min(3.3次/s)，即调用间隔>300ms;
                # whisper流量限制为50次/min(0.8次/s)，即调用间隔>1200ms;
                # (https://platform.openai.com/account/rate-limits)
                time.sleep(0.31)


                # time.sleep(0.1)  # 需求：100个用户同一时刻访问，若要10s内发出gpt请求，需要100ms发一个。（限制：GPT流量限制为3500次/min(58次/s)，即调用间隔>17ms）
                # print("next task:")
                # print(datetime.datetime.now())
            else:
                time.sleep(1)  # 如果队列为空，每过1秒查询一次队列
                # 在redis中发布queue_length
                # Publisher.publish("chatgpt_queue_len_channel", cls._queue.qsize())

    @classmethod
    def initialize_queue_thread(cls):
        queue_thread = threading.Thread(target=cls._process_queue)
        queue_thread.daemon = True
        queue_thread.start()

    # # 在这里，我们将回调函数及其参数一起存储
    # request_data = (callback, args, kwargs)
    # # 然后将请求数据添加到队列
    # add_request(request_data)
    @classmethod
    def add_request(cls, callback, *args, **kwargs):
        with cls._lock:
            event_data = {
                "ev": threading.Event(),
                "id": str(uuid4()),    # 这个str()很关键，否则id为uuid类型而非string，dict查询id会报错
                "result":{},
            }
            cls._tasks[event_data["id"]] = event_data   #登记event_id及对应event(是否完成的状态)
            request_data = (callback, args, kwargs, event_data)
            cls._queue.put(request_data)
            queue_length = cls._queue.qsize()
            # 在redis中发布queue_length
            Publisher.publish("chatgpt_queue_len_channel", cls._queue.qsize())
        return queue_length, event_data

    @classmethod
    def request_started(cls, task_id):
        # printd("==================1==================")
        # printd(cls._tasks)
        # printd(task_id)
        ev = cls._get_task(task_id)
        # printd("ev2 is : {}".format(ev))
        # printd("==================2==================")
        # printd(ev["ev"])
        started = ev["ev"].is_set()
        # printd("==================3==================")
        data = {
            'type': 'bool',
            "request_started": started,
            "result":ev["result"],
        }
        return data

    @classmethod
    def get_queue_length(cls):
        with cls._lock:
            queue_length = cls._queue.qsize()
        return queue_length

    @classmethod
    def _get_task(cls, task_id):
        with cls._lock:
            # printd(cls._tasks)
            # print_dict(cls._tasks)
            ev = cls._tasks[task_id]
            # printd("ev1 is : {}".format(ev))
            return ev


Concurrent_Requests_Manage.initialize_queue_thread()

def main():
    def queue_print(user_id, role_id):
        print(datetime.datetime.now())
        time.sleep(2)
        print("task in queue invoked (user: {}, role: {}, len is {})".format(user_id, role_id, Concurrent_Requests_Manage.get_queue_length()))
        print(datetime.datetime.now())

    print(datetime.datetime.now())

    # User_GPT_Request_Queue.initialize_queue_thread()
    len=0
    task = [1,2,3,4]
    len, task[0] = Concurrent_Requests_Manage.add_request(queue_print, "jack2", "default_role")
    len, task[1] = Concurrent_Requests_Manage.add_request(queue_print, "jack3", "default_role")
    len, task[2] = Concurrent_Requests_Manage.add_request(queue_print, "jack4", "default_role")
    len, task[3] = Concurrent_Requests_Manage.add_request(queue_print, "jack5", "default_role")

    # ev = User_GPT_Request_Queue.get_task(task[0]["id"])
    # print("client ev0: id'{}', finished '{}'".format(ev["id"],ev["ev"].wait(2)))

    called1 = Concurrent_Requests_Manage.request_started(task[3]["id"])
    print("task0 finished: {}".format(called1))

    print("start wait task1.")
    ev = Concurrent_Requests_Manage._get_task(task[3]["id"])
    # print(datetime.datetime.now())
    print("client ev1: id'{}', finished '{}'".format(ev["id"],ev["ev"].wait(9.4)))
    # print(datetime.datetime.now())

    called1 = Concurrent_Requests_Manage.request_started(task[3]["id"])
    print("task0 finished: {}".format(called1))



    while(1):
        time.sleep(1)  # 如果队列为空，每过1秒查询一次队列


if __name__ == "__main__" :
    main()
