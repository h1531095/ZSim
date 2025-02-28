from sim_progress.Preload import SkillNode
from sim_progress.Report import report_to_log


class LoadingMission:
    def __init__(self, mission: SkillNode):
        self.mission_active_state = False
        self.mission_node = mission
        self.mission_dict = {}
        self.mission_start_tick = mission.preload_tick
        self.hitted_count = 0  # 已经结算的hit数量
        self.mission_tag = mission.skill_tag
        self.mission_end_tick = mission.end_tick
        self.mission_character = mission.char_name

    def mission_start(self, timenow):
        self.mission_active_state = True
        timecost = self.mission_node.skill.ticks
        time_step = (timecost - 1)/(self.mission_node.hit_times + 1)
        self.mission_dict[float(self.mission_node.preload_tick)] = "start"
        # if self.mission_node.hit_times == 1:
        #     self.mission_dict[float(self.mission_node.preload_tick+timecost - 1)/2] = "hit"
        # else:
        for i in range(self.mission_node.hit_times):
            tick_key = self.mission_node.preload_tick + time_step * (i + 1)
            # 由于timetick在循环中的自增量是整数，所以为了保证能和键值准确匹配，
            # 这里的键值也要向上取整，注意，这里产生的是一个int，所以要转化为float
            self.mission_dict[tick_key] = "hit"
        self.mission_dict[float(self.mission_node.preload_tick + timecost)] = "end"
        report_to_log(f"[Skill LOAD]:{timenow}:{self.mission_tag}开始并拆分子任务。", level=4)

    def mission_end(self):
        self.mission_active_state = False
        self.hitted_count = 0
        self.mission_dict = {}

    def check_myself(self, timenow):
        if self.mission_end_tick < timenow:
            self.mission_end()
