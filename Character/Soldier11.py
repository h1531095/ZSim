from Preload import SkillNode
from Report import report_to_log
from .filters import _skill_node_filter
from .character import Character
import sys

class Soldier11(Character):
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
        self.fire_suppression: int = 0 # 强制的火力镇压
        self.settle_tick: int | None = None

    def special_resources(self, *args, **kwargs) -> None:
        """模拟11号的火力镇压机制"""
        # 输入类型检查
        skill_nodes: list[SkillNode] = _skill_node_filter(*args, **kwargs)
        main_module = sys.modules['__main__']
        tick = main_module.tick
        for node in skill_nodes:
            if self.settle_tick is not None:
                # 超时重置
                if tick - self.settle_tick >= 480:
                    self.fire_suppression = 0
                    self.settle_tick = None
            # 过滤非11号技能
            if '1041' not in node.skill_tag:
                continue
            # 获取层数逻辑
            if node.skill_tag in ['1041_E_EX', '1041_QTE', '1041_Q']:
                self.fire_suppression = 8
                self.settle_tick = tick
            # 消耗层数逻辑
            if 'SNA' in node.skill_tag and self.fire_suppression > 0:
                self.fire_suppression -= 1

    def get_resources(self, *args, **kwargs) -> tuple[str | None, int | float | None]:
        return '火力镇压', self.fire_suppression