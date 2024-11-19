import Enemy
from Buff.buff_class import Buff
from Buff.BuffAdd import add_debuff_to_enemy


def ScheduleBuffSettle(time_tick: int, exist_buff_dict: dict, enemy: Enemy.Enemy, DYNAMIC_BUFF_DICT: dict):
    for char_name, sub_exist_buff_dict in exist_buff_dict.items():
        for buff in sub_exist_buff_dict.values():
            if not isinstance(buff, Buff):
                raise TypeError(f'{buff}不是Buff类！')
            if not buff.ft.schedule_judge:
                continue
            # EXPLAIN：在schedule阶段处理的buff一般都是复杂buff，所以不管判定条件多简单，都直接通过xjudge来完成判断。
            # Buff判定
            all_match = buff.logic.xjudge()
            if not all_match:
                continue
            # Buff 激活
            buff_new = Buff.create_new_from_existing(buff)
            if buff.ft.simple_effect_logic:
                buff_new.simple_start(time_tick, sub_exist_buff_dict)
            else:
                buff_new.logic.xeffect()
                buff_new.update_to_buff_0(buff)

            # Buff加载
            buff_existing_check = next((existing_buff for existing_buff in DYNAMIC_BUFF_DICT[char_name] if existing_buff.ft.index == buff.ft.index), None)
            if buff_existing_check:
                DYNAMIC_BUFF_DICT[char_name].remove(buff_existing_check)
            DYNAMIC_BUFF_DICT[char_name].append(buff_new)
            if char_name == 'enemy':
                add_debuff_to_enemy(buff_new, char_name, enemy)

