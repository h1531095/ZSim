def Update_Dynamic_Bufflist(dynamic_buff_list:list, tick):
    for buff in dynamic_buff_list:
        if buff.ft.simple_logic:
            if tick >= buff.dy.endtime:
                dynamic_buff_list.remove(buff)
        else:
            buff.logic.xlogic
    return dynamic_buff_list