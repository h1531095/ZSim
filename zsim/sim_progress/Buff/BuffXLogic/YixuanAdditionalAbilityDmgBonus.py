from sim_progress.Buff import Buff, JudgeTools, check_preparation
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from simulator.simulator_class import Simulator
    from sim_progress.Preload import SkillNode


class YixuanAdditionalAbilityDmgBonusRecord:
    def __init__(self):
        self.char = None
        self.trigger_buff_0 = None


class YixuanAdditionalAbilityDmgBonus(Buff.BuffLogic):
    """仪玄组队被动的增伤效果：触发条件是：凝云术和墨烬影消命中失衡状态下的敌人时触发。"""
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance: Buff = buff_instance
        self.xjudge = self.special_judge_logic
        self.buff_0 = None
        self.record = None

    def get_prepared(self, **kwargs):
        return check_preparation(buff_instance=self.buff_instance, buff_0=self.buff_0, **kwargs)

    def check_record_module(self):
        if self.buff_0 is None:
            self.buff_0 = JudgeTools.find_exist_buff_dict(sim_instance=self.buff_instance.sim_instance)["仪玄"][
                self.buff_instance.ft.index
            ]
        if self.buff_0.history.record is None:
            self.buff_0.history.record = YixuanAdditionalAbilityDmgBonusRecord()
        self.record = self.buff_0.history.record

    def special_judge_logic(self, **kwargs):
        self.check_record_module()
        self.get_prepared(char_CID=1371)
        skill_node = kwargs.get("skill_node", None)
        if skill_node is None:
            return False
        if not isinstance(skill_node, SkillNode):
            raise TypeError(f"{self.buff_instance.ft.index}的Xjudge函数中获取的skill_node不是SkillNode类")
        enemy = self.buff_instance.sim_instance.schedule_data.enemy
        if not enemy.dynamic.stun:
            return False
        if "1371_E_EX_B_" not in skill_node.skill_tag:
            return False
        return True



