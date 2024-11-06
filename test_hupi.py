from Buff.BuffExist_Judge import buff_exist_judge
from SkillEventSplit import SkillEventSplit
from Buff.BuffLoad import BuffLoadLoop
from Update_Buff import update_dynamic_bufflist
import Skill_Class
import tqdm
import Preload
from Buff.BuffAdd import buff_add
from Report import write_to_csv
import Enemy


DYNAMIC_BUFF_DICT = {}
enemy = Enemy.Enemy()
Charname_box = ['艾莲', '苍角', '莱卡恩']
Judge_list_set = [['艾莲', '深海访客', '极地重金属'], ['苍角', '含羞恶面', '自由蓝调'], ['莱卡恩', '拘缚者', '镇星迪斯科']]
weapon_dict = {'艾莲': ['深海访客', 1], '苍角': ['含羞恶面', 5], '莱卡恩': ['拘缚者', 1]}
exist_buff_dict = buff_exist_judge(Charname_box, Judge_list_set, weapon_dict)
for name in Charname_box + ['enemy']:
    DYNAMIC_BUFF_DICT[name] = []
timelimit = 1200
load_mission_dict = {}
LOADING_BUFF_DICT = {}
p = Preload.Preload(Skill_Class.Skill(CID=1221), Skill_Class.Skill(CID=1191))
name_dict = {}
for tick in tqdm.trange(timelimit):
    update_dynamic_bufflist(DYNAMIC_BUFF_DICT, tick, exist_buff_dict, enemy)
    p.do_preload(tick)
    preload_action_list = p.preload_data.preloaded_action
    if preload_action_list:
        SkillEventSplit(preload_action_list, load_mission_dict, name_dict, tick)
    BuffLoadLoop(tick, load_mission_dict, exist_buff_dict, Charname_box, LOADING_BUFF_DICT)
    buff_add(tick, LOADING_BUFF_DICT, DYNAMIC_BUFF_DICT, enemy)
write_to_csv()

