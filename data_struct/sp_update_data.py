import Buff
from Report import report_to_log
from functools import lru_cache
from typing import Generator
from Character import Character


@lru_cache(maxsize=128)
def cal_buff_total_bonus(enabled_buff: tuple | Generator) -> dict:
        """
        计算角色buff的总加成。

        该方法首先读取buff效果的键值对，然后遍历角色身上的所有buff。
        对于每个buff，检查其是否为Buff类型，然后根据buff的计数（count）来计算总加成。

        参数:
        - char_buff: 包含角色所有buff的列表。
        """
        # 初始化动态语句字典，用于累加buff效果的值
        dynamic_statement: dict = {}

        # 遍历角色身上的所有buff
        for buff_obj in enabled_buff:
            # 确保buff是Buff类的实例
            if not isinstance(buff_obj, Buff.Buff):
                raise TypeError(f"{buff_obj} 不是Buff类型，无法计算！")
            else:
                # 检查buff的简单效果是否为空
                buff_obj: Buff.Buff
                # if not buff_obj.ft.simple_hit_logic:
                #     raise NotImplementedError(f"属性 ft.simple_effect 不能为：{buff_obj.ft.simple_hit_logic}，功能还没写！")
                if not buff_obj.dy.active:
                     report_to_log(f"[Buff Effect] 动态buff列表中混入了未激活buff: {str(buff_obj)}，已跳过")
                     continue


                # 获取buff的层数
                count = buff_obj.dy.count
                count = count if count > 0 else 0

                # 遍历buff的每个效果和对应的值，并将其累加
                for key, value in buff_obj.effect_dct.items():
                    # 如果键值对在动态语句字典中，则累加值，否则初始化并赋值
                    try:
                        dynamic_statement[key] = dynamic_statement.get(key, 0) + value * count
                    except TypeError:
                        continue
        return dynamic_statement

class SPUpdateData:
    def __init__(self, char_obj: Character, dynamic_buff: dict):
        """更新角色SP时的专用数据结构，仅用于传递角色的静态与动态的能量自动回复效率"""
        self.char_name = char_obj.NAME
        self.static_sp_regen: float = char_obj.statement.sp_regen
        enabled_buff: Generator = (buff for buff in dynamic_buff[self.char_name])
        self.dynamic_sp_regen: float = self.__cal_dynamic_sp_regen(enabled_buff)

    @staticmethod
    def __cal_dynamic_sp_regen(enabled_buff: Generator):
        buff_bonus: dict = cal_buff_total_bonus(enabled_buff)
        dynamic_sp_regen = buff_bonus.get('sp_regen', 0) + buff_bonus.get('field_sp_regen', 0)
        return dynamic_sp_regen

    def get_sp_regen(self) -> float:
        return self.static_sp_regen + self.dynamic_sp_regen