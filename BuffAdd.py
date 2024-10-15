from Report import report_to_log
from BuffClass import Buff


def buff_add(timenow: float,
             timecost: float,
             be_hitted: bool,
             LOADING_BUFF_DICT: dict,
             DYNAMIC_BUFF_DICT: dict,
             existbuff_dict: dict):
    """
    该函数是Buff三部曲中的最后一步。
    它负责把LOADING_BUFF_DICT中的待加载的buff添加到对应角色的Dynamic_Buff_List中，\n
    在这个过程中，buff_add函数会轮询LOADING_BUFF_DICT，查询其中所有buff实例的buff.dy.startticks，
    如果starticks = timenow，则执行添加，
    要把被添加的buff从LOADING_BUFF_DICT中移除，同时将它添加到DYNAMIC_BUFF_DICT中。
    """
    for char in LOADING_BUFF_DICT:
        if char == 'empty':
            continue
        for buff in LOADING_BUFF_DICT[char]:
            if not isinstance(buff, Buff):
                raise ValueError(f'loading_buff_dict中的{buff}元素不是Buff类')
            if not buff.readyjudge(timenow):
                report_to_log(f'[Buff INFO]:{timenow}:{buff.ft.name}因内置CD未就绪触发失败.')
                continue
            if buff.dy.startticks <= timenow:
                # 这里，buff的startticks和当前的tick进行比较。如果startticks<=timenow，则意味着buff需要在当前tick执行。
                # 如果不符合条件，则说明该buff需要在以后执行，不是现在。所以直接用continue跳过。
                # 由于程序的运行逻辑永远都是在主循环的开头令当前tick+= 1，
                # 所以，本轮主循环内使用的所谓的“当前tick”数值，其实是这个tick的最后一刻，
                # 比如，当前tick数值是1，代表的是，当前时间段是tick0~1的这个阶段，且是（0，1]
                # 所以，当前tick内所有被考察的事件的startticks属性不需要取整，直接和当前tick比较即可。
                continue
            buff_existing_chek = next((existing_buff for existing_buff in DYNAMIC_BUFF_DICT[char]['dynamic_buff_list'] if  existing_buff.ft.name == buff.ft.name), None)
            # 这个语句的作用是，检查buff是否已经存在。检查的索引是buff.ft.name。
            if buff_existing_chek:
                DYNAMIC_BUFF_DICT[char]['dynamic_buff_list'].remove(buff_existing_chek)
                report_to_log(f'[Buff INFO]:{timenow}:老的{buff_existing_chek.ft.name}被移除,并已经添加新的buff.')
            DYNAMIC_BUFF_DICT[char]['dynamic_buff_list'].append(buff)
            report_to_log(f'[Buff INFO]:{timenow}:{buff.ft.name}第{buff.dy.activetimes}次触发:endticks:{buff.dy.endticks}')
    return DYNAMIC_BUFF_DICT
