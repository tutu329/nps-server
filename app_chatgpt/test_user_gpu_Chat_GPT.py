import requests, json
import time, uuid

def input_to_llm(in_uid, in_input, in_user_name):
    send_data = {
        "uid":in_uid,
        "user_name": in_user_name,
        "role":"consumer",
        "cmd":"input",
        "content":in_input,
    }
    headers = {'content-type':'application/json'}
    url = 'https://powerai.cc/gpu_llm_proxy'
    result = requests.post(url, data=json.dumps(send_data), headers=headers)
    json_result = json.loads(result.text)
    return json_result

def polling_llm(in_uid):
    send_data = {
        "uid":in_uid,
        "role":"consumer",
        "cmd":"polling",
    }
    headers = {'content-type':'application/json'}
    url = 'https://powerai.cc/gpu_llm_proxy'
    result = requests.post(url, data=json.dumps(send_data), headers=headers)
    json_result = json.loads(result.text)
    return json_result

def main():
    uid = str(uuid.uuid4())
    while(True):
        try:
            # time.sleep(0.01)
            query = input("\n【USR】")
            rtn = input_to_llm(uid, query, 'tutu')
            print("llm_input result: ", rtn)
            print("【LLM】", end='')
            while(True):
                result = polling_llm(uid)
                # print("llm_polling result: ", result)
                delta_data = result["content"]
                print(delta_data['delta']['content'], end='', flush=True)
                if result['success'] and delta_data['finish_reason']=="stop":
                    print("(本轮对话结束)")
                    break
        except requests.exceptions.ConnectionError as e:
            print("服务器无法连接。。。")
            continue
        except Exception as e:
            print("服务器错误：", e)
            continue

if __name__ == "__main__":
    main()