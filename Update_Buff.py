from BuffClass import Buff
from Report import report_to_log


def update_dynamic_bufflist(DYNAMIC_BUFF_DICT:dict, timetick, charname_box, exist_buff_dict: dict):
    """
    该函数是buff修改三部曲的第一步,\n
    \n
    位于整个main函数主循环的第二部分,紧跟在tick_update函数之后.\n
    这个函数主要用于更新DYNAMIC_BUFF_DICT,需要扔给它三个参数 \n
    DICT,以及角色名的box(是一个list),以及当前时间timetick \n
    它会轮询charname_box,并且以其中的角色名为key,到DICT中去提取对应的dynamic_buff_list \n
    最后,将这些bufflist中的所有buff,挨个判断结束状态,如果该结束的,则执行buff.end(),并且把buff从list中移除.
    """
    for charname in charname_box:
        sub_exist_buff_dict = exist_buff_dict[charname]
        for _ in DYNAMIC_BUFF_DICT[charname][:]:
            if not isinstance(_, Buff):
                raise TypeError(f'{_}不是Buff类！')
            if _.ft.simple_start_logic:
                if timetick >= _.dy.endticks:
                    _.end(timetick, sub_exist_buff_dict)
                    DYNAMIC_BUFF_DICT[charname].remove(_)
                    report_to_log(f"[Buff END]:{timetick}:{_.ft.index}结束，已从动态列表移除", level=4)
            else:
                _.logic.xend
    return DYNAMIC_BUFF_DICT
