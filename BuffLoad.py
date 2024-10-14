from BuffClass import Buff
from CharSet_new import Character


def buff_load(CHARACTER_ORDER_DICT: dict,
              existbuff_dict: dict,
              action,
              used_buffname_box: list,
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
    """
    for _ in CHARACTER_ORDER_DICT:
        if LOADING_BUFF_DICT[_] is None:
            LOADING_BUFF_DICT[_] = []
    # 对LOADING_BUFF_DICT进行初始化
    for buff_name in existbuff_dict:
        buff_now = existbuff_dict[buff_name]
        if not isinstance(buff_now,  Buff):
            raise ValueError(f'当前正在检索的{buff_name}并不是Buff类！')
        # Buff类的保险
        if buff_now.ft.simple_judge_logic:
            all_match = False
        else:
            exec(buff_now.logic.xjudge)


    #
    #
    # for item in existbuff_dict:
    #     buff = existbuff_dict[item]
    #     if not isinstance(buff, Buff):
    #         raise ValueError(f'在buff_load环节发现{existbuff_dict}中的{buff}不是Buff类的实例')
    #     if buff.ft.simple_judge_logic:
    #         pass
    #     else:
    #         buff.logic.xjudge
    #
    #     binary_str = f'{int(buff.ft.add_buff_to):03b}'