from Buff import Buff, JudgeTools
import sys


class SokakuAdditionalAbilityICEBonus(Buff.BuffLogic):
    """
    苍角组队被动：
    消耗涡流发动展旗时激活
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        # 初始化特定逻辑
        self.xjudge = self.special_judge_logic
        self.char = None
        self.action_stack = None
        self.buff_0 = None

    def special_judge_logic(self):
        if self.char is None:
            self.char = JudgeTools.find_char_from_CID(1131)
        if self.action_stack is None:
            self.action_stack = JudgeTools.find_stack()
        if self.buff_0 is None:
            self.buff_0 = JudgeTools.find_exist_buff_dict()['苍角'][self.buff_instance.ft.index]
        action_now = self.action_stack.peek()
        if action_now.mission_tag not in ['1131_E_EX_A', '1131_QTE', '1131_Q']:
            return False
        if self.buff_0.history.last_update_resource < self.char.get_resources()[1]:
            return True
        else:
            return False


