from Buff import Buff, JudgeTools, check_preparation

class Record():
    def __init__(self):
        self.char = None



class QingYiAdditionalAbilityStunConvertToATK(Buff.BuffLogic):
    def __init__(self, buff_instance):
        """
        青衣的组队被动之冲击力转模部分。
        """
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
