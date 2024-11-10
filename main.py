from dataclasses import dataclass, field

import tqdm

import Buff
import Load
import Preload
import Report
import ScheduledEvent as ScE
from CharSet_new import Character
from Enemy import Enemy
from Report import write_to_csv
from Update_Buff import update_dynamic_bufflist


@dataclass
class InitData:
    name_box = ['艾莲', '苍角', '莱卡恩']
    Judge_list_set = [['艾莲', '深海访客', '极地重金属'],
                      ['苍角', '含羞恶面', '自由蓝调'],
                      ['莱卡恩', '拘缚者', '镇星迪斯科']]
    weapon_dict = {'艾莲': ['深海访客', 1],
                   '苍角': ['含羞恶面', 5],
                   '莱卡恩': ['拘缚者', 1]}

@dataclass
class CharacterData:
    char_obj_list: list[Character] = field(init=False)
    name_box: list

    def __post_init__(self):
        self.char_obj_list = []
        if self.name_box:
            for name in self.name_box:
                char_obj = Character(name=name)
                self.char_obj_list.append(char_obj)

@dataclass
class LoadData:
    name_box: list
    Judge_list_set: list
    weapon_dict: dict
    exist_buff_dict: dict = field(init=False)
    load_mission_dict = {}
    LOADING_BUFF_DICT = {}
    name_dict = {}

    def __post_init__(self):
        self.exist_buff_dict = Buff.buff_exist_judge(self.name_box, self.Judge_list_set, self.weapon_dict)

@dataclass
class ScheduleData:
    event_list = []
    loading_buff = {}
    dynamic_buff = {}
    enemy: Enemy
    char_obj_list: list[Character]


@dataclass
class GlobalStats:
    DYNAMIC_BUFF_DICT = {}
    name_box: list
    def __post_init__(self):
        for name in self.name_box + ['enemy']:
            self.DYNAMIC_BUFF_DICT[name] = []

def main_loop(tick: int):
    # Tick Update
    update_dynamic_bufflist(global_stats.DYNAMIC_BUFF_DICT, tick, load_data.exist_buff_dict, schedule_data.enemy)

    # Preload
    preload.do_preload(tick, schedule_data.enemy)
    preload_list = preload.preload_data.preloaded_action

    # Load
    if preload_list:
        Load.SkillEventSplit(preload_list, load_data.load_mission_dict, load_data.name_dict, tick)
    Buff.BuffLoadLoop(tick, load_data.load_mission_dict, load_data.exist_buff_dict, load_data.name_box, load_data.LOADING_BUFF_DICT)
    Buff.buff_add(tick, load_data.LOADING_BUFF_DICT, global_stats.DYNAMIC_BUFF_DICT, schedule_data.enemy)
    Load.DamageEventJudge(tick, load_data.load_mission_dict, schedule_data.enemy, schedule_data.event_list)

    # ScheduledEvent
    scheduled = ScE.ScheduledEvent(global_stats.DYNAMIC_BUFF_DICT, schedule_data, tick)
    scheduled.event_start()

    # Write Buffer Data

if __name__ == '__main__':
    # global data
    init_data = InitData()
    char_data = CharacterData(name_box=init_data.name_box)
    load_data = LoadData(
            name_box=init_data.name_box,
            Judge_list_set=init_data.Judge_list_set,
            weapon_dict=init_data.weapon_dict)
    schedule_data = ScheduleData(enemy = Enemy(), char_obj_list=char_data.char_obj_list)
    global_stats = GlobalStats(name_box=init_data.name_box)

    # Initialize Preload Data
    skills = (char.skill_object for char in char_data.char_obj_list)
    preload = Preload.Preload(*skills)

    # Get max time, and in case, add it by 60
    MAX_TICK = preload.preload_data.max_tick + 60

    for tick in tqdm.trange(MAX_TICK):
        main_loop(tick)
    write_to_csv()

    Report.log_queue.join()
    Report.result_queue.join()
