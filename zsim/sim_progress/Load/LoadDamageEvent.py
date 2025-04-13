from ..Update import UpdateAnomaly
from .. import Dot
# import Enemy
from .loading_mission import LoadingMission


def SpawnDamageEvent(mission: LoadingMission | Dot.Dot, event_list: list):
    """
    负责往event_list中添加伤害生成事件，添加的内容是实例：
    要么是SkillNode的实例，要么是Dot的实例。
    """
    if isinstance(mission, LoadingMission):
        if mission.hitted_count > mission.mission_node.hit_times:
            raise ValueError(f'{mission.mission_tag}目前是第{mission.hitted_count}，最多{mission.mission_node.hit_times}')
        mission.hitted_count += 1
        event_list.append(mission)
    elif isinstance(mission, Dot.Dot):
        if mission.dy.effect_times > mission.ft.max_effect_times:
            raise ValueError('该Dot任务已经完成，应当被删除！')
        event_list.append(mission.anomaly_data)


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
                dot.dy.last_effect_ticks = timetick
                dot.dy.ready = False
                dot.dy.effect_times += 1
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
                dot.dy.ready = False
                dot.dy.last_effect_ticks = timetick
                dot.dy.effect_times += 1


def ProcessFreezLikeDots(timetick: int, enemy, event_list: list):
    """
    所有碎冰类逻辑的dot都用此函数结算。
    """
    dot_list = enemy.dynamic.dynamic_dot_list
    for dot in dot_list[:]:
        if not isinstance(dot, Dot.Dot):
            raise TypeError(f'{dot}不是Dot类！')
        if dot.ft.effect_rules == 4:
            dot.ready_judge(timetick)
            if dot.dy.ready:
                SpawnDamageEvent(dot, event_list)
                dot.dy.ready = False
                dot.dy.last_effect_ticks = timetick
                dot.dy.effect_times += 1
                dot_list.remove(dot)
                enemy.dynamic.frozen = False
                return True


def DamageEventJudge(timetick: int, load_mission_dict: dict, enemy, event_list: list, char_obj_list: list):
    """
    DamageEvent的Judge函数：轮询load_mission_dict以及enemy.dynamic_dot_list，判断是否应生成Hit事件。
    并且当Hit时间生成时，将对应的实例添加到event_list中。
    当前可能产生Hit的mission类型共有两种，第一种是动作类，第二种是Dot类。
        1-动作类：
            首先应该查询mission.mission_dict，并且查询所有的键值，检查是否有键值需要在本tick处理。
            如果有，则应该将mission.mission_node传递给Schedule Event List。
        2-Dot类：
            首先应明确是固定随时间变化的Dot，还是命中后才产生伤害的Dot。这一条件以Dot.effect_rules来区分。
            如果effect_rules = 1，则表明是仅根据时间和内置CD来产生伤害的，则应该每个Tick都随着本函数执行一次判断；
            如果effect_rules = 2，则表明是根据命中来产生伤害的，则应该和动作类mission一起判断。
    同时，本函数还会在子任务是end的时候检查enemy的积蓄值。如果积蓄值满，则会触发异常（update_anomaly函数）
    """
    # 处理 Load.Mission 任务
    for mission in load_mission_dict.values():
        if not isinstance(mission, LoadingMission | Dot.Dot):
            raise TypeError(f'{mission}不是LoadingMission或是Dot类！')
        for sub_mission_tick in mission.mission_dict:
            if timetick-1 < sub_mission_tick <= timetick and mission.mission_dict[sub_mission_tick] == 'hit':
                SpawnDamageEvent(mission, event_list)
            # 当Mission触发时，检查 effect_rules == 2 的 Dot
                ProcessHitUpdateDots(timetick, enemy.dynamic.dynamic_dot_list, event_list)
            elif timetick-1 < sub_mission_tick <= timetick and mission.mission_dict[sub_mission_tick] == 'end':
                # and mission.mission_node.skill.anomaly_attack
                # 在end处进行属性异常检查。
                # TODO：新增重攻击 判定的接口
                freez_deal = ProcessFreezLikeDots(timetick, enemy, event_list)
                UpdateAnomaly.update_anomaly(mission.mission_node.skill.element_type, enemy, timetick, event_list, char_obj_list, skill_node=mission.mission_node)

    # 始终检查 effect_rules == 1 的 Dot
    ProcessTimeUpdateDots(timetick, enemy.dynamic.dynamic_dot_list, event_list)
    # TODO：预留接口：处理effect_rules == 3 的buff（但是涉及快照）
