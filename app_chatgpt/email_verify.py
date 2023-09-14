# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.header import Header
# import urllib.parse
#
# from uuid import uuid4
#
# import sys
# import os
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# from Python_User_Logger import *
#
# from .Chat_GPT import *
#
# class User_Email_Verify():
#     # user通过email验证的dict
#     s_user_verify_token = {}
#     '''
#     {
#         "email":{
#             "email": in_user_email,
#             "password": in_password,
#             "token": token,
#         }
#     }
#     '''
#
#     # 添加user
#     @classmethod
#     def add_user(cls, in_username):
#         user = cls.s_user_verify_token.get(in_username)
#         password=""
#         if user:
#             password = user["password"]
#             rtn = Chatgpt_Server_Config.db_add_user(in_username, password)
#             if rtn["success"]:
#                 # ========================这里删除email verify的标志，防止user被admin手动删除后，新建user发生已发送email而无法注册的错误（主要用于server admin测试）========================
#                 del cls.s_user_verify_token[in_username]
#                 # ========================这里删除email verify的标志，防止user被admin手动删除后，新建user发生已发送email而无法注册的错误（主要用于server admin测试）========================
#                 print("user {} added.".format(in_username), end="")
#             else:
#                 print("User_Email_Verify.add_user(\"{}\")  failed: {}".format(in_username, rtn["content"]), end="")
#
#         else:
#             print("User_Email_Verify.add_user(): try to add user {} but user not found in dict.".format(in_username), end="")
#
#     # 客户端打开email认证链接后，后台获得链接中的token，将其与发送email时生成的token进行对比验证
#     @classmethod
#     def verify_email(cls, in_email, in_token):
#         user = cls.s_user_verify_token.get(in_email)
#         if user:
#             if user["token"]==in_token:
#                 passwd = user["password"]
#                 return {"success":True, "passwd":passwd}
#             else:
#                 return {"success":False}
#         else:
#             return {"success":False}
#     # def verify_email(cls, in_email, in_token):
#     #     rtn = cls.s_user_verify_token.get(in_email)
#     #     if rtn:
#     #         if rtn["token"]==in_token:
#     #             return True
#     #         else:
#     #             return False
#     #     else:
#     #         return False
#
#     @classmethod
#     def send_verify_email(cls, in_user_email, in_password):
#         result = {"success": False, "content": "email_verify() failed."}
#
#         # 已经发送验证email
#         rtn = cls.s_user_verify_token.get(in_user_email)
#         if rtn:
#             result = {
#                 "success": False,
#                 "type": "ALREADY_SENT",
#                 "content": "email has sent to {} already.".format(in_user_email)}
#             return result
#
#         # 生成token
#         token=str(uuid4())
#
#         # ===========================这里就要存储表明该email已经在发送了，防止client循环发送（而此时一个邮件还没发送完成）=========
#         # 存储user_email、password、token
#         # {1}user_email <--> {1}token
#         cls.s_user_verify_token[in_user_email] = {
#             "email":in_user_email,
#             "password":in_password,
#             "token":token,
#         }
#         # ==============================================================================================================
#
#         server_email = 'jack.seaver@163.com'
#         server_password = 'JRDGPAFXHQOFPFZJ'   #需用第三方邮件客户专用密码
#         # user_email = '896626981@qq.com'
#         # user_email = 'jack.seaver@163.com'
#         # user_email = 'jack.seaver@outlook.com'
#         user_email = in_user_email
#
#
#         message = MIMEMultipart()
#         # message['From'] = server_email
#
#         nickname = 'PowerAI'
#         message['From'] = "%s <%s>" % (Header(nickname, 'utf-8'), server_email)
#
#         message['To'] = user_email
#         message['Subject'] = '【需要操作】验证以激活您的PowerAI账户'
#
#         verification_url = "https://powerai.cc/email_verify_page?" + urllib.parse.urlencode({
#             'email': user_email,
#             'token': token,
#         })
#         email_html_content = """
#         <html>
#          <body>
#             <p>尊贵的用户: </p>
#             <p>您好！</p>
#             <p>感谢您创建PowerAI账户，出于安全考虑，请点击下面的链接以验证并激活您的账户。</p>
#             <a href="{url}">{url}</a>
#             <p>您所申请的账号(e-mail)：</p>
#             <p style = 'font-size:20px;color:red;font-weight:bold;font-family: '黑体', 'sans-serif';'>{email}</p>
#             <p>您所设置的密码(e-mail)：</p>
#             <p style = 'font-size:20px;color:red;font-weight:bold;font-family: '黑体', 'sans-serif';'>{passwd}</p>
#             <p>祝您连接愉快,</p>
#             <p>PowerAI</p>
#           </body>
#         </html>""".format(url=verification_url, email=in_user_email, passwd=in_password)
#
#         message_body = MIMEText(email_html_content, 'html')
#
#         print("==============send verify email step: 1================", end="")
#         message.attach(message_body)
#         # message.attach(MIMEText(body, "plain"))
#         print("==============send verify email step: 2================", end="")
#
#         try:
#             # 方式一
#             # server = smtplib.SMTP('smtp.163.com', 25)
#
#             # 方式二（最常用、最安全的方式，如qq.com、163.com、outlook.com）
#             server = smtplib.SMTP_SSL('smtp.163.com', 465)
#
#             # 方式三（老的才可能用25、587）
#             # server = smtplib.SMTP('smtp.163.com', 587)
#             # server.starttls()
#
#
#             print("==============send verify email step: 3================", end="")
#             server.login(server_email, server_password)
#             print("==============send verify email step: 4================", end="")
#             text = message.as_string()
#             server.sendmail(server_email, user_email, text)
#             server.quit()
#         except Exception as e:
#             printd("email_verify() failed: {e}".format(e))
#             result = {
#                 "success": False,
#                 "type": "VERIFY_EMAIL_FAILED",
#                 "content": "email_verify() failed: {e}".format(e),
#                 "token": token,
#             }
#             return result
#
#         print("==============send verify email step: 5================", end="")
#
#         print("==============Email sent successfully.================", end="")
#
#         result = {
#             "success": True,
#             "content": "email_verify() success.",
#             "token":token,
#         }
#         return result
#
#     # 支付成功后，向email发送账单
#     @classmethod
#     def send_payment_email(cls, in_user_id, in_order_id, in_payment_type, in_amount):
#         result = {"success": False, "content": "send_payment_email() failed."}
#
#         # 已经发送验证email
#
#         server_email = 'jack.seaver@163.com'
#         server_password = 'JRDGPAFXHQOFPFZJ'   #需用第三方邮件客户专用密码
#         user_email = in_user_id
#
#
#         message = MIMEMultipart()
#         # message['From'] = server_email
#
#         nickname = 'PowerAI'
#         message['From'] = "%s <%s>" % (Header(nickname, 'utf-8'), server_email)
#
#         message['To'] = user_email
#         message['Subject'] = '【无需操作】支付成功。PowerAI账单请查收。'
#
#         email_html_content = """
#         <html>
#          <body>
#             <p>尊贵的用户: </p>
#             <p>您好！</p>
#             <p>您已成功支付。以下是本次账单信息：</p>
#             <p>您的账号(e-mail)：</p>
#             <p style = 'font-size:20px;color:black;font-family: '黑体', 'sans-serif';'>{email}</p>
#             <p>您的账单号：</p>
#             <p style = 'font-size:20px;color:black;font-family: '黑体', 'sans-serif';'>{order_id}</p>
#             <p>您的购买类型：</p>
#             <p style = 'font-size:20px;color:red;font-weight:bold;font-family: '黑体', 'sans-serif';'>{payment_type}</p>
#             <p>您的支付金额：</p>
#             <p style = 'font-size:20px;color:red;font-weight:bold;font-family: '黑体', 'sans-serif';'>{amount}</p>
#             <p>祝您连接愉快,</p>
#             <p>PowerAI</p>
#           </body>
#         </html>""".format(email=user_email, order_id=in_order_id, payment_type=in_payment_type, amount=in_amount)
#
#         message_body = MIMEText(email_html_content, 'html')
#
#         print("==============send verify email step: 1================", end="")
#         message.attach(message_body)
#         # message.attach(MIMEText(body, "plain"))
#         print("==============send verify email step: 2================", end="")
#
#         try:
#             # 方式一
#             # server = smtplib.SMTP('smtp.163.com', 25)
#
#             # 方式二（最常用、最安全的方式，如qq.com、163.com、outlook.com）
#             server = smtplib.SMTP_SSL('smtp.163.com', 465)
#
#             # 方式三（老的才可能用25、587）
#             # server = smtplib.SMTP('smtp.163.com', 587)
#             # server.starttls()
#
#
#             print("==============send verify email step: 3================", end="")
#             server.login(server_email, server_password)
#             print("==============send verify email step: 4================", end="")
#             text = message.as_string()
#             server.sendmail(server_email, user_email, text)
#             server.quit()
#         except Exception as e:
#             printd("send_payment_email() failed: {e}".format(e))
#             result = {
#                 "success": False,
#                 "type": "PAYMENT_EMAIL_FAILED",
#                 "content": "send_payment_email() failed: {e}".format(e),
#             }
#             return result
#
#         print("==============send verify email step: 5================", end="")
#
#         print("==============Email sent successfully.================", end="")
#
#         result = {
#             "success": True,
#             "type": "SUCCESS",
#             "content": "send_payment_email() success.",
#         }
#         return result
#
# def main():
#     User_Email_Verify.send_verify_email()
#
# if __name__ == "__main__" :
#     main()