import Load
import sys
from Buff.buff_class import Buff
from Buff.BuffAdd import add_debuff_to_enemy


def ScheduleBuffSettle(time_tick: int, exist_buff_dict: dict, enemy, DYNAMIC_BUFF_DICT: dict, action_stack):
    for char_name, sub_exist_buff_dict in exist_buff_dict.items():
        main_module = sys.modules['__main__']
        name_box_now = main_module.load_data.name_box + ['enemy']
        for buff in sub_exist_buff_dict.values():
            if not isinstance(buff, Buff):
                raise TypeError(f'{buff}不是Buff类！')
            if not buff.ft.schedule_judge:
                continue
            action_now = action_stack.peek()
            if not isinstance(action_now, Load.LoadingMission):
                raise TypeError(f'{action_now}不是LoadingMission类！')
            if buff.ft.passively_updating:
                continue
            else:
                if buff.ft.operator != action_now.mission_node.char_name:
                    continue
            # EXPLAIN：在schedule阶段处理的buff一般都是复杂buff，所以不管判定条件多简单，都直接通过xjudge来完成判断。
            # Buff判定
            all_match = buff.logic.xjudge()
            if not all_match:
                continue
            # Buff 激活
            adding_buff_code = str(int(buff.ft.add_buff_to)).zfill(4)
            selected_characters = [name_box_now[i] for i in range(len(name_box_now)) if adding_buff_code[i] == '1']
            for characters in selected_characters:
                buff_new = Buff.create_new_from_existing(buff)
                if buff.ft.simple_effect_logic:
                    buff_new.simple_start(time_tick, sub_exist_buff_dict)
                else:
                    buff_new.logic.xeffect()
                    buff_new.update_to_buff_0(buff)
                # Buff加载
                buff_existing_check = next((existing_buff for existing_buff in DYNAMIC_BUFF_DICT[characters] if existing_buff.ft.index == buff.ft.index), None)
                if buff_existing_check:
                    DYNAMIC_BUFF_DICT[characters].remove(buff_existing_check)
                DYNAMIC_BUFF_DICT[characters].append(buff_new)
                if characters == 'enemy':
                    add_debuff_to_enemy(buff_new, characters, enemy)
