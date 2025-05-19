from sim_progress.Buff import Buff, JudgeTools, check_preparation, find_tick


class BuffXLogicNameRecord:
    def __init__(self):
        self.equipper = None
        self.char = None


class BuffXLogicName(Buff.BuffLogic):
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance: Buff = buff_instance
        self.xjudge = self.special_judge_logic
        self.equipper = None
        self.buff_0 = None
        self.record = None

    def get_prepared(self, **kwargs):
        return check_preparation(self.buff_0, **kwargs)

    def check_record_module(self):
        if self.equipper is None:
            self.equipper = JudgeTools.find_equipper("装备名字")
        if self.buff_0 is None:
            self.buff_0 = JudgeTools.find_exist_buff_dict()[self.equipper][
                self.buff_instance.ft.index
            ]
        if self.buff_0.history.record is None:
            self.buff_0.history.record = BuffXLogicNameRecord()
        self.record = self.buff_0.history.record

    def special_judge_logic(self, **kwargs):
        self.check_record_module()
        self.get_prepared(equipper="装备名字")
