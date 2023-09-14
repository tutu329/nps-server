from uuid import uuid4
import threading
from time import sleep
import json

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import Config
from llm import LLM

from concurrent_requests_manage import *
from redis_monitor import *

import random

class Not_Dict_Exception(Exception):
    def __init__(self, message):
        self.message = message

class Dice:
    def __init__(self, sides):
        self.sides = sides

    def roll(self, dice_number=1):
        return sum(random.randint(1, self.sides) for _ in range(dice_number))

class Base_Thread():
    def __init__(self):
        # 用于pause、stop线程的参数组
        self._flag = threading.Event()
        self._flag.set()
        self._running = threading.Event()
        self._running.set()

        # 用于控制on_event阻塞操作的参数
        self._processing = False

    def response_from_action(self):
        pass

    def observe(self):
        pass

    def think(self):
        pass

    def action(self):
        pass

    def summary(self):
        pass

    def _loop(self):
        while self._running.is_set():
            self._flag.wait()

            if self._processing==False:
                self._processing = True

                # 阻塞操作，同一个对象，同一时间只能做一件事情
                self.response_from_action()
                self.observe()
                self.think()
                self.action()
                self.summary()
                sleep(0.1)
                self._processing = False
            else:
                sleep(0.1)

    def start(self):
        self._thread = threading.Thread(target=self._loop)
        self._thread.daemon = True
        self._thread.start()

    def pause(self):
        self._flag.clear()

    def resume(self):
        self._flag.set()

    def stop(self):
        self._flag.set()
        self._running.clear()

class World_Choices():
    # 这些选择是给GPT看的示例，GPT完全可能生成这些选择以外的词汇

    action_types = [
        "talk",
        "flirt",
        "touch",
        "kiss",
        "hug",
        "hit",
        "miss",
        "whisper",
    ]
    action_types_string = json.dumps(action_types)
    action_observable = {
        "talk": {
            "visible_to_all":False,     # 所有人看见
            "visible_to_me":False,      # 仅对象看见
            "audible_to_all":True,      # 所有人听见
            "audible_to_me":True,       # 仅对象听见
        },
        "flirt": {
            "visible_to_all":False,
            "visible_to_me":True,
            "audible_to_all":False,
            "audible_to_me":True,
        },
        "touch": {
            "visible_to_all":True,
            "visible_to_me":True,
            "audible_to_all":False,
            "audible_to_me":False,
        },
        "kiss": {
            "visible_to_all":True,
            "visible_to_me":True,
            "audible_to_all":False,
            "audible_to_me":True,
        },
        "hug": {
            "visible_to_all":True,
            "visible_to_me":True,
            "audible_to_all":False,
            "audible_to_me":False,
        },
        "hit": {
            "visible_to_all":True,
            "visible_to_me":True,
            "audible_to_all":False,
            "audible_to_me":False,
        },
        "miss": {
            "visible_to_all":False,
            "visible_to_me":False,
            "audible_to_all":False,
            "audible_to_me":False,
        },
        "whisper": {
            "visible_to_all":False,
            "visible_to_me":False,
            "audible_to_all":False,
            "audible_to_me":True,
        },
    }

class Action():
    '''
    {
        "type":"flirt",
        "subject":"茵茵",
        "object":"笨笨",
        "content":"牵了一下笨笨的手",
    }
    '''
    def __init__(self, in_action_type='', in_name='', in_obj='', in_content=''):
        self.action_dict = {
            "action":in_action_type,
            "name":in_name,
            "to":in_obj,
            "content":in_content,
        }

    def __str__(self):
        dict_str = json.dumps(self.action_dict, ensure_ascii=False)
        return dict_str

    def get_dict(self):
        return self.action_dict

    @classmethod
    def load_from_string(self, in_dict_str):
        action = Action()
        action.action_dict = json.loads(in_dict_str)

        if type(action.action_dict)!=dict:
            raise Not_Dict_Exception(f'GPT返回的不是dict数据')
        return action

