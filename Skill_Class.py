import pandas as pd
import Report
from define import ElementType
from define import *


def lookup_name_or_cid(name: str = None, cid: int = None) -> tuple[str, int]:
    """
    初始化角色名称和CID（角色ID）。

    这个方法用于验证和确定角色的名称和CID。它可以根据提供的名称或CID来查找
    对应的角色信息，并确保提供的名称和CID匹配。如果只提供了名称或CID，它将
    尝试从 ./data/character.csv 中查找对应的CID或名称。

    参数:
    - name:str 角色的名称。
    - CID:int 角色的ID。

    示例：
    self.NAME, self.CID = lookup_name_or_cid(name, cid)

    返回:
    - 一个包含角色名称和CID的元组。

    异常:
    - ValueError: 提供的名称和CID不匹配，或者角色不存在。
    - IOError: 角色数据库常量 CHARACTER_DATA_PATH 有误
    - SystemError: 无法处理提供的参数。
    """
    try:
        # 读取角色数据
        char_dataframe = pd.read_csv(CHARACTER_DATA_PATH, encoding='utf-8')
    except Exception as e:
        raise IOError(f"无法读取文件 {CHARACTER_DATA_PATH}: {e}")

    # 查找角色信息
    if name is not None:
        result = char_dataframe[char_dataframe['name'] == name].to_dict('records')
    elif cid is not None:
        result = char_dataframe[char_dataframe['CID'] == cid].to_dict('records')
    else:
        raise ValueError("角色名称与ID必须至少提供一个")

    if not result:
        raise ValueError("角色不存在")

    character_info = result[0]

    # 检查传入的name与CID是否匹配
    if name is not None and cid is not None:
        if int(character_info['CID']) != cid:
            raise ValueError("传入的name与CID不匹配")

    return character_info['name'], int(character_info['CID'])


