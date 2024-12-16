from Preload import SkillNode
from Report import report_to_log
from .filters import _skill_node_filter
from .character import Character


class Ellen(Character):
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
        self.flash_freeze: int = 0

    def special_resources(self, *args, **kwargs) -> None:
        """模拟艾莲的急冻充能"""
        # 输入类型检查
        skill_nodes: list[SkillNode] = _skill_node_filter(*args, **kwargs)
        for node in skill_nodes:
            if '1191' not in node.skill_tag:
                continue
            if node.skill_tag in ['1191_SNA_1', '1191_SNA_2', '1191_SNA_3']:
                self.flash_freeze -= 1
                if self.flash_freeze < 0:
                    report_to_log(f'[Character] 释放 {node.skill_tag} 时，{self.NAME}的急冻充能不足，请检查技能树')
            if self.flash_freeze < 3:
                if node.skill_tag in ['1191_E_EX', '1191_E_EX_A', '1191_RA_NFC']:
                    self.flash_freeze += 1
                    report_to_log(f"[Character] {self.NAME}的急冻充能被更新为：{self.flash_freeze}")
                if node.skill_tag == '1191_RA_FC':
                    self.flash_freeze += 3
                    report_to_log(f"[Character] {self.NAME}的急冻充能被更新为：{self.flash_freeze}")
            self.flash_freeze = max(self.flash_freeze, 0)
            self.flash_freeze = min(self.flash_freeze, 3)

    def get_resources(self):
        return self.flash_freeze
