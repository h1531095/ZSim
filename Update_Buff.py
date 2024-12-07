from Buff import Buff
from Report import report_to_log, report_buff_to_log
import Enemy
from Dot import BaseDot


def update_dynamic_bufflist(DYNAMIC_BUFF_DICT: dict, timetick, exist_buff_dict: dict, enemy: Enemy.Enemy):
    """
    该函数是buff修改三部曲的第一步,\n
    \n
    位于整个main函数主循环的第二部分,紧跟在tick_update函数之后.\n
    这个函数主要用于更新DYNAMIC_BUFF_DICT,需要扔给它三个参数 \n
    DICT,以及角色名的box(是一个list),以及当前时间timetick \n
    它会轮询charname_box,并且以其中的角色名为key,到DICT中去提取对应的dynamic_buff_list \n
    最后,将这些bufflist中的所有buff,挨个判断结束状态,如果该结束的,则执行buff.end(),并且把buff从list中移除.
    """
    # print([buffs.ft.index for buffs in DYNAMIC_BUFF_DICT['enemy']])
    update_anomaly_bar(timetick, enemy)
    for charname in exist_buff_dict:
        sub_exist_buff_dict = exist_buff_dict[charname]
        for _ in DYNAMIC_BUFF_DICT[charname][:]:
            if not isinstance(_, Buff):
                raise TypeError(f'{_}不是Buff类！')
            if _.ft.is_debuff and charname != 'enemy':
                raise ValueError(f'{_.ft.index}是debuff但是却进入了{charname}的buff池！')
            if (not _.ft.is_debuff) and charname == 'enemy':
                raise ValueError(f'{_.ft.index}是buff但是却在enemy的debuff池中！')
            if _.ft.simple_exit_logic:
                shoud_exit = True
            else:
                shoud_exit = _.logic.xexit()
            if not shoud_exit:
                report_buff_to_log(charname, timetick, _.ft.index, _.dy.count, True, level=4)
                continue
            if _.ft.alltime:
                report_buff_to_log(charname, timetick, _.ft.index, _.dy.count, True, level=4)
                continue
            report_buff_to_log(charname, timetick, _.ft.index, _.dy.count, True, level=4)
            if _.ft.individual_settled:
                if len(_.dy.built_in_buff_box) <= 0:
                    _.end(timetick, sub_exist_buff_dict)
                    if _.ft.is_debuff:
                        # debuff比正常的buff需要多执行一步，那就是将DYNAMIC_BUFF_DICT的修改同步到enemy.dynamic.dynamic_debuff_list中。
                        enemy.dynamic.dynamic_debuff_list.remove(_)
                else:
                    for tuples in _.dy.built_in_buff_box:
                        if tuples[1] <= timetick:
                            _.dy.built_in_buff_box.remove(tuples)
                            _.dy.count = len(_.dy.built_in_buff_box)
            else:
                if timetick >= _.dy.endticks or ((not _.ft.simple_exit_logic) and shoud_exit):
                    # 不管是不是debuff，时间到点了就要结束。所以buff.end()以及对应的DYNAMIC_BUFF_DICT的修改都是必须进行的.
                    if _.ft.index == 'Buff-角色-雅-核心被动-冰焰':
                        print(11111111111111)
                    _.end(timetick, sub_exist_buff_dict)
                    DYNAMIC_BUFF_DICT[charname].remove(_)
                    report_to_log(f"[Buff END]:{timetick}:{_.ft.index}结束，已从动态列表移除", level=4)
                    if _.ft.is_debuff:
                        # debuff比正常的buff需要多执行一步，那就是将DYNAMIC_BUFF_DICT的修改同步到enemy.dynamic.dynamic_debuff_list中。
                        enemy.dynamic.dynamic_debuff_list.remove(_)

        update_dot(enemy, timetick)
    return DYNAMIC_BUFF_DICT


def update_dot(enemy: Enemy.Enemy, timetick):
    for _ in enemy.dynamic.dynamic_dot_list[:]:
        if not isinstance(_, BaseDot.Dot):
            raise TypeError(f'Enemy的dot列表中的{_}不是Dot类！')
        if timetick >= _.dy.end_ticks:
            _.end(timetick)
            enemy.dynamic.dynamic_dot_list.remove(_)
            report_to_log(f"[Dot END]:{timetick}:{_.ft.index}结束，已从动态列表移除", level=4)

def update_anomaly_bar(time_now: int ,enemy: Enemy.Enemy):
    for element_type, bar in enemy.anomaly_bars_dict.items():
        bar.check_myself(time_now)
        setattr(enemy.dynamic, enemy.trans_anomaly_effect_to_str[element_type], bar.active)


