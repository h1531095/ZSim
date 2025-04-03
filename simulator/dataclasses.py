from dataclasses import dataclass, field
from define import APL_MODE
from sim_progress import Load, Preload, Buff, ScheduledEvent as ScE, Report
from sim_progress.Character import Character, character_factory
from sim_progress.Enemy import Enemy
from sim_progress.data_struct import ActionStack


@dataclass
class InitData:
    name_box = ['扳机', '丽娜', '零号·安比']
    Judge_list_set = [[name_box[0], '索魂影眸', '震星迪斯科','啄木鸟电音'],
                      [name_box[1], '深海访客', '静听嘉音', '摇摆爵士'],
                      [name_box[2], '牺牲洁纯', '如影相随', '啄木鸟电音']]
    char_0 = {'name': name_box[0],
              'weapon': Judge_list_set[0][1], 'weapon_level': 1,
              'equip_set4': Judge_list_set[0][2], 'equip_set2_a': Judge_list_set[0][3],
              'drive4': '暴击率', 'drive5': '电属性伤害', 'drive6': '冲击力%',
              'scCRIT': 35,
              'cinema': 0}
    char_1 = {'name': name_box[1],
              'weapon': Judge_list_set[1][1], 'weapon_level': 5,
              'equip_set4': Judge_list_set[1][2], 'equip_set2_a': Judge_list_set[1][3],
              'drive4': '暴击率%', 'drive5': '穿透率', 'drive6': '能量自动回复%',
              'scATK_percent': 10, 'scCRIT': 20,
              'cinema': 2}
    char_2 = {'name': name_box[2],
              'weapon': Judge_list_set[2][1], 'weapon_level': 1,
              'equip_set4': Judge_list_set[2][2], 'equip_set2_a': Judge_list_set[2][3],
              'drive4': '暴击率', 'drive5': '电属性伤害', 'drive6': '攻击力%',
              'scATK_percent': 8, 'scCRIT': 10, 'scATK': 2, 'scPEN': 5, 'scCRIT_DMG': 15,
              'cinema': 0,
              'crit_balancing': False}
    weapon_dict = {name_box[0]: [char_0['weapon'], char_0['weapon_level']],
                   name_box[1]: [char_1['weapon'], char_1['weapon_level']],
                   name_box[2]: [char_2['weapon'], char_2['weapon_level']]}
    cinema_dict = {name_box[0]: char_0['cinema'],
                   name_box[1]: char_1['cinema'],
                   name_box[2]: char_2['cinema']}


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


@dataclass
class ScheduleData:
    enemy: Enemy
    char_obj_list: list[Character]
    event_list: list = field(default_factory=list)
    judge_required_info_dict = {'skill_node': None}
    loading_buff: dict[str, list[Buff.Buff]] = field(default_factory=dict)
    dynamic_buff: dict[str, list[Buff.Buff]] = field(default_factory=dict)


@dataclass
class GlobalStats:
    name_box: list
    DYNAMIC_BUFF_DICT: dict[str, list[Buff.Buff]] = field(default_factory=dict)
    
    def __post_init__(self):
        for name in self.name_box + ['enemy']:
            self.DYNAMIC_BUFF_DICT[name] = []