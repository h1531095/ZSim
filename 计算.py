import xlwings as xw
from tqdm import tqdm #这是一个显示进度条的函数，用法是：for t in tqdm(list)
import pandas as pd
from functools import partial
import math
import os
from ChangeChar import process_action



wb = xw.Book('F:\我的\镜像相关\绝区零公测后\ZZZ总数据库及计算\绝区零数据库.xlsx')       #数据库表（起点）
#wb_t = xw.Book('F:\我的\镜像相关\绝区零公测后\ZZZ总数据库及计算\计算总表.xlsx')     #计算表（终点）
sheet_basic = wb.sheets['配装&面板']        #数据源
charactername_sheet = wb.sheets['角色名与编号']     #所有角色名的表
charactername_range = 'B2:B16'      #记录了角色名的范围
weaponname_range = 'D10:D53'        #记录了音擎名的范围
weaponname_sheet = wb.sheets['音擎基础数据库']      #所有音擎名的表
characterbox = list(charactername_sheet.range(charactername_range).value)       #将角色名转化为list
weaponbox = list(weaponname_sheet.range(weaponname_range).value)        #将音擎名转化为list
characterconfig_dict = {'30词条0+1艾莲':['1191','艾莲','60','0','6','12','12','12','12','12','深海访客','60','1','极地重金属','啄木鸟电音','0','0', '生命值', '攻击力', '防御力','暴击率','冰属性伤害加成','攻击力%','35','2','2','2','2','2','2','1','19','0','2'],
                        '标准0+1狼哥':['1141','莱卡恩','60','0','6','12','12','12','12','12','拘缚者','60','1','自由蓝调','极地重金属','0','0','生命值','攻击力','防御力','攻击力%','冰属性伤害加成','冲击力%','15','0','0','0','5','5','0','0','0','5','0'],
                        '标准6+5苍角':['1131','苍角','60','6','6','12','12','12','12','12','含羞恶面','60','5','自由蓝调','摇摆爵士','0','0','生命值','攻击力','防御力','异常精通','冰属性伤害加成','能量自动回复%','15','0','0','0','5','5','0','0','0','5','0'],
                        '25词条0+1朱鸢':['1241','朱鸢','60','0','6','12','12','12','12','12','防暴者VI型','60','1','混沌重金属','啄木鸟电音','0','0','生命值','攻击力','防御力','暴击率','以太伤害加成','攻击力%','35','2','2','2','2','2','2','15','5','0','3'],
                        }       #把角色的代码收集到一个字典里；
configcheck_positionlist = [1, 10, 13] #角色配置单中，分别记录了角色的名字，武器，4件套。这三个地方的名字将用来判断某些buff是否激活。
characterconfig_range = ['D3','D2','D4','H38',
                         'D6','C38','D38','E38','F38','G38',
                         'F2','F3','F4','D9','E9','F9','G9',
                         'D11', 'E11', 'F11', 'G11','H11','I11',
                         'J1','M2','M3','M4','M5','M6','M7','M8','M9','M10','M11']#和配装方案对应，记录的是每一位数值填写到哪个单元格里面去
'''配置表list清单
    ['id', 'name', 'level', 'talent', 
    'unique_skill', 'normal_attack', 'dash_skill', 'support_skill', 'special_skill', 'qte_skill',
    'weapon', 'weapon_level', 'refinement', 'equipment_set4', 'equipment_set2_a', 'equipment_set2_b', 'equipment_set2_c',
    'position1', 'position2', 'position3', 'position4', 'position5', 'position6',
    'sum', 'hp', 'attack', 'defense', 'hpper', 'atkper', 'defper', 'cr', 'cd', 'elementmystery', 'pendelta']
'''

enemyconfig_dict = {'默认面板-提尔锋（弱以太）':['101110911', '提尔锋', '以骸', '70', '53357.22', '421.42', '714.6', '1000.33', '0.5', '1',  '500', '0', '0', '0', '0', '-0.2'],
                    '默认面板-法布提（弱冰+以太）':['20001', '法布提', '以骸', '70', '356958.18', '964.83', '857.52', '5781.54', '0.25', '2', '3000', '0', '0', '-0.2', '0', '-0.1'],
                    '默认面板-死路屠夫（弱冰+以太）':['30001', '死路屠夫', '以骸', '70', '660613.2', '1330.8', '952.8', '5270.52', '1', '3', '5000', '0', '0', '-0.2', '0', '-0.1']}
'''enemysetkey 

              ID，名字，怪物种类，等级，
              生命值，攻击力，防御力，失衡，失衡易伤，连携次数，元素蓄积值（暂定，由于解包数据无法解读，所以这里只能用一个虚拟值来代替，暂时不参与计算）
              物理抗性，火抗，冰抗，电抗，以太抗
'''

keys = ['id', 'name', 'level', 'talent', 
    'unique_skill', 'normal_attack', 'dash_skill', 'support_skill', 'special_skill', 'qte_skill',
    'weapon', 'weapon_level', 'refinement', 'equipment_set4', 'equipment_set2_a', 'equipment_set2_b', 'equipment_set2_c',
    'position1', 'position2', 'position3', 'position4', 'position5', 'position6',
    'sum', 'hp', 'attack', 'defense', 'hpper', 'atkper', 'defper', 'cr', 'cd', 'elementmystery', 'pendelta',]

#用来装stat_dict键值的keybox
statementkeys = ['hp', 'atk', 'defs', 'bs', 'cr', 'cd', 'eap', 'em', 'pr', 'pd', 'spr', 'spgr', 'spm', 'phy', 'fir', 'ice', 'ele', 'eth']
statefix_dict_default = {'hp': 0, 'atk': 0, 'defs': 0, 'bs': 0, 'cr': 0, 'cd': 0, 'eap': 0, 'em': 0, 'pr': 0, 'pd': 0, 'spr': 0, 'spgr': 0, 'spm': 0, 'phy': 0, 'fir': 0, 'ice': 0, 'ele': 0, 'eth': 0}
stateoutsidebonus_dict_default = {'hp': 0, 'atk': 0, 'defs': 0, 'bs': 0, 'cr': 0, 'cd': 0, 'eap': 0, 'em': 0, 'pr': 0, 'pd': 0, 'spr': 0, 'spgr': 0, 'spm': 0, 'phy': 0, 'fir': 0, 'ice': 0, 'ele': 0, 'eth': 0}
'''statementkeys中文翻译：
生命值，攻击力，防御，冲击力，暴击率，爆伤，异常掌控，异常精通，穿透率，穿透值，能量自动回复，能量获得效率，能量上限，物理伤，火伤，  冰伤， 电伤， 以太伤]
'''

enemysetkeys = ['ID', 'Name', 'Type', 'Level', 
                'Hp', 'Atk', 'Def', 'Stun', 'StunDamageTakeRatio' ,'StunResetCount' ,'ElementAbnormal' , 
                'PhyResist', 'FireResist', 'IceResist', 'EleResist', 'EthResist']
'''
↑↑↑↑↑↑↑↑↑↑↑↑
enemysetkey = ID，名字，怪物种类，等级，
              生命值，攻击力，防御力，失衡，元素蓄积值（暂定，由于解包数据无法解读，所以这里只能用一个虚拟值来代替，暂时不参与计算）
              物理抗性，火抗，冰抗，电抗，以太抗
'''
#用来存放敌人信息的空字典
enemyinformation = {}


#记录了元素种类的keys表
elementtype_key = ['phy', 'fire', 'ice', 'ele', 'eth']
elementtype_dict = {'phy':'PhyBonus', 'fire':'FireBonus', 'ice':'IceBonus', 'ele':'EleBonus', 'eth':'EthBonus'}


buffkeylist = ['from', 'exsist', 'name', 'active', 'maxduration', 'duration', 'maxcount', 'count']
buffdict = {'from':None, 'exsist': False, 'name':None, 'active': False, 'maxduration': 0, 'duration': 0, 'maxcount': 1, 'count':0}


#记录了技能标签的keys列表
skill_stat_keys = ['id', 'Name', 'OfficialName', 
                   'DmgRatio', 'StunRatio', 'SpConsumption', 
                   'SpRecovery_hit', 'FeverRecovery', 
                   'ElementAbnormalAccumlation', 'SkillType', 'TriggerBuffLevel', 'ElementType', 
                   'TimeCost', 'HitNumber', 
                   'DmgRelated_Attributes', 'StunRelated_Attributes']
standard_key = ['id', 'OfficialName', 'SpConsumption', 'SpRecovery_hit', 'FeverRecovery', 'ElementAbnormalAccumlation', 'SkillType', 'TriggerBuffLevel', 'ElementType', 'TimeCost', 'HitNumber', 'DmgRelated_Attributes', 'StunRelated_Attributes']
activcharacter_allskilldict = {}
#乘区字典，这里是作为默认字典加入的，如果以后有需要常驻某加成，可以直接修改这个内容。
muldict_default = {
           'PhyBonus': 0, 'FireBonus': 0, 'IceBonus': 0, 'EleBonus': 0, 'EthBonus': 0, 
           'AttackType': 0, 
           'NormalAttack': 0,'SpecialSkill': 0,'ExSpecial': 0,'Dashattack': 0,'Avoidattack': 0,'QTE': 0,'Q': 0,'BHaid': 0,'Parryaid': 0,'Assaultaid': 0, 'ElementalStatus': 0,
           'ALLDMG': 0, 
           'Defincrease': 0, 'Defdecrease': 0, 'Deffix': 0,
           'Pendelta': 0, 'Pendelta_Ratio': 0, 
           'Element_reduce': 0, 'Element_penetrate': 0, 
           'PhyRes': 0, 'FireRes': 0, 'IceRes': 0, 'EleRes': 0, 'EthRes': 0, 'AllRes': 0, 
           'Chance_to_be_crit': 0, 'Damage_from_crit': 0,
           'Dmgtaken_Increase': 0, 'Dmgtaken_Decrease': 0, 
           'StunDamage_TakeRatio': 0, 'StunDamage_TakeRatio_Delta': 0, 
           'Special_Multiplication_Zone': 0}
skilltypekey_list = ['NormalAttack','SpecialSkill','ExSpecial','Dashattack','Avoidattack','QTE','Q','BHaid','Parryaid','Assaultaid','ElementalStatus']
skilltypekey_dict = {'NormalAttack':'na','SpecialSkill':'special','ExSpecial':'exspecial','Dashattack':'dasha','Avoidattack':'avoida','QTE':'qte','Q':'q','BHaid':'bh','Parryaid':'parry','Assaultaid':'assault','ElementalStatus':'elementalstatus'}
enemyreskey_csv_list = ['PhyRes','FireRes','IceRes','EleRes','EthRes','AllRes']
enemyreskey_list = ['phy', 'fire', 'ice', 'ele', 'eth' ,'all']
enemyres_dict = dict(zip(enemyreskey_list, enemyreskey_csv_list))
deflist = ['defup', 'defdown', 'deffix']
defdict = {'defup':'Defincrease', 'defdown':'Defdecrease', 'deffix':'Deffix'}

