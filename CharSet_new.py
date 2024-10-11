import json
import numpy as np
import pandas as pd

class Character:
    def __init__(self,
                 char_name,    # 角色名字-必填项
                 weapon=None, weapon_level=1, # 武器名字-选填项
                 equip_set4=None, equip_set2_a=None, equip_set2_b=None, equip_set2_c=None,  # 驱动盘套装-选填项
                 drive4=None, drive5=None, drive6=None,  # 驱动盘主词条-选填项
                 scATK_percent=0, scATK=0, scHP_percent=0, scHP=0, scDEF_percent=0, scDEF=0, scAnomalyProficiency=0, scPEN=0, scCRIT=0, #副词条数量-选填项
                 initial_sp=60 # 初始充能-默认60
                 ):
        self.CID = None
        # 攻击力各组件
        self.baseATK: float = 0
        self.ATK_percent: float = 0
        self.ATK_numeric: float = 0
        self.overral_ATK_percent: float = 0
        self.overral_ATK_numeric: float = 0
        
        # 生命值各组件
        self.baseHP: float = 0
        self.HP_percent: float = 0
        self.HP_numeric: float = 0
        self.overral_HP_percent: float = 0
        self.overral_HP_numeric: float = 0

        # 防御力各组件
        self.baseDEF: float = 0
        self.DEF_percent: float = 0
        self.DEF_numeric: float = 0
        self.overral_DEF_percent: float = 0
        self.overral_DEF_numeric: float = 0
        
        # 冲击力各组件
        self.baseIMP: float = 0
        self.IMP_percent: float = 0
        self.IMP_numeric: float = 0
        self.overral_IMP_percent: float = 0
        self.overral_IMP_numeric: float = 0
        
        # 异常精通各组件
        self.baseAP: float = 0
        self.AP_percent: float = 0 
        self.AP_numeric: float = 0 
        self.overral_AP_percent: float = 0
        self.overral_AP_numeric: float = 0

        # 异常掌控各组件
        self.baseAM: float = 0
        self.AM_percent: float = 0
        self.AM_numeric: float = 0
        self.overral_AM_percent: float = 0
        self.overral_AM_numeric: float = 0

        # 暴击分数各组件
        self.baseCRIT_score: float = 60
        self.CRIT_rate_numeric: float = 0
        self.CRIT_damage_numeric: float = 0

        # 充能各组件
        self.sp_limit: int = 120 # 充能上限
        self.sp = min(initial_sp, self.sp_limit)    # 初始能量，从输入值中读取，默认为60，不超过120
        self.base_sp_regen = 0    # 能量自动回复
        self.sp_regen_percent = 0
        self.sp_regen_numeric = 0
        self.sp_get_ratio = 1   # 能量获得效率

        # 增伤各组件
        self.ICE_DMG_bonus = 0
        self.FIRE_DMG_bonus = 0
        self.PHY_DMG_bonus = 0
        self.ETHER_DMG_bonus = 0
        self.ELECTRIC_DMG_bonus = 0
        self.ALL_DMG_bonus = 0
        self.Trigger_DMG_bonus = 0

        # 穿透各组件
        self.PEN_ratio = 0
        self.PEN_numeric = 0
        
        # 抄表赋值！
        # 初始化角色基础属性    .\data\character.csv
        self.init_base_attribute(char_name)
        # 初始化武器基础属性    .\data\weapon.csv
        self.init_weapon_primitive(weapon, weapon_level)
        # 初始化套装效果        .\data\equip_set.csv
        self.init_equip_set(equip_set4, equip_set2_a, equip_set2_b, equip_set2_c)
        # 初始化主词条          .\data\primary_drive.csv
        self.init_primary_drive(drive4, drive5, drive6)
        # 初始化副词条          .\data\secondary_drive.csv
        self.init_secondary_drive(scATK_percent, scATK, scHP_percent, scHP, scDEF_percent, scDEF, scAnomalyProficiency, scPEN, scCRIT)

        
    class Statement:
        def __init__(self,char_class):
            '''
            char_class : 已实例化的角色
            每次计算角色局外属性：传入已经实例化的角色对象，计算出目前的角色面板
            实例化格式为Character.Statement(char_class)，需要传入一个角色对象
            获取面板数值：使用属性名调用，格式为char_dynamic_statement.ATK
            也可以使用key调用面板数值，格式为Character.Statement.get_statement(key, char_class)

            例: char = Character("柳")      # 实例化一个角色
                char_dynamic = Character.Statement(char)    # 实例化角色面板
                print(char_dynamic.CRIT_damage) # 获取角色面板数值
                print(Character.Statement.get_statement('CRIT_damage', char))  # 实例化同时读出面板，用于程序中debug
            '''
            
            self.ATK = (char_class.baseATK * (1 + char_class.ATK_percent) + char_class.ATK_numeric) * (1 + char_class.overral_ATK_percent) + char_class.overral_ATK_numeric
            self.HP = (char_class.baseHP * (1 + char_class.HP_percent) + char_class.HP_numeric) * (1 + char_class.overral_HP_percent) + char_class.overral_HP_numeric
            self.DEF = (char_class.baseDEF * (1 + char_class.DEF_percent) + char_class.DEF_numeric) * (1 + char_class.overral_DEF_percent) + char_class.overral_DEF_numeric
            self.IMP = (char_class.baseIMP * (1 + char_class.IMP_percent) + char_class.IMP_numeric) * (1 + char_class.overral_IMP_percent) + char_class.overral_IMP_numeric
            self.AP = (char_class.baseAP * (1 + char_class.AP_percent) + char_class.AP_numeric) * (1 + char_class.overral_AP_percent) + char_class.overral_AP_numeric
            self.AM = (char_class.baseAM * (1 + char_class.AM_percent) + char_class.AM_numeric) * (1 + char_class.overral_AM_percent) + char_class.overral_AM_numeric
            self.CRIT_damage = max(char_class.baseCRIT_score/200, 0.5) + char_class.CRIT_damage_numeric
            self.CRIT_rate = (char_class.baseCRIT_score/100 - (self.CRIT_damage - char_class.CRIT_damage_numeric)) / 2 + char_class.CRIT_rate_numeric
            self.sp_regen = char_class.base_sp_regen * (1 + char_class.sp_regen_percent) + char_class.sp_regen_numeric
            self.sp_get_ratio = char_class.sp_get_ratio
            self.sp = char_class.sp
            self.PEN_ratio = char_class.PEN_ratio
            self.PEN_numeric = char_class.PEN_numeric
            self.DMG_bonus = self.deving_func_DMG_bonus(char_class.ICE_DMG_bonus, char_class.FIRE_DMG_bonus, char_class.PHY_DMG_bonus, char_class.ETHER_DMG_bonus, char_class.ELECTRIC_DMG_bonus, char_class.ALL_DMG_bonus, char_class.Trigger_DMG_bonus)
            
            self.statement = {
                'ATK': self.ATK,
                'HP': self.HP,
                'DEF': self.DEF,
                'IMP': self.IMP,
                'AP': self.AP,
                'AM': self.AM,
                'CRIT_damage': self.CRIT_damage,
                'CRIT_rate': self.CRIT_rate,
                'sp_regen': self.sp_regen,
                'sp_get_ratio': self.sp_get_ratio,
                'sp': self.sp,
                'PEN_ratio': self.PEN_ratio,
                'PEN_numeric': self.PEN_numeric,
                'DMG_bonus': self.DMG_bonus,
            }
            print(self.statement)
        @classmethod
        def get_statement(cls, attr:str, char_class:object) -> float:
            '''
            attr : 要获取的属性
            char_class : 已实例化的角色
            每次计算角色局外属性：传入已经实例化的角色对象，计算出目前的角色面板
            '''
            statement = cls(char_class)
            return statement.statement[attr]
        
        def deving_func_DMG_bonus(self, ICE_DMG_bonus:float, FIRE_DMG_bonus:float, PHY_DMG_bonus:float, ETHER_DMG_bonus:float, ELECTRIC_DMG_bonus:float, ALL_DMG_bonus:float, Trigger_DMG_bonus:float) -> float:
            '''
            计算增伤区
            '''
            self.DMG_bonus = ICE_DMG_bonus
            
            
    def init_base_attribute(self, char_name:str):
        """
        初始化角色基础属性。
        根据角色名称，从CSV文件中读取角色的基础属性数据，并将其赋值给角色对象。
        参数:
        char_name(str): 角色的名称。
        """
        df = pd.read_csv('.\\data\\character.csv')
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
            self.CID = float(row.get('CID',None))
        else:
            raise ValueError(f"角色{char_name}不存在")
     
    
    def init_weapon_primitive(self, weapon:str, weapon_level:int) -> None:
        """
        初始化武器属性
        """
        if weapon is not None:
            df = pd.read_csv('.\\data\\weapon.csv')
            row_5 = df[df['weapon_ID'] == weapon] # 找到第一个包含此武器的行
            if not row_5.empty:     # 检查是否找到匹配项
                row = row_5[row_5['level'] == weapon_level].to_dict('records') # 找到对应精炼等级的行，并转化为列表
                if row:
                    row = row[0]
                    self.baseATK += float(row.get('Base_ATK', 0))
                    self.ATK_percent += float(row.get('ATK%', 0))
                    self.DEF_percent += float(row.get('DEF%', 0))
                    self.HP_percent += float(row.get('HP%', 0))
                    self.IMP_percent += float(row.get('IMP%', 0))
                    self.overral_ATK_percent += float(row.get('oATK%', 0))
                    self.overral_DEF_percent += float(row.get('oDEF%', 0))
                    self.overral_HP_percent += float(row.get('oHP%', 0))
                    self.overral_IMP_percent += float(row.get('oIMP%', 0))
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
                raise ValueError(f"请输入正确的武器名称")

    def init_equip_set(self, equip_set4:str, equip_set2_a:str, equip_set2_b:str, equip_set2_c:str):
        '''
        初始化套装效果
        '''
        return None
    
    def init_primary_drive(self, drive4:str, drive5:str, drive6:str):
        '''
        初始化主词条
        '''
        return None
    
    def init_secondary_drive(self, scATK_percent:int, scATK:int, scHP_percent:int, scHP:int, scDEF_percent:int, scDEF:int, scAnomalyProficiency:int, scPEN:int, scCRIT:int):
        '''
        初始化副词条
        '''
        self.ATK_percent += (scATK_percent * 0.03)
        self.ATK_numeric += (scATK * 19)
        self.HP_percent += (scHP_percent * 0.03)
        self.HP_numeric += (scHP * 112)
        self.DEF_percent += (scDEF_percent * 0.048)
        self.DEF_numeric += (scDEF * 15)
        self.AP_numeric += (scAnomalyProficiency * 9)
        self.PEN_numeric += (scPEN * 9)
        self.baseCRIT_score += (scCRIT * 4.8)
    
'''
if __name__ == "__main__":
    char = Character("艾莲", "深海访客", 1,None,None,None,None,None,None,None,1,1,1,1,1,1,1,1,25)      # 实例化默认角色
    char_dynamic = Character.Statement(char)
    print(char_dynamic.CRIT_damage)
    print(char_dynamic.CRIT_rate)
'''
