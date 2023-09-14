from openai import *

from datetime import *
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

import django.utils
# from django.utils import timezone

# from .models import *
# from Params_to_Sys import *

from .redis_monitor import *
from .concurrent_requests_manage import *
# from .email_verify import *

# 添加对上一级目录import的支持
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import Global
Global.init()
# Global.std_file() 

from Python_User_Logger import *

from .Chat_GPT import Chat_GPT, Chatgpt_Server_Config, User_Monitor, User_Email_Verify
from .gpu_llm_proxy import *
from .payment import *
from .commands.search import *

from gpu_server.Stable_Diffusion import *
from agent.agent_factory import *
Agent_Factory.create_agent(in_agent_id='001', in_agent_type='human').init().life_start()

# GPU服务器polling的接口
#remote_gpu_llm = Remote_GPU_LLM_Manager()
# Remote_GPU_LLM_Manager.gpu_server_run_queue_manage()


#【unused】
# gpu_sd_proxy用于调用local gpu的stable diffusion API( http://powerai.cc:30080 )
# g_sd = Stable_Diffusion(in_model="pureRealisticPornPRP_v10.safetensors")
g_sd = Stable_Diffusion(in_model="majicmixAlpha_v10.safetensors")
g_sd.init()
def gpu_sd_proxy(request):
    global g_sd

    result = {"success": False, "content": "gpu_sd_proxy() error."}
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        result = {
            "success": False,
            "type": "NOT_POST",
            "content": "gpu_sd_proxy() should be POST. invoke failed.",
        }
        printd(result)
        return JsonResponse(result)


    prompt = g_sd.build_prompt(
        in_other='',  # presenting panties, panties aside, panty_pull, buruma pull, torn panties, wet panties
        # skirt lift, thigh gap, underboob,
        # bent_over, top-down_bottom-up, m legs, legs apart,
        in_up_cloth='透视连衣裙',
        # in_up_cloth='上衣较少',
        in_bottom_cloth='几乎赤裸的围裙',
        in_underwear='无胸罩',
        in_panties='无内裤',
        in_shoe='高跟鞋',
        in_gesture='走',
        in_shot='第一人称',
        in_light='电影光效',
        in_style1='照片',
        in_style2='现实',
        in_env='海滩',

        in_role='chinese girl',
        in_expression='shy,smile',
        in_hair='drill hair,long hair,shiny hair,hair strand,light brown hair',  # 公主卷、长发、有光泽、一缕一缕、浅褐色
        in_eyes='blue eyes',
        in_lip='red lip',
        in_face='(perfect face, ultra detailed face, best quality face, 8k, real skin)',
        in_legs='(thin legs:1.3),(long legs:1.5),(super model),(slim waist)',
        in_breast='small breasts',
    )
    g_sd.set_prompt(
        in_vertical=True,
        in_steps=30,
        in_batch_size=8,
        in_sampler='DDIM',
        in_l_size=768,
        in_s_size=512,

        in_prompt=prompt,
        in_negative_prompt=g_sd.build_negative_prompt(),
    )
    g_sd.txt2img_and_save(in_file_name='remote_out')   # output1.png、output2.png...
    return JsonResponse(result)

# gpu_llm_proxy用于转发client侧GPU_LLM的服务，consumer和GPU_LLM都需要访问该接口
def gpu_llm_proxy(request):
    # global remote_gpu_llm

    result = {"success": False, "content": "gpu_llm_servant() error."}
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        result = {
            "success": False,
            "type": "NOT_POST",
            "content": "gpu_llm_servant() should be POST. invoke failed.",
        }
        printd(result)
        return JsonResponse(result)

    # uuid(consumer发起的uid，gpu_llm_server根据该uid返回数据)
    uid = data.get('uid')
    user_name = data.get('user_name')
    # 'consumer'、'gpu_llm_server'
    role = data.get('role')
    # 'input'、'polling'
    cmd = data.get('cmd')
    # 为input时则有内容，为polling时无内容
    content = data.get('content')
    # 本轮对话结束的标志
    finish_reason = data.get('finish_reason')

    if role=='consumer':
        if cmd=='input':
            Remote_GPU_LLM_Manager.consumer_start_stream(uid, content, user_name)
            result = {"success": True, "content": "consumer_start_stream success."}
            return JsonResponse(result)
        elif cmd=='polling':
            # pop数据
            delta = Remote_GPU_LLM_Manager.consumer_polling_stream(uid)
            result = {"success": True, "content": delta}
            return JsonResponse(result)
        else:
            pass

    elif role=='gpu_llm_server':
        if cmd=='polling_input':
            rtn = Remote_GPU_LLM_Manager.gpu_llm_polling_input()    # 返回{uuid, input}的list
            result = {"success": True, "content": rtn}
            return JsonResponse(result)
        elif cmd=='response':
            result = {"success": False, "content": "don't invoke legacy_gpu_llm_response()."}
            return JsonResponse(result)
            # ==============================这部分由socket版本替代，见gpu_llm_proxy.GPU_LLM_Handler()==============================================
            # # pop数据
            # print(content, end='')
            # # print("response delta : ", content, end='')
            #
            # Remote_GPU_LLM_Manager.gpu_llm_response(uid, content, in_stop=(finish_reason=='stop'))
            # print("server stream status: ", Remote_GPU_LLM_Manager._user_stream_status[uid]['current_delta_data'], end='')
            # result = {"success": True, "content": "gpu_llm_response success."}
            # return JsonResponse(result)
        else:
            pass
    else:
        pass

    return JsonResponse(result)