mulkey_list = ['dmg', 'defence', 'res', 'crit', 'vul', 'stdmg', 'special']        #大乘区的key值的list，
muldefaultvalue_list = [1,1,1,1,1,1,1]
keybox = []
calculate_box = {}       #用于存放激活角色信息的字典，在character_set()函数结束后，这个box里面会放入三个角色的配置代码！！格式，角色配置名称：长列表
statementbasic_box = {}       #用于存放激活角色实时属性的box，每一个键值后面都是一个float
statementBonus_box = {}      #用于存放激活角色实时加成的box，其中每一个键值后面都是一个[a,b]，a是固定加成，b是百分比加成
statementoutside_box = {}     #用于存放激活角色的站街面板的box，
config_list = []        #只用于存放长列表
character_1 = None
character_2 = None
character_3 = None
activ_characterbox = [character_1,character_2,character_3]      #三个空角色变量，在character_set()结束后，会将calculatebox字典中的三个角色配置信息分别通过character类的方法进行分配
#charactername_box = []      #空列表，拿来装本次参与计算的角色名
characterbox_now = [None, None, None]       #用来存放本次激活的角色




# 定义一个函数，将字符串转换为浮点数，如果不能转换则保持为字符串
def convert_to_float(s):
    try:
        return float(s)
    except ValueError:
        return s

'''计算方式：

下面这个class是一个单独的class，记录了计算的方法，
就是基础值与固定值、百分比加成之间的计算关系，
到时候调用这个class，我们就能直接得到计算的结果，


'''
class BonusCalculate: 
    def __init__(self, bonus_list: list[float]):     #定义最终计算方法，之后调用的时候就是调用的这个位置，需要输入一个列表,[a,b]，a是固定加成，b是百分比加成。
        if len(bonus_list) != 2:
            raise ValueError('bonus_list必须包含2个元素！')
        self.fix = self.FixedBonus(bonus_list[0])
        self.perc = self.PercentageBonus(bonus_list[1])

    class FixedBonus:    #定义固定加成的计算方法，
        def __init__(self, value:float):  #首先，value其实就是a
            self.value = value

        def calc(self, base:float) -> float:    #定义一个计算函数，需要一个基础值变量base，这个变量可以是外部赋予的，输出的是base + a
            return base + self.value

    class PercentageBonus:   #定义百分比加成的算法
        def __init__(self, value:float):  #这里面的value其实就是b
            self.value = value

        def calc(self, base:float) -> float: #定义一个计算函数，需要一个基础值变量base，这个变量是外部赋予的，输出的base * (1+b)
            return base * (1 + self.value)

    def calc(self, base:float) -> float:   #在Bonus类下面定义一个计算函数，需要一个基础值变量base，这个变量是外部赋予的，然后开始计算
        base_with_perc = self.perc.calc(base)   #先计算百分比，
        final_value = self.fix.calc(base_with_perc)     #计算完之后再加上固定值
        return final_value          #最后输出的是最终值

class Character:
    def __init__(self, config, stat_dict1=None, stat_dict2=None, stat_dict3 = None, action_dict=None):     #config以后会是一个字典，而里面的内容应该是字典中的一个键，用对应键值去取值。
        '''
        Character这个类，需要初始化的时候输入以下几个dict
            1、config，是一个dict，里面记录了角色的配置信息，这些信息会分别发放到Character下面的information、skill、build、equipment_Position以及minor_statement里面
            2、stat_dict1,
            3、stat_dict2,
            4、stat_dict3,
            5、action_dict，用于初始化Action类
        '''
        #下面这个代码，允许这个方法只提供config参数的情况下，顺利调用Character。
        if stat_dict1 is None:
            stat_dict1 = self.default_stat_dict1()
        if stat_dict2 is None:
            stat_dict2 = self.default_stat_dict2()
        if stat_dict3 is None:
            stat_dict3 = self.default_stat_dict3()

        '''
        调用的时候，要用前面的小写，不能用后面的大写。
        比如：XXXX.information.name
             XXXX.skill.normal_attack
        '''

        self.information = self.Information(config['id'], config['name'], config['level'], config['talent'])

        self.skill = self.Skill(config['unique_skill'], config['normal_attack'], config['dash_skill'], config['support_skill'], config['special_skill'], config['qte_skill'])
        
        self.build = self.Build(config['weapon'], config['weapon_level'], config['refinement'], 
                                config['equipment_set4'], config['equipment_set2_a'], config['equipment_set2_b'], config['equipment_set2_c'])
        
        self.equipment_Position = self.Equipment_Position(config['position1'], config['position2'], config['position3'], config['position4'], config['position5'], config['position6'])
        
        self.minor_statement = self.Minor_statement(config['sum'], config['hp'], config['attack'], config['defense'], 
                                                    config['hpper'], config['atkper'], config['defper'], 
                                                    config['cr'], config['cd'], config['elementmystery'], config['pendelta'])
        
        self.statement = self.statementbasic(stat_dict1)
        
        self.bonus = self.statementBonus(stat_dict2)
        
        self.outside = self.StatementOutside(stat_dict3)

        self.action = self.Action(action_dict)

    '''
    下面这两个@staticmethod代码块，
    写的就是不提供dict1和dict2的情况下的默认配置。
    '''
    @staticmethod
    def default_stat_dict1():
        keys = ['hp', 'atk', 'defs', 'bs', 'cr', 'cd', 'eap', 'em', 'pr', 'pd', 'spr', 'spgr', 'spm', 'phy', 'fir', 'ice', 'ele', 'eth']
        return {key: 0 for key in keys}
    @staticmethod
    def default_stat_dict2():
        keys = ['hp', 'atk', 'defs', 'bs', 'cr', 'cd', 'eap', 'em', 'pr', 'pd', 'spr', 'spgr', 'spm', 'phy', 'fir', 'ice', 'ele', 'eth']
        return {key: [0, 0] for key in keys}
    @staticmethod
    def default_stat_dict3():
        keys = ['hp', 'atk', 'defs', 'bs', 'cr', 'cd', 'eap', 'em', 'pr', 'pd', 'spr', 'spgr', 'spm', 'phy', 'fir', 'ice', 'ele', 'eth']
        return {key: [0, 0] for key in keys}
    



    class Information:  #角色的基本信息
        def __init__(self, id, name, level, talent):
            self.id = id
            self.name = name
            self.level = int(level)
            self.talent = int(talent)

    class Skill:        #角色技能等级
        def __init__(self, unique_skill, normal_attack, dash_skill, support_skill, special_skill, qte_skill):
            self.unique_skill = unique_skill
            self.normal_attack = normal_attack    
            self.support_skill = support_skill
            self.dash_skill = dash_skill
            self.special_skill = special_skill            
            self.qte_skill = qte_skill

    class Build:    #角色的装备，音擎，四件套、二件套
        def __init__(self, weapon, weapon_level, refinement, equipment_set4, equipment_set2_a, equipment_set2_b, equipment_set2_c):
            self.weapon = weapon
            self.weapon_level = weapon_level
            self.refinement = refinement
            self.equipment_set4 = equipment_set4
            self.equipment_set2_a = equipment_set2_a
            self.equipment_set2_b = equipment_set2_b
            self.equipment_set2_c = equipment_set2_c
    
    class Equipment_Position:   #主词条
        def __init__(self, position1, position2, position3, position4, position5, position6):
            self.position1 = position1
            self.position2 = position2
            self.position3 = position3
            self.position4 = position4
            self.position5 = position5
            self.position6 = position6

    class Minor_statement:      #副词条，这里指的是数量。
        def __init__(self, sum, hp, atk, defend, hpper, atkper, defper, cr, cd, elementmystery, pendelta):
            self.sum = sum
            self.hp = hp
            self.atk = atk
            self.defend = defend
            self.hpper = hpper
            self.atkper = atkper
            self.defper = defper
            self.cr = cr
            self.cd = cd
            self.elementmystery = elementmystery
            self.pendelta = pendelta
    class statementbasic:
        def __init__(self, stat_dict):      # 这是一个字典，键值是下面的内容，
            self.hp = stat_dict['hp']       # 生命值
            self.atk = stat_dict['atk']     # 攻击力
            self.defs = stat_dict['defs']   # 防御力
            self.bs = stat_dict['bs']       # 基础值
            self.cr = stat_dict['cr']       # 暴击率
            self.cd = stat_dict['cd']       # 暴击伤害
            self.eap = stat_dict['eap']     # 异常掌控
            self.em = stat_dict['em']       # 异常精通
            self.pr = stat_dict['pr']       # 穿透率
            self.pd = stat_dict['pd']       # 穿透值
            self.spr = stat_dict['spr']     # 能量自动回复
            self.spgr = stat_dict['spgr']   # 能量获得效率
            self.spm = stat_dict['spm']     # 能量上限
            self.phy = stat_dict['phy']     # 物理伤害加成
            self.fir = stat_dict['fir']     # 火属性伤害加成
            self.ice = stat_dict['ice']     # 冰属性伤害加成
            self.ele = stat_dict['ele']     # 电属性伤害加成
            self.eth = stat_dict['eth']     # 以太属性加成     
    class statementBonus:       # 记录加成的属性
        def __init__(self, stat_dict):      # 这是一个字典，键值是下面的内容，
            self.hp = stat_dict['hp']       # 生命值
            self.atk = stat_dict['atk']     # 攻击力
            self.defs = stat_dict['defs']   # 防御力
            self.bs = stat_dict['bs']       # 基础值
            self.cr = stat_dict['cr']       # 暴击率
            self.cd = stat_dict['cd']       # 暴击伤害
            self.eap = stat_dict['eap']     # 异常掌控
            self.em = stat_dict['em']       # 异常精通
            self.pr = stat_dict['pr']       # 穿透率
            self.pd = stat_dict['pd']       # 穿透值
            self.spr = stat_dict['spr']     # 能量自动回复
            self.spgr = stat_dict['spgr']   # 能量获得效率
            self.spm = stat_dict['spm']     # 能量上限
            self.phy = stat_dict['phy']     # 物理伤害加成
            self.fir = stat_dict['fir']     # 火属性伤害加成
            self.ice = stat_dict['ice']     # 冰属性伤害加成
            self.ele = stat_dict['ele']     # 电属性伤害加成
            self.eth = stat_dict['eth']     # 以太属性加成
    class StatementOutside:  
        '''
        由于在公测版本中，动态的基础属性加成被挪到了括号外面，也就说
        XXX秒内增加XX%攻击力
        会和场外的站街攻击力总值进行交互，
        所以新建一个statementOutside类，用来记录角色的站街属性
        这一段数值会从计算表的B33:T33范围中获取，
        '''
        def  __init__(self, stat_dict):
            self.hp = stat_dict['hp']       # 生命值
            self.atk = stat_dict['atk']     # 攻击力
            self.defs = stat_dict['defs']   # 防御力
            self.bs = stat_dict['bs']       # 基础值
            self.cr = stat_dict['cr']       # 暴击率
            self.cd = stat_dict['cd']       # 暴击伤害
            self.eap = stat_dict['eap']     # 异常掌控
            self.em = stat_dict['em']       # 异常精通
            self.pr = stat_dict['pr']       # 穿透率
            self.pd = stat_dict['pd']       # 穿透值
            self.spr = stat_dict['spr']     # 能量自动回复
            self.spgr = stat_dict['spgr']   # 能量获得效率
            self.spm = stat_dict['spm']     # 能量上限
            self.phy = stat_dict['phy']     # 物理伤害加成
            self.fir = stat_dict['fir']     # 火属性伤害加成
            self.ice = stat_dict['ice']     # 冰属性伤害加成
            self.ele = stat_dict['ele']     # 电属性伤害加成
            self.eth = stat_dict['eth']     # 以太伤害加成
    class Action:
        '''
        先设计需要输入的字典的结构，
        在总字典Action_dict中，结构应该是：
        {'NA1':{'id':xxxxx, 'dmgratio':xxxxx, 'stunratio':xxxxx, ...... },
        'NA2':{'id':xxxxx, 'dmgratio':xxxxx, 'stunratio':xxxxx, ...... },
        'SNA1':{'id':xxxxx, 'dmgratio':xxxxx, 'stunratio':xxxxx, ...... },
        'SNA2':{'id':xxxxx, 'dmgratio':xxxxx, 'stunratio':xxxxx, ...... },
        'E':{'id':xxxxx, 'dmgratio':xxxxx, 'stunratio':xxxxx, ...... },
        'E1':{'id':xxxxx, 'dmgratio':xxxxx, 'stunratio':xxxxx, ...... },
        'E_EX':{'id':xxxxx, 'dmgratio':xxxxx, 'stunratio':xxxxx, ...... },
        'E_EX_1':{'id':xxxxx, 'dmgratio':xxxxx, 'stunratio':xxxxx, ...... },
        ........
        }
        这个字典，可以从计算表的固定区域里面读取，属于初始化工作的一环，
        以上字典通过XXX.Action.attack(NA1)进行调用，
        从字典里面提取对应的数据，比如{'id':xxxxx, 'dmgratio':xxxxx, 'stunratio':xxxxx, ...... }，并且将这个数据用于计算
        而当我们不需要角色发动攻击时，那就使用Action.dash或者Action.break或者Action.switch，分别代表闪避，被打断，和换人，
        那么这个action就需要attack，dash，break，switch，四个函数，
        并且，无论是dash还是break或者swtich，这三个本质上也是一个技能，只是数值是固定的，{'id':XXXXXX, 'dmgratio':0, 'stunratio':0, ...... }
        '''
        #首先判定，初始化时有没有给一个dict，如果没有就创建一个空的。
        def __init__(self, action_dict=None):
            if action_dict is not None:     
                self.Action_dict = action_dict
            else:
                self.Action_dict = {}

            # 默认的动作也需要一个完整的库来装数据，只不过赋值都是0
            self.default_actions = {
                'dash': {'id':'Dash', 'Name':'冲刺、闪避', 'OfficialName':'冲刺、闪避', 'DmgRatio':0, 'StunRatio':0, 'SpConsumption':0, 'SpRecovery_hit':0, 'FeverRecovery':0, 'ElementAbnormalAccumlation':0, 'SkillType':0, 'TriggerBuffLevel':0, 'ElementType':0, 'TimeCost':30, 'HitNumber':0, 'DmgRelated_Attributes':'atk', 'StunRelated_Attributes':'bs'},
                'breaked': {'id':'Breaked', 'Name':'被打断', 'OfficialName':'被打断', 'DmgRatio':0, 'StunRatio':0, 'SpConsumption':0, 'SpRecovery_hit':0, 'FeverRecovery':0, 'ElementAbnormalAccumlation':0, 'SkillType':0, 'TriggerBuffLevel':0, 'ElementType':0, 'TimeCost':90, 'HitNumber':0, 'DmgRelated_Attributes':'atk', 'StunRelated_Attributes':'bs'},
                'switch': {'id':'Switch', 'Name':'换人', 'OfficialName':'换人', 'DmgRatio':0, 'StunRatio':0, 'SpConsumption':0, 'SpRecovery_hit':0, 'FeverRecovery':0, 'ElementAbnormalAccumlation':0, 'SkillType':0, 'TriggerBuffLevel':0, 'ElementType':0, 'TimeCost':20, 'HitNumber':0, 'DmgRelated_Attributes':'atk', 'StunRelated_Attributes':'bs'},
                'bwswitch': {'id':'BackwardSwitch', 'Name':'反向换人', 'OfficialName':'反向换人', 'DmgRatio':0, 'StunRatio':0, 'SpConsumption':0, 'SpRecovery_hit':0, 'FeverRecovery':0, 'ElementAbnormalAccumlation':0, 'SkillType':0, 'TriggerBuffLevel':0, 'ElementType':0, 'TimeCost':20, 'HitNumber':0, 'DmgRelated_Attributes':'atk', 'StunRelated_Attributes':'bs'}
            }
            self.dash = self.Dash()
            self.breaked = self.Breaked()
            self.switch = self.Switch()
            self.bwswitch = self.Bwswitch()
        #定义attack函数，即action.attack
        def attack(self, action_name):

            #如果attack()函数里面的技能名字，给的是Action_dict中的键值，那就输出键值对应的数据，并赋值给action_data，
            if action_name in self.Action_dict:
                action_data = self.Action_dict[action_name]
                return action_data
            
            #如果没有，那就报错，
            else:
                raise ValueError(f"所输入的动作 {action_name} 并不在该角色的技能列表中！！")
        #定义dash动作
        def Dash(self):
            action_data = self.default_actions['dash']
            # Perform calculations using action_data
            return action_data
        
        def Breaked(self):
            action_data = self.default_actions['breaked']
            # Perform calculations using action_data
            return action_data
        
        def Switch(self):
            action_data = self.default_actions['switch']
            # Perform calculations using action_data
            return action_data
        def Bwswitch(self):
            action_data = self.default_actions['bwswitch']
            return action_data


