import os
import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nps.settings')
# django.setup()
from django.db import models
from django.forms.models import model_to_dict

# Create your models here.

# 将改用户信息如open_id，入库
def register_user_info(in_user_id, in_nickname="", in_gender=False, in_language="", in_city="", in_province="") :
    t_user = Persistent_User_Info()
    t_user.user_id = in_user_id
    if in_nickname!="" :
        t_user.nickname = in_nickname

    t_user.gender = in_gender

    if in_language!="" :
        t_user.language = in_language

    if in_city!="" :
        t_user.city = in_city

    if in_province!="" :
        t_user.province = in_province

    t_user.save()

# 将一个dict增加到params表里
def add_params_with_dict(in_user_id, in_task_name, in_task_type, in_dict) :
    try :
        if in_task_type=="投资优化" :
            # 获取user
            t_user_obj = Persistent_User_Info.objects.get(user_id=in_user_id)

            # 增加task，并获取所增加的task对象
            t_task_obj = Persistent_Task.objects.create(user=t_user_obj, task_name=in_task_name, task_type=in_task_type)

            # 增加参数
            t_dict = in_dict
            if t_dict.get("id") :
                t_dict.pop("id")    # 去除可能存在的id
            if t_dict.get("task") :
                t_dict.pop("task")  # 去除可能存在的id
            t_params_obj = Persistent_Params_of_Investment_Opt.objects.create(task=t_task_obj, **t_dict)

            return t_params_obj

    except Persistent_User_Info.DoesNotExist :
        print("user with id \"{}\" not found.".format(in_user_id))
    except :
        print("add_params_with_dict() unknown error.")
    return None

# 用dict更新一个task的params
def update_params_with_dict(in_task_type, in_dict, in_task_id=0, in_user_id=0, in_task_name=0) :
    try :
        if in_task_type=="投资优化" :
            # 获取user
            if in_user_id!=0 :
                t_user_obj = Persistent_User_Info.objects.get(user_id=in_user_id)

            # 找到task，并获取所update的task对象
            if in_task_id==0 or in_task_id=="0":
                # open_id和task_name一起定位，如open_id和"autosave"
                t_task_obj = Persistent_Task.objects.get(task_name=in_task_name, user=t_user_obj)
            else:
                # task_id直接定位
                t_task_obj = Persistent_Task.objects.get(task_id=in_task_id)

            # 更新参数
            t_dict = in_dict
            if t_dict.get("id") :
                t_dict.pop("id")    # 去除可能存在的id
            if t_dict.get("task") :
                t_dict.pop("task")  # 去除可能存在的id
            t_params_obj = Persistent_Params_of_Investment_Opt.objects.filter(task=t_task_obj).update(**t_dict)

            return t_params_obj

    except Persistent_Task.DoesNotExist :
        if in_task_id == 0 or in_task_id=="0":
            print("task with name \"{}\" not found, change \"update\" to \"add\"".format(in_task_name))
            add_params_with_dict(in_user_id=in_user_id, in_task_name=in_task_name, in_task_type=in_task_type, in_dict=in_dict)
        else:
            print("task with id \"{}\" not found.".format(in_task_id))
    except :
        print("update_params_with_dict() unknown error.")
    return None

# 删除一个task的params
def del_task_and_paramst(in_task_id, in_task_type) :
    try :
        if in_task_type=="投资优化" :
            # 找到task和params
            t_task_obj = Persistent_Task.objects.get(task_id=in_task_id)

            # 删除参数
            Persistent_Params_of_Investment_Opt.objects.filter(task=t_task_obj).delete()

            # 删除任务
            Persistent_Task.objects.filter(task_id=in_task_id).delete()

    except Persistent_Task.DoesNotExist :
        print("task with id \"{}\" not found.".format(in_task_id))
    except Persistent_Params_of_Investment_Opt.DoesNotExist :
        print("params of task with id \"{}\" not found.".format(in_task_id))
    except :
        print("del_task_and_paramst() unknown error.")