# mac终端访问chatgpt(3.5)
def mac_console_ask_server(request):
    result = {"success": False, "content": "mac_console_ask_server() error."}
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        result = {
            "success": False,
            "type": "NOT_POST",
            "content": "mac_console_ask_server() should be POST. invoke failed.",
        }
        printd(result)
        return JsonResponse(result)

    # print("mac_console_ask_server data is: ", data)
    question = data['question']

    try:
        rtn = Chat_GPT().ask_gpt(question, in_max_tokens=500)
    except Exception as e:
        result = {"success": False, "type": "OPENAI_ERROR", "content": "{}".format(e)}
        # result = {"success": False, "type":"OPENAI_ERROR", "content": "openai.ChatCompletion.create() error: {}".format(e)}
        return JsonResponse(result)

    result = {"success": True, "content": rtn}
    # print(result)
    return JsonResponse(result)

# search网络
def web_search(request):
    result = {"success": False, "content": "web_search() error."}
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        result = {
            "success": False,
            "type": "NOT_POST",
            "content": "web_search() should be POST. invoke failed.",
        }
        printd(result)
        return JsonResponse(result)

    search_string = data['search_string']
    results_num = data['results_num']
    time = data['time']     # d w m y，即一天内、一周内、一月内、一年内

    rtn = google_search(search_string, results_num, time)
    result = {"success": True, "content": rtn}
    return JsonResponse(result)

# 更新user信息（nickname, gender）
def db_update_user_info(request):
    result = {"success": False, "content": "db_update_user_info() error."}
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        result = {
            "success": False,
            "type": "NOT_POST",
            "content": "db_update_user_info() should be POST. invoke failed.",
        }
        printd(result)
        return JsonResponse(result)

    user_id = data['user_id']
    user_info = data['user_info']

    try:
        Chatgpt_Server_Config.db_update_user_info(user_id, user_info)
    except Exception as e:
        result = {"success": False, "type": "UPDATE_DB_ERROR", "content": "server: db_update_user_info() error: {}".format(e)}
        print(result, end="")
        return result

    result = {"success": True, "content": "db_update_user_info() succeeded."}
    return JsonResponse(result)

# 后续用于celery中，如每晚12时，app轮训所有user的role的chat_list和nickname，然后db_update_role_data()
def db_update_role_data(request):
    result = {"success": False, "content": "db_update_role_data() error."}
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        result = {
            "success": False,
            "type": "NOT_POST",
            "content": "db_update_role_data() should be POST. invoke failed.",
        }
        printd(result)
        return JsonResponse(result)

    user_id = data['user_id']
    role_id = data['role_id']
    role_data = data['role_data']

    try:
        Chatgpt_Server_Config.db_update_role_data(user_id, role_id, role_data)
    except Exception as e:
        result = {"success": False, "type": "UPDATE_DB_ERROR", "content": "server: db_update_role_data() error: {}".format(e)}
        print(result, end="")
        return result

    result = {"success": True, "content": "db_update_role_data() succeeded."}
    return JsonResponse(result)

def db_update_role_parameters(request):
    result = {"success": False, "content": "db_update_role_parameters() error."}
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        result = {
            "success": False,
            "type": "NOT_POST",
            "content": "db_update_role_parameters() should be POST. invoke failed.",
        }
        printd(result)
        return JsonResponse(result)

    user_id = data['user_id']
    role_id = data['role_id']
    role_parameter = data['role_parameter']

    print("data is : {}".format(data), end="")

    try:
        Chatgpt_Server_Config.db_update_role_parameters(user_id, role_id, role_parameter)
    except Exception as e:
        result = {"success": False, "type": "UPDATE_DB_ERROR", "content": "server: db_update_role_parameters() error: {}".format(e)}
        print(result, end="")
        return result

    result = {"success": True, "content": "db_update_role_parameters() succeeded."}
    return JsonResponse(result)

