import gc

from define import APL_MODE, ENEMY_ADJUST_ID, ENEMY_DIFFICULTY, ENEMY_INDEX_ID
from sim_progress import Buff, Load, update_dynamic_bufflist
from sim_progress import ScheduledEvent as ScE
from sim_progress.Character.skill_class import Skill
from sim_progress.data_struct import ActionStack
from sim_progress.Enemy import Enemy
from sim_progress.Preload import PreloadClass
from sim_progress.Report import start_report_threads
from simulator.dataclasses import (
    CharacterData,
    GlobalStats,
    InitData,
    LoadData,
    ScheduleData,
)

tick = 0
crit_seed = 0
init_data: InitData | None = None
char_data: CharacterData | None = None
load_data: LoadData | None = None
schedule_data: ScheduleData | None = None
global_stats: GlobalStats | None = None
skills: list[Skill] | None = None
preload: PreloadClass | None = None
game_state: dict[str, object] | None = None


def check_state_reset():
    """在main_loop开头调用"""
    current_fingerprint = init_data._init_fingerprint if init_data else None
    # 如果是第一次运行，记录指纹
    if not hasattr(check_state_reset, "last_fingerprint"):
        check_state_reset.last_fingerprint = current_fingerprint
        return

    # 后续运行时检查指纹是否变化
    if current_fingerprint == check_state_reset.last_fingerprint:
        raise RuntimeError("状态重置失败！检测到相同的初始化指纹")

    # 更新最新指纹
    check_state_reset.last_fingerprint = current_fingerprint


def reset_sim_data():
    """重置所有全局变量为初始状态。"""
    global \
        tick, \
        crit_seed, \
        init_data, \
        char_data, \
        load_data, \
        schedule_data, \
        global_stats, \
        skills, \
        preload, \
        game_state
    del (
        init_data,
        char_data,
        load_data,
        schedule_data,
        global_stats,
        skills,
        preload,
        game_state,
    )
    gc.collect()  # 强制回收

    tick = 0
    crit_seed = 0
    init_data = InitData()

    char_data = CharacterData(init_data)
    load_data = LoadData(
        name_box=init_data.name_box,
        Judge_list_set=init_data.Judge_list_set,
        weapon_dict=init_data.weapon_dict,
        cinema_dict=init_data.cinema_dict,
        action_stack=ActionStack(),
    )
    schedule_data = ScheduleData(
        enemy=Enemy(
            index_ID=ENEMY_INDEX_ID,
            adjust_ID=ENEMY_ADJUST_ID,
            difficulty=ENEMY_DIFFICULTY,
        ),
        char_obj_list=char_data.char_obj_list,
    )

    global_stats = GlobalStats(name_box=init_data.name_box)
    skills = [char.skill_object for char in char_data.char_obj_list]
    preload = PreloadClass(skills, load_data=load_data)

    game_state = {  # noqa: F841
        "tick": tick,
        "init_data": init_data,
        "char_data": char_data,
        "load_data": load_data,
        "schedule_data": schedule_data,
        "global_stats": global_stats,
        "preload": preload,
    }


def reset_simulator():
    """重置程序为初始状态。"""
    reset_sim_data()  # 重置所有全局变量
    start_report_threads()  # 启动线程以处理日志和结果写入


def main_loop(stop_tick: int | None = 10800):
    reset_simulator()
    check_state_reset()
    global \
        tick, \
        crit_seed, \
        init_data, \
        char_data, \
        load_data, \
        schedule_data, \
        global_stats, \
        preload
    while True:
        # Tick Update
        # report_to_log(f"[Update] Tick step to {tick}")
        update_dynamic_bufflist(
            global_stats.DYNAMIC_BUFF_DICT,
            tick,
            load_data.exist_buff_dict,
            schedule_data.enemy,
        )  # type: ignore

        # Preload
        preload.do_preload(tick, schedule_data.enemy, init_data.name_box, char_data)  # type: ignore
        preload_list = preload.preload_data.preload_action  # type: ignore

        if stop_tick is None:
            if not APL_MODE and preload.preload_data.skills_queue.head is None:  # type: ignore
                stop_tick = tick + 120
        elif tick >= stop_tick:
            break

        # Load
        if preload_list:
            Load.SkillEventSplit(
                preload_list,
                load_data.load_mission_dict,
                load_data.name_dict,
                tick,
                load_data.action_stack,
            )  # type: ignore
        Load.DamageEventJudge(
            tick,
            load_data.load_mission_dict,
            schedule_data.enemy,
            schedule_data.event_list,
            char_data.char_obj_list,
            dynamic_buff_dict=global_stats.DYNAMIC_BUFF_DICT,
        )  # type: ignore
        Buff.BuffLoadLoop(
            tick,
            load_data.load_mission_dict,
            load_data.exist_buff_dict,
            init_data.name_box,
            load_data.LOADING_BUFF_DICT,
            load_data.all_name_order_box,
        )  # type: ignore
        Buff.buff_add(
            tick,
            load_data.LOADING_BUFF_DICT,
            global_stats.DYNAMIC_BUFF_DICT,
            schedule_data.enemy,
        )  # type: ignore
        # Load.DamageEventJudge(tick, load_data.load_mission_dict, schedule_data.enemy, schedule_data.event_list, char_data.char_obj_list)
        # ScheduledEvent
        scheduled = ScE.ScheduledEvent(
            global_stats.DYNAMIC_BUFF_DICT,
            schedule_data,
            tick,
            load_data.exist_buff_dict,
            load_data.action_stack,
        )  # type: ignore
        scheduled.event_start()
        tick += 1
        print(f"\r{tick} ", end="")

        if tick % 100 == 0 and tick != 0:
            gc.collect()