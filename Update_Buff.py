from BuffClass import Buff
def update_dynamic_bufflist(dynamic_buff_list:list, timetick):
    for buff in dynamic_buff_list[:]:
        if isinstance(buff, Buff):
            if buff.ft.simple_start_logic:
                if timetick >= buff.dy.endticks:
                    buff.end(timetick)
                    dynamic_buff_list.remove(buff)
            else:
                buff.logic.xend
    return dynamic_buff_list