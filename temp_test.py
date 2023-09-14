class LLM_Socket_Server():
    _server_inited = 0
    _server = None
    _server_thread = None

    @classmethod
    def init(cls, in_callback_handler_class=None):
        global g_server_host
        global g_port

        print("cls._server_inited = {}".format(cls._server_inited))
        if cls._server_inited>0:
            return

        cls._server_inited += 1
        print("s:{}".format( cls._server_inited))
        return

LLM_Socket_Server.init()
LLM_Socket_Server.init()
LLM_Socket_Server.init()
LLM_Socket_Server.init()