class Person(Base_Thread):
    def __init__(self, in_world_ref):
        super().__init__()
        self.id = uuid4()
        self.name = ''
        self.gender = '男'
        self.age = 20

        self.observed_actions = []  # 观测得到的情况
        self.gpt_response = ''

        # self._flag = threading.Event()
        # self._flag.set()
        # self._running = threading.Event()
        # self._running.set()

        self._world = in_world_ref
        in_world_ref._add_person(self.id, self)

        self._thread = None

        # 用于人物prompt构建的参数
        self._goal_prompt = ''
        self._destinatin_prompt = ''
        self._prompt_tail = f'以下是大家的聊天内容：'
        self._rule_prompt = ''

    # 必须在__init__初始化之后调用，确保子类已经初始化
    def init(self, in_name, in_age, in_goal):
        self.name = in_name
        self.age = in_age
        self._goal_prompt = f'你的重要目标是{in_goal}。'
        self._rule_prompt = f'你是一个正在参与聊天的{self.age}岁{self.gender}性，名字是{self.name}，' \
                            f'所有输入给你的信息都是json数据，你回复的信息必须是json格式数据:{{"action":"...","name":"{self.name}","to":"...","content":"..."}}, 注意只能发一条数据, ' \
                            f'其中"action"的值必须是{World_Choices.action_types_string}中的一个，"to"的值必须是"action"实施对象的名字或者"all"，"content"的值必须是"action"的描述内容。' \
                            + self._goal_prompt \
                            + self._prompt_tail

    def _print_prompt(self):
        print(f"{self.name}的提示是: '{self._rule_prompt}'")

    def response_from_action(self):
        pass

    def observe(self):
        # 看见和听见
        self.observed_actions = []
        for action in self._world.all_action_list:
            _observable = World_Choices.action_observable[action["action"]]
            if _observable["visible_to_all"] or _observable["audible_to_all"] or (_observable["visible_to_me"] and (action["to"]==self.name)) or (_observable["audible_to_me"] and (action["to"]==self.name)) :
                # 如果对自己可见或可听，则添加observe记录
                self.observed_actions.append(action)
                # print(f"{self.name} 记录了action {action}")

        # 调试输出观察结果
        # self._print_observed_actions()

    def _print_observed_actions(self):
        print(f"{self.name}的观察结果：")
        for action in self.observed_actions:
            print(action)

    def think(self):
        if type(self)!=Philosopher:
            sleep(random.randint(5, 10))
        # print(f"【{self.name}】: thinking...")

    def action(self):
        try:
            print(f"{self.name}思考中：")
            res = self._wait_ask_gpt(self._rule_prompt + json.dumps(self.observed_actions, ensure_ascii=False))
            action = Action.load_from_string(res)
        except json.JSONDecodeError as e:
            print(f"【{self._world.name}】: {self.name}回答格式有误({res}).")
            sleep(random.randint(5, 10))
            return
        except Exception as e:
            print(f"【{self._world.name}】: {self.name}网络不好: {e}")
            sleep(random.randint(5, 10))
            return

        def func(in_action):
            return
        self._world.start_action(func, action)

    def summary(self):
        pass

    # GPT的调用，统一让World调度
    def _wait_ask_gpt(self, in_input, in_timeout=30):
        queue_length, event_data = self._world.start_gpt(in_input, self)
        event = event_data["ev"]

        if event.wait(in_timeout):
            # print('GPT回复:', self.gpt_response)
            return self.gpt_response
        else:
            raise TimeoutError(f'World({self._world.name})访问GPT超时.')

    def __str__(self):
        return f"Person '{self.name}' is in world '{self._world.name}'"