'''Enemy类，

将角色的瞬时属性、基础属性；技能的瞬时属性；乘区囊括在内，
单个类的初始化，需要4个字典，
分为基本信息的EnemyInformation、基础数值的Enemystatement、记录了抗性的EnemyResist；


'''
class Enemy:
    def __init__(self, config):
        self.information = self.EnemyInformation(config)
        self.statement = self.Enemystatement(config)
        self.resist = self.EnemyResist(config)
    class EnemyInformation:
        def __init__(self, config):
            self.id = float(config['ID'])
            self.name = config['Name']
            self.type = config['Type']
            self.level = float(config['Level'])
    class Enemystatement:
        def __init__(self, config):
            self.hp = float(config['Hp'])
            self.atk = float(config['Atk'])
            self.defence = float(config['Def'])
            self.stun = float(config['Stun'])
            self.stundamage_takeratio = float(config['StunDamageTakeRatio'])
            self.stunreset_count = float(config['StunResetCount'])
            self.elementabnormal = float(config['ElementAbnormal'])
    class EnemyResist:
        def __init__(self, config):
            self.phy_resist = float(config['PhyResist'])
            self.fire_resist = float(config['FireResist'])
            self.ice_resist = float(config['IceResist'])
            self.ele_resist = float(config['EleResist'])
            self.eth_resist = float(config['EthResist'])


def get_parameter(prompt, validation_func=None):        #判断函数，prompt是输入参数，而后面的则是条件表达式
    while True:
        value = input(prompt)
        try:
            if validation_func and not validation_func(value):
                print("输入不符合要求，请重新输入。")
                continue
            return value
        except ValueError:
            print("请输入有效的参数。")
'''

enemyset()函数是用来初始化敌人状态的函数，

'''
def enemyset():
    print('当前已激活的敌人配置方案如下：')
    
    #把enemyconfig_dict中的键值提取出来，变成一个列表，放到enemyconfig_key 中
    enemyconfig_key = list(a for a in enemyconfig_dict) 

    #取enemyconfig_key的长度
    enemyconfigcount = len(enemyconfig_key)

    #显示目前所有方案
    for i in range(enemyconfigcount):
        print(f'{i+1}、',enemyconfig_key[i])

    #选择敌人方案序号，并判断输入是否正确
    enemyconfig_number = get_parameter('请输入要选择的敌人配置方案序号：', lambda x: 0 <= int(x) <= enemyconfigcount)
    enemyconfig_number = int(enemyconfig_number)

    enemyconfig_valuelist = enemyconfig_dict[enemyconfig_key[enemyconfig_number - 1]]
    enemyconfig_now = dict(zip(enemysetkeys, enemyconfig_valuelist))
    
    #把怪物属性通过Enemy类进行实例化，并且放到Enemyactive里面
    Enemyactive = Enemy(enemyconfig_now)
    print(f'当前激活的敌人是：{Enemyactive.information.name}')
    return Enemyactive
Enemyactive = enemyset()



