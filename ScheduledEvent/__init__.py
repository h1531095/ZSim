from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

import Buff.BuffLoad
import Enemy
import Preload
from Buff.BuffExist_Judge import buff_exist_judge
from Calculator import Calculator
from CharSet_new import Character


@dataclass
class ScData:
    event_list = []
    char_obj_list = []
    dynamic_buff = {}
    enemy: Enemy = Enemy.Enemy()


#TODO Schedule逻辑开发
class ScheduledEvent:
    """
    计划事件方法类

    主逻辑链 self.event_start()：
    1、读取计划事件列表，将其中所有的buff示例排到列表最靠前的位置。self.sort_events()
    2、遍历事件列表，从开始到结束，将每一个事件派发到分支逻辑链内进行处理
    """

    def __init__(self):
        pass

    @staticmethod
    def sort_events() -> None:
        """提前处理Buff实例"""
        buff_events = []
        other_events = []
        for event in ScData.event_list[:]:
            if isinstance(event, Buff.Buff):
                buff_events.append(event)
            else:
                other_events.append(event)
        ScData.event_list = buff_events + other_events

    def event_start(self):
        if ScData.event_list:
            self.sort_events()
            for event in ScData.event_list[:]:
                if isinstance(event, Preload.SkillNode):
                    self.skill_event(event)
                    ScData.event_list.remove(event)
                else:
                    raise NotImplementedError(f"Wrong event type: {type(event)}")

    def skill_event(self, event):
        cal_obj = Calculator(skill_node=event,
                             character_obj=ScData.char_obj_list[event.char_name],
                             enemy_obj=ScData.enemy,
                             dynamic_buff=ScData.dynamic_buff)
        self.skill_event_output(cal_obj)

    @staticmethod
    def skill_event_output(cal_obj: Calculator) -> None:
        skill_tag: str = cal_obj.skill_tag
        element_type: int = cal_obj.element_type
        dmg_expect: np.float64 = cal_obj.cal_dmg_expect()
        dmg_crit: np.float64 = cal_obj.cal_dmg_crit()
        stun: np.float64 = cal_obj.cal_stun()
        buildup: np.float64 = cal_obj.anomaly_multipliers.anomaly_buildup
        snapshot: np.ndarray = cal_obj.cal_anomaly_snapshot()[2]
        output_data = {
                'skill_tag': skill_tag,
                'element_type': element_type,
                'dmg_expect': dmg_expect,
                'dmg_crit': dmg_crit,
                'stun': stun,
                'buildup': buildup,
                'snapshot': snapshot
        }

        df = pd.DataFrame([output_data])
        file_path = 'output.csv'
        df.to_csv(file_path, mode='a', header=not Path(file_path).exists(),index=False)
        print(f"{output_data['skill_tag']} 伤害期望: {output_data['dmg_expect']}")


if __name__ == '__main__':
    char = Character(name='艾莲')
    skills = char.skill_object
    p = Preload.Preload(skills)
    skill = p.preload_data.skills_queue[0]
    enemy = Enemy.Enemy()
    name_box = ['艾莲', '苍角', '莱卡恩']
    Judge_list_set = [['艾莲', '深海访客', '极地重金属'], ['苍角', '含羞恶面', '自由蓝调'],
                      ['莱卡恩', '拘缚者', '镇星迪斯科']]
    weapon_dict = {'艾莲': ['深海访客', 1], '苍角': ['含羞恶面', 5], '莱卡恩': ['拘缚者', 1]}
    exist_buff_dict = buff_exist_judge(name_box, Judge_list_set, weapon_dict)
    all_match, judge_condition_dict, active_condition_dict = Buff.BuffLoad.BuffInitialize('Ellen_PassiveSkill',
                                                                                     exist_buff_dict['艾莲'])
    buff = Buff.Buff(active_condition_dict, judge_condition_dict)
    test_md = Calculator(skill, char, enemy, {'艾莲': [buff]})
    pass
