from Buff import Buff
from ScheduledEvent import MultiplierData, Calculator
import sys
import Preload
from RandomNumberGenerator import RNG


class WoodpeckerElectroSet4_NA(Buff.BuffLogic):
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        # 初始化特定逻辑
        self.xjudge = self.special_judge_logic


    def special_judge_logic(self):
        main_module = sys.modules['__main__']
        name_box = main_module.init_data.name_box
        char_on_stage = name_box[0]
        rng = RNG()
        seed = rng.r
        seed = (seed/(2**63-1)+1)/2
        enemy = main_module.schedule_data.enemy
        info_dict = main_module.schedule_data.judge_required_info_dict
        dynamic_buff = main_module.global_stats.DYNAMIC_BUFF_DICT
        char_list = main_module.char_data.char_obj_list
        for _ in char_list:
            if _.NAME == char_on_stage:
                character = _
                mul_data = MultiplierData(enemy, dynamic_buff, character)
                break
        else:
            raise ValueError(f'char_list中并未找到角色{char_on_stage}')
        event = info_dict['skill_node']
        if event is None:
            raise ValueError(f'Schedule阶段没有向judge_required_info_dict内传入对应的skill_node！')
        if not isinstance(event, Preload.SkillNode):
            raise TypeError(f'judge_required_info_dict的skill_node键值下存放的并非SkillNode类！')
        if event.skill.trigger_buff_level == 0:
            cric_rate = Calculator.RegularMul.cal_crit_rate(mul_data)
            if seed <= cric_rate:
                return True
            else:
                return False
        else:
            return False
