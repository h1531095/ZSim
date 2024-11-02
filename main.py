from BuffExist_Judge import buff_exist_judge
from SkillEventSplit import SkillEventSplit
from BuffLoad import BuffLoadLoop
from Update_Buff import update_dynamic_bufflist
import Skill_Class
import tqdm
import Preload
from BuffAdd import buff_add



DYNAMIC_BUFF_DICT = {}

Charname_box = ['艾莲', '苍角', '莱卡恩']
Judge_list_set = [['艾莲', '深海访客', '极地重金属'], ['苍角', '含羞恶面', '自由蓝调'], ['莱卡恩', '拘缚者', '镇星迪斯科']]
weapon_dict = {'艾莲': ['深海访客', 1], '苍角': ['含羞恶面', 5], '莱卡恩': ['拘缚者', 1]}
exist_buff_dict = buff_exist_judge(Charname_box, Judge_list_set, weapon_dict)
for name in Charname_box:
    DYNAMIC_BUFF_DICT[name] = []
timelimit = 1200
load_mission_dict = {}
LOADING_BUFF_DICT = {}
p = Preload.Preload(Skill_Class.Skill(CID=1221), Skill_Class.Skill(CID=1191))
name_dict = {}
for tick in tqdm.trange(timelimit):
    update_dynamic_bufflist(DYNAMIC_BUFF_DICT, tick, Charname_box, exist_buff_dict)
    p.do_preload(tick)
    preload_action_list = p.preload_data.preloaded_action
    if preload_action_list:
        SkillEventSplit(preload_action_list, load_mission_dict, name_dict, tick)
    BuffLoadLoop(tick, load_mission_dict, exist_buff_dict, Charname_box, LOADING_BUFF_DICT)
    buff_add(tick, LOADING_BUFF_DICT, DYNAMIC_BUFF_DICT)
    char_name = '艾莲'
    output = ';  '.join(f'{buff.ft.index}' for buff in DYNAMIC_BUFF_DICT[char_name])
    print(f'{tick}:角色{char_name}的动态buff列表为{output}')
    '''
    DYNAMIC_BUFF_DICT = {
    '艾莲':[buff1, buff2, buff3, buff4.........],
    '苍角':[buff1, buff2, buff3, buff4.........],
    '莱卡恩':[buff1, buff2, buff3, buff4.........]
    }
    mul_change_dict = {
    '属性变化':{atk: a1, def: a2, hp: a3, ……}
    '乘区变化':{增伤区:b1, 防御区:b2, ......}
    }
    
    '''

