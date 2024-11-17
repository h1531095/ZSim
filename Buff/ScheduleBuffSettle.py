import Enemy
from Buff.buff_class import Buff


def ScheduleBuffSettle(exist_buff_dict: dict, enemy: Enemy.Enemy):
    for char_nam, sub_exist_buff_dict in exist_buff_dict:
        for buff in sub_exist_buff_dict:
            if not isinstance(buff, Buff):
                raise TypeError(f'{buff}不是Buff类！')
            if not buff.ft.schedule_judge:
                continue
            # EXPLAIN：在schedule阶段处理的buff一般都是复杂buff，所以不管判定条件多简单，都直接通过xjudge来完成判断。
            all_match = buff.logic.xjudge()
            if not all_match:
                continue
            