class Philosopher(Person):
    def __init__(self, in_world_ref, in_name, in_question, in_ai=False):
        super().__init__(in_world_ref)
        self.name = in_name
        self.question = in_question
        self.ai = in_ai

    def action(self):
        # print(f"【{self.name}】: acting...")
        question = self.question
        # question = "你是金庸小说中的任我行，你现在向田伯光提一个与《笑傲江湖》中田伯光调戏尼姑仪琳师妹有关的问题，要简洁、嚣张，毕竟你是坏人，直接问，不要提其他信息"
        # question = "1)问一个生活上的问题，2)表达一下心情很好，3)问一个很有灵性的、很有趣的问题；在这三个选项中，随机选一项回答，直接回答，不要提及选项几或选项有关的信息，也不要解释"


        if self.ai:
            print("Philosopher ai starts to say.")
            try:
                res = self._wait_ask_gpt(question)
            except Exception as e:
                print(f"【{self._world.name}】: {self.name}出错: {e}")
                sleep(120)
                return

            action = Action("talk", self.name, "all", res)
        else:
            print("Philosopher non-ai starts to say.")
            action = Action("talk", self.name, "all", self.question)

        def func(in_action):
            return
        print("Philosopher action start to register.")
        self._world.start_action(func, action)
        print("Philosopher action registered.")

        # =============================测试=============================
        _a = Action("whisper", self.name, "田伯光", "我们等下调戏周芷若去.")
        self._world.start_action(func, _a)
        # =============================测试=============================

        sleep(120)

class Female(Person):
    def __init__(self, in_world_ref):
        super().__init__(in_world_ref)
        self.gender = '女'

    # def think(self):
    #     # print(f"【{self.name}】: thinking...")
    #     sleep(random.randint(5, 10))
    #
    # def action(self):
    #     # print(f"【{self.name}】: acting...")
    #     try:
    #         res = self._wait_ask_gpt(self._rule_prompt + json.dumps(self.observed_actions, ensure_ascii=False))
    #         action = Action.load_from_string(res)
    #     except Exception as e:
    #         print(f"【{self._world.name}】: {self.name}回答格式有误或网络不好.")
    #         sleep(random.randint(5, 10))
    #         return
    #
    #     def func(in_action):
    #         return
    #     self._world.start_action(func, action)

class Male(Person):
    def __init__(self, in_world_ref):
        super().__init__(in_world_ref)
        self.gender = '男'

    # def think(self):
    #     # print(f"【{self.name}】: thinking...")
    #     sleep(random.randint(5, 10))
    #
    # def action(self):
    #     # print(f"【{self.name}】: acting...")
    #     try:
    #         res = self._wait_ask_gpt(self._rule_prompt + json.dumps(self.observed_actions, ensure_ascii=False))
    #         action = Action.load_from_string(res)
    #     except Exception as e:
    #         print(f"【{self._world.name}】: {self.name}回答格式有误或网络不好.")
    #         sleep(random.randint(5, 10))
    #         return
    #
    #     def func(in_action):
    #         return
    #     self._world.start_action(func, action)

class Person_Group():
    def __init__(self):
        self._person_group = {}

    def _add_person(self, in_id, in_person):
        self._person_group[in_id] = in_person

    def start_all_persons(self):
        for key, value in self._person_group.items():
            value.start()

    def pause_all_persons(self):
        for key, value in self._person_group.items():
            value.pause()

    def resume_all_persons(self):
        for key, value in self._person_group.items():
            value.resume()

    def stop_all_persons(self):
        for key, value in self._person_group.items():
            value.stop()

    def __str__(self):
        rtn = ''
        for key, value in self._person_group.items():
            rtn += value.name + '\n'
        return rtn