def db_reset_role_parameters(request):
    result = {"success": False, "content": "db_reset_role_parameter() error."}
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        result = {
            "success": False,
            "type": "NOT_POST",
            "content": "db_reset_role_parameter() should be POST. invoke failed.",
        }
        printd(result)
        return JsonResponse(result)

    user_id = data['user_id']
    role_id = data['role_id']

    try:
        rtn_role_config = Chatgpt_Server_Config.db_reset_role_parameters(user_id, role_id)
    except Exception as e:
        result = {"success": False, "type": "UPDATE_DB_ERROR", "content": "server: db_reset_role_parameter() error: {}".format(e)}
        print(result, end="")
        return result

    result = {"success": True, "content": rtn_role_config}
    return JsonResponse(result)

def user_update_current_role(request):
    result = {"success": False, "content": "user_update_current_role() error."}
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        result = {
            "success": False,
            "type": "NOT_POST",
            "content": "user_update_current_role() should be POST. invoke failed.",
        }
        printd(result)
        return JsonResponse(result)

    user_id = data['user_id']
    role_id = data['role_id']

    try:
        Chatgpt_Server_Config.db_update_current_role(user_id, role_id)
    except Exception as e:
        result = {"success": False, "type": "UPDATE_DB_ERROR", "content": "server: db_update_current_role() error: {}".format(e)}
        print(result, end="")
        return result

    result = {"success": True, "content": "user_update_current_role() succeeded."}
    return JsonResponse(result)

def pay_success_callback(request):
    result = {"success": False, "content": "pay_success_callback() error."}
    # 阿里支付宝的回调：居然不能带自定义参数如user_id和order_id之类！！！带了也会截去，所以回调powerai.cc/pay_success_callback时，data都是None

    Payment.pay_success_callback()
    result = {"success": True, "content": "pay_success_callback() succeeded."}
    return JsonResponse(result)

def pay_query(request):
    result = {"success": False, "content": "pay_query() error."}
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        result = {
            "success": False,
            "type": "NOT_POST",
            "content": "pay_query() should be POST. invoke failed.",
        }
        printd(result)
        return JsonResponse(result)

    user_id = data['user_id']
    order_id = data['order_id']

    rtn = Payment.client_pay_query(user_id, order_id)
    return JsonResponse(rtn)

def pay(request):
    result = {"success": False, "content": "pay() error."}
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        result = {
            "success": False,
            "type": "NOT_POST",
            "content": "pay() should be POST. invoke failed.",
        }
        printd(result)
        return JsonResponse(result)

    print("pay() POST data is: {}".format(data), end="")
    user_id = data['user_id']
    order_id = data['order_id']
    subject = data['subject']
    vip_type = data['vip_type']
    invoke_payment = data['invoke_payment']


    rtn = Payment.pay_precreate(
        in_user_id=user_id,
        in_order_id=order_id,
        in_subject=subject,
        in_vip_type=vip_type,
        in_invoke_payment = invoke_payment,
    )
    print(rtn, end="")
    return JsonResponse(rtn)

def email_verify_page(request):
    token = request.GET.get('token')
    email = request.GET.get('email')
    context = {
        'mycompany': 'PowerAI'  # 使用您的公司名称
    }
    if token and email:
        rtn = User_Email_Verify.verify_email(email, token)
        if rtn["success"]:
            #添加用户
            User_Email_Verify.add_user(email)

            context = {
                'username': email,  # 从验证过程中获取用户名
                'password': rtn["passwd"],
                'mycompany': 'PowerAI'  # 使用您的公司名称
            }
            return render(request, Global.get("path") + 'templates/email_verify_success.html', context)
        else:
            return render(request, Global.get("path") + 'templates/email_verify_failed.html', context)
    else:
        return render(request, Global.get("path") + 'templates/email_verify_failed.html', context)

def _db_user_register_timeout(in_timeout=60):
    # 1)send_verify_email()发送verify邮件（含token）
    # 2)verify(request)异步设置token收到标志
    # 3)异步wait返回的token
    pass