'''Event说明
character是参与角色的变量，是Character类的实例化对象，
activbuff_list 是一个列表，记录了整个模拟中可能会用到的所有buff。
actionname 是动作名，比如，NA_1、NA_2、E_EX等，利用这个名称，去已经实例化的类中选取对应的技能信息，进行比较。
standard_key是动作的判断标准，是一个字典，里面的键值如下(这些键值记录在一个叫standard_key的list里面，该list和记录技能信息的key列表是一样的)：
['id', 'Name', 'OfficialName', 
'DmgRatio', 'StunRatio', 
'SpConsumption', 'SpRecovery_hit', 'FeverRecovery', 
'ElementAbnormalAccumlation', 
'SkillType', 'TriggerBuffLevel', 'ElementType', 
'TimeCost', 'HitNumber', 
'DmgRelated_Attributes', 'StunRelated_Attributes']
standard_dict 是一个以Standardkey作为键值的字典，记录了该次判断所涉及的信息，以及条件。涉及的项目就填实际值，不涉及的就是0。

effect_dict是一个记录了激活之后效果的字典，其键值就是Event所需的字典的键值，



新思路：
1、把所有需要判断的动作都放在一个actionlist里面
2、把所有待触发的事件 都放在一个csv里面，第一列是buff名称，后面都是触发条件和系数；
3、把待触发事件对应的buff效果，都放在另一个csv里面，第一列是buff名称（和2里面一样），后面都是关联的乘区；
4、
'''
class Event:
    def __init__(self, number, enemy, character, eventinfo_dict, statefix_dict, stateoutsidebonus_dict, muldict):
        self.eventinfo = self.Eventinfomation(number, eventinfo_dict)
        self.statechange = self.StateChange(statefix_dict, stateoutsidebonus_dict, character)
        self.multiplication = self.Multiplication(enemy, character, muldict)
    class Eventinfomation:      #事件的信息
        def __init__(self, number, eventinfo_dict):
            self.eventid = eventinfo_dict['eventid']            #该次事件的ID，一般从1开始计数，
            self.timenow = eventinfo_dict['timenow']            #该次事件发生时的时间点
            self.char = eventinfo_dict['charactername']         #该次事件涉及的角色名
            self.actionname = eventinfo_dict['actionname']      #该次事件中，角色进行的动作的名称，或者索引
            self.number = number                                #该次事件的事件编号
    class StateChange:
        def __init__(self, statefix_dict, stateoutsidebonus_dict, character):
            self.fix = self.Fix(statefix_dict)
            self.outsidebonus = self.OutsideBonus(stateoutsidebonus_dict)
            self.final = self.StateFinal(character, self.fix, self.outsidebonus)
        class Fix:  # 固定加成
            def __init__(self, stat_dict):
                self.hp = stat_dict['hp']  # 生命值
                self.atk = stat_dict['atk']  # 攻击力
                self.defs = stat_dict['defs']  # 防御力
                self.bs = stat_dict['bs']  # 基础值
                self.cr = stat_dict['cr']  # 暴击率
                self.cd = stat_dict['cd']  # 暴击伤害
                self.eap = stat_dict['eap']  # 异常掌控
                self.em = stat_dict['em']  # 异常精通
                self.pr = stat_dict['pr']  # 穿透率
                self.pd = stat_dict['pd']  # 穿透值
                self.spr = stat_dict['spr']  # 能量自动回复
                self.spgr = stat_dict['spgr']  # 能量获得效率
                self.spm = stat_dict['spm']  # 能量上限
                self.phy = stat_dict['phy']  # 物理伤害加成
                self.fir = stat_dict['fir']  # 火属性伤害加成
                self.ice = stat_dict['ice']  # 冰属性伤害加成
                self.ele = stat_dict['ele']  # 电属性伤害加成
                self.eth = stat_dict['eth']  # 以太属性加成

        class OutsideBonus:  # 全局加成
            def __init__(self, stat_dict):
                self.hp = stat_dict['hp']  # 生命值
                self.atk = stat_dict['atk']  # 攻击力
                self.defs = stat_dict['defs']  # 防御力
                self.bs = stat_dict['bs']  # 基础值
                self.cr = stat_dict['cr']  # 暴击率
                self.cd = stat_dict['cd']  # 暴击伤害
                self.eap = stat_dict['eap']  # 异常掌控
                self.em = stat_dict['em']  # 异常精通
                self.pr = stat_dict['pr']  # 穿透率
                self.pd = stat_dict['pd']  # 穿透值
                self.spr = stat_dict['spr']  # 能量自动回复
                self.spgr = stat_dict['spgr']  # 能量获得效率
                self.spm = stat_dict['spm']  # 能量上限
                self.phy = stat_dict['phy']  # 物理伤害加成
                self.fir = stat_dict['fir']  # 火属性伤害加成
                self.ice = stat_dict['ice']  # 冰属性伤害加成
                self.ele = stat_dict['ele']  # 电属性伤害加成
                self.eth = stat_dict['eth']  # 以太属性加成

        class StateFinal:
            def __init__(self, character, fix, outsidebonus):
                self.hp = character.outside.hp * (1 + outsidebonus.hp) + fix.hp  # 生命值
                self.atk = character.outside.atk * (1 + outsidebonus.atk) + fix.atk  # 攻击力
                self.defs = character.outside.defs * (1 + outsidebonus.defs) + fix.defs  # 防御力
                self.bs = character.outside.bs * (1 + outsidebonus.bs) + fix.bs  # 基础值
                self.cr = character.outside.cr * (1 + outsidebonus.cr) + fix.cr  # 暴击率
                self.cd = character.outside.cd * (1 + outsidebonus.cd) + fix.cd  # 暴击伤害
                self.eap = character.outside.eap * (1 + outsidebonus.eap) + fix.eap  # 异常掌控
                self.em = character.outside.em * (1 + outsidebonus.em) + fix.em  # 异常精通
                self.pr = character.outside.pr * (1 + outsidebonus.pr) + fix.pr  # 穿透率
                self.pd = character.outside.pd * (1 + outsidebonus.pd) + fix.pd  # 穿透值
                self.spr = character.outside.spr * (1 + outsidebonus.spr) + fix.spr  # 能量自动回复
                self.spgr = character.outside.spgr * (1 + outsidebonus.spgr) + fix.spgr  # 能量获得效率
                self.spm = character.outside.spm * (1 + outsidebonus.spm) + fix.spm  # 能量上限
                self.phy = character.outside.phy * (1 + outsidebonus.phy) + fix.phy  # 物理伤害加成
                self.fir = character.outside.fir * (1 + outsidebonus.fir) + fix.fir  # 火属性伤害加成
                self.ice = character.outside.ice * (1 + outsidebonus.ice) + fix.ice  # 冰属性伤害加成
                self.ele = character.outside.ele * (1 + outsidebonus.ele) + fix.ele  # 电属性伤害加成
                self.eth = character.outside.eth * (1 + outsidebonus.eth) + fix.eth  # 以太属性加成            


    class Multiplication:       #和事件绑定的乘区
        #首先是增伤区，也是最复杂的区
        def __init__(self, enemy, character, muldict):
            self.dmg = self.Damage_Increase_Zone(character,muldict)
            self.defence = self.Defense_Zone(character, muldict) 
            self.res = self.Resistance_Zone(enemy, muldict)
            self.crit = self.Crit_Zone(character, muldict)
            self.vul = self.Vulnerability_Zone(muldict)
            self.stdmg = self.StunDamage_TakeRatio(enemy, muldict)
            self.special = self.Special_Multiplication_Zone(muldict)
        class Damage_Increase_Zone:
            def __init__(self, character, muldict):
                #元素类增伤
                self.elemental_dmg_bonus = self.Elemental_DMG_Bonus(character, muldict)
                #攻击类增伤，一般这里是0
                self.attack_type = self.Attack_Type(muldict)
                #技能类型增伤
                self.skill_type = self.Skill_Type(muldict)
                #全类型增伤
                self.alldmg = self.All_Dmg(muldict)
            #元素增伤区
            #元素增伤区的计算方式，等于角色面板 + muldict字典中的内容。
            class Elemental_DMG_Bonus:
                def __init__(self, character, muldict):
                    Phybase = character.statement.phy
                    Firebase = character.statement.fir
                    Icebase = character.statement.ice
                    Elebase = character.statement.ele
                    Ethbase = character.statement.eth
                    PhyBonus = BonusCalculate(character.bonus.phy)
                    FireBonus = BonusCalculate(character.bonus.fir)
                    IceBonus = BonusCalculate(character.bonus.ice)
                    EleBonus = BonusCalculate(character.bonus.ele)
                    EthBonus = BonusCalculate(character.bonus.eth)
                    self.phy = PhyBonus.calc(Phybase) + muldict['PhyBonus']
                    self.fire = FireBonus.calc(Firebase) + muldict['FireBonus']
                    self.ice = IceBonus.calc(Icebase) + muldict['IceBonus'] 
                    self.ele = EleBonus.calc(Elebase) + muldict['EleBonus']
                    self.eth = EthBonus.calc(Ethbase) + muldict['EthBonus']
            #攻击类型区，一般为0
            class Attack_Type:
                def __init__(self, muldict):
                    self.attacktype = float(muldict['AttackType'])
            #技能种类
            class Skill_Type:
                def __init__(self, muldict):
                    #定义各种标签！
                    self.na = float(muldict['NormalAttack'])                       #普攻
                    self.special = float(muldict['SpecialSkill'])                  #特殊技
                    self.exspecial = float(muldict['ExSpecial'])                   #强化特殊技
                    self.dasha = float(muldict['Dashattack'])                      #冲刺攻击
                    self.avoida = float(muldict['Avoidattack'])                    #闪避反击
                    self.qte = float(muldict['QTE'])                               #连携技
                    self.q = float(muldict['Q'])                                   #大招
                    self.bh = float(muldict['BHaid'])                              #受击支援
                    self.parry = float(muldict['Parryaid'])                        #回避支援
                    self.assault = float(muldict['Assaultaid'])                    #支援突击
                    self.elementalstatus = float(muldict['ElementalStatus'])       #元素异常倍率
            #全增伤标签
            class All_Dmg:
                def __init__(self, muldict):
                    self.value = float(muldict['ALLDMG'])                         #全增伤        
        #防御区
        class Defense_Zone:
            #防御区有众多参数，有直接和怪物属性挂钩的，也有和其他内容挂钩的
            #这里涉及的内容有：
                #固定值：敌方基础防御，敌方等级，攻击方等级（以及依靠改数据计算出的攻击方等级基数）
                #动态属性： 攻击方穿透率，攻击方穿透值，敌方减防，固定防御
            def __init__(self, character, muldict):
                self.defup = muldict['Defincrease']
                self.defdown = muldict['Defdecrease']
                self.deffix = muldict['Deffix']
                pendeltabasic = character.statement.pd
                pendelta_ratiobasic = character.statement.pr
                pendelta_bonus = BonusCalculate(character.bonus.pd)
                pendelta_ratiobonus = BonusCalculate(character.bonus.pr)
                self.pendelta = pendelta_bonus.calc(pendeltabasic) + muldict['Pendelta']
                self.pendelta_ratio = pendelta_ratiobonus.calc(pendelta_ratiobasic) + muldict['Pendelta_Ratio']
        #抗性区
        class Resistance_Zone:
            def __init__(self,enemy, muldict):
                #抗性区涉及的三个参数，其中，“受击方抗性”是一个固定值，和怪物种类有关，与伤害类型标签相似，这个参数共有五个类型，
                #分别是：PhyRes, FireRes, IceRes, EleRes, EthRes, ALL
                #此处应该是一个字典。
                #当然，这一个系列里面应该都是字典，因为是和抗性相关的，字典的键值是一样的，
                self.ele_res = self.Element_Res(enemy, muldict)
                self.ele_reduce = muldict['Element_reduce']             #受击方全抗性降低
                self.ele_penetrate = muldict['Element_penetrate']       #攻击方全抗性穿透
            #敌人元素抗性（动态）
            class Element_Res:  #受击方抗性
                def __init__(self, enemy, muldict):
                    self.phy = enemy.resist.phy_resist + muldict['PhyRes']
                    self.fire = enemy.resist.fire_resist + muldict['FireRes']
                    self.ice = enemy.resist.ice_resist + muldict['IceRes']
                    self.ele = enemy.resist.ele_resist + muldict['EleRes']
                    self.eth = enemy.resist.eth_resist + muldict['EthRes']
                    self.all = muldict['AllRes']
        #双爆区
        class Crit_Zone:
            #这个区的数据，只有双爆需要参与，而且一般计算的时候，是由随机数系统来控制暴击的，和这个区无关。
            #只有在计算期望的时候，才需要用到这个区的属性。
            #期望的计算 = 1 + 暴击率 * 暴击伤害
            def __init__(self, character, muldict):
                CRbasic = character.statement.cr         #暴击率基础值
                CRBounus = character.bonus.cr        #暴击率加成，列表
                CDBasic = character.statement.cd         #爆伤基础值
                CDBonus = character.bonus.cd         #爆伤加成，列表
                crictR = BonusCalculate(CRBounus)            #暴击率加成实例化，传到crictR里面
                crictD = BonusCalculate(CDBonus)             #爆伤加成实例化，传到crictD里面
                self.cbc = muldict['Chance_to_be_crit']      #被暴击的几率
                self.dfc = muldict['Damage_from_crit']       #受到的爆击伤害。
                self.cr = crictR.calc(CRbasic)               #计算最终的暴击率值
                self.cd = crictD.calc(CDBasic)               #计算最终的暴击伤害值                                
                #最终的双爆期望，这才是我们需要的数据
                self.CriticalExpect = 1 + (self.cr + self.cbc) * (self.cd + self.dfc)
        #减、易伤区
        class Vulnerability_Zone:
            def __init__(self, muldict):
                self.di = muldict['Dmgtaken_Increase']      #受到伤害增加
                self.dd = muldict['Dmgtaken_Decrease']      #受到伤害减少
                #直接输出计算结果，这个乘区的整体数字！
                self.result = 1 + self.di - self.dd
        #失衡易伤区
        class StunDamage_TakeRatio:
            def __init__(self, enemy, muldict):
                #失衡易伤倍率
                self.st = muldict['StunDamage_TakeRatio'] + enemy.statement.stundamage_takeratio
                #易伤倍率增加
                self.std = muldict['StunDamage_TakeRatio_Delta']
        #特殊乘区
        class Special_Multiplication_Zone:
            def __init__(self, muldict):
                self.value = muldict['Special_Multiplication_Zone']    

