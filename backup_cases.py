# 2021.3.12之前的浙江省储能配置分析参数

def model_init_coupled_energy(self, in_para=0, in_progress_callback_func=0):
    if in_para == 0:
        # ======================================本地调用======================================
        # 负荷初始化
        self._m_load_type = "TOD"
        # self._m_simu_hours = 24
        # self._m_simu_hours = 24*30
        # self._m_simu_hours = 8760
        self._m_simu_hours = 8760 * 5
        # self._m_simu_hours = 8760*10
        # 浙江2025年负荷
        self._m_peak_load_elec = 130000.
        self._m_peak_load_heat = 0.
        self._m_peak_load_cold = 0.

        self._m_logger = Python_User_Logger.get_debug_func()
        self._m_debug = Python_User_Logger.get_id_debug_func()

        self._m_progress = Progress(in_interval_seconds=1, in_est_total_seconds=450 * self._m_simu_hours / 8000)
        self._m_progress.set_progress_callback_func(in_progress_callback_func=in_progress_callback_func)

        # =======调整t_typical_day_elec、in_month_rand_range、in_month_dist，使年负荷利用小时数合理（如5000h）=======
        t_typical_day_elec = 0
        # t_typical_day_elec = [
        #     3300, 3200, 3000, 3000, 3150, 4100,
        #     5150, 5100, 5150, 5150, 5200, 5350,
        #     5400, 4250, 4750, 5150, 5200, 9900,
        #     10900, 9550, 6610, 5200, 4000, 3300
        # ]

        if self._m_load_type == "industry":
            self._m_heat_cold_load_pu = deepcopy(
                Annual_Industry_Heat_Cold_Load(in_month_rand_range=[0.9, 1.0], in_month_dist=0.5,
                                               in_simu_hours=self._m_simu_hours))
            self._m_elec_load_pu = deepcopy(Annual_Industry_Elec_Load(in_month_rand_range=[0.9, 1.0], in_month_dist=0.5,
                                                                      in_simu_hours=self._m_simu_hours))
        else:
            # 其他均采用TOD类型的负荷
            self._m_heat_cold_load_pu = deepcopy(
                Annual_TOD_Heat_Cold_Load(in_month_rand_range=[0.3, 1.0], in_month_dist=0.5,
                                          in_simu_hours=self._m_simu_hours))
            self._m_elec_load_pu = deepcopy(Annual_TOD_Elec_Load(in_month_rand_range=[0.7, 1.0], in_month_dist=0.5,
                                                                 in_simu_hours=self._m_simu_hours,
                                                                 in_typical_day_elec=t_typical_day_elec))
        # =======调整t_typical_day_elec、in_month_rand_range、in_month_dist，使年负荷利用小时数合理（如5000h）=======

        self._m_8760_load_elec = deepcopy(self._m_elec_load_pu.get_simu_hours_elec_load(self._m_peak_load_elec))
        self._m_8760_load_heat = deepcopy(self._m_heat_cold_load_pu.get_simu_hours_heat_load(self._m_peak_load_heat))
        self._m_8760_load_cold = deepcopy(self._m_heat_cold_load_pu.get_simu_hours_cold_load(self._m_peak_load_cold))

        self._m_8760_pv_p_max_pu = deepcopy(
            Annual_PV_output(in_simu_hours=self._m_simu_hours).get_simu_hours_pv_output(in_peak_pv=1.))
        self._m_8760_wind_p_max_pu = deepcopy(
            Annual_wind_output(in_simu_hours=self._m_simu_hours).get_simu_hours_wind_output(in_peak_wind=1.))

        self._m_opt = Coupled_Energy_Sectors_Invest_Opt(in_if_debug=True, in_snapshots=range(self._m_simu_hours))

        # 全局约束
        # 一旦开启CO2约束，可能会导致一些bus_t、generator_t的'p'不输出，因而pypsa报错
        # self._m_opt.add_global_constraint_co2_less_equal_than(in_carrier_attribute="co2_emissions", in_co2_limit=0.)

        # carrier
        self._m_opt.add_nuclear_carrier(in_co2_emissions=0.)
        self._m_opt.add_ac_carrier(in_co2_emissions=0.)
        self._m_opt.add_wind_carrier(in_co2_emissions=0.)
        self._m_opt.add_solar_carrier(in_co2_emissions=0.)
        self._m_opt.add_gas_carrier(in_co2_emissions=0.2)
        self._m_opt.add_heat_carrier(in_co2_emissions=0.)
        self._m_opt.add_coal_carrier(in_co2_emissions=0.3)

        # 电力节点和负荷
        self._m_opt.add_ac_buses()
        self._m_opt.add_ac_loads(in_p_set=self._m_8760_load_elec)

        # 冷热节点和负荷
        # self._m_opt.add_heat_buses()
        # self._m_opt.add_cold_buses()
        # self._m_opt.add_heat_loads(in_p_set=self._m_8760_load_heat)
        # self._m_opt.add_cold_loads(in_p_set=self._m_8760_load_cold)

        # 天然气节点
        # self._m_opt.add_gas_buses()

        # 光伏机组（边际成本取0元/kWh，综合造价4.0元/W）(低压接入3.6，高压接入3.8-4.0，来源于王铖)
        # self._m_opt.add_pv_gens(
        #     in_marginal_cost=0., in_capital_cost=4000, in_efficiency=1.,
        #     in_p_nom_extendable=True, in_p_max_pu=self._m_8760_pv_p_max_pu, in_p_nom_max=2000
        # )
        # 浙江2025年光伏
        # 光伏存量机组
        self._m_opt.add_pv_gens(
            in_nick_name="pv",
            in_efficiency=1.,
            in_p_nom_extendable=False, in_p_max_pu=self._m_8760_pv_p_max_pu, in_p_min_pu=self._m_8760_pv_p_max_pu,
            in_p_nom=17600.
        )

        # 风电机组
        # self._m_opt.add_wind_gens(
        #     in_marginal_cost=0., in_capital_cost=4000, in_efficiency=1.,
        #     in_p_nom_extendable=True, in_p_max_pu=self._m_8760_wind_p_max_pu, in_p_nom_max=2000
        # )
        # 浙江2025年风电
        # 风电存量机组
        self._m_opt.add_wind_gens(
            in_nick_name="wind",
            in_efficiency=1.,
            in_p_nom_extendable=False, in_p_max_pu=self._m_8760_wind_p_max_pu, in_p_min_pu=self._m_8760_wind_p_max_pu,
            in_p_nom=7440.
        )

        # 其他机组（其他零星机组的等效处理，如生物质+水电11000MW、区外送入20000MW、白鹤滩7500MW）
        self._m_opt.add_coal_gens(
            in_nick_name="external_p",
            in_p_nom=31000, in_p_min_pu=0.65,
            in_efficiency=1.0,
            in_ramp_limit_up=0.9, in_ramp_limit_down=1.0,
            in_p_nom_extendable=False
        )

        # 近年来我国电力行业SO2和NOX排放情况如图7和图8所示。本文引用“影子价格”计算SO2和NOX造成的经济损失。联合国把影子价格定义为“一种投入(比如资本、劳动力和外汇)的机会成本或它的供应量减少
        # 一个单位给整个经济带来的损失”。2007年美国国家研究委员会采用剂量——响应模型确定SO2和NOX的影子价格分别为5800美元 / 吨、1600美元 / 吨，按照2007年美元兑人民币汇率换算，即44138元 / 吨、
        # 12176元 / 吨。由中国环境统计年报2007年统计数据可知，电力行业排放SO21099万吨，排放NOX811万吨。由此可计算2007年我国电力行业排放SO2和NOX带来的经济损失分别为4850亿元和987亿元。2007
        # 年我国火力发电总量为2.7万亿千瓦时，可得由燃煤火电排放SO2和NOX引起的环境成本分别为Ce(SO2) = 0.1795元 / 千瓦时，Ce(NOX) = 0.0366元 / 千瓦时。

        # 2008年我国火力发电总量为2.79万亿千瓦时，由此可计算燃煤火电排放CO2带来的环境成本为Ce(CO2) = 0.1865元 / 千瓦时
        # 综合以上数据，2010年由PM2.5造成的燃煤火电环境成本为Ce(PM2.5)=0.1065元 / 千瓦时。

        # 根据中电联的统计，煤电灵活性改造（浙江省已经完成灵活性改造，经济性调峰到40%，极限到30%）单位千瓦调峰容量成本约在500元-1500元，再加上改造后的运维成本、煤耗成本增加，如果没有合理的补偿，企业积极性不足。
        # 而且近年来基层电厂在环保改造投入大量资金，导致其他技术改造项目资金不足。同时，基层企业亏损面大，扭亏减亏任务艰巨，加之调峰补贴力度较小，基层企业改造动力不足。

        # 煤电机组（这里若作为网电，则边际成本取0.15元/kWh，综合造价0元/W；若非网电，则边际成本取0.15元/kWh，综合造价3.2元/W。最小出力pu为0.4）
        # ===固定规模===
        self._m_opt.add_coal_gens(
            in_nick_name="coal",
            # in_p_nom=47000,in_efficiency=0.4,
            in_p_nom=47000, in_p_min_pu=0.4, in_efficiency=0.4,
            in_ramp_limit_up=0.6, in_ramp_limit_down=0.6,
            in_marginal_cost=200.,
            in_p_nom_extendable=False
        )
        # ===可优化规模===
        self._m_opt.add_coal_gens(
            in_nick_name="coal_opt",
            # in_p_nom=0,in_efficiency=0.4,
            in_p_nom=0, in_p_min_pu=0.4, in_efficiency=0.4,
            in_ramp_limit_up=0.6, in_ramp_limit_down=0.6,
            in_marginal_cost=200., in_capital_cost=3200000.,
            in_p_nom_extendable=True
        )

        # 燃机机组（边际成本取0.5元/kWh，综合造价2.2元/W）
        # ===固定规模===
        # ===存量不参与优化===
        # self._m_opt.add_gas_gens(
        #     in_nick_name="gas",
        #     in_p_nom=14590, in_efficiency=0.5,
        #     in_ramp_limit_up=0.9, in_ramp_limit_down=1.0,
        #     in_marginal_cost=600,
        #     in_p_nom_extendable=False
        # )
        # ===存量参与优化===
        self._m_opt.add_gas_gens(
            in_nick_name="gas",
            in_p_nom=14590, in_efficiency=0.5,
            in_marginal_cost=600, in_capital_cost=2200000.,
            in_ramp_limit_up=0.9, in_ramp_limit_down=1.0,
            in_p_nom_extendable=True
        )
        # ===增量参与优化===
        # self._m_opt.add_gas_gens(
        #     in_nick_name="gas_opt",
        #     in_p_nom=0,
        #     in_marginal_cost=600, in_capital_cost=2200000., in_efficiency=0.5,
        #     in_ramp_limit_up=0.9, in_ramp_limit_down=1.0,
        #     in_p_nom_extendable=True
        # )

        # 核电机组（边际成本取0.06元/kWh，综合造价12元/W）
        self._m_opt.add_nuclear_gens(
            in_nick_name="nuclear",
            in_p_nom=13980, in_p_min_pu=1.0,
            in_ramp_limit_up=0.05, in_ramp_limit_down=0.05,
            in_marginal_cost=60., in_capital_cost=12000000, in_efficiency=0.5,
            in_p_nom_extendable=False
        )

        # 蓄电（抽蓄）
        # 目前4*300MW级的电站，一般容量为5-7h电量，2016年的1400MW宁海抽蓄动态79亿元（建设期7-8年，经营期30年），大约5600元/kW，其中机电及金属结构设备安装26%、建筑26%、施工辅助工程+环保水土7%、征地+移民补偿5%、独立费用（建设、设计）15%、预备+价差10%、建设期利息11%。）
        # 因此，取0.46元/Wh、2.80元/W。
        # 综合效率取80%左右，因此充放电效率分别取90%、90%
        # ===固定规模===
        self._m_opt.add_elec_stores(
            # in_nick_name="pumped_hydro",
            in_nick_name="PSP",
            in_effi=0.81,
            in_p_nom_in=8680, in_p_nom_out=8680, in_e_nom=8680 * 6, in_e_cyclic=True, in_e_nom_extendable=False,
            in_p_nom_extendable=False)
        # ===可优化规模===
        self._m_opt.add_elec_stores(
            in_nick_name="PSP_opt",
            in_effi=0.81,
            in_p_nom_in=0, in_p_nom_out=0, in_e_nom=0,
            in_mwh_capital_cost=460000., in_mw_capital_cost=2800000., in_e_cyclic=True, in_e_nom_extendable=True,
            in_p_nom_extendable=True)

        # 蓄电（电池储能）
        # 目前大型储能电站，2020年的萧电储能系统100MW*2h
        # 静态投资约5.86亿元（经营期15年），储能单元及安装54.0%、特殊项目费用（第一期和第二期的电池更换）19.4%、PCS系统11.15%（由于是考虑功率成本，因此含PCS 5.27%、主变1.24%（220kV主变可能不计列钱，即仅计及35kV变压器）、配电4.64%）、其他设施和工程（控制保护2%、电缆接地3%、集装箱基础1%、其他6%）12%，其他费用2%、预备费2%
        # 动态投资约5.46亿元，其中第一期和第二期电池更换费用折现共计-0.48亿元。
        # 因此，按电池和pcs的造价比例73.4:11.15，取2.54元/Wh、0.38元/W。（注意：如果考虑储能生命周期过短，可以把电池储能的Wh和W成本提高一倍或一定倍数考虑）
        # 注：计算中，按照2025年水平，价格均按50%计，取1.38元/Wh、0.24元/W（本项目不计220kV主变，后续项目最好考虑110kV及以下接入或220主变免费，即kW造价按0.4-0.5元/W左右（含pcs、35kV升压变、配电、110kV升压变，比较合理）
        # 综合效率取90%左右，因此充放电效率分别取95%、95%
        # ===可优化规模===（注意额定容量必须为0，因为目标函数中仅计算增量容量对应的投资增量，即总投资会减去额定容量对应的投资）
        self._m_opt.add_elec_stores(
            in_nick_name="BES_opt",
            in_effi=0.9025,
            in_p_nom_in=0, in_p_nom_out=0, in_e_nom=0,
            # in_mwh_capital_cost=2730000., in_mw_capital_cost=200000., in_e_cyclic=True, in_e_nom_extendable=True, in_p_nom_extendable=True)
            in_mwh_capital_cost=1380000., in_mw_capital_cost=240000., in_e_cyclic=True, in_e_nom_extendable=True,
            in_p_nom_extendable=True)

        # CHP机组(天然气内燃机CHP，边际成本取1.0元/kWh，设备造价3.5元/W左右)
        # self._m_opt.add_chp_gens(
        #     in_nom_r=1., in_c_v=0.15, in_c_m=0.75,
        #     in_boiler_marginal_cost=0.5, in_boiler_capital_cost=1500, in_absorber_heat_efficiency=1., in_absorber_cold_efficiency=1.,
        #     in_gen_marginal_cost=0.5, in_gen_capital_cost=2000, in_gen_efficiency=0.45,
        #     in_p_nom_extendable=True
        # )

        # 锅炉（边际成本取0.3元/kWh，设备造价0.2元/W左右）
        # self._m_opt.add_boiler_gens(
        #     in_marginal_cost=0.3, in_capital_cost=200, in_efficiency=1., in_p_nom_extendable=True
        # )

        # 电冷水机（边际成本取0.3元/kWh，设备造价0.2元/W左右）
        # self._m_opt.add_ac_coolers(in_marginal_cost=0.3, in_capital_cost=500, in_efficiency=3.0, in_p_nom_extendable=True)

        # 热泵（边际成本取0.3元/kWh，设备造价1元/W左右）
        # self._m_opt.add_heat_pumps(
        #     in_marginal_cost=0.3, in_capital_cost=1000, in_heat_efficiency=2.5, in_p_nom_extendable=True,
        #     in_cold_efficiency=3.0
        # )

        # 天然气存储
        # self._m_opt.add_gas_stores(in_mwh_capital_cost=200, in_mw_capital_cost=0., in_e_cyclic=True, in_e_nom_extendable=True, in_p_nom_extendable=True)

        # 蓄热（设备造价取0.2元/Wh）
        # self._m_opt.add_heat_stores(in_mwh_capital_cost=20, in_mw_capital_cost=0., in_e_cyclic=True, in_e_nom_extendable=True, in_p_nom_extendable=True)
        # self._m_opt.add_heat_stores(in_mwh_capital_cost=200, in_mw_capital_cost=0., in_e_cyclic=True, in_e_nom_extendable=True, in_p_nom_extendable=True)

        # 冰蓄冷（设备造价取0.2元/Wh）
        # self._m_opt.add_cold_stores(in_mwh_capital_cost=20, in_mw_capital_cost=0., in_e_cyclic=True, in_e_nom_extendable=True, in_p_nom_extendable=True)
        # self._m_opt.add_cold_stores(in_mwh_capital_cost=200, in_mw_capital_cost=0., in_e_cyclic=True, in_e_nom_extendable=True, in_p_nom_extendable=True)

        # P2G（gas）
        # opt.add_power_to_gases(in_efficiency=0., in_p_nom_extendable=True)

    # ======================================远程client调用======================================