# 对user会话进行基于django session的数据存储、统计
def _set_user_session_data(request, username):
    request.session.set_expiry(600)  # 设置当前会话超时为10分钟（600秒）
    request.session['username'] = username
    request.session['user_online'] = True
    request.session.save()
    print("-------------user {} logined -----------------".format(username), end="")
    print("session['user_online'] registered and saved.", end="")
    print(f"Session ID: {request.session.session_key}", end="")

    # for session in Session.objects.all():
    #     decoded_data = session.get_decoded()
    #     username = decoded_data.get('username')
    #     if username:
    #         print("------------------------------")
    #         print(f"Session ID: {session.seuser_get_chat_listssion_key}")
    #         print(f"Username: {username}")
    #         print(f"Decoded_data data: {decoded_data}")

    # ======统计在线user数量（未超时user数量）======
    user_num = _get_online_users_count()
    # printd("user online number is : {}".format(user_num))
    Publisher.publish("chatgpt_user_online", user_num)

    User_Monitor.publish_user_info(username)
    # printd("User_Monitor.publish_user_info({}) invoked.".format(username))

# user登录：密码验证、新建账户email验证
def db_user_login(request):
    # 1)用户存在、密码正确
    # 2)用户不存在：
    # (1)生成token
    # (2)返回token并让用户自动发送验证email
    # (3)等待用户点击右键的链接访问verify接口，验证verify接口中包含的token
    result = {"success": False, "content": "db_user_login() error."}
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        result = {
            "success": False,
            "type": "NOT_POST",
            "content": "db_user_login() should be POST. invoke failed.",
        }
        printd(result)
        return JsonResponse(result)

    username = data['user_id']
    password = data['password']
    user = authenticate(request, username=username, password=password)
    printd("\"{}\":\"{}\" entered.".format(username, password))

    if user is not None:
        # ======user密码认证通过======
        login(request, user)    # user设置login状态
        result = {"success": True, "content": "User {} successfully logined.".format(username)}

        # ======用于统计在线user数量======
        _set_user_session_data(request, username)

        return JsonResponse(result)
    else:
        # ======django判断用户名或密码错误======
        # result = {
        #     "success": False,
        #     "type": "AUTHENTICATE_FAIL",  # django判断用户名或密码错误
        #     "content": "User {} authenticate failed.".format(username),
        # }

        if User.objects.filter(username=username):
            # ======仅仅是密码错误======
            result = {
                "success": False,
                "type": "PASSWORD_WRONG",  # 密码错误
                "content": "User {} password wrong.".format(username),
            }
        else:
            # ======需要新注册用户======
            rtn = User_Email_Verify.send_verify_email(username, password)     # 向username(email)发送认证邮件
            if rtn["success"] :
                result = {
                    "success": False,
                    "type": "VERIFY_EMAIL_SUCCEESS",  # 发送认证email成功
                    "content": "Verifying User {}'s email success.".format(username),
                }
            else:
                t_type = rtn.get("type")
                if  t_type and t_type=="ALREADY_SENT" :
                    result = {
                        "success": False,
                        "type": "VERIFY_EMAIL_ALREADY_SENT",  # 已发送
                        "content": rtn["content"],
                    }
                else:
                    result = {
                        "success": False,
                        "type": "VERIFY_EMAIL_FAILED",  # 发送认证email失败
                        "content": rtn["content"],
                    }

        return JsonResponse(result)

def db_get_server_user_config(request):
    result = {"success": False, "content": "db_get_server_user_config() error."}
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        result = {
            "success": False,
            "type": "NOT_POST",
            "content": "db_get_server_user_config() should be POST. invoke failed.",
        }
        return JsonResponse(result)

    rtn = Chatgpt_Server_Config.db_get_server_user_config()
    result = {"success": True, "content": rtn}
    return JsonResponse(result)

def db_get_server_role_config(request):
    result = {"success": False, "content": "db_get_server_role_config() error."}
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        result = {
            "success": False,
            "type": "NOT_POST",
            "content": "db_get_server_role_config() should be POST. invoke failed.",
        }
        return JsonResponse(result)

    rtn = Chatgpt_Server_Config.db_get_server_role_config()
    result = {"success": True, "content": rtn}
    return JsonResponse(result)

def db_get_user_data(request):
    result = {"success": False, "content": "db_get_user_data() error."}
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        result = {
            "success": False,
            "type": "NOT_POST",
            "content": "db_get_user_data() should be POST. invoke failed.",
        }
        return JsonResponse(result)

    username = data['user_id']
    rtn = Chatgpt_Server_Config.db_get_user_data(username)
    result = {"success": True, "content": rtn}
    return JsonResponse(result)

def db_get_user_and_roles(request):
    result = {"success": False, "content": "db_get_user_and_roles() error."}
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        result = {
            "success": False,
            "type": "NOT_POST",
            "content": "db_get_user_and_roles() should be POST. invoke failed.",
        }
        return JsonResponse(result)

    username = data['user_id']
    rtn = Chatgpt_Server_Config.db_get_user_and_roles(username)
    result = {"success": True, "content": rtn}
    return JsonResponse(result)

