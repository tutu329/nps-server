import time
from threading import Thread
import copy, json
from .llm_socket import *

# socket版本: 替代legacy_gpu_llm_response()
# 用于接收GPU_LLM的实时response数据的socket server handler
# 将接收到的delta_string连接至: Remote_GPU_LLM_Manager._user_stream_status[uid]['current_delta_data']['delta']['content']
class GPU_LLM_Handler(socketserver.StreamRequestHandler):

    # socket中，一旦handle()返回，则server和client的connect就关闭了
    def handle(self):
        while(True):
            # request = self.request
            # if request:
            #     # ======Socket_Package.decoded_object 将 '{}\\\\{}\\\\' --> {}的generator======
            #     objs = Socket_Package.decoded_object(request)
            #
            #     if not objs:
            #         continue
            #
            #     for item in objs:

            self.data = str(self.request.recv(8192), 'utf-8')
            if self.data!='':
                print("=====================received data====================", self.data, end='')

                # ======Socket_Package.decoded_object 将 '{}\\\\{}\\\\' --> {}的generator======
                try:
                    objs = Socket_Package.decoded_object(self.data)
                except Exception as e:
                    print("============GPU_LLM_Handler exception============: ", e, end='', flush=True)
                    print("============self.data at the exception============: ", self.data)
                    continue

                if not objs:
                    continue

                for item in objs:

                # # =============================================================================
                # # 1、GPU侧：self.data 被调制为"{}, {},"这样的数据
                # # 2、server侧：json.loads转换为["{}","{}",""]
                # self.data = self.data.split('\\\\\\\\')
                # for item in self.data:
                #     # 3、server侧：将["{}","{}",""]转换为{}和{}且""被过滤掉
                #     if item!='':
                #         print("item : ", item)
                #         item = json.loads(item)
                #     else:
                #         break

                    # 处理llm_proxy的delta_stream
                    # self.data = {
                    #     'uid': '',
                    #     'cmd': 'response',
                    #     'content': '',
                    #     'finish_reason': '' or 'stop',
                    # }

                    uid = item.get('uid') if item.get('uid') else ''
                    cmd = item.get('cmd') if item.get('cmd') else ''
                    delta_string = item.get('content') if item.get('content') else ''
                    finish_reason = item.get('finish_reason') if item.get('finish_reason') else ''

                    # 更新数据
                    # 注意这里必须直接用Remote_GPU_LLM_Manager._user_stream_status['template']['current_delta_data']['delta']['content']，用delta_stream的话需要增加赋值操作(和js中的字典update有点像)
                    delta_stream = Remote_GPU_LLM_Manager._user_stream_status[uid]['current_delta_data']['delta']['content']
                    Remote_GPU_LLM_Manager._user_stream_status[uid]['current_delta_data']['delta']['content'] += delta_string
                    # delta_stream += delta_string
                    # Remote_GPU_LLM_Manager._user_stream_status[uid]['current_delta_data']['delta']['content'] = delta_stream

                    # 设置标志
                    if finish_reason=='stop':
                        # 本轮对话结束
                        Remote_GPU_LLM_Manager._user_stream_status[uid]['current_delta_data']['finish_reason'] = 'stop'
                        Remote_GPU_LLM_Manager._user_stream_status[uid]['query_status'] = 'query_finished'
                    else:
                        Remote_GPU_LLM_Manager._user_stream_status[uid]['current_delta_data']['finish_reason'] = ''
                        # Remote_GPU_LLM_Manager._user_stream_status[uid]['query_status'] = 'querying'

                    # print("test status: ", Remote_GPU_LLM_Manager._user_stream_status[uid]['current_delta_data'], end='')

LLM_Socket_Server.init(in_callback_handler_class=GPU_LLM_Handler)


