import unittest
from sim_progress.Character import Character
from sim_progress import Preload, Buff, Enemy
from sim_progress.Buff.BuffExist_Judge import buff_exist_judge

class Test_ScheduledEvent(unittest.TestCase):
    def test_Calculator(self):
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
        all_match, judge_condition_dict, active_condition_dict = sim_progress.Buff.BuffLoad.BuffInitialize('Ellen_PassiveSkill',
                                                                                                           exist_buff_dict['艾莲'])
        buff = Buff.Buff(active_condition_dict, judge_condition_dict)
        test_md = ScheduledEvent.Calculator(skill, char, enemy, {'艾莲': [buff]})
        de = test_md.cal_dmg_expect()
        dc = test_md.cal_dmg_crit()
        sps = test_md.cal_snapshot()