# 获取admin缺省配置的dict
def get_default_params_dict(in_task_type="投资优化") :
    if in_task_type=="投资优化" :
        return get_params_dict(in_user_id=0, in_task_name="缺省"+in_task_type)  # admin id=0
    elif in_task_type=="机组组合" :
        return get_params_dict(in_user_id=0, in_task_name="缺省"+in_task_type)  # admin id=0
    else:
        return

# 获取admin的所有缺省task dict的list
def get_all_default_tasks_dict_list(in_user_id) :
    return get_tasks_dict_list(in_user_id=in_user_id)  # admin id=0

# 获取user的所有task dict的list
def get_tasks_dict_list(in_user_id) :
    try :
        user_obj = Persistent_User_Info.objects.get(user_id=in_user_id)
        if in_user_id == "o1Qen5J_nEK4hPTFQPq9Y6j_82hI":
            # admin返回所有方案
            task_objs = Persistent_Task.objects.all()
            task_objs = task_objs.exclude(task_name="autosave")
            task_objs = task_objs.exclude(task_name="缺省投资优化")
        else:
            task_objs = Persistent_Task.objects.filter(user=user_obj)
            task_objs = task_objs.exclude(task_name="autosave")
            task_objs = task_objs.exclude(task_name="缺省投资优化")

        t_tasks_list = []
        for i in task_objs :
            t_tasks_list.append(model_to_dict(i))

        return t_tasks_list

    except Persistent_User_Info.DoesNotExist :
        print("user with id \"{}\" not found.".format(in_user_id))
    except :
        print("get_tasks_list() unknown error.")
    return None

# 获取user下某task的配置dict
def get_params_dict(in_user_id, in_task_id=0, in_task_name=0) :
    try :
        obj_user = Persistent_User_Info.objects.get(user_id=in_user_id)

        # 用in_task_name查询: 仅当查询 "缺省"参数时，才用in_task_name; 否则必须用in_task_id（保证唯一性）
        if in_task_name !=0 :
            obj_task = Persistent_Task.objects.get(task_name=in_task_name)
        # 用in_task_id查询
        else:
            obj_task = Persistent_Task.objects.get(task_id=in_task_id)

        # 获取 "投资优化"表 的数据
        if obj_task.task_type == "投资优化" :
            t_obj = Persistent_Params_of_Investment_Opt.objects.get(task=obj_task)
            return model_to_dict(t_obj)
        # 获取 "机组组合"表 的数据
        elif obj_task.task_type == "机组组合" :
            # t_obj = Persistent_Params_of_Unit_Commitment.objects.get(task=obj_task)
            # return model_to_dict(t_obj)
            pass
        else :
            return None

    except Persistent_User_Info.DoesNotExist :
        pass
        # print("user with id \"{}\" not found.".format(in_user_id))
    except Persistent_Task.DoesNotExist :
        pass
        # print("task with id \"{}\" not found.".format(in_task_id))
    except :
        print("get_params_dict() unknown error.")
    return None

#
def del_task(in_user_id, in_task_id) :
    try :
        obj_user = Persistent_User_Info.objects.get(user_id=in_user_id)
        Persistent_Task.objects.filter(task_id=in_task_id).delete()
        return

    except Persistent_User_Info.DoesNotExist :
        print("user with id \"{}\" not found.".format(in_user_id))
    except Persistent_Task.DoesNotExist :
        print("task with id \"{}\" not found.".format(in_task_id))
    except :
        print("get_params_dict() unknown error.")
    return None

# 执行migrate之前，记得要在admin.py中注册下面的class。（如果出错，可以考虑删除db.sqlite3后，再migrate，但需要重新创建admin）
# 用户信息表
class Persistent_User_Info(models.Model):
    user_id = models.CharField(max_length=128, verbose_name="用户ID", primary_key=True, )
    nickname = models.CharField(default="", max_length=128, verbose_name="昵称")

    gender_categories = [
        (True, "女"),
        (False, "男")
    ]
    gender = models.BooleanField(default=False, choices = gender_categories, verbose_name="性别")

    language = models.CharField(default="zh_CN", max_length=64, verbose_name="语言")
    city = models.CharField(default="", max_length=64, verbose_name="城市")
    province = models.CharField(default="", max_length=64, verbose_name="省份")

