from Buff import Buff
from Skill_Class import Skill
import pandas as pd
from SkillEventSplit import SkillEventSplit, LoadingMission
from define import BUFF_LOADING_CONDITION_TRANSLATION_DICT, JUDGE_FILE_PATH, EXIST_FILE_PATH, EFFECT_FILE_PATH
from Buff.BuffExist_Judge import buff_exist_judge
import Preload
import tqdm
import numpy as np
from Report import report_to_log
import Skill_Class

EXIST_FILE = pd.read_csv(EXIST_FILE_PATH, index_col='BuffName')
JUDGE_FILE = pd.read_csv(JUDGE_FILE_PATH, index_col='BuffName')
# EFFECT_FILE = pd.read_csv(EFFECT_FILE_PATH, index_col='BuffName')


def process_buff(buff_0, sub_exist_buff_dict, mission, time_now, selected_characters, LOADING_BUFF_DICT):
    all_match, judge_condition_dict, active_condition_dict = BuffInitialize(buff_0.ft.index, sub_exist_buff_dict)
    all_match = BuffJudge(buff_0, judge_condition_dict, all_match, mission)
    if not all_match:
        return
    for char in selected_characters:
        buff_new = Buff(active_condition_dict, judge_condition_dict)
        for sub_mission_start_tick, sub_mission in mission.mission_dict.items():
            if time_now - 1 < sub_mission_start_tick <= time_now:
                buff_new.update(char, time_now, mission.skill_node.skill.ticks, sub_exist_buff_dict, sub_mission)
                LOADING_BUFF_DICT[char].append(buff_new)
                # report_to_log(f'[Buff LOAD]:{time_now}:{char}的{buff_0.ft.index}已加载', level=4)


def BuffLoadLoop(time_now: float, load_mission_dict: dict, existbuff_dict: dict, character_name_box: list,
                 LOADING_BUFF_DICT: dict):
    """
    这是buff修改三部曲的第二步,也是最核心的一个步骤.
    该函数有以下几个功能:
        0, 判断当前的事件具体阶段，如果is_happening返回False，则直接跳过。
        1,判断当前动作是否会触发buff
            1.1,先判断buff的触发逻辑，也就是buff.logic.simple_judge_logic，
                1.1.1,如果是True，就遍历该buff的触发csv，获取激活参数，并且以此根据索引值和传入的skill的各项属性作对比，对比完全通过，则判定为触发。
                1.1.2, 如果是False，则直接执行buff.logic.xjudge方法，读取json中记录的代码块，执行复杂判断，执行后抛出的依旧是是否触发的信号。
        2,如果buff触发,则立刻重新实例化一个新的buff出来，并且根据buff的各种属性，修改它们的各项dynamic属性值，主要集中在count、startticks、endticks中。
        3,修改buff源头（existbuff_dict）中，对应buff的history值，主要是active_times属性的修改。
        4,将这个修改回传给新的buff实例，更新buff实例的history值。
        5,将buff添加到LOADING_BUFF_DICT中,这部分需要和受益者进行打组合，形成字典
        6,受益者是激活判断.csv中的一个字段,叫做add_buff_to,它由2进制转译为10进制并记录,
            在buff实例化的时候,这个字段会一起被实例化,并且可以用buff.ft.add_buff_to调用,
            具体的翻译表如下:
    给自己___下一个__上一个_____二进制______含义
    0__________0________0___________000____________无
    0__________0________1___________001____________只给上一个
    0__________1________0___________010____________只给下一个
    0__________1________1___________011____________给所有后台角色
    1__________0________0___________100____________只给自己
    1__________0________1___________101____________给自己和上一个
    1__________1________0___________110____________给自己和下一个
    1__________1________1___________111____________给全队
        7,另外，程序运行时,需要传入的几个参数中,character_order_dict中记录了当前tick中角色的前后台关系,
            该DICT包含了三个key,分别是:on_field, next 和 previous三个,分别代表当前在场,下一位和上一位,
        8, 由于所有的buff的更新规则可以被分为以下三类，
            ①复杂逻辑（用json中的复杂代码块单走）；
            ②动作开始时/结束时更新（由prejudge和endjudge分别控制，endjudge是10.16新增的参数，用来标志那些结束时更新的buff，但是游戏中  目前暂无此类buff）
            ③动作命中时更新（由hitincrease控制，如果hitincrease为True，则需要检索事件链表内的hit节点）
            所以，一旦事件的is_happening函数返回True（事件正在发生），就需要在每个tick判断当前发生的具体事件，用函数check_current_event()实现
            并且核心是一组if elif 判断，不同的分支执行不同的更新规则；  """
    # 初始化LOADING_BUFF_DICT
    for character in character_name_box:
        LOADING_BUFF_DICT[character] = []
    # 遍历load_mission_dict中的任务
    for mission in load_mission_dict.values():
        if not isinstance(mission, LoadingMission):
            raise TypeError(f"当前{mission}不是SkillNode类！")
        character_name = mission.mission_character
        if character_name not in existbuff_dict:
            raise ValueError(f'当前角色的Buff源并未创建！')
        # 提取当前角色的 Buff 列表
        sub_exist_buff_dict = existbuff_dict[character_name]
        for buff_key, buff_0 in sub_exist_buff_dict.items():
            if not isinstance(buff_0, Buff):
                raise TypeError(f"当前{buff_key}不是Buff类！")
            # 提前计算添加Buff的角色列表
            adding_code = str(int(buff_0.ft.add_buff_to)).zfill(3)
            selected_characters = [character_name_box[i] for i in range(len(character_name_box)) if adding_code[i] == '1']
            # 处理每个 Buff 的逻辑
            process_buff(buff_0, sub_exist_buff_dict, mission, time_now, selected_characters, LOADING_BUFF_DICT)
    return LOADING_BUFF_DICT


