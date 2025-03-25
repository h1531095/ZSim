from sim_progress.Buff import Buff, spawn_buff_from_index
from sim_progress.Buff.BuffLoad import process_buff_for_test
from sim_progress.Character import Skill
from sim_progress.Preload.SkillsQueue import spawn_node
from sim_progress.Load import LoadingMission

#
#
# def creat_test_buff(index: str):
#     buff_output = spawn_buff_from_index(index)
#     return buff_output
#
#
# class TestBuff:
#     def test_init_buff(self):
#         tested_buff_index = 'Buff-武器-精1聚宝箱-回能'
#         tested_char_name = '妮可'
#         tested_char_skill_tag = ''
#         tested_buff = creat_test_buff(tested_buff_index)
#         sub_dict = {tested_buff.ft.index: tested_buff}
#         tested_char_skill = Skill(tested_char_name)
#         tested_node = spawn_node(tested_char_skill_tag, 0, tested_char_skill)
#         tested_mission = LoadingMission(tested_node)
#         result = process_buff_for_test(tested_buff, sub_dict, tested_mission)


