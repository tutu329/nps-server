# 看外网ip命令：curl ifconfig.me/all

import os
import openai
openai.api_key="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"
model_list = openai.Model.list().data

# print(model_list)
# for i in range(len(model_list)):
#     print("{}: {}".format(i, model_list[i].id))

while True:
    prompt = input("请输入问题：")
    if prompt=='exit':
        break
    else:
        response = openai.Completion.create(
            model="code-davinci-002",
            # model="text-davinci-003",
            prompt=prompt,
            temperature=0.9,
            max_tokens=1000,
            # top_p=1,
            frequency_penalty=0.0,      #词汇频率
            presence_penalty=0.0,       #主题频率
            # n=3,
            # best_of=4,
            # stream=True,
        )
    # print(response['choices'][0])
    print(response['choices'][0]['text'])

    #编写一个能通过api_key和chatgpt聊天的网页程序
# <!DOCTYPE html>
# <html>
# <head>
#     <title>ChatGPT API Demo</title>
#     <script src="https://cdn.jsdelivr.net/npm/chatgpt@1.0.0/dist/chatgpt.min.js"></script>
#     <script>
#         // 初始化ChatGPT
#         const chatgpt = new ChatGPT('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');
#     </script>
# </head>
# <body>
#     <div id="chatgpt-container"></div>
#     <script>
#         // 将ChatGPT添加到页面
#         chatgpt.addChatGPTToPage('#chatgpt-container');
#     </script>
# </body>
# </html>
def main():
    pass

if __name__ == "__main__" :
    main()