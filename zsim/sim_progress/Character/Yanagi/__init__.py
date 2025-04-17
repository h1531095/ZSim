from .StanceManager import StanceManager
from sim_progress.Preload import SkillNode
from sim_progress.Character.utils.filters import _skill_node_filter, _anomaly_filter, _sp_update_data_filter
from sim_progress.Character import Character
from sim_progress.AnomalyBar.CopyAnomalyForOutput import NewAnomaly
from sim_progress.Buff.BuffAddStrategy import buff_add_strategy


class Yanagi(Character):
    """柳的特殊资源系统"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stance_manager = StanceManager(self)
        self.cinme_1_buff_index = 'Buff-角色-柳-1画-洞悉'
        self.cinema_4_buff_index = 'Buff-角色-柳-4画-识破'

    def special_resources(self, *args, **kwargs) -> None:
        skill_nodes: list[SkillNode] = _skill_node_filter(*args, **kwargs)
        anomalies: list[NewAnomaly] = _anomaly_filter(*args, **kwargs)
        # tick = kwargs.get('tick', 0)
        for nodes in skill_nodes:
            self.stance_manager.update_myself(nodes)
        if self.cinema >= 1 and anomalies:
            buff_add_strategy(self.cinme_1_buff_index)
            if self.cinema >= 4:
                for _anomaly in anomalies:
                    if isinstance(_anomaly.actived_by, SkillNode):
                        if str(self.CID) in _anomaly.actived_by.skill_tag:
                            buff_add_strategy(self.cinema_4_buff_index)
                            break

    def update_sp_and_decibel(self, *args, **kwargs):
        """自然更新能量和喧响的方法"""
        # Preload Skill
        skill_nodes = _skill_node_filter(*args, **kwargs)
        for node in skill_nodes:
            # SP
            if node.char_name == self.NAME:
                if node.skill_tag == '1221_E_EX_1' and self.cinema == 6:
                    sp_consume = node.skill.sp_consume/2
                else:
                    sp_consume = node.skill.sp_consume
                sp_threshold = node.skill.sp_threshold
                sp_recovery = node.skill.sp_recovery
                if self.sp < sp_threshold:
                    print(f"{node.skill_tag}需要{sp_threshold:.2f}点能量，目前{self.NAME}仅有{self.sp:.2f}点，需求无法满足，请检查技能树")
                sp_change = sp_recovery - sp_consume
                self.update_sp(sp_change)
            # Decibel
            if self.NAME == node.char_name and node.skill_tag.split('_')[1] == 'Q':
                if self.decibel - 3000 <= -1e-5:
                    raise ValueError(f"{self.NAME} 释放大招时喧响值不足3000，目前为{self.decibel:.2f}点，请检查技能树")
                self.decibel = 0
            else:
                # 计算喧响变化值
                decibel_change = node.skill.self_fever_re
                # 如果喧响变化值大于0，则更新喧响值
                if decibel_change > 0:
                    # 如果不是自身技能，倍率折半
                    if node.char_name != self.NAME:
                        decibel_change *= 0.5
                    # 更新喧响值
                    self.update_decibel(decibel_change)
        # SP recovery over time
        sp_regen_data = _sp_update_data_filter(*args, **kwargs)
        for mul in sp_regen_data:
            if mul.char_name == self.NAME:
                sp_change_2 = mul.get_sp_regen() / 60   # 每秒回能转化为每帧回能
                self.update_sp(sp_change_2)

    def get_resources(self) -> tuple[str|None, int|float|bool|None]:
        """柳的get_resource不返回内容！因为柳没有特殊资源，只有特殊状态"""
        return None, None

    def get_special_stats(self, *args, **kwargs) -> dict[str|None, object|None]:
        return {'当前架势': self.stance_manager.stance_now,
                '森罗万象状态': self.stance_manager.shinrabanshou.active}
