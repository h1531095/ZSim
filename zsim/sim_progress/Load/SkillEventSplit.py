import tqdm
from sim_progress.Report import report_to_log
from sim_progress import Load, Preload
from sim_progress.data_struct import ActionStack


def SkillEventSplit(
    preloaded_action_list: list,
    Load_mission_dict: dict,
    name_dict: dict,
    timenow,
    action_stack: ActionStack,
):
    to_remove = []
    for mission in Load_mission_dict.values():
        if not isinstance(mission, Load.LoadingMission):
            raise TypeError(f"{mission}并非LoadingMission类！")
        mission.check_myself(timenow)
    for i in range(len(preloaded_action_list)):
        skill = preloaded_action_list.pop()
        if not isinstance(skill, Preload.SkillNode):
            raise ValueError(f"本次拆分的{type(skill)}不是SkillNode类！")
        this_mission = Load.LoadingMission(skill)
        this_mission.mission_start(timenow)
        action_stack.push(this_mission)
        if skill.skill_tag in name_dict:
            name_dict[skill.skill_tag] += 1
        else:
            name_dict[skill.skill_tag] = 1
        key = skill.skill_tag + f"[{name_dict[skill.skill_tag]}]"
        Load_mission_dict[key] = this_mission
        for key, mission in Load_mission_dict.items():
            if not isinstance(mission, Load.LoadingMission):
                raise TypeError(f"{mission}并非LoadingMission类！")
            if not mission.mission_active_state:
                if key not in to_remove:
                    to_remove.append(key)
    for key in to_remove:
        report_to_log(
            f"[Skill LOAD]:{timenow}:{Load_mission_dict[key].mission_tag}已经结束,已从Load中移除",
            level=2,
        )
        Load_mission_dict.pop(key)
    return Load_mission_dict


if __name__ == "__main__":  # 测试
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

# TODO: 将SkillEventSplit中，对于load_mission_dict的维护部分单独拆分，并且每个ticks查询，如果当前有hit子任务，则直接向schedule_event_list添加对应的SkillNode