# 获取在线user数量
def _get_online_users_count():
    online_users_count = 0

    # 注意：Session.objects的操作只有在session配置为db时才行！！！（配置为cache时查询不到数据，但django并不报错！）
    active_sessions = Session.objects.filter(expire_date__gte=django.utils.timezone.now())  # 这里是用了django的时区的now()而非datetime.now()，也要注意。

    for session in active_sessions:
        session_data = session.get_decoded()
        if session_data.get('user_online', False):
            online_users_count += 1

    print("==========num of user online is : {}==========".format(online_users_count), end="")

    return online_users_count

def db_user_has_logined(request):
    result = {"success": False, "content": "user_has_logined() error."}
    if request.user.is_authenticated:
        # ======user处于已login状态======
        result = {"success": True, "content": "User {} has logined.".format(request.user.username)}
        # User_Monitor.publish_user_info(request.user.username)

        # ======用于统计在线user数量======
        _set_user_session_data(request, request.user.username)

        return JsonResponse({"success": True, "content":request.user.username})
    else:
        return JsonResponse(result)

# 【legacy】
def user_login(request):
    result = {"success": False, "content": "user_login() error."}
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        result = {"success": False, "content": "user_login() should be POST. invoke failed."}
        printd(result)
        return JsonResponse(result)

    user_id = data["user_id"]
    # printd("User \"{}\" starts login.".format(user_id))

    #==================以后要改为load_role_and_data而不是add_user==============
    Chatgpt_Server_Config.mem_add_user_profile_and_role(user_id)
    result = {"success": True, "content": "User \"{}\" successfully loaded to memory.".format(user_id)}
    # result = Chatgpt_Server_Config.add_user_id(user_id)

    # printd_dict(result)
    printd("User \"{}\" successfully loaded to memory.".format(user_id))
    printd("===user data is===:{}".format(Chatgpt_Server_Config.s_users_data))
    return JsonResponse(result)

