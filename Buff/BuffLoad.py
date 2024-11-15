import numpy as np
import pandas as pd

import Load
from Skill_Class import Skill
from Buff.BuffExist_Judge import buff_exist_judge
from Buff.buff_class import Buff
from define import BUFF_LOADING_CONDITION_TRANSLATION_DICT, JUDGE_FILE_PATH, EXIST_FILE_PATH

EXIST_FILE = pd.read_csv(EXIST_FILE_PATH, index_col='BuffName')
JUDGE_FILE = pd.read_csv(JUDGE_FILE_PATH, index_col='BuffName')
JUDGE_FILE = JUDGE_FILE.replace({np.nan: None})
EXIST_FILE = EXIST_FILE.replace({np.nan: None})


class BuffInitCache:
    def __init__(self):
        self.cache = {}

    def get(self, key):
        return self.cache.get(key)

    def add(self, key, value):
        self.cache[key] = value
        max_cache = 128
        while len(self.cache) > max_cache:
            self.cache.popitem()


def process_buff(buff_0, sub_exist_buff_dict, mission, time_now, selected_characters, LOADING_BUFF_DICT):
    all_match, judge_condition_dict, active_condition_dict = BuffInitialize(buff_0.ft.index, sub_exist_buff_dict)
    all_match = BuffJudge(buff_0, judge_condition_dict, all_match, mission)
    if not all_match:
        return
    # if not buff_0.ft.is_debuff:
    """
    在20241114的更新中，我删除了debuff分支。因为buff的add_buff_to被拓展成了4字段，所以就没有必要判断是否是debuff了
    如果一个buff是debuff，那么它的add_buff_to字段的最后一位肯定是1，比如0001，
    这样，它就一定会在buff_go_to函数中导致'enemy'字段进入selected_characters列表，这样一来，enemy会被当成正常角色来执行正常的buff添加和update。
    """
    for char in selected_characters:
        buff_new = Buff(active_condition_dict, judge_condition_dict)
        for sub_mission_start_tick, sub_mission in mission.mission_dict.items():
            if time_now - 1 < sub_mission_start_tick <= time_now:
                """
                筛选出正在发生的子任务，如果子任务正在发生就直接执行update，把子任务的str传进buff.update()函数
                并且触发对应的分支（start、hit、end），完成符合buff属性的时间、层数更新。
                """
                buff_new.update(char, time_now, mission.mission_node.skill.ticks, sub_exist_buff_dict, sub_mission)
                LOADING_BUFF_DICT[char].append(buff_new)
                # report_to_log(f'[Buff LOAD]:{time_now}:{char}的{buff_0.ft.index}已加载', level=4)
    # else:
    #     buff_new = Buff(active_condition_dict, judge_condition_dict)
    #     for sub_mission_start_tick, sub_mission in mission.mission_dict.items():
    #         if time_now - 1 < sub_mission_start_tick <= time_now:
    #             buff_new.update('enemy', time_now, mission.mission_node.skill.ticks, sub_exist_buff_dict, sub_mission)
    #             LOADING_BUFF_DICT['enemy'].append(buff_new)



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
            并且核心是一组if elif 判断，不同的分支执行不同的更新规则；
    """
    # 初始化LOADING_BUFF_DICT
    all_name_box = character_name_box + ['enemy']
    for character in all_name_box:
        LOADING_BUFF_DICT[character] = []
    # 遍历load_mission_dict中的任务
    for mission in load_mission_dict.values():
        if not isinstance(mission, Load.LoadingMission):
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
            selected_characters = buff_go_to(buff_0, all_name_box)
            # 处理每个buff的逻辑，但是要区分是buff还是debuff
            process_buff(buff_0, sub_exist_buff_dict, mission, time_now, selected_characters, LOADING_BUFF_DICT)
            """
            注意，这部分的分支，指的是以角色为第一视角来给自己或是其他人添加Buff。这里面的其他人也包括“enemy”。
            由于这里是Load阶段，所以，动作的第一人称永远是角色，只有角色给enemy上debuff的可能性，
            而所有环境或者其他外部因素造成enemy被上了debuff，那应该在schedule阶段执行。
            """
    return LOADING_BUFF_DICT


def buff_go_to(buff_0, all_name_box):
    """
    运行函数前，总有：
    all_name_box  = character_name_box + ['enemy']
    该函数是用来处理buff该加给什么角色的。首先，它需要输入位于exist_buff_dict中的buff_0，
    提取方式:buff_0 = exist_buff_dict[角色名: str][buff名: str]
    其中，角色名是你当前触发Buff事件的主角就，通常为前台角色。当然如果这是一个debuff（buff.ft.is_debuff == True)，角色名就是'enemy'
    buff名指的是Buff的index，调取方式： buff.ft.index
    character_name_box是个list，里面装了三个角色名。请确保这个namebox是新鲜的，以防艾莲加给自己的buff偏到狼哥身上去。
    在函数外部，它们会被强行在尾部添加一个enemy，变成一个4个元素的列表，传入本函数。
    该函数会返回一个新的namebox，以输入的character_name_box是[艾莲，莱卡恩，苍角]为例
    比如这个buff的add_buff_to字段的内容是110（加给自己和下一位），那么新的这个selected_characters就会输出[艾莲，莱卡恩]
    如果字段内容是101（加给自己和上一位），那么新的selected_characters就会输出[艾莲，苍角]
    """
    adding_code = str(int(buff_0.ft.add_buff_to)).zfill(3)
    selected_characters = [all_name_box[i] for i in range(len(all_name_box)) if adding_code[i] == '1']
    return selected_characters


def BuffInitialize(buff_name: str, existbuff_dict: dict, *,cache = BuffInitCache()):
    cache_key = (buff_name, tuple(existbuff_dict.items()))
    if cache_key in cache.cache:
        return cache.get(cache_key)
    # 对单个buff进行初始化，抛出一个触发状态参数，两个参数序列。
    all_match = False
    buff_now = existbuff_dict[buff_name]
    if not isinstance(buff_now, Buff):
        raise ValueError(f'当前正在检索的Buff：{buff_name}并不是Buff类！')
    if buff_name not in JUDGE_FILE.index:
        raise ValueError(f'Buff{buff_name}不在JUDGE_FILE中！')
    judge_condition_dict = JUDGE_FILE.loc[buff_name].copy()
    active_condition_dict = EXIST_FILE.loc[buff_name].copy()
    active_condition_dict['BuffName'] = buff_name
    # 根据buff名称，直接把判断信息从JUDGE_FILE中提出来并且转化成dict。

    results = all_match, judge_condition_dict, active_condition_dict
    cache.add(cache_key, results)
    return results


def BuffJudge(buff_now: Buff, judge_condition_dict, all_match: bool, mission: Load.LoadingMission):
    """
        如果judge_condition_dict的全部内容是None，同时buff还是简单判断逻辑
        说明是环境或是战斗系统自带的debuff，则直接返回False，跳过判断。
    """

    if all(value is None for value in judge_condition_dict.values()) and buff_now.ft.simple_judge_logic:
        return False  # 字典中所有值都是None，跳过判断，返回False

    """
    正常buff的判断逻辑
    """
    skill_now = mission.mission_node.skill
    if not isinstance(skill_now, Skill.InitSkill):
        raise TypeError(f"{skill_now}并非Skill类！")
    if buff_now.ft.simple_judge_logic:
        all_match = True
        """
        先假定all_match是True，一会儿循环过程中一旦有不符合的项，就改成False。
        只有全部通过才能继续维持All_match的值。
        """
        for condition, judge_condition in BUFF_LOADING_CONDITION_TRANSLATION_DICT.items():
            """
            由于SkillNode中的属性名和judge_condition_dict中的键值名不同，
            所以需要BUFF_LOADING_CONDITION_TRANSLATION_DICT进行翻译。
            """
            csv_judge_condition = judge_condition_dict[condition]
            if csv_judge_condition is not None:
                """
                如果键值下面是None则直接跳过。
                """
                final_condition = process_string(csv_judge_condition)
                if getattr(skill_now, judge_condition) not in final_condition:
    else:
        buff_now.logic.xjudge
    return all_match


def process_string(s):
    """
    在2024.11.13的更新中，从csv中读取的数据从单个数值变成了字符串，但是数据类型有点复杂。
    如果单元格内没有分隔符，那么就会被转化为单元素列表，且会自动转换其中的数字为int，
    如果有分隔符，则会根据分隔符打散成列表，并且将其中的数字转化成int。
    由于getattr方法获得的技能属性的数值永远是单个的，所以用 技能属性 in list 的判定逻辑，
    这样就可以实现“或”逻辑。
    """
    if '|' in s:
        split_list = s.split('|')
        return [int(item) if item.isdigit() else item for item in split_list]
    else:
        return [int(s) if s.isdigit() else s]


if __name__ == "__main__":      # 测试
    Charname_box = ['艾莲', '苍角', '莱卡恩']
    Judge_list_set = [['艾莲', '深海访客', '极地重金属'], ['苍角', '含羞恶面', '自由蓝调'], ['莱卡恩', '拘缚者', '镇星迪斯科']]
    weapon_dict = {'艾莲': ['深海访客', 1], '苍角': ['含羞恶面', 5], '莱卡恩': ['拘缚者', 1]}
    exist_buff_dict = buff_exist_judge(Charname_box, Judge_list_set, weapon_dict)
    timelimit = 3600
    load_mission_dict = {}
    LOADING_BUFF_DICT = {}
    import Preload
    p = Preload.Preload(Skill(CID=1221), Skill(CID=1191))
    name_dict = {}
    import tqdm
    for tick in tqdm.trange(timelimit):
        p.do_preload(tick)
        preload_action_list = p.preload_data.preloaded_action
        if preload_action_list:
            Load.SkillEventSplit(preload_action_list, load_mission_dict, name_dict, tick)
        BuffLoadLoop(tick, load_mission_dict, exist_buff_dict, Charname_box, LOADING_BUFF_DICT)









