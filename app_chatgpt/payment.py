import threading
import time
from alipay import AliPay
from alipay.utils import AliPayConfig

from .Chat_GPT import Chatgpt_Server_Config

# 添加对上一级目录import的支持
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import Global
Global.init()


class Payment_Query_Thread(threading.Thread):
    def __init__(self, in_user_id, in_order_id, inout_user_dict):
        super().__init__()
        self.user_id = in_user_id
        self.order_id = in_order_id
        self.user_dict_obj = inout_user_dict

    def run(self):
        count = 0
        while count < Payment.s_payment_query_timeout_times:    # 200次
            # 调用查询支付结果的函数，这里省略具体实现
            result = Payment.server_pay_query(self.user_id, self.order_id)

            if result["success"]:
                # print('Payment succeeded!')
                print("user_payment_dict before is : {}".format(self.user_dict_obj), end="")
                self.user_dict_obj["pay_success_finally"]=True
                print("user_payment_dict after is : {}".format(self.user_dict_obj), end="")
                return

            time.sleep(Payment.s_payment_query_per_second)  # 等待200ms后再次查询
            count += 1

        print("payment timeout with user_payment_dict: {}".format(self.user_dict_obj), end="")
        return

class Payment():
    '''
    1、如果支付宝密钥生成工具生成的密钥没有头尾要自己加上
    2、必须要注意的是：格式头尾和content必须要换行，而content必须是完整的一行
    私钥格式：
    -----BEGIN RSA PRIVATE KEY-----
        base64 encoded content
    -----END RSA PRIVATE KEY-----

    公钥格式：
    -----BEGIN PUBLIC KEY-----
        base64 encoded content
    -----END PUBLIC KEY-----
    '''
    s_app_private_key_string = open(Global.get("path") + 'app_chatgpt/prkey.txt').read()
    s_alipay_public_key_string = open(Global.get("path") + 'app_chatgpt/alipubkey.txt').read()
    s_appid = "2021003190651790"                                        # 应用列表中“应用2.0签约******”的appid
    s_sign_type = "RSA2"
    s_debug=False
    s_verbose=False

    s_payment_query_per_second = 0.2        # 0.2秒查询一次
    s_payment_query_timeout_times = 200     # 查询200次即40s后timeout

    s_users_dict = {}
    '''
    s_users_dict = {
        "jack.seaver@163.com"+":"+"some_order_no":{
            "vip_type":"",
            "pay_success_finally":False,
            "alipay_obj":alipay_obj,
            "amount":amount,
        },
    }
    '''

    # 支付成功后的必须的回调（执行VIP等级调整、存盘等操作）
    @classmethod
    def pay_success_callback(cls):
        print("server(alipay's non-parameter callback): some user's payment finally succeeded.", end="")
        return

    # def pay_success_callback(cls, in_user_id, in_order_id):
    #     result = { "success":False, "type":"ERROR", "content":"pay_success_callback() error." }
    #     user_with_order_id = cls.s_users_dict.get(in_user_id +":" + in_order_id)
    #     if not user_with_order_id:
    #         result = {"success": False, "type": "USER_NOT_FOUND", "content": "pay_success_callback() user \"{}\" not found.".format(in_user_id)}
    #         print(result, end="")
    #         return result
    #
    #     vip_type = cls.s_users_dict[user_with_order_id].get("vip_type")
    #     print("user \"{}\"'s payment with order id \"{}\" ({}) finally succeeded.".format(in_user_id, in_order_id, vip_type), end="")

    # 发起支付
    @classmethod
    def pay_precreate(cls, in_user_id, in_order_id, in_subject, in_vip_type="vip_monthly", in_invoke_payment=False, in_callback=None):
        result = { "success":False, "type":"ERROR", "content":"pay_precreate() error." }
        try:
            print("=========================1============================", end="")
            # my_alipay_obj = Payment(in_user_id, in_order_id, in_vip_type)    # 实例化my_alipay仅仅是便于存储不同user、不同order的回调函数

            # 阿里支付宝的回调：居然不能带自定义参数如user_id和order_id之类！！！带了也会截去，所以回调powerai.cc/pay_success_callback时，data都是None
            call_back_url = "https://powerai.cc/pay_success_callback"
            # call_back_url = "https://powerai.cc/pay_success_callback?user_id={}&order_id={}".format(in_user_id, in_order_id)
            print("call_back_url is : {}".format(call_back_url), end="")
            alipay = AliPay(
                appid=cls.s_appid,
                app_notify_url=call_back_url,                               # 回调url（这里是"https://powerai.cc/xxx"这样的字符串，而不是python内部函数！）
                # app_notify_url=in_callback,                                 # 回调url（这里是"https://powerai.cc/xxx"这样的字符串，而不是python内部函数！）
                app_private_key_string=cls.s_app_private_key_string,        # 应用私钥
                alipay_public_key_string=cls.s_alipay_public_key_string,    # 支付宝公钥
                sign_type=cls.s_sign_type,                                  # RSA 或者 RSA2(具体要看你的密钥是什么类型)
                debug=cls.s_debug,
                verbose=cls.s_verbose,
                config=AliPayConfig(timeout=cls.s_payment_query_per_second*cls.s_payment_query_timeout_times)
            )
            print("=========================2============================", end="")

            if in_invoke_payment:
                # 购买次数
                invoke_pay = Chatgpt_Server_Config.s_user_invoke_payment.get(in_vip_type)
                if invoke_pay:
                    amount = invoke_pay["cost"]
                    print("---------invoke_pay is '{}'---------".format(invoke_pay), end="")
                else:
                    result = {"success": False, "type": "ERROR_VIP_TYPE", "content": "pay_precreate() user \"{}\" vip_type \"{}\" error.".format(in_user_id, in_vip_type)}
                    print(result, end="")
                    return result
            else:
                # 购买VIP
                amount_index = Chatgpt_Server_Config.s_user_level_index.get(in_vip_type)
                if not amount_index:
                    result = {"success": False, "type": "ERROR_VIP_TYPE", "content": "pay_precreate() user \"{}\" vip_type \"{}\" error.".format(in_user_id, in_vip_type)}
                    print(result, end="")
                    print("---------amount_index is '{}'---------".format(amount_index), end="")
                    return result

                amount = Chatgpt_Server_Config.s_user_level_fee[amount_index]
            print("=========================3============================", end="")

            user_dict = {
                "vip_type": in_vip_type,
                "invoke_payment": in_invoke_payment,
                "pay_success_finally":False,
                "alipay_obj": alipay,
                "amount": amount,
            }
            cls.s_users_dict[in_user_id +":" + in_order_id] = user_dict

            print("=========================4============================", end="")
            print("subject: {}".format(in_subject), end="")
            print("order_id: {}".format(in_order_id), end="")
            print("amount: {}".format(amount), end="")
            response = alipay.api_alipay_trade_precreate(
                subject = in_subject,                                       # 订单标题
                out_trade_no = in_order_id,                                 # 订单号（不可重复）
                total_amount = amount                                       # 支付金额（元）
            )
            print("=========================5============================", end="")
        except Exception as e:
            print("=========================6============================", end="")
            result = {"success": False, "type": "ALIPAY_ERROR", "content": "pay_precreate() api_alipay_trade_precreate error: {}".format(e)}
            print(result, end="")
            return result

        # 这里应该返回 {
        # 'code': '10000',
        # 'msg': 'Success',
        # 'out_trade_no': 'in_order_id',
        # 'qr_code': 'https://qr.alipay.com/bax05832mvaotxhcpjeh6074'}

        result = {"success": True, "type": "SUCCESS", "content": response, "amount":amount}
        # 新起thread查询支付结果
        print("server: try to start server query thread.", end="")
        query_thread = Payment_Query_Thread(in_user_id, in_order_id, cls.s_users_dict[in_user_id +":" + in_order_id])
        query_thread.start()
        print("server: payment query thread started.", end="")
        # print(result, end="")
        return result

    # server查询支付结果
    @classmethod
    def server_pay_query(cls, in_user_id, in_order_id):
        result = { "success":False, "type":"ERROR", "content":"pay_query() error." }
        user_with_order_id = cls.s_users_dict.get(in_user_id +":" + in_order_id)
        if not user_with_order_id:
            result = {"success": False, "type": "USER_NOT_FOUND", "content": "server_pay_query() user \"{}\" not found.".format(in_user_id)}
            print(result, end="")
            return result

        try:
            response = user_with_order_id["alipay_obj"].api_alipay_trade_query(out_trade_no=in_order_id)
        except Exception as e:
            result = {"success": False, "type": "ALIPAY_ERROR", "content": "server_pay_query() api_alipay_trade_query error: {}".format(e)}
            print(result, end="")
            return result

        if response.get("trade_status", "") == "TRADE_SUCCESS":
            # ============支付最终成功，调用server侧的VIP信息存盘============
            vip_type = user_with_order_id.get("vip_type")
            invoke_payment = user_with_order_id.get("invoke_payment")
            amount = user_with_order_id.get("amount")
            if vip_type:
                try:
                    Chatgpt_Server_Config.db_add_payment_record_and_send_payment_email(in_user_id, in_order_id, vip_type, amount)
                    Chatgpt_Server_Config.db_update_vip_info(in_user_id, vip_type, invoke_payment)
                except Exception as e:
                    result = {"success": False, "type": "PAY_FATAL_ERROR", "content": "server: db_update_vip_info() error: {}".format(e)}
                    print(result, end="")
                    return result
                result = {"success": True, "type": "PAY_COMPLETED", "content": "server: payment successful finally."}
            else:
                result = {"success": False, "type": "PAY_FATAL_ERROR", "content": "server: payment fatal error. vip_type is none."}
                print(result, end="")
                return result
            # ============支付最终成功，调用server侧的VIP信息存盘============
        else:
            result = {"success": False, "type": "PAY_NOT_COMPLETED", "content": "server_pay_query() payment not successful yet."}

        # print(result, end="")
        return result

    # client查询支付结果(注意：client有可能因为任何原因没有来查询支付结果)
    @classmethod
    def client_pay_query(cls, in_user_id, in_order_id):
        result = { "success":False, "type":"ERROR", "content":"client_pay_query() error." }
        user_with_order_id = cls.s_users_dict.get(in_user_id +":" + in_order_id)
        if not user_with_order_id:
            result = {"success": False, "type": "USER_NOT_FOUND", "content": "client_pay_query() user \"{}\" not found.".format(in_user_id)}
            print(result, end="")
            return result

        user_pay_success_finally = user_with_order_id.get("pay_success_finally")
        if user_pay_success_finally and user_pay_success_finally==True:
            result = {"success": True, "type": "PAY_COMPLETED", "content": "client_pay_query() paid successfully."}
        else:
            result = {"success": False, "type": "PAY_NOT_COMPLETED", "content": "client_pay_query() payment not successful yet."}

        # print(result, end="")
        return result

    # 取消支付
    @classmethod
    def pay_cancel(cls, in_user_id, in_order_id):
        result = { "success":False, "type":"ERROR", "content":"pay_cancel() error." }
        user_with_order_id = cls.s_users_dict.get(in_user_id +":" + in_order_id)
        if not user_with_order_id:
            result = {"success": False, "type": "USER_NOT_FOUND", "content": "pay_cancel() user \"{}\" not found.".format(in_user_id)}
            print(result, end="")
            return result

        try:
            response = user_with_order_id["alipay_obj"].api_alipay_trade_cancel(out_trade_no=in_order_id)
        except Exception as e:
            result = {"success": False, "type": "ALIPAY_ERROR", "content": "pay_cancel() api_alipay_trade_cancel error: {}".format(e)}
            print(result, end="")
            return result

        result = {"success": True, "type": "PAY_CANCELED", "content": "payment canceled successfully."}
        # print(result, end="")
        return result

