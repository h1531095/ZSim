import Enemy
import Load
import Dot


def SpawnDamageEvent(mission: Load.LoadingMission | Dot.Dot, event_list: list):
    """
    负责往event_list中添加伤害生成事件，添加的内容是实例：
    要么是SkillNode的实例，要么是Dot的实例。
    """
    if isinstance(mission, Load.LoadingMission):
        if mission.hitted_count > mission.mission_node.hit_times:
            raise ValueError(f'{mission.mission_tag}目前是第{mission.hitted_count}，最多{mission.mission_node.hit_times}')
        mission.hitted_count += 1
        event_list.append(mission.mission_node)
    elif isinstance(mission, Dot.Dot):
        if mission.dy.effect_times > mission.ft.max_effect_times:
            raise ValueError('该Dot任务已经完成，应当被删除！')
        mission.dy.effect_count += 1
        mission.dy.ready = False
        event_list.append(mission)


def ProcessTimeUpdateDots(timetick: int, dot_list: list, event_list: list):
    """
    处理effect_rules == 1的Dot对象，始终检查是否应触发。
    """
    for dot in dot_list:
        if not isinstance(dot, Dot.Dot):
            raise TypeError(f'{dot}不是Dot类！')

        # 只处理 effect_rules == 1 的 Dot
        if dot.ft.effect_rules == 1:
            dot.ready_judge(timetick)
            if dot.dy.ready:
                SpawnDamageEvent(dot, event_list)


def ProcessHitUpdateDots(timetick: int, dot_list: list, event_list: list):
    """
    处理effect_rules == 2的Dot对象，只在Mission触发时检查。
    """
    for dot in dot_list:
        if not isinstance(dot, Dot.Dot):
            raise TypeError(f'{dot}不是Dot类！')

        # 只处理 effect_rules == 2 的 Dot
        if dot.ft.effect_rules == 2:
            dot.ready_judge(timetick)
            if dot.dy.ready:
                SpawnDamageEvent(dot, event_list)


def DamageEventJudge(timetick: int, load_mission_dict: dict, enemy: Enemy.Enemy, event_list: list):
    """
    DamageEvent的Judge函数：轮询load_mission_dict以及enemy.dynamic_dot_list，判断是否应生成Hit事件。
    并且当Hit时间生成时，将对应的实例添加到event_list中。
    """
    # 处理 Load.Mission 任务
    for mission in load_mission_dict.values():
        if not isinstance(mission, Load.LoadingMission):
            raise TypeError(f'{mission}不是LoadingMission类！')
        for sub_mission_tick in mission.mission_dict:
            if timetick-1 < sub_mission_tick <= timetick and mission.mission_dict[sub_mission_tick] == 'hit':
                print(timetick)
                SpawnDamageEvent(mission, event_list)
            # 当Mission触发时，检查 effect_rules == 2 的 Dot
                ProcessHitUpdateDots(timetick, enemy.dynamic.dynamic_dot_list, event_list)
    # 始终检查 effect_rules == 1 的 Dot
    ProcessTimeUpdateDots(timetick, enemy.dynamic.dynamic_dot_list, event_list)
