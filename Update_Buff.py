def Update_Buff(dynamic_buff_list:list, tick):
    for buff in dynamic_buff_list:
        if buff.ft.simple_logic:
            if tick >= buff.dy.endtime:
                dynamic_buff_list.remove(buff)
        else:
            pass
    return dynamic_buff_list