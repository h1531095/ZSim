from dataclasses import dataclass

import Preload
from CharSet_new import Character
from Calculator import MultiplierData
import Enemy
import BuffLoad, BuffClass
from BuffExist_Judge import buff_exist_judge


@dataclass
class ScheduledData:
    event_list = []


#TODO Schedule逻辑开发
class ScheduledEvent:
    def __init__(self, tick, *events):
        for event in events:
            if event.preload_tick <= tick:
                self.event_start(event)

    @staticmethod
    def event_start(event):
        pass


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
    all_match, judge_condition_dict, active_condition_dict = BuffLoad.BuffInitialize('Ellen_PassiveSkill',
                                                                                     exist_buff_dict['艾莲'])
    buff = BuffClass.Buff(active_condition_dict, judge_condition_dict)
    test_md = MultiplierData(skill, char, enemy, {'艾莲': [buff]})
    pass
