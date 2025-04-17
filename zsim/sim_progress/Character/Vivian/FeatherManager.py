from ..character import Character
from zsim.sim_progress.Preload import SkillNode


class FeatherManager:
    """薇薇安的羽毛管理器，飞羽、护羽存储、转化、消耗。"""
    def __init__(self, char_instance: Character):
        self.char = char_instance
        self.flight_feather = 2                     # 飞羽，进场初始化为4层
        self.guard_feather = 0                    # 护羽，初始化为0层
        self.feather_max_count = 5            # 最大飞羽/护羽层数，默认为6层
        self.co_attack_index = '1331_CoAttack_A'

    def trans_feather(self):
        """将现有的飞羽全部转化成护羽：注意，飞羽转化为护羽的时间点为SNA_2的最后一跳，所以这里不能走特殊资源，只能从触发器走。"""
        trans_count = self.flight_feather
        self.guard_feather = min(self.guard_feather + trans_count, self.feather_max_count)
        self.flight_feather = 0

    def gain_feather(self, skill_node: SkillNode, tick: int):
        """获得飞羽，飞羽的获得结算大多为技能的最后一跳，所以也需要从触发器走。"""
        if skill_node.char_name != '薇薇安':
            return
        if 'flight_feather' not in skill_node.skill.labels:
            return
        flight_feather_count = skill_node.labels['flight_feather']
        self.flight_feather = min(self.flight_feather + flight_feather_count, self.feather_max_count)

    def spawn_coattack(self):

        return self.co_attack_index
