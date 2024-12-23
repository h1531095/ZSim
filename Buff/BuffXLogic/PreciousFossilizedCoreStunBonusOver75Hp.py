from Buff import Buff
from Buff import JudgeTools


class PreciousFossilizedCoreStunBonusOver75Hp(Buff.BuffLogic):
    """
    这段代码是贵重骨核的复杂判断逻辑，
    敌人生命值大于等于75%时返回True
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        # 初始化特定逻辑
        self.xjudge = self.special_judge_logic
        self.main_module = None

    def special_judge_logic(self):
        if self.main_module is None:
            self.main_module = JudgeTools.find_main()
        hp_pct = self.main_module.schedule_data.enemy.get_hp_percentage()
        if hp_pct >= 0.75:
            return True
        else:
            return False