# 2021.6.30之前的浙江省储能配置分析参数
def model_init_coupled_energy(self, in_para=0, in_progress_callback_func=0):
        if in_para==0:
            # ======================================本地调用======================================
            # 负荷初始化
            self._m_load_type = "TOD"
            self._m_simu_hours = 24
            # self._m_simu_hours = 24*30
            # self._m_simu_hours = 8760
            # self._m_simu_hours = 8760*5
            # self._m_simu_hours = 8760*10
            # 浙江2025年负荷
            self._m_peak_load_elec = 124300.
            self._m_peak_load_heat = 0.
            self._m_peak_load_cold = 0.


            self._m_logger = Python_User_Logger.get_debug_func()
            self._m_debug = Python_User_Logger.get_id_debug_func()

            self._m_progress = Progress(in_interval_seconds=1, in_est_total_seconds=450 * self._m_simu_hours / 8000)
            self._m_progress.set_progress_callback_func(in_progress_callback_func=in_progress_callback_func)


            # =======调整t_typical_day_elec、in_month_rand_range、in_month_dist，使年负荷利用小时数合理（如5000h）=======
            t_typical_day_elec = 0
            # t_typical_day_elec = [
            #     3300, 3200, 3000, 3000, 3150, 4100,
            #     5150, 5100, 5150, 5150, 5200, 5350,
            #     5400, 4250, 4750, 5150, 5200, 9900,
            #     10900, 9550, 6610, 5200, 4000, 3300
            # ]

            if self._m_load_type == "industry":
                self._m_heat_cold_load_pu = deepcopy(Annual_Industry_Heat_Cold_Load(in_month_rand_range=[0.9, 1.0], in_month_dist=0.5, in_simu_hours=self._m_simu_hours))
                self._m_elec_load_pu = deepcopy(Annual_Industry_Elec_Load(in_month_rand_range=[0.9, 1.0], in_month_dist=0.5, in_simu_hours=self._m_simu_hours))
            else:
                # 其他均采用TOD类型的负荷
                self._m_heat_cold_load_pu = deepcopy(Annual_TOD_Heat_Cold_Load(in_month_rand_range=[0.3, 1.0], in_month_dist=0.5, in_simu_hours=self._m_simu_hours))
                self._m_elec_load_pu = deepcopy(Annual_TOD_Elec_Load(in_month_rand_range=[0.7, 1.0], in_month_dist=0.5, in_simu_hours=self._m_simu_hours, in_typical_day_elec=t_typical_day_elec))
            # =======调整t_typical_day_elec、in_month_rand_range、in_month_dist，使年负荷利用小时数合理（如5000h）=======

            self._m_8760_load_elec = deepcopy(self._m_elec_load_pu.get_simu_hours_elec_load(self._m_peak_load_elec))
            self._m_8760_load_heat = deepcopy(self._m_heat_cold_load_pu.get_simu_hours_heat_load(self._m_peak_load_heat))
            self._m_8760_load_cold = deepcopy(self._m_heat_cold_load_pu.get_simu_hours_cold_load(self._m_peak_load_cold))

            self._m_8760_pv_p_max_pu = deepcopy(Annual_PV_output(in_simu_hours=self._m_simu_hours).get_simu_hours_pv_output(in_peak_pv=1.))
            self._m_8760_wind_p_max_pu = deepcopy(Annual_wind_output(in_simu_hours=self._m_simu_hours).get_simu_hours_wind_output(in_peak_wind=1.))

            self._m_opt = Coupled_Energy_Sectors_Invest_Opt(in_if_debug=True, in_snapshots=range(self._m_simu_hours))

            # 全局约束
            # 一旦开启CO2约束，可能会导致一些bus_t、generator_t的'p'不输出，因而pypsa报错
            # self._m_opt.add_global_constraint_co2_less_equal_than(in_carrier_attribute="co2_emissions", in_co2_limit=0.)

            # carrier
            self._m_opt.add_nuclear_carrier(in_co2_emissions=0.)
            self._m_opt.add_ac_carrier(in_co2_emissions=0.)
            self._m_opt.add_wind_carrier(in_co2_emissions=0.)
            self._m_opt.add_solar_carrier(in_co2_emissions=0.)
            self._m_opt.add_gas_carrier(in_co2_emissions=0.2)
            self._m_opt.add_heat_carrier(in_co2_emissions=0.)
            self._m_opt.add_coal_carrier(in_co2_emissions=0.3)

            # 电力节点和负荷
            self._m_opt.add_ac_buses()
            self._m_opt.add_ac_loads(in_p_set=self._m_8760_load_elec)

            # 冷热节点和负荷
            # self._m_opt.add_heat_buses()
            # self._m_opt.add_cold_buses()
            # self._m_opt.add_heat_loads(in_p_set=self._m_8760_load_heat)
            # self._m_opt.add_cold_loads(in_p_set=self._m_8760_load_cold)

            # 天然气节点
            # self._m_opt.add_gas_buses()

            # 光伏机组（边际成本取0元/kWh，综合造价4.0元/W）(低压接入3.6，高压接入3.8-4.0，来源于王铖)
            # self._m_opt.add_pv_gens(
            #     in_marginal_cost=0., in_capital_cost=4000, in_efficiency=1.,
            #     in_p_nom_extendable=True, in_p_max_pu=self._m_8760_pv_p_max_pu, in_p_nom_max=2000
            # )
            # 浙江2025年光伏
            # 光伏存量机组
            self._m_opt.add_pv_gens(
                in_nick_name="pv",
                in_efficiency=1.,
                in_p_nom_extendable=False, in_p_max_pu=self._m_8760_pv_p_max_pu, in_p_min_pu=self._m_8760_pv_p_max_pu, in_p_nom=27500.
            )

            # 风电机组
            # self._m_opt.add_wind_gens(
            #     in_marginal_cost=0., in_capital_cost=4000, in_efficiency=1.,
            #     in_p_nom_extendable=True, in_p_max_pu=self._m_8760_wind_p_max_pu, in_p_nom_max=2000
            # )
            # 浙江2025年风电
            # 风电存量机组
            self._m_opt.add_wind_gens(
                in_nick_name="wind",
                in_efficiency=1.,
                in_p_nom_extendable=False, in_p_max_pu=self._m_8760_wind_p_max_pu, in_p_min_pu=self._m_8760_wind_p_max_pu, in_p_nom=6410.
            )

            # ===========生物质、水电、外来电小时数对于抽蓄优化结果影响非常大！！！===========
            # 其他机组（其他机组的等效处理，如生物质2500MW+水电7150MW、区外送入40190MW），溪洛渡水电为0.3元/kWh，省内水电为0.4-0.5，边际成本应接近0
            self._m_opt.add_coal_gens(
                in_nick_name="external_p",
                in_p_nom=49840,
                in_p_min_pu=0.30,       #浙江外来电小时数约4500-4800,这里通过调p_min_pu拟合小时数到4500-4800
                in_efficiency=1.0,
                in_ramp_limit_up=0.9, in_ramp_limit_down=1.0,
                in_marginal_cost=0.,
                in_p_nom_extendable=False
            )

            # 近年来我国电力行业SO2和NOX排放情况如图7和图8所示。本文引用“影子价格”计算SO2和NOX造成的经济损失。联合国把影子价格定义为“一种投入(比如资本、劳动力和外汇)的机会成本或它的供应量减少
            # 一个单位给整个经济带来的损失”。2007年美国国家研究委员会采用剂量——响应模型确定SO2和NOX的影子价格分别为5800美元 / 吨、1600美元 / 吨，按照2007年美元兑人民币汇率换算，即44138元 / 吨、
            # 12176元 / 吨。由中国环境统计年报2007年统计数据可知，电力行业排放SO21099万吨，排放NOX811万吨。由此可计算2007年我国电力行业排放SO2和NOX带来的经济损失分别为4850亿元和987亿元。2007
            # 年我国火力发电总量为2.7万亿千瓦时，可得由燃煤火电排放SO2和NOX引起的环境成本分别为Ce(SO2) = 0.1795元 / 千瓦时，Ce(NOX) = 0.0366元 / 千瓦时。

            # 2008年我国火力发电总量为2.79万亿千瓦时，由此可计算燃煤火电排放CO2带来的环境成本为Ce(CO2) = 0.1865元 / 千瓦时
            # 综合以上数据，2010年由PM2.5造成的燃煤火电环境成本为Ce(PM2.5)=0.1065元 / 千瓦时。

            # 根据中电联的统计，煤电灵活性改造（浙江省已经完成灵活性改造，经济性调峰到40%，极限到30%）单位千瓦调峰容量成本约在500元-1500元，再加上改造后的运维成本、煤耗成本增加，如果没有合理的补偿，企业积极性不足。
            # 而且近年来基层电厂在环保改造投入大量资金，导致其他技术改造项目资金不足。同时，基层企业亏损面大，扭亏减亏任务艰巨，加之调峰补贴力度较小，基层企业改造动力不足。

            # 煤电机组（这里若作为网电，则边际成本取0.15元/kWh，综合造价0元/W；若非网电，浙江上网电价0.3746元/kWh，综合造价3.2元/W。最小出力pu为0.4）
            # ===固定规模=== 火电51380MW+油电20MW+余热余压1310MW
            self._m_opt.add_coal_gens(
                in_nick_name="coal",
                # in_p_nom=47000,in_efficiency=0.4,
                in_p_nom=52720,
                in_p_min_pu=0.4,
                in_efficiency=0.4,
                in_ramp_limit_up=0.6, in_ramp_limit_down=0.6,
                in_marginal_cost=200.,  #浙江火电小时数约5300h，上网电价0.378，边际成本考虑0.2
                in_p_nom_extendable=False
            )
            # ===可优化规模===
            # self._m_opt.add_coal_gens(
            #     in_nick_name="coal_opt",
            #     # in_p_nom=0,in_efficiency=0.4,
            #     in_p_nom=0, in_p_min_pu=0.4, in_efficiency=0.4,
            #     in_ramp_limit_up=0.6, in_ramp_limit_down=0.6,
            #     in_marginal_cost=200., in_capital_cost=3200000.,
            #     in_p_nom_extendable=True
            # )


            # 燃机机组（上网电价0.6，边际成本考虑0.3，综合造价2.2元/W）
            # ===固定规模===
            # ===存量不参与优化===
            self._m_opt.add_gas_gens(
                in_nick_name="gas",
                in_p_nom=14960, in_efficiency=0.5,
                in_p_min_pu=0.0,
                in_ramp_limit_up=0.9, in_ramp_limit_down=1.0,
                in_marginal_cost=300,   #浙江气电小时数为2000h，这里考虑动边际成本以拟合2000h
                in_p_nom_extendable=False
            )
            # ===存量参与优化=== 仅考虑145统调考虑新增的2400MW
            # self._m_opt.add_gas_gens(
            #     in_nick_name="gas",
            #     in_p_nom=14960, in_efficiency=0.5,
            #     in_p_min_pu = 0.0,
            #     in_marginal_cost=600, in_capital_cost=2200000.,
            #     in_ramp_limit_up=0.9, in_ramp_limit_down=1.0,
            #     in_p_nom_extendable=True
            # )
            # ===增量参与优化===
            self._m_opt.add_gas_gens(
                in_nick_name="gas_opt",
                in_p_nom=0,
                in_p_min_pu=0.0,
                in_marginal_cost=300,    #浙江气电小时数为2000h，这里考虑动边际成本以拟合2000h
                in_capital_cost=2200000., in_efficiency=0.5,
                in_ramp_limit_up=0.9, in_ramp_limit_down=1.0,
                in_p_nom_extendable=True
            )

            # ===========核电小时数对于抽蓄优化结果影响非常大！！！===========
            # 核电机组（浙江上网电价为0.4，边际成考虑接近0，综合造价12元/W）
            self._m_opt.add_nuclear_gens(
                in_nick_name="nuclear",
                in_p_nom=11510,
                in_p_min_pu=1.00,    #浙江核电小时数为7800h，这里可以降一点p_min_pu
                in_ramp_limit_up=0.05, in_ramp_limit_down=0.05,
                in_marginal_cost=60., in_capital_cost=12000000, in_efficiency=0.5,
                in_p_nom_extendable=False
            )

            # 蓄电（抽蓄）
            # 目前4*300MW级的电站，一般容量为5-7h电量，2016年的1400MW宁海抽蓄动态79亿元（建设期7-8年，经营期30年），大约5600元/kW，其中机电及金属结构设备安装26%、建筑26%、施工辅助工程+环保水土7%、征地+移民补偿5%、独立费用（建设、设计）15%、预备+价差10%、建设期利息11%。）
            # 因此，取0.46元/Wh、2.80元/W。
            # 综合效率取80%左右，因此充放电效率分别取90%、90%
            # ===固定规模=== 仅考虑2021和2022长龙山新增的2100MW
            # 浙江抽蓄小时数为1300h
            self._m_opt.add_elec_stores(
                # in_nick_name="pumped_hydro",
                in_nick_name="PSP",
                in_effi=0.81,
                in_p_nom_in=6680, in_p_nom_out=6680,  in_e_nom=6680*4, in_e_cyclic=True, in_e_nom_extendable=False, in_p_nom_extendable=False)
            # ===可优化规模===
            self._m_opt.add_elec_stores(
                in_nick_name="PSP_opt",
                in_effi=0.81,
                in_p_nom_in=0, in_p_nom_out=0,  in_e_nom=0,
                in_mwh_capital_cost=460000., in_mw_capital_cost=2800000., in_e_cyclic=True, in_e_nom_extendable=True, in_p_nom_extendable=True)

            # 蓄电（电池储能）
            # 目前大型储能电站，2020年的萧电储能系统100MW*2h
            # 静态投资约5.86亿元（经营期15年），储能单元及安装54.0%、特殊项目费用（第一期和第二期的电池更换）19.4%、PCS系统11.15%（由于是考虑功率成本，因此含PCS 5.27%、主变1.24%（220kV主变可能不计列钱，即仅计及35kV变压器）、配电4.64%）、其他设施和工程（控制保护2%、电缆接地3%、集装箱基础1%、其他6%）12%，其他费用2%、预备费2%
            # 动态投资约5.46亿元，其中第一期和第二期电池更换费用折现共计-0.48亿元。
            # 因此，按电池和pcs的造价比例73.4:11.15，取2.54元/Wh、0.38元/W。（注意：如果考虑储能生命周期过短，可以把电池储能的Wh和W成本提高一倍或一定倍数考虑）
            # 注：计算中，按照2025年水平，价格均按50%计，取1.38元/Wh、0.24元/W（本项目不计220kV主变，后续项目最好考虑110kV及以下接入或220主变免费，即kW造价按0.4-0.5元/W左右（含pcs、35kV升压变、配电、110kV升压变，比较合理）
            # 综合效率取90%左右，因此充放电效率分别取95%、95%
            # ===可优化规模===（注意额定容量必须为0，因为目标函数中仅计算增量容量对应的投资增量，即总投资会减去额定容量对应的投资）
            self._m_opt.add_elec_stores(
                in_nick_name="BES_opt",
                in_effi=0.9025,
                in_p_nom_in=0, in_p_nom_out=0,  in_e_nom=0,
                # in_mwh_capital_cost=1380000., in_mw_capital_cost=240000., in_e_cyclic=True, in_e_nom_extendable=True, in_p_nom_extendable=True)
                in_mwh_capital_cost=850000., in_mw_capital_cost=240000., in_e_cyclic=True, in_e_nom_extendable=True, in_p_nom_extendable=True)

            # CHP机组(天然气内燃机CHP，边际成本取1.0元/kWh，设备造价3.5元/W左右)
            # self._m_opt.add_chp_gens(
            #     in_nom_r=1., in_c_v=0.15, in_c_m=0.75,
            #     in_boiler_marginal_cost=0.5, in_boiler_capital_cost=1500, in_absorber_heat_efficiency=1., in_absorber_cold_efficiency=1.,
            #     in_gen_marginal_cost=0.5, in_gen_capital_cost=2000, in_gen_efficiency=0.45,
            #     in_p_nom_extendable=True
            # )

            # 锅炉（边际成本取0.3元/kWh，设备造价0.2元/W左右）
            # self._m_opt.add_boiler_gens(
            #     in_marginal_cost=0.3, in_capital_cost=200, in_efficiency=1., in_p_nom_extendable=True
            # )

            # 电冷水机（边际成本取0.3元/kWh，设备造价0.2元/W左右）
            # self._m_opt.add_ac_coolers(in_marginal_cost=0.3, in_capital_cost=500, in_efficiency=3.0, in_p_nom_extendable=True)

            # 热泵（边际成本取0.3元/kWh，设备造价1元/W左右）
            # self._m_opt.add_heat_pumps(
            #     in_marginal_cost=0.3, in_capital_cost=1000, in_heat_efficiency=2.5, in_p_nom_extendable=True,
            #     in_cold_efficiency=3.0
            # )

            # 天然气存储
            # self._m_opt.add_gas_stores(in_mwh_capital_cost=200, in_mw_capital_cost=0., in_e_cyclic=True, in_e_nom_extendable=True, in_p_nom_extendable=True)

            # 蓄热（设备造价取0.2元/Wh）
            # self._m_opt.add_heat_stores(in_mwh_capital_cost=20, in_mw_capital_cost=0., in_e_cyclic=True, in_e_nom_extendable=True, in_p_nom_extendable=True)
            # self._m_opt.add_heat_stores(in_mwh_capital_cost=200, in_mw_capital_cost=0., in_e_cyclic=True, in_e_nom_extendable=True, in_p_nom_extendable=True)

            # 冰蓄冷（设备造价取0.2元/Wh）
            # self._m_opt.add_cold_stores(in_mwh_capital_cost=20, in_mw_capital_cost=0., in_e_cyclic=True, in_e_nom_extendable=True, in_p_nom_extendable=True)
            # self._m_opt.add_cold_stores(in_mwh_capital_cost=200, in_mw_capital_cost=0., in_e_cyclic=True, in_e_nom_extendable=True, in_p_nom_extendable=True)

            # P2G（gas）
            # opt.add_power_to_gases(in_efficiency=0., in_p_nom_extendable=True)

        # ======================================远程client调用======================================
        else:
            self._m_logger = Python_User_Logger.get_debug_func()
            self._m_debug = Python_User_Logger.get_id_debug_func()

            # 负荷初始化
            self._m_load_type = in_para['load_type']
            self._m_simu_hours = in_para['simu_hours']
            self._m_solver_name = in_para['solver_name']

            self._m_progress = Progress(in_interval_seconds=1, in_est_total_seconds=450 * self._m_simu_hours / 8000)
            self._m_progress.set_progress_callback_func(in_progress_callback_func=in_progress_callback_func)

            self._m_peak_load_elec = in_para['load_p_max_ac']
            self._m_peak_load_heat = in_para['load_p_max_heat']
            self._m_peak_load_cold = in_para['load_p_max_cold']

            if self._m_load_type == "industry":
                self._m_heat_cold_load_pu = Annual_Industry_Heat_Cold_Load(in_month_rand_range=[0.9, 1.0], in_month_dist=0.5, in_simu_hours=self._m_simu_hours)
                self._m_elec_load_pu = Annual_Industry_Elec_Load(in_month_rand_range=[0.9, 1.0], in_month_dist=0.5, in_simu_hours=self._m_simu_hours)
            else:
                # 其他均采用TOD类型的负荷
                self._m_heat_cold_load_pu = Annual_TOD_Heat_Cold_Load(in_month_rand_range=[0.3, 1.0], in_month_dist=0.5, in_simu_hours=self._m_simu_hours)
                self._m_elec_load_pu = Annual_TOD_Elec_Load(in_month_rand_range=[0.3, 1.0], in_month_dist=0.5, in_simu_hours=self._m_simu_hours)

            self._m_8760_load_elec = deepcopy(self._m_elec_load_pu.get_simu_hours_elec_load(self._m_peak_load_elec))
            self._m_8760_load_heat = deepcopy(self._m_heat_cold_load_pu.get_simu_hours_heat_load(self._m_peak_load_heat))
            self._m_8760_load_cold = deepcopy(self._m_heat_cold_load_pu.get_simu_hours_cold_load(self._m_peak_load_cold))
            self._m_8760_pv_p_max_pu = Annual_PV_output(in_simu_hours=self._m_simu_hours).get_simu_hours_pv_output(in_peak_pv=1.)
            self._m_8760_wind_p_max_pu = Annual_wind_output(in_simu_hours=self._m_simu_hours).get_simu_hours_wind_output(in_peak_wind=1.)

            self._m_opt = Coupled_Energy_Sectors_Invest_Opt(in_if_debug=True, in_snapshots=range(self._m_simu_hours))

            # 全局约束
            # 一旦开启CO2约束，可能会导致一些bus_t、generator_t的'p'不输出，因而pypsa报错
            if in_para["carrier_global_constraint"] == True:
                t_debug("co2 limit is {} tons.".format(in_para["co2_limit"]))
                self._m_opt.add_global_constraint_co2_less_equal_than(in_carrier_attribute="co2_emissions", in_co2_limit=in_para["co2_limit"])

            # carrier（co2_emissions: tonnes/MWh）
            self._m_opt.add_nuclear_carrier(in_co2_emissions=0.)
            self._m_opt.add_ac_carrier(in_co2_emissions=0.)
            self._m_opt.add_wind_carrier(in_co2_emissions=0.)
            self._m_opt.add_solar_carrier(in_co2_emissions=0.)
            self._m_opt.add_gas_carrier(in_co2_emissions=in_para["carrier_gas_co2"])
            self._m_opt.add_heat_carrier(in_co2_emissions=0.)
            self._m_opt.add_coal_carrier(in_co2_emissions=in_para["carrier_coal_co2"])

            # 电力节点和负荷
            self._m_opt.add_ac_buses()
            self._m_opt.add_ac_loads(in_p_set=self._m_8760_load_elec)

            # 冷热节点和负荷
            self._m_opt.add_heat_buses()
            self._m_opt.add_cold_buses()
            self._m_opt.add_heat_loads(in_p_set=self._m_8760_load_heat)
            self._m_opt.add_cold_loads(in_p_set=self._m_8760_load_cold)

            # 天然气节点
            self._m_opt.add_gas_buses()

            # 风电机组（边际成本取0元/kWh，综合造价5.0元/W）
            self._m_opt.add_wind_gens(in_marginal_cost=in_para["res_wind_gen_mc"],
                                    in_capital_cost=in_para["res_wind_gen_cc"],
                                    in_efficiency=in_para["res_wind_gen_effi"],
                                    in_p_nom_extendable=in_para["res_wind_gen_p_nom_extendable"],
                                    in_p_max_pu=self._m_8760_wind_p_max_pu,
                                    in_p_nom_max=in_para["res_wind_gen_p_nom_max"]   )

            # 光伏机组（边际成本取0元/kWh，综合造价4.0元/W）(低压接入3.6，高压接入3.8-4.0，来源于王铖)
            self._m_opt.add_pv_gens(in_marginal_cost=in_para["res_pv_gen_mc"],
                                    in_capital_cost=in_para["res_pv_gen_cc"],
                                    in_efficiency=in_para["res_pv_gen_effi"],
                                    in_p_nom_extendable=in_para["res_pv_gen_p_nom_extendable"],
                                    in_p_max_pu=self._m_8760_pv_p_max_pu,
                                    in_p_nom_max=in_para["res_pv_gen_p_nom_max"])

            # t_debug("pv_p_max_pu is : "+self._m_8760_pv_p_max_pu)

            # 煤电机组（这里即为网电，边际成本取0.15元/kWh，综合造价0元/W）
            self._m_opt.add_coal_gens(
                in_marginal_cost=in_para["res_coal_gen_mc"], in_capital_cost=in_para["res_coal_gen_cc"], in_efficiency=in_para["res_coal_gen_effi"],
                in_p_nom_extendable=in_para["res_coal_gen_p_nom_extendable"]
            )

            # CHP机组(天然气内燃机CHP，边际成本取1.0元/kWh，设备造价3.5元/W左右)
            self._m_opt.add_chp_gens(
                in_nom_r=in_para["res_chp_gen_nom_r"], in_c_v=in_para["res_chp_gen_c_v"], in_c_m=in_para["res_chp_gen_c_m"],
                in_boiler_marginal_cost=in_para["res_chp_gen_boiler_mc"], in_boiler_capital_cost=in_para["res_chp_gen_boiler_cc"],
                in_absorber_heat_efficiency=in_para["res_chp_gen_absorber_heat_effi"], in_absorber_cold_efficiency=in_para["res_chp_gen_absorber_cold_effi"],
                in_gen_marginal_cost=in_para["res_chp_gen_gen_mc"], in_gen_capital_cost=in_para["res_chp_gen_gen_cc"], in_gen_efficiency=in_para["res_chp_gen_gen_effi"],
                in_p_nom_extendable=in_para["res_chp_gen_p_nom_extendable"]
            )

            # 锅炉（边际成本取0.3元/kWh，设备造价0.2元/W左右）
            self._m_opt.add_boiler_gens(
                in_marginal_cost=in_para["res_boiler_gen_mc"], in_capital_cost=in_para["res_boiler_gen_cc"],
                in_efficiency=in_para["res_boiler_gen_effi"], in_p_nom_extendable=in_para["res_boiler_gen_p_nom_extendable"]
            )

            # 电冷水机（边际成本取0.3元/kWh，设备造价0.2元/W左右）
            self._m_opt.add_ac_coolers(in_marginal_cost=in_para["res_accool_link_mc"], in_capital_cost=in_para["res_accool_link_cc"],
                                       in_efficiency=in_para["res_accool_link_effi"], in_p_nom_extendable=in_para["res_accool_link_p_nom_extendable"])

            # 热泵（边际成本取0.3元/kWh，设备造价1元/W左右）
            self._m_opt.add_heat_pumps(
                in_marginal_cost=in_para["res_heatpump_link_mc"], in_capital_cost=in_para["res_heatpump_link_cc"],
                in_heat_efficiency=in_para["res_heatpump_link_heat_effi"], in_p_nom_extendable=in_para["res_heatpump_link_p_nom_extendable"],
                in_cold_efficiency=in_para["res_heatpump_link_cold_effi"])

            # 天然气存储
            self._m_opt.add_gas_stores(in_marginal_cost=in_para["res_gas_store_mc"],
                                       in_kwh_capital_cost=in_para["res_gas_store_kwh_cc"],
                                       in_kw_capital_cost=in_para["res_gas_store_kw_cc"],
                                       in_standing_loss=in_para["res_gas_store_standing_loss"],
                                       in_charge_effi=in_para["res_gas_store_charge_effi"],
                                       in_discharge_effi=in_para["res_gas_store_discharge_effi"],
                                       in_e_nom_extendable=in_para["res_gas_store_e_nom_extendable"],
                                       in_p_nom_extendable=in_para["res_gas_store_p_nom_extendable"])

            # 蓄热（设备造价取0.2元/Wh）
            self._m_opt.add_heat_stores(in_marginal_cost=in_para["res_heat_store_mc"],
                                       in_kwh_capital_cost=in_para["res_heat_store_kwh_cc"],
                                       in_kw_capital_cost=in_para["res_heat_store_kw_cc"],
                                       in_standing_loss=in_para["res_heat_store_standing_loss"],
                                       in_charge_effi=in_para["res_heat_store_charge_effi"],
                                       in_discharge_effi=in_para["res_heat_store_discharge_effi"],
                                       in_e_nom_extendable=in_para["res_heat_store_e_nom_extendable"],
                                       in_p_nom_extendable=in_para["res_heat_store_p_nom_extendable"])

            # 冰蓄冷（设备造价取0.2元/Wh）
            self._m_opt.add_cold_stores(in_marginal_cost=in_para["res_cold_store_mc"],
                                       in_kwh_capital_cost=in_para["res_cold_store_kwh_cc"],
                                       in_kw_capital_cost=in_para["res_cold_store_kw_cc"],
                                       in_standing_loss=in_para["res_cold_store_standing_loss"],
                                       in_charge_effi=in_para["res_cold_store_charge_effi"],
                                       in_discharge_effi=in_para["res_cold_store_discharge_effi"],
                                       in_e_nom_extendable=in_para["res_cold_store_e_nom_extendable"],
                                       in_p_nom_extendable=in_para["res_cold_store_p_nom_extendable"])

            # 蓄电
            self._m_opt.add_elec_stores(in_marginal_cost=in_para["res_elec_store_mc"],
                                        in_mwh_capital_cost=in_para["res_elec_store_kwh_cc"],
                                        in_mw_capital_cost=in_para["res_elec_store_kw_cc"],
                                        in_standing_loss=in_para["res_elec_store_standing_loss"],
                                        in_charge_effi=in_para["res_elec_store_charge_effi"],
                                        in_discharge_effi=in_para["res_elec_store_discharge_effi"],
                                        in_e_nom_extendable=in_para["res_elec_store_e_nom_extendable"],
                                        in_p_nom_extendable=in_para["res_elec_store_p_nom_extendable"])

            # P2G（gas）
            self._m_opt.add_power_to_gases(
                                    in_marginal_cost=in_para["res_p2g_link_mc"],
                                    in_capital_cost=in_para["res_p2g_link_cc"],
                                    in_efficiency=in_para["res_p2g_link_effi"],
                                    in_p_nom_extendable=in_para["res_p2g_link_p_nom_extendable"])
