from BuffClass import Buff
from CharSet_new import Character
from Skill_Class import Skill
import pandas as pd
from define import BUFF_LOADING_CONDITION_TRANSLATION_DICT, JUDGE_FILE_PATH, EXIST_FILE_PATH, EFFECT_FILE_PATH

EXIST_FILE = pd.read_csv(EXIST_FILE_PATH, index_col='BuffName')
JUDGE_FILE = pd.read_csv(JUDGE_FILE_PATH, index_col='BuffName')
EFFECT_FILE = pd.read_csv(EFFECT_FILE_PATH, index_col='BuffName')


def buff_load(timenow: float,
              action: Skill,
              be_hitted: bool,
              CHARACTER_ORDER_DICT: dict,
              existbuff_dict: dict,
              action_name: str,
              LOADING_BUFF_DICT: dict):
    """
    这是buff修改三部曲的第二步,也是最核心的一个步骤.\n
    该函数有以下几个功能:\n
        1,判断当前动作是否会触发buff\n
            1.1,先判断buff的触发逻辑，也就是buff.logic.simple_judge_logic，
                1.1.1,如果是True，就遍历该buff的触发csv，获取激活参数，并且以此根据索引值和传入的skill的各项属性作对比，对比完全通过，则判定为触发。
                1.1.2, 如果是False，则直接执行buff.logic.xjudge方法，读取json中记录的代码块，执行复杂判断，执行后抛出的依旧是是否触发的信号。
        2,如果buff触发,则立刻重新实例化一个新的buff出来，并且根据buff的各种属性，修改它们的各项dynamic属性值，主要集中在count、startticks、endticks中。
        3,修改buff源头（existbuff_dict）中，对应buff的history值，主要是active_times属性的修改。
        4,将这个修改回传给新的buff实例，更新buff实例的history值。
        5,将buff添加到LOADING_BUFF_DICT中,这部分需要和受益者进行打组合，形成字典\n
        6,受益者是激活判断.csv中的一个字段,叫做add_buff_to,它由2进制转译为10进制并记录,\n
            在buff实例化的时候,这个字段会一起被实例化,并且可以用buff.ft.add_buff_to调用,\n
            具体的翻译表如下:\n
    给自己___下一个__上一个_____二进制______含义
    0__________0________0___________000____________无
    0__________0________1___________001____________只给上一个
    0__________1________0___________010____________只给下一个
    0__________1________1___________011____________给所有后台角色
    1__________0________0___________100____________只给自己
    1__________0________1___________101____________给自己和上一个
    1__________1________0___________110____________给自己和下一个
    1__________1________1___________111____________给全队
        7,另外，程序运行时,需要传入的几个参数中,character_order_dict中记录了当前tick中角色的前后台关系,\n
            该DICT包含了三个key,分别是:on_field, next 和 previous三个,分别代表当前在场,下一位和上一位,\n
        8, 对于那些在命中时叠层的buff，应该用相同的函数进行处理。逻辑如下：
            8.1, 当该程序检测到当前的事件标签是Action_Start，就会判定一次Buff是否触发；
                    此时触发的buff应该是那些刚一抬手就会触发的buff，这需要一个Active_when_action_start参数来控制，
                    也就是“动作开始时更新”
                    另一个触发器则是
            8.2, 若buff会在事件命中时更新，
    """
    all_match = None
    for _ in CHARACTER_ORDER_DICT:
        if LOADING_BUFF_DICT[_] is None:
            LOADING_BUFF_DICT[_] = []
    # 对LOADING_BUFF_DICT进行初始化
    for buff_name in existbuff_dict:
        buff_now = existbuff_dict[buff_name]
        if not isinstance(buff_now,  Buff):
            raise ValueError(f'当前正在检索的Buff：{buff_name}并不是Buff类！')

        if buff_name not in JUDGE_FILE.index:
            raise ValueError(f'Buff{buff_name}不在JUDGE_FILE中！')
        judge_condition_dict = JUDGE_FILE.loc[buff_name].to_dict()
        active_condition_dict = EXIST_FILE.loc[buff_name].to_dict()
        # 根据buff名称，直接把判断信息从JUDGE_FILE中提出来并且转化成dict。

        if buff_now.ft.simple_judge_logic:
            all_match = False
            for conditions in BUFF_LOADING_CONDITION_TRANSLATION_DICT:
                if judge_condition_dict[conditions] != action.get_skill_info(skill_tag=action_name, attr_info=BUFF_LOADING_CONDITION_TRANSLATION_DICT[conditions]):
                    all_match = False
            else:
                all_match = True
        else:
            exec(buff_now.logic.xjudge)
        if all_match:
            buff_new = Buff(active_condition_dict, judge_condition_dict)
            buff_new.dy.active = True
            # 实例化一个新的Buff出来
            buff_now.history.active_times += 1
            buff_new.history.active_times = buff_now.history.active_times
            buff_new.timeupdate(buff_now, action.get_skill_info(skill_tag=action_name, attr_info="ticks"), timenow)
            buff_new.countupdate(be_hitted)
            #   以上这些是初始化，只有在检测到事件的状态是“开始”标签时才会执行。