# 任务信息表
class Persistent_Task(models.Model):
    # # 定义一个商品模型，用来作为主表
    # class Goods(models.Model):
    #     gid = models.AutoField(primary_key=True)
    #
    # # 定义一个订单模型，用来作为商品表的从表
    # class Order(models.Model):
    #     '''
    #     商品模型与订单模型是一种主从关系，得先有商品，然后才能有所谓的订单
    #     在Order模型中定义goods为外键，goods引用自Goods模型中的主键
    #     设置的on_delete选项为CASCADE, 即当商品删除时，对应的订单也会一同删除。
    #     '''
        # goods = models.ForeignKey(to=Goods, to_field='gid', on_delete=models.CASCADE)

    # 外键-->Persistent_User_Info.s_user_id
    user = models.ForeignKey(to=Persistent_User_Info, to_field='user_id', on_delete=models.CASCADE)

    task_id = models.AutoField(primary_key=True, verbose_name="任务ID")
    task_name = models.CharField(default="新建任务", max_length=256, verbose_name="任务名称")
    task_type = models.CharField(default="投资优化", max_length=128, verbose_name="任务类型")     # 如"投资优化"、"机组组合"等

# 任务参数表（投资优化）
class Persistent_Params_of_Investment_Opt(models.Model):
    s_float_inf = 10000000
    s_float_negative_inf = -10000000

    # 外键-->Persistent_Task.s_task_id
    task = models.ForeignKey(to=Persistent_Task, to_field='task_id', on_delete=models.CASCADE)

    solver_name = models.CharField(default="cplex", max_length=64, verbose_name="解算器名称")
    simu_hours = models.IntegerField(default=720, verbose_name="仿真时长（h）")
    objective_function_type = models.CharField(default="social", max_length=128, verbose_name="目标函数类型")  # 如"social"、"financial"等

    # 负荷
    load_type = models.CharField(default="city", max_length=64, verbose_name="负荷类型")  # 如"city"、"industry"等
    elec_load_max = models.FloatField(default=100.0, verbose_name="最大电负荷（MW）")
    heat_load_max = models.FloatField(default=100.0, verbose_name="最大热负荷（MW）")
    cold_load_max = models.FloatField(default=100.0, verbose_name="最大冷负荷（MW）")

    # 风电
    wind_capital_cost = models.FloatField(default=5000.0, verbose_name="单位造价（元/kW）")
    wind_p_nom = models.FloatField(default=0.0, verbose_name="存量装机（MW）")
    wind_p_nom_extendable = models.BooleanField(default=False, verbose_name="是否优化装机")
    wind_p_nom_max = models.FloatField(default=s_float_inf, verbose_name="技术可开发装机（MW）")

    # 光伏
    pv_capital_cost = models.FloatField(default=4000.0, verbose_name="单位造价（元/kW）")
    pv_p_nom = models.FloatField(default=0.0, verbose_name="存量装机（MW）")
    pv_p_nom_extendable = models.BooleanField(default=False, verbose_name="是否优化装机")
    pv_p_nom_max = models.FloatField(default=s_float_inf, verbose_name="技术可开发装机（MW）")

    # 水电
    hydro_type = models.CharField(default="character", max_length=64, verbose_name="水电建模方式") # 如"character定特性"、"energy定发电量"等

    hydro_capital_cost = models.FloatField(default=10000.0, verbose_name="单位造价（元/kW）")
    hydro_p_nom = models.FloatField(default=0.0, verbose_name="存量装机（MW）")
    hydro_p_nom_extendable = models.BooleanField(default=False, verbose_name="是否优化装机")
    hydro_p_nom_max = models.FloatField(default=s_float_inf, verbose_name="技术可开发装机（MW）")
    hydro_hours_max = models.FloatField(default=3000.0, verbose_name="最大年发电利用小时数（h）")

    # 煤电
    coal_marginal_cost = models.FloatField(default=0.06, verbose_name="发电边际成本（元/kWh）")  #待核实
    coal_capital_cost = models.FloatField(default=3200.0, verbose_name="单位造价（元/kW）")
    coal_p_nom = models.FloatField(default=0.0, verbose_name="存量装机（MW）")
    coal_p_nom_extendable = models.BooleanField(default=False, verbose_name="是否优化装机")
    coal_p_nom_max = models.FloatField(default=s_float_inf, verbose_name="技术可开发装机（MW）")
    coal_p_max_pu = models.FloatField(default=1.0, verbose_name="最大出力水平（P.U.）")
    coal_p_min_pu = models.FloatField(default=0.4, verbose_name="最小出力水平（P.U.）")

    # 柴发
    diesel_marginal_cost = models.FloatField(default=1.62, verbose_name="发电边际成本（元/kWh）")
    diesel_capital_cost = models.FloatField(default=6700.0, verbose_name="单位造价（元/kW）")
    diesel_p_nom = models.FloatField(default=0.0, verbose_name="存量装机（MW）")
    diesel_p_nom_extendable = models.BooleanField(default=False, verbose_name="是否优化装机")
    diesel_p_nom_max = models.FloatField(default=s_float_inf, verbose_name="技术可开发装机（MW）")
    diesel_p_max_pu = models.FloatField(default=1.0, verbose_name="最大出力水平（P.U.）")
    diesel_p_min_pu = models.FloatField(default=0.15, verbose_name="最小出力水平（P.U.）")

    # 核电
    nuclear_marginal_cost = models.FloatField(default=0.01, verbose_name="发电边际成本（元/kWh）")
    nuclear_capital_cost = models.FloatField(default=12000.0, verbose_name="单位造价（元/kW）")
    nuclear_p_nom = models.FloatField(default=0.0, verbose_name="存量装机（MW）")
    nuclear_p_nom_extendable = models.BooleanField(default=False, verbose_name="是否优化装机")
    nuclear_p_nom_max = models.FloatField(default=s_float_inf, verbose_name="技术可开发装机（MW）")
    nuclear_p_max_pu = models.FloatField(default=1.0, verbose_name="最大出力水平（P.U.）")
    nuclear_p_min_pu = models.FloatField(default=0.9, verbose_name="最小出力水平（P.U.）")

    # 天然气: 若3元/方，由于1方天然气热值10kWh，因此大约为0.3元/kWh
    gas_price = models.FloatField(default=0.3, verbose_name="天然气价格（元/kWh）")

    # 天然气机组
    gas_capital_cost = models.FloatField(default=2200.0, verbose_name="单位造价（元/kW）")
    gas_p_nom = models.FloatField(default=0.0, verbose_name="存量装机（MW）")
    gas_p_nom_extendable = models.FloatField(default=False, verbose_name="是否优化装机")
    gas_p_nom_max = models.FloatField(default=s_float_inf, verbose_name="技术可开发装机（MW）")
    gas_p_max_pu = models.FloatField(default=1.0, verbose_name="最大出力水平（P.U.）")
    gas_p_min_pu = models.FloatField(default=0.0, verbose_name="最小出力水平（P.U.）")

    gas_effi = models.FloatField(default=0.5, verbose_name="效率")

    # 热电联产
    chp_capital_cost = models.FloatField(default=1750.0, verbose_name="单位造价（元/kW）")
    chp_p_nom = models.FloatField(default=0.0, verbose_name="存量装机（MW）")
    chp_p_nom_extendable = models.FloatField(default=False, verbose_name="是否优化装机")
    chp_p_nom_max = models.FloatField(default=s_float_inf, verbose_name="技术可开发装机（MW）")

    chp_effi = models.FloatField(default=0.8, verbose_name="效率")
    chp_ratio12 = models.FloatField(default=1.0, verbose_name="热电比")
    chp_p_max_pu = models.FloatField(default=1.0, verbose_name="最大出力水平（P.U.）")
    chp_p_min_pu = models.FloatField(default=0.0, verbose_name="最小出力水平（P.U.）")

    # 天然气锅炉
    gas_boiler_capital_cost = models.FloatField(default=200.0, verbose_name="单位造价（元/kW）")
    gas_boiler_p_nom = models.FloatField(default=0.0, verbose_name="存量装机（MW）")
    gas_boiler_p_nom_extendable = models.FloatField(default=False, verbose_name="是否优化装机")
    gas_boiler_p_nom_max = models.FloatField(default=s_float_inf, verbose_name="技术可开发装机（MW）")
    gas_boiler_effi = models.FloatField(default=0.95, verbose_name="效率")

    # 电制冷机组
    elec_cooler_capital_cost = models.FloatField(default=200.0, verbose_name="单位造价（元/kW）")
    elec_cooler_p_nom = models.FloatField(default=0.0, verbose_name="存量装机（MW）")
    elec_cooler_p_nom_extendable = models.FloatField(default=False, verbose_name="是否优化装机")
    elec_cooler_effi = models.FloatField(default=5.0, verbose_name="效率")

    # 电制热机组
    elec_heater_capital_cost = models.FloatField(default=200.0, verbose_name="单位造价（元/kW）")
    elec_heater_p_nom = models.FloatField(default=0.0, verbose_name="存量装机（MW）")
    elec_heater_p_nom_extendable = models.FloatField(default=False, verbose_name="是否优化装机")
    elec_heater_effi = models.FloatField(default=3.0, verbose_name="效率")

    # 热泵机组
    heatpump_capital_cost = models.FloatField(default=1000.0, verbose_name="单位造价（元/kW）")
    heatpump_p_nom = models.FloatField(default=0.0, verbose_name="存量装机（MW）")
    heatpump_p_nom_extendable = models.FloatField(default=False, verbose_name="是否优化装机")
    heatpump_effi = models.FloatField(default=4.0, verbose_name="效率")
    heatpump_ratio12 = models.FloatField(default=1.0, verbose_name="冷热比")

    # 抽蓄
    php_p_capital_cost = models.FloatField(default=2800.0, verbose_name="功率单位造价（元/kW）")
    php_e_capital_cost = models.FloatField(default=460.0, verbose_name="能量单位造价（元/kWh）")
    php_p_nom = models.FloatField(default=0.0, verbose_name="功率存量装机（MW）")
    php_e_nom = models.FloatField(default=0.0, verbose_name="能量存量装机（MW）")
    php_pe_nom_extendable = models.FloatField(default=False, verbose_name="是否优化功率和能量装机")
    php_p_nom_max = models.FloatField(default=s_float_inf, verbose_name="功率技术可开发装机（MW）")
    php_e_nom_max = models.FloatField(default=s_float_inf, verbose_name="能量技术可开发装机（MW）")
    php_charge_effi = models.FloatField(default=0.9, verbose_name="蓄电效率")
    php_discharge_effi = models.FloatField(default=0.9, verbose_name="放电效率")

    # 蓄电系统
    elec_storage_p_capital_cost = models.FloatField(default=240.0, verbose_name="功率单位造价（元/kW）")
    elec_storage_e_capital_cost = models.FloatField(default=1380.0, verbose_name="能量单位造价（元/kWh）")
    elec_storage_p_nom = models.FloatField(default=0.0, verbose_name="功率存量装机（MW）")
    elec_storage_e_nom = models.FloatField(default=0.0, verbose_name="能量存量装机（MW）")
    elec_storage_pe_nom_extendable = models.FloatField(default=False, verbose_name="是否优化功率和能量装机")
    elec_storage_p_nom_max = models.FloatField(default=s_float_inf, verbose_name="功率技术可开发装机（MW）")
    elec_storage_e_nom_max = models.FloatField(default=s_float_inf, verbose_name="能量技术可开发装机（MW）")
    elec_storage_charge_effi = models.FloatField(default=0.95, verbose_name="蓄电效率")
    elec_storage_discharge_effi = models.FloatField(default=0.95, verbose_name="放电效率")

    # 电蓄氢、放电系统
    hydrogen_storage_charge_p_capital_cost = models.FloatField(default=2240.0, verbose_name="功率单位造价（元/kW）")
    hydrogen_storage_discharge_p_capital_cost = models.FloatField(default=2200.0, verbose_name="功率单位造价（元/kW）")
    hydrogen_storage_e_capital_cost = models.FloatField(default=6.0, verbose_name="能量单位造价（元/kWh）")
    hydrogen_storage_p_nom = models.FloatField(default=0.0, verbose_name="功率存量装机（MW）")
    hydrogen_storage_e_nom = models.FloatField(default=0.0, verbose_name="能量存量装机（MW）")
    hydrogen_storage_pe_nom_extendable = models.FloatField(default=False, verbose_name="是否优化功率和能量装机")
    hydrogen_storage_p_nom_max = models.FloatField(default=s_float_inf, verbose_name="功率技术可开发装机（MW）")
    hydrogen_storage_e_nom_max = models.FloatField(default=s_float_inf, verbose_name="能量技术可开发装机（MW）")
    hydrogen_storage_charge_effi = models.FloatField(default=0.8, verbose_name="蓄氢效率")
    hydrogen_storage_discharge_effi = models.FloatField(default=0.6, verbose_name="放电效率")

    # 电蓄热、放热系统
    heat_storage_p_capital_cost = models.FloatField(default=200.0, verbose_name="功率单位造价（元/kW）")
    heat_storage_e_capital_cost = models.FloatField(default=200.0, verbose_name="能量单位造价（元/kWh）")
    heat_storage_p_nom = models.FloatField(default=0.0, verbose_name="功率存量装机（MW）")
    heat_storage_e_nom = models.FloatField(default=0.0, verbose_name="能量存量装机（MW）")
    heat_storage_pe_nom_extendable = models.FloatField(default=False, verbose_name="是否优化功率和能量装机")
    heat_storage_p_nom_max = models.FloatField(default=s_float_inf, verbose_name="功率技术可开发装机（MW）")
    heat_storage_e_nom_max = models.FloatField(default=s_float_inf, verbose_name="能量技术可开发装机（MW）")
    heat_storage_charge_effi = models.FloatField(default=0.95, verbose_name="蓄热效率")
    heat_storage_discharge_effi = models.FloatField(default=1.0, verbose_name="放热效率")

    # 电蓄冷、放冷系统
    cold_storage_p_capital_cost = models.FloatField(default=200.0, verbose_name="功率单位造价（元/kW）")
    cold_storage_e_capital_cost = models.FloatField(default=200.0, verbose_name="能量单位造价（元/kWh）")
    cold_storage_p_nom = models.FloatField(default=0.0, verbose_name="功率存量装机（MW）")
    cold_storage_e_nom = models.FloatField(default=0.0, verbose_name="能量存量装机（MW）")
    cold_storage_pe_nom_extendable = models.FloatField(default=False, verbose_name="是否优化功率和能量装机")
    cold_storage_p_nom_max = models.FloatField(default=s_float_inf, verbose_name="功率技术可开发装机（MW）")
    cold_storage_e_nom_max = models.FloatField(default=s_float_inf, verbose_name="能量技术可开发装机（MW）")
    cold_storage_charge_effi = models.FloatField(default=0.95, verbose_name="蓄冷效率")
    cold_storage_discharge_effi = models.FloatField(default=1.0, verbose_name="放冷效率")

    # 吸收节点(p<0)
    slack_absorp_p_max = models.FloatField(default=100.0, verbose_name="最大吸收功率（MW）")
    slack_absorp_marginal_cost = models.FloatField(default=-0.0, verbose_name="边际电量成本（元/kWh）") # 这里若考虑新能源倒送成本，则应为负值，即乘以负的功率，成本为正
    # 注入节点(p>0)
    slack_inject_p_max = models.FloatField(default=100.0, verbose_name="最大注入功率（MW）")
    slack_inject_marginal_cost = models.FloatField(default=0.0, verbose_name="边际电量成本（元/kWh）") # 这里若考虑网电成本，则应为正值，即乘以正的功率，成本为正

# 测试
# 注意：这个main()会报错（settings.py方面的错误）,无法调试models.py中的数据库class，必须在后台apache中才能调试
def main():
    print("hello")

if __name__ == "__main__" :
    main()

