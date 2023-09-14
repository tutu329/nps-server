import socketserver
import socket
import threading
import json, time

# 注意：阿里云ECS上构建socket连接中，server必须用私网地址，client必须用公网地址
g_server_host = '172.18.140.217'    # ECS私网地址
g_client_host = 'powerai.cc'        # ECS公网地址
g_port = {
    'gpu_llm':30888,
}

class Socket():
    _recv_len = 1024

    @classmethod
    def recv(cls, in_request):
        data = in_request.recv(cls._recv_len)


class Socket_Package():
    _end_flag = '\\\\\\\\'  #
    _RECV_LENGTH = 8192
    _DATA_LENGTH_STR_MAX = 0    # '000 000 099' 支持约900MBytes

    @classmethod
    def encode(cls, in_data):
        # '{}' --> '{}\\\\'
        rtn = json.dumps(in_data)+cls._end_flag
        # 生成数据头、并连接：'{}\\\\' --> '000000099{}\\\\'
        data_length = len(rtn)  # '{}\\\\'的长度
        head=''
        # head = '{:0{}d}'.format(data_length, cls._DATA_LENGTH_STR_MAX)  # '0000000999'
        rtn = head + rtn
        return rtn

    @classmethod
    def decoded_object_bak(cls, in_request):
        raw_headed_data = str(in_request.recv(cls._RECV_LENGTH), 'utf-8')
        # '{}\\\\{}\\\\'-->['{}','{}','']
        if raw_headed_data!='':
            # '000000099{}\\\\' --> '000000099'和'{}\\\\'
            # data_len = int(raw_headed_data[0:cls._DATA_LENGTH_STR_MAX])     # 数据头（长度）
            raw_data = raw_headed_data[cls._DATA_LENGTH_STR_MAX:]        # 数据

            print("data: ", raw_data, end='', flush=True)

            # if len(raw_data)!= data_len:
            #     print("=====send_data_len: [{}], recv_data_len: [{}]======".format(data_len, len(raw_data)), end='', flush=True)
            #     print("data: ", raw_data, end='', flush=True)
            #
            # while len(raw_data) < data_len:
            #     raw_data += in_request.recv(cls._RECV_LENGTH)
            #     data_len = int(raw_data[0:cls._DATA_LENGTH_STR_MAX])  # 数据头（长度）
            #     raw_data = raw_data[cls._DATA_LENGTH_STR_MAX:]  # 数据

            list_of_json_string = raw_data.split(cls._end_flag)
            list_of_json_string.pop()   # ['{}','{}']

            for item in list_of_json_string:
                # yield {}
                yield json.loads(item)
        else:
            yield None

    @classmethod
    def decoded_object(cls, in_raw_data):
        # '{}\\\\{}\\\\'-->['{}','{}','']
        if in_raw_data!='':
            list_of_json_string = in_raw_data.split(cls._end_flag)
            list_of_json_string.pop()   # ['{}','{}']

            for item in list_of_json_string:
                # yield {}
                yield json.loads(item)
        else:
            yield None

class test_Handler(socketserver.StreamRequestHandler):
    def handle(self):
        self.data = str(self.request.recv(1024), 'utf-8')
        # self.data = str(self.rfile.readline().strip(), 'utf-8')
        # self.data = str(self.rfile.readline(), 'utf-8')

        #处理llm_proxy的delta_stream
        # llm_proxy.delta_stream += self.data
        print("received: \"{}\"".format(self.data))

        data = {
            'uuid':'',
            'delta_string':'',
        }

# Server: 用于stream实时通信
class LLM_Socket_Server():
    _server = None
    _server_thread = None

    @classmethod
    def init(cls, in_callback_handler_class=None):
        # global g_server_inited
        global g_server_host
        global g_port

        try:
            if not in_callback_handler_class:
                cls._server = socketserver.TCPServer((g_server_host, g_port['gpu_llm']), test_Handler)
            else:
                print("try to start port: {}".format(g_port['gpu_llm']))
                cls._server = socketserver.TCPServer((g_server_host, g_port['gpu_llm']), in_callback_handler_class)
        except:
            print("LLM_Socket_Server.init() warning. {}".format("perhaps try the second port."))
            return

        cls._server_thread = threading.Thread(target=cls._server.serve_forever)

        print("LLM Socker Server listening...")
        cls._server_thread.start()

# Client: 用于stream实时通信
def _client_loop():
    while(True):
        time.sleep(1)

class LLM_Socket_Client():
    _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _client_thread = None

    @classmethod
    def connect(cls):
        global g_client_host
        global g_port
        try:
            cls._sock.connect((g_client_host, g_port['gpu_llm']))
            print("LLM Socker Client connected.")
            # cls._client_thread = threading.Thread(target=_client_loop)
            # cls._client_thread.start()
        except Exception as e:
            print("socket client connect error: ", e)
            cls._sock.close()

    @classmethod
    def send(cls, in_str):
        try:
            rtn = cls._sock.sendall(bytes(in_str, "utf-8"))
            return True
        except Exception as e:  # 注意，这里如果直接用finally: cls._sock.close()，server只能收到''空字符串，很奇怪
            print("socket client send error: ", e)
            cls._sock.close()
            return False


    # socket为双向，client也可以receive
    @classmethod
    def receive(cls):
        try:
            return str(cls._sock.recv(1024), "utf-8")
        except Exception as e:
            print("socket client receive error: ", e)
            cls._sock.close()
            return ''

def main():
    LLM_Socket_Client.connect()
    while(True):
        inp = input("\n【USR】")
        data={
            'uid':'template',
            'content':inp,
        }
        LLM_Socket_Client.send(json.dumps(data))

if __name__ == "__main__":
    main()