'''
buff类，主要用于控制buff的开关。
这个buff，是一个跟随着事件进行的buff字典，
每次事件进行后，都会进行buff的判断，更新buff状态，然后再进入下一轮事件。
而每一次action开始之前，都要遍历目前所有已经激活的buff，并且计算最终属性。
这意味着，action本身的属性不会变化。


'''
class Buff:
    def __init__(self, buffdict):
        self.buffname = buffdict['BuffName']
        self.bufffrom = buffdict['from']
        self.exsist = buffdict['exsist']                        #buff是否参与了计算，即是否允许被激活
        self.name = buffdict['name']                            #buff的名字
        self.active = buffdict['active']                        #buff当前的激活状态
        self.durationtype = buffdict['durationtype']            #buff的持续时间类型，如果是True，就是有持续时间的，如果是False，就没有持续时间类型，属于瞬时buff。
        self.maxduration = buffdict['maxduration']              #buff最大持续时间    
        self.duration = buffdict['duration']                    #buff当前剩余时间
        self.maxcount = buffdict['maxcount']                    #buff允许被叠加的最大层数
        self.count = buffdict['count']                          #buff当前层数
        self.step = buffdict['incrementalstep']                 #buff的自增步长
        self.prejudge = buffdict['prejudge']                    #buff的判定类型，True是提前判定类型，即未命中先有buff；False是命中后类型，当前动作不受影响。
        self.fresh = buffdict['freshtype']                      #buff的刷新类型，True是刷新层数时，刷新时间，False是刷新层数是，不影响时间。
        self.alltime = buffdict['alltime']                      #buff的永远生效类型，True是无条件永远生效，False是有条件
        self.hitincrease = buffdict['hitincrease']              #buff的层数增长类型，True就是命中一次就增长一层，False就是一个招式增长一层。
        self.increasecd  = buffdict['increaseCD']               #buff的叠层内置CD
        self.ready = buffdict['readyto_increase']               #buff的可叠层状态，如果是True，就意味着是内置CD结束了，可以叠层，如果不是True，就不能叠层。
        self.starttime = 0
    def __repr__(self):             #通报buff情况
        return f"Buff(buff名称：{self.name!r}, 是否激活：{self.exsist!r}, 持续时间：{self.duration!r}s, 激活状态：{self.active!r}, 层数：{self.count!r})"
    def EndBuff(self):
        self.duration = 0
        self.count = 0
        self.active = False
    #用于更新buff的刷新状态，来看看buff是否准备就绪。
    def Update(self, timenow):
        if not self.ready:
            if timenow - self.starttime >= self.increasecd:
                self.ready = True
    #这个就是用来更新buff的层数了。
    def Count(self, hitnumber, timecost):
        if self.ready:
            if self.hitincrease:
                if self.increasecd > 0:
                    self.count = min(self.maxcount, self.count + math.floor(self.increasecd/(timecost/hitnumber)))
                else:
                    self.count = min(self.maxcount, self.count + hitnumber)
            else:
                self.count = min(self.maxcount, self.count + self.step)
            self.ready = False
            
    


while True:
    characternumber = input("请输入参与计算的角色数量：")       #输入角色数量
    try:
        characternumber = int(characternumber)
        if characternumber >3 or characternumber<1:
            print("输入错误，角色数量最小为1，最大为3，请重新输入。")
            continue
        else:
            print(f"当前参与计算的角色数量为：{characternumber}")
            break
    except ValueError:
        print("请输入有效的整数。")
        continue





def character_set():        #角色基础配置更新
    listnumber = len(characterconfig_dict)
    keys_list = list(characterconfig_dict.keys())
    print('现有配装方案如下，请选择：')
    for i in range(listnumber):
        print(i+1,'、',keys_list[i])

    for k in range(characternumber):
         while True:
            setnumber = get_parameter(f'请输入需要导入的第{k + 1}位角色的配装方案序号：', lambda x: x.isdigit() and 0 < int(x) <= listnumber)       #输入需要的配装方案代号
            setnumber = int(setnumber)
            if setnumber <= listnumber:
                selected_key = keys_list[setnumber - 1]


                print(f"已选择的配装方案为：{selected_key}")        # 在这里可以根据 selected_key 进行进一步操作，例如更新角色的配置，
                                                                  # 这个变量里面记录了当前循环的dict里面的对应位置的键值，
                                                                  #=====>比如“标准30词条0+1艾莲”<=====
                
                keybox.append(selected_key)                       #把每次用于检索的selectkey 都放到keybox列表中，
                characterconfig_now = characterconfig_dict[selected_key]        #把总配装方案dict中的第k个键对应的值（是一个列表）拿出来，放到这个now变量里面，
                characterbox_now[k] = characterconfig_dict[selected_key][1] #按顺序记录激活的角色

                #config_list.append(characterconfig_now)           #把每次从配置列表里面取出来的select_key对应的键值（是一个{……}）放到外面的config_list里面//这一行暂时弃置
            
                for i in range(34): 
                    sheet_basic.range(characterconfig_range[i]).value = characterconfig_now[i]
                    #把now变量里面的内容，填写到range列表中记录的一个个位置里，
                    
                characterconfig_now = [convert_to_float(item) for item in characterconfig_now]      #把里面能转成数值的项目，转化成数值

                configdict = dict(zip(keys,characterconfig_now))        #角色配置信息提炼出来的字典，

                calculate_box[selected_key] = configdict                #信息汇总到计算用的dict中,里面的内容是========>{配装方案名:{id:xxx, name:xxx, ......}}


                characterbase_statlist = sheet_basic.range('C20:T20').value                 #临时用来存储角色属性的list
                characterbase_statdict = dict(zip(statementkeys,characterbase_statlist))     #把list里面的数值，和statementkeys里面的键值一一对应，装入dict里面
                statementbasic_box[selected_key] = characterbase_statdict                    #在总字典中录入信息，即{配装方案名字：{hp:xxx, atk:xxx ……}}
                bonuslist = []      #令一个空list，用来2合1

                fixbonus = sheet_basic.range('C31:T31').value               #令一个空list，用来装固定加成
                percentbonus = sheet_basic.range('C32:T32').value           #令一个空list，用来装百分比加成
                statementoutside_lsit = sheet_basic.range('C33:T33').value   #令一个空list，用来装角色站街面板
                for i in range(len(statementkeys)):
                    bonuslist.append([fixbonus[i],percentbonus[i]])
                bonusdict = dict(zip(statementkeys,bonuslist))        #另一个空的dict，用来和bonuslist进行zip
                statementBonus_box[selected_key] = bonusdict         #封包到statementBonus里面去，即{配装方案名字：{hp:[a,b], atk:[a,b], ……}}
                statementoutside_dict = dict(zip(statementkeys, statementoutside_lsit))    #打包成字典，{hp:xxx, atk:xxx, ……}
                statementoutside_box[selected_key] = statementoutside_dict                #进一步打包成{配装方案名:{hp:xxx, atk:xxx, ……}}
                #接下去的内容，是要准备为角色录入技能数据。
                #首先是从表里面拿出来，我们从sheet_basic  也就是“配装&面板”表中，获取A42单元格的内容，那里，记录着取值范围，这个取值范围的值，本来是记录了有多少个技能被调用出来了，
                #而这个值，直接决定了查阅数值的循环次数。

                #第一步，新建一个空的字典，一会儿用来装拿出来的数据。
                #当然，如果我们是第二次来到这里，那么就应该是清空旧字典中的内容了，应新的空字典去装新的角色。
                skillcopydata = {}

                #把A42的那个取值范围拿出来，并且转化为int
                count = sheet_basic.range('A40').value
                count = int(count)
                print(f'本次录入的角色技能共有{count}个！')


                #开始循环。
                for i in range(count):
                    
                    #起始行数
                    rowstart = 42

                    #终止行数，第1次循环，那就是42，第2次循环，那就是43，以此类推，
                    rownow = rowstart + i

                    #用来装技能数据的字典，新建一个键值，键值的内容是'A'列中记录的技能名，并且对这个键值进行赋值，赋值的内容是一个zip打包过后的新字典
                        #首先，把当前这一行的B~Q列的内容抄下来，
                        #用zip语法，和早在前面新建好的列表  skill_stat_keys 进行一一对应的打包，变成了一个记录了单一技能信息的字典，比如
                        #{普攻第一段：{攻击倍率：xxxxx, 失衡倍率：xxxxx, ……}}
                        #在当前循环结束后，我们应该会得到一个大字典，其中记录了这个角色的所有技能信息，每个技能都有自己的各种倍率、回能信息，
                    
                    
                    skillcopydata[sheet_basic.range(f'A{rownow}').value] = dict(zip(skill_stat_keys,sheet_basic.range(f'B{rownow}:Q{rownow}').value))


                    #print(f'加载第{i+1}个技能： ',skillcopydata[sheet_basic.range(f'A{rownow}').value]['id'])   #实时通报加载进度
                


                #在循环结束后，单个角色的信息录入来到了尾声，我们需要把刚才循环20~40次才得到的大型技能信息表，传递到循环外面，也就是用最终字典activcharacter_allskilldict来装他们，键值就是角色名
                #于是，在该角色信息录入的末尾，我们在最终字典中加入了如下信息：
                #{角色配装方案名：{技能信息1，技能信息2，技能信息3，}}
                activcharacter_allskilldict[selected_key] = skillcopydata
                break
            else:
                print("输入不符合要求，请重新输入。")
                continue
        
    #然后把字典中的每个键值对应的元素，传递到character类
    for i in range(characternumber):        
        activ_characterbox[i] = Character(calculate_box[keybox[i]],
                                          statementbasic_box[keybox[i]],
                                          statementBonus_box[keybox[i]],
                                          statementoutside_box[keybox[i]],
                                          activcharacter_allskilldict[keybox[i]])
    return characterbox_now

