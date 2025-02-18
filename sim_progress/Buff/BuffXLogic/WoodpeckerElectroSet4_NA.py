from sim_progress.Buff import Buff, JudgeTools, check_preparation
from sim_progress.ScheduledEvent import MultiplierData, Calculator
from sim_progress.RandomNumberGenerator import RNG


class WoodpeckerElectroNARecord:
    def __init__(self):
        self.equipper = None
        self.char = None
        self.dynamic_buff_list = None
        self.enemy = None
        self.action_stack = None


class WoodpeckerElectroSet4_NA(Buff.BuffLogic):
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        # 初始化特定逻辑
        self.xjudge = self.special_judge_logic
        self.buff_0 = None
        self.record = None
        self.equipper = None

    def get_prepared(self, **kwargs):
        return check_preparation(self.buff_0, **kwargs)

    def check_record_module(self):
        if self.equipper is None:
            self.equipper = JudgeTools.find_equipper('啄木鸟电音')
        if self.buff_0 is None:
            self.buff_0 = JudgeTools.find_exist_buff_dict()[self.equipper][self.buff_instance.ft.index]
        if self.buff_0.history.record is None:
            self.buff_0.history.record = WoodpeckerElectroNARecord()
        self.record = self.buff_0.history.record

    def special_judge_logic(self):
        self.check_record_module()
        self.get_prepared(equipper="啄木鸟电音", enemy=1, dynamic_buff_list=1, action_stack=1)
        action_now = self.record.action_stack.peek()
        if str(self.record.char.CID) not in action_now.mission_tag:
            return False
        rng = RNG()
        seed = rng.r
        seed = (seed/(2**63-1)+1)/2
        mul_data = MultiplierData(self.record.enemy,self.record. dynamic_buff_list, self.record.char)
        if action_now.mission_node.skill.trigger_buff_level == 0:
            cric_rate = Calculator.RegularMul.cal_crit_rate(mul_data)
            if seed <= cric_rate:
                return True
            else:
                return False
        else:
            return False

