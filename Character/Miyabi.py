import sys

from AnomalyBar import Disorder
from Preload import SkillNode
from Report import report_to_log
from .filters import _skill_node_filter
from .character import Character


def _disorder_counter(*args, **kwargs) -> int:
    """用于计算输入中紊乱的次数"""
    counter: int = 0
    for arg in args:
        if isinstance(arg, Disorder):
            counter += 1
    for value in kwargs.values():
        if isinstance(value, Disorder):
            counter += 1
    return counter


class Miyabi(Character):
    def __init__(self,
                 name: str = '', CID: int = None,  # 角色名字和CID-必填至少一个
                 weapon=None, weapon_level=1,  # 武器名字-选填项
                 equip_set4=None, equip_set2_a=None, equip_set2_b=None, equip_set2_c=None,  # 驱动盘套装-选填项
                 drive4=None, drive5=None, drive6=None,  # 驱动盘主词条-选填项
                 scATK_percent=0, scATK=0, scHP_percent=0, scHP=0, scDEF_percent=0, scDEF=0, scAnomalyProficiency=0,
                 scPEN=0, scCRIT=0,  # 副词条数量-选填项
                 sp_limit=120  # 能量上限-默认120
                 ):
        super().__init__(
                name, CID,
                weapon, weapon_level,
                equip_set4, equip_set2_a, equip_set2_b, equip_set2_c,
                drive4, drive5, drive6,
                scATK_percent, scATK, scHP_percent, scHP, scDEF_percent, scDEF, scAnomalyProficiency, scPEN, scCRIT,
                sp_limit)
        self.last_tick: int | None = None
        self.frosty: int = 3

    def special_resources(self, *args, **kwargs) -> None:
        """模拟雅的落霜机制"""
        # 输入类型检查
        skill_nodes: list[SkillNode] = _skill_node_filter(*args, **kwargs)
        for node in skill_nodes:
            if '1091' not in node.skill_tag:
                continue
            if self.frosty <= 6:
                if node.skill_tag in ['1091_E_EX_A_1', '1091_E_EX_B_1']:
                    self.frosty += 2
                elif node.skill_tag == '1091_Core_Passive' and not self._shatter_internal_cd():
                    """
                    霜灼·破的产生，在冰焰buff的exist逻辑里。
                    在exist逻辑返回True之前，会把霜灼破扔给special_resources以及eventlist
                    """
                    self.frosty += 1
                elif node.skill_tag == '1091_Q':
                    self.frosty += 3
            else:
                self.frosty = 6
            if node.skill_tag == '1091_SNA_1':
                self.frosty -= 2
            elif node.skill_tag == '1091_SNA_2':
                self.frosty -= 4
            elif node.skill_tag == '1091_SNA_3':
                self.frosty -= 6

            if self.frosty < 0:
                log = f"[Character] {self.NAME}的落霜不足，被消耗至{self.frosty}点，已重置，请检查技能树"
                print(log)
                report_to_log(log)
                self.frosty = 0

        if self.frosty <= 6:
            disorder_times = _disorder_counter(*args, **kwargs)
            self.frosty += disorder_times * 2
            self.frosty = min(self.frosty, 6)

    def _shatter_internal_cd(self) -> bool:
        """判断落霜叠层是否处于CD"""
        main_module = sys.modules['__main__']
        tick: int = main_module.tick
        if self.last_tick is None:
            self.last_tick = tick
            return False
        if tick - self.last_tick < 60:
            return True
        else:
            self.last_tick = tick
            return False

    def get_resources(self):
        return '落霜', self.frosty