from BuffClass import Buff
from CharSet_new import Character
from Skill_Class import Skill
from SkillsQueue import SkillNode
from LinkedList import LinkedList
import pandas as pd
from SkillEventSplit import SkillEventSplit, LoadingMission
from define import BUFF_LOADING_CONDITION_TRANSLATION_DICT, JUDGE_FILE_PATH, EXIST_FILE_PATH, EFFECT_FILE_PATH

EXIST_FILE = pd.read_csv(EXIST_FILE_PATH, index_col='BuffName')
JUDGE_FILE = pd.read_csv(JUDGE_FILE_PATH, index_col='BuffName')
EFFECT_FILE = pd.read_csv(EFFECT_FILE_PATH, index_col='BuffName')


def BuffLoadLoop(time_now: float,
                load_mission_dict: dict,
                existbuff_dict: dict):
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

    for mission in load_mission_dict.values():
        if not isinstance(mission, LoadingMission):
            raise TypeError(f"当前{mission}不是SkillNode类！")
        print(f"当前动作为{mission.mission_tag}")
        # 先用existbuff_dict 中的buff_0 进行判断，是否触发。这一步不需要修改buff的值。
        # 判断结束后，抛出all_match。
        for buff in existbuff_dict:
            buff_0 = existbuff_dict[buff]
            if not isinstance(buff_0, Buff):
                raise TypeError(f"当前{buff}不是Buff类！")
            all_match, judge_condition_dict, active_condition_dict = BuffInitialize(buff_0.ft.name, existbuff_dict)
            all_match = BuffJudge(buff_0, judge_condition_dict, all_match, mission)
            print(f"\t当前检验的buff为{buff_0.ft.name}, all_match判定结果为{all_match}")
            if not all_match:
                continue
            sub_mission = None
            for sub_mission_start_tick in mission.mission_dict:
                if not (time_now - 1 <= sub_mission_start_tick <= time_now):
                    continue
                sub_mission = mission.mission_dict[sub_mission_start_tick]
                if sub_mission == 'start':
                    print(f'\t\t现在子任务是{sub_mission}')
                    pass
                elif sub_mission == 'hit':
                    print(f'\t\t现在子任务是{sub_mission}')
                    pass
                elif sub_mission == 'end':
                    print(f'\t\t现在子任务是{sub_mission}')
                    pass


def BuffInitialize(buff_name: str, existbuff_dict: dict):
    # 对单个buff进行初始化，抛出一个触发状态参数，两个参数序列。
    all_match = False
    buff_now = existbuff_dict[buff_name]
    if not isinstance(buff_now,  Buff):
        raise ValueError(f'当前正在检索的Buff：{buff_name}并不是Buff类！')
    if buff_name not in JUDGE_FILE.index:
        raise ValueError(f'Buff{buff_name}不在JUDGE_FILE中！')
    judge_condition_dict = JUDGE_FILE.loc[buff_name].to_dict()
    active_condition_dict = EXIST_FILE.loc[buff_name].to_dict()
    # 根据buff名称，直接把判断信息从JUDGE_FILE中提出来并且转化成dict。
    return all_match, judge_condition_dict, active_condition_dict


def BuffJudge(buff_now:Buff, judge_condition_dict, all_match: bool, mission: LoadingMission):
    skill_now = mission.skill_node.skill
    if not isinstance(skill_now, Skill):
        raise TypeError(f"{skill_now}并非Skill类！")
    if buff_now.ft.simple_judge_logic:
        for conditions in BUFF_LOADING_CONDITION_TRANSLATION_DICT:
            if judge_condition_dict[conditions] != skill_now.get_skill_info(skill_tag=mission.mission_tag,
            attr_info = BUFF_LOADING_CONDITION_TRANSLATION_DICT[conditions]):
                all_match = False
                return all_match
        else:
            all_match = True
    else:
        exec(buff_now.logic.xjudge)
    return all_match

#     if all_match:
#         buff_new = Buff(active_condition_dict, judge_condition_dict)
#         buff_new.dy.active = True
#         # 实例化一个新的Buff出来
#         buff_now.history.active_times += 1
#         buff_new.history.active_times = buff_now.history.active_times
#         buff_new.timeupdate(buff_now, action.get_skill_info(skill_tag=action_name, attr_info="ticks"), timenow)
#         buff_new.countupdate(be_hitted)
#         以上这些是初始化，只有在检测到事件的状态是“开始”标签时才会执行


 if __name__ == '__main__':
    pass
    # CHARACTER_ORDER_DICT = {}
    # LOADING_BUFF_DICT = {}
    # for _ in CHARACTER_ORDER_DICT.values():
    #     if LOADING_BUFF_DICT[_] is None:
    #         LOADING_BUFF_DICT[_] = []