class World(Base_Thread):
    def __init__(self, in_name, in_max_tokens=200):
        super().__init__()
        self.id = uuid4()
        self.name = in_name
        self.max_tokens = in_max_tokens

        self._persons = Person_Group()

        # world元素
        self._thread = None
        self._world_oscillator = None

        # 外部元素
        self._world_outsiders = None

        self._gpt = LLM()

        # 历史记录
        # 记录类型：all
        self.all_action_list = []

    # Concurrent_Requests_Manage队列：增加请求（可以是GPT访问，也可以是Action等需要限制时间间隔的或异步的动作）
    def start_action(self, in_callback, in_action):
        # 这里做异步处理，是因为有些action会产生后果，需要异步处理
        Concurrent_Requests_Manage.add_request(in_callback, in_action)

        name = in_action.get_dict()['name']
        action = in_action.get_dict()['action']
        to = in_action.get_dict()['to']
        content = in_action.get_dict()['content']
        print(f"【{name}】[{action}] to 【{to}】：{content}")
        print("\n")

        Publisher.publish("chatgpt_world_"+name, json.dumps(in_action.get_dict(), ensure_ascii=False))

        # print(f"【{self.name}】: {in_action}")

        # 记录action
        self.all_action_list.append(in_action.get_dict())

    def start_gpt(self, in_input, in_person_obj):
        def _ask_gpt(in_str):
            try:
                rtn = in_person_obj.gpt_response = self._gpt.ask_gpt(in_str, in_max_tokens=self.max_tokens)
                return rtn
            except Exception as e:
                print(f"【{self.name}】: 网络不好.")
                return ''

        # print(f"_ask_gpt() returned with: {rtn}")
        queue_length, event_data = Concurrent_Requests_Manage.add_request(_ask_gpt, in_input)
        # print(f"start_gpt(): {in_input}")
        return queue_length, event_data

    def action(self):
        pass
        # print("world event happens.")

    def start(self):
        super().start()
        self._persons.start_all_persons()

    def pause(self):
        super().pause()
        self._persons.pause_all_persons()

    def resume(self):
        super().resume()
        self._persons.resume_all_persons()

    def stop(self):
        super().stop()
        self._persons.stop_all_persons()

    def _add_person(self, in_id, in_person):
        self._persons._add_person(in_id, in_person)

    def __str__(self):
        return f"world '{self.name}' has persons :\n{self._persons}"

def main():
    print("world启动.")
    Concurrent_Requests_Manage.initialize_queue_thread()
    print("Concurrent_Requests_Manage queue thread started.")

    arg = sys.argv

    w = World("金庸世界", in_max_tokens=300)
    if len(arg)>=2:
        p1 = Philosopher(w, "任我行", arg[1])
    else:
        # p1 = Philosopher(w, "任我行", "你是金庸小说中的任我行，你提一个与《笑傲江湖》中岳不群的问题，要简洁、嚣张，毕竟你是坏人，直接问，不要提其他信息", in_ai=True)
        p1 = Philosopher(w, "任我行", "听说大家昨天过情人节，各种野战、做爱")

    # p1 = Philosopher("任我行", w, "你是金庸小说中的任我行，你现在向田伯光提一个与《笑傲江湖》中田伯光调戏尼姑仪琳师妹有关的问题，要简洁、嚣张，毕竟你是坏人，直接问，不要提其他信息")
    p2 = Female(w)
    p2.init("周芷若", 20, '用描绘性爱细节的刺激语言挑逗张无忌或回应他的挑逗，告诉他你想象引诱他做爱的细节')
    # p2._print_prompt()

    p3 = Male(w)
    p3.init("小昭", 30, '用描绘性爱细节的刺激语言挑逗令狐冲或回应他的挑逗，用语言描述你怎么和他缠绵')

    p4 = Male(w)
    p4.init("令狐冲", 50, '用描绘性爱细节的刺激语言挑逗小昭或其他女人，用语言描述你和她们做爱的细节，如抚摸、插入后的细节')

    p5 = Male(w)
    p5.init("张无忌", 55, '用描绘性爱细节的刺激语言挑逗其他女人或回应挑逗，聊怎么抚摸女人')

    p6 = Female(w)
    p6.init("赵敏", 20, '用描绘性爱细节的刺激语言挑逗张无忌或回应他的挑逗，聊性交细节如怎么刺激阴茎或阴蒂')

    w.start()
    print("World object thread started.")

    # self.prompt = f'你是一个正在参与聊天的男生，名字叫{in_name}，所有输入给你的信息都是json数据，你回复的信息必须是json格式数据:{{"type":"...","name":"{self.name}","to":"...","content":"..."}}，其中type可以是"talk"或者其他，object可以是"all"或者其他人的名字，content是你talk或其他动作的内容。以下是大家的聊天内容，你的重要目标是以金庸小说人物田伯光略带邪气、但又深刻而洒脱的风格发表你的观点：'

    x = 0
    while True:
        # if x>5:
        #     w.pause()
        # if x>10:
        #     w.resume()
        if x>120:
            w.stop()
            print(f"【{w.name}】：表演结束。")
            break
        # if x>20:
        #     w.resume()
        # print(x)
        sleep(1)
        x += 1

if __name__ == "__main__" :
    main()



