from BuffClass import Buff
def update_dynamic_bufflist(DYNAMIC_BUFF_DICT:dict, timetick, charname_box):
    """
    这个函数主要用于更新DYNAMIC_BUFF_DICT,需要扔给它三个参数 \n
    DICT,以及角色名的box(是一个list),以及当前时间timetick \n
    它会轮询charname_box,并且以其中的角色名为key,到DICT中去提取对应的dynamic_buff_list \n
    最后,将这些bufflist中的所有buff,挨个判断结束状态,如果该结束的,则执行buff.end(),并且把buff从list中移除.
    """
    for charname in charname_box:
        for _ in DYNAMIC_BUFF_DICT[charname]['dynamic_buff_list'][:]:
            if isinstance(_, Buff):
                if _.ft.simple_start_logic:
                    if timetick >= _.dy.endticks:
                        _.end(timetick)
                        DYNAMIC_BUFF_DICT[charname]['dynamic_buff_list'].remove(_)
                else:
                    _.logic.xend
    return DYNAMIC_BUFF_DICT