wb.save
#wb_t.save
character_set()
print(f'现已激活的角色列表为：{characterbox_now}')


character_a = activ_characterbox[0]
character_b = activ_characterbox[1]
character_c = activ_characterbox[2]


judgefilepath = 'F:\我的\镜像相关\绝区零公测后\ZZZ总数据库及计算\触发判断.csv'
effectfilepath = 'F:\我的\镜像相关\绝区零公测后\ZZZ总数据库及计算\Buff效果.csv'
exsistfilepath = 'F:\我的\镜像相关\绝区零公测后\ZZZ总数据库及计算\激活判断.csv'
judgefile = pd.read_csv(judgefilepath, index_col='BuffName')
effectfile = pd.read_csv(effectfilepath, index_col='BuffName')
exsistfile = pd.read_csv(exsistfilepath, index_col='BuffName')
exsistfile['active'] = exsistfile['active'].map({'FALSE': False, 'TRUE': True})
allbuff_list = exsistfile.index.tolist()    #把索引列转化为list

#确认exsistfile文件中，exsist列是否是布尔值，如果不是，则转换为布尔值。
if 'exsist' not in exsistfile.columns:
    exsistfile['exsist'] = False
else:
    exsistfile['exsist'] = exsistfile['exsist'].astype(bool)

allbuff_dict = {}
allbuff_dict_char = {}

def Charbufflist(characterbox_now, characternumber):
    for charnumber in range(characternumber):    #这是为了将参与计算的每个角色的buff列表都单独放开，
        charbuff_minor = {}
        #创建检查用的配置单
        testlist = []
        for a in configcheck_positionlist:
            testlist.append(characterconfig_dict[keybox[charnumber]][a])
        #检查激活状态的循环，如果buff的from，在配置单中，那么就修改exsist为True，否则就为False
        for i in allbuff_list:
            row_dict = {}           #把上个循环中用的dict清理干净。
            row_index = i           #把buff名称提出来

            row_data = exsistfile.loc[i]                #根据buff名称提取一整行数据，但是这一行数据不包含buff名称
            row_dict = row_data.to_dict()               #先打包成字典，
            row_dict['BuffName'] = row_index            #字典新增一个键值，buff名称。
            charbuff_minor[i] = Buff(row_dict)          #对allbuffdict中的每一个buff的键值进行Buff类的实例化
            #对exsist属性进行初始化
            if exsistfile.loc[i, 'from'] in testlist:
                charbuff_minor[i].exsist = True
            else:
                charbuff_minor[i].exsist = False
        allbuff_dict_char[characterbox_now[charnumber]] = charbuff_minor

    return allbuff_dict_char
Charbufflist(characterbox_now, characternumber)



'''
√  激活检查 
√  对allbuff_list中的所有buff进行类的实例化，赋予它们属性。


接下来是计算模块！
针对每一个动作，在动作dict里面进行Event实例化

1、遍历allbuff_dict，对其中的每一个buff进行激活检查，确认本次动作受益的buff是哪些
2、将本次动作受益的buff，装入列表中（该列表每次循环都重置），形成临时的bufflist
3、遍历bufflist，计算里面所有的buff提供的加成
4、输出最终伤害
5、更新buff状态，结算buff时间，修改buff的active、count属性。
6、进入下一个循环

'''

'''
TODO:
    1、判断谁是前台角色，谁是后台角色，谁是下一顺位的角色。
    2、留好角色的独立逻辑的接口，角色的单独逻辑，会根据怪物的情况，生成下一个动作。
    3、确定给队友、怪物的buff类技能，到底放在什么内容里面来做。
    4、
    5、

    
基本逻辑：在每次循环之前，都要获取状态，确认当前战斗的阶段，怪物的状态，角色的资源等情况，
根据当前的状态，将参数输入到角色的动作逻辑函数中，得出下一个动作。
    1、获取当前的目标状态，目标状态包括：存活标志，参与血量（百分比），失衡百分比，
    2、获取当前的角色状态，角色状态包括：前台角色、下一个角色、上一个角色；角色特殊资源，角色能量，被打断状态，切人CD，
    3、角色的动作逻辑函数需要接收的参数有：当前的战斗阶段（攻坚期、失衡期、攻坚期（收尾））；战斗终止的信号；当前的资源量（能量，特殊资源），特别是后台角色的能量，应该时刻处于被调取的状态，
'''


