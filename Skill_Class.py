import pandas as pd
import Report

class Skill:
    def __init__(self, 
                 name:str=None, CID:int=None, 
                 normal_level=12, special_level=12, dodge_level=12, chain_level=12, assist_level=12, 
                 core_level=6
                 ):
        '''
        根据提供的角色、各技能等级，创建一个角色的技能对象。
        成功创建的对象会包含角色的名称、ID、核心技等级、包含全部技能的字典
        skills_dict：
            -keys: 该角色的全部技能标签（skill_tag）
            -values: 包含全部属性的 InitSkill 对象，可使用getattr()方法调用
        
        方法 get_skill_info()：
            -在仅输入技能标签（skill_tag）时，返回该技能的 InitSkill 对象
            -在同时输入技能标签（skill_tag）和所需属性时（attr_info)时，返回该技能对象的指定属性
        
        以下两个标识符必须提供至少一个：\n
        name:str 角色名称\n
        CID:int 角色的ID

        skill type等级对应表：      \n
        type    描述        Tag     \n
        normal  普攻        0       \n
        special 特殊技      1       \n
        dodge   闪避        2       \n
        chain   连携技      3       \n
        assist  支援技      5       \n
        core    核心被动    4       \n

        调用示例：
        test_object = Skill(name='艾莲')
        skill_lst = list(test_object.skills_dict.keys())
        print(skill_lst)    # 调取所有技能名称，输出为列表
        skill_0 = test_object.skills_dict[skill_lst[0]] # 利用Skill对象内的dict，返回包含特定技能全部属性的对象
        print(skill_0.damage_ratio) # 面对特定技能对象，直接读取其属性
        print(test_object.get_skill_info(skill_tag=skill_lst[0], attr_info='damage_ratio')) # 利用get_skill_info()方法获取属性
        '''
        
        # 初始化角色名称和CID
        self.name, self.CID = self.__init_name(name, CID)
        # 核心技等级需要可读
        self.core_level = core_level
        # 最晚在这里创建DataFrame，优化不了一点，这玩意可大了
        skill_dataframe = pd.read_csv("./data/skill.csv")
        # 根据CID提取角色的技能数据
        self.skill_dataframe = skill_dataframe[skill_dataframe['CID'] == self.CID]
        self.skills_dict = {} # 技能名str:技能参数object
        # 提取dataframe中，每个索引为skill_tag的值，保存为keys
        keys = self.skill_dataframe['skill_tag'].unique()
        for key in keys:
            self.skill_object:object = self.InitSkill(self.skill_dataframe, key, normal_level, special_level, dodge_level, chain_level, assist_level, core_level)
            self.skills_dict[key] = self.skill_object
        
    def __init_name(self, name, CID):
        '''
        初始化角色名称和CID（角色ID）。

        这个方法用于验证和确定角色的名称和CID。它可以根据提供的名称或CID来查找
        对应的角色信息，并确保提供的名称和CID匹配。如果只提供了名称或CID，它将
        尝试从 ./data/character.csv 中查找对应的CID或名称。

        参数:
        - name:str 角色的名称。
        - CID:int 角色的ID。

        返回:
        - 一个包含角色名称和CID的元组。

        异常:
        - ValueError: 如果提供的名称和CID不匹配，或者角色不存在。
        - SystemError: 如果无法处理提供的参数。
        '''
        if name is None and CID is None:
            raise ValueError("角色名称与ID必须至少提供一个")
        # 在./data/character.csv中，自动补全CID或name，若同时传入，检查CID与name是否匹配
        char_dataframe = pd.read_csv("./data/character.csv")
        # 如果同时提供了name和CID，检查它们是否匹配
        if (name is not None) and (CID is not None):
            row = char_dataframe[char_dataframe['name'] == name].to_dict('records')
            if row:
                row = row[0]
                if int(row['CID']) == CID:
                    return name, CID
                else:
                    raise ValueError("传入的name与CID不匹配")
            else:
                raise ValueError("角色不存在")
        # 如果只提供了name，尝试查找对应的CID
        elif name is not None:
            row = char_dataframe[char_dataframe['name'] == name].to_dict('records')
            if row:
                row = row[0]
                CID = int(row.get('CID',0))
                return name, CID
            else:
                raise ValueError("角色不存在")
        # 如果只提供了CID，尝试查找对应的name
        elif CID is not None:
            row = char_dataframe[char_dataframe['CID'] == CID].to_dict('records')
            if row:
                row = row[0]
                name = row.get('name',None)
                return name, CID
            else:
                raise ValueError("角色不存在")
        # 处理异常情况
        else:
            raise SystemError("它爆炸了")

    def get_skill_info(self, skill_tag:str, attr_info:str=None):
        '''
        -在仅输入技能标签（skill_tag）时，返回该技能的 InitSkill 对象\n
        -在同时输入技能标签（skill_tag）和所需属性时（attr_info)时，返回该技能对象的指定属性
        '''
        skill_info:object = self.skills_dict[skill_tag]
        if attr_info is None:
            return skill_info
        else:
            return getattr(skill_info, attr_info)


    class InitSkill:
        def __init__(self, skill_dataframe, key, 
                     normal_level, special_level, dodge_level, chain_level, assist_level, 
                     core_level):
            '''
            初始化角色的技能。
            会在执行class Skill的时候自动调用，不用手动创建此类的对象
            继承自此类的对象会包含输入的技能（key）的全部属性
            '''
            # 提取数据库内，该技能的数据
            _raw_skill_data = skill_dataframe[skill_dataframe['skill_tag'] == key]
            _raw_skill_data = _raw_skill_data.to_dict('records')
            pass
            if _raw_skill_data == {}:
                raise ValueError("未找到技能")
            else:
                _raw_skill_data = _raw_skill_data[0]
            # 如果不是攻击力倍率，报错，未来可接复杂逻辑
            if _raw_skill_data['diff_multiplier'] != 0:
                try :
                    raise ValueError("目前只支持攻击力倍率")
                except ValueError as e:
                    print(e)
            # 储存技能名
            self.skill_tag:str = key
            self.CN_skill_tag:str = _raw_skill_data['CN_skill_tag']
            # 确定使用的技能等级
            self.skill_type:int = int(_raw_skill_data['skill_type'])
            self.__level:int = self.__init_skill_level(self.skill_type, 
                                                       normal_level, special_level, dodge_level, chain_level, assist_level, 
                                                       core_level)
            # 确定伤害倍率
            self.damage_ratio:float = float(_raw_skill_data['damage_ratio']) + float(_raw_skill_data['damage_ratio_growth']) * (self.__level-1)
            # 确定失衡倍率
            self.stun_ratio:float = float(_raw_skill_data['stun_ratio']) + float(_raw_skill_data['stun_ratio_growth']) * (self.__level-1)
            # 能量相关属性
            self.sp_threshold:float = float(_raw_skill_data['sp_threshold'])
            self.sp_consume:float = float(_raw_skill_data['sp_consume'])
            self.sp_recovery:float = float(_raw_skill_data['sp_recovery'])
            # 喧响值
            self.fever_recovery:float = float(_raw_skill_data['fever_recovery'])
            # 距离衰减，不知道有啥用
            self.distance_attenuation:int = int(_raw_skill_data['distance_attenuation'])
            # 属性异常蓄积值，直接转化为浮点
            self.anomaly_accumlation:float = float(_raw_skill_data['anomaly_accumlation'])/100
            # TriggerBuffLevel
            self.trigger_buff_level:int = int(_raw_skill_data['trigger_buff_level'])
            # 元素相关
            self.element_type:int = int(_raw_skill_data['element_type'])
            self.element_damage_percent:float = float(_raw_skill_data['element_damage_percent'])
            # 动画相关
            self.ticks:int = int(_raw_skill_data['ticks'])
            self.hit_times:int = int(_raw_skill_data['hit_times'])

            self.skills_info = {attr: getattr(self, attr) 
                                for attr in dir(self) 
                                if not attr.startswith('__') and not callable(getattr(self, attr))              
            }
            Report.report_to_log(f'[Skill INFO]:{self.skill_tag}:{str(self.skills_info)}')


        def __init_skill_level(self, skill_type:int, 
                               normal_level:int, special_level:int, dodge_level:int, chain_level:int, assist_level:int, 
                               core_level:int)->int:
            '''
            skill type等级对应表：
            type    描述        Tag
            normal  普攻        0
            special 特殊技      1
            dodge   闪避        2
            chain   连携技      3
            assist  支援技      5
            core    核心被动    4
            '''
            match skill_type:
                case 0:
                    return normal_level
                case 1:
                    return special_level
                case 2:
                   return dodge_level
                case 3:
                   return chain_level
                case 5:
                   return assist_level
                case 4:
                   return core_level
                case _:
                    return 1
                

test_object = Skill(name='艾莲')
skill_lst = list(test_object.skills_dict.keys())
# print(skill_lst)
skill_0 = test_object.skills_dict[skill_lst[0]]
# print(skill_0.damage_ratio)
print(test_object.get_skill_info(skill_tag=skill_lst[0], attr_info='damage_ratio'))