# user查询gpt调用是否已启动（通过队列中的全局id(uuid1():物理地址+时间标签）
def user_request_started(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        return JsonResponse({'success': "start_chatgpt_stream() should be POST. invoke failed."})

    printd_dict("user_request_started() post data is : {}".format(data))

    request_id = data.get("request_id")

    if request_id:
        # printd("request_id is :{}".format(request_id))
        rtn = Concurrent_Requests_Manage.request_started(request_id)
        # printd("request with id {} started: {}".format(request_id, started))

        # data = {
        #     'type': 'bool',
        #     "request_started":started,
        # }
    else:
        rtn = {
            'type': 'error',
            "content":"user_request_started() POST has no request id.",
        }

    printd_dict("user_request_started()返回结果: {}".format(rtn))
    return JsonResponse(rtn)

def _stable_diffusion_generator(in_prompt):
    global g_sd

    # 使用template
    if "ttt" in in_prompt:
        prompt = g_sd.build_prompt(
            in_other='',  # presenting panties, panties aside, panty_pull, buruma pull, torn panties, wet panties
            # skirt lift, thigh gap, underboob,
            # bent_over, top-down_bottom-up, m legs, legs apart,
            in_up_cloth='透视连衣裙',
            # in_up_cloth='上衣较少',
            in_bottom_cloth='超短裙',
            in_underwear='无胸罩',
            in_panties='无内裤',
            in_shoe='高跟鞋',
            in_gesture='站立',
            in_shot='特写',
            in_light='电影光效',
            in_style1='照片',
            in_style2='现实',
            in_env='海滩',

            in_role='girl',
            # in_role='chinese girl',
            in_expression='shy,smile',
            in_hair='drill hair,long hair,shiny hair,hair strand,light brown hair',  # 公主卷、长发、有光泽、一缕一缕、浅褐色
            in_eyes='blue eyes',
            in_lip='red lip',
            in_face='(perfect face, ultra detailed face, best quality face, 8k, real skin)',
            in_legs='(thin legs:1.3),(long legs:1.5),(super model),(slim waist)',
            in_breast='small breasts',
        )
        g_sd.set_prompt(
            in_vertical=True,
            in_steps=20,
            in_batch_size=1,
            in_sampler='DDIM',
            in_l_size=768,
            in_s_size=512,
            in_prompt=prompt,
            in_negative_prompt=g_sd.build_negative_prompt(),
        )
        # g_sd.txt2img_and_save(in_file_name='remote_out')   # output1.png、output2.png...
        for img_base64 in g_sd.txt2img_generator():
            yield img_base64

    # 使用输入的prompt
    else:
    # if 'ppp' in in_prompt:
    #     prompt = in_prompt.replace("ppp", "")
        g_sd.set_prompt(
            in_vertical=True,
            in_steps=20,
            in_batch_size=1,
            in_sampler='DDIM',
            in_l_size=768,
            in_s_size=512,

            in_prompt=in_prompt,
            in_negative_prompt=g_sd.build_negative_prompt(),
        )
        # g_sd.txt2img_and_save(in_file_name='remote_out')   # output1.png、output2.png...
        for img_base64 in g_sd.txt2img_generator():
            yield img_base64

# user用role发起对话
def user_start_chatgpt_stream(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        return JsonResponse({'success': "start_chatgpt_stream() should be POST. invoke failed."})

    in_txt = data["data"]
    # printd(in_txt)

    user_id = data["user_id"]
    role_id = data["role_id"]

    if not Chatgpt_Server_Config.db_user_has_invokes_per_day(user_id, role_id) :
        data = {
            'type': 'error',
            'message': "user has not enough invoke times today.",
        }
        return JsonResponse(data)

    # =================================stable diffusion=================================
    if role_id=="painter_role":
        print(f'================start painting ================', end='', flush=True)
        t_png_base64_list = []
        for img_base64 in _stable_diffusion_generator(in_txt):
            t_png_base64_list.append(img_base64)
            # t_pic_string_list = ['picture1', 'picture2']

        data = {
            'type': 'pic_string_list',
            'message': "stable diffusion started.",
            'content': t_png_base64_list,
        }
        print(f'================sd returned data: {data} ================', end='', flush=True)
        return JsonResponse(data)
    # =================================stable diffusion=================================

    gpt = Chat_GPT(in_user=user_id+":"+role_id)


    # 将chat添加到mem（本role是否有mem，由函数内部检查）
    chat_mem = {"role":"user", "content":in_txt}
    Chatgpt_Server_Config.add_chat_list(user_id, role_id, chat_mem)

    # 组装后的 memory_input ~= prompt + chat_list + input
    input = {"role":"user", "content":in_txt}
    Chatgpt_Server_Config.create_input_with_prompt_and_mem(user_id, role_id, input)
    memory_input = Chatgpt_Server_Config.get_input_with_prompt_and_mem(user_id, role_id)["content"]
    # printd_dict("input with prompt and chat_list is : {}".format(memory_input))


    try:
        # printd("==========================entering start_gpt_stream=================================")

        printd("GPT Queue request added.(user:{}, role: {})".format(user_id, role_id))
        len, event_data = Concurrent_Requests_Manage.add_request(gpt.user_start_gpt_stream, in_user_id=user_id, in_role_id=role_id, in_txt=memory_input)
        printd("GPT request id is : {}".format(event_data["id"]))
        # gpt.user_start_gpt_stream(in_user_id=user_id, in_role_id=role_id, in_txt=memory_input)
    except Exception as e:
        if isinstance(e, InvalidRequestError):
            # tokens超限异常，如 >4000 tokens时，将chat_list备份后清空
            # 这里先简单化：清空chat_list
            Chatgpt_Server_Config.clear_chat_mem(user_id, role_id)
            data = {
                'type': 'error',
                'message': "返回数据时tokens数量超限，清空聊天记录",
            }
            return JsonResponse(data)
        else:
            data = {
                'type': 'error',
                'message': repr(e),
            }
            return JsonResponse(data)
    data = {
        'type': 'string',
        'message': "chatGPT stream started.",
        "gpt_queue_len":len,
        "request_id":event_data["id"],
    }

    # printd("returned: {}".format(data))
    return JsonResponse(data)

# user的role获取对话stream
def user_get_chatgpt_stream_chunk(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        return JsonResponse({'success': "get_chatgpt_stream_chunk() should be POST. invoke failed."})

    # printd(data)
    user_id = data["user_id"]
    role_id = data["role_id"]

    gpt = Chat_GPT(in_user=user_id+":"+role_id)

    try:
        # printd("==========================getting gpt_stream_chunk=================================")
        # printd("django server session key is: {}".format(request.session.session_key))
        res = gpt.user_get_gpt_stream_chunk(in_user_id=user_id, in_role_id=role_id)
    except Exception as e:
        if isinstance(e, InvalidRequestError):
            # tokens超限异常，如 >4000 tokens时，将chat_list备份后清空
            # 这里先简单化：清空chat_list
            Chatgpt_Server_Config.clear_chat_mem(user_id, role_id)
            data = {
                'type': 'error',
                'message': "返回数据时tokens数量超限，清空前次聊天记忆",
            }
            return JsonResponse(data)
        else:
            # printd("Exception: {}".format(e))
            data = {
                'type': 'error',
                'message': repr(e),
                # 'message': repr(e)+" with api_key【{}】".format(gpt.s_api_key)
            }  # repr()是获得完整的出错信息
            return JsonResponse(data)

    # printd("user_get_gpt_stream_chunk res is: {}".format(res))

    if not res["success"]:
        data = {
            'type': 'error',
            'message': "something wrong with chunk res returned: {}".format(res["content"]),
        }
        print(data, end="")
        print("the error chunk res returned is : {}".format(res), end="")
        return JsonResponse(data)

    try:
        data = {
            'type': 'string',
            'message': res["content"],
            'finish_reason':res["finish_reason"],
        }
    except Exception as e:
        data = {
            'type': 'error',
            'message': "something wrong with chunk res returned: {}".format(e),
        }
        print(data, end="")
        print("the error chunk res returned is : {}".format(res), end="")
        return JsonResponse(data)


    # 将chunk组成chat_full_response_once，lock和是否chat_mem由函数内部判断
    Chatgpt_Server_Config.add_chunk_for_chat_full_response_once(user_id, role_id, res["content"])

    if res["finish_reason"]=="stop" :
        # 将完整chat response而非chunk添加到mem（本role是否有mem，由函数内部检查）
        full_res = Chatgpt_Server_Config.get_chat_full_response_once(user_id, role_id)["content"]
        chat_mem = {"role":"assistant", "content":full_res}
        Chatgpt_Server_Config.add_chat_list(user_id, role_id, chat_mem)
        # 然后清空chat_full_response_once
        Chatgpt_Server_Config.del_chat_full_response_once(user_id, role_id)

        # printd_dict("chat memory now is : {}".format(Chatgpt_Server_Config.get_chat_memory(user_id, role_id)["content"]))

    # printd("returned: {}".format(data))
    return JsonResponse(data)

# user获取chat_list
def user_get_chat_list(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        return JsonResponse({'success': "user_get_chat_list() should be POST. invoke failed."})

    user_id = data["user_id"]
    role_id = data["role_id"]

    result = Chatgpt_Server_Config.get_chat_list(user_id, role_id)["content"]
    # printd_dict(result)
    return JsonResponse(result, safe=False)

# user删除chat_list(同时删除chat_mem)
def user_clear_chat_list(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        return JsonResponse({'success': "user_get_chat_list() should be POST. invoke failed."})

    user_id = data["user_id"]
    role_id = data["role_id"]

    result = Chatgpt_Server_Config.del_chat_list(user_id, role_id)
    # printd_dict(result)
    return JsonResponse(result)

# user cancel当前正在进行的回复
def user_cancel_current_response(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.get('data')
    else:
        return JsonResponse({'success': "user_cancel_current_response() should be POST. invoke failed."})

    user_id = data["user_id"]
    role_id = data["role_id"]

    result = Chatgpt_Server_Config.user_set_cancel_current_reponse_flag(user_id, role_id)
    # printd_dict(result)
    return JsonResponse(result)

# user升级VIP
def user_set_vip(request):
    pass

# user设置role的role_prompt和active_talk_prompt
def user_set_prompt(request):
    pass

# user清空role的chat_memory
def user_clear_role_memory(request):
    pass

def index_test(request):
    # print(Global.get("path")+'static/index.html')
    # return render(request, "index.html")
    # return render(request, Global.get("path")+'templates/chatgpt.html')
    return render(request, Global.get("path")+'static/vue_chatgpt/dist/index.html')

# legacy
def get_role_template_list(request):
    result = {"success": False, "content": "get_role_template_list() error."}
    # printd("***************************************************")
    # printd("***************************************************")
    # printd("***************************************************")
    list = Chatgpt_Server_Config.get_role_template_list()
    # printd("---------------------------------------------------")
    # printd("***************************************************")
    # printd("***************************************************")
    # printd_dict(list)
    result = {"success": True, "content": list}
    return JsonResponse(result)

# legacy
def start_chatgpt_stream(request):
    # 第一次访问，session_key==None，必须先save()一下
    if not request.session.session_key:
        request.session.save()

    if request.method == 'POST':
        if request.content_type == 'application/json':
            printd("json invoke")
            data = json.loads(request.body)
            # do something with data
        else:
            printd("not json invoke")
            data = request.POST.get('data')
            # do something with data
        printd("invoke success")
    else:
        printd("start_chatgpt_stream() should be POST. invoke failed.")
        return JsonResponse({'success': "start_chatgpt_stream() should be POST. invoke failed."})

    in_txt = data["data"]
    printd(in_txt)

    gpt = Chat_GPT(in_user=request.session.session_key)

    try:
        printd("====================================================================================")
        printd("==========================entering start_gpt_stream=================================")
        printd("django server session key is: {}".format(request.session.session_key))
        gpt.start_gpt_stream(in_txt, in_session_key=request.session.session_key)
    except Exception as e:
        if isinstance(e, InvalidRequestError):
            # tokens超限异常，如 >4000 tokens时，将chat_list备份后清空
            # 这里先简单化：清空chat_list
            # Chatgpt_Server_Config.clear_chat_mem()
            data = {
                'type': 'error',
                'message': "申请数据时tokens数量超限，清空聊天记录",
            }
            return JsonResponse(data)
        else:
            printd("Exception: {}".format(e))
            data = {
                'type': 'error',
                'message': repr(e),
                # 'message': repr(e)+" with api_key【{}】".format(gpt.s_api_key)
            }  # repr()是获得完整的出错信息
            return JsonResponse(data)

    data = {
        'type': 'string',
        'message': "chatGPT stream started.",
    }
    printd("returned: {}".format(data))
    return JsonResponse(data)

# legacy
def get_chatgpt_stream_chunk(request):
    # 第一次访问，session_key==None，必须先save()一下
    if not request.session.session_key:
        request.session.save()

    if request.method == 'POST':
        if request.content_type == 'application/json':
            printd("json invoke")
            data = json.loads(request.body)
            # do something with data
        else:
            printd("not json invoke")
            data = request.POST.get('data')
            # do something with data
        printd("invoke success")
    else:
        printd("get_chatgpt_stream_chunk() should be POST. invoke failed.")
        return JsonResponse({'success': "get_chatgpt_stream_chunk() should be POST. invoke failed."})

    printd(data)

    gpt = Chat_GPT(in_user=request.session.session_key)

    try:
        printd("==========================getting gpt_stream_chunk=================================")
        printd("django server session key is: {}".format(request.session.session_key))
        res = gpt.get_gpt_stream_chunk(request.session.session_key)
    except Exception as e:
        printd("Exception: {}".format(e))
        data = {
            'type': 'error',
            'message': repr(e),
            # 'message': repr(e)+" with api_key【{}】".format(gpt.s_api_key)
        }  # repr()是获得完整的出错信息
        return JsonResponse(data)
    data = {
        'type': 'string',
        'message': res["content"],
        'finish_reason':res["finish_reason"],
    }
    printd("returned: {}".format(data))
    return JsonResponse(data)

# legacy
def chatgpt_sync(request):
    # 第一次访问，session_key==None，必须先save()一下
    if not request.session.session_key:
        request.session.save()

    if request.method == 'POST':
        if request.content_type == 'application/json':
            printd("json invoke")
            data = json.loads(request.body)
            # do something with data
        else:
            printd("not json invoke")
            data = request.POST.get('data')
            # do something with data
        printd("invoke success")
    else:
        printd("chatgpt_sync() should be POST. invoke failed.")
        return JsonResponse({'success': "chatgpt_sync() should be POST. invoke failed."})

    printd(data)
    in_txt = data["data"]
    printd(in_txt)
    gpt = Chat_GPT(in_user=request.session.session_key)     # 采用django的"session_key"，作为chatgpt-3.5-turbo的"user_id"
    printd("session_key is: {}".format(request.session.session_key))
    printd("question: {}".format(in_txt))
    if "draw" in in_txt:
        try:
            answer = gpt.draw_images(in_txt)
        except Exception as e:
            printd("Exception: {}".format(e))
            data = {
                'type':'error',
                'message': repr(e),
                # 'message': repr(e)+" with api_key【{}】".format(gpt.s_api_key)
            }     #repr()是获得完整的出错信息
            return JsonResponse(data)
        data={
            'type':'image_url_list',
            'image_num':gpt.image_num,
            'message':answer,
        }
        printd("returned: {}".format(data))
        return JsonResponse(data)
    else:
        try:
            answer = gpt.ask_gpt(in_txt)
        except Exception as e:
            printd("Exception: {}".format(e))
            data = {
                'type':'error',
                'message':repr(e),
                # 'message': repr(e)+" with api_key【{}】".format(gpt.s_api_key)
            }     #repr()是获得完整的出错信息
            return JsonResponse(data)
        data={
            'type':'string',
            'message':answer,
        }
        printd("returned: {}".format(data))
        return JsonResponse(data)

def main():
    print("hi chatgpt_view.")

if __name__ == "__main__" :
    main()


