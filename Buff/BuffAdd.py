from Report import report_to_log
from Buff import Buff


def buff_add(timenow: float,
             LOADING_BUFF_DICT: dict,
             DYNAMIC_BUFF_DICT: dict):
    """
    该函数是Buff三部曲中的最后一步。
    它负责把LOADING_BUFF_DICT中的待加载的buff添加到对应角色的Dynamic_Buff_List中，\n
    在这个过程中，buff_add函数会轮询LOADING_BUFF_DICT，查询其中所有buff实例的buff.dy.startticks，
    如果starticks = time_now，则执行添加，
    要把被添加的buff从LOADING_BUFF_DICT中移除，同时将它添加到DYNAMIC_BUFF_DICT中。
    """
    for char in LOADING_BUFF_DICT:
        if not LOADING_BUFF_DICT[char]:
            continue
        for buff in LOADING_BUFF_DICT[char]:
            if not isinstance(buff, Buff):
                raise ValueError(f'loading_buff_dict中的{buff}元素不是Buff类')
            buff_existing_check = next((existing_buff for existing_buff in DYNAMIC_BUFF_DICT[char] if existing_buff.ft.index == buff.ft.index), None)
            # 这个语句的作用是，检查buff是否已经存在。检查的索引是buff.ft.index。
            if buff_existing_check:
                DYNAMIC_BUFF_DICT[char].remove(buff_existing_check)
                DYNAMIC_BUFF_DICT[char].append(buff)
                # report_to_log(f'[Buff ADD]:{timenow}:{buff_existing_check.ft.name}刷新了')
            else:
                DYNAMIC_BUFF_DICT[char].append(buff)
                # report_to_log(f'[Buff ADD]:{timenow}:{buff.ft.name}第{buff.history.active_times}次触发:endticks:{buff.dy.endticks}')
    return DYNAMIC_BUFF_DICT