#Enemyactive, character, eventinfo_dict, statefix_dict_default, stateoutsidebonus_dict_default, muldict_default
actionlist_test = ['BH_Aid', 'RA_FC', 'SNA_1', 'SNA_2', 'SNA_3_FC', 'dash', 'switch','NA_1' ,'NA_2' ,'bwswitch' ,'SNA_1', 'SNA_2', 'SNA_3_FC' ]  #  'RA_FC', 'NA_2', 'NA_3_FC','RA_FC', 'SNA_1', 'SNA_2', 'SNA_3_FC' 'NA_1', 'NA_2', 'NA_3_FC', 'NA_1', 'NA_2', 'NA_3_FC'
eventinfokey_list = ['eventid', 'timenow', 'charactername', 'actionname']
buffactivekey_list = ['id', 'OfficialName', 'SpConsumption', 'SpRecovery_hit', 'FeverRecovery', 'ElementAbnormalAccumlation', 'SkillType', 'TriggerBuffLevel', 'ElementType', 'TimeCost', 'HitNumber', 'DmgRelated_Attributes', 'StunRelated_Attributes']
allaction_dict = {}
# 文件名
file_name = 'log.xlsx'
def EventCreat(actionlist, character):
# 清空log.xlsx文件
    if os.path.exists(file_name):
        try:
            # 创建一个空的DataFrame
            empty_df = pd.DataFrame()
            
            # 写入到log.xlsx文件，清空其内容
            empty_df.to_excel(file_name, index=False)
        except PermissionError:
            print(f"无法访问文件 {file_name}。请确认文件未被其他程序占用。")
            exit(1)  # 退出程序
    eventcount = 0
    buffinfo_key = ['allmatch', 'name', 'duration', 'ready', 'count']
    timenow = 0
    current_index = 0
    
    

    for action in actionlist:  
        (character_now, character_before, character_next), current_index = process_action(characterbox_now, action, current_index)
        print(f'当前前台角色是：{character_now}, 上一位角色是：{character_before}, 下一位角色是：{character_next}, 当前动作是：{action}')
        
        #载入当前角色的buff列表
        allbuff_dict = allbuff_dict_char[character_now]
        
        #时间变化模块
        timecost = 0
        timecost_dict = {'dash':30, 'breaked':90,'switch':20, 'bwswitch':20}
        if action not in ['dash', 'breaked', 'switch', 'bwswitch']: 
            timecost = character.action.attack(action)['TimeCost']/60
            hitnumber = float(character.action.attack(action)['HitNumber'])
        else:
            timecost = timecost_dict[action]/60
            hitnumber = 0
        
        buffinfodict_now = {}                           #用于记录buff 的基本信息的——是否通过匹配、buff内容、剩余时间、目前层数
        activebufflist_now = []                         #用于每个动作的激活buff列表。
        character_statementdic_now = {}                 #用于记录每个动作事件，的当前属性。
        Ostatedict_now = stateoutsidebonus_dict_default  #每个动作初始化的时候，都要从default字典中抄一份全是0的字典作为初始化。但是这个default字典是可以变的，将被用于buff字典中的迭代。
        Fstatedict_now = statefix_dict_default
        muldict_now = muldict_default                   #每个动作初始化的时候，都要从default字典中抄一份全是0的字典作为初始化。但是这个default字典是可以变的，将被用于buff字典中的迭代。

        eventinfo_dict = {} #先把上一个循环的eventdict清空
        eventcount += 1
        #现场搓一个现成的eventdict
        eventinfo_list = [eventcount, timenow, character.information.name, action]
        eventinfo_dict = dict(zip(eventinfokey_list, eventinfo_list))
        actioncount_now = {action: 0 for action in actionlist}
        actioncount_now[action] += 1 
        actionkey_now = f'{action}_{actioncount_now[action]}'

        allaction_dict[actionkey_now] = Event(eventcount, Enemyactive, character, eventinfo_dict, Fstatedict_now, Ostatedict_now, muldict_now)
        eventnow = allaction_dict[actionkey_now]

        for buff in allbuff_list:
            #print(f'当前进行判断的buff是：{buff}')
            buffnow = allbuff_dict[buff]
            all_none_empty_list = []        #触发条件box，记录了buff触发所需要的所有的前置条件。   
            all_match = False               #每个buff判断开始前， 初始化这个变量为false
            if buffnow.exsist:   #首先判断，buff是处于被激活状态的
                if buffnow.alltime == False:
                    none_empty_column_indices = judgefile.loc[buff].dropna().index.to_list()

                    #将csv的每个非空值的键值变成一个list，并将list添加到allnone....中，这样我们就能获得该buff的所有触发条件的判断。

                    all_none_empty_list.extend(none_empty_column_indices)   
                    #上面这个if的作用：是知道每一个buff的判断条件，可能是单个的，也可能是多个的，所以，我必须保证action的每个属性都符合要求，才能输出True。                
                    for i in all_none_empty_list:
                        if action not in ['dash', 'breaked', 'switch', 'bwswitch']:   # 如果动作不是冲刺、打断、切人
                            if character.action.attack(action)[i] != judgefile.loc[buff, i]:
                                all_match = False
                                break
                        else:
                            if getattr(character.action, action)[i] != judgefile.loc[buff, i]:
                                all_match = False
                                break
                    else:                       # 如果 for 循环没有被 break 终止，则设置 all_match 为 True
                        all_match = True

                else:
                    all_match = True
                #print(f'{buff}的all_match状态是：{all_match}')
                buffnow.Update(timenow)             # 用来更新buff的刷新状态，判断内置CD是否转完了。
                if all_match:                       # 如果buff的触发判定过了，则buff触发。
                                 
                    buffnow.active = True
                    if buffnow.ready:
                        buffnow.starttime = timenow
                    
                    if buffnow.durationtype:
                        #如果buff已经确认要激活，并且是持续时间类buff，并且是提前判定类的buff，持续时间<=0时，
                        #其实就是新触发的buff，所以要更新一个新的buff时间，
                        #由于这个buff是提前触发的，所以当前循环周期就要减去一次动作用时。
                        if buffnow.duration > 0:    #如果已经有buff在持续，
                            if buffnow.fresh:     #如果buff的refresh种类是True，也就是buff层数刷新会伴随着时间刷新，

                                #当确认buff可以被刷新，那么首先就是刷新判定。
                                if buffnow.prejudge:
                                    buffnow.duration = buffnow.maxduration - timecost
                                else:
                                    buffnow.duration = buffnow.maxduration
                                
                                buffnow.Count(hitnumber, timecost)

                            else:
                                #如果buff的refresh种类是False，也就是buff层数无论多高，到点结束，
                                if buffnow.duration - timecost <= 0:
                                    buffnow.EndBuff()
                                else:
                                    buffnow.duration = buffnow.duration - timecost
                                    buffnow.Count(hitnumber, timecost)
                        else:
                            buffnow.Count(hitnumber, timecost)
                            if buffnow.prejudge:
                                buffnow.duration = buffnow.maxduration - timecost
                            else:
                                buffnow.duration = buffnow.maxduration
                            '''
                            TODO:
                            该代码目前无法解决“层数衰退”的问题，该问题可能涉及的参数有：衰退周期，衰减层数，以及可能需要一个“衰退状态”的临时判定参数。
                            这部分功能专门用来针对那些层数衰减时不马上掉完的buff，一层一层掉的那种
                            比如 咒术洪流 和 炽焰连击 的类似buff；
                            
                            TODO:
                            同时，这部分代码页无法解决“延迟生效”的问题，类似于妮可的buff或者其他的具有前摇时间的buff；
                            '''
                    else:
                        buffnow.Count(hitnumber, timecost)   
                    activebufflist_now.append(buffnow)
                    buffinfodict_now[buffnow.buffname] = dict(zip(buffinfo_key, [all_match, buffnow.name, buffnow.duration, buffnow.ready, buffnow.count]))
                else:
                    if buffnow.durationtype:
                    #这是没有匹配上的情况，
                        if buffnow.duration >0: 
                            buffnow.active = True       
                            #allmatch 是False，只能意味着这一个动作的判定没有通过，并不能直接关闭buff，所以还是要判断buff的持续时间。
                            #因为就是会存在，buff判定没过，但是buff还是存在的情况，
                            if buffnow.duration - timecost <= 0:
                                buffnow.EndBuff()    
                            else:
                                buffnow.duration -= timecost
                                activebufflist_now.append(buffnow)
                                buffinfodict_now[buffnow.buffname] = dict(zip(buffinfo_key, [all_match, buffnow.name, buffnow.duration, buffnow.ready, buffnow.count]))
                        else:
                            buffnow.EndBuff()
                            
                    else:
                        buffnow.EndBuff()

            #接下来是计算环节
        for singlebuff in activebufflist_now:
            if buffnow.active:
            #print(f'当前检验的buff是{singlebuff.name}，剩余时间{singlebuff.duration}，层数为{singlebuff.count}')
            #首先是更新属性，战斗内对于属性的更新主要是两个部分。fix加成和outside加成。也就是固定值和全局百分比。
            #更新固定属性加成
                for fkey in statementkeys:                  
                    f_key = f'f_{fkey}'
                    fixchange = effectfile.loc[singlebuff.buffname, f_key] * singlebuff.count
                    fixchange_before = getattr(eventnow.statechange.fix, fkey)
                    setattr(eventnow.statechange.fix, fkey, fixchange_before + fixchange)
                
                #print(f'当前的冰伤固定加成是：{eventnow.statechange.fix.ice:.2F}')
                #更新全局属性加成属性加成
                for okey in statementkeys:                  
                    o_key = f'o_{okey}'
                    bonuschange = effectfile.loc[singlebuff.buffname, o_key] * singlebuff.count
                    bonuschange_before = getattr(eventnow.statechange.outsidebonus, okey)          
                    setattr(eventnow.statechange.outsidebonus, okey, bonuschange_before + bonuschange)

                #更新增伤区中的技能种类区加成
                for typekey in skilltypekey_list:           
                    typechange = effectfile.loc[singlebuff.buffname, typekey] * singlebuff.count
                    typechange_before = getattr(eventnow.multiplication.dmg.skill_type, skilltypekey_dict[typekey])
                    setattr(eventnow.multiplication.dmg.skill_type, skilltypekey_dict[typekey], typechange_before + typechange)
                    #更新全局增伤。
                alldmgchange = effectfile.loc[singlebuff.buffname, 'ALLDMG'] * singlebuff.count
                alldmgchange_before = eventnow.multiplication.dmg.alldmg.value
                eventnow.multiplication.dmg.alldmg.value = alldmgchange_before + alldmgchange

                #防御区
                for key in deflist:
                    defchange = effectfile.loc[singlebuff.buffname, defdict[key]] * singlebuff.count
                    defchange_before = getattr(eventnow.multiplication.defence, key)
                    setattr(eventnow.multiplication.defence, key, defchange_before + defchange)

                #更新抗性区
                for keys in enemyreskey_list:               
                    reschange = effectfile.loc[singlebuff.buffname, enemyres_dict[keys]] * singlebuff.count
                    reschange_before = getattr(eventnow.multiplication.res.ele_res, keys)
                    setattr(eventnow.multiplication.res.ele_res, keys, reschange_before + reschange)
                    #更新全属性抗性降低
                ele_reducechange = effectfile.loc[singlebuff.buffname, 'Element_reduce'] * singlebuff.count
                ele_reducechange_before = eventnow.multiplication.res.ele_reduce
                eventnow.multiplication.res.ele_reduce = ele_reducechange + ele_reducechange_before
                    #更新全属性抗性穿透
                ele_penchange = effectfile.loc[singlebuff.buffname, 'Element_penetrate'] * singlebuff.count
                ele_penchange_before = eventnow.multiplication.res.ele_penetrate
                eventnow.multiplication.res.ele_penetrate = ele_penchange_before + ele_penchange


                #更新双爆区中的“被暴击率”和“受到的爆击伤害增加”
                    #被暴击率
                cbc_change = effectfile.loc[singlebuff.buffname, 'Chance_to_be_crit'] * singlebuff.count
                cbc_change_before = eventnow.multiplication.crit.cbc
                eventnow.multiplication.crit.cbc = cbc_change + cbc_change_before
                    #受到的暴击伤害
                dfc_change = effectfile.loc[singlebuff.buffname, 'Damage_from_crit'] * singlebuff.count
                dfc_change_before = eventnow.multiplication.crit.dfc
                eventnow.multiplication.crit.dfc = dfc_change_before + dfc_change


                #更新易伤区
                    #受到伤害增加
                di_change = effectfile.loc[singlebuff.buffname, 'Dmgtaken_Increase'] * singlebuff.count
                di_change_before = eventnow.multiplication.vul.di
                eventnow.multiplication.vul.di = di_change_before + di_change
                    #受到伤害减少
                dd_change = effectfile.loc[singlebuff.buffname, 'Dmgtaken_Decrease'] * singlebuff.count
                dd_change_before = eventnow.multiplication.vul.dd
                eventnow.multiplication.vul.dd = dd_change_before + dd_change


                #更新失衡易伤区
                    #失衡易伤增加
                std_change = effectfile.loc[singlebuff.buffname, 'StunDamage_TakeRatio_Delta'] * singlebuff.count
                std_change_before = eventnow.multiplication.stdmg.std
                eventnow.multiplication.stdmg.std = std_change_before + std_change


                #特殊伤害乘区
                specialmul_change = effectfile.loc[singlebuff.buffname, 'Special_Multiplication_Zone'] * singlebuff.count
                specialmul_change_before = eventnow.multiplication.special.value
                eventnow.multiplication.special.value = specialmul_change_before + specialmul_change


        #print(f'固定加成：{eventnow.statechange.fix.ice:.2f}, 百分比加成{eventnow.statechange.outsidebonus.ice:.2f}')
        for finalkey in statementkeys:              #计算最终属性，并且记录在临时的字典中。(已经调试)
            statement_final = getattr(character.outside, finalkey) * (1 + getattr(eventnow.statechange.outsidebonus, finalkey)) + getattr(eventnow.statechange.fix, finalkey)
            character_statementdic_now[finalkey] = statement_final
        
        
        for elekey in elementtype_key:              #将最终属性中的元素伤害，更新给eventnow。
            setattr(eventnow.multiplication.dmg.elemental_dmg_bonus, elekey, character_statementdic_now[elekey[:3]])
        
        #更新穿透区，和增伤区的属性一样，都是在迭代循环完成后，从最终的属性dict中抄取结果。
        eventnow.multiplication.defence.pendelta = character_statementdic_now['pd']
        eventnow.multiplication.defence.pendelta_ratio = character_statementdic_now['pr']
        #print(f'当前穿透值：{eventnow.multiplication.defence.pendelta}，当前穿透率：{eventnow.multiplication.defence.pendelta_ratio}')

        #更新双爆区
        eventnow.multiplication.crit.cr = character_statementdic_now['cr']
        eventnow.multiplication.crit.cd = character_statementdic_now['cd']

        '''
        至此，所有的乘区数值都迭代完毕，我们接下去要计算每个乘区的数值。
        
        '''
        
        #判断，动作是否是几个0伤害动作，如果是，直接跳过。
        if action not in ['dash', 'breaked', 'switch', 'bwswitch']:
            level = character.information.level
            enemydef_basic = Enemyactive.statement.defence                                      #怪物的基础防御值，此处的基础防御值是计算了白值和百分比加成以及固定加成的版本。
            enemydef_increase = eventnow.multiplication.defence.defup                           #防御加成%
            enemydef_decrease = eventnow.multiplication.defence.defdown                         #防御降低%
            enemydef_fix = eventnow.multiplication.defence.deffix                               #固定防御加成
            dmg_basestate = character.action.attack(action)['DmgRelated_Attributes']            #记录了该技能计算伤害所使用的属性。
            stun_basestate = character.action.attack(action)['StunRelated_Attributes']          #记录了该技能计算失衡所使用的属性。
            action_ele = True                                                                   #记录了该动作是否是元素。
            action_eletype = max(int(character.action.attack(action)['ElementType'])-1, 0)      #记录了该动作的元素类型。
            action_skilltype = int(character.action.attack(action)['TriggerBuffLevel'])         #记录了该动作的技能类型
            isStun = True                                                                       #失衡易伤开关
                            
            # DMG_1 = getattr(eventnow.multiplication.dmg.elemental_dmg_bonus, elementtype_key[action_eletype])
            # DMG_2 = getattr(eventnow.multiplication.dmg.skill_type, skilltypekey_dict[skilltypekey_list[action_skilltype]])
            # DMG_3 = eventnow.multiplication.dmg.alldmg.value
            # print(f'{DMG_1:.2f},{DMG_2:.2f},{DMG_3:.2f}')

            DMG_Sum = getattr(eventnow.multiplication.dmg.elemental_dmg_bonus, elementtype_key[action_eletype]) + \
                      getattr(eventnow.multiplication.dmg.skill_type, skilltypekey_dict[skilltypekey_list[action_skilltype]]) + \
                      eventnow.multiplication.dmg.alldmg.value + 1
            

            Attacker_Level_Base =  0.1551 * level ** 2 + 3.141 * level + 47.2039
            enemydef = enemydef_basic * (1+enemydef_increase-enemydef_decrease) + enemydef_fix                                                              #攻击方等级基数
            enemy_effective_def = max(enemydef*(1-eventnow.multiplication.defence.pendelta_ratio)-eventnow.multiplication.defence.pendelta, 0)              #受击方有效防御
            DEF_Sum = Attacker_Level_Base/(enemy_effective_def + Attacker_Level_Base)

            effective_res = getattr(eventnow.multiplication.res.ele_res, elementtype_key[action_eletype]) + eventnow.multiplication.res.ele_res.all
            resreduce = eventnow.multiplication.res.ele_reduce
            ele_pen = eventnow.multiplication.res.ele_penetrate
            RES_Sum = 1 - effective_res + resreduce + ele_pen

            # print(f'当前暴击率：{eventnow.multiplication.crit.cr:2f}， 当前爆击伤害：{eventnow.multiplication.crit.cd:.2f}')
            # print(f'当前目标被暴击率增加：{eventnow.multiplication.crit.cbc:2f}，当前目标的暴击伤害增加{eventnow.multiplication.crit.dfc:.2f}')
            CRIT_Sum = 1 + (eventnow.multiplication.crit.cr + eventnow.multiplication.crit.cbc)*(eventnow.multiplication.crit.cd + eventnow.multiplication.crit.dfc)

            di = eventnow.multiplication.vul.di
            dd = eventnow.multiplication.vul.dd
            # print(f'受击方易伤：{di:2f}, 受击方减伤：{dd:2f}')
            VUL_Sum = 1 + di - dd

            if isStun:
                STUN_Sum = 1 + eventnow.multiplication.stdmg.st + eventnow.multiplication.stdmg.std
            else:
                STUM_Sum = 1
            
            SPECIAL_Sum = eventnow.multiplication.special.value + 1
            # print(SPECIAL_Sum)
            dmg_ratio  = float(character.action.attack(action)['DmgRatio'])
            state_beforebattle = float(getattr(character.outside, dmg_basestate))
            statebonus_fix = float(getattr(eventnow.statechange.fix, dmg_basestate))
            statebonus_ratio = float(getattr(eventnow.statechange.outsidebonus, dmg_basestate))
            statenow = state_beforebattle * (1 + statebonus_ratio) + statebonus_fix
            # print(f'角色站街攻击力为：{state_beforebattle:.2f}，局内固定攻击力加成：{statebonus_fix:.2f}，局内百分比攻击力加成为{statebonus_ratio*100:.2f}%')
            # print(f'角色局内动态总攻击为：{statenow:.2f}')
            final_dmg = dmg_ratio * statenow * DMG_Sum * DEF_Sum * RES_Sum * CRIT_Sum * VUL_Sum * STUN_Sum * SPECIAL_Sum

            buffactive_namelist = []
            for itemcount in range(len(activebufflist_now)):
                buffactive_namelist.append(activebufflist_now[itemcount].buffname)
            
            print(f'当前激活的buff列表为：{buffactive_namelist}')
            print(f'本动作是：{action}，其伤害为：{final_dmg:.2f}')
            print(f'\t攻击力总值为：{float(statenow):.2f}')
            print(f'\t增伤区总值为：{DMG_Sum:.2F}')
            print(f'\t防御区总值为：{DEF_Sum:.2F}')
            print(f'\t抗性区总值为：{RES_Sum:.2F}')
            print(f'\t双爆区总值为：{CRIT_Sum:.2F}')
            print(f'\t易伤区总值为：{VUL_Sum:.2F}')
            print(f'\t失衡区总值为：{STUN_Sum:.2F}')
        else:
            final_dmg = 0
            print(f'当前激活的buff有：{buffactive_namelist}')
            print(f'本次动作并非进攻技能，最终伤害是{final_dmg}')
    
    



        # '''
        # 一下代码块是记录log的代码块，位于计算的最后一环，
        # 也就是每次action循环的末尾，但是timenow变量更新之前。
        # '''
        # # 记录循环开始标志
        # timenow_2f = round(timenow,2)
        # loop_start_row = {'当前时间': timenow_2f, '当前动作': actionkey_now, '是否触发': '', 'buff名称': '', '持续时间': '', '叠层就绪': '', '当前层数': ''}
        # # 两行空行
        # empty_row = {'当前时间': timenow_2f, '当前动作': '', '是否触发': '', 'buff名称': '', '持续时间': '', '叠层就绪': '', '当前层数': ''}

        # # 准备数据
        # data = [loop_start_row]  # 插入起始行
        # for a in buffactive_namelist:
        #     timenow_a = f"{timenow:.2f}" if isinstance(timenow, (int, float)) else str(timenow)
        #     allmatch_a = f"{buffinfodict_now[a]['allmatch']}" if isinstance(buffinfodict_now[a]['allmatch'], (int, float)) else str(buffinfodict_now[a]['allmatch'])
        #     duration_a = f"{buffinfodict_now[a]['duration']:.2f}" if isinstance(buffinfodict_now[a]['duration'], (int, float)) else str(buffinfodict_now[a]['duration'])
        #     ready_a = f"{buffinfodict_now[a]['ready']}" if isinstance(buffinfodict_now[a]['ready'], (int, float)) else str(buffinfodict_now[a]['ready'])
        #     count_a = f"{buffinfodict_now[a]['count']}" if isinstance(buffinfodict_now[a]['count'], (int, float)) else str(buffinfodict_now[a]['count'])

        #     data.append({
        #         '当前时间': timenow_a,
        #         '当前动作': actionkey_now,
        #         '是否触发': allmatch_a,
        #         'buff名称': buffinfodict_now[a]['name'],
        #         '持续时间': duration_a,
        #         '叠层就绪': ready_a,
        #         '当前层数': count_a
        #     })
        # # 创建DataFrame
        # new_data_df = pd.DataFrame(data)
        # if os.path.exists(file_name):
        #     # 读取现有的Excel文件
        #     existing_data_df = pd.read_excel(file_name)
        #     # 将新的数据追加到现有数据
        #     updated_data_df = pd.concat([existing_data_df, new_data_df], ignore_index=True)
        # else:
        #     # 如果文件不存在，使用新数据
        #     updated_data_df = new_data_df
        # # 写入Excel文件
        # updated_data_df.to_excel(file_name, index=False)

        #所有计算和log记录都结束后，更新时间。
        timenow += timecost

