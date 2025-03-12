import gc
from simulator.dataclasses import InitData, CharacterData, LoadData, ScheduleData, GlobalStats
from define import APL_MODE
from sim_progress import Load, Preload, Buff, ScheduledEvent as ScE, Enemy, update_dynamic_bufflist
from sim_progress.data_struct import ActionStack
from sim_progress.Preload import PreloadClass

tick = 0
crit_seed = 0
init_data = InitData()
char_data = CharacterData(init_data)
load_data = LoadData(
        name_box=init_data.name_box,
        Judge_list_set=init_data.Judge_list_set,
        weapon_dict=init_data.weapon_dict,
        cinema_dict=init_data.cinema_dict,
        action_stack=ActionStack())
schedule_data = ScheduleData(enemy=Enemy(enemy_index_ID=11752), char_obj_list=char_data.char_obj_list)
global_stats = GlobalStats(name_box=init_data.name_box)
skills = [char.skill_object for char in char_data.char_obj_list]
# preload = Preload.Preload(*skills)
preload = PreloadClass(skills)
game_state = {
    "tick": tick,
    "init_data": init_data,
    "char_data": char_data,
    "load_data": load_data,
    "schedule_data": schedule_data,
    "global_stats": global_stats,
    "preload": preload
}


def main_loop(stop_tick: int | None = 6000):
    global tick
    tick = 0
    while True:
        # Tick Update
        # report_to_log(f"[Update] Tick step to {tick}")
        update_dynamic_bufflist(global_stats.DYNAMIC_BUFF_DICT, tick, load_data.exist_buff_dict, schedule_data.enemy)

        # Preload
        preload.do_preload(tick, schedule_data.enemy, init_data.name_box, char_data)
        # preload_list = preload.preload_data.preloaded_action
        preload_list = preload.preload_data.preload_action

        if stop_tick is None:
            if not APL_MODE and preload.preload_data.skills_queue.head is None:
                stop_tick = tick + 120
        elif tick >= stop_tick:
            break

        # Load
        if preload_list:
            Load.SkillEventSplit(preload_list, load_data.load_mission_dict, load_data.name_dict, tick, load_data.action_stack)
        Buff.BuffLoadLoop(tick, load_data.load_mission_dict, load_data.exist_buff_dict, init_data.name_box, load_data.LOADING_BUFF_DICT, load_data.all_name_order_box)
        Buff.buff_add(tick, load_data.LOADING_BUFF_DICT, global_stats.DYNAMIC_BUFF_DICT, schedule_data.enemy)
        Load.DamageEventJudge(tick, load_data.load_mission_dict, schedule_data.enemy, schedule_data.event_list, char_data.char_obj_list)
        # ScheduledEvent
        scheduled = ScE.ScheduledEvent(global_stats.DYNAMIC_BUFF_DICT, schedule_data, tick, load_data.exist_buff_dict, load_data.action_stack)
        scheduled.event_start()
        tick += 1
        print(f"\r{tick} ", end='')

        if tick % 100 == 0 and tick != 0:
            gc.collect()