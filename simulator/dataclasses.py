from calendar import day_name
from dataclasses import dataclass, field
from define import APL_MODE, saved_char_config
from sim_progress import Load, Preload, Buff, ScheduledEvent as ScE, Report
from sim_progress.Character import Character, character_factory
from sim_progress.Enemy import Enemy
from sim_progress.data_struct import ActionStack
import time


@dataclass
class InitData:
    def __init__(self):
        """
        初始化角色配置数据。
        
        从配置文件中加载角色配置信息，并初始化相关数据结构。
        如果配置文件不存在或配置信息不完整，将抛出异常。
        """
        self._init_fingerprint = time.time()
        config: dict = saved_char_config
        if not config:
            assert False, "No character init configuration found."
        try:
            self.name_box: list[str] = config['name_box']
            self.Judge_list_set: list[list[str]] = []    # [[角色名, 武器名, 四件套, 二件套], ...]
            self.char_0 = config[self.name_box[0]]
            self.char_1 = config[self.name_box[1]]
            self.char_2 = config[self.name_box[2]]
        except KeyError as e:
            assert False, f"Missing key in character init configuration: {e}"
        
        for name in self.name_box:
            char = getattr(self, f'char_{self.name_box.index(name)}')
            self.Judge_list_set.append([
                name,
                char['weapon'],
                char.get('equip_set4', ''),
                char.get('equip_set2_a', '')
            ])
        
        self.weapon_dict: dict[str: list[str, int]] = {
            name: [getattr(self, f'char_{self.name_box.index(name)}')['weapon'], 
                   getattr(self, f'char_{self.name_box.index(name)}')['weapon_level']]
            for name in self.name_box
        }   # {角色名: [武器名, 武器精炼等级], ...}
        
        self.cinema_dict = {
            name: getattr(self, f'char_{self.name_box.index(name)}')['cinema']
            for name in self.name_box
        }   # {角色名: 影画等级, ...}
        pass



@dataclass
class CharacterData:
    char_obj_list: list[Character] = field(init=False)
    init_data: InitData

    def __post_init__(self):
        self.char_obj_list = []
        if self.init_data.name_box:
            i = 0
            for _ in self.init_data.name_box:
                char_dict = getattr(self.init_data, f'char_{i}')
                char_obj: Character = character_factory(**char_dict)
                self.char_obj_list.append(char_obj)
                i += 1

    def reset_myself(self):
        for obj in self.char_obj_list:
            obj.reset_myself()


@dataclass
class LoadData:
    name_box: list
    Judge_list_set: list
    weapon_dict: dict
    action_stack: ActionStack
    cinema_dict: dict
    exist_buff_dict: dict = field(init=False)
    load_mission_dict: dict = field(default_factory=dict)
    LOADING_BUFF_DICT: dict = field(default_factory=dict)
    name_dict: dict = field(default_factory=dict)
    all_name_order_box: dict = field(default_factory=dict)
    preload_tick_stamp: dict = field(default_factory=dict)

    def __post_init__(self):
        self.exist_buff_dict = Buff.buff_exist_judge(self.name_box, self.Judge_list_set, self.weapon_dict, self.cinema_dict)
        self.all_name_order_box = Buff.change_name_box(self.name_box)

    def reset_exist_buff_dict(self):
        """重置buff_exist_dict"""
        for char_name, sub_exist_buff_dict in self.exist_buff_dict.items():
            for buff_name, buff in sub_exist_buff_dict.items():
                buff.reset_myself()

    def reset_myself(self, name_box, Judge_list_set, weapon_dict, cinema_dict):
        self.name_box = name_box
        self.Judge_list_set = Judge_list_set
        self.weapon_dict = weapon_dict
        self.cinema_dict = cinema_dict
        self.action_stack.reset_myself()
        self.reset_exist_buff_dict()
        self.load_mission_dict = {}
        self. LOADING_BUFF_DICT = {}
        self.name_dict = {}
        self.all_name_order_box = Buff.change_name_box(self.name_box)
        self.preload_tick_stamp = {}


@dataclass
class ScheduleData:
    enemy: Enemy
    char_obj_list: list[Character]
    event_list: list = field(default_factory=list)
    judge_required_info_dict = {'skill_node': None}
    loading_buff: dict[str, list[Buff.Buff]] = field(default_factory=dict)
    dynamic_buff: dict[str, list[Buff.Buff]] = field(default_factory=dict)

    def reset_myself(self):
        """重置ScheduleData的动态数据！"""
        self.enemy.reset_myself()
        self.event_list = []
        self.judge_required_info_dict = {'skill_node': None}
        for char_name in self.loading_buff:
            self.loading_buff[char_name] = []
            self.dynamic_buff[char_name] = []


@dataclass
class GlobalStats:
    name_box: list
    DYNAMIC_BUFF_DICT: dict[str, list[Buff.Buff]] = field(default_factory=dict)
    
    def __post_init__(self):
        for name in self.name_box + ['enemy']:
            self.DYNAMIC_BUFF_DICT[name] = []

    def reset_myself(self, name_box):
        for name in self.name_box + ['enemy']:
            self.DYNAMIC_BUFF_DICT[name] = []