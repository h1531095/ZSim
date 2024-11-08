import Dot
import Load
from Buff.BuffExist_Judge import buff_exist_judge
from Load.SkillEventSplit import SkillEventSplit
from Buff.BuffLoad import BuffLoadLoop
from Update_Buff import update_dynamic_bufflist
import Skill_Class
import tqdm
import Preload
from Buff.BuffAdd import buff_add
from Report import write_to_csv
import Enemy
from Load.LoadDamageEvent import DamageEventJudge


DYNAMIC_BUFF_DICT = {}
event_list = []
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
        for _ in load_mission_dict.values():
            if isinstance(_, Load.LoadingMission):
                print(_.mission_dict)
    # BuffLoadLoop(tick, load_mission_dict, exist_buff_dict, Charname_box, LOADING_BUFF_DICT)
    # buff_add(tick, LOADING_BUFF_DICT, DYNAMIC_BUFF_DICT, enemy)
    DamageEventJudge(tick, load_mission_dict, enemy, event_list)
    event_list = []

# write_to_csv()

"""
1-DYNAMIC_BUFF_DICT：嵌套字典，记录了角色+敌人身上的所有动态Buff和Debuff
2-exist_buff_dict：嵌套字典，记录了所有在本次模拟中可能被触发的Buff（由配置列表、或是webui中的数据得出）
3-LOADING_BUFF_DICT：嵌套字典，从BuffLoadLoop阶段产生，并且会被buff_add函数完全pop干净，不会留到后面。下一个Tick中，BuffLoadLoop会重新重置一个空的LOADING_BUFF_DICT。
4-load_mission_dict：在Preload阶段有东西抛出的时候，SkillEventSplit函数会更新这个字典中的内容。这里记录了所有正在进行中的动作事件。
    SkillEventSplit在每次执行时，会对load_mission_dict进行一次维护，从中剔除已经结束的动作，这部分内容预计以后将会单独拆分成一个函数来执行，每个Tick都执行。
5-name_dict：由于load_mission_dict中的动作名称是作为键值存在的，不能重复，所以在生成键值时，load_mission_dict会对name_dict中已有的技能名字进行检查，并且通过后缀+=1的方式生成新的技能名字。

"""