def main():
    Payment.pay_precreate(
        in_user_id="admin",
        in_order_id="12345678",
        in_subject="VIP支付",
        in_vip_type="vip_annual"
        # in_vip_type="vip_monthly"
        # in_vip_type="vip_permanent"
    )

def main1():
    # 密钥工具生成的私钥，和支付宝公钥（我保存在了文件中）
    app_private_key_string = open("prkey.txt").read()
    alipay_public_key_string = open("alipubkey.txt").read()

    print(app_private_key_string)
    print(alipay_public_key_string)
    '''
    这里打印应该是这种格式（如果支付宝密钥生成工具生成的密钥没有头尾要自己加上）
    私钥格式：
    -----BEGIN RSA PRIVATE KEY-----
        base64 encoded content
    -----END RSA PRIVATE KEY-----

    公钥格式：
    -----BEGIN PUBLIC KEY-----
        base64 encoded content
    -----END PUBLIC KEY-----
    
    必须要注意的是：格式头尾和content必须要换行，而content必须是完整的一行
    '''

    alipay = AliPay(
        appid="2021003190651790",  # 应用列表中“应用2.0签约******”的appid
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,  # 应用私钥
        alipay_public_key_string=alipay_public_key_string,  # 支付宝公钥
        sign_type="RSA2",  # RSA 或者 RSA2(具体要看你的密钥是什么类型)
        debug=False,  # 默认False
        verbose=False,
        config = AliPayConfig(timeout=30)
    )

    out_trade_no = "out_trade_no_123"
    # 创建订单
    result = alipay.api_alipay_trade_precreate(
        subject="test subject",  # 订单标题
        out_trade_no=out_trade_no,  # 订单号（不可重复）
        total_amount=0.1  # 订单金额，单位元
    )

    print(result)
    # 这里应该打印出{'code': '10000', 'msg': 'Success', 'out_trade_no': 'out_trade_no_123', 'qr_code': 'https://qr.alipay.com/bax05832mvaotxhcpjeh6074'}
    # 其中用qr_code生成二维码，支付宝扫描即可付款

    # # check order status
    # paid = False
    # for i in range(30):
    #     # check every 3s, and 10 times in all
    #     print("now sleep 3s")
    #     time.sleep(3)
    #     result = alipay.api_alipay_trade_query(out_trade_no=out_trade_no)
    #     if result.get("trade_status", "") == "TRADE_SUCCESS":
    #         paid = True
    #         break
    #     print("not paid...")
    #
    # # order is not paid in 30s , cancel this order
    # if paid is False:
    #     print("支付失败，取消订单")
    #     alipay.api_alipay_trade_cancel(out_trade_no=out_trade_no)
    # else:
    #     print("支付成功")




    # alipay = AliPay(
    #     appid="2021000121627616",
    #     app_notify_url=None,  # 默认回调 url
    #     app_private_key_string=app_private_key_string,
    #     # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
    #     alipay_public_key_string=alipay_public_key_string,
    #     sign_type="RSA2",  # RSA 或者 RSA2
    #     debug=False,  # 默认 False
    #     verbose=False,  # 输出调试数据
    #     config=AliPayConfig(timeout=15)  # 可选，请求超时时间
    # )
    #
    # res = alipay.api_alipay_trade_page_pay(
    #     out_trade_no='1000101',  # 订单号
    #     total_amount=float(999),  # 价格
    #     subject='气球',  # 名称
    #     return_url='http://127.0.0.1:8080/pay/success/',  # 支付成功后会跳转的页面
    #     notify_url='http://127.0.0.1:8000/order/',  # 回调地址，支付成功后支付宝会向这个地址发送post请求
    # )
    #
    # gataway = 'https://openapi.alipaydev.com/gateway.do?'
    # # 支付链接
    # pay_url = gataway + res
    # print(pay_url)

if __name__ == "__main__" :
    main()


