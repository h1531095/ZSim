from Preload import SkillNode
from Report import report_to_log
from . import _skill_node_filter
from .character import Character

class Lighter(Character):
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
        self.morale: int = 4000 # 士气初始40 整形为4000
        self.last_tick: int = 0

    def special_resources(self, *args, **kwargs) -> None:
        """
        模拟莱特的士气机制

        判断目前的时间，与上一次激活时做差，并更新士气值
        确保士气值不超过100

        将传入的skill_node消耗的能量转为士气值
        需要消耗士气时对应扣除
        """
        # 输入类型检查
        skill_nodes: list[SkillNode] = _skill_node_filter(*args, **kwargs)
        # 对输入的skill_node进行遍历
        for node in skill_nodes:
            # 累加逻辑
            if self.morale < 10000:
                from main import tick
                # 每 6 ticks 更新
                if (minus := tick - self.last_tick) >= 6:
                    self.morale += minus * 29
                    self.last_tick += 6
                # 消耗能量及时更新
                sp_consume = node.skill.sp_consume
                if sp_consume == 0:
                    continue
                else:
                    self.morale += sp_consume * 26
                self.morale = min(self.morale, 10000)

            if '1161' not in node.skill_tag:
                continue

            # 递减逻辑
            if node.skill_tag == '1161_NA_5_SH_EX':
                self.morale -= 1000
                report_to_log(f"[Character] 莱特的士气消耗至 {self.morale/100:.2f}")
            elif node.skill_tag == '1161_NA_5_CoH_EX':
                self.morale -= 9000
                report_to_log(f"[Character] 莱特的士气消耗至 {self.morale / 100:.2f}")

            if self.morale <= 0:
                print(f"[Character] 莱特的士气消耗至 {self.morale / 100:.2f}, 请检查")