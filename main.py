from dataclasses import dataclass, field

import Buff
import Load
import Preload
import Report
import ScheduledEvent as ScE
from Character import Character, character_factory
from Enemy import Enemy
from Report import write_to_csv
from Update_Buff import update_dynamic_bufflist


@dataclass
class InitData:
    name_box = ['艾莲', '苍角', '莱特']
    Judge_list_set = [['艾莲', '深海访客', '极地重金属'],
                      ['苍角', '含羞恶面', '自由蓝调'],
                      ['莱特', '拘缚者', '镇星迪斯科']]
    char_0 = {'name' : name_box[0],
              'weapon': '深海访客', 'weapon_level': 1,
              'equip_set4': '极地重金属', 'equip_set2_a': '啄木鸟电音',
              'drive4' : '暴击率', 'drive5' : '攻击力%', 'drive6' : '攻击力%',
              'scATK_percent': 10, 'scCRIT': 20}
    char_1 = {'name' : name_box[1],
              'weapon': '含羞恶面', 'weapon_level': 5,
              'equip_set4': '摇摆爵士', 'equip_set2_a': '自由蓝调',
              'drive4' : '暴击率', 'drive5' : '攻击力%', 'drive6' : '能量自动回复%',
              'scATK_percent': 10, 'scCRIT': 20}
    char_2 = {'name' : name_box[2],
              'weapon': '拘缚者', 'weapon_level': 1,
              'equip_set4': '震星迪斯科', 'equip_set2_a': '摇摆爵士',
              'drive4' : '暴击率', 'drive5' : '攻击力%', 'drive6' : '冲击力%',
              'scATK_percent': 10, 'scCRIT': 20}
    weapon_dict = {name_box[0]: [char_0['weapon'], char_0['weapon_level']],
                   name_box[1]: [char_1['weapon'], char_1['weapon_level']],
                   name_box[2]: [char_2['weapon'], char_2['weapon_level']]}

@dataclass
class CharacterData:
    char_obj_list: list[Character] = field(init=False)
    InitData: InitData

    def __post_init__(self):
        self.char_obj_list = []
        if self.InitData.name_box:
            i = 0
            for _ in self.InitData.name_box:
                char_dict = getattr(InitData, f'char_{i}')
                char_obj: Character = character_factory(**char_dict)
                self.char_obj_list.append(char_obj)
                i += 1

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

tick = 0

init_data = InitData()
char_data = CharacterData(init_data)
load_data = LoadData(
        name_box=init_data.name_box,
        Judge_list_set=init_data.Judge_list_set,
        weapon_dict=init_data.weapon_dict)
schedule_data = ScheduleData(enemy=Enemy(), char_obj_list=char_data.char_obj_list)
global_stats = GlobalStats(name_box=init_data.name_box)

def main_loop(stop_tick: int | None = None):
    tick = 0
    while True:
        # Tick Update
        update_dynamic_bufflist(global_stats.DYNAMIC_BUFF_DICT, tick, load_data.exist_buff_dict, schedule_data.enemy)

        # Preload
        preload.do_preload(tick, schedule_data.enemy, init_data.name_box, char_data)
        preload_list = preload.preload_data.preloaded_action

        if stop_tick is None:
            if len(preload.preload_data.skills_queue) == 0:
                stop_tick = tick + 120
        elif tick >= stop_tick:
            break

        # Load
        if preload_list:
            Load.SkillEventSplit(preload_list, load_data.load_mission_dict, load_data.name_dict, tick)
        Buff.BuffLoadLoop(tick, load_data.load_mission_dict, load_data.exist_buff_dict, load_data.name_box, load_data.LOADING_BUFF_DICT)
        Buff.buff_add(tick, load_data.LOADING_BUFF_DICT, global_stats.DYNAMIC_BUFF_DICT, schedule_data.enemy)
        Load.DamageEventJudge(tick, load_data.load_mission_dict, schedule_data.enemy, schedule_data.event_list, global_stats.DYNAMIC_BUFF_DICT, load_data.exist_buff_dict)

        # ScheduledEvent
        scheduled = ScE.ScheduledEvent(global_stats.DYNAMIC_BUFF_DICT, schedule_data, tick)
        scheduled.event_start()

        tick += 1
        print(f"\r{tick}", end='')




if __name__ == '__main__':
    # global data


    # Initialize Preload Data
    skills = (char.skill_object for char in char_data.char_obj_list)
    preload = Preload.Preload(*skills)


    main_loop()
    write_to_csv()

    Report.log_queue.join()
    Report.result_queue.join()