class Skill:
    def __init__(self,
                 name: str = None, CID: int = None,
                 normal_level=12, special_level=12, dodge_level=12, chain_level=12, assist_level=12,
                 core_level=6
                 ):
        """
        根据提供的角色、各技能等级，创建一个角色的技能对象。
        成功创建的对象会包含角色的名称、ID、核心技等级、包含全部技能的字典
        skills_dict：
            -keys: 该角色的全部技能标签（skill_tag）
            -values: 包含全部属性的 InitSkill 对象，可使用getattr()方法调用

        方法 __create_action_list():
            -检查 self.skill_dict 中是否包含闪避、正向切人、反向切人、被打断、发呆
                -有，则使用自身的技能
                -没有，则使用自带 module，初始化这些动作
            -返回仅包含动作名称的列表

        方法 get_skill_info()：
            -在仅输入技能标签（skill_tag）时，返回该技能的 InitSkill 对象
            -在同时输入技能标签（skill_tag）和所需属性时（attr_info)时，返回该技能对象的指定属性

        以下两个标识符必须提供至少一个：\n
        name:str 角色名称\n
        CID:int 角色的ID

        调用示例：
        test_object = Skill(name='艾莲')
        action_list = test_object.action_list  # 获取动作列表
        skills_dict = test_object.skills_dict  # 获取技能字典
        skill_0: Skill.InitSkill = test_object.skills_dict[action_list[0]]  # 获取第一个动作对应的技能对象
        skill_0.damage_ratio  # 获取第一个动作的伤害倍率—方式1
        test_object.get_skill_info(skill_tag=action_list[0], attr_info='damage_ratio')  # 获取第一个动作的伤害倍率-方式2
        """

        # 初始化角色名称和CID
        self.name, self.CID = lookup_name_or_cid(name, CID)
        # 核心技等级需要可读
        self.core_level = core_level
        # 最晚在这里创建DataFrame，优化不了一点，这玩意可大了
        skill_dataframe = pd.read_csv(SKILL_DATA_PATH)

        # 根据CID提取角色的技能数据

        try:
            self.skill_dataframe = skill_dataframe[skill_dataframe['CID'] == self.CID]
            # 如果没有找到对应CID，则报错
            if self.skill_dataframe.empty:
                raise ValueError
            # 提取dataframe中，每个索引为skill_tag的值，保存为keys
            else:
                __keys = self.skill_dataframe['skill_tag'].unique()
        except KeyError:
            print(f"{SKILL_DATA_PATH} 中缺少 'skill_tag' 列")  # 虽然不可能
            return
        except ValueError:
            print(f"找不到CID为 {self.CID} 的角色信息")
            return

        # 创建技能字典与技能列表 self.skills_dict 与 self.action_list
        self.skills_dict = {}  # {技能名str:技能参数object:InitSkill}
        for key in __keys:
            skill = self.InitSkill(skill_dataframe=self.skill_dataframe, key=key, normal_level=normal_level,
                                   special_level=special_level, dodge_level=dodge_level, chain_level=chain_level,
                                   assist_level=assist_level, core_level=core_level, CID=self.CID, char_name=self.name)
            self.skills_dict[key] = skill
        self.action_list = self.__create_action_list()

    def get_skill_info(self, skill_tag: str, attr_info: str = None):
        """
        -在仅输入技能标签（skill_tag）时，返回该技能的 InitSkill 对象\n
        -在同时输入技能标签（skill_tag）和所需属性时（attr_info)时，返回该技能对象的指定属性
        """
        skill_info: Skill.InitSkill = self.skills_dict[skill_tag]
        if attr_info is None:
            return skill_info
        else:
            return getattr(skill_info, attr_info)

    def __create_action_list(self):
        """
        创建动作列表并检查初始化状态

        此函数旨在为角色或实体创建一个动作列表，并检查这些动作是否已经初始化。
        它通过检查技能字典（skills_dict）中的键来确定哪些动作已经存在，如果不存在（即未初始化），
        则会创建这些动作的默认实例。
        """
        # 定义需要检查是否初始化的动作列表
        default_actions_dataframe = pd.read_csv(DEFAULT_SKILL_PATH)
        by_default_actions = default_actions_dataframe['skill_tag'].unique()

        # 初始化每个动作的状态为 True
        init_actions = {action: True for action in by_default_actions}

        # 遍历 skills_dict 的键
        for key in self.skills_dict.keys():
            # 检查键中是否包含某个动作
            for action in by_default_actions:
                if action in key:
                    # 如果包含，则将对应动作的状态设为 False
                    init_actions[action] = False

        # 遍历每个动作及其初始化状态
        for action, init in init_actions.items():
            # 如果某个动作未被初始化，则创建对应的 Skill 对象并添加到 skills_dict
            if init:
                self.skills_dict[f'{self.CID}_{action}'] = Skill.InitSkill(default_actions_dataframe, key=action,
                                                                           CID=self.CID)
        return list(self.skills_dict.keys())

    class InitSkill:
        def __init__(self, skill_dataframe, key,
                     normal_level=12, special_level=12, dodge_level=12, chain_level=12, assist_level=12,
                     core_level=6,
                     CID=0,
                     char_name=None
                     ):
            """
            初始化角色的技能。
            会在执行class Skill的时候自动调用，不用手动创建此类的对象
            继承自此类的对象会包含输入的技能（key）的全部属性
            """
            # 提取数据库内，该技能的数据
            _raw_skill_data = skill_dataframe[skill_dataframe['skill_tag'] == key]
            _raw_skill_data = _raw_skill_data.to_dict('records')
            if not _raw_skill_data:
                raise ValueError("未找到技能")
            else:
                _raw_skill_data = _raw_skill_data[0]
            # 如果不是 攻击力/生命值/防御力/精通 倍率，报错，未来可接复杂逻辑
            self.diff_multiplier = int(_raw_skill_data['diff_multiplier'])
            if _raw_skill_data['diff_multiplier'] not in [0, 1, 2, 3]:
                raise ValueError("目前只支持 攻击力/生命值/防御力/精通 倍率")
            self.char_name = char_name
            # 储存技能Tag
            self.skill_tag = f'{CID}_{key}' if str(CID) not in key else key
            self.CN_skill_tag: str = _raw_skill_data['CN_skill_tag']
            # 确定使用的技能等级
            self.skill_type: int = int(_raw_skill_data['skill_type'])
            self.skill_level: int = self.__init_skill_level(self.skill_type,
                                                            normal_level, special_level, dodge_level, chain_level,
                                                            assist_level,
                                                            core_level)
            # 确定伤害倍率
            damage_ratio = float(_raw_skill_data['damage_ratio'])
            damage_ratio_growth = float(_raw_skill_data['damage_ratio_growth'])
            self.damage_ratio: float = damage_ratio + damage_ratio_growth * (self.skill_level - 1)
            # 确定失衡倍率
            stun_ratio = float(_raw_skill_data['stun_ratio'])
            stun_ratio_growth = float(_raw_skill_data['stun_ratio_growth'])
            self.stun_ratio: float = stun_ratio + stun_ratio_growth * (self.skill_level - 1)
            # 能量相关属性
            self.sp_threshold: float = float(_raw_skill_data['sp_threshold'])
            self.sp_consume: float = float(_raw_skill_data['sp_consume'])
            self.sp_recovery: float = float(_raw_skill_data['sp_recovery'])
            # 喧响值
            self.fever_recovery: float = float(_raw_skill_data['fever_recovery'])
            # 距离衰减，不知道有啥用
            self.distance_attenuation: int = int(_raw_skill_data['distance_attenuation'])
            # 属性异常蓄积值，直接转化为浮点
            self.anomaly_accumulation: float = float(_raw_skill_data['anomaly_accumulation']) / 100
            # TriggerBuffLevel
            self.trigger_buff_level: int = int(_raw_skill_data['trigger_buff_level'])
            # 元素相关
            self.element_type: ElementType = ElementType(int(_raw_skill_data['element_type']))
            self.element_damage_percent: float = float(_raw_skill_data['element_damage_percent'])
            # 动画相关
            self.ticks: int = int(_raw_skill_data['ticks'])
            temp_hit_times = int(_raw_skill_data['hit_times'])
            self.hit_times: int = temp_hit_times if temp_hit_times > 0 else 1

            self.skill_attr_dict = {attr: getattr(self, attr)
                                    for attr in dir(self)
                                    if not attr.startswith('__') and not callable(getattr(self, attr))
                                    }
            Report.report_to_log(f'[Skill INFO]:{self.skill_tag}:{str(self.skill_attr_dict)}')

        @staticmethod
        def __init_skill_level(skill_type: int,
                               normal_level: int, special_level: int, dodge_level: int, chain_level: int,
                               assist_level: int,
                               core_level: int) -> int:
            """
            根据 skill_type 选择对应的技能等级

            参数:
            - skill_type (int): 技能类型标签
            - normal_level (int): 普攻等级
            - special_level (int): 特殊技等级
            - dodge_level (int): 闪避等级
            - chain_level (int): 连携技等级
            - assist_level (int): 支援技等级
            - core_level (int): 核心被动等级
            """
            skill_levels = {
                0: normal_level,
                1: special_level,
                2: dodge_level,
                3: chain_level,
                4: core_level,
                5: assist_level
            }

            if skill_type in skill_levels:
                return skill_levels[skill_type]
            else:
                raise ValueError(f"Invalid skill_type: {skill_type}")


if __name__ == '__main__':
    test_object = Skill(name='艾莲')
    test_object2 = Skill(CID=1221)
    action_list = test_object.action_list  # 获取动作列表
    skills_dict = test_object.skills_dict  # 获取技能字典
    skill_0: Skill.InitSkill = test_object.skills_dict[action_list[0]]  # 获取第一个动作对应的技能对象
    print(skill_0.damage_ratio)  # 获取第一个动作的伤害倍率
    print(test_object.get_skill_info(skill_tag=action_list[0], attr_info='damage_ratio'))  # 获取第一个动作的伤害倍率
