from sim_progress import Preload, Buff, Report
from sim_progress.AnomalyBar import AnomalyBar as AnB
from sim_progress.AnomalyBar import Disorder
from sim_progress.Buff import ScheduleBuffSettle
from sim_progress.Character import Character
from sim_progress.data_struct import SingleHit, SPUpdateData, ActionStack, ScheduleRefreshData
from sim_progress.Load.loading_mission import LoadingMission
from .CalAnomaly import CalAnomaly, CalDisorder
from .Calculator import Calculator, MultiplierData


class ScConditionData:
    """
    用于记录在本tick可能的判断 buff 数据，以方便后续计算伤害
    """
    def __init__(self):
        self.buff_list: list = []
        self.when_crit: bool = False


class ScheduledEvent:
    """
    计划事件方法类

    主逻辑链 self.event_start()：
    1、读取计划事件列表，将其中所有的buff示例排到列表最靠前的位置。self.sort_events()
    2、遍历事件列表，从开始到结束，将每一个事件派发到分支逻辑链内进行处理
    """

    def __init__(
        self, 
        dynamic_buff: dict, 
        data, 
        tick: int, 
        exist_buff_dict: dict, 
        action_stack: ActionStack, 
        *, 
        loading_buff: dict | None = None, 
        judging_buff: dict | None = None
        ):

        self.data = data    # ScheduleData in __main__
        self.data.dynamic_buff = dynamic_buff
        self.judge_required_info_dict = data.judge_required_info_dict
        self.action_stack = action_stack
        if isinstance(judging_buff, dict):
            judge_condition = ScConditionData()

        if loading_buff is None:
            loading_buff = {}
        elif not isinstance(loading_buff, dict):
            raise ValueError(f'loading_buff参数必须为字典，但你输入了{loading_buff}')

        if not isinstance(tick, int):
            raise ValueError(f'tick参数必须为整数，但你输入了{tick}')

        # 更新Data
        self.tick = tick
        self.data.loading_buff = loading_buff
        self.exist_buff_dict = exist_buff_dict
        self.enemy = self.data.enemy

    def event_start(self):
        """Schedule主逻辑"""
        # 更新角色面板
        for char in self.data.char_obj_list:
            char: Character
            sp_update_date = SPUpdateData(char_obj=char, dynamic_buff=self.data.dynamic_buff)
            char.update_sp_and_decibel(sp_update_date)
        # 判断循环
        if self.data.event_list:
            self.solve_buff()  # 先处理优先级高的buff

            # 其余事件挨个处理
            for _ in range(len(self.data.event_list)):
                event = self.data.event_list.pop(0)
                # 添加buff
                if isinstance(event, Buff.Buff):
                    raise NotImplementedError(f"{type(event)}，目前不应存在于 event_list")
                elif isinstance(event, Preload.SkillNode | LoadingMission):
                    if event.preload_tick <= self.tick:
                        self.skill_event(event)
                        self.judge_required_info_dict['skill_node'] = event
                elif isinstance(event, Disorder):
                    self.disorder_event(event)
                    self.judge_required_info_dict['disorder'] = event
                elif isinstance(event, AnB):
                    self.anomaly_event(event)
                    self.judge_required_info_dict['anb'] = event
                elif isinstance(event, ScheduleRefreshData):
                    self.refresh_event(event)
                    self.judge_required_info_dict['refresh'] = event
                else:
                    raise NotImplementedError(f"{type(event)}，目前不应存在于 event_list")
                ScheduleBuffSettle(self.tick, self.exist_buff_dict, self.enemy, self.data.dynamic_buff, self.action_stack)

            # 计算过程中如果又有新的事件生成，则继续循环
            if self.data.event_list:
                self.event_start()

        # FIXME: ScheduleBuffSettle函数如果内置在eventstart内，似乎会引发如下问题：
        """
        如果当前的tick的eventlist内的事件个数>1，就会导致ScheduleBuffSettle函数被多次执行。
        比如，在霜灼破触发的tick，eventlist中就可能会出现两个skill_node。然后导致该函数被执行两次。
        亦或是属性异常、紊乱等情况，也会导致该函数重复执行。
        
        几乎所有在Schedule阶段处理的Buff，都拥有复杂逻辑special_judge函数，而该函数的判定依据大概率来自于skill_node、部分main中变量等元素
        所以在某个tick，如果该buff能够通过判定，那么无论在这个tick判定多少次，大概率都是能够通过的。反之亦然。
        每次判定通过，都会导致buff的special_effect被运行一次，其中或许就包括了buff的叠层、或者是重启逻辑，最后导致buff的层数或是其他属性异常。
        
        在以往的测试中，ScheduleBuffSettle大概率不会用到，因为以前只有啄木鸟电音的套装效果需要Schedule来判断。
        只要不佩戴这个套装，那么该函数就是完全空跑。所以这个问题一直没观察到。
        
        本“Bug”是在今晚我给啜泣摇篮的自增伤部分debug的时候想到的，仔细思考了结构后我认为可能会出现这个问题。
        或许我想的有问题，索性留言一下，你看到了也考虑考虑这个地方到底会不会出bug
        """

    def solve_buff(self) -> None:
        """提前处理Buff实例"""
        Buff.buff_add(self.tick, self.data.loading_buff, self.data.dynamic_buff, self.data.enemy)
        buff_events = []
        other_events = []
        for event in self.data.event_list[:]:
            if isinstance(event, Buff.Buff):
                buff_events.append(event)
            else:
                other_events.append(event)
        self.data.event_list = buff_events + other_events

    def skill_event(self, _event: Preload.SkillNode | LoadingMission) -> None:
        """SkillNode处理分支逻辑"""
        if isinstance(_event, LoadingMission):
            event = _event.mission_node
            hitted_count = _event.hitted_count
        else:
            event = _event
            hitted_count = 0
            """
            注意，主动动作的skill_node，都会在Load阶段被打包成LoadingMission的数据结构传入，所以具有非0的hitted_count，
            而其他阶段通过暴力手段添加进event_list的大概率都是未经打包的Skill_node，它们往往与hitted_count所关联的系统没有联动，所以此处强制设置为0
            目前，hitted_count参数只服务于enemy下面的QTE次数计算。未来若有其他需求，那么本函数则需要重构（迟早的事）
            """
        char_obj = None
        for character in self.data.char_obj_list:
            if character.NAME == event.skill.char_name:
                char_obj = character
        if char_obj is None:
            assert False, f"{event.skill.char_name} not found in char_obj_list"
        # 计算伤害的对象
        cal_obj = Calculator(skill_node=event,
                             character_obj=char_obj,
                             enemy_obj=self.data.enemy,
                             dynamic_buff=self.data.dynamic_buff)
        snapshot = cal_obj.cal_snapshot()
        stun = cal_obj.cal_stun()
        dmg_expect = cal_obj.cal_dmg_expect()
        dmg_crit = cal_obj.cal_dmg_crit()
        hit_result = SingleHit(event.skill_tag, snapshot, stun, dmg_expect, dmg_crit, hitted_count)
        if event.skill.follow_by:
            hit_result.proactive = False
        if event.hit_times == hitted_count and event.skill.heavy_attack:
            # 重攻击标签！
            hit_result.heavy_hit = True
        self.enemy.hit_received(hit_result, self.tick)

        Report.report_dmg_result(tick=self.tick,
                                 element_type=event.skill.element_type,
                                 skill_tag=event.skill_tag,
                                 dmg_expect=dmg_expect,
                                 dmg_crit=dmg_crit,
                                 stun=stun,
                                 stun_status=self.data.enemy.dynamic.stun,
                                 buildup=snapshot[1],
                                 enemy_dynamic=self.data.enemy.dynamic.__str__()
                                 )

    def anomaly_event(self, event: AnB) -> None:
        """普通异常伤害处理分支逻辑"""
        cal_obj = CalAnomaly(anomaly_obj=event, enemy_obj=self.data.enemy, dynamic_buff=self.data.dynamic_buff)
        dmg_anomaly = cal_obj.cal_anomaly_dmg()
        Report.report_dmg_result(tick=self.tick,
                                 element_type=event.element_type,
                                 dmg_expect=dmg_anomaly,
                                 is_anomaly=True)

    def disorder_event(self, event: Disorder):
        """紊乱处理分支逻辑"""
        cal_obj = CalDisorder(disorder_obj=event, enemy_obj=self.data.enemy, dynamic_buff=self.data.dynamic_buff)
        dmg_disorder = cal_obj.cal_anomaly_dmg()
        stun = cal_obj.cal_disorder_stun()
        self.data.enemy.update_stun(stun)
        Report.report_dmg_result(tick=self.tick,
                                 element_type=event.element_type,
                                 dmg_expect=dmg_disorder,
                                 is_anomaly=True,
                                 is_disorder=True)

    def refresh_event(self, event: ScheduleRefreshData):
        """强制更新角色数据"""
        character: Character
        char_mapping = {character.NAME: character for character in self.data.char_obj_list}
        target: str = ''
        try:
            for target in event.sp_target:
                if target != '':
                    char_mapping[target].update_sp(event.sp_value)
            for target in event.decibel_target:
                if target != '':
                    char_mapping[target].update_decibel(event.decibel_value)
        except KeyError:
            raise ValueError(f"[Schedule] target: {target} not found in char_obj_list, check the alloc.")


if __name__ == '__main__':
    pass