def BuffInitialize(buff_name: str, existbuff_dict: dict):
    # 对单个buff进行初始化，抛出一个触发状态参数，两个参数序列。
    all_match = False
    buff_now = existbuff_dict[buff_name]
    if not isinstance(buff_now, Buff):
        raise ValueError(f'当前正在检索的Buff：{buff_name}并不是Buff类！')
    if buff_name not in JUDGE_FILE.index:
        raise ValueError(f'Buff{buff_name}不在JUDGE_FILE中！')
    judge_condition_dict = JUDGE_FILE.loc[buff_name].replace({pd.NA: None, pd.NaT: None, np.nan: None})
    active_condition_dict = EXIST_FILE.loc[buff_name].replace({pd.NA: None, pd.NaT: None, np.nan: None})
    active_condition_dict['BuffName'] = buff_name
    # 根据buff名称，直接把判断信息从JUDGE_FILE中提出来并且转化成dict。
    return all_match, judge_condition_dict, active_condition_dict


def BuffJudge(buff_now: Buff, judge_condition_dict, all_match: bool, mission: LoadingMission):
    skill_now = mission.skill_node.skill
    if not isinstance(skill_now, Skill.InitSkill):
        raise TypeError(f"{skill_now}并非Skill类！")
    if buff_now.ft.simple_judge_logic:
        for conditions in BUFF_LOADING_CONDITION_TRANSLATION_DICT:
            judge_conditions = BUFF_LOADING_CONDITION_TRANSLATION_DICT[conditions]
            if judge_condition_dict[conditions] is None:
                continue
            else:
                if judge_condition_dict[conditions] != getattr(skill_now, judge_conditions):
                    all_match = False
                    return all_match
        else:
            all_match = True
    else:
        exec(buff_now.logic.xjudge)
    return all_match


if __name__ == "__main__":      # 测试
    Charname_box = ['艾莲', '苍角', '莱卡恩']
    Judge_list_set = [['艾莲', '深海访客', '极地重金属'], ['苍角', '含羞恶面', '自由蓝调'], ['莱卡恩', '拘缚者', '镇星迪斯科']]
    weapon_dict = {'艾莲': ['深海访客', 1], '苍角': ['含羞恶面', 5], '莱卡恩': ['拘缚者', 1]}
    exist_buff_dict = buff_exist_judge(Charname_box, Judge_list_set, weapon_dict)
    timelimit = 3600
    load_mission_dict = {}
    LOADING_BUFF_DICT = {}
    p = Preload.Preload(Skill_Class.Skill(CID=1221), Skill_Class.Skill(CID=1191))
    name_dict = {}
    for tick in tqdm.trange(timelimit):
        p.do_preload(tick)
        preload_action_list = p.preload_data.preloaded_action
        if preload_action_list:
            SkillEventSplit(preload_action_list, load_mission_dict, name_dict, tick)
        BuffLoadLoop(tick, load_mission_dict, exist_buff_dict, Charname_box, LOADING_BUFF_DICT)









