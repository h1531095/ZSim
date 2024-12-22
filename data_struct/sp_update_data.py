from typing import Generator
from Character import Character
from .data_analyzer import cal_buff_total_bonus



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