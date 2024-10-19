from LinkedList import LinkedList
from Skill_Class import Skill
import Preload
from TickClass import Tick
import pandas as pd


def SkillEventSplit(skills_queue: LinkedList, timenow: float):
    dynamic_loading_dict = {}
    for skill in skills_queue:
        if not isinstance(skill, Preload.SkillNode):
            raise ValueError(f"本次拆分的{skill}不是SkillNode类！")
        if skill.preload_tick <= timenow:
            loadmission = LoadingMission(skill)
            loadmission.mission_start(skill)
            dynamic_loading_dict[skill.skill_tag] = loadmission
            print(f"已经对{skill.skill_tag}进行加载，执行列表为{dynamic_loading_dict[skill.skill_tag].mission_dict}")
    return dynamic_loading_dict


class LoadingMission:
    def __init__(self, skill: Preload.SkillNode):
        self.mission_tag = skill.skill_tag
        self.mission_dict = {}
        self.mission_active_state = False
        self.mission_start_tick = skill.preload_tick

    def mission_start(self, skill: Preload.SkillNode):
        self.mission_active_state = True
        timecost = skill.skill.ticks
        timestep = (timecost - 1)/skill.hit_times
        self.mission_dict[skill.preload_tick] = "start"
        for i in range(skill.hit_times):
            tick_key = skill.preload_tick + timestep * (i+1)
            self.mission_dict[tick_key] = "hit"
        self.mission_dict[skill.preload_tick + timecost] = "end"

    def mission_end(self, dynamic_mission_dict: dict):
        self.mission_active_state = False
        self.mission_dict = {}
        dynamic_mission_dict.pop(self.mission_tag)

    def sub_mission_completed(self, ticks: float):
        if ticks not in self.mission_dict:
            raise ValueError(f"{ticks}并不是当前子任务的时间节点！")
        print(f"完成子任务{self.mission_dict[ticks]}，当前子任务属于{self.mission_tag}")
        self.mission_dict.pop(ticks)

    def sub_mission_check(self, ticknow: float):
        for items in self.mission_dict[:]:
            if items <= ticknow:
                self.sub_mission_completed(ticknow)






if __name__ == "__main__":      # 测试
    timestart = 0
    timestep = 1
    timelimit = 300
    timenow = timestart
    test = {
        'skill_tag': ['1221_NA_1', '1221_NA_2', '1221_NA_3', '1221_NA_4', '1221_NA_5']
    }
    test_skill_dataframe = pd.DataFrame(test)
    test_object = Skill(CID=1221)
    skill_queue = Preload.SkillsQueue.get_skills_queue(test_skill_dataframe, test_object)
    while timenow < timelimit:
        Dynamic_loading_dict = SkillEventSplit(skill_queue, timenow)
        timenow += timestep
    for item in Dynamic_loading_dict[:]:
        print(f"当前tick是{Dynamic_loading_dict[item].mission_start_tick}，当前任务dict属于{item}，具体执行列表为：{Dynamic_loading_dict[item].mission_dict}")