# 远程GPU管理( {1}uuid<-->{1}一个多轮对话 )
class Remote_GPU_LLM_Manager():
    _queue_manage_thread = None

    # 多轮对话的所有状态
    # 数据
    _delta_data_template = {
        'uuid':'',
        'delta':{
            'role':'assistant',
            'content':'',           # 该值其实为delta_stream，gpu数据会将delta_string连接到其末尾，consumer获取该数据后将其清空
        },
        'finish_reason':'',
    }

    # 控制状态
    _user_stream_status = {
        # 一轮对话的状态
        'template':{
            'uuid':'',
            'user_name':'',
            # 'user_input':'',
            # 'llm_generator':None,

            # 一一对应的input_queue、delta_data_queue
            # 'input_queue':[],           # 多轮对话的m个fifo, queue成员为input字符串
            # 'delta_data_queue':[],      # 多轮对话的m个fifo, queue成员为delta_data数据

            # 当前正在进行的对话的状态
            'current_input':'',         # 一轮对话1个
            'current_delta_data':copy.deepcopy(_delta_data_template),    # 一轮对话n个，但用1个动态更新变量表示，current_delta_data是动态被consumer的polling pop数据和被gpu_llm的polling push数据的缓存

            'query_status':'waiting_for_query',     # waiting_for_query、querying、query_finished
            'current_query_finished':True,

            # 'current_stream_manage_thread':None,

            # 对话的cancel状态('normal', 'canceling', 'canceled')
            'cancel_status':'normal',
        }
    }


    # # GPT server端的queue_manage_loop(处理input和response的队列)
    # @classmethod
    # def _gpu_server_queue_manage_loop(cls):
    #     while(True):
    #         for uid in cls._user_stream_status:
    #             # current_query没有finish时执行:
    #             if uid!='template' and cls._user_stream_status[uid]['current_query_finished']==True :
    #                 input_queue = cls._user_stream_status[uid]['input_queue']
    #                 cls._user_stream_status[uid]['current_input'] = input_queue.pop(0)
    #                 delta_data_queue = cls._user_stream_status[uid]['delta_data_queue']
    #                 cls._user_stream_status[uid]['current_delta_data']  = delta_data_queue.pop(0)
    #
    #                 # 表明current_query正在异步执行，尚未finish
    #                 cls._user_stream_status[uid]['current_query_finished'] == False
    #         time.sleep(0.1)

    # # 开线程run queue_manage({1}server<-->{1}queue_manage)
    # @classmethod
    # def gpu_server_run_queue_manage(cls):
    #     if not cls._queue_manage_thread:
    #         cls._queue_manage_thread = Thread(target=cls._gpu_server_queue_manage_loop)
    #         cls._queue_manage_thread.start()

    # # GPT server端的current_stream_manage_loop(处理当前stream的接收)
    # @classmethod
    # def _consumer_current_stream_manage_loop(cls, in_uid):
    #     uid = in_uid
    #     if cls._user_stream_status[uid]['current_query_finished'] == False:
    #         delta_data = cls._user_stream_status[uid]['delta_data']
    #         while(delta_data['finish_reason']!='stop'):
    #             # 数据异步接收中
    #             # append
    #             time.sleep(0.05)
    #         cls._user_stream_status[uid]['current_query_finished'] == True

    # # 开线程run current_stream_manage({1}server<-->{n}stream_manage)
    # @classmethod
    # def _consumer_run_current_stream_manage_thread(cls, in_uid):
    #     uid = in_uid
    #     if not cls._user_stream_status[uid]['current_query_finished']:
    #         cls._user_stream_status[uid]['current_query_finished'] = Thread(target=cls._consumer_current_stream_manage_loop, args=(uid,))
    #         cls._user_stream_status[uid]['current_query_finished'].start()

    # GPU_LLM端polling所有uuid对应的input，注意：返回的input，必须是waiting_for_query==True状态；如果简单的获取current_query_finished==False，网络不好时，会重复获取。
    @classmethod
    def gpu_llm_polling_input(cls):
        rtn = []
        for key in cls._user_stream_status:
            # print("uid[{}] found.".format(key), end='')
            # print("data is : ", cls._user_stream_status[key], end='')
            if key!='template' and cls._user_stream_status[key]['query_status']=='waiting_for_query':
                print("uuid[{}] username[{}] input[{}] appended.".format(cls._user_stream_status[key]['uuid'], cls._user_stream_status[key]['user_name'], cls._user_stream_status[key]['current_input']), end='')
                rtn.append({
                    'uuid':cls._user_stream_status[key]['uuid'],
                    'user_name': cls._user_stream_status[key]['user_name'],
                    'input':cls._user_stream_status[key]['current_input'],
                })
                cls._user_stream_status[key]['query_status'] = 'querying'
        return rtn

    # 【legacy】
    # GPU_LLM端的response uuid对应的返回数据delta
    @classmethod
    def legacy_gpu_llm_response(cls, in_uid, in_delta_string, in_stop=False):
        # 将GPU_LLM送来的delta_string加到delta_stream中
        delta_stream = cls._user_stream_status[in_uid]['current_delta_data']['delta']['content']
        delta_stream += in_delta_string
        cls._user_stream_status[in_uid]['current_delta_data']['delta']['content'] = delta_stream
        if in_stop:
            # 本轮对话结束
            cls._user_stream_status[in_uid]['current_delta_data']['finish_reason'] = 'stop'
            cls._user_stream_status[in_uid]['query_status'] = 'query_finished'
        else:
            cls._user_stream_status[in_uid]['current_delta_data']['finish_reason'] = ''
            # cls._user_stream_status[in_uid]['query_status'] = 'querying'

    # GPT server端的input调用
    @classmethod
    def consumer_start_stream(cls, in_uid, in_input, in_user_name):
        uid = in_uid

        # 初始化 cls._user_stream_status[uid]
        cls._user_stream_status[uid] = copy.deepcopy(cls._user_stream_status['template'])

        cls._user_stream_status[uid]['uuid'] = uid
        cls._user_stream_status[uid]['query_status'] = 'waiting_for_query'
        cls._user_stream_status[uid]['current_input'] = in_input
        cls._user_stream_status[uid]['user_name'] = in_user_name

        # 初始化 cls._user_stream_status[uid] 的 current_delta_data
        cls._user_stream_status[uid]['current_delta_data'] = copy.deepcopy(cls._delta_data_template)

        cls._user_stream_status[uid]['current_delta_data']['uuid'] = uid
        # cls._user_stream_status[uid]['current_delta_data']['delta']['role'] = 'assistant'
        # cls._user_stream_status[uid]['current_delta_data']['delta']['content'] = ''
        # cls._user_stream_status[uid]['current_delta_data']['finish_reason'] = ''

        print("==============> init data[{}] is {}: ".format(uid, cls._user_stream_status[uid]), end='')

    # GPT server端的polling
    @classmethod
    def consumer_polling_stream(cls, in_uid):
        delta = ''
        gpu_answer_finished=False
        if cls._user_stream_status.get(in_uid):
            # print("conumer get delta_stream: ", Remote_GPU_LLM_Manager._user_stream_status[in_uid]['current_delta_data'], end='')
            if cls._user_stream_status[in_uid]['current_delta_data']['finish_reason']=='stop':
                gpu_answer_finished=True

            delta = copy.deepcopy(cls._user_stream_status[in_uid]['current_delta_data'])        # consumer: 获取delta_stream
            cls._user_stream_status[in_uid]['current_delta_data']['delta']['content'] = ''      # consumer: 清空delta_stream、
            if gpu_answer_finished:
                cls._user_stream_status[in_uid]['current_delta_data']['finish_reason'] = ''     # consumer: 若finish==true则清空delta状态(这个设置非常重要！)

            # print("conumer clear delta_stream: ", Remote_GPU_LLM_Manager._user_stream_status[in_uid]['current_delta_data'], end='')

        return delta

def main():
    llm = Remote_GPU_LLM_Manager()

if __name__ == "__main__":
    main()
