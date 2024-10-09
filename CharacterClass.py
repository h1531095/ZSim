class Character:
    def __init__(self, config, stat_dict1=None, stat_dict2=None, stat_dict3=None, action_dict=None):
        # config以后会是字典，而里面的内容应该是字典中的一个键，用对应键值去取值。
        # 下面这个代码，允许这个方法只提供config参数的情况下，顺利调用Character。
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

        self.info = self.Information(config['id'], config['name'], config['level'], config['talent'])
        self.skill = self.Skill(config['unique_skill'], config['normal_attack'], config['dash_skill'],
                                config['support_skill'], config['special_skill'], config['qte_skill'])
        self.build = self.Build(config['weapon'], config['weapon_level'], config['refinement'],
                                config['equipment_set4'], config['equipment_set2_a'], config['equipment_set2_b'],
                                config['equipment_set2_c'])
        self.equip = self.Equipment_Position(config['position1'], config['position2'], config['position3'],
                                             config['position4'], config['position5'], config['position6'])
        self.minor = self.Minor_statement(config['sum'], config['hp'], config['attack'], config['defense'],
                                          config['hpper'], config['atkper'], config['defper'],
                                          config['cr'], config['cd'], config['elementmystery'], config['pendelta'])
        self.basic = self.Statementbasic(stat_dict1)
        self.bonus = self.StatementBonus(stat_dict2)
        self.outside = self.StatementOutside(stat_dict3)
        self.action = self.Action(action_dict)

    '''
    下面这两个@staticmethod代码块，
    写的就是不提供dict1和dict2的情况下的默认配置。
    '''

    @staticmethod
    def default_stat_dict1():
        keys = ['hp', 'atk', 'defs', 'bs', 'cr', 'cd', 'eap', 'em', 'pr', 'pd', 'spr', 'spgr', 'spm', 'phy', 'fir',
                'ice', 'ele', 'eth']
        return {key: 0 for key in keys}

    @staticmethod
    def default_stat_dict2():
        keys = ['hp', 'atk', 'defs', 'bs', 'cr', 'cd', 'eap', 'em', 'pr', 'pd', 'spr', 'spgr', 'spm', 'phy', 'fir',
                'ice', 'ele', 'eth']
        return {key: [0, 0] for key in keys}

    @staticmethod
    def default_stat_dict3():
        keys = ['hp', 'atk', 'defs', 'bs', 'cr', 'cd', 'eap', 'em', 'pr', 'pd', 'spr', 'spgr', 'spm', 'phy', 'fir',
                'ice', 'ele', 'eth']
        return {key: [0, 0] for key in keys}

    class Information:  # 角色的基本信息
        def __init__(self, id, name, level, talent):
            self.id = id
            self.name = name
            self.level = int(level)
            self.talent = int(talent)

    class Skill:  # 角色技能等级
        def __init__(self, unique_skill, normal_attack, dash_skill, support_skill, special_skill, qte_skill):
            self.unique_skill = unique_skill
            self.normal_attack = normal_attack
            self.support_skill = support_skill
            self.dash_skill = dash_skill
            self.special_skill = special_skill
            self.qte_skill = qte_skill

    class Build:  # 角色的装备，音擎，四件套、二件套
        def __init__(self, weapon, weapon_level, refinement, equipment_set4, equipment_set2_a, equipment_set2_b,
                     equipment_set2_c):
            self.weapon = weapon
            self.weapon_level = weapon_level
            self.refinement = refinement
            self.equipment_set4 = equipment_set4
            self.equipment_set2_a = equipment_set2_a
            self.equipment_set2_b = equipment_set2_b
            self.equipment_set2_c = equipment_set2_c

    class Equipment_Position:  # 主词条
        def __init__(self, position1, position2, position3, position4, position5, position6):
            self.position1 = position1
            self.position2 = position2
            self.position3 = position3
            self.position4 = position4
            self.position5 = position5
            self.position6 = position6

    class Minor_statement:  # 副词条，这里指的是数量。
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

    class Statementbasic:
        def __init__(self, stat_dict):  # 这是一个字典，键值是下面的内容，
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

    class StatementBonus:  # 记录加成的属性
        def __init__(self, stat_dict):  # 这是一个字典，键值是下面的内容，
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

    class StatementOutside:
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
            self.eth = stat_dict['eth']  # 以太伤害加成

    class Action:
        # 首先判定，初始化时有没有给一个dict，如果没有就创建一个空的。
        def __init__(self, action_dict=None):
            if action_dict is not None:
                self.Action_dict = action_dict
            else:
                self.Action_dict = {}

            # 默认的动作也需要一个完整的库来装数据，只不过赋值都是0
            self.default_actions = {
                'dash': {'id': 'Dash', 'Name': '冲刺、闪避', 'OfficialName': '冲刺、闪避', 'DmgRatio': 0, 'StunRatio': 0,
                         'SpConsumption': 0, 'SpRecovery_hit': 0, 'FeverRecovery': 0, 'ElementAbnormalAccumlation': 0,
                         'SkillType': 0, 'TriggerBuffLevel': 0, 'ElementType': 0, 'TimeCost': 30, 'HitNumber': 0,
                         'DmgRelated_Attributes': 'atk', 'StunRelated_Attributes': 'bs'},
                'breaked': {'id': 'Breaked', 'Name': '被打断', 'OfficialName': '被打断', 'DmgRatio': 0, 'StunRatio': 0,
                            'SpConsumption': 0, 'SpRecovery_hit': 0, 'FeverRecovery': 0,
                            'ElementAbnormalAccumlation': 0, 'SkillType': 0, 'TriggerBuffLevel': 0, 'ElementType': 0,
                            'TimeCost': 90, 'HitNumber': 0, 'DmgRelated_Attributes': 'atk',
                            'StunRelated_Attributes': 'bs'},
                'switch': {'id': 'Switch', 'Name': '换人', 'OfficialName': '换人', 'DmgRatio': 0, 'StunRatio': 0,
                           'SpConsumption': 0, 'SpRecovery_hit': 0, 'FeverRecovery': 0, 'ElementAbnormalAccumlation': 0,
                           'SkillType': 0, 'TriggerBuffLevel': 0, 'ElementType': 0, 'TimeCost': 20, 'HitNumber': 0,
                           'DmgRelated_Attributes': 'atk', 'StunRelated_Attributes': 'bs'},
                'bwswitch': {'id': 'BackwardSwitch', 'Name': '反向换人', 'OfficialName': '反向换人', 'DmgRatio': 0,
                             'StunRatio': 0, 'SpConsumption': 0, 'SpRecovery_hit': 0, 'FeverRecovery': 0,
                             'ElementAbnormalAccumlation': 0, 'SkillType': 0, 'TriggerBuffLevel': 0, 'ElementType': 0,
                             'TimeCost': 20, 'HitNumber': 0, 'DmgRelated_Attributes': 'atk',
                             'StunRelated_Attributes': 'bs'}
            }
            self.dash = self.Dash()
            self.breaked = self.Breaked()
            self.switch = self.Switch()
            self.bwswitch = self.Bwswitch()

        # 定义attack函数，即action.attack
        def attack(self, action_name):

            # 如果attack()函数里面的技能名字，给的是Action_dict中的键值，那就输出键值对应的数据，并赋值给action_data，
            if action_name in self.Action_dict:
                action_data = self.Action_dict[action_name]
                return action_data

            # 如果没有，那就报错，
            else:
                raise ValueError(f"所输入的动作 {action_name} 并不在该角色的技能列表中！！")

        # 定义dash动作
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
