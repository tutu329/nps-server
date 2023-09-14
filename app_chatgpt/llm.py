import openai

class LLM():
    s_api_key = "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"   # openai账号：采用微软账号(jack.seaver@outlook.com)，plus 20美元/月、token费用另算。
    # s_api_key = "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"  # openai账号：jack.seaver@163.com:Jackseaver112279
    # s_api_key = "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"
    # s_api_key = "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"
    # s_api_key = "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"
    # s_api_key = "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"
    # s_api_key = "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"

    # 一个session对应一个stream_generator
    s_session_stream_generator_pool = {
        "session_key+role_name":"{some_stream_generator}",
    }

    # 一个session对应一个history_chat_list
    s_session_history_chat_list_pool = {
        "session_key+role_name":"{some_history_chat_list}",
    }

    def __init__(self,
                 in_model="gpt-3.5-turbo-0301",
                 # in_model="gpt-4-0314",
                 in_temperature=0.8,
                 in_presence_penalty=1.0,
                 in_frequency_penalty=1.0,
                 in_user="itsmylife",
                 in_image_num=2,
                 in_image_size="512x512"):
        self.model = in_model
        self.temperature = in_temperature
        self.presence_penalty = in_presence_penalty
        self.frequency_penalty = in_frequency_penalty
        self.user = in_user
        self.image_num = in_image_num
        self.image_size = in_image_size

    def get_model_list(self, in_has_name=""):
        openai.api_key = LLM.s_api_key
        model_list = []
        data = openai.Model.list().data
        for i in range(len(data)):
            if in_has_name in data[i].root :
                model_list.append(data[i].root)
        return model_list

    # =====================================常用openai.ChatCompletion.create【同步】调用=====================================
    def ask_gpt(self, in_txt, in_max_tokens=50):
        openai.api_key = LLM.s_api_key
        message = [{"role": "user", "content": in_txt}]
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=message,
            temperature=self.temperature,
            presence_penalty=self.presence_penalty,
            frequency_penalty=self.frequency_penalty,
            max_tokens=in_max_tokens,
            user=self.user,
        )
        single_answer = response['choices'][0]['message']['content']
        return single_answer

    # =====================================常用openai.ChatCompletion.create【异步】调用=====================================
    # ===================启动stream调用===================
    # def user_start_gpt_stream(self, in_user_id, in_role_id, in_txt):
    #     result = {"success":False, "type":"SOME_ERROR_TYPE", "content":"user_start_gpt_stream error."}
    #     db_django_user = User.objects.get(username=in_user_id)
    #     db_user = UserProfile.objects.get(user=db_django_user)
    #     db_role = Role.objects.get(user_profile=db_user, role_id=in_role_id)
    #     user_level = db_user.user_level
    #     role_can_use = Chatgpt_Server_Config.s_role_config[in_role_id]["can_use"][user_level]
    #     # role_chat_list_max = Chatgpt_Server_Config.s_role_config[in_role_id]["chat_list_max"][db_user.user_level]
    #
    #     printd("============user_start_gpt_stream() with prompt: {} ==============".format(db_role.prompt))
    #     print("====================================1=================================", end="")
    #     #==============================user的认证===============================
    #     user = Chatgpt_Server_Config.s_users_data.get(in_user_id)
    #     if not user:
    #         result = {"success": False, "type":"USER_NOT_FOUND", "content": "User \"{}\" not found.".format(in_user_id)}
    #         # printd(result)
    #         print("====================================2=================================", end="")
    #         return result
    #     # user_nickname = user["user_nick"]
    #     # user_gender = user["gender"]
    #     # user_level = user["user_level"]
    #     # user_vip_expired = user["vip_expired"]
    #     # printd_dict({
    #     #     "user_id":in_user_id,
    #     #     "user_nickname":user_nickname,
    #     #     "user_gender":user_gender,
    #     #     "user_level":user_level,
    #     #     "user_vip_expired":user_vip_expired,
    #     # })
    #
    #     #==============================role的认证===============================
    #     role = user["roles"].get(in_role_id)
    #     if not role:
    #         # 该user的role_id错误
    #         result = {"success": False, "type":"ROLE_NOT_FOUND", "content": "Role \"{}\" not found.".format(in_role_id)}
    #         # printd(result)
    #         print("====================================3=================================", end="")
    #         return result
    #     if not role_can_use :
    #         # 该user的role没有使用权限（防止client使用错误的欺骗权限）
    #         result = {"success": False, "type":"ROLE_NO_AUTHENTICATION", "content": "{}".format(in_role_id)}
    #         # printd(result)
    #         print("====================================4=================================", end="")
    #         return result
    #
    #
    #     role["stream_gen_canceled"] = False
    #
    #
    #     # ============================role的gpt参数=============================
    #     role_nickname = db_role.nickname
    #     # chat_list_max = role_chat_list_max
    #
    #     role_prompt = db_role.prompt
    #     active_talk_prompt = db_role.active_talk_prompt
    #
    #     temperature = db_role.temperature
    #     presence_penalty = db_role.presence_penalty
    #     frequency_penalty = db_role.frequency_penalty
    #
    #     # printd_dict({
    #     #     "role_id":in_role_id,
    #     #     "role_nickname":role_nickname,
    #     #     "chat_list_max":chat_list_max,
    #     #     "chat_persistence":chat_persistence,
    #     #     "role_prompt":role_prompt,
    #     #     "active_talk_prompt":active_talk_prompt,
    #     #     "temperature":temperature,
    #     #     "presence_penalty":presence_penalty,
    #     #     "frequency_penalty":frequency_penalty,
    #     # })
    #
    #     # ===============================调用gpt================================
    #     openai.api_key = Chat_GPT.s_api_key
    #
    #     printd("============user_start_gpt_stream() with in_txt: {} ==============".format(in_txt))
    #
    #     if type(in_txt)==list:
    #         # in_txt为list时，表明输入的是memory_input
    #         message = in_txt
    #     else:
    #         message = [{"role": "user", "content": in_txt}]
    #
    #     try:
    #         the_model = self.model
    #         if Chatgpt_Server_Config.can_use_gpt4(in_user_id, in_role_id):
    #             the_model = "gpt-4-0314"
    #             print("------------ Using \"GPT-4-0314\" 8k model! ------------", end="")
    #
    #         response_generator = openai.ChatCompletion.create(
    #             model=the_model,
    #             messages=message,
    #             temperature=temperature,
    #             presence_penalty=presence_penalty,
    #             frequency_penalty=frequency_penalty,
    #             user=self.user, # 这个是给gpt用的user_id + role_id
    #             stream=True,
    #         )
    #     except Exception as e:
    #         if isinstance(e, InvalidRequestError):
    #             # tokens超限异常，如 >4000 tokens时，将chat_list备份后清空
    #             # 这里先简单化：清空chat_list
    #             Chatgpt_Server_Config.clear_chat_mem(in_user_id, in_role_id)
    #             printd("Max context length > 4097 tokens: {}".format(e))
    #             printd("Invoke clear_chat_mem() and openai.ChatCompletion.create() again.")
    #             # 重组message
    #             if len(message)<=2:
    #                 # 说明mem的token数很大仅仅是因为input超级长
    #                 result = {"success": False, "type":"REGROUP", "content": "regroup"}
    #                 printd("openai.ChatCompletion.create() error: input large than 4096 tokens")
    #                 print("====================================5=================================", end="")
    #                 return result
    #             else:
    #                 # 重组message, 把list删除中间，只剩下message[0]即prompt和message[len]即input_text
    #                 msg_len = len(message)
    #                 msg_prompt = message[0]
    #                 msg_input = message[msg_len-1]
    #                 new_msg = []
    #                 new_msg.append(msg_prompt)
    #                 new_msg.append(msg_input)
    #                 printd_dict("Regrouped mem list is: {}".format(new_msg))
    #             # 再一次申请GPT调用
    #             response_generator = openai.ChatCompletion.create(
    #                 model=self.model,
    #                 messages=new_msg,
    #                 temperature=temperature,
    #                 presence_penalty=presence_penalty,
    #                 frequency_penalty=frequency_penalty,
    #                 user=self.user, # 这个是给gpt用的user_id + role_id
    #                 stream=True,
    #             )
    #             gen_id = in_user_id + ":" + in_role_id
    #             gen = Chat_GPT.s_session_stream_generator_pool.get(gen_id)
    #             Chat_GPT.s_session_stream_generator_pool[gen_id] = response_generator  # 不管是否存在，都要新建一个gen
    #             result = {"success": True, "type":"REGROUP", "content": "regroup"}
    #             printd_dict(result)
    #             print("====================================6=================================", end="")
    #             return result
    #         else:
    #             result = {"success": False, "type":"OPENAI_ERROR", "content": "{}".format(e)}
    #             # result = {"success": False, "type":"OPENAI_ERROR", "content": "openai.ChatCompletion.create() error: {}".format(e)}
    #             printd("openai.ChatCompletion.create() error: {}".format(e))
    #             print("====================================7=================================", end="")
    #             return result
    #
    #     # response_generator = openai.ChatCompletion.create(
    #     #     model=self.model,
    #     #     messages=message,
    #     #     temperature=self.temperature,
    #     #     presence_penalty=self.presence_penalty,
    #     #     frequency_penalty=self.frequency_penalty,
    #     #     user=self.user,
    #     #     stream=True,
    #     # )
    #     #---------------------------如果1个user在不同浏览器需要不同的聊天：{1}session   <--> {n}gpt---------------------------
    #     #---------------------------如果1个user在不同浏览器需要相同的聊天：{1}user+role <--> {n}gpt---------------------------
    #     print("====================================8=================================", end="")
    #     gen_id = in_user_id+":"+in_role_id
    #     gen = Chat_GPT.s_session_stream_generator_pool.get(gen_id)
    #     Chat_GPT.s_session_stream_generator_pool[gen_id] = response_generator   # 不管是否存在，都要新建一个gen
    #     print("user_start_gpt_stream() success. s_session_stream_generator_pool is : {}".format(Chat_GPT.s_session_stream_generator_pool), end="")
    #     result = {"success": True, "content": "gpt stream of \"{}:{}\" started.".format(in_user_id, in_role_id)}
    #
    #     Chatgpt_Server_Config.db_user_max_invokes_per_day_decline(in_user_id, in_role_id)
    #     #---------------------------------------------------------------------------------------------------------------
    #     return result

    # def start_gpt_stream(self, in_txt, in_session_key):
    #     openai.api_key = Chat_GPT.s_api_key
    #     message = [{"role": "user", "content": in_txt}]
    #     response_generator = openai.ChatCompletion.create(
    #         model=self.model,
    #         messages=message,
    #         temperature=self.temperature,
    #         presence_penalty=self.presence_penalty,
    #         frequency_penalty=self.frequency_penalty,
    #         user=self.user,
    #         stream=True,
    #     )
    #     Chat_GPT.s_session_stream_generator_pool[in_session_key] = response_generator  # 存储基于当前会话的python generator
    #     return

    # ===================获取stream的chunk===================
    # def user_get_gpt_stream_chunk(self, in_user_id, in_role_id):
    #     # printd("user_get_gpt_stream_chunk entered with {}:{}.".format(in_user_id,in_role_id))
    #     response = {"success":False, "content":"user_get_gpt_stream_chunk error."}
    #     gen_id = in_user_id+":"+in_role_id
    #
    #     if not Chat_GPT.s_session_stream_generator_pool.get(gen_id) :
    #         response = {"success": False, "content": "Role ID \"{}\" of \"{}\" not found.".format(in_role_id, in_user_id)}
    #         printd(response)
    #         print("s_session_stream_generator_pool is : {}".format(Chat_GPT.s_session_stream_generator_pool), end="")
    #         return response
    #
    #     # printd("==============0=============")
    #     gen = Chat_GPT.s_session_stream_generator_pool[gen_id]
    #     # print("==============1=============")
    #     response = {
    #         "success": True,
    #         "content":"",
    #         "finish_reason":None,
    #     }
    #     # print("==============1.5=============")
    #     finished = False
    #
    #     role = Chatgpt_Server_Config.s_users_data[in_user_id]["roles"][in_role_id]
    #     # print("==============1.6=============")
    #     # printd(role)
    #     if role["stream_gen_canceled"]==False :
    #         # printd("start get chunk of gen.")
    #         # for res in gen:       #不能用for res in gen，因为server会一次性从服务器把数据全部取完
    #         chunk_num_one_time = 5
    #         for i in range(chunk_num_one_time):
    #             res=next(gen)
    #             # res = gen.next()
    #
    #             # generator所含函数： 'close', 'gi_code', 'gi_frame', 'gi_running', 'gi_suspended', 'gi_yieldfrom', 'send', 'throw'
    #             # print(gen)
    #             # print(type(gen))
    #             # print(dir(gen))
    #
    #             # 如果stream中含有"finish_reason":"stop"这样的数据块，说明stream已经结束
    #             finish_reason = res['choices'][0].get('finish_reason')
    #             if finish_reason=="stop" or finish_reason=="length":    # finish_reason=="length"时，是指回复长度值达到了设置的max_tokens值
    #                 finished = True
    #                 response["finish_reason"]="stop"
    #                 break
    #
    #             # print(res['choices'][0])
    #             content = res['choices'][0]['delta'].get('content')
    #             # print("content: {}".format(content))
    #             # print("==============2=============")
    #             if content:
    #                 response["content"] += content
    #                 # print("response: {}".format(response["content"]))
    #                 finish_reason = res['choices'][0].get('finish_reason')
    #                 # print("==============3=============")
    #                 if finish_reason :
    #                     response["finish_reason"] = finish_reason
    #     else:
    #         # 用户主动cancel的回复
    #         printd("gen canceled with \"{}\":\"{}\"".format(in_user_id, in_role_id))
    #         gen.close()
    #
    #
    #         # 这里不能设置False，而改为在user_start_gpt_stream()中设置False
    #         # role["stream_gen_canceled"] = False
    #
    #
    #         finished = True
    #         response["finish_reason"] = "stop"
    #
    #     # print("【response】: {}".format(response))
    #     # print("==============99=============")
    #     return response

    # def get_gpt_stream_chunk(self, in_session_key):
    #     if not Chat_GPT.s_session_stream_generator_pool.get(in_session_key) :
    #         return {"content":"", "finish_reason":"session_key not found.",}
    #
    #     # printd("==============0=============")
    #     gen = Chat_GPT.s_session_stream_generator_pool[in_session_key]
    #     # print("==============1=============")
    #     response = {
    #         "content":"",
    #         "finish_reason":None,
    #     }
    #     finished = False
    #
    #     # for res in gen:       #不能用for res in gen，因为会一次性从服务器把数据全部取完
    #     chunk_num_one_time = 5
    #     for i in range(chunk_num_one_time):
    #         res=next(gen)
    #         # res = gen.next()
    #
    #         # generator所含函数： 'close', 'gi_code', 'gi_frame', 'gi_running', 'gi_suspended', 'gi_yieldfrom', 'send', 'throw'
    #         # print(gen)
    #         # print(type(gen))
    #         # print(dir(gen))
    #
    #         # 如果stream中含有"finish_reason":"stop"这样的数据块，说明stream已经结束
    #         finish_reason = res['choices'][0].get('finish_reason')
    #         if finish_reason=="stop":
    #             finished = True
    #             response["finish_reason"]="stop"
    #             break;
    #
    #         # print(res['choices'][0])
    #         content = res['choices'][0]['delta'].get('content')
    #         # print("content: {}".format(content))
    #         # print("==============2=============")
    #         if content:
    #             response["content"] += content
    #             # print("response: {}".format(response["content"]))
    #             finish_reason = res['choices'][0].get('finish_reason')
    #             # print("==============3=============")
    #             if finish_reason :
    #                 response["finish_reason"] = finish_reason
    #
    #     # print("【response】: {}".format(response))
    #     # print("==============99=============")
    #     return response

    # =====================================chatGPT stream的res['choices'][0]的数据结构=====================================
    # {
    #     "delta": {
    #         "role": "assistant"
    #     },
    #     "finish_reason": null,
    #     "index": 0
    # }
    # {
    #     "delta": {
    #         "content": "\n\n"
    #     },
    #     "finish_reason": null,
    #     "index": 0
    # }
    # {
    #     "delta": {
    #         "content": "Hello"
    #     },
    #     "finish_reason": stop,
    #     "index": 0
    # }



    # =====================================老openai接口【同步】调用=====================================
    # code-davinci-002 分支
    def ask_gpt_code(self, in_txt):
        openai.api_key = LLM.s_api_key
        response = openai.Completion.create(
            model="text-davinci-003",
            # model="code-davinci-002",
            prompt=in_txt,
            temperature=0.1,
            presence_penalty=0.1,
            frequency_penalty=0.1,
        )
        single_answer = response['choices'][0]['text']
        return single_answer

    def draw_images(self, in_txt):
        openai.api_key = LLM.s_api_key
        response = openai.Image.create(
            prompt=in_txt,
            n=self.image_num,
            size=self.image_size
        )
        images_url_list = []
        for i in range(self.image_num):
            images_url_list.append(response['data'][i]['url'])
        return images_url_list
