from LinkedList import LinkedList
from Skill_Class import Skill
import Preload
from TickClass import Tick
import pandas as pd
import tqdm
from define import CHARACTER_DATA_PATH
character_config_data = pd.read_csv(CHARACTER_DATA_PATH)


def SkillEventSplit(preloaded_action_list: LinkedList, Load_mission_dict: dict, name_dict: dict, timenow):
    to_remove = []
    for mission in Load_mission_dict.values():
        if not isinstance(mission, LoadingMission):
            raise TypeError(f'{mission}并非LoadingMission类！')
        mission.check_myself(timenow)
    for i in range(len(preloaded_action_list)):
        skill = preloaded_action_list.pop_head()
        if not isinstance(skill, Preload.SkillNode):
            raise ValueError(f"本次拆分的{skill}不是SkillNode类！")
        this_mission = LoadingMission(skill)
        this_mission.mission_start()
        if skill.skill_tag in name_dict:
            name_dict[skill.skill_tag] += 1
        else:
            name_dict[skill.skill_tag] = 1
        key = skill.skill_tag + f'[{name_dict[skill.skill_tag]}]'
        Load_mission_dict[key] = this_mission
        for key, mission in Load_mission_dict.items():
            if not isinstance(mission, LoadingMission):
                raise TypeError(f'{mission}并非LoadingMission类！')
            if not mission.mission_active_state:
                to_remove.append(key)
        for key in to_remove:
            print(f'{timenow}，{Load_mission_dict[key].mission_tag}已经结束，从Load_mission_dict中移除')
            Load_mission_dict.pop(key)
    return Load_mission_dict


class LoadingMission:
    def __init__(self, skill: Preload.SkillNode):
        self.mission_tag = skill.skill_tag
        self.mission_dict = {}
        self.mission_already_start = False
        self.mission_active_state = False
        self.mission_start_tick = skill.preload_tick
        self.mission_end_tick = skill.preload_tick + skill.skill.ticks
        self.skill_node = skill
        CID = int(skill.skill.skill_tag[:4])
        self.mission_character = str(character_config_data.loc[character_config_data['CID'] == CID, 'name'].values[0])

    def mission_start(self):
        self.mission_active_state = True
        self.mission_already_start = True
        timecost = self.skill_node.skill.ticks
        time_step = (timecost - 1)/self.skill_node.hit_times
        self.mission_dict[float(self.skill_node.preload_tick+1)] = "start"
        for i in range(self.skill_node.hit_times):
            tick_key = self.skill_node.preload_tick + time_step * (i+1)
            # 由于timetick在循环中的自增量是整数，所以为了保证能和键值准确匹配，
            # 这里的键值也要向上取整，注意，这里产生的是一个int，所以要转化为float
            self.mission_dict[tick_key] = "hit"
        self.mission_dict[float(self.skill_node.preload_tick + timecost)] = "end"

    def mission_end(self):
        self.mission_active_state = False
        self.mission_dict = {}

    def check_myself(self, timenow):
        if self.mission_active_state < timenow:
            self.mission_end()


if __name__ == "__main__":      # 测试
    timelimit = 3600
    load_mission_dict = {}
    p = Preload.Preload()
    name_dict = {}
    for tick in tqdm.trange(timelimit):
        p.do_preload(tick)
        preload_action_list = p.preload_data.preloaded_action
        if not preload_action_list:
            continue
        SkillEventSplit(preload_action_list, load_mission_dict, name_dict)
    for item in load_mission_dict:
        print(f"{item}, {load_mission_dict[item].mission_character_number}")

