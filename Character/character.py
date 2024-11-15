import pandas as pd

from Skill_Class import Skill, lookup_name_or_cid
from Report import report_to_log
import logging
from define import *


class Character:
    def __init__(self,
                 name: str = '', CID: int = None,  # 角色名字和CID-必填至少一个
                 weapon=None, weapon_level=1,  # 武器名字-选填项
                 equip_set4=None, equip_set2_a=None, equip_set2_b=None, equip_set2_c=None,  # 驱动盘套装-选填项
                 drive4=None, drive5=None, drive6=None,  # 驱动盘主词条-选填项
                 scATK_percent=0, scATK=0, scHP_percent=0, scHP=0, scDEF_percent=0, scDEF=0, scAnomalyProficiency=0,
                 scPEN=0, scCRIT=0,  # 副词条数量-选填项
                 sp_limit=120  # 能量上限-默认120
                 ):
        """
        调用时，会生成包含全部角色基础信息的对象，自动从数据库中查找全部信息
        缺少任何信息都是 bug

        调用内置类 Character.Statement 时，会基于角色基础信息计算角色静态面板
        同时实例化 Character 与 Character.Statement 耗时大约 70ms，每次计算时都重新生成对象的性能开销可以接受
        如果你想要在基础面板上手动加一些数值，那么这两个类应该分开调用

        构造时必须：
        -name 和 CID 两个参数二选一，或同时提供能互相匹配上的一对值

        构造时选填：
        -weapon、weapon_level：武器名称和武器精炼等级
        -equip_setx：驱动盘套装效果，使用四件套后会忽略后两个二件套槽位
        -drive4~6: 主词条4-6号位，默认1-3号位也会被初始化
        -scXXXX：各种副词条数量
        -sp_limit：能量上限，默认为120，基本不用管

        自生成参数：
        -self.level = 60 默认角色等级，传给防御区用
        -记录每个基础属性来源的各参数，主要来自查表
        -包含角色全部技能信息的 Skill 对象，以及来自 Skill 的 action_list, skills_dict

        包含的方法：
        -没有！想写吗？

        包含的类：
        -Character.Statement 看下面注释去

        生成对象示例：
        char = Character(name="柳", weapon='时流贤者',
                         equip_set4='混沌爵士', equip_set2_a='雷暴重金属',
                         drive4='异常精通', drive5='电属性伤害%', drive6='异常掌控',
                         scAnomalyProficiency=10, scATK_percent=14, scCRIT=4)
        生成角色面板示例：
        char_dynamic = Character.Statement(char)

        还没写的：
        -自定义技能等级、角色等级、武器等级
        不复杂，但麻烦，还不重要
        -非暴击配平逻辑，未来会通过 config.json 控制
        不复杂，麻烦，重要性较高
        """
        # 参数类型检查，贼长
        if not isinstance(name, str):
            raise TypeError("char_name must be a string")
        if CID is not None and not isinstance(CID, int):
            try:
                CID = int(CID)
            except ValueError:
                raise ValueError("CID must be an integer")
        if not isinstance(sp_limit, int):
            try:
                sp_limit = int(sp_limit)
            except ValueError:
                raise TypeError("sp_limit must be an integer")
        if weapon is not None and not isinstance(weapon, str):
            raise TypeError("weapon must be a string")
        if not isinstance(weapon_level, int):
            try:
                weapon_level = int(weapon_level)
            except ValueError:
                raise TypeError("weapon_level must be an integer")
        if equip_set4 is not None and not isinstance(equip_set4, str):
            raise TypeError("equip_set4 must be a string")
        if equip_set2_a is not None and not isinstance(equip_set2_a, str):
            raise TypeError("equip_set2_a must be a string")
        if equip_set2_b is not None and not isinstance(equip_set2_b, str):
            raise TypeError("equip_set2_b must be a string")
        if equip_set2_c is not None and not isinstance(equip_set2_c, str):
            raise TypeError("equip_set2_c must be a string")
        if drive4 is not None and not isinstance(drive4, str):
            raise TypeError("drive4 must be a string")
        if drive5 is not None and not isinstance(drive5, str):
            raise TypeError("drive5 must be a string")
        if drive6 is not None and not isinstance(drive6, str):
            raise TypeError("drive6 must be a string")
        if not isinstance(scATK_percent, (int, float)):
            try:
                scATK_percent = float(scATK_percent)
            except ValueError:
                raise TypeError("scATK_percent must be a number")
        if not isinstance(scATK, (int, float)):
            try:
                scATK = float(scATK)
            except ValueError:
                raise TypeError("scATK must be a number")
        if not isinstance(scHP_percent, (int, float)):
            try:
                scHP_percent = float(scHP_percent)
            except ValueError:
                raise TypeError("scHP_percent must be a number")
        if not isinstance(scHP, (int, float)):
            try:
                scHP = float(scHP)
            except ValueError:
                raise TypeError("scHP must be a number")
        if not isinstance(scDEF_percent, (int, float)):
            try:
                scDEF_percent = float(scDEF_percent)
            except ValueError:
                raise TypeError("scDEF_percent must be a number")
        if not isinstance(scDEF, (int, float)):
            try:
                scDEF = float(scDEF)
            except ValueError:
                raise TypeError("scDEF must be a number")
        if not isinstance(scAnomalyProficiency, (int, float)):
            try:
                scAnomalyProficiency = float(scAnomalyProficiency)
            except ValueError:
                raise TypeError("scAnomalyProficiency must be a number")
        if not isinstance(scPEN, (int, float)):
            try:
                scPEN = float(scPEN)
            except ValueError:
                raise TypeError("scPEN must be a number")
        if not isinstance(scCRIT, (int, float)):
            try:
                scCRIT = float(scCRIT)
            except ValueError:
                raise TypeError("scCRIT must be a number")

        # 从数据库中查找角色信息，并核对必填项
        self.NAME, self.CID = lookup_name_or_cid(name, CID)

        # 初始化为0的各属性
        self.baseATK = 0
        self.ATK_percent = 0
        self.ATK_numeric = 0
        self.overall_ATK_percent = 0
        self.overall_ATK_numeric = 0

        self.baseHP = 0
        self.HP_percent = 0
        self.HP_numeric = 0
        self.overall_HP_percent = 0
        self.overall_HP_numeric = 0

        self.baseDEF = 0
        self.DEF_percent = 0
        self.DEF_numeric = 0
        self.overall_DEF_percent = 0
        self.overall_DEF_numeric = 0

        self.baseIMP = 0
        self.IMP_percent = 0
        self.IMP_numeric = 0
        self.overall_IMP_percent = 0
        self.overall_IMP_numeric = 0

        self.baseAP = 0
        self.AP_percent = 0
        self.AP_numeric = 0
        self.overall_AP_percent = 0
        self.overall_AP_numeric = 0

        self.baseAM = 0
        self.AM_percent = 0
        self.AM_numeric = 0
        self.overall_AM_percent = 0
        self.overall_AM_numeric = 0

        self.baseCRIT_score = 0
        self.CRIT_rate_numeric = 0
        self.CRIT_damage_numeric = 0

        self.sp_limit = 0
        self.base_sp_regen = 0
        self.sp_regen_percent = 0
        self.sp_regen_numeric = 0
        self.sp_get_ratio = 0

        self.ICE_DMG_bonus = 0
        self.FIRE_DMG_bonus = 0
        self.PHY_DMG_bonus = 0
        self.ETHER_DMG_bonus = 0
        self.ELECTRIC_DMG_bonus = 0
        self.ALL_DMG_bonus = 0
        self.Trigger_DMG_bonus = 0

        self.PEN_ratio = 0
        self.PEN_numeric = 0

        # 单独初始化的各组件
        self.level = 60
        self.weapon_ID = weapon
        self.weapon_level = weapon_level
        self.baseCRIT_score: float = 60
        self.sp_get_ratio: float = 1  # 能量获得效率
        self.sp_limit: int = sp_limit

        # 抄表赋值！
        # 初始化角色基础属性    .\data\character.csv
        self._init_base_attribute(name)
        # 初始化武器基础属性    .\data\weapon.csv
        self._init_weapon_primitive(weapon, weapon_level)
        # 初始化套装效果        .\data\equip_set_2pc.csv
        self._init_equip_set(equip_set4, equip_set2_a, equip_set2_b, equip_set2_c)
        self.equip_sets = [
            self.equip_set4,
            self.equip_set2_a,
            self.equip_set2_b,
            self.equip_set2_c
        ]
        # 初始化主词条
        self._init_primary_drive(drive4, drive5, drive6)
        # 初始化副词条
        self._init_secondary_drive(scATK_percent, scATK, scHP_percent, scHP, scDEF_percent, scDEF, scAnomalyProficiency,
                                   scPEN, scCRIT)

        # 角色技能列表，还没有写修改技能等级的接口
        self.statement = Character.Statement(self, crit_balancing=CRIT_BALANCING)
        self.skill_object: Skill = Skill(name=self.NAME, CID=self.CID)
        self.action_list = self.skill_object.action_list
        self.skills_dict = self.skill_object.skills_dict

    class Statement:
        def __init__(self, char_class, crit_balancing=True):
            """
            -char_class : 已实例化的角色

            用于计算角色面板属性：
            -传入已经实例化的 Character 对象，计算出目前的角色面板
            -如果和 Character 对象同时调用，那么本对象会储存角色的局外面板属性
            -可在调用本类前对一个 Character 对象内的值进行更改，以实现手动调整面板的功能

            调用格式为：
            char_dynamic = Character.Statement(char)    # 需要传入一个角色对象

            获取面板数值：
            -使用属性名调用，格式为 char_dynamic.ATK
            -使用内置字典调用，格式为 char_dynamic.statement['ATK'] # 谁会想用这个方法呢，这个字典不过是方便输出 log 罢了

            值得注意的是，这个类有许多属性直接继承自 Character，但是防止混淆没有写成子类，但你依然可以直接调用 NAME、CID 等静态参数

            包含的方法：
            -还是没有！这个类是被动的，不应该自己变化，需要的时候重新生成，你要强行写函数改也行（乐
            """

            self.NAME = char_class.NAME
            self.CID = char_class.CID
            self.ATK = (char_class.baseATK * (1 + char_class.ATK_percent) + char_class.ATK_numeric) * (
                    1 + char_class.overall_ATK_percent) + char_class.overall_ATK_numeric
            self.HP = (char_class.baseHP * (1 + char_class.HP_percent) + char_class.HP_numeric) * (
                    1 + char_class.overall_HP_percent) + char_class.overall_HP_numeric
            self.DEF = (char_class.baseDEF * (1 + char_class.DEF_percent) + char_class.DEF_numeric) * (
                    1 + char_class.overall_DEF_percent) + char_class.overall_DEF_numeric
            self.IMP = (char_class.baseIMP * (1 + char_class.IMP_percent) + char_class.IMP_numeric) * (
                    1 + char_class.overall_IMP_percent) + char_class.overall_IMP_numeric
            self.AP = (char_class.baseAP * (1 + char_class.AP_percent) + char_class.AP_numeric) * (
                    1 + char_class.overall_AP_percent) + char_class.overall_AP_numeric
            self.AM = (char_class.baseAM * (1 + char_class.AM_percent) + char_class.AM_numeric) * (
                    1 + char_class.overall_AM_percent) + char_class.overall_AM_numeric
            # 更换balancing参数可实线不同的逻辑，默认为True，即配平逻辑
            self.CRIT_damage, self.CRIT_rate = self._func_statement_CRIT(char_class.baseCRIT_score,
                                                                         char_class.CRIT_rate_numeric,
                                                                         char_class.CRIT_damage_numeric,
                                                                         balancing=crit_balancing)
            self.sp_regen = char_class.base_sp_regen * (1 + char_class.sp_regen_percent) + char_class.sp_regen_numeric
            self.sp_get_ratio = char_class.sp_get_ratio
            self.sp_limit = char_class.sp_limit
            # 动态计算目前能量的函数

            self.PEN_ratio = char_class.PEN_ratio
            self.PEN_numeric = char_class.PEN_numeric
            self.ICE_DMG_bonus = char_class.ICE_DMG_bonus
            self.FIRE_DMG_bonus = char_class.FIRE_DMG_bonus
            self.PHY_DMG_bonus = char_class.PHY_DMG_bonus
            self.ETHER_DMG_bonus = char_class.ETHER_DMG_bonus
            self.ELECTRIC_DMG_bonus = char_class.ELECTRIC_DMG_bonus

            # 将当前对象 (self) 的所有非可调用（即不是方法或函数）的属性收集到一个字典中
            self.statement = {attr: getattr(self, attr)
                              for attr in dir(self)
                              if not callable(getattr(self, attr)) and not attr.startswith("__")}
            report_to_log(f'[CHAR STATUS]:{self.NAME}:{str(self.statement)}')

        @staticmethod
        def _func_statement_CRIT(CRIT_score: float,
                                 CRIT_rate_numeric: float,
                                 CRIT_damage_numeric: float,
                                 balancing=True) -> tuple:
            """
            双暴状态函数
            balancing : 是否使用配平逻辑
            CRIT_score : 暴击评分
            CRIT_rate_numeric : 暴击率数值
            CRIT_damage_numeric : 暴击伤害数值
            返回：
            CRIT_damage : 暴击伤害
            CRIT_rate : 暴击率

            默认为True，即配平逻辑，会使用暴击评分、暴击暴伤输出，集中计算暴击率与暴击伤害
            若为False，则忽略传入的暴击评分，直接返回给定的数值
            """
            # 参数有效性验证
            if not (0 <= CRIT_score):
                raise ValueError("CRIT_score must be above 0")
            if not (0 <= CRIT_rate_numeric):
                raise ValueError("CRIT_rate_numeric must be above 0")
            if not (0 <= CRIT_damage_numeric):
                raise ValueError("CRIT_damage_numeric must be above 0")

            if balancing:
                all_CRIT_score = CRIT_score + CRIT_rate_numeric * 200 + CRIT_damage_numeric * 100
                if all_CRIT_score >= 400:
                    CRIT_rate = 1
                    CRIT_damage = (CRIT_score / 100 - 2) + (CRIT_damage_numeric + CRIT_rate_numeric * 2)
                else:
                    CRIT_damage = max(0.5, CRIT_score / 200) + CRIT_damage_numeric
                    CRIT_rate = (CRIT_score / 100 - CRIT_damage) / 2 + CRIT_rate_numeric
            else:
                CRIT_damage = CRIT_damage_numeric
                CRIT_rate = CRIT_rate_numeric
            return min(5.0, CRIT_damage), min(1.0, CRIT_rate)

        def __str__(self) -> str:
            return f"角色静态面板：{self.NAME}"

    def _init_base_attribute(self, char_name: str):
        """
        初始化角色基础属性。
        根据角色名称，从CSV文件中读取角色的基础属性数据，并将其赋值给角色对象。
        参数:
        char_name(str): 角色的名称。
        """
        if not isinstance(char_name, str) or not char_name.strip():
            raise ValueError("角色名称必须是非空字符串")
        try:
            df = pd.read_csv(CHARACTER_DATA_PATH)
            # 查找与角色名称匹配的行，并转换为字典形式，每条记录一个字典
            row = df[df['name'] == char_name].to_dict('records')
            if row:
                # 将对应记录提取出来，并赋值给角色对象
                row = row[0]
                self.baseATK = float(row.get('基础攻击力', 0))
                self.baseHP = float(row.get('基础生命值', 0))
                self.baseDEF = float(row.get('基础防御力', 0))
                self.baseIMP = float(row.get('基础冲击力', 0))
                self.baseAP = float(row.get('基础异常精通', 0))
                self.baseAM = float(row.get('基础异常掌控', 0))
                self.baseCRIT_score = float(row.get('基础暴击分数', 60))
                self.PEN_ratio = float(row.get('基础穿透率', 0))
                self.PEN_numeric = float(row.get('基础穿透值', 0))
                self.base_sp_regen = float(row.get('基础能量自动回复', 0))
                self.base_sp_get_ratio = float(row.get('基础能量获取效率', 1))
                # CID特殊处理，避免不必要的类型转换
                cid_value = row.get('CID', None)
                self.CID = int(cid_value) if cid_value is not None else None
            else:
                raise ValueError(f"角色{char_name}不存在")
        except FileNotFoundError:
            logging.error("找不到角色数据文件，请检查路径是否正确。")
            raise
        except pd.errors.EmptyDataError:
            logging.error("角色数据文件为空。")
            raise
        except Exception as e:
            logging.error(f"初始化角色属性时发生未知错误：{e}")
            raise

    def _init_weapon_primitive(self, weapon: str, weapon_level: int) -> None:
        """
        初始化武器属性
        """
        if weapon is not None:
            df = pd.read_csv(WEAPON_DATA_PATH)
            row_5 = df[df['weapon_ID'] == weapon]  # 找到所有包含此武器的行
            if not row_5.empty:  # 检查是否找到匹配项
                row = row_5[row_5['level'] == weapon_level].to_dict('records')  # 找到对应精炼等级的行，并转化为字典
                if row:
                    row = row[0]
                    self.baseATK += float(row.get('base_ATK', 0))
                    self.ATK_percent += float(row.get('ATK%', 0))
                    self.DEF_percent += float(row.get('DEF%', 0))
                    self.HP_percent += float(row.get('HP%', 0))
                    self.IMP_percent += float(row.get('IMP%', 0))
                    self.overall_ATK_percent += float(row.get('oATK%', 0))
                    self.overall_DEF_percent += float(row.get('oDEF%', 0))
                    self.overall_HP_percent += float(row.get('oHP%', 0))
                    self.overall_IMP_percent += float(row.get('oIMP%', 0))
                    self.baseCRIT_score += 100 * (float(row.get('Crit_Rate', 0)) * 2 + float(row.get('Crit_Damage', 0)))
                    self.AM_numeric += float(row.get('Anomaly_Mastery', 0))
                    self.AP_numeric += float(row.get('Anomaly_Proficiency', 0))
                    self.sp_regen_percent += float(row.get('Regen%', 0))
                    self.sp_regen_numeric += float(row.get('Regen', 0))
                    self.sp_get_ratio += float(row.get('Get_ratio', 0))
                    self.ICE_DMG_bonus += float(row.get('ICE_DMG_bonus', 0))
                    self.FIRE_DMG_bonus += float(row.get('FIRE_DMG_bonus', 0))
                    self.ELECTRIC_DMG_bonus += float(row.get('ELECTRIC_DMG_bonus', 0))
                    self.PHY_DMG_bonus += float(row.get('PHY_DMG_bonus', 0))
                    self.ETHER_DMG_bonus += float(row.get('ETHER_DMG_bonus', 0))
                else:
                    raise ValueError(f"请输入正确的精炼等级")
            else:
                raise ValueError(f"请输入正确的武器名称，{weapon} 不存在！")

    def _init_equip_set(self, equip_set4: str, equip_set2_a: str, equip_set2_b: str, equip_set2_c: str):
        """
        初始化套装效果，Character类仅计算二件套
        """
        # 将自身套装效果抄录
        equip_set_all = [equip_set4, equip_set2_a, equip_set2_b, equip_set2_c]
        # 检查是否有相同套装
        unique_sets = [i for i in equip_set_all if bool(i)]
        if len(set(unique_sets)) != len(unique_sets):
            raise ValueError("请勿输入重复的套装名称")
        self.equip_set4, self.equip_set2_a, self.equip_set2_b, self.equip_set2_c = tuple(equip_set_all)
        # 存在四件套则移出2b、2c
        if bool(equip_set4):  # 非空判断
            if equip_set2_b in equip_set_all:  # 别删这个if，否则输入None会报错
                equip_set_all.remove(equip_set2_b)
            if equip_set2_c in equip_set_all:  # 别删这个if，否则输入None会报错
                equip_set_all.remove(equip_set2_c)
        if equip_set_all is not None:  # 全空则跳过
            df = pd.read_csv(EQUIP_2PC_DATA_PATH)
            for equip_2pc in equip_set_all:
                if bool(equip_2pc):  # 若二件套非空，则继续
                    row = df[df['set_ID'] == equip_2pc].to_dict('records')
                    if row:
                        row = row[0]
                        self.ATK_percent += float(row.get('ATK%', 0))
                        self.HP_percent += float(row.get('HP%', 0))
                        self.DEF_percent += float(row.get('DEF%', 0))
                        self.IMP_percent += float(row.get('IMP%', 0))
                        self.AM_numeric += float(row.get('Anomaly_Mastery', 0))
                        self.AP_numeric += float(row.get('Anomaly_Proficiency', 0))
                        self.sp_regen_percent += float(row.get('Regen%', 0))
                        self.sp_regen_numeric += float(row.get('Regen', 0))
                        self.sp_get_ratio += float(row.get('Get_ratio', 0))
                        self.PEN_ratio += float(row.get('PEN%', 0))
                        self.PEN_numeric += float(row.get('PEN', 0))
                        self.ICE_DMG_bonus += float(row.get('ICE_DMG_bonus', 0))
                        self.FIRE_DMG_bonus += float(row.get('FIRE_DMG_bonus', 0))
                        self.ELECTRIC_DMG_bonus += float(row.get('ELECTRIC_DMG_bonus', 0))
                        self.PHY_DMG_bonus += float(row.get('PHY_DMG_bonus', 0))
                        self.ETHER_DMG_bonus += float(row.get('ETHER_DMG_bonus', 0))
                    else:
                        raise ValueError(f"套装 {equip_2pc} 不存在")

    def _init_primary_drive(self, drive4: str, drive5: str, drive6: str):
        """
        初始化主词条
        """
        drive_parts = [drive4, drive5, drive6]
        # 初始化1-3号位
        self.HP_numeric += 2200
        self.ATK_numeric += 316
        self.DEF_numeric += 184
        # 匹配4-6号位
        for drive in drive_parts:
            match drive:
                case '生命值%' | '生命值':
                    self.HP_percent += 0.3
                case '攻击力%' | '攻击力':
                    self.ATK_percent += 0.3
                case '防御力%' | '防御力':
                    self.DEF_percent += 0.48
                case '暴击率%' | '暴击率':
                    # self.CRIT_rate_numeric += 0.24
                    self.baseCRIT_score += 48
                case '暴击伤害%' | '暴击伤害':
                    # self.CRIT_damage_numeric += 0.48
                    self.baseCRIT_score += 48
                case '异常精通':
                    self.AP_numeric += 92
                case '穿透率%' | '穿透率':
                    self.PEN_ratio += 0.24
                case '冰属性伤害%' | '冰属性伤害':
                    self.ICE_DMG_bonus += 0.3
                case '火属性伤害%' | '火属性伤害':
                    self.FIRE_DMG_bonus += 0.3
                case '电属性伤害%' | '电属性伤害':
                    self.ELECTRIC_DMG_bonus += 0.3
                case '以太属性伤害%' | '以太属性伤害':
                    self.ETHER_DMG_bonus += 0.3
                case '物理属性伤害%' | '物理属性伤害':
                    self.PHY_DMG_bonus += 0.3
                case '异常掌控':
                    self.AM_percent += 0.3
                case '冲击力%' | '冲击力':
                    self.IMP_percent += 0.18
                case '能量自动回复%' | '能量自动回复':
                    self.sp_regen_percent += 0.6
                case None:
                    continue
                case 'None':
                    continue
                case _:
                    raise ValueError(f"提供的主词条名称 {drive} 不存在")

    def _init_secondary_drive(self, scATK_percent: int, scATK: int, scHP_percent: int, scHP: int, scDEF_percent: int,
                              scDEF: int, scAnomalyProficiency: int, scPEN: int, scCRIT: int):
        """
        初始化副词条
        """
        # 类型检查
        if not all(isinstance(x, (int, float)) for x in
                   [scATK_percent, scATK, scHP_percent, scHP, scDEF_percent, scDEF, scAnomalyProficiency, scPEN,
                    scCRIT]):
            raise TypeError("词条数量必须是数.")

        # 参数有效性检查
        if any(x < 0 for x in
               [scATK_percent, scATK, scHP_percent, scHP, scDEF_percent, scDEF, scAnomalyProficiency, scPEN, scCRIT]):
            raise ValueError("词条数量不能为负.")

        self.ATK_percent += (scATK_percent * 0.03)
        self.ATK_numeric += (scATK * 19)
        self.HP_percent += (scHP_percent * 0.03)
        self.HP_numeric += (scHP * 112)
        self.DEF_percent += (scDEF_percent * 0.048)
        self.DEF_numeric += (scDEF * 15)
        self.AP_numeric += (scAnomalyProficiency * 9)
        self.PEN_numeric += (scPEN * 9)
        self.baseCRIT_score += (scCRIT * 4.8)


    def special_resources(self, *args, **kwargs) -> None:
        """父类中不包含默认特殊资源"""
        return None

    def __str__(self) -> str:
        return f"{self.NAME} {self.level}级"

# TODO 每个拥有特殊资源的角色单独写类，继承自Character

if __name__ == "__main__":
    pass