'''
TODO:
    极地重金属的四件套的第二特效，需要冻结或碎冰才能触发，暂时无法实现。
    
'''   
EventCreat(actionlist_test, character_a)             

# a = ['f_hp', 'f_atk', 'f_defs', 'f_bs', 'f_cr', 'f_cd', 'f_eap', 'f_em', 'f_pr', 'f_pd', 'f_spr', 'f_spgr', 'f_spm', 'f_phy', 'f_fir', 'f_ice', 'f_ele', 'f_eth', 
#      'o_hp', 'o_atk', 'o_defs', 'o_bs', 'o_cr', 'o_cd', 'o_eap', 'o_em', 'o_pr', 'o_pd', 'o_spr', 'o_spgr', 'o_spm', 'o_phy', 'o_fir', 'o_ice', 'o_ele', 'o_eth', 
#      'PhyBonus', 'FireBonus', 'IceBonus', 'EleBonus', 'EthBonus', 'AttackType', 'NormalAttack', 'SpecialSkill', 'QTE', 'DashSkill', 'SupSkill', 'ElementalStatus', 'ALLDMG', 
#      'Pendelta', 'Pendelta_Ratio', 'Element_reduce', 'Element_penetrate', 
#      'PhyRes', 'FireRes', 'IceRes', 'EleRes', 'EthRes', 'AllRes', 
#      'Dmgtaken_Increase', 'Dmgtaken_Decrease', 
#      'StunDamage_TakeRatio', 'StunDamage_TakeRatio_Delta', 
#      'Special_Multiplication_Zone']

