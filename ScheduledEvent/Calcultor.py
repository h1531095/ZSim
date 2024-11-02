import pandas as pd

from CharSet_new import Character
from Preload import SkillNode
from Enemy import Enemy
from BuffClass import Buff
from Report import report_to_log
from define import EFFECT_FILE_PATH


# from BuffExist_Judge import buff_exist_judge

class MultiplierData:
    def __int__(self, skill: SkillNode, character: Character, enemy: Enemy, dynamic_buff: dict = None):
        if dynamic_buff is None:
            dynamic_buff = {}
        else:
            pass

        if not isinstance(skill, SkillNode):
            raise ValueError("错误的参数类型，应该为SkillNode")
        if not isinstance(character, Character):
            raise ValueError("错误的参数类型，应该为Character")
        if not isinstance(enemy, Enemy):
            raise ValueError("错误的参数类型，应该为Enemy")
        if not isinstance(dynamic_buff, dict):
            raise ValueError("错误的参数类型，应该为dict")

        try:
            self.char_buff: list = dynamic_buff[self.char_name]
        except KeyError:
            self.char_buff = []
            report_to_log(f"动态Buff列表内没有角色{self.char_name}", level=4)

        static_statement: Character.Statement = character.statement
        self.__init_static_statement(static_statement)
        self.__cal_buff_total_bonus(self.char_buff)
        self.__init_enemy_statement(enemy)
        self.__cal_char_multiplier(skill)

    def __init_static_statement(self, static_statement: Character.Statement):
        """将角色面板抄下来！！！！！"""
        self.char_name: str                     = static_statement.NAME
        self.char_cid: int                      = static_statement.CID
        self.static_atk: float                  = static_statement.ATK
        self.static_hp: float                   = static_statement.HP
        self.static_def: float                  = static_statement.DEF
        self.static_imp: float                  = static_statement.IMP
        self.static_ap: float                   = static_statement.AP
        self.static_am: float                   = static_statement.AM
        self.static_crit_rate: float            = static_statement.CRIT_rate
        self.static_crit_damage: float          = static_statement.CRIT_damage
        self.static_sp_regen: float             = static_statement.sp_regen
        self.static_sp_get_ratio: float         = static_statement.sp_get_ratio
        self.static_sp_limit: float             = static_statement.sp_limit
        self.static_pen_ratio: float            = static_statement.PEN_ratio
        self.static_pen_numeric: float          = static_statement.PEN_numeric
        self.static_phy_dmg_bonus: float        = static_statement.PHY_DMG_bonus
        self.static_ice_dmg_bonus: float        = static_statement.ICE_DMG_bonus
        self.static_fire_dmg_bonus: float       = static_statement.FIRE_DMG_bonus
        self.static_ether_dmg_bonus: float      = static_statement.ETHER_DMG_bonus
        self.static_electric_dmg_bonus: float   = static_statement.ELECTRIC_DMG_bonus

    def __cal_buff_total_bonus(self, char_buff: list) -> None:
        """
        计算角色buff的总加成。

        该方法首先读取buff效果的键值对，然后遍历角色身上的所有buff。
        对于每个buff，检查其是否为Buff类型，然后根据buff的计数（count）来计算总加成。

        参数:
        - char_buff: 包含角色所有buff的列表。
        """
        # 初始化动态语句字典，用于累加buff效果的值
        self.dynamic_statement: dict = self.__read_buff_effect_keys()

        # 遍历角色身上的所有buff
        for buff in char_buff:
            # 确保buff是Buff类的实例
            if isinstance(buff, Buff):
                # 检查buff的简单效果是否为空
                if buff.ft.simple_effect is not True:
                    raise ValueError(f"属性 ft.simple_effect 不能为：{buff.ft.simple_effect}，功能还没写！")

                # 获取buff的层数
                count = buff.dy.count

                # 遍历buff的每个效果和对应的值
                for key, value in buff.effect_dct.items():
                    # 如果效果键在动态语句字典中，则累加其值
                    if key in self.dynamic_statement:
                        self.dynamic_statement[key] += value * count
                    else:
                        # 如果效果键无效，则抛出KeyError
                        raise KeyError(f"Invalid buff multiplier key: {key}")

    def __init_enemy_statement(self, enemy):
        pass

    def __cal_char_multiplier(self, skill: SkillNode) -> None:
        # 基础伤害乘区 = 技能倍率 * 基础属性
        self.base_dmg: float = (skill.skill.damage_ratio / skill.hit_times)

    @staticmethod
    def __read_buff_effect_keys():
        # 提取首列外的列名
        keys = pd.read_csv(EFFECT_FILE_PATH, nrows = 1).columns[1:]
        return {key: 0 for key in keys}



if __name__ == '__main__':
    char = Character(name='柳')