from Preload import SkillNode
from Report import report_to_log
from .filters import _skill_node_filter
from .character import Character
from Buff.BuffAddStrategy import BuffAddStrategy

class Soukaku(Character):
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
        self.vortex: int = 0  # 涡流初始0点

    def special_resources(self, *args, **kwargs) -> None:
        """模拟苍角的涡流机制"""
        # 输入类型检查
        skill_nodes: list[SkillNode] = _skill_node_filter(*args, **kwargs)
        # 对输入的skill_node进行遍历
        for node in skill_nodes:
            if '1131' not in node.skill_tag:
                continue
            if self.vortex <= 3:
                if node.skill_tag in ['1131_E_EX_1', '1131_E_EX_2', '1131_E_EX_3', '1131_QTE']:
                    self.vortex += 1
                    report_to_log(f"[Character] 苍角的涡流被更新为 {self.vortex}")
                elif node.skill_tag == '1131_Q':
                    self.vortex = 3
                    report_to_log(f"[Character] 苍角的涡流被更新为 {self.vortex}")
            # 这里不能 elif
            if self.vortex >= 3:
                if node.skill_tag in ['1131_E_EX_A', '1131_QTE', '1131_Q']:
                    self.vortex = 0
                    from main import init_data
                    char = init_data.name_box[1]
                    # load_data.LOADING_BUFF_DICT[char].append('Buff-角色-苍角-核心被动-2')
                    # BuffAddStrategy('Buff-角色-苍角-核心被动-2')
                    report_to_log(f"[Character] 苍角的涡流被更新为 {self.vortex}")
