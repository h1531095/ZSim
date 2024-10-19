from LinkedList import LinkedList
from Skill_Class import Skill
import Preload
from TickClass import Tick
import pandas as pd
import math


def SkillEventSplit(skills_queue: LinkedList):
    Load_mission_dict = {}
    for skill in skills_queue:
        if not isinstance(skill, Preload.SkillNode):
            raise ValueError(f"本次拆分的{skill}不是SkillNode类！")
        Load_mission_dict[skill.skill_tag] = LoadingMission(skill)
    return Load_mission_dict


def StartJudge(Load_mission_dict: dict, time_now: float):
    for mission in Load_mission_dict:
        if not isinstance(Load_mission_dict[mission], LoadingMission):
            raise TypeError(f'本次检验的{mission}并非LoadingMission类！')
        if Load_mission_dict[mission].mission_already_start:
            continue
            # 如果任务显示为已经被加载过，那么就跳过加载。这样可以避免重复加载。
        if Load_mission_dict[mission].mission_start_tick <= time_now:
            Load_mission_dict[mission].mission_start()
            print(f"当前tick{time_now}，{Load_mission_dict[mission].mission_tag}任务开始了，子任务列表为：{Load_mission_dict[mission].mission_dict}")


def SubMissionLoop(Load_mission_dict: dict, time_now: float):
    for mission in Load_mission_dict:
        if not isinstance(Load_mission_dict[mission], LoadingMission):
            raise TypeError(f"正在加载的{mission}并非LoadingMission类！！")
        if not Load_mission_dict[mission].mission_active_state:
            continue
        for sub_mission_tick in list(Load_mission_dict[mission].mission_dict):
            if sub_mission_tick > time_now:
                continue
            if Load_mission_dict[mission].mission_dict[sub_mission_tick] == 'start':
                del Load_mission_dict[mission].mission_dict[sub_mission_tick]
                print(f'当前tick{time_now}，{mission}任务的子任务序启动！start事件已经被移除，当前子任务列表为：{Load_mission_dict[mission].mission_dict}')
            else:
                if not Load_mission_dict[mission].mission_dict[sub_mission_tick] == 'end':
                    print(f'当前tick{time_now}，{mission}事件的子任务{Load_mission_dict[mission].mission_dict[sub_mission_tick]}已经执行')
                    del Load_mission_dict[mission].mission_dict[sub_mission_tick]
                    print(f'剩余子任务列表为：{Load_mission_dict[mission].mission_dict}')
                    continue
                Load_mission_dict[mission].mission_end()
                print(f'当前tick{time_now}，{mission}事件的全部子任务都已经完成！剩余子任务列表为：{Load_mission_dict[mission].mission_dict}')


class LoadingMission:
    def __init__(self, skill: Preload.SkillNode):
        self.mission_tag = skill.skill_tag
        self.mission_dict = {}
        self.mission_already_start = False
        self.mission_active_state = False
        self.mission_start_tick = skill.preload_tick
        self.skill = skill

    def mission_start(self):
        self.mission_active_state = True
        self.mission_already_start = True
        timecost = self.skill.skill.ticks
        time_step = (timecost - 1)/self.skill.hit_times
        self.mission_dict[float(self.skill.preload_tick)] = "start"
        for i in range(self.skill.hit_times):
            tick_key = float(math.ceil(self.skill.preload_tick + time_step * (i+1)))
            # 由于timetick在循环中的自增量是整数，所以为了保证能和键值准确匹配，
            # 这里的键值也要向上取整，注意，这里产生的是一个int，所以要转化为float
            self.mission_dict[tick_key] = "hit"
        self.mission_dict[self.skill.preload_tick + timecost] = "end"

    def mission_end(self):
        self.mission_active_state = False
        self.mission_dict = {}


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
    load_mission_dict = SkillEventSplit(skill_queue)
    while timenow <= timelimit:
        StartJudge(load_mission_dict, timenow)
        SubMissionLoop(load_mission_dict,  timenow)
        timenow += timestep

