from pyomo.environ import *
import pyomo.gdp as gdp
# from cplex import *
import numpy as np
import pandas as pd
from Relational_Plots import *
from Python_User_Logger import *
from Data_Analysis import *
import Global
from Create_Word import *
import gc
import copy

g_performance_test = False
g_print_cons = True
print_node_para_detail = False
print_model = False
print_opt_list = False
pic_output = True
print_pyomo_result = True

def print_cons(in_expr, in_i):
    global g_print_cons
    if g_print_cons==True and in_i==1:
        print(in_expr)

def performance_test_print(in_string):
    global g_performance_test
    if g_performance_test==True:
        print(in_string)

g_NPV_Work = True
def npv(in_value, in_rate, i, in_computer_year_days):
    global g_NPV_Work
    # if i//8760>0:
    # print(i+1,"h, {}有折现率{},npv为{}".format(in_value, in_rate, in_value / ((1+in_rate)**(i//8760))))
    if g_NPV_Work==True:
        return in_value / ((1 + in_rate) ** (i // in_computer_year_days)) # in_computer_year_days为8760或8760-春节小时时长
    else:
        return in_value

def print_members(in_obj):
    for t_name in vars(in_obj):
        print(t_name)

def print_funcs(in_obj):
    for t_name in dir(in_obj):
        print(t_name)

def Get_Current_Func_Name():
    return inspect.stack()[1][3]

def Get_Class_Funcs(in_klass):
    t_funcs = []
    for k in in_klass.__bases__:
        Get_Class_Funcs(k)
    for m in dir(in_klass):
        if "__" not in m:
            t_funcs.append(m)
    return t_funcs

def Call_Class_Funcs(in_klass, in_case="", in_path="xls/", in_lambda=0):
    t_obj = in_klass()
    t_funcs_str = Get_Class_Funcs(in_klass)
    for t_str in t_funcs_str:
        t_func = getattr(t_obj, t_str)
        if t_str==in_case:
            return t_func(in_called=True, in_path=in_path, in_lambda=in_lambda)
        else:
            continue
            # return t_func(in_called=False, in_path=in_path)

class Spring_Festival():
    def __init__(self, in_years, in_bypass=False, in_start_day=10, in_stop_day=60):
        self.simu_years = in_years
        self.bypass = in_bypass
        self.start_day = in_start_day
        self.stop_day = in_stop_day
        self.hours = (in_stop_day-in_start_day+1)*24*self.simu_years

    def Year_Days(self):
        t_year_days = 0
        if self.bypass==True:
            t_year_days = 8760-self.hours
        else:
            t_year_days = 8760
        return t_year_days

# ===============================Base类================================
class Object_Base():
    def __init__(self, in_sys, in_name_id, in_model):
        self._sys = in_sys  #系统信息。前缀"_"的为protected成员，前缀"__"的为private成员
        if in_sys!=0:
            in_sys.object_list.append(self)

        self.name_id = in_name_id
        self.mode = in_model

        self.p_nom_extendable = True  #额定容量是否可以扩展，如不能扩展，则额定容量fix为固定值

        self.sequence_output_list = []
        # 时序数据输出用的多个list
        # [ {   "caption":"xxx1",
        #       "name":"price_list",
        #       "type":"param",
        #       "list":list1
        #   },
        #   {
        #       "caption":"xxx2",
        #       "name":"p_list",
        #       "type":"var",
        #       "list":list2
        #   }, ]
        self.var_output_list = []
        # 普通变量输出的list
        # [ {   "caption":"xxx1",
        #       "name":"p_max",
        #       "type":"param",
        #       "unit":""
        #   },
        #   {
        #       "caption":"xxx2",
        #       "name":"p_nom",
        #       "type":"var",
        #       "unit":""
        #   }, ]

    def add_model(self):
        self.model_init_output()
        self._add_param()
        self._add_var()
        self._add_constrait()
            # print("\"{}\" add {} \"{}\" with caption \"{}\"".format(self.name_id, self.sequence_output_list[i]["type"], self.sequence_output_list[i]["name"], self.sequence_output_list[i]["caption"]))

    def model_init_output(self):
        pass

    def _add_param(self):
        pass

    def _add_var(self):
        pass

    def _add_constrait(self):
        pass

    def add_output(self):
        for i in range(len(self.sequence_output_list)):
            if self.sequence_output_list[i]["type"] == "param":
                # self.sequence_output_list[i]["caption"] = self.name_id + " " + self.sequence_output_list[i]["caption"]
                # self.sequence_output_list[i]["list"] = self._param_list_values(self.sequence_output_list[i]["name"])
                if isinstance(self, NE_Plant) and self.p_nom_extendable==True :
                    # 如果输出list为NE_Plant的出力，则需要:出力list * value(p_nom)
                    self.sequence_output_list[i]["caption"] = self.name_id + " " + self.sequence_output_list[i]["caption"]
                    t_list = self._param_list_values(self.sequence_output_list[i]["name"])
                    for x in range(len(t_list)):
                        t_list[x] = t_list[x] * self._var_value("p_nom")
                    self.sequence_output_list[i]["list"] = t_list
                else:
                    self.sequence_output_list[i]["caption"] = self.name_id + " " + self.sequence_output_list[i]["caption"]
                    self.sequence_output_list[i]["list"] = self._param_list_values(self.sequence_output_list[i]["name"])
            if self.sequence_output_list[i]["type"] == "var":
                self.sequence_output_list[i]["caption"] = self.name_id + " " + self.sequence_output_list[i]["caption"]
                self.sequence_output_list[i]["list"] = self._var_list_values(self.sequence_output_list[i]["name"])

    def _get_initial_cost_expr(self):
        return 0

    # 对象的Life Cycle Cost表达式
    def _add_objective_func_lcc(self):
        return 0

    # 对象的Life Cycle Net Profit表达式
    def _add_objective_func_lcnp(self):
        return 0

    # 对常量参数PARAM进行建模(在model中的名字前置了Node的name_id)
    def _to_param(self, in_attr_name, in_param, in_output=False, in_caption="", in_unit=""):
        if isinstance(in_param, list) or isinstance(in_param, np.ndarray):
            # var_list
            def param_list_func(model, i):
                return in_param[i - 1]  # pyomo的list是从1~N，python的list是从0~N-1，所以-1
            setattr(self.model, "PARAM_"+self.name_id+"_"+in_attr_name, Param(range(1, len(in_param) + 1), initialize=param_list_func))
            if in_output==True:
                t_output_list = {"caption":in_caption, "name":in_attr_name, "type": "param", "list":[]}
                self.sequence_output_list.append(t_output_list)
            else:
                pass
        else :
            # 单个var
            setattr(self.model, "PARAM_"+self.name_id+"_"+in_attr_name, Param(initialize=in_param))
            if in_output==True:
                self.var_output_list.append({"caption":self.name_id+" "+in_caption,"name":in_attr_name,"type":"param","unit":in_unit})

    # 对决策变量VAR进行建模(在model中的名字前置了Node的name_id)
    def _to_var(self, in_attr_name, in_len=0, in_output=False, in_caption="", in_unit=""):
        if in_len>0:
            setattr(self.model, "VAR_" + self.name_id + "_" + in_attr_name, Var(range(1, in_len + 1), domain=Reals, initialize=0.0))
            if in_output==True:
                t_output_list = {"caption":in_caption, "name":in_attr_name, "type": "var", "list":[]}
                self.sequence_output_list.append(t_output_list)
            else:
                pass
        else :
            setattr(self.model, "VAR_"+self.name_id+"_"+in_attr_name, Var(domain=Reals, initialize=0.0))
            if in_output==True:
                self.var_output_list.append({"caption":self.name_id+" "+in_caption,"name":in_attr_name,"type":"var","unit":in_unit})

    # 对var_list进行常数设置
    def _var_list_fix_num(self, in_attr_name, in_fix_num):
        t_var_list = self._var(in_attr_name)
        for i in range(1, len(t_var_list)+1):
            t_var_list[i].fix(in_fix_num)

    # 对约束方程进行建模
    def _to_cons(self, in_attr_name, in_func, in_len=0, in_print_sum=0, in_print=True):
        t_cons = 0
        if in_len>0:
            setattr(self.model, "CON_"+self.name_id+"_"+in_attr_name, Constraint(range(1, in_len + 1), rule=in_func))
            if in_print==True:
                self.print_cons(in_func([],1), in_print_sum)
        else:
            setattr(self.model, "CON_"+self.name_id+"_"+in_attr_name, Constraint(rule=in_func))
            if in_print==True:
                self.print_cons(in_func([]), in_print_sum)

    # print约束方程
    def print_cons(self, in_expr, in_print_sum=0):
        global g_print_cons
        if g_print_cons==True:
            if in_print_sum==0:
                print("约束({:<6s}): {}".format(self.name_id, in_expr))
            else:
                print("约束({:<6s}): {}".format(self.name_id, in_print_sum))

    # 获取node在model中param的expr
    def _param(self, in_attr_name, in_name_id=0):
        t_name_id = self.name_id
        if in_name_id!=0:
            t_name_id = in_name_id
        return getattr(self.model, "PARAM_"+t_name_id+"_"+in_attr_name)

    # 获取node在model中var的expr
    def _var(self, in_attr_name, in_name_id=0):
        t_name_id = self.name_id
        if in_name_id!=0:
            t_name_id = in_name_id
        return getattr(self.model, "VAR_"+t_name_id+"_"+in_attr_name)

    # 获取node在model中param的值
    def _param_value(self, in_attr_name, in_name_id=0):
        t_name_id = self.name_id
        if in_name_id!=0:
            t_name_id = in_name_id
        return value(getattr(self.model, "PARAM_"+t_name_id+"_"+in_attr_name))

    # 获取node在model中var的值
    def _var_value(self, in_attr_name, in_name_id=0):
        t_name_id = self.name_id
        if in_name_id!=0:
            t_name_id = in_name_id
        return value(getattr(self.model, "VAR_"+t_name_id+"_"+in_attr_name))

    # 获取param list的值
    def _param_list_values(self, in_attr_name):
        t_param_list = self._param(in_attr_name)
        t_list = []
        for i in range(len(t_param_list)):
            t_list.append(value(t_param_list[i+1]))
        return t_list

    # 获取var list的值
    def _var_list_values(self, in_attr_name):
        t_var_list = self._var(in_attr_name)
        t_list = []
        for i in range(len(t_var_list)):
            t_list.append(value(t_var_list[i+1]))
        return t_list

# =============================Component类=============================
# 只含一个p_list的基础组件类：包括Load、Plant等
class Component_Base(Object_Base):
    # bus的总数量
    bus_num  = 1    # 节点的静态总数量，缺省为1，即节点0
    def __init__(self, in_sys, in_name_id, in_constraint_sign=1, in_constraint_effi=1.0, in_p_nom=0, in_max_pu=1.0, in_min_pu=-1.0, in_p_nom_extendable=True, in_bus_id=-1, in_e_output=True):
        self.model = in_sys.model
        Object_Base.__init__(self, in_sys, in_name_id, in_model=self.model)
        in_sys.component_list.append(self)

        # 是否输出最优p_list对应的电量
        self.e_output = in_e_output

        # 改版后======================================
        self.effi =         {"value":1.00, "name":"效率"}  #若输入的边际成本为单位最终发电量的成本而不是单位输入燃料（当量热值）的成本，则其效率直接为100%

        self.p_max_pu = {"value":in_max_pu, "name":"最大出力标幺值"}
        self.p_min_pu = {"value":in_min_pu, "name":"最小出力标幺值"}

        self.p_nom_max =        {"value":float('inf'), "name":"最大技术装机(kW)"}
        self.p_nom_min =        {"value":-float('inf'), "name":"最小技术装机(kW)"}

        self.p_nom_extendable = in_p_nom_extendable
        self.p_nom =        {"value":in_p_nom, "name":"固定额定装机(kW)"}      # 当p_nom_extendable为False时，p_nom将被fix为固定额定容量

        # 单位综合造价，煤电：4.0元/W，     天然气电站：3.0元/W，   水电：10元/W，   核电：12元/W
        self.capital_cost = {"value":0.0, "name":"功率单位造价(元/W)"}
        # 边际发电成本，煤电：0.2元/kWh，   天然气电站：0.3元/kWh， 水电：0元/kWh，  核电：0.06元/kWh
        self.marginal_cost ={"value":0.0, "name":"边际发电成本(元/kWh)"}

        self.constraint_sign = in_constraint_sign    # 用于控制约束的符号
        self.constraint_effi = in_constraint_effi    # 用于控制约束的效率

        # self.cnp_sign = -in_constraint_sign   #用于cost、netprofit的符号

        self.use_price_list = False #输出时用的分类，采用price_list还是采用marginal_cost
        # 改版后======================================

        # 输出成本/收益用的价格
        # price_output[0]为标志， 0表示后面放一个数据, -777表示需要取得price_list中对应的值, -888表示包含储能的charge和discharge的mc)
        # price_output[1]和price_output[2]为数据
        # self.price_output = [0,-999,-999]

        if in_bus_id==-1:
            self.bus_id =  self._sys.Current_Bus_ID()   # 所属的节点ID
            self._sys.Current_Bus_Add_Component(self)         # 在bus_id对应的节点中，增加本对象
        else:
            self.bus_id = in_bus_id
            self._sys.Bus_Add_Component(self, in_bus_id)

    # 节点编号，只有Add_Bus才可以增加
    @staticmethod
    def Add_Bus():
        Component_Base.bus_num = Component_Base.bus_num + 1

        # 时序数据输出用的多个list
        # [ {   "caption":"xxx1",
        #       "name":"price_list",
        #       "type":"param",
        #       "list":list1
        #   },
        #   {
        #       "caption":"xxx2",
        #       "name":"p_list",
        #       "type":"var",
        #       "list":list2
        #   }, ]

    def model_init_output(self):
        pass

    def _add_param(self):
        # 参数：系统充电效率
        self._to_param("effi", self.effi["value"])

        # 参数：功率单位造价(元/W)
        self._to_param("capital_cost", self.capital_cost["value"])

        # 参数：容量单位造价(元/Wh)
        self._to_param("marginal_cost", self.marginal_cost["value"])

        self._to_param("p_max_pu", self.p_max_pu["value"])   #最大出力标幺值
        self._to_param("p_min_pu", self.p_min_pu["value"])   #最大出力标幺值

    def _add_var(self):
        # 变量：最优额定功率（kW）
        self._to_var("p_nom",in_output=True, in_caption="p_nom", in_unit="kW")
        # 当p_nom_extendable为False时，p_nom将被fix为固定额定容量
        if self.p_nom_extendable==False:
            self._var("p_nom").fix(self.p_nom["value"])

        print("----------------{} p_nom extendable is {}, value is: {}".format(self.name_id,self.p_nom_extendable, self.p_nom["value"]))

        # 变量：最优出力序列(kW)
        self._to_var("p_list", in_len=self._sys.simu_hours + 1, in_output=True, in_caption="p")  #这里+1是为了防止constraints的index构造时溢出

    def _add_constrait(self):     # in_effi，看是否需要传入effi，如储能中discharge需要。
        # --------------------------------------------额定值约束----------------------------------------------
        # 约束1(N*2组)：p_nom_opt*p_min_pu <= p[i] <= p_nom_opt*p_max_pu*effi （额定功率）
        if self.constraint_sign==1:
            def func1(model, i):
                expr = self._var("p_list")[i] <= self._var("p_nom") * self.p_max_pu["value"] * self.constraint_effi     # self.constraint_effi目前仅用于Energy_Store的discharge（即用一个注入节点模拟一条支路）中，用于限制discharge扣除损耗后的最大出功率。
                return expr
            self._to_cons("p_cons_list1", func1, in_len=self._sys.simu_hours)

            def func2(model, i):
                expr = self._var("p_list")[i] >= self._var("p_nom") * self.p_min_pu["value"]
                return expr
            self._to_cons("p_cons_list2", func2, in_len=self._sys.simu_hours)

            if self.p_nom_extendable==True:
                def func3(model):
                    expr = self._var("p_nom") >= self.p_nom["value"]
                    return expr
                self._to_cons("p_nom_cons", func3)

            def func4(model):
                expr = self._var("p_nom") <= self.p_nom_max["value"]
                return expr
            self._to_cons("p_nom_max_cons", func4)

            def func5(model):
                expr = self._var("p_nom") >= self.p_nom_min["value"]
                return expr
            self._to_cons("p_nom_min_cons", func5)

        # 约束1(N*2组)：-effi*p_nom_opt*p_max_pu <= p[i] <= -p_nom_opt*p_min_pu （额定功率）
        if self.constraint_sign==-1:
            def func1(model, i):
                expr = self._var("p_list")[i] >= -self._var("p_nom") * self.p_max_pu["value"] * self.constraint_effi     # self.constraint_effi目前仅用于Energy_Store的discharge（即用一个注入节点模拟一条支路）中，用于限制discharge扣除损耗后的最大出功率。
                return expr
            self._to_cons("p_cons_list1", func1, in_len=self._sys.simu_hours)

            def func2(model, i):
                expr = self._var("p_list")[i] <= -self._var("p_nom") * self.p_min_pu["value"]
                return expr
            self._to_cons("p_cons_list2", func2, in_len=self._sys.simu_hours)

            if self.p_nom_extendable == True:
                def func3(model):
                    expr = self._var("p_nom") >= self.p_nom["value"]
                    return expr
                self._to_cons("p_nom_cons", func3)

            def func4(model):
                expr = self._var("p_nom") <= self.p_nom_max["value"]
                return expr
            self._to_cons("p_nom_max_cons", func4)

            def func5(model):
                expr = self._var("p_nom") >= self.p_nom_min["value"]
                return expr
            self._to_cons("p_nom_min_cons", func5)

    def _get_initial_cost_expr(self):
        # 初期造价
        t_expr = 0
        if self.p_nom_extendable==True:
            # 若p_nom可以扩展，则考虑增量的投资成本
            t_expr = 1000*self._param("capital_cost")*(self._var("p_nom")-self.p_nom["value"])
        else:
            t_expr = 0

        return t_expr

    # 对象的Life Cycle Cost表达式
    def _add_objective_func_lcc(self):
        print("目标函数增加：{}的LCC成本".format(self.name_id))
        t_lcc_expr = 0

        # 初期造价
        t_lcc_expr = self._get_initial_cost_expr()
        print("目标函数增加：{}的LCC成本【cost调用成功】:{}".format(self.name_id, t_lcc_expr))

        # 运行成本
        # 2022-05-17：存量如混合抽蓄，p_nom_extendable为False，此时marginal_cost仍然应该起作用，因此无论p_nom_extendable为何值，除Load外，都要计算边际成本
        if not isinstance(self, Load):
        # if self.p_nom_extendable==True:
            # 若p_nom可以扩展，则考虑运营成本
            t_lcc_expr = t_lcc_expr + sum(npv(
                self._var("p_list")[i] * self._param("marginal_cost"),
                # self.cnp_sign * self._var("p_list")[i] * self._param("marginal_cost"),
                self._sys.rate,
                i - 1,
                self._sys.spring_festival.Year_Days()
            ) for i in range(1, self._sys.simu_hours + 1))
        else:
            t_lcc_expr = t_lcc_expr + 0

        print("目标函数增加：{}的LCC成本【函数运行成功】")
        # print("目标函数增加：{}的LCC成本【函数运行成功】:{}".format(self.name_id, t_lcc_expr))
        print("-----------------------------------")
        return t_lcc_expr

    # 对象的Life Cycle Net Profit表达式
    def _add_objective_func_lcnp(self):
        print("目标函数增加：{}的LCNP即成本-收益".format(self.name_id))
        t_lcnp_expr = 0

        # 初期造价
        t_lcnp_expr = self._get_initial_cost_expr()

        # 运行成本
        if self.p_nom_extendable==True:
            t_lcnp_expr = t_lcnp_expr + sum(npv(
                self._var("p_list")[i] * (self._param("marginal_cost")-self._sys._param("price_list")[i]),
                # self.cnp_sign * self._var("p_list")[i] * self._sys._param("price_list")[i],
                self._sys.rate,
                i - 1,
                self._sys.spring_festival.Year_Days()
            ) for i in range(1, self._sys.simu_hours + 1))
        else:
            t_lcnp_expr = t_lcnp_expr + 0

        return t_lcnp_expr

    def get_optimized_kWh_and_hours(self):
        t_sum = 0
        t_hours = 0

        if isinstance(self, Undispatchable_Component):
            # param化的p_list电量统计
            if isinstance(self, NE_Plant):
                # 新能源p_list电量统计
                if self.p_nom_extendable == True:
                    t_list = self._param_list_values(in_attr_name="p_list")
                    t_sum = sum(t_list) * self._var_value("p_nom")
                    # t_sum = sum(t_list) * self.p_nom["value"]
                    t_max = max(self._var_value("p_nom"), max(max(t_list), -min(t_list)))
                    # t_max = max(self.p_nom["value"], max(max(t_list), -min(t_list)))
                else:
                    t_list = self._param_list_values(in_attr_name="p_list")
                    t_sum = sum(t_list)
                    t_max = self.p_nom["value"]
                    # t_max = self.p_nom["value"]
            else:
                # load等的p_list电量统计
                t_list = self._param_list_values(in_attr_name="p_list")
                t_sum = sum(t_list)
                # t_max = value(o._var("p_nom"))
                t_max = self.p_nom["value"]
        else:
            # var的p_list电量统计
            t_list = self._var_list_values(in_attr_name="p_list")
            t_sum = sum(t_list)
            if hasattr(self, "p_nom"):
                t_max = self._var_value("p_nom")
                # t_max = self.p_nom["value"]
            else:
                t_max = max(max(t_list), -min(t_list))

        t_hours = t_sum / t_max if t_max != 0 else 0
        return t_sum, t_hours

    # 计算obj的生命周期运行成本
    def get_cnp_cost(self):
        kwh = self.get_optimized_kWh_and_hours()[0]
        cnp_cost = 0.0
        if (not isinstance(self, Load)) and (not isinstance(self, Undispatchable_Component)):
            # if isinstance(o, Slack_Node) or o.p_nom_extendable==True:
            if self._sys.investor == "government":
                cnp_cost = -self.marginal_cost["value"] * kwh
                cnp_cost = cnp_cost / 10000.0  # 输出万元
            if self._sys.investor == "user_finance":
                if isinstance(self, Slack_Node):
                    cnp_cost = -sum(np.array(self._var_list_values(in_attr_name="p_list")) * self.marginal_cost["value"])
                else:
                    # (边际成本-price)[k]和p[k}点积
                    cnp_cost = -list_sumproduct(
                        self._var_list_values(in_attr_name="p_list"),
                        np.array([self.marginal_cost["value"]] * len(self._sys._param_list_values(in_attr_name="price_list"))) - np.array(self._sys._param_list_values(in_attr_name="price_list")) )
                    # (边际成本-price)[k]和p[k}点积
                    # cnp_cost = -list_sumproduct(
                    #     self._var_list_values(in_attr_name="p_list"),
                    #     np.array([self.marginal_cost["value"]] * len(
                    #         self._param_list_values(in_attr_name="price_list"))) - np.array(
                    #         self._param_list_values(in_attr_name="price_list"))
                    # )
                cnp_cost = cnp_cost / 10000.0  # 输出万元
        else:
            cnp_cost = 0.0

        return cnp_cost

# 松弛节点，主要用途：允许电量交换、新能源弃能
class Slack_Node(Component_Base):
    def __init__(self, in_sys, in_name_id, in_p_nom_extendable=False):
        Component_Base.__init__(self, in_sys, in_name_id)

        # 边际发电成本，煤电：0.2元/kWh，   天然气电站：0.3元/kWh， 水电：0元/kWh，  核电：0.06元/kWh
        self.marginal_cost ={"value":0.5, "name":"边际发电成本(元/kWh)"}

        # self.p_max = {"value":float("inf"), "name":"最大注入功率(kW)"}
        # self.p_min = {"value":-float("inf"), "name":"最大吸收功率(kW)"}
        # p_max和p_min改为以下：
        self.p_nom =        {"value":float("inf"), "name":"最大功率(kW)"}
        self.p_nom_extendable = in_p_nom_extendable
        self.p_max_pu = {"value":1.0, "name":"最大出力标幺值"}
        self.p_min_pu = {"value":0.0, "name":"最小出力标幺值"}

        self.e_max = {"value":float("inf"), "name":"最大注入电量(kWh)"}
        self.e_min = {"value":-float("inf"), "name":"最大吸收电量(kWh)"}

    def _get_initial_cost_expr(self):
        # 初期造价(Slack节点，视作有足够的存量容量，不需要额外投资）
        # ===如果需要考虑增容成本，可以考虑用plant及其kw成本和mc成本，来模拟变电容量===
        return 0

    # Life Cycle Cost的表达式
    def _add_objective_func_lcc(self):
        print("目标函数增加：{}的LCC成本".format(self.name_id))

        # 初期造价
        t_lcc_expr = self._get_initial_cost_expr()

        # # 运行成本(暂考虑全社会成本为：注入电量*影子电价，即为：p * 1 * mc_charge（若p为吸收功率，则成本没有市场意义，通过定义只吸收功率的slack2将marginal_cost定为0来解决）
        t_lcc_expr = t_lcc_expr + sum(npv(
            self._var("p_list")[i]* self._param("marginal_cost"),
            self._sys.rate,
            i - 1,
            self._sys.spring_festival.Year_Days()
        ) for i in range(1, self._sys.simu_hours + 1))

        # self.price_output[0] = 0
        # self.price_output[1] = self._param("marginal_cost")
        return t_lcc_expr

    # Life Cycle Net Profit的表达式
    # slack节点，不管是注入还是吸收功率，因为都是和外部的交换，因此全社会成本lcc和财务成本lcnp一致。
    def _add_objective_func_lcnp(self):
        print("目标函数增加：{}的LCNP即成本-收益".format(self.name_id))

        # 初期造价
        t_lcnp_expr = self._get_initial_cost_expr()

        # # 运行成本(暂考虑全社会成本为：注入电量*影子电价，即为：p * 1 * mc_charge（若p为吸收功率，则成本没有市场意义，通过定义只吸收功率的slack2将marginal_cost定为0来解决）
        t_lcnp_expr = t_lcnp_expr + sum(npv(
            self._var("p_list")[i]* self._param("marginal_cost"),
            self._sys.rate,
            i - 1,
            self._sys.spring_festival.Year_Days()
        ) for i in range(1, self._sys.simu_hours + 1))

        # self.price_output[0] = 0
        # self.price_output[1] = self._param("marginal_cost")
        return t_lcnp_expr

    def _add_param(self):
        Component_Base._add_param(self)
        # 参数：
        # self._to_param("p_max", self.p_max["value"])
        # self._to_param("p_min", self.p_min["value"])
        self._to_param("e_max", self.e_max["value"])
        self._to_param("e_min", self.e_min["value"])

    def _add_var(self):
        Component_Base._add_var(self)
        # 变量：最优联络功率序列(kW)
        # self._to_var("p_list", in_len=self._sys.simu_hours + 1, in_output=True, in_caption="p", in_unit="kW")  #这里+1是为了防止constraints的index构造时溢出

    def _add_constrait(self):
        # p_min <= p[i] <= p_max
        def func1(model, i):
            if self.constraint_sign == -1:
                expr = self._var("p_list")[i] >= -self._var("p_nom") * self._param("p_max_pu")
            else:
                expr = self._var("p_list")[i] <= self._var("p_nom") * self._param("p_max_pu")
            return expr
        self._to_cons("p_cons_list1", func1, in_len=self._sys.simu_hours)

        def func2(model, i):
            if self.constraint_sign == -1:
                expr = self._var("p_list")[i] <= -self._var("p_nom") * self._param("p_min_pu")
            else:
                expr = self._var("p_list")[i] >= self._var("p_nom") * self._param("p_min_pu")
            return expr
        self._to_cons("p_cons_list2", func2, in_len=self._sys.simu_hours)

        # sum(p[i]) <= e_max
        def func3(model):
            expr = sum(self._var("p_list")[i] for i in range(1, self._sys.simu_hours+1)) <= self._param("e_max")
            return expr
        # print_con(func3([]))
        self._to_cons("e_cons1", func3, in_print_sum="sum(p_list[i]) <= e_max")

        # sum(p[i]) >= e_min
        def func4(model):
            expr = sum(self._var("p_list")[i] for i in range(1, self._sys.simu_hours+1)) >= self._param("e_min")
            return expr
        # print_con(func4([]))
        self._to_cons("e_cons2", func4, in_print_sum="sum(p_list[i]) >= e_min")

# 仅注入的slack节点
class Injection_Slack_Node(Slack_Node):
    def __init__(self, in_sys, in_name_id, in_p_max, in_e_max, in_p_nom_extendable=False, in_marginal_cost=0.0):
    # def __init__(self, in_sys, in_name_id, in_p_max, in_e_max, in_p_nom_extendable=False, in_marginal_cost=0.65):
        Slack_Node.__init__(self, in_sys, in_name_id,  in_p_nom_extendable=in_p_nom_extendable )

        self.p_nom =        {"value":in_p_max, "name":"最大功率(kW)"}
        self.e_max["value"]=in_e_max
        self.e_min["value"]=0

        self.capital_cost = {"value":5.0, "name":"输变电容量的功率单位造价(元/W)"}    # 如新建全户内GIS110kV变电站的综合造价为400万元/MVA，考虑其他因素，这里考虑10kV层面的增容成本为5元/W
        self.marginal_cost["value"]=in_marginal_cost

# 仅吸收的slack节点
class Absorption_Slack_Node(Slack_Node):
    def __init__(self, in_sys, in_name_id, in_p_max, in_e_max, in_p_nom_extendable=False, in_marginal_cost=0.0):
    # def __init__(self, in_sys, in_name_id, in_p_max, in_e_max, in_p_nom_extendable=False, in_marginal_cost=0.45):
        Slack_Node.__init__(self, in_sys, in_name_id, in_p_nom_extendable=in_p_nom_extendable )

        self.p_nom =        {"value":in_p_max, "name":"最大功率(kW)"}
        self.constraint_sign = -1   # 使component_base添加约束时，为p_list[i] >= -p_nom

        self.e_max["value"] = 0
        self.e_min["value"] = -in_e_max

        self.capital_cost = {"value":0.0, "name":"输变电容量的功率单位造价(元/W)"}    # 吸收功率暂不考虑增容成本
        self.marginal_cost["value"] = in_marginal_cost

# 不可调度类：包括Load、新能源等
class Undispatchable_Component(Component_Base):
    def __init__(self, in_sys, in_name_id, in_negative=False):
        Component_Base.__init__(self, in_sys, in_name_id)

        # p时间序列(kW)
        self.one_year_p_list = [0]

        # 如果negative==True，则p_list全改为负值
        self.negative = in_negative

    def set_one_year_p(self, in_list=0, in_is_pu=True):
        in_list = copy.copy(in_list)

        # 如果输入load列表为空，则为常量负荷，即负荷为一条p_nom的直线
        if in_list==0 :
            self.one_year_p_list = [self.p_nom["value"]] * 8760
        else :
            # 如果是NE_plant且p_nom_extendable==True，则输入出力必须为标幺值
            if in_is_pu==False and not (isinstance(self, NE_Plant) and self.p_nom_extendable==True) :
                self.one_year_p_list = in_list
            else:
            # 一般情况，需要对数据进行标幺化出力，然后优化p_nom时只取标幺值，不优化p_nom时将in_list和p_nom点积
                self.one_year_p_list = in_list
                t_max = max(max(in_list), -min(in_list))
                for i in range(len(in_list)):
                    if self.p_nom_extendable==True:
                        # 对p_nom进行优化，则p_list必须为标幺值
                        self.one_year_p_list[i]=self.one_year_p_list[i] / t_max if t_max!=0 else 0
                    else:
                        # 不对p_nom进行优化，则p_list必须*p_nom，且为固定值
                        self.one_year_p_list[i]=self.one_year_p_list[i] / t_max * self.p_nom["value"]  if t_max!=0 else 0

        # print_list(self.one_year_p_list, 24)
        # 如果negative==True，则p_list全改符号
        if self.negative==True:
            self.one_year_p_list = list(np.array(self.one_year_p_list) * (-1))

    # 负荷去除春节负荷
    def p_list_cut_spring_festival_simu(self):
        t_start_day = self._sys.spring_festival.start_day
        t_stop_day = self._sys.spring_festival.stop_day

        if self._sys.spring_festival.bypass==True:
            if self._sys.spring_festival.simu_years >= 1:
                t_list = []
                for i in range(len(self.one_year_p_list)):
                    if i<t_start_day*24 or i>t_stop_day*24:
                        t_list.append(self.one_year_p_list[i])
                self.one_year_p_list = t_list
    def _add_param(self):
        # 负荷去除春节负荷
        self.p_list_cut_spring_festival_simu()
        # 将一年的负荷重复为多年负荷
        t_simu_p_list = list_convolution(self.one_year_p_list, self._sys.simu_hours)

        # 参数：负荷序列（kW）
        self._to_param("p_list", t_simu_p_list, in_output=True, in_caption="p")

        # print_list(self.one_year_p_list, 12)
        print("增加负荷曲线成功1===================")
        # print_list(t_simu_p_list, 12)

class Load(Undispatchable_Component):
    def __init__(self, in_sys, in_name_id, in_p_nom=0.0, in_negative=True):
        Undispatchable_Component.__init__(self, in_sys, in_name_id, in_negative=in_negative)

        # 负荷时间序列(kW)
        self.one_year_p_list = [0]

        self.p_nom_extendable = False

        # 这行不能去掉，否则会被component_base中的p_nom的0覆盖掉
        self.p_nom = {"value":in_p_nom, "name":"最大负荷(kW)"}

        self.capital_cost["value"] = 0

        # 最大允许负荷（kW）（应大于等于max(load_list)，主要用于限制储能出力、限制倒送电水平）
        # self.load_nom = float('inf')

    def _add_param(self):
        Undispatchable_Component._add_param(self)

        # 参数：p_nom（kW，最大负荷）
        self._to_param("p_nom", self.p_nom["value"])
        print("增加负荷曲线成功2===================")

    def _add_var(self):
        pass

    def _add_constrait(self):
        pass

    def model_init_output(self):
        print("# -----------------------负荷参数---------------------------")
        print("最大负荷为：{:.1f}kW".format(-min(self.one_year_p_list)))
        print("最小负荷为：{:.1f}kW".format(-max(self.one_year_p_list)))
        print("负荷利用小时数为：{:.1f}h".format(-sum(self.one_year_p_list) / -min(self.one_year_p_list) if -min(self.one_year_p_list)!=0 else 0))
        # print("负荷所在主变最大允许功率为：",self.load_nom, "kW（不允许倒送）")

    def load_list_print(self):
        print("# =======================负荷序列===========================")
        print_list(self.one_year_p_list, 24, in_float_dot_num=1, in_num=7)
        print("# ==========================================================\n")

    def elec_price_list_print(self):
        print("# =======================目录电价===========================")
        print_list(self.tariff_list, 6, in_float_dot_num=4, in_num=6)
        print("# ==========================================================\n")

class NE_Plant(Undispatchable_Component):
    def __init__(self, in_sys, in_name_id, in_p_nom=0.0, in_p_nom_max=float('inf'), in_p_nom_extendable=True):
        Undispatchable_Component.__init__(self, in_sys, in_name_id)

        self.p_nom_extendable = in_p_nom_extendable
        self.p_nom =        {"value":in_p_nom, "name":"固定额定装机(kW)"}      # 当p_nom_extendable为False时，p_nom将被fix为固定额定容量
        self.p_nom_max =    {"value":in_p_nom_max, "name":"技术额定装机(kW)"}  # p_nom的最大技术装机容量

        # 单位综合造价，煤电：4.0元/W，     天然气电站：3.0元/W，   水电：10元/W，   核电：12元/W
        self.capital_cost = {"value":5.0, "name":"功率单位造价(元/W)"}
        # 边际发电成本，煤电：0.2元/kWh，   天然气电站：0.3元/kWh， 水电：0元/kWh，  核电：0.06元/kWh
        self.marginal_cost ={"value":0.0, "name":"边际发电成本(元/kWh)"}

    # Life Cycle Cost的表达式
    def _add_objective_func_lcc(self):
        print("目标函数增加：{}的LCC成本".format(self.name_id))

        # 初期造价
        t_lcc_expr = self._get_initial_cost_expr()
        # t_lcc_expr = 0
        # if self.p_nom_extendable==True:
        #     # 若p_nom可以扩展，则投资仅计及基于输入p_nom的增量，且约束中var_p_nom>=p_nom
        #     t_lcc_expr = 1000*self._param("capital_cost")*(self._var("p_nom")-self.p_nom["value"])
        # else:
        #     t_lcc_expr = 0

        # 运行成本为0
        t_lcc_expr = t_lcc_expr + 0

        # self.price_output[0] = 0
        # self.price_output[1] = 0
        return t_lcc_expr

    # Life Cycle Net Profit的表达式
    def _add_objective_func_lcnp(self):
        print("目标函数增加：{}的LCNP即成本-收益".format(self.name_id))

        # 初期造价
        t_lcnp_expr = self._get_initial_cost_expr()
        # t_lcnp_expr = 0
        # if self.p_nom_extendable==True:
        #     # 若p_nom可以扩展，则投资仅计及基于输入p_nom的增量，且约束中var_p_nom>=p_nom
        #     t_lcnp_expr = 1000*self._param("capital_cost")*(self._var("p_nom")-self.p_nom["value"])
        # else:
        #     t_lcnp_expr = 0

        # 运行收益和成本( 暂考虑投资方的成本-收益为：-发电收益，即：-p[i] * price[i] * 优惠率 )
        # 当新能源的p_nom优化时，仅考虑增量资产的发电收益。另外，p[i]为标幺值p_list[i] * 优化变量p_nom
        if self.p_nom_extendable == True:
            t_lcnp_expr = t_lcnp_expr + sum(npv(
                -(self._var("p_nom")-self.p_nom["value"]) * self._param("p_list")[i] * self._sys._param("price_list")[i] * (1-self._sys.investor_user_discount),
                self._sys.rate,
                i - 1,
                self._sys.spring_festival.Year_Days()
            ) for i in range(1, self._sys.simu_hours + 1))
        # 当新能源的p_nom不优化时，即为存量资产，不考虑收益
        else:
            t_lcnp_expr = t_lcnp_expr + 0

        # self.price_output[0] = -777 # 需要获取price_list中的值
        return t_lcnp_expr

    def _add_param(self):
        Undispatchable_Component._add_param(self)

        # 参数：功率单位造价(元/W)
        self._to_param("capital_cost", self.capital_cost["value"])

        # 参数：容量单位造价(元/Wh)
        self._to_param("marginal_cost", self.marginal_cost["value"])

    def _add_var(self):
        # 变量：最优额定功率（kW）
        self._to_var("p_nom",in_output=True, in_caption="p_nom", in_unit="kW")
        # 当p_nom_extendable为False时，p_nom将被fix为固定额定容量
        if self.p_nom_extendable==False:
            self._var("p_nom").fix(self.p_nom["value"])

    def _add_constrait(self):
        def func1(model):
            expr = self._var("p_nom") >= self.p_nom["value"]
            # expr = self._var("p_nom") >= 0
            return expr
        self._to_cons("p_nom_cons", func1)

        # if self.p_nom_max["value"]!=0:
        def func2(model):
            expr = self._var("p_nom") <= self.p_nom_max["value"]
            return expr
        self._to_cons("p_nom_max_cons", func2)

# 一次能源供应（如天然气、氢能等燃料）
class Primary_Energy_Supply(Component_Base):
    def __init__(self, in_sys, in_name_id, in_marginal_cost=0.0):
        Component_Base.__init__(self, in_sys, in_name_id, in_p_nom=0.0, in_p_nom_extendable=True)

        # 燃料成本，煤：??元/kWh，   天然气：??元/kWh， 氢：??元/kWh
        self.marginal_cost ={"value":in_marginal_cost, "name":"燃料成本(元/kWh)"}

    def _add_param(self):
        Component_Base._add_param(self)

    def _add_var(self):
        Component_Base._add_var(self)

    def _add_constrait(self):
        Component_Base._add_constrait(self)

    def _get_initial_cost_expr(self):
        return Component_Base._get_initial_cost_expr(self)

    def _add_objective_func_lcc(self):
        return Component_Base._add_objective_func_lcc(self)

    def _add_objective_func_lcnp(self):
        return Component_Base._add_objective_func_lcnp(self)

    def model_init_output(self):
        print("# =======================一次能源的参数打印===========================")
        print("燃料成本为：{}({})".format(self.marginal_cost["value"], "元/W"))

class Plant(Component_Base):
    def __init__(self, in_sys, in_name_id, in_p_nom=0.0, in_p_nom_extendable=True, in_max_pu=1.0, in_min_pu=0.0):
        Component_Base.__init__(self, in_sys, in_name_id, in_p_nom=in_p_nom, in_p_nom_extendable=in_p_nom_extendable, in_max_pu=in_max_pu, in_min_pu=in_min_pu)

        self.effi =         {"value":1.00, "name":"发电效率"}  #若输入的边际成本为单位最终发电量的成本而不是单位输入燃料（当量热值）的成本，则其效率直接为100%

        self.p_max_pu = {"value":in_max_pu, "name":"最大出力标幺值"}
        self.p_min_pu = {"value":in_min_pu, "name":"最小出力标幺值"}

        self.p_nom_extendable = in_p_nom_extendable
        self.p_nom =        {"value":in_p_nom, "name":"固定额定装机(kW)"}      # 当p_nom_extendable为False时，p_nom将被fix为固定额定容量
        # self.p_nom_max =    {"value":9998.0, "name":"最大额定装机(kW)"}   # 即技术装机，"value":float('inf')
        # self.p_nom_min =    {"value":-9998.0, "name":"最小额定装机(kW)"}  # 即技术装机，"value":-float('inf')

        # 单位综合造价，煤电：4.0元/W，     天然气电站：3.0元/W，   水电：10元/W，   核电：12元/W
        self.capital_cost = {"value":3.0, "name":"功率单位造价(元/W)"}
        # 边际发电成本，煤电：0.2元/kWh，   天然气电站：0.3元/kWh， 水电：0元/kWh，  核电：0.06元/kWh
        self.marginal_cost ={"value":0.3, "name":"边际发电成本(元/kWh)"}

    def _add_param(self):
        Component_Base._add_param(self)

    def _add_var(self):
        Component_Base._add_var(self)

    def _add_constrait(self):
        Component_Base._add_constrait(self)

    def _get_initial_cost_expr(self):
        return Component_Base._get_initial_cost_expr(self)

    def _add_objective_func_lcc(self):
        return Component_Base._add_objective_func_lcc(self)

    def _add_objective_func_lcnp(self):
        return Component_Base._add_objective_func_lcnp(self)

    def model_init_output(self):
        print("# =======================电站参数打印===========================")
        print("电站的发电效率为：{}".format(self.effi["value"]))
        print("电站的单位造价为：{}({})".format(self.capital_cost["value"], "元/W"))
        print("电站的边际发电成本为：{}({})".format(self.marginal_cost["value"], "元/W"))
        print("电站的最大出力pu为：{}".format(self.p_max_pu["value"]))
        print("电站的最小出力pu为：{}".format(self.p_min_pu["value"]))

        if self.p_nom_extendable==False:
            print("电站的固定额定容量为：{}({})".format(self.p_nom["value"], "kW"))

class Hydro_Plant(Plant):
    def __init__(self, in_sys, in_name_id, in_hours_nom=2000, in_p_nom=0.0, in_p_nom_extendable=True):
        Plant.__init__(self, in_sys, in_name_id, in_p_nom=in_p_nom, in_p_nom_extendable=in_p_nom_extendable)

        # 年最大发电小时数
        self.hours_nom = in_hours_nom
        self.simu_years = in_sys.original_simu_years

        # 年最大发电量(kWh)
        # self.e_nom = {"value":in_hours_nom * in_p_nom * self.simu_years, "name":"全周期最大发电量(kWh)"}

    def _add_param(self):
        Plant._add_param(self)

        # 参数：年最大发电量(kWh)
        # self._to_param("e_nom", self.e_nom["value"])

    def _add_constrait(self):
        Plant._add_constrait(self)

        def func1(model):
            # 水电的总发电量 <= p_nom * 年最大发电小时数 * 年数
            expr = sum(self._var("p_list")[i] for i in range(1, self._sys.simu_hours+1)) <= self._var("p_nom") * self.hours_nom * self.simu_years
            return expr
        self._to_cons("e_cons_list", func1, in_print_sum="sum(p_list[i]) <= e_nom")

    def _get_initial_cost_expr(self):
        return Plant._get_initial_cost_expr(self)

    def _add_objective_func_lcc(self):
        return Plant._add_objective_func_lcc(self)

    def _add_objective_func_lcnp(self):
        return Plant._add_objective_func_lcnp(self)

# =============================Container类=============================
# 特殊的component，属于容器：包括Bus、Link等
class Container_Base(Object_Base):
    def __init__(self, in_name_id, in_sys, in_model):
        Object_Base.__init__(self, in_sys, in_name_id, in_model=in_model)
        self.model = in_model

        # 2022-06-28：外部调用中in_name_id可能为数值，后续会报错，因此要转为string
        self.name_id = str(in_name_id)

        if in_sys!=0:
            in_sys.container_list.append(self)

# Bus，存放component的容器
class Bus(Container_Base):
    bus_num = 0
    def __init__(self, in_sys):
        Container_Base.__init__(self, in_name_id="bus"+str(Bus.bus_num), in_model=in_sys.model, in_sys=in_sys)

        self._sys = in_sys
        self.bus_id = Bus.bus_num
        Bus.bus_num = Bus.bus_num + 1

        self.component_list = []

    def Add_Component(self, in_com):
        self.component_list.append(in_com)

# 电力系统节点
class Elec_Bus(Bus):
    def __init__(self, in_sys, in_if_reference_bus=False):
        Bus.__init__(self, in_sys)

        self.reference_bus = in_if_reference_bus
        self.power_angle = 0    # 电力系统功角（采用直流潮流，p_ij=(delta_i-delta_j）/x_ij）

    def model_init_output(self):
        pass

    def _add_param(self):
        pass

    def _add_var(self):
        # 变量：电力系统功角
        self._to_var("power_angle", in_len=self._sys.simu_hours + 1, in_output=True, in_caption="delta", in_unit="rad")
        # 当reference_bus为True时，power_angle将被fix为0
        if self.reference_bus==True:
            self._var_list_fix_num("power_angle", 0.0)

    def _add_constrait(self):
        pass

# 无损双向Link，存放2个component的容器
class Link_Base(Container_Base):
    def __init__(self, in_sys, in_bus0_id, in_bus1_id, in_name, in_capital_cost=0.0, in_p_nom=0, in_p_nom_extendable=False):
        self.name_id = in_name+"["+str(in_bus0_id)+"->"+str(in_bus1_id)+"]"
        Container_Base.__init__(self, in_name_id=self.name_id, in_sys=in_sys, in_model=in_sys.model)
        self._sys = in_sys  #系统信息。前缀"_"的为protected成员，前缀"__"的为private成员

        self.p_nom = {"value":in_p_nom, "name":"设定的额定功率(kW)"}
        self.p_nom_extendable = in_p_nom_extendable

        self.capital_cost = {"value":in_capital_cost, "name":"功率单位造价(元/W)"}

        # 从com0流向com1
        # com0为负值，constraint_sign=-1
        # self.com0 = Component_Base(in_sys, in_name + "_com0", in_bus_id=in_bus0_id, in_constraint_sign=-1)

        # com0
        self.com0 = Component_Base(in_sys, in_name + "_com0", in_bus_id=in_bus0_id)
        self.com0.p_nom["value"] = self.p_nom["value"]
        self.com0.capital_cost["value"] = self.capital_cost["value"]    # 造价全部分配在bus0

        # com1
        self.com1 = Component_Base(in_sys, in_name + "_com1", in_bus_id=in_bus1_id)
        self.com1.p_nom["value"] = self.p_nom["value"]


    def model_init_output(self):
        pass

    def _add_param(self):
        pass
        # 参数：功率单位造价(元/W)
        # self._to_param("capital_cost", self.capital_cost["value"])

        # 参数：容量单位造价(元/Wh)
        # self._to_param("marginal_cost", self.marginal_cost["value"])

    def _add_var(self):
        pass
        # # 变量：最优额定功率（kW）
        # self._to_var("p_nom",in_output=True, in_caption="p_nom", in_unit="kW")
        # # 当p_nom_extendable为False时，p_nom将被fix为固定额定容量
        # if self.p_nom_extendable==False:
        #     self._var("p_nom").fix(self.p_nom["value"])

    def _add_constrait(self):
        # p_bus0 == -p_bus1, 注入为"+"，流出为"-"
        def func1(model, i):
            expr = self.com0._var("p_list")[i] == -self.com1._var("p_list")[i]
            return expr
        self._to_cons("p_cons_list1", func1, in_len=self._sys.simu_hours)

# 自然潮流支路（如电力线路、主变）
class Passive_Branch(Link_Base):
    branch_num = 0
    def __init__(self, in_sys, in_name, in_bus0_id, in_bus1_id):
        Link_Base.__init__(self, in_sys, in_bus0_id=in_bus0_id, in_bus1_id=in_bus1_id, in_name=in_name)

        self._sys = in_sys
        self.branch_id = Passive_Branch.branch_num
        Passive_Branch.branch_num = Passive_Branch.branch_num + 1

        self.bus0 = self._sys.bus_list[in_bus0_id]
        self.bus1 = self._sys.bus_list[in_bus1_id]

    def model_init_output(self):
        Link_Base.model_init_output(self)

    def _add_param(self):
        Link_Base._add_param(self)

    def _add_var(self):
        Link_Base._add_var(self)
        # 支路潮流p_list
        self._to_var("p_list", in_len=self._sys.simu_hours + 1, in_output=True, in_caption="p")  #这里+1是为了防止constraints的index构造时溢出

    def _add_constrait(self):
        Link_Base._add_constrait(self)

        # p_01 = -p_com0 = p_com1
        def func1(model, i):
            expr = self._var("p_list")[i] == self.com1._var("p_list")[i]
            return expr
        self._to_cons("p01_pcom0_pcom1_cons_list1", func1, in_len=self._sys.simu_hours)

# class Passive_Branch1(Container_Base):
#     branch_num = 0
#     def __init__(self, in_sys, in_name, in_bus0_id, in_bus1_id):
#         self.name_id = in_name+"["+str(in_bus0_id)+"->"+str(in_bus1_id)+"]"
#         Container_Base.__init__(self, in_name_id=self.name_id, in_sys=in_sys, in_model=in_sys.model)
#
#         self._sys = in_sys
#         self.branch_id = Passive_Branch.branch_num
#         Passive_Branch.branch_num = Passive_Branch.branch_num + 1
#
#         # 支路所属的容器节点0和容器节点1
#         self.bus0 = self._sys.bus_list[in_bus0_id]
#         self.bus1 = self._sys.bus_list[in_bus1_id]
#
#         # 支路的功率模型com0和com1（这里的com0和com1）
#         self.com0 = Component_Base(in_sys, in_name + "_com0", in_bus_id=in_bus0_id)
#         self.com1 = Component_Base(in_sys, in_name + "_com1", in_bus_id=in_bus1_id)
#
#     def model_init_output(self):
#         Container_Base.model_init_output(self)
#
#     def _add_param(self):
#         Container_Base._add_param(self)
#
#     def _add_var(self):
#         Container_Base._add_var(self)
#         # 支路潮流p_list
#         self._to_var("p_list", in_len=self._sys.simu_hours + 1, in_output=True, in_caption="p")  #这里+1是为了防止constraints的index构造时溢出
#
#     def _add_constrait(self):
#         Container_Base._add_constrait(self)
#
#         # p_01 = -p_com0 = p_com1
#         def func1(model, i):
#             expr = self._var("p_list")[i] == self.com1._var("p_list")[i]
#             return expr
#         self._to_cons("p01_pcom0_pcom1_cons_list1", func1, in_len=self._sys.simu_hours)
#
#         # p_com0 == -p_com1, 注入为"+"，流出为"-"
#         def func2(model, i):
#             expr = self.com0._var("p_list")[i] == -self.com1._var("p_list")[i]
#             return expr
#         self._to_cons("p_cons_list1", func2, in_len=self._sys.simu_hours)

# 电力支路（线路、主变）
class Elec_Branch(Passive_Branch):
    def __init__(self, in_sys, in_name, in_bus0_id, in_bus1_id, in_reactance_pu):
        Passive_Branch.__init__(self, in_sys, in_name=in_name, in_bus0_id=in_bus0_id, in_bus1_id=in_bus1_id)

        # 电抗（采用直流潮流，U1=U2=1，r=0，只考虑电抗）
        assert(in_reactance_pu != 0.0)      # 电抗不能等于0.0，负值也可以
        self.reactance = in_reactance_pu


    def model_init_output(self):
        Passive_Branch.model_init_output(self)

    def _add_param(self):
        Passive_Branch._add_param(self)
        # 参数：电力系统功角
        self._to_param("reactance", self.reactance)

    def _add_var(self):
        Passive_Branch._add_var(self)

    def _add_constrait(self):
        Passive_Branch._add_constrait(self)
        # 采用直流潮流，p* = (delta_0-delta_1）/ x*, (x* = x/Sb, p* = p/Sb, Sb=100MVA)
        def func1(model, i):
            expr = self._var("p_list")[i] / 1000.0 / 100 == (self.bus0._var("power_angle")[i]-self.bus1._var("power_angle")[i]) / self._param("reactance")
            return expr
        self._to_cons("p_dc_flow_cons_list", func1, in_len=self._sys.simu_hours)

# 单向有损Link(bus1->bus2)
# 用于常规电厂（燃料需建模）、P2G、P2Heat、P2Hydro、溴化锂等X2X
class Oneway_Link(Link_Base):
    def __init__(self, in_sys, in_bus0_id, in_bus1_id, in_name, in_capital_cost=0.0, in_p_nom=0.0, in_p_nom_extendable=False, in_effi=1.00, in_p_max_pu=1.0, in_p_min_pu=0.0, in_p_nom_max=float('inf'), in_p_nom_min=-float('inf') ):
        Link_Base.__init__(self, in_sys, in_bus0_id, in_bus1_id, in_name, in_capital_cost=in_capital_cost, in_p_nom=in_p_nom, in_p_nom_extendable=in_p_nom_extendable)

        self.com1.p_max_pu["value"] = in_p_max_pu
        self.com1.p_min_pu["value"] = in_p_min_pu
        self.com1.p_nom_max["value"] = in_p_nom_max
        self.com1.p_nom_min["value"] = in_p_nom_min

        self.effi = in_effi

    def _add_param(self):
        Link_Base._add_param(self)

        self._to_param("effi", self.effi)

    def _add_var(self):
        Link_Base._add_var(self)

    def _add_constrait(self):
        # 和父类约束冲突!!，因此不调用父类约束
        # Link_Base._add_constrait(self)

        # p_bus0 * effi == -p_bus1
        def func1(model, i):
            expr = self.com0._var("p_list")[i] * self.effi == -self.com1._var("p_list")[i]
            return expr
        self._to_cons("p_cons_list1", func1, in_len=self._sys.simu_hours)

# 联产（如天然气-->热和电）
class Cogeneration(Container_Base):
    def __init__(self, in_sys, in_bus0_id, in_bus1_id, in_bus2_id, in_name,
                 in_effi=1.0,
                 in_capital_cost=0.0,   # 总容量的单位造价
                 in_ratio_12=1.0,           # bus1和bus2的功率比例，如热电比
                 in_p_nom=0, in_p_nom_extendable=False,
                 in_p_max_pu=1.0, in_p_min_pu=0.0, in_p_nom_max=float('inf'), in_p_nom_min=-float('inf')
                 ):
        self.name_id = in_name+"【"+str(in_bus0_id)+"->"+str(in_bus1_id)+"&"+str(in_bus2_id)+"】"
        Container_Base.__init__(self, in_name_id=self.name_id, in_sys=in_sys, in_model=in_sys.model)
        self._sys = in_sys  #系统信息。前缀"_"的为protected成员，前缀"__"的为private成员

        self.effi = in_effi
        self.ratio_12 = in_ratio_12
        self.p_nom = {"value":in_p_nom, "name":"设定的额定功率(kW)"}
        self.p_nom_extendable = in_p_nom_extendable

        self.capital_cost = {"value":in_capital_cost, "name":"功率单位造价(元/W)"}

        # 从bus0流向bus1和bus2
        # bus0为负值，constraint_sign=-1
        self.com0 = Component_Base(in_sys, in_name + "_com0", in_bus_id=in_bus0_id, in_constraint_sign=-1)
        self.com0.p_nom["value"] = self.p_nom["value"]
        self.com0.capital_cost["value"] = self.capital_cost["value"]    # 造价全部分配在bus0

        self.com0.p_max_pu["value"] = in_p_max_pu
        self.com0.p_min_pu["value"] = in_p_min_pu
        self.com0.p_nom_max["value"] = in_p_nom_max
        self.com0.p_nom_min["value"] = in_p_nom_min

        # bus1
        self.com1 = Component_Base(in_sys, in_name + "_com1", in_bus_id=in_bus1_id)
        self.com1.p_nom["value"] = self.p_nom["value"]
        # bus2
        self.com2 = Component_Base(in_sys, in_name + "_com2", in_bus_id=in_bus2_id)
        self.com2.p_nom["value"] = self.p_nom["value"]

    def model_init_output(self):
        pass

    def _add_param(self):
        pass

    def _add_var(self):
        pass

    def _add_constrait(self):
        # -p0 * effi == p1 + p2, 注入为"+"，流出为"-"
        def func1(model, i):
            expr = -self.com0._var("p_list")[i] * self.effi == self.com1._var("p_list")[i] + self.com2._var("p_list")[i]
            return expr
        self._to_cons("p_cons_list1", func1, in_len=self._sys.simu_hours)

        # p1/p2 == ratio_12
        def func2(model, i):
            expr = self.com1._var("p_list")[i] == self.com2._var("p_list")[i] * self.ratio_12
            return expr
        self._to_cons("p_ratio_cons_list1", func2, in_len=self._sys.simu_hours)

# 储能的线性规划模型
class Energy_Storage(Container_Base):
    def __init__(self, in_sys, in_name_id, in_charge_effi, in_discharge_effi, in_store_init_zero=False, in_bus0_id=-1, in_bus1_id=-1, in_p_charge_nom=0.0, in_p_discharge_nom=0.0, in_e_nom=0.0,in_p_equal=True, in_p_charge_nom_extendable=False, in_p_discharge_nom_extendable=False, in_e_nom_extendable=False):
        Container_Base.__init__(self, in_name_id, in_sys, in_model=in_sys.model)

        # 该参数非常重要！！！，决定t[0]时，储能是否有能量（某些光储孤岛项目，t[0]如果储能e=0，则t[0]时刻光伏没有电，系统无法计算）
        self._store_init_zero = in_store_init_zero

        self.e_nom =                {"value":in_e_nom, "name":"设定的额定电量容量(kWh)"}
        self.e_nom_extendable = in_e_nom_extendable
        self.e_nom_max =        {"value":float('inf'), "name":"最大额定容量(kWh)"}
        self.e_nom_min =        {"value":0.0, "name":"最小额定容量(kWh)"}
        self.capital_cost_e =   {"value":0.0, "name":"容量单位造价(元/kWh)"}

        self.p_equal = in_p_equal   # p_charge_nom 是否等于 p_discharge_nom

        self.charge = Component_Base(in_sys, in_name_id + "_charge", in_constraint_sign=-1, in_bus_id=in_bus0_id)
        self.charge.p_max_pu["value"] = 1.0
        self.charge.p_min_pu["value"] = 0.0
        self.charge.p_nom =         {"value":in_p_charge_nom, "name":"设定的额定充电功率(kW)"}
        self.charge.p_nom_extendable = in_p_charge_nom_extendable
        self.charge.p_nom_max =        {"value":float('inf'), "name":"最大额定装机(kW)"}
        self.charge.p_nom_min =        {"value":-float('inf'), "name":"最小额定装机(kW)"}
        self.charge.effi =      {"value":in_charge_effi, "name":"充电效率"}
        # 110kV变电站向上级电网购电的结算价格（是省局每年调整的一个内部价格，各县不一样且存在劫富济贫，萧山局2020年是0.52158元/kWh）（2021.6.30来自萧山局朱主任）
        self.charge.marginal_cost =   {"value":0.0, "name":"边际充电量成本(元/kWh)"}
        self.charge.capital_cost =   {"value":0.0, "name":"功率单位造价(元/kW)"}

        self.discharge = Component_Base(in_sys, in_name_id + "_discharge", in_constraint_effi=in_discharge_effi, in_bus_id=in_bus1_id)
        self.discharge.p_max_pu["value"] = 1.0
        self.discharge.p_min_pu["value"] = 0.0
        self.discharge.p_nom =      {"value":in_p_discharge_nom, "name":"设定的额定放电功率(kW)"}
        self.discharge.p_nom_extendable = in_p_discharge_nom_extendable
        self.discharge.p_nom_max =        {"value":float('inf'), "name":"最大额定装机(kW)"}
        self.discharge.p_nom_min =        {"value":-float('inf'), "name":"最小额定装机(kW)"}
        self.discharge.effi =   {"value":in_discharge_effi, "name":"放电效率"}
        # 110kV变电站向上级电网购电的结算价格（是省局每年调整的一个内部价格，各县不一样且存在劫富济贫，萧山局2020年是0.52158元/kWh）（2021.6.30来自萧山局朱主任）
        self.discharge.marginal_cost =   {"value":0.0, "name":"边际发电量成本(元/kWh)"}
        self.discharge.capital_cost =   {"value":0.0, "name":"功率单位造价(元/kW)"}

        # self.capital_cost_p2 =   {"value":0.4, "name":"设备换新的功率单位造价(元/W)"}    # 10年后的成本
        # self.capital_cost_e2 =   {"value":1.0, "name":"设备换新的容量单位造价(元/Wh)"}   # 10年后的成本
        # self.capital_cost2_year = {"value":10, "name":"设备换新年限(年)"}

    def add_model(self):
        self.model_init_output()

        self._add_param()
        self._add_var()
        self._add_constrait()

    # 获取初期投资的表达式
    def _get_initial_cost_expr(self):
        # 初期造价
        # sys()中调用了所有component和container的_get_initial_cost_expr()，因此这里不需要调用charge和discharge
        # t_expr = self.charge._get_initial_cost_expr() + self.discharge._get_initial_cost_expr()
        # print("!!!!!!!!!!!!enter e_nom_cost ")
        if self.e_nom_extendable==True:
            t_expr = 1000*self._param("capital_cost_e") * (self._var("e_nom") - self.e_nom["value"])
            # print("!!!!!!!!!!!!e_nom_cost ok , expr is {}!!!!!!!!!!1".format(t_expr))
        else:
            # print("!!!!!!!!!!!!e_nom_cost not ok ")
            t_expr = 0
        return t_expr

        # t_expr = 0
        # if self.p_charge_nom_extendable==True:
        #     t_expr = t_expr + 1000*self._param("capital_cost_charge_p") * (self._var("p_charge_nom") - self.p_charge_nom["value"])
        # else:
        #     t_expr = t_expr + 0
        #
        # if self.p_discharge_nom_extendable==True:
        #     t_expr = t_expr + 1000*self._param("capital_cost_discharge_p") * (self._var("p_discharge_nom") - self.p_discharge_nom["value"])
        # else:
        #     t_expr = t_expr + 0
        #
        # if self.e_nom_extendable==True:
        #     t_expr = t_expr + 1000*self._param("capital_cost_e") * (self._var("e_nom") - self.e_nom["value"])
        # else:
        #     t_expr = t_expr + 0
        #
        # return t_expr

    # Life Cycle Cost的表达式
    def _add_objective_func_lcc(self):
        # # 运行成本(暂考虑全社会成本为：损耗电量*影子电价=(charge-discharge)*mc，由于充电功率定义为负方向、放电功率定义为正方向）
        # 因此为：-p_charge * 1 * mc_charge - p_discharge * 1 * mc_discharge
        # sys()中调用了所有component和container的_get_initial_cost_expr()，因此这里不需要调用charge和discharge
        # self.charge._add_objective_func_lcc(in_sign=-1)
        # self.discharge._add_objective_func_lcc(in_sign=-1)
        t_expr = self._get_initial_cost_expr()
        return t_expr

        # # return 0
        # print("目标函数增加：{}的LCC成本".format(self.name_id))
        #
        # # 初期造价
        # t_lcc_expr = self._get_initial_cost_expr()
        #
        # # # 运行成本(暂考虑全社会成本为：损耗电量*影子电价=(charge-discharge)*mc，由于充电功率定义为负方向、放电功率定义为正方向）
        # # 因此为：-p_charge * 1 * mc_charge - p_discharge * 1 * mc_discharge
        # t_lcc_expr = t_lcc_expr + sum(npv(
        #     -self.charge._var("p_list")[i]* self._param("charge_marginal_cost")-self.discharge._var("p_list")[i]* self._param("discharge_marginal_cost"),
        #     self._sys.rate,
        #     i - 1,
        #     self._sys.spring_festival.Year_Days()
        # ) for i in range(1, self._sys.simu_hours + 1))
        #
        # # t_lcc_expr = t_lcc_expr + sum(
        # #     self.charge._var("p_list")[i]* self._param("charge_marginal_cost")+self.discharge._var("p_list")[i]* self._param("discharge_marginal_cost")
        # #  for i in range(1, self._sys.simu_hours + 1))
        #
        # # self.price_output[0] = -888 # 针对储能
        # # self.price_output[1] = self._param("charge_marginal_cost")
        # # self.price_output[2] = self._param("discharge_marginal_cost")
        # return t_lcc_expr

    # Life Cycle Net Profit的表达式
    def _add_objective_func_lcnp(self):
        # 运行收益和成本( 暂考虑投资方的成本-收益为：充电成本-放电收益*电价优惠率，由于充电功率定义为负方向、放电功率定义为正方向）
        # 因此为：-p_charge[i] * 1 * price[i]  - p_discharge[i] * 1 * price[i] * 优惠率
        # sys()中调用了所有component和container的_get_initial_cost_expr()，因此这里不需要调用charge和discharge
        # self.charge._add_objective_func_lcnp(in_sign=-1)
        # self.discharge._add_objective_func_lcnp(in_sign=-1)
        t_expr = self._get_initial_cost_expr()
        return t_expr

        # # return 0
        # print("目标函数增加：{}的LCNP即成本-收益 ".format(self.name_id))
        #
        # # 初期造价
        # t_lcnp_expr = self._get_initial_cost_expr()
        #
        # # 运行收益和成本( 暂考虑投资方的成本-收益为：充电成本-放电收益*电价优惠率，由于充电功率定义为负方向、放电功率定义为正方向）
        # # 因此为：-p_charge[i] * 1 * price[i]  - p_discharge[i] * 1 * price[i] * 优惠率
        # t_lcnp_expr = t_lcnp_expr + sum(npv(
        #     -self.charge._var("p_list")[i] * self._sys._param("price_list")[i]-self.discharge._var("p_list")[i] * self._sys._param("price_list")[i] * (1-self._sys.investor_user_discount),
        #     self._sys.rate,
        #     i - 1,
        #     self._sys.spring_festival.Year_Days()
        # ) for i in range(1, self._sys.simu_hours + 1))
        #
        # # self.price_output[0] = -777 # 需要取price_list中的值
        # return t_lcnp_expr

    def _add_param(self):
        # sys()中是对所有container和component进行添加param、var和constraint的操作
        # self.charge._add_param()
        # self.discharge._add_param()

        # 参数：容量单位造价(元/Wh)
        self._to_param("capital_cost_e", self.capital_cost_e["value"])

        # # 参数：系统充电效率
        # self._to_param("effi_charge", self.effi_charge["value"])
        #
        # # 参数：系统放电效率
        # self._to_param("effi_discharge", self.effi_discharge["value"])
        #
        # # 参数：功率单位造价(元/W)
        # self._to_param("capital_cost_charge_p", self.capital_cost_charge_p["value"])
        #
        # # 参数：功率单位造价(元/W)
        # self._to_param("capital_cost_discharge_p", self.capital_cost_discharge_p["value"])
        #
        # # 参数：容量单位造价(元/Wh)
        # self._to_param("capital_cost_e", self.capital_cost_e["value"])
        #
        # # 参数：换新的功率单位造价(元/W)
        # self._to_param("capital_cost_p2", self.capital_cost_p2["value"])
        #
        # # 参数：换新的容量单位造价(元/Wh)
        # self._to_param("capital_cost_e2", self.capital_cost_e2["value"])
        #
        # # 参数：换新年限（年）
        # self._to_param("capital_cost2_year", self.capital_cost2_year["value"])
        #
        # # 参数：边际成本
        # self._to_param("charge_marginal_cost", self.charge_marginal_cost["value"])
        # self._to_param("discharge_marginal_cost", self.discharge_marginal_cost["value"])

    def _add_var(self):
        # sys()中是对所有container和component进行添加param、var和constraint的操作
        # self.charge._add_var()
        # self.discharge._add_var()

        # 变量：最优额定容量（kWh）
        self._to_var("e_nom",in_output=True, in_caption="e_nom", in_unit="kWh")
        if self.e_nom_extendable==False:
            self._var("e_nom").fix(self.e_nom["value"])

        # 变量：最优电量序列(kWh)
        self._to_var("e_list", in_len=self._sys.simu_hours + 1, in_output=True, in_caption="e")         #这里+1是为了防止constraints的index构造时溢出
        # ===========e[1]一定不能定为0，否则孤立光储系统的第一天的load[1]就无法满足从而导致无解===========
        if self._store_init_zero==True :
            self._var("e_list")[1].fix(0.0)
        # ===========e[1]一定不能定为0，否则孤立光储系统的第一天的load[1]就无法满足从而导致无解===========


        # # 变量：最优额定功率（kW）
        # self._to_var("p_charge_nom",in_output=True, in_caption="p_charge_nom", in_unit="kW")
        # if self.p_charge_nom_extendable==False:
        #     self._var("p_charge_nom").fix(self.p_charge_nom["value"])
        #
        # # 变量：最优额定功率（kW）
        # self._to_var("p_discharge_nom",in_output=True, in_caption="p_discharge_nom", in_unit="kW")
        # if self.p_discharge_nom_extendable==False:
        #     self._var("p_discharge_nom").fix(self.p_discharge_nom["value"])
        #
        # # 变量：最优额定容量（kWh）
        # self._to_var("e_nom",in_output=True, in_caption="e_nom", in_unit="kWh")
        # if self.e_nom_extendable==False:
        #     self._var("e_nom").fix(self.e_nom["value"])
        #
        # # 变量：最优电量序列(kWh)
        # self._to_var("e_list", in_len=self._sys.simu_hours + 1, in_output=True, in_caption="e")         #这里+1是为了防止constraints的index构造时溢出
        # self._var("e_list")[1].fix(0.0)

    def _add_constrait(self):
        # --------------------------------------------储能电量约束------------------------------------------
        # e[i+1] - e[i] == -p_charge[i]*effi_charge - p_discharge[i]/effi_discharge
        def func1(model, i):
            expr = self._var("e_list")[i+1] - self._var("e_list")[i] == -self.charge._var("p_list")[i]*self.charge._param("effi") - self.discharge._var("p_list")[i]/self.discharge._param("effi")
            return expr
        self._to_cons("energy_cons_list", func1, in_len=self._sys.simu_hours)

        # 0 <= e[i] <= e_nom
        def func2(model, i):
            expr = self._var("e_list")[i] <= self._var("e_nom")
            return expr
        self._to_cons("e_cons_list1", func2, in_len=self._sys.simu_hours+1)     #这里+1是为了确保e_list[i]-e_list[i-1]的约束中，如第8761个(e_list[8760])也在[0,p_nom]之间
        def func3(model, i):
            expr = self._var("e_list")[i] >= 0
            return expr
        self._to_cons("e_cons_list2", func3, in_len=self._sys.simu_hours+1)     #这里+1是为了确保e_list[i]-e_list[i-1]的约束中，如第8761个(e_list[8760])也在[0,p_nom]之间

        # --------------------------------------------储能功率约束----------------------------------------------
        # sys()中是对所有container和component进行添加param、var和constraint的操作
        # self.charge._add_constrait(in_sign=-1)
        # self.discharge._add_constrait(in_effi=self.discharge._param("effi"))

        if self.e_nom_extendable==True:
            def func4(model):
                expr = self._var("e_nom") >= self.e_nom["value"]
                return expr
            self._to_cons("e_nom_cons", func4)

        if self.p_equal==True:
            def func5(model):
                expr = self.charge._var("p_nom") == self.discharge._var("p_nom")
                return expr
            self._to_cons("q_equal_cons", func5)

    def model_init_output(self):
        global print_node_para_detail
        print("# -----------------------储能参数---------------------------")
        if print_node_para_detail :
            self.para_print()
        print("储能系统的充电效率为：",self.charge.effi["value"])
        print("储能系统的放电效率为：",self.discharge.effi["value"])
        print("储能功率的单位造价为：",self.charge.capital_cost["value"], "元/W")
        print("储能功率的单位造价为：",self.discharge.capital_cost["value"], "元/W")
        print("储能容量的单位造价为：",self.capital_cost_e["value"], "元/Wh")
        # print("设备换新的储能功率的单位造价为：",self.capital_cost_p2["value"], "元/W")
        # print("设备换新的储能容量的单位造价为：",self.capital_cost_e2["value"], "元/Wh")
        # print("设备换新的年限为：",self.capital_cost2_year["value"], "年")

    def para_print(self):
        t_member_dict = self.__dict__
        # print("# ----------------------ESS成员变量------------------------")
        # for t_member_key in t_member_dict:
        #     print("{:<20}".format(t_member_key), end=" ")   # <20表示：左对齐、占位20字节
        #     for t_member_value_key in t_member_dict[t_member_key]:
        #         t_value = t_member_dict[t_member_key][t_member_value_key]
        #         if isinstance(t_value,float):
        #             print("{:>10.2f}".format(t_value),end=" ")
        #         else:
        #             print("{:<20}".format(t_value),end=" ")
        #     print()
        # print("# --------------------------------------------------------")

# Sys，顶层方案
class Sys_Base(Container_Base):
    def __init__(self, in_simu_hours, in_name_id, in_investor, in_investor_user_discount, in_user_finance_strategy="max_rate", in_dpi=128, in_sys=0, in_analysis_day_list=0, tee=False, in_lambda=0):
        self.model = ConcreteModel()
        Container_Base.__init__(self, in_name_id=in_name_id, in_model=self.model, in_sys=in_sys)
        # create a model
        self.simu_hours = in_simu_hours
        self.dpi = in_dpi   # 绘图分辨率 128比较好，但文件大，64文件小，但放大略模糊
        self.tee = tee      # pyomo的中间输出标志tee

        # 投资方为政府投资或财务投资 = { "government", "user_finance" }
        # 政府投资：仅考虑全社会成本（如外部燃料成本、基建成本、电量损耗），不考虑转移支付（如内部的发电收益和用电成本）；不考虑效益（因为需求不变，即效益恒定不变，需要优化的仅为成本）
        # 财务投资：考虑投资方的收益和成本（包括燃料成本、基建成本、发电收益、用电成本等）
        self.investor = in_investor
        self.user_finance_strategy = in_user_finance_strategy    #财务最大化策略："max_rate"、"max_profit"
        self.investor_user_discount = in_investor_user_discount
        self.fp_lambda = in_lambda    # 分数规划Fractional Programming中构建的lambda迭代变量
        # self.fp_lambda = -1*(1.4)    # 分数规划Fractional Programming中构建的lambda迭代变量
        self.fp_dichotomy = 2.0 # 分数规划Fractional Programming中用于迭代调整的二分法系数
        self.fp_temp_obj = -1   # 分数规划Fractional Programming中的迭代目标函数最优值(fp_temp_obj为0时，对应的Lambda为原问题最优解。
        self._tables_for_report_output = []  # 财务优化（含分数规划)的中间结果表格列表

        self.component_list = []    # 所有Component_Base对象的引用
        self.container_list = []    # 所有Container_Base对象的引用
        self.object_list = []       # 所有Object_Base对象的引用

        self.bus_list = []         # 所有Bus容器（每个Bus容器有若干Component对象引用）
        self.passive_branch_list = []
        self.link_list = []                 # 所有Link_Base对象的引用

        self.analysis_day_list = in_analysis_day_list         # 要单独draw数据的那几日

        self.has_solution = False
        self.solver_result = 0

        self.pic_output = True
        self.print_model = False
        self.print_pyomo_result = False

        self.print_objfunc = False

    def print_objfunc_expr(self):
        if self.print_objfunc==True:
            print("----->目标函数表达式为：{}".format(self.model.OBJ_FUNC.expr))

    def Add_Bus(self):
        self.bus_list.append(Bus(self))

    def Add_Elec_Bus(self, in_if_reference_bus=False):
        self.bus_list.append(Elec_Bus(self, in_if_reference_bus))

    def Current_Bus_ID(self):
        return len(self.bus_list)-1

    def Current_Bus_Add_Component(self, in_com):
        self.bus_list[-1].Add_Component(in_com)

    def Bus_Add_Component(self, in_com, in_bus_id):
        self.bus_list[in_bus_id].Add_Component(in_com)

    def print_bus_list(self):
        print("# =======================节点列表===========================")
        print("【{}】各节点组件情况为：".format(self.name_id))
        for i in range(len(self.bus_list)):
            for j in range(len(self.bus_list[i].component_list)):
                print("节点[{}]包含组件: {}".format(i, self.bus_list[i].component_list[j].name_id))
            # for j in range(len(self.bus_list[i].container_list)):
            #     print("节点[{}]包含容器: {}".format(i, self.bus_list[i].container_list[j].name_id))

    def print_component_list(self):
        print("# =======================组件列表===========================")
        print("【{}】组件列表情况为：".format(self.name_id))
        for i in range(len(self.component_list)):
            print("{}".format(self.component_list[i].name_id))
        # for i in range(len(self.container_list)):
        #     print("{}".format(self.container_list[i].name_id))

    def do_optimize(self, in_create_report=True, inout_tables=0):   # in_note目前为计算中间结果的lambda值
        self.print_bus_list()
        self.print_component_list()

        self.cb_sys_add_param()         # 回调：设置sys参数
        self.cb_sys_add_var()           # 回调：设置sys变量
        self._container_and_component_add_model()         # 设置所有元件模型
        self._sys_add_constrait()
        self.cb_sys_add_constrait()     # 回调：设置sys约束（与元件相关，因此需在设置元件模型之后）
        self.cb_sys_add_objfunc()       # 回调：设置sys目标函数

        self.print_objfunc_expr()

        self._optimize()                                                                    # 执行计算
        if inout_tables!=0 :
            self._add_iteration_table_for_report_output( in_table_head_note="(lambda : {}, err : {:.1f}万元)".format(self.fp_lambda, value(self.model.OBJ_FUNC) / 10000),inout_tables=inout_tables)  # 添加中间结果表
        self.post_process(in_create_report=in_create_report, in_tables=inout_tables)     # 后处理

    def post_process(self, in_create_report=True, in_tables=0):
        self._print_solve_result()              # 输出计算结论
        if self.has_solution==True:
            # 有解
            self._print_opt_var()  # 输出最优变量
            self._add_output_opt_var_list()  # 注册最优时序变量
            # self._add_iteration_table_for_report_output(in_table_head_note="(lambda : {}, err : {:.1f}万元)".format(self.fp_lambda, value(self.model.OBJ_FUNC)/10000), inout_tables=inout_tables)  # 添加中间结果表
            if self.investor == "government" :
                # self._draw_opt_var_list()                 # 输出最优时序变量
                self._print_conclusion()                    # 输出统计结果
                if in_create_report==True :
                    self._draw_opt_var_list()               # 输出最优时序变量
                    # self._get_table_for_report_input()      # 生成计算报告所需的输入表格
                    # self._get_table_for_report_output()     # 生成计算报告所需的结果表格
                    self._create_report()                   # 生成计算报告、对应的docx文件

            elif self.investor == "user_finance" :
                # self._draw_opt_var_list()                 # 输出最优时序变量
                self._print_conclusion()                    # 输出统计结果
                if in_create_report==True :
                    self._draw_opt_var_list()               # 输出最优时序变量
                    # self._get_table_for_report_input()      # 生成计算报告所需的输入表格
                    # self._get_table_for_report_output()     # 生成计算报告所需的结果表格
                    self._create_report(in_tables=in_tables)                   # 生成计算报告、对应的docx文件

    # 内部函数：二分法迭代求解分数规划问题（难点在于G()可能无界或不可行，此时value(OBJ_FUNC)==0，需要判断往上界方向迭代还是反方向）
    @staticmethod
    def do_fractional_programming_iteration(in_sys_create_func, in_lambda=-5, in_iter_num=15, in_min_tolerance=100000, in_min=-10.0, in_max=10.0):
        # "user_finance"财务最优的分数规划迭代过程
        t_iteration_tables = []

        t_iter_num = in_iter_num            # 迭代次数
        t_min_tolerance = in_min_tolerance  # 可接受的近零值，先超过迭代次数或先达到可接受近零值即退出

        t_lambda = in_lambda                # lambda
        t_max = in_max                      # 迭代上界
        t_min = in_min                      # 迭代下届
        t_objvalue = 0                      # G()的目标函数值

        # 首先明确上下界是否ok（目标函数等于0，表明无界或不可行）
        # t_sys = Params_to_Sys(
        #     in_params=in_params,
        #     tee=False,
        #     in_open_id=t_open_id,
        #     in_fp_lambda=in_max,    # 检测lambda上界值
        #     in_investor=t_investor
        # )
        t_sys = in_sys_create_func()
        t_sys.fp_lambda = in_max
        t_sys.do_optimize(in_create_report=False, inout_tables=t_iteration_tables)
        t_max_ok = (value(t_sys.model.OBJ_FUNC) != 0)  # 判断G()的lambda上界是否有解

        # t_sys = Params_to_Sys(
        #     in_params=in_params,
        #     tee=False,
        #     in_open_id=t_open_id,
        #     in_fp_lambda=in_min,    # 检测lambda下界值
        #     in_investor=t_investor
        # )
        t_sys = in_sys_create_func()
        t_sys.fp_lambda = in_min
        t_sys.do_optimize(in_create_report=False, inout_tables=t_iteration_tables)
        t_min_ok = (value(t_sys.model.OBJ_FUNC) != 0) # 判断G()的lambda下界是否有解

        # 如果上下界都不ok，则直接返回（无解）
        if (t_max_ok == False) and (t_min_ok == False):
            return [None, None, None, None]

        t_record = {}
        t_result_list = []
        for i in range(t_iter_num):
            # t_sys = Params_to_Sys(
            #     in_params=in_params,
            #     tee=False,
            #     in_open_id=t_open_id,
            #     in_fp_lambda=t_lambda,
            #     in_investor=t_investor
            # )
            t_sys = in_sys_create_func()
            t_sys.fp_lambda = t_lambda
            if i == t_iter_num-1:
                t_sys.do_optimize(in_create_report=True, inout_tables=t_iteration_tables)
            else:
                t_sys.do_optimize(in_create_report=False, inout_tables=t_iteration_tables)
            t_objvalue = value(t_sys.model.OBJ_FUNC)

            # 如果G()的迭代值接近0并可接受，则认为当前lambda即为原F()的最优值
            if (abs(t_objvalue) < t_min_tolerance) and (t_objvalue!=0.0) :
                # 这里要专门输出报告
                t_sys.post_process(in_create_report=True, in_tables=t_iteration_tables)
                return [t_sys, t_lambda, t_objvalue, t_result_list]

            t_record["lambda"] = t_lambda
            t_record["min"] = t_min
            t_record["max"] = t_max
            # t_record["bes_kW_opt"] = value(t_ess1.charge._var("p_nom"))
            # t_record["bes_kWh_opt"] = value(t_ess1._var("e_nom"))

            # 如果：迭代结果>0，则当前lambda作为ok的下界
            if t_objvalue > 0:
                t_min = t_lambda
                t_lambda = (t_min + t_max) / 2.0
                t_min_ok = True
            # 如果：迭代结果<0，则当前lambda作为ok的上界
            elif t_objvalue < 0:
                t_max = t_lambda
                t_lambda = (t_min + t_max) / 2.0
                t_max_ok = True
            # 如果：迭代结果==0（即unbound或者infeasible），则检测上下界，哪个不ok，则当前lambda就作为哪个方向的界
            elif t_objvalue == 0:
                if t_min_ok == True:
                    t_max = t_lambda
                    t_lambda = (t_min + t_max) / 2.0
                elif t_max_ok == True:
                    t_min = t_lambda
                    t_lambda = (t_min + t_max) / 2.0

            t_record["objvalue"] = t_objvalue
            t_result_list.append(copy.copy(t_record))

        for item in t_result_list:
            print("=======", item, "========")

        # 返回可以接受的lambda
        return [t_sys, t_lambda, t_objvalue, t_result_list]

    def cb_sys_add_param(self):
        pass

    def cb_sys_add_var(self):
        pass

    def _container_and_component_add_model(self):
        print("# ==========================基本对象参数==============================")
        for i in range(len(self.component_list)):
            self.component_list[i].add_model()
        for i in range(len(self.container_list)):
            self.container_list[i].add_model()

    def _sys_add_constrait(self):
        # --------------------------------------------基尔霍夫约束--------------------------------------------
        # 所有p[i]之和为0，注入为"+"，流出为"-"
        # print("# ======================基尔霍夫约束=========================")
        for i_bus in range(len(self.bus_list)):
            # expr结构为{"expr":expr,"obj":obj}
            expr_list = []

            # 统计汇总每一个bus上的注入电源或负荷component
            # print("---bus{}---".format(i_bus))
            for i_obj in range(len(self.bus_list[i_bus].component_list)):
                t_obj = self.bus_list[i_bus].component_list[i_obj]
                # print("原有对象:{}".format(self.object_list[i_obj].name_id))
                # Load类，注册param类型的p_list
                if isinstance(t_obj, Undispatchable_Component):
                    expr_list.append({"expr":t_obj._param("p_list"),"obj":t_obj})
                # Bus类，注册var类型的p_list
                elif isinstance(t_obj, Component_Base):
                    expr_list.append({"expr":t_obj._var("p_list"),"obj":t_obj})

            # 注册每个bus节点下所有注入的simu_hours个基尔霍夫约束
            def func3(model, i):
                expr = 0
                for i_list in range(len(expr_list)):
                    if expr_list[i_list]["obj"].p_nom_extendable==True and isinstance(expr_list[i_list]["obj"], NE_Plant):
                        # if i==1:
                        #     print(expr_list[i_list]["expr"][i])
                        #     print(expr_list[i_list]["obj"]._var("p_nom"))

                        # 如果为新能源出力，且p_nom_extendable为True，则在该节点的出力为p_list*p_nom，其中p_list为参数list（出力标幺值）
                        # 注意：根据测试，在下面这个表达式里，必须要把_var放在左边，否则会编译报错
                        expr = expr_list[i_list]["obj"]._var("p_nom") * expr_list[i_list]["expr"][i] + expr
                    else:
                        expr = expr +expr_list[i_list]["expr"][i]
                expr = expr==0
                if i<=1:
                    print("约束(节点[{}]基尔霍夫): {}".format(i_bus, expr))
                if i==1:
                    print("...")
                if i>=self.simu_hours:
                    print("约束(节点[{}]基尔霍夫): {}".format(i_bus, expr))
                return expr
            self._to_cons("Kirchhoff_cons_list" + str(i_bus), in_func=func3, in_len=self.simu_hours,  in_print=False)

    def cb_sys_add_constrait(self):
        pass

    def _add_output_opt_var_list(self):
        for i in range(len(self.component_list)):
            self.component_list[i].add_output()
        for i in range(len(self.container_list)):
            self.container_list[i].add_output()

    def _print_opt_var_lists_range(self, in_lists, in_names):
        for i in range(len(in_lists)) :
            t_list = in_lists[i]
            t_list_name = in_names[i]
            # 打印所有时序变量的取值范围和成本/收益
            # t_cost = 0
            # if self.investor=="government":
            #     t_cost = list(np.array(t_list), )
            # if self.investor=="user_finance":
            #     t_cost = list_sumproduct(t_list, self._param_list_values("price_list"))
            print("序列取值范围: {:<20s} [ {:>15.2f}, {:>15.2f} ]".format(t_list_name, min(t_list), max(t_list)), flush=True)

    def _draw_opt_var_list(self):
        print("计算结果图表详见生成的png文件")
        def _draw_image_output(in_hours, in_plot_method="line", in_kde=False):
            t_plot = Relational_Plots()

            t_data_lists_part = []
            t_caption_list = []

            # 如果不考虑多月输出、或者仿真时长少于1年，则不输出多月数据
            if self.analysis_day_list == 0 or self.simu_hours<self.spring_festival.Year_Days():
                # component_list
                for x in range(len(self.component_list)):
                    for i in range(len(self.component_list[x].sequence_output_list)):
                        t_data_lists_part.append(self.component_list[x].sequence_output_list[i]["list"][:in_hours])
                        t_caption_list.append(self.component_list[x].sequence_output_list[i]["caption"])
                # container_list
                for x in range(len(self.container_list)):
                    for i in range(len(self.container_list[x].sequence_output_list)):
                        t_data_lists_part.append(self.container_list[x].sequence_output_list[i]["list"][:in_hours])
                        t_caption_list.append(self.container_list[x].sequence_output_list[i]["caption"])

                if in_hours == self.simu_hours:
                    # 只输出一次变量的范围
                    self._print_opt_var_lists_range(in_lists=t_data_lists_part, in_names=t_caption_list)

                t_name = "NPS_IO_{}h".format(in_hours)
                Data_Analysis.draw_lists(
                    in_open_id = self._remote_user_open_id,
                    in_dpi=self.dpi,
                    in_share_y=self.share_y,
                    in_lists=t_data_lists_part,
                    in_names=t_caption_list,
                    in_pic_name=t_name
                    # in_start=720*3,
                    # in_stop=720+720*3
                )
                self._pic_file_name_list.append(t_name)
                self._pic_file_url_list.append("https://www.poweryourlife.cn/static/pic/"+t_name+"_openid("+self._remote_user_open_id+").png")

            else:
                # analysis_day_list为[0,30,60,90]之类的情况
                for i_day in range(len(self.analysis_day_list)):
                    if in_hours > 720:
                        # 输出8760之类时
                        # 720h以上的，不考虑输出多个月的数据
                        # component_list
                        for x in range(len(self.component_list)):
                            for i in range(len(self.component_list[x].sequence_output_list)):
                                t_data_lists_part.append(
                                    self.component_list[x].sequence_output_list[i]["list"][:in_hours])
                                t_caption_list.append(self.component_list[x].sequence_output_list[i]["caption"])
                        # container_list
                        for x in range(len(self.container_list)):
                            for i in range(len(self.container_list[x].sequence_output_list)):
                                t_data_lists_part.append(
                                    self.container_list[x].sequence_output_list[i]["list"][:in_hours])
                                t_caption_list.append(self.container_list[x].sequence_output_list[i]["caption"])

                        if in_hours==self.simu_hours:
                            # 只输出一次变量的范围
                            self._print_opt_var_lists_range(in_lists=t_data_lists_part, in_names=t_caption_list)

                        t_name = "NPS_IO_{}h".format(in_hours)
                        Data_Analysis.draw_lists(
                            in_open_id=self._remote_user_open_id,
                            in_dpi=self.dpi,
                            in_share_y=self.share_y,
                            in_lists=t_data_lists_part,
                            in_names=t_caption_list,
                            in_pic_name=t_name
                            # in_start=720*3,
                            # in_stop=720+720*3
                        )
                        self._pic_file_name_list.append(t_name)
                        self._pic_file_url_list.append("https://www.poweryourlife.cn/static/pic/" + t_name + "_openid(" + self._remote_user_open_id + ").png")

                        break
                    else:
                        # 输出720、24之类时
                        t_data_lists_part = []
                        t_caption_list = []
                        # component_list
                        for x in range(len(self.component_list)):
                            for i in range(len(self.component_list[x].sequence_output_list)):
                                t_data_lists_part.append(self.component_list[x].sequence_output_list[i]["list"][self.analysis_day_list[i_day]*24:self.analysis_day_list[i_day]*24+in_hours])
                                t_caption_list.append(self.component_list[x].sequence_output_list[i]["caption"])
                        # container_list
                        for x in range(len(self.container_list)):
                            for i in range(len(self.container_list[x].sequence_output_list)):
                                t_data_lists_part.append(self.container_list[x].sequence_output_list[i]["list"][self.analysis_day_list[i_day]*24:self.analysis_day_list[i_day]*24+in_hours])
                                t_caption_list.append(self.container_list[x].sequence_output_list[i]["caption"])
                        t_name = "NPS_IO_{}h_{}th_day".format(in_hours, self.analysis_day_list[i_day])
                        Data_Analysis.draw_lists(
                            in_open_id=self._remote_user_open_id,
                            in_dpi=self.dpi,
                            in_share_y=self.share_y,
                            in_lists=t_data_lists_part,
                            in_names=t_caption_list,
                            in_pic_name=t_name
                            # in_start=self.analysis_day_list[i_day]*24,
                            # in_stop=self.analysis_day_list[i_day]*24+720
                        )
                        self._pic_file_name_list.append(t_name)
                        self._pic_file_url_list.append("https://www.poweryourlife.cn/static/pic/" + t_name + "_openid(" + self._remote_user_open_id + ").png")

                        # t_plot.draw_p_output(
                        #     "pic/NPS_Invest_Opt_{}h_{}th_day".format(in_hours, self.analysis_day_list[i_day]),
                        #     t_caption_list,
                        #     t_data_lists_part,
                        #     in_start_time=self.analysis_day_list[i_day],
                        #     in_plot_method=in_plot_method,
                        #     in_kde=in_kde)

        if self.pic_output==True:

            # 绘制 全部h 曲线
            # _draw_image_output(self.simu_hours, in_plot_method="line", in_kde=Fals)

            # 绘制 8760、720、24h 曲线
            if self.simu_hours>8760:
                _draw_image_output(self.simu_hours)
            if self.simu_hours>=8760:
                _draw_image_output(8760)
            elif self.simu_hours>=7000:
                _draw_image_output(self.simu_hours)
            if self.simu_hours>=720:
                _draw_image_output(720)
            if self.simu_hours>=24:
                # _draw_image_output(24,in_plot_method="bar", in_kde=False)
                _draw_image_output(24,in_plot_method="bar", in_kde=False)
            if self.simu_hours==1:
                _draw_image_output(1,in_plot_method="bar", in_kde=False)

            # 注意：在后台的话，plt.show()改为plt.close()才能正常保存图片
            t_user_id = "remote_user"
            # t_user_id = "local_user"
            if t_user_id == "local_user":
                plt.show()
            else:
                plt.close()

    def _print_conclusion(self):
        # 打印 name_id、kW_opt、kW造价、kWh_opt、kWh造价、运行收益
        print("{:>8s} {:>20s} {:>19s} {:>10s} {:>19s} {:>10s} {:>19s} {:>10s}".format(
            "序号",
            "name_id",
            "kW_opt",
            "新增投资",
            "kWh_opt",
            "新增投资",
            "kWh",
            "运行收益"
        ))
        i=0

        # component_list
        for x in range(len(self.component_list)):
            o = self.component_list[x]
            # if isinstance(o, Load) or isinstance(o, Plant) or isinstance(o, Slack_Node):
            if isinstance(o, Component_Base):
                i = i + 1
                if hasattr(o, "p_nom"):
                    if isinstance(o, Load):
                        kw_opt=o.p_nom["value"]
                    else:
                        kw_opt=o._var_value(in_attr_name="p_nom")
                else:
                    kw_opt="/"

                if hasattr(o, "p_nom"):
                    if not isinstance(o, Load):
                        kw_cost = (o._var_value(in_attr_name="p_nom") - o.p_nom["value"]) * o.capital_cost["value"]
                        kw_cost = kw_cost * 1000 / 10000.0    # 输出万元
                    else:
                        kw_cost = 0.0
                else:
                    kw_cost="/"

                if hasattr(o, "e_nom"):
                    kwh_opt=o.self._var_value(in_attr_name="e_nom")
                else:
                    kwh_opt="/"


                kwh, hours = o.get_optimized_kWh_and_hours()
                # if isinstance(o, Load):
                #     kwh = sum(o._param_list_values(in_attr_name="p_list"))
                # else:
                #     kwh = sum(o._var_list_values(in_attr_name="p_list"))

                cnp_cost = o.get_cnp_cost()
                # if not isinstance(o, Load):
                # # if isinstance(o, Slack_Node) or o.p_nom_extendable==True:
                #     if self.investor=="government":
                #         cnp_cost = -o.marginal_cost["value"] * kwh
                #         cnp_cost = cnp_cost / 10000.0  # 输出万元
                #     if self.investor=="user_finance":
                #         if isinstance(o, Slack_Node):
                #             cnp_cost = -sum(np.array(o._var_list_values(in_attr_name="p_list"))*o.marginal_cost["value"])
                #         else:
                #             cnp_cost = -list_sumproduct(
                #                 o._var_list_values(in_attr_name="p_list"),
                #                 np.array([o.marginal_cost["value"]]*len(self._param_list_values(in_attr_name="price_list")))-np.array(self._param_list_values(in_attr_name="price_list"))
                #             )
                #         cnp_cost = cnp_cost / 10000.0  # 输出万元
                #         # print("cnp_cost is {}".format(cnp_cost))
                #         # print(o._var_list_values(in_attr_name="p_list"))
                #         # print(self._param_list_values(in_attr_name="price_list"))
                # else:
                #     cnp_cost = 0.0

                print("{:>9d} {:>20s} {:>19.2f} {:>13.2f} {:>19} {:>13} {:>19.2f} {:>14.2f}".format(
                    i,
                    o.name_id,
                    kw_opt,
                    kw_cost,
                    kwh_opt,
                    "/",
                    kwh,
                    cnp_cost
                ))

        # container_list
        for x in range(len(self.container_list)):
            o = self.container_list[x]
            # if isinstance(o, Load) or isinstance(o, Plant) or isinstance(o, Slack_Node):
            if isinstance(o, Energy_Storage):
                i = i + 1
                kw_opt = "/"

                if hasattr(o, "e_nom"):
                    kwh_opt=o._var_value(in_attr_name="e_nom")
                else:
                    kwh_opt="/"

                if hasattr(o, "e_nom"):
                    kwh_cost = (o._var_value(in_attr_name="e_nom") - o.e_nom["value"]) * o.capital_cost_e["value"]
                    kwh_cost = kwh_cost * 1000 / 10000.0  # 输出万元
                else:
                    kwh_cost="/"

                kwh = sum(o._var_list_values(in_attr_name="e_list"))

                print("{:>9d} {:>20s} {:>19s} {:>13} {:>19.2f} {:>13.2f} {:>19.2f} {:>14}".format(
                    i,
                    o.name_id,
                    kw_opt,
                    "/",
                    kwh_opt,
                    kwh_cost,
                    kwh,
                    "/"
                ))

    def cb_sys_add_objfunc(self):
        pass

    def _optimize(self):
        # print(f'======================_optimize()========================')
        # pyomo模型输出
        # self.model.pprint()
        if self.print_model == True:
            self.model.pprint()

        # SolverFactory('glpk').solve(self.model).write()
        if is_mac():
            # t_solver = SolverFactory('gurobi', server_io="python")
            t_solver = SolverFactory('gurobi')
            # print(f'======================gurobi========================')

        else:
            t_solver = SolverFactory('cplex')
            # print(f'======================cplex========================')
        # t_solver = SolverFactory('glpk')
        # t_solver.options['max_iter'] = 1000   # glpk用不了这个参数
        self.solver_result = t_solver.solve(
            self.model,
            tee=self.tee        #输出中间结果
        )
        # print(f'======================_optimize() finished.========================')

        # gdp可以直接调用glpk，下面2行并不需要
        # TransformationFactory('gdp.bigm').apply_to(model)
        # SolverFactory('baron').solve(model)

    def _print_solve_result(self):
        print("# =====================PYOMO优化结论========================")
        if self.print_pyomo_result==True :
            print(self.solver_result)
        else:
            print("\"status\" = \"{}\"".format(self.solver_result.solver.status))
            print("\"termination_condition\" = \"{}\"".format(self.solver_result.solver.termination_condition))
        print("# =======================优化结果===========================")
        if self.solver_result.solver.status=="ok":
            print("1、计算成功")
        else:
            print("1、计算失败")
            print("# =========================================================")
            return

        if self.solver_result.solver.termination_condition=="optimal":
            print("2、计算得到最优解")
            self.has_solution = True
        else:
            print("2、计算无最优解")
        print("3、计算时间为：{:.3f}秒".format(self.solver_result.solver.time))

    def _print_opt_var(self):
        print("# ----------------------变量最优解--------------------------")
        # 所有component的单变量最优值
        for i in range(len(self.component_list)):
            o = self.component_list[i]
            for j in range(len(o.var_output_list)):
                v = o.var_output_list[j]
                if v["type"]=="param":
                    print("最优值: {:<20s} {:>15.2f} {}".format(v["caption"], self._param_value(in_name_id=o.name_id, in_attr_name=v["name"]),v["unit"]))
                if v["type"]=="var":
                    print("最优值: {:<20s} {:>15.2f} {}".format(v["caption"], self._var_value(in_name_id=o.name_id, in_attr_name=v["name"]),v["unit"]))

        # 所有component的最优p_list对应的电量之和以及小时数
        for i in range(len(self.component_list)):
            o = self.component_list[i]
            if o.e_output==True:
                kwh, hours = o.get_optimized_kWh_and_hours()
                print("全周期电量: {:<20s} {:>10.3f} 亿kWh ({:>7.1f})h".format(o.name_id, kwh/10**8, hours))

                # if isinstance(o, Undispatchable_Component):
                #     # param化的p_list电量统计
                #     if isinstance(o, NE_Plant):
                #         # 新能源p_list电量统计
                #         if o.p_nom_extendable==True:
                #             t_list = o._param_list_values(in_attr_name="p_list")
                #             t_sum = sum(t_list) * o._var_value("p_nom")
                #             # t_sum = sum(t_list) * o.p_nom["value"]
                #             t_max = max(o._var_value("p_nom"), max(max(t_list), -min(t_list)))
                #             # t_max = max(o.p_nom["value"], max(max(t_list), -min(t_list)))
                #             print("全周期电量: {:<20s} {:>10.3f} 亿kWh ({:>7.1f})h".format( o.name_id, t_sum/10**8, (t_sum/t_max if t_max!=0 else 0) ) )
                #         else:
                #             t_list = o._param_list_values(in_attr_name="p_list")
                #             t_sum = sum(t_list)
                #             t_max = o.p_nom["value"]
                #             # t_max = o.p_nom["value"]
                #             print("全周期电量: {:<20s} {:>10.3f} 亿kWh ({:>7.1f})h".format( o.name_id, t_sum/10**8, (t_sum/t_max if t_max!=0 else 0) ) )
                #     else:
                #         # load等的p_list电量统计
                #         t_list = o._param_list_values(in_attr_name="p_list")
                #         t_sum = sum(t_list)
                #         # t_max = value(o._var("p_nom"))
                #         t_max = o.p_nom["value"]
                #         print("全周期电量: {:<20s} {:>10.3f} 亿kWh ({:>7.1f})h".format( o.name_id, t_sum/10**8, (t_sum/t_max if t_max!=0 else 0) ) )
                # else:
                #     # var的p_list电量统计
                #     t_list = o._var_list_values(in_attr_name="p_list")
                #     t_sum = sum(t_list)
                #     if hasattr(o, "p_nom"):
                #         t_max = o._var_value("p_nom")
                #         # t_max = o.p_nom["value"]
                #     else:
                #         t_max = max(max(t_list), -min(t_list))
                #     print("全周期电量: {:<20s} {:>10.3f} 亿kWh ({:>7.1f})h".format( o.name_id, t_sum/10**8, (t_sum/t_max if t_max!=0 else 0) ) )

        # 所有container的单变量最优值
        for i in range(len(self.container_list)):
            o = self.container_list[i]
            for j in range(len(o.var_output_list)):
                v = o.var_output_list[j]
                if v["type"]=="param":
                    print("最优值: {:<20s} {:>15.2f} {}".format(v["caption"], self._param_value(in_name_id=o.name_id, in_attr_name=v["name"]),v["unit"]))
                if v["type"]=="var":
                    print("最优值: {:<20s} {:>15.2f} {}".format(v["caption"], self._var_value(in_name_id=o.name_id, in_attr_name=v["name"]),v["unit"]))

        if self.investor=="government":
            print("【目标函数值】 为 {:.3f} 万元(NPV,折现率为{:.3f})".format(value(self.model.OBJ_FUNC)/10000.0, self.rate))
            # print("目标函数值为 {:.8f} 万元(NPV,折现率为{:.3f})".format(self.model.objective()/10000.0, self.rate))

        if self.investor=="user_finance":
            print("分数规划Fractional Programming的【Lambda】为: {}".format(self.fp_lambda))
            print("分数规划Fractional Programming的【迭代目标函数值】为 {:.10f} ".format(value(self.model.OBJ_FUNC)))
            self.fp_temp_obj = value(self.model.OBJ_FUNC)

        print("# =========================================================")

# 全系统：目标函数、基尔霍夫约束、新能源弃能约束、碳排放约束等
class Sys(Sys_Base):
    def __init__(self, in_simu_hours, in_spring_festival, in_lambda=0, in_remote_user_open_id="", in_investor="government", in_user_finance_strategy="max_rate", in_investor_user_discount=0.1, in_name_id="", in_rate=0, in_analysis_day_list=0, in_share_y=False, in_bus0=0, in_dpi=128, tee=False):
        Sys_Base.__init__(self, in_lambda=in_lambda, in_investor=in_investor, in_user_finance_strategy=in_user_finance_strategy, in_investor_user_discount=in_investor_user_discount, in_simu_hours=in_simu_hours, in_name_id=in_name_id, in_analysis_day_list=in_analysis_day_list, in_dpi=in_dpi, tee=tee)

        # 24h 目录电价序列（元/kWh）（2021.1.1日起执行的浙江一般工商业电价（1-10kV）
        self.tariff_list = [
            0.3536, 0.3536, 0.3536, 0.3536, 0.3536, 0.3536,
            0.3536, 0.3536, 0.8656, 0.8656, 0.8656, 0.3536,
            0.3536, 0.8656, 0.8656, 0.8656, 0.8656, 0.8656,
            0.8656, 1.1636, 1.1636, 0.8656, 0.3536, 0.3536 ]

        self.rate = in_rate    # 用于计算npv的折现率

        self.original_simu_hours = in_simu_hours
        self.original_simu_years = in_simu_hours // 8760
        self.spring_festival = in_spring_festival     # 基尔霍夫约束中，不考虑春节期间的源荷平衡
        # simu_hours仿真时长减去春节的时长
        if self.spring_festival.bypass==True:
            self.simu_hours = self.simu_hours - self.spring_festival.hours

        self.output_p_charge_opt_list = []
        # self.output_p_discharge_opt_list = []
        self.output_e_opt_list = []
        self.output_price_list = []
        self.share_y = in_share_y

        # 计算报告的文摘string、对应的docx文件url
        self._report_string_list = []
        self._report_file_url = ""
        self._remote_user_open_id = in_remote_user_open_id
        self._pic_file_name_list = []                       # 输出图片的名字list，如["xxx24h.png","xxx720h.png"]
        self._pic_file_url_list = []                        # 输出图片的url list，如["https://.../static/pic/xxx24h.png",]

        print("排除春节负荷为 {}".format(self.spring_festival.bypass))
        print("仿真时长为 {}h".format(self.simu_hours))
        print("投资分析模式为 \"{}\"".format(self.investor))

    def get_result_dict(self):
        t_dict = {
            "status":                   self.solver_result.solver.status,
            "termination_condition":    0,
            "has_solution":             0,
            "time":                     "{:.2f}".format(self.solver_result.solver.time),
            "report":                   0,
            "report_file_url":          "",
        }

        if t_dict["status"] == "ok":
            t_dict["termination_condition"] = self.solver_result.solver.termination_condition
            if t_dict["termination_condition"] == "optimal" :
                t_dict["has_solution"] = True
                t_dict["report"] = self._report_string_list
                t_dict["report_file_url"] = self._report_file_url
            else:
                t_dict["has_solution"] = False
        else :
            t_dict["termination_condition"] = "n/a"
            t_dict["has_solution"] = "n/a"

        return t_dict

    # ===================生成计算报告所需的输入表格===================
    def _get_table_for_report_input(self):
        rtn_table = []

        # 报告不同于调试输出，不宜采用全部component的输出，而是适合遍历容器的方式输出
        obj_list = [
            {"class_name":"Load", "name_id":"elec load", "verbose":"电力负荷"},
            {"class_name":"Load", "name_id":"heat load", "verbose":"热力负荷"},
            {"class_name":"Load", "name_id":"cold load", "verbose":"冷力负荷"},

            {"class_name":"NE_Plant", "name_id":"wind" , "verbose":"风电"},
            {"class_name":"NE_Plant", "name_id":"pv"   , "verbose":"光伏"},
            {"class_name":"NE_Plant", "name_id":"hydro", "verbose":"水电"},

            {"class_name":"Plant", "name_id":"coal"    , "verbose":"煤电"},
            {"class_name":"Plant", "name_id":"nuclear" , "verbose":"核电"},
            {"class_name":"Plant", "name_id":"diesel"  , "verbose":"柴发"},

            {"class_name":"Energy_Storage", "name_id":"php"  , "verbose":"抽水蓄能"},
            {"class_name":"Energy_Storage", "name_id":"hes"  , "verbose":"蓄氢系统"},
            {"class_name":"Energy_Storage", "name_id":"bes"  , "verbose":"电池储能"},
            {"class_name":"Energy_Storage", "name_id":"tes"  , "verbose":"蓄热系统"},
            {"class_name":"Energy_Storage", "name_id":"ces"  , "verbose":"蓄冷系统"},

            {"class_name":"Oneway_Link", "name_id":"elec boiler"  , "verbose":"电锅炉"},
            {"class_name":"Oneway_Link", "name_id":"elec cooler"  , "verbose":"电制冷"},
            {"class_name":"Oneway_Link", "name_id":"gas turbine"  , "verbose":"燃气电站"},
            {"class_name":"Oneway_Link", "name_id":"gas boiler"   , "verbose":"燃气锅炉"},

            {"class_name":"Cogeneration", "name_id":"heatpump"  , "verbose":"热泵"},
            {"class_name":"Cogeneration", "name_id":"CHP"       , "verbose":"热电联产"},

            {"class_name":"Primary_Energy_Supply", "name_id":"gas supply" , "verbose":"燃气"},

            {"class_name":"Slack_Node" , "name_id":"inject" , "verbose":"电网下送"},
            {"class_name":"Slack_Node", "name_id":"absorp" , "verbose":"电网上送"},
        ]
        # 返回对象的{"class_name":xxx, "verbose":xxx}
        def get_obj_info(in_obj):
            obj_info = {
                "class_name": "",
                "verbose"   : ""
            }
            for item in obj_list:
                if (item["name_id"] in in_obj.name_id) and isinstance(in_obj, eval(item["class_name"])):
                    obj_info["class_name"]  = item["class_name"]
                    obj_info["verbose"]     = item["verbose"]
                    # 找到则返回obj_info
                    return obj_info
            # 没找到则返回0
            return 0

        def obj_to_table(in_obj, in_obj_info):
            t_row = [0] * len(t_table_header)
            t_rows = []
            t_simu_year = self.simu_hours//8760 if self.simu_hours>=8760 else 1


            if in_obj_info["class_name"] == "NE_Plant":
                t_row[0] = in_obj_info["verbose"]
                t_row[1] = "0"
                t_row[2] = "{:.3f}".format(in_obj.capital_cost["value"])
                t_row[3] = "-"
                t_row[4] = "{:.1f}".format(in_obj.p_nom["value"]/1000.0)
                t_row[5] = "-"
                t_row[6] = "是" if in_obj.p_nom_extendable==True else "否"
                t_row[7] = "{:.2f}".format(in_obj.p_min_pu["value"])
                t_row[8] = "{:.2f}".format(in_obj.p_max_pu["value"])
                t_row[9] = "-"
                t_rows.append(t_row)

            if in_obj_info["class_name"] == "Plant":
                t_row[0] = in_obj_info["verbose"]
                t_row[1] = "{:.3f}".format(in_obj.marginal_cost["value"])
                t_row[2] = "{:.3f}".format(in_obj.capital_cost["value"])
                t_row[3] = "-"
                t_row[4] = "{:.1f}".format(in_obj.p_nom["value"]/1000.0)
                t_row[5] = "-"
                t_row[6] = "是" if in_obj.p_nom_extendable==True else "否"
                t_row[7] = "{:.2f}".format(in_obj.p_min_pu["value"])
                t_row[8] = "{:.2f}".format(in_obj.p_max_pu["value"])
                t_row[9] = "{:.2f}".format(in_obj.effi["value"])
                t_rows.append(t_row)

            if in_obj_info["class_name"] == "Energy_Storage":
                t_row[0] = in_obj_info["verbose"]
                t_row[1] = "0"
                t_row[2] = "{:.3f}/{:.3f}".format(in_obj.charge.capital_cost["value"], in_obj.discharge.capital_cost["value"])
                t_row[3] = "{:.3f}".format(in_obj.capital_cost_e["value"])
                t_row[4] = "{:.1f}/{:.1f}".format(in_obj.charge.p_nom["value"]/1000.0, in_obj.discharge.p_nom["value"]/1000.0)
                t_row[5] = "{:.1f}".format(in_obj.e_nom["value"]/1000.0)
                t_row[6] = "是" if in_obj.charge.p_nom_extendable==True else "否"
                t_row[7] = "{:.2f}/{:.2f}".format(in_obj.charge.p_min_pu["value"], in_obj.discharge.p_min_pu["value"])
                t_row[8] = "{:.2f}/{:.2f}".format(in_obj.charge.p_max_pu["value"], in_obj.discharge.p_max_pu["value"])
                t_row[9] = "{:.2f}/{:.2f}".format(in_obj.charge.effi["value"], in_obj.discharge.effi["value"])
                t_rows.append(t_row)

            if in_obj_info["class_name"] == "Oneway_Link":
                t_row[0] = in_obj_info["verbose"]
                t_row[1] = "-"
                t_row[2] = "{:.3f}".format(in_obj.capital_cost["value"])
                t_row[3] = "-"
                t_row[4] = "{:.1f}".format(in_obj.p_nom["value"]/1000.0)
                t_row[5] = "-"
                t_row[6] = "是" if in_obj.p_nom_extendable==True else "否"
                t_row[7] = "{:.2f}".format(in_obj.com1.p_min_pu["value"])
                t_row[8] = "{:.2f}".format(in_obj.com1.p_max_pu["value"])
                t_row[9] = "{:.2f}".format(in_obj.effi)
                t_rows.append(t_row)

            if in_obj_info["class_name"] == "Cogeneration":
                t_row[0] = in_obj_info["verbose"]
                t_row[1] = "0"
                t_row[2] = "{:.3f}".format(in_obj.capital_cost["value"])
                t_row[3] = "-"
                t_row[4] = "{:.1f}".format(in_obj.com0.p_nom["value"]/1000.0)
                t_row[5] = "-"
                t_row[6] = "是" if in_obj.p_nom_extendable==True else "否"
                t_row[7] = "{:.2f}".format(in_obj.com0.p_min_pu["value"])
                t_row[8] = "{:.2f}".format(in_obj.com0.p_max_pu["value"])
                t_row[9] = "{:.2f}".format(in_obj.effi)
                t_rows.append( t_row)

            if in_obj_info["class_name"] == "Slack_Node":
                t_row[0] = in_obj_info["verbose"]
                t_row[1] = "{:.3f}".format(in_obj.marginal_cost["value"])
                t_row[2] = "{:.3f}".format(in_obj.capital_cost["value"])
                t_row[3] = "-"
                t_row[4] = "{:.1f}".format(in_obj.p_nom["value"]/1000.0)
                t_row[5] = "-"
                t_row[6] = "是" if in_obj.p_nom_extendable==True else "否"
                t_row[7] = "{:.2f}".format(in_obj.p_min_pu["value"])
                t_row[8] = "{:.2f}".format(in_obj.p_max_pu["value"])
                t_row[9] = "-"
                t_rows.append(t_row)

            if in_obj_info["class_name"] == "Primary_Energy_Supply":
                t_row[0] = in_obj_info["verbose"]
                t_row[1] = "{:.3f}".format(in_obj.marginal_cost["value"])
                t_row[2] = "-"
                t_row[3] = "-"
                t_row[4] = "-"
                t_row[5] = "-"
                t_row[6] = "-"
                t_row[7] = "-"
                t_row[8] = "-"
                t_row[9] = "-"
                t_rows.append(t_row)

            for row in t_rows :
                if in_obj_info["class_name"]=="Primary_Energy_Supply" or in_obj_info["class_name"]=="Slack_Node":
                    # 负荷和slack放在表格最上面、表头的下面
                    rtn_table.insert(1, row)
                else:
                    # 其他放在表格下面
                    rtn_table.append(row)
            return

        t_table_header = [
            "项目类型", "边际成本(元/kWh)", "单位造价(元/W)", "单位造价(元/Wh)", "存量装机(MW)", "存量装机(MWh)", "规模优化", "最小出力", "最大出力", "效率"
        ]
        rtn_table.append(t_table_header)
        for obj in self.object_list :
            t_obj_info = get_obj_info(obj)
            if t_obj_info!=0:
                obj_to_table(obj, t_obj_info)

        # 决策变量的变化范围
        # 投资及运行成本汇总
        # 其他值（目标函数值、折现率等）
        t_objs = []
        for o in self.object_list:
            t_objs.append(o.name_id)

        for row in rtn_table:
            print(row)

        print(t_objs)
        return rtn_table

    # ===================添加计算的中间结果表格===================
    def _add_iteration_table_for_report_output(self, in_table_head_note, inout_tables):
        if inout_tables!=0:
            t_result = {
                "note" : in_table_head_note,
                "table" : self._get_table_for_report_output()
            }
            inout_tables.append(t_result)

    # ===================生成计算报告所需的结果表格===================
    def _get_table_for_report_output(self):
        rtn_table = []

        # 报告不同于调试输出，不宜采用全部component的输出，而是适合遍历容器的方式输出
        obj_list = [
            {"class_name":"Load", "name_id":"elec load", "verbose":"电力负荷"},
            {"class_name":"Load", "name_id":"heat load", "verbose":"热力负荷"},
            {"class_name":"Load", "name_id":"cold load", "verbose":"冷力负荷"},

            {"class_name":"NE_Plant", "name_id":"wind" , "verbose":"风电"},
            {"class_name":"NE_Plant", "name_id":"pv"   , "verbose":"光伏"},
            {"class_name":"NE_Plant", "name_id":"hydro", "verbose":"水电"},

            {"class_name":"Plant", "name_id":"coal"    , "verbose":"煤电"},
            {"class_name":"Plant", "name_id":"nuclear" , "verbose":"核电"},
            {"class_name":"Plant", "name_id":"diesel"  , "verbose":"柴发"},

            {"class_name":"Energy_Storage", "name_id":"php"  , "verbose":"抽水蓄能"},
            {"class_name":"Energy_Storage", "name_id":"hes"  , "verbose":"蓄氢系统"},
            {"class_name":"Energy_Storage", "name_id":"bes"  , "verbose":"电池储能"},
            {"class_name":"Energy_Storage", "name_id":"tes"  , "verbose":"蓄热系统"},
            {"class_name":"Energy_Storage", "name_id":"ces"  , "verbose":"蓄冷系统"},

            {"class_name":"Oneway_Link", "name_id":"elec boiler"  , "verbose":"电锅炉"},
            {"class_name":"Oneway_Link", "name_id":"elec cooler"  , "verbose":"电制冷"},
            {"class_name":"Oneway_Link", "name_id":"gas turbine"  , "verbose":"燃气电站"},
            {"class_name":"Oneway_Link", "name_id":"gas boiler"   , "verbose":"燃气锅炉"},

            {"class_name":"Cogeneration", "name_id":"heatpump"  , "verbose":"热泵"},
            {"class_name":"Cogeneration", "name_id":"CHP"       , "verbose":"热电联产"},

            {"class_name":"Primary_Energy_Supply", "name_id":"gas supply" , "verbose":"燃气"},

            {"class_name":"Slack_Node" , "name_id":"inject" , "verbose":"电网下送"},
            {"class_name":"Slack_Node", "name_id":"absorp" , "verbose":"电网上送"},
        ]
        # 返回对象的{"class_name":xxx, "verbose":xxx}
        def get_obj_info(in_obj):
            obj_info = {
                "class_name": "",
                "verbose"   : ""
            }
            for item in obj_list:
                if (item["name_id"] in in_obj.name_id) and isinstance(in_obj, eval(item["class_name"])):
                    obj_info["class_name"]  = item["class_name"]
                    obj_info["verbose"]     = item["verbose"]
                    # 找到则返回obj_info
                    return obj_info
            # 没找到则返回0
            return 0

        def obj_to_table(in_obj, in_obj_info):
            t_row = [0] * len(t_table_header)
            t_rows = []
            t_simu_year = self.simu_hours//8760 if self.simu_hours>=8760 else 1

            if in_obj_info["class_name"] == "Load":
                t_row[0] = "规模优化"
                t_row[1] = in_obj_info["verbose"]
                t_row[2] = "{:.1f}".format(in_obj.p_nom["value"]/1000.0)
                t_row[3] = "MW"
                t_row[4] = "{:.1f}".format(value(in_obj._param("p_nom"))/1000.0)
                t_row[5] = "MW"
                t_row[6] = "{:.1f}".format(min(in_obj._param_list_values("p_list"))/1000.0)
                t_row[7] = "{:.1f}".format(max(in_obj._param_list_values("p_list"))/1000.0)
                t_row[8] = "MW"
                t_row[9] = "{:.2f}".format(in_obj.get_optimized_kWh_and_hours()[0]/10**8)
                t_row[10] = "亿kWh"
                t_row[11] = "-"
                t_row[12] = "-"
                t_row[13] = "-"
                t_row[14] = "{:.0f}".format(in_obj.get_optimized_kWh_and_hours()[1]/t_simu_year)
                t_rows.append(t_row)

            if in_obj_info["class_name"] == "NE_Plant":
                t_row[0] = "规模优化"
                t_row[1] = in_obj_info["verbose"]
                t_row[2] = "{:.1f}".format(in_obj.p_nom["value"]/1000.0)
                t_row[3] = "MW"
                t_row[4] = "{:.1f}".format(value(in_obj._var("p_nom"))/1000.0)
                t_row[5] = "MW"
                t_row[6] = "{:.1f}".format(min(in_obj._param_list_values("p_list")) * value(in_obj._var("p_nom")) if in_obj.p_nom_extendable==True else min(in_obj._param_list_values("p_list"))/1000.0)
                t_row[7] = "{:.1f}".format(max(in_obj._param_list_values("p_list")) * value(in_obj._var("p_nom")) if in_obj.p_nom_extendable==True else max(in_obj._param_list_values("p_list"))/1000.0)
                t_row[8] = "MW"
                t_row[9] = "{:.2f}".format(in_obj.get_optimized_kWh_and_hours()[0]/10**8)
                t_row[10] = "亿kWh"
                t_row[11] = "{:.1f}".format((value(in_obj._var("p_nom"))-in_obj.p_nom["value"]) * in_obj.capital_cost["value"] / 10000.0 *1000.0  if in_obj.p_nom_extendable==True else 0)
                t_row[12] = "{:.1f}".format(-in_obj.get_cnp_cost())
                t_row[13] = "万元"
                t_row[14] = "{:.0f}".format(in_obj.get_optimized_kWh_and_hours()[1]/t_simu_year)
                t_rows.append(t_row)

            if in_obj_info["class_name"] == "Plant":
                t_row[0] = "规模优化"
                t_row[1] = in_obj_info["verbose"]
                t_row[2] = "{:.1f}".format(in_obj.p_nom["value"]/1000.0)
                t_row[3] = "MW"
                t_row[4] = "{:.1f}".format(value(in_obj._var("p_nom"))/1000.0)
                t_row[5] = "MW"
                t_row[6] = "{:.1f}".format(min(in_obj._var_list_values("p_list"))/1000.0)
                t_row[7] = "{:.1f}".format(max(in_obj._var_list_values("p_list"))/1000.0)
                t_row[8] = "MW"
                t_row[9] = "{:.2f}".format(in_obj.get_optimized_kWh_and_hours()[0]/10**8)
                t_row[10] = "亿kWh"
                t_row[11] = "{:.1f}".format((value(in_obj._var("p_nom"))-in_obj.p_nom["value"]) * in_obj.capital_cost["value"] / 10000.0*1000.0)  #万元
                t_row[12] = "{:.1f}".format(-in_obj.get_cnp_cost())
                t_row[13] = "万元"
                t_row[14] = "{:.0f}".format(in_obj.get_optimized_kWh_and_hours()[1]/t_simu_year)
                t_rows.append(t_row)

            if in_obj_info["class_name"] == "Energy_Storage":
                t_row[0] = "规模优化"
                t_row[1] = in_obj_info["verbose"]+"充"
                t_row[2] = "{:.1f}".format(in_obj.charge.p_nom["value"]/1000.0)
                t_row[3] = "MW"
                t_row[4] = "{:.1f}".format(value(in_obj.charge._var("p_nom"))/1000.0)
                t_row[5] = "MW"
                t_row[6] = "{:.1f}".format(min(in_obj.charge._var_list_values("p_list"))/1000.0)
                t_row[7] = "{:.1f}".format(max(in_obj.charge._var_list_values("p_list"))/1000.0)
                t_row[8] = "MW"
                t_row[9] = "{:.2f}".format(-in_obj.charge.get_optimized_kWh_and_hours()[0]/10**8)
                t_row[10] = "亿kWh"
                t_row[11] = "{:.1f}".format((value(in_obj.charge._var("p_nom"))-in_obj.charge.p_nom["value"]) * in_obj.charge.capital_cost["value"] / 10000.0*1000.0)  #万元
                t_row[12] = "{:.1f}".format(-in_obj.charge.get_cnp_cost())
                t_row[13] = "万元"
                t_row[14] = "{:.0f}".format(in_obj.charge.get_optimized_kWh_and_hours()[1]/t_simu_year)
                t_rows.append(copy.copy(t_row))

                t_row[0] = "规模优化"
                t_row[1] = in_obj_info["verbose"]+"放"
                t_row[2] = "{:.1f}".format(in_obj.discharge.p_nom["value"]/1000.0)
                t_row[3] = "MW"
                t_row[4] = "{:.1f}".format(value(in_obj.discharge._var("p_nom"))/1000.0)
                t_row[5] = "MW"
                t_row[6] = "{:.1f}".format(min(in_obj.discharge._var_list_values("p_list"))/1000.0)
                t_row[7] = "{:.1f}".format(max(in_obj.discharge._var_list_values("p_list"))/1000.0)
                t_row[8] = "MW"
                t_row[9] = "{:.2f}".format(in_obj.discharge.get_optimized_kWh_and_hours()[0]/10**8)
                t_row[10] = "亿kWh"
                t_row[11] = "{:.1f}".format((value(in_obj.discharge._var("p_nom"))-in_obj.discharge.p_nom["value"]) * in_obj.discharge.capital_cost["value"] / 10000.0*1000.0)  #万元
                t_row[12] = "{:.1f}".format(-in_obj.discharge.get_cnp_cost())
                t_row[13] = "万元"
                t_row[14] = "{:.0f}".format(in_obj.discharge.get_optimized_kWh_and_hours()[1]/t_simu_year)
                t_rows.append(copy.copy(t_row))

                t_row[0] = "规模优化"
                t_row[1] = in_obj_info["verbose"]+"E"
                t_row[2] = "{:.1f}".format(in_obj.e_nom["value"]/1000.0)
                t_row[3] = "MWh"
                t_row[4] = "{:.1f}".format(value(in_obj._var("e_nom"))/1000.0)
                t_row[5] = "MWh"
                t_row[6] = "{:.1f}".format(min(in_obj._var_list_values("e_list"))/1000.0)
                t_row[7] = "{:.1f}".format(max(in_obj._var_list_values("e_list"))/1000.0)
                t_row[8] = "MWh"
                t_row[9] = "0" # 暂不考虑贮存损耗
                t_row[10] = "亿kWh"
                t_row[11] = "{:.1f}".format((value(in_obj._var("e_nom"))-in_obj.e_nom["value"]) * in_obj.capital_cost_e["value"] / 10000.0*1000.0)  #万元
                t_row[12] = "-"
                t_row[13] = "万元"
                t_row[14] = "-"
                t_rows.append(copy.copy(t_row))

            if in_obj_info["class_name"] == "Oneway_Link":
                t_row[0] = "规模优化"
                t_row[1] = in_obj_info["verbose"]
                t_row[2] = "{:.1f}".format(in_obj.com0.p_nom["value"]/1000.0)
                t_row[3] = "MW"
                t_row[4] = "{:.1f}".format(value(in_obj.com0._var("p_nom"))/1000.0)
                t_row[5] = "MW"
                t_row[6] = "{:.1f}".format(min(in_obj.com1._var_list_values("p_list"))/1000.0)
                t_row[7] = "{:.1f}".format(max(in_obj.com1._var_list_values("p_list"))/1000.0)
                t_row[8] = "MW"
                t_row[9] = "{:.2f}".format((in_obj.com1.get_optimized_kWh_and_hours()[0]+in_obj.com0.get_optimized_kWh_and_hours()[0])/10**8)
                t_row[10] = "亿kWh"
                t_row[11] = "{:.1f}".format((value(in_obj.com0._var("p_nom"))-in_obj.com0.p_nom["value"]) * in_obj.com0.capital_cost["value"] / 10000.0*1000.0)  #万元
                t_row[12] = "{:.1f}".format(-in_obj.com1.get_cnp_cost()-in_obj.com0.get_cnp_cost())
                t_row[13] = "万元"
                t_row[14] = "{:.0f}".format(in_obj.com1.get_optimized_kWh_and_hours()[1]/t_simu_year)
                t_rows.append(t_row)

            if in_obj_info["class_name"] == "Cogeneration":
                t_row[0] = "规模优化"
                t_row[1] = in_obj_info["verbose"]
                t_row[2] = "{:.1f}".format(in_obj.com0.p_nom["value"]/1000.0)
                t_row[3] = "MW"
                t_row[4] = "{:.1f}".format(value(in_obj.com0._var("p_nom"))/1000.0)
                t_row[5] = "MW"
                t_row[6] = "{:.1f}".format(min(in_obj.com0._var_list_values("p_list"))/1000.0)
                t_row[7] = "{:.1f}".format(max(in_obj.com0._var_list_values("p_list"))/1000.0)
                t_row[8] = "MW"
                t_row[9] = "{:.2f}".format((in_obj.com1.get_optimized_kWh_and_hours()[0]+in_obj.com2.get_optimized_kWh_and_hours()[0]+in_obj.com0.get_optimized_kWh_and_hours()[0])/10**8)
                t_row[10] = "亿kWh"
                t_row[11] = "{:.1f}".format((value(in_obj.com0._var("p_nom"))-in_obj.com0.p_nom["value"]) * in_obj.com0.capital_cost["value"] / 10000.0*1000.0)  #万元
                t_row[12] = "{:.1f}".format(-in_obj.com1.get_cnp_cost()-in_obj.com2.get_cnp_cost()-in_obj.com0.get_cnp_cost())
                t_row[13] = "万元"
                t_row[14] = "{:.0f}".format(in_obj.com0.get_optimized_kWh_and_hours()[1]/t_simu_year)
                t_rows.append( t_row)

            if in_obj_info["class_name"] == "Slack_Node":
                t_row[0] = "规模优化"
                t_row[1] = in_obj_info["verbose"]
                t_row[2] = "{:.1f}".format(in_obj.p_nom["value"]/1000.0)
                t_row[3] = "MW"
                t_row[4] = "{:.1f}".format(value(in_obj._var("p_nom"))/1000.0)
                t_row[5] = "MW"
                t_row[6] = "{:.1f}".format(min(in_obj._var_list_values("p_list"))/1000.0)
                t_row[7] = "{:.1f}".format(max(in_obj._var_list_values("p_list"))/1000.0)
                t_row[8] = "MW"
                t_row[9] = "{:.2f}".format(in_obj.get_optimized_kWh_and_hours()[0]/10**8)
                t_row[10] = "亿kWh"
                t_row[11] = "{:.1f}".format((value(in_obj._var("p_nom"))-in_obj.p_nom["value"]) * in_obj.capital_cost["value"] / 10000.0*1000.0)  #万元
                t_row[12] = "{:.1f}".format(-in_obj.get_cnp_cost())
                t_row[13] = "万元"
                t_row[14] = "{:.0f}".format(in_obj.get_optimized_kWh_and_hours()[1]/t_simu_year)
                t_rows.append(t_row)

            if in_obj_info["class_name"] == "Primary_Energy_Supply":
                t_row[0] = "规模优化"
                t_row[1] = in_obj_info["verbose"]
                t_row[2] = "{:.1f}".format(in_obj.p_nom["value"]/1000.0)
                t_row[3] = "MW"
                t_row[4] = "{:.1f}".format(value(in_obj._var("p_nom"))/1000.0)
                t_row[5] = "MW"
                t_row[6] = "{:.1f}".format(min(in_obj._var_list_values("p_list"))/1000.0)
                t_row[7] = "{:.1f}".format(max(in_obj._var_list_values("p_list"))/1000.0)
                t_row[8] = "MW"
                t_row[9] = "{:.2f}".format(in_obj.get_optimized_kWh_and_hours()[0]/10**8)
                t_row[10] = "亿kWh"
                t_row[11] = "{:.1f}".format((value(in_obj._var("p_nom"))-in_obj.p_nom["value"]) * in_obj.capital_cost["value"] / 10000.0*1000.0)  #万元
                t_row[12] = "{:.1f}".format(-in_obj.get_cnp_cost())
                t_row[13] = "万元"
                t_row[14] = "{:.0f}".format(in_obj.get_optimized_kWh_and_hours()[1]/t_simu_year)
                t_rows.append(t_row)

            for row in t_rows :
                if in_obj_info["class_name"]=="Load" or in_obj_info["class_name"]=="Slack_Node":
                    # 负荷和slack放在表格最上面、表头的下面
                    rtn_table.insert(1, row)
                else:
                    # 其他放在表格下面
                    rtn_table.append(row)
            return

        t_table_header = [
            "数据类型", "项目类型", "存量规模", "单位", "最优规模", "单位", "最小值", "最大值", "单位", "供用能量", "单位", "投资", "成本", "单位", "年小时数(h)"
        ]
        rtn_table.append(t_table_header)
        for obj in self.object_list :
            t_obj_info = get_obj_info(obj)
            if t_obj_info!=0:
                obj_to_table(obj, t_obj_info)

        # 决策变量的变化范围
        # 投资及运行成本汇总
        # 其他值（目标函数值、折现率等）
        t_objs = []
        for o in self.object_list:
            t_objs.append(o.name_id)

        for row in rtn_table:
            print(row)

        print(t_objs)

        # t_table = {
        #     "note":"",
        #     "table":rtn_table
        # }
        return rtn_table

    # ===================生成计算报告、对应的docx文档===================
    def _create_report(self, in_tables=0, in_url='http://localhost:18001'):
        t_fnames = self._pic_file_name_list     # 所有输出的图片名称
        t_docx_filename = "投资优化"
        t_content = [
            "本项目处于规划或前期阶段，旨在通过全生命周期的投资优化定量计算，明确项目所需建设的各类能源电力设施的最佳建设规模和生命周期内的最优出力水平。\n报告所提投资优化分析适用于新型电力系统、综合能源项目、微电网项目以及传统电力系统项目，具体支持冷热电气各类机组和设备模型，负荷类型支持城市类型、工业类型等，优化目标支持社会效益最大和财务效益最佳等。计算中已经内置了8760h负荷特性、新能源出力特性已经分时电价等信息。\n投资优化定量计算分析的优势主要体现于能够精确计算涉及以下难点的场景：\n1）支持全生命周期及8760h的分析。实际上投资优化分析必须通过8760h以上的时间颗粒度进行计算，通盘考虑全生命周期内每一个小时的负荷和新能源特性，将负荷和出力时间序列背后隐含的统计特性完整的反应在项目分析中，才能明确传统峰腰谷断面分析中无法明确的动态因素。\n2）支持新能源、蓄能体系、多能联供、能源转换等设施。传统峰腰谷断面分析的核心是在全生命周期内抽取系统最恶劣运行工况，校核能源电力系统的功率和能量平衡水平，进一步可通过机组组合或生产模拟的分析手段优化和校核系统运行方式。然而前者无法考虑蓄能能量的时间依赖性和机组爬坡能力、出力水平限制等因素；后者能够以8760h的方式精确计算最优出力组合，却无法明确最优建设规模和投资水平，即初始投资成本和生命周期内运行成本的优化没有做到闭环优化。以上问题决定了新能源大规模接入电力系统，综合能源项目、分布式冷热电项目和微电网项目快速发展的背景下，宏观的能源发展路线分析、能源规划分析，中观的区域能源电力系统、综合能源系统规划分析，以及微观的源网荷储一体化项目和多能互补一体化项目的立项分析，都遇到了分析手段严重不足的问题。而本报告能够较为有效的解决上述问题。\n3）定量计算结果的决策支持应用。报告计算结果具有广泛的适用性，最优建设规模信息能够为能源发展路线分析、能源电力规划分析提供最优终端用能结构、一次及二次能源供能结构等方面的决策信息，为产业规划提供转型相关的有效参考；能够为能源电力系统、综合能源系统项目的优化规划提供建设规模、造价、成本方面的决策信息；能够为源网荷储一体化项目、多能互补一体化项目、用户侧项目、微电网项目等提供基于社会效益和财务效益最优的定量结论，且能对项目建成后的日内运行优化提供有效的方式参考。",
            "报告根据所在项目的负荷特性和供用能设施的建设边界，对新能源、冷热电气发供用设备、蓄能和调节等各类设备的存量和增量进行优化计算，通过给定的社会效益最优或财务效益最优目标函数，采用线性规划或非线性规划等效结果，给出数学最优结论，如有需要，可以通过边界的灵敏度分析排查项目的最优建设空间。",
            "目前报告投资优化目标函数主要包括以下两类：\n1）各类设施的初期投资以及运营期内运行成本总和最小（线性目标）。\n2）各类设施的全生命周期财务投资收益率最大（非线性目标）。",
            "随着新能源的大规模接入，电力系统面临着快速调节设施kW造价成本和蓄能类设施kWh造价成本的优化问题，与转移支付及发电价格和用电价格无关，仅与燃料价格、抽蓄的kW成本和kWh成本、新型储能的kW成本和kWh成本、氢能体系的kW成本和kWh成本等外部影子成本相关。\n上述kW成本和kWh成本的投资优化问题，是典型的线性规划问题或者整数混合线性规划问题，其难度主要在于新能源出力特性和负荷特性数据的获取、各类设施的相对造价获取、决策变量达到数百万以上以及软件工程实施门槛等。",
            "目标函数为新建设施初始投资与所有设施的边际成本之和，其中光伏计及初始投资、柴发利用已有机组不计及初始投资。\n公式主要包括以下内容，其中P_PV为光伏最优额定功率，C_PV为光伏功率单位造价，P_ESS为储能的最优额定kW容量，C_ESSp储能的kW容量单位造价，E_ESS为储能的最优额定kWh容量，C_ESSe储能的kWh容量单位造价，P (t)为发电设施在t时刻的出力功率，C_fuel为发电设施的发电边际成本，i为基准折现率，t为小时时刻数。",
            "约束方程主要包括以下内容：\n1）所有节点的基尔霍夫约束\n2）广义储能系统的能量约束、储能系统效率约束\n3）新能源及负荷的功率特性约束\n4）机组的额定功率约束\n5）机组的出力比例限制约束\n6）所有可控支路/转换设备的方向和效率约束\n以储能系统的约束方程为例，主要包括充放电额定功率约束、额定容量约束、配电容量约束和充放电动作的能量时序约束。\n其中P_cha_optt为储能最优充电功率序列，P_dis_optt为储能最优放电功率序列，P_nom_opt为储能系统最优额定功率，E_optt为储能最优能量序列，E_nom_opt为储能系统最优额定容量。\n其中P_cha_optt为储能最优充电功率序列，P_dis_optt为储能最优放电功率序列，P_nom_opt为储能系统最优额定功率，E_optt为储能最优能量序列，E_nom_opt为储能系统最优额定容量。\n根据目前国内外主流线性规划求解器公开信息，以内点法求解线性规划问题的计算复杂度为O(n^3.5 L^2)，其中n为变量数量、L为输入长度。\n项目若不考虑新能源的规模优化，计算时长通常在0.5h以内；考虑新能源规模优化时，计算时长可能超过为2h。",
            "待补充。（如各类关键设施和设备的存量规模、是否参与规模优化、kW和kWh单位造价、供能边际成本、出力上下限、技术可开发规模等）",
            "待补充。（如计算时长、负荷类型、目标函数类型、松弛节点配置等）\n\n技术经济输入数据详细如下表所示。",
            "新能源数据：已提供内置新能源的8760h出力特性（1MW系统的出力序列）。\n负荷数据：已提供内置的城市类型和工业类型的8760h负荷特性序列。",
            "1）最优建设规模情况\n待补充。\n2）投资估算及综合成本、收益情况\n待补充。\n计算结果详细如下图表所示。",
            "1）蓄能类设施kW最优建设规模的合理性分析\na）待补充。（如是否有同时充放增加新能源消纳水平的情况。）\nb）待补充。（如是否有充电和放电建设规模不同的情况。）\n2）蓄能类设施kWh最优建设规模的合理性分析\na）待补充。（如是否有kWh最优规模远大于kW最优规模的季节性调度情况。）\nb）待补充。（如是否有kW最优规模较大而kWh最优规模接近零的情况。）\n3）新能源设施最优建设规模的合理性分析\na）待补充。（如是否有优化建设规模仅包含光伏或风电的情况。）\nb）待补充。（如是否有新能源最优规模远高于最大负荷的情况。）\n4）综合能源设施最优建设规模的合理性分析\na）待补充。（如是否有天然气联供或锅炉最优建设规模为零的情况。）\nb）待补充。（如是否有最优建设规模仅包括电制冷水机的情况。）\n结果合理性分析表明，报告中各类供用能设施的最优建设规模结论是合理和必要的。",
            "1）项目总体思路。待补充。\n2）项目最优建设规模情况。待补充。\n3）项目投资估算及成本情况。待补充。\n4）项目建设必要性。待补充。\n5）项目建设可行性。待补充。\n6）项目最优目标与原有目标的差异分析。待补充。",
            "1）进一步核实负荷8760h序列及预测水平。\n2）进一步核实供用能设施单位造价现状和发展趋势。\n3）进一步蓄能类设施的kW单位造价和kWh单位造价的合理组成和发展趋势。\n4）待补充。\n5）待补充。",
        ]

        w = Word(
            in_filename=t_docx_filename,
            in_id=self._remote_user_open_id,
            in_domain_name=in_url,
            # in_domain_name="https://www.poweryourlife.cn",
        )
        # sec = w.section_break(in_start_type=WD_SECTION_START.NEW_PAGE, in_rotate=False, in_is_linked_to_previous=False)
        w.add_page_number(in_sec=w.get_current_section(), in_show_total=False)

        w.para("新型电力系统投资优化分析报告", in_style="报告标题", in_center=True, in_indent=False)
        w.heading("一、项目概况", 1)
        w.heading("1、项目诉求", 2).para(t_content[0])
        w.heading("2、报告思路", 2).para(t_content[1])
        w.heading("二、优化目标", 1).para(t_content[2])
        w.heading("三、机理分析", 1)
        w.heading("1、目标函数", 2).para(t_content[3])
        w.heading("2、约束方程", 2).para(t_content[4])
        w.heading("3、计算规模", 2).para(t_content[5])
        w.heading("四、技术经济输入数据", 1)
        w.heading("1、能源设施技术经济输入数据", 2).para(t_content[6])
        w.heading("2、计算方案相关输入数据", 2).para(t_content[7])

        w.section_break(in_rotate=True)
        t_table = self._get_table_for_report_input()
        t_head = t_table.pop(0)
        w.table(
            in_table_head_list=t_head,
            in_table_data_list=t_table,
            in_title="技术经济输入数据汇总表"
        )
        w.section_break(in_rotate=True)

        w.heading("五、8760h输入数据", 1).para(t_content[8])
        w.heading("六、计算结果及合理性分析", 1)
        w.heading("1、计算结果汇总", 2).para(t_content[9])

        w.section_break(in_rotate=True)
        print(self._tables_for_report_output)
        if in_tables!=0 :
            for item in in_tables :
                t_table = item["table"]
                t_head = t_table.pop(0)
                w.table(
                    in_table_head_list=t_head,
                    in_table_data_list=t_table,
                    in_title="投资优化计算结果汇总表"+item["note"]
                )
                w.para("")
        else:
            t_table = self._get_table_for_report_output()
            t_head = t_table.pop(0)
            w.table(
                in_table_head_list=t_head,
                in_table_data_list=t_table,
                in_title="投资优化计算结果汇总表"
            )
            w.para("")
        w.section_break(in_rotate=True)

        for i in t_fnames :
            w.pic(in_filename=i, in_title="最优结果示意图("+i+")", in_width_crop=0.9, in_height_crop=0.85)

        w.heading("2、结果合理性分析", 2).para(t_content[10])
        w.heading("七、结论及建议", 1)
        w.heading("1、初步结论", 2).para(t_content[11])
        w.heading("2、下一步工作建议", 2).para(t_content[12])

        #存盘
        w.save()

        # 返回报告string_list
        self._report_string_list = t_content

        # 返回报告docx的url
        self._report_file_url = w.get_docx_full_url()

        global g_NPV_Work

        print("============== npv:{} ============".format(g_NPV_Work))

        return w.docx_filename

    # def free_model_mem(self):
    #     pass
        # 释放model的内存
        # del self.model
        # gc.collect()

    def cb_sys_add_objfunc(self):
        print("# =======================目标函数===========================")
        # min，目标函数(元)：储能功率造价+储能容量造价
        def func1(model):
            # min，目标函数(元)：储能功率造价+储能容量造价
            expr = 0

            # 社会效益最大（考虑折现率）
            if self.investor == "government" :
                for i in range(len(self.object_list)):
                    expr = expr + self.object_list[i]._add_objective_func_lcc()     # life cycle cost
                return expr

            # 投资收益率最大（暂不考虑折现率）
            if self.investor == "user_finance" :
                # global g_NPV_Work

                # 通过分数规划计算收益率时，暂时关闭NPV计算
                # if self.user_finance_strategy=="max_profit" :
                #     g_NPV_Work = False

                initial_cost_expr = 0

                expr = 0
                for i in range(len(self.object_list)):
                    expr = expr + self.object_list[i]._add_objective_func_lcnp()     # life cycle net profit
                    initial_cost_expr = initial_cost_expr + self.object_list[i]._get_initial_cost_expr()     # 初期投资

                # print("!!!!!!!!!!!!!add cost {}, expr is {}".format(self.object_list[i].name_id, initial_cost_expr))

                # if self.user_finance_strategy=="max_rate" :
                # =======================目标函数为收益率最大，构建g(L)=========================
                # 注意：投资收益率=净收益/初期投资，投资收益率最优问题，为"分数规划问题"，需要通过构建g(L)=min(a*x-L*b*x)函数，并通过二分法查找L并迭代求解使g(L)=0，此时L即为问题最优目标，对应x即为解。
                # 以下为原目标函数 min f(x)=a*x/(b*x)
                # expr = expr / initial_cost_expr
                # 以下为重新构建的g(L)
                expr = expr - self.fp_lambda * initial_cost_expr
                print("fp_lambda is: {}".format(self.fp_lambda))
                # g_NPV_Work = True
                return expr
                # elif self.user_finance_strategy=="max_profit" :
                #     # =======================目标函数为利润最大，直接线性规划，不涉及L=========================
                #     return expr

        self.model.OBJ_FUNC = Objective(rule=func1, sense=minimize)

    def cb_sys_add_param(self):
        # 参数：折现率
        self._to_param("rate", self.rate)

        if self.investor == "user_finance" :
            # 参数：购售电价序列(元/kWh，售电/放电的功率为正）
            # 每个小时的电价（通过目录电价列表tariff_list进行循环连接
            t_price_list = self.tariff_list.copy() #一维的深copy，二维深copy需要用copy.deepcopy()
            t_price_list = list_convolution(t_price_list, self.simu_hours)
            self._to_param("price_list", t_price_list)

    # def cb_sys_add_var(self):
    #     # 变量：新能源弃用发电序列(kW)
    #     self._to_var("p_abandoned_ne_elec_list", in_len=self.simu_hours + 1)   #这里+1是为了防止constraints的index构造时溢出
    #
    # def cb_sys_add_param(self):
    #     # 参数：新能源允许弃用的发电量
    #     self._to_param("total_abandoned_ne_elec", self.total_abandoned_ne_elec)

    # def cb_sys_add_constrait(self):
    #     # --------------------------------------------新能源弃用发电的约束------------------------------------------
    #     def func1(model, i):
    #         expr = self._var("sys1", "p_abandoned_ne_elec_list")[i] >= 0.0
    #         return expr
    #     self._to_cons("p_abandoned_ne_elec_cons_list", func1, in_len=self.simu_hours)
    #
    #     # --------------------------------------------新能源弃用的全年总量约束------------------------------------------
    #     def func2(model):
    #         expr = sum(self._var("sys1", "p_abandoned_ne_elec_list")[i] for i in range(1, self.simu_hours+1)) <= self._param("sys1", "total_abandoned_ne_elec")
    #         return expr
    #     self._to_cons("e_total_abandoned_ne_elec_cons", func2)





