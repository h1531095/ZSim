from sim_progress import Buff, Preload, Report
from sim_progress.AnomalyBar import AnomalyBar as AnB
from sim_progress.AnomalyBar import Disorder
from sim_progress.AnomalyBar.CopyAnomalyForOutput import (
    PolarityDisorder,
    DirgeOfDestinyAnomaly,
)
from sim_progress.Buff import ScheduleBuffSettle
from sim_progress.Character import Character
from sim_progress.data_struct import (
    ActionStack,
    ScheduleRefreshData,
    SingleHit,
    SPUpdateData,
)
from sim_progress.Load.loading_mission import LoadingMission
from sim_progress.Preload import SkillNode
from sim_progress.Update import update_anomaly

from .CalAnomaly import CalAbloom, CalAnomaly, CalDisorder, CalPolarityDisorder
from .Calculator import Calculator


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
    ):
        self.data = data  # ScheduleData in __main__
        self.data.dynamic_buff = dynamic_buff
        self.judge_required_info_dict = data.judge_required_info_dict
        self.action_stack = action_stack

        if loading_buff is None:
            loading_buff = {}
        elif not isinstance(loading_buff, dict):
            raise ValueError(f"loading_buff参数必须为字典，但你输入了{loading_buff}")

        if not isinstance(tick, int):
            raise ValueError(f"tick参数必须为整数，但你输入了{tick}")

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
            sp_update_date = SPUpdateData(
                char_obj=char, dynamic_buff=self.data.dynamic_buff
            )
            char.update_sp_and_decibel(sp_update_date)
        # 判断循环
        if self.data.event_list:
            self.solve_buff()  # 先处理优先级高的buff

            # 其余事件挨个处理
            for _ in range(len(self.data.event_list)):
                event = self.data.event_list.pop(0)
                # 添加buff
                if isinstance(event, Buff.Buff):
                    raise NotImplementedError(
                        f"{type(event)}，目前不应存在于 event_list"
                    )
                elif isinstance(event, Preload.SkillNode | LoadingMission):
                    if event.preload_tick <= self.tick:
                        self.skill_event(event)
                        self.judge_required_info_dict["skill_node"] = event
                        """
                        在2025.4.14的更新中，在skill_event分支新增了下面这个函数，
                        这是经过改良后的新的更新异常条的节点。
                        具体原因见函数内部，这里不过多赘述。
                        """
                        self.update_anomaly_bar_after_skill_event(event)
                        ScheduleBuffSettle(
                            self.tick,
                            self.exist_buff_dict,
                            self.enemy,
                            self.data.dynamic_buff,
                            self.action_stack,
                            skill_node=event,
                        )
                elif isinstance(event, DirgeOfDestinyAnomaly):
                    self.abloom_event(event)
                    self.judge_required_info_dict["abloom"] = event
                elif isinstance(event, PolarityDisorder):
                    self.polarity_disorder_event(event)
                    self.judge_required_info_dict["polarity_disorder"] = event
                elif isinstance(event, Disorder):
                    # print(f'检测到{event.element_type}属性的紊乱，快照为：{event.current_ndarray}')
                    self.disorder_event(event)
                    self.judge_required_info_dict["disorder"] = event
                elif isinstance(event, AnB):
                    self.anomaly_event(event)
                    self.judge_required_info_dict["anb"] = event
                elif isinstance(event, ScheduleRefreshData):
                    self.refresh_event(event)
                    self.judge_required_info_dict["refresh"] = event
                else:
                    raise NotImplementedError(
                        f"{type(event)}，目前不应存在于 event_list"
                    )

            # 计算过程中如果又有新的事件生成，则继续循环
            if self.data.event_list:
                self.event_start()

    def update_anomaly_bar_after_skill_event(self, event):
        """在Schedule阶段，处理完一个SkillEvent后，都要进行一次异常条更新。"""
        """
        将异常值更新移动到Schedule阶段的主要原因：原有的Buff更新、异常/紊乱结算的顺序不合理；
        原有顺序：
        Preload -> Load -> update_anomaly() -> Buff(第一轮) ->  Schedule -> Buff(第二轮)
        现有顺序：
        Preload -> Load -> Buff(第一轮) ->  Schedule -> update_anomaly() -> Buff(第二轮)
        
        由于update_anomaly()函数是根据现有积蓄值来判断是否触发属性异常的，
        所以在运行过程中，只有先把积蓄值打满的下一次update_anomaly()才会触发属性异常，
        无论是哪种结构，enemy的receive_hit()函数都会在Schedule阶段执行，
        故任何早于Schedule阶段的update_anomaly都只能更新到上个tick的属性异常，
        所以，原有结构中，第Ntick打满的异常条，会在第N+1 tick被激活，
        
        一般情况下，这种迟滞1tick的激活行为不会对模拟的结果造成影响，
        (长难句警告！！)--但若是某个Buff事件的激活 依赖于发生在 技能last_hit标签处的属性异常更新--
        那么在老的结构下，事件的更新顺序为
            --(第N Tick)-- 
                -> update_anomaly(此时的异常条还没打满[来自于上个tick]所以第Ntick的运行无结果)
                -> Buff事件触发器检测（异常条更新状态没有改变，所以触发器不触发） 
                -> Schedule，AnomalyBar满，
            --(第N+1 Tick)--
                -> update_anomaly(异常条满，更新异常)
                -> Buff事件触发器检测（已经错过了触发窗口，所以触发器不触发）
            
        而在新的结构下，事件更新顺序为：
            --(第N Tick)-- 
                -> Schedule，AnomalyBar满，
                -> update_anomaly(异常条满，更新异常)
                -> Buff事件触发器检测（将该Buff改为Schedule处理类型）
        
        上述结构的改变就能够彻底规避来自于结构的触发误差——来自柳极性紊乱触发器的启发
        """
        if isinstance(event, SkillNode):
            _node = event
        elif isinstance(event, LoadingMission):
            _node = event.mission_node
        else:
            raise TypeError("无法解析的事件类型")

        """接下来要通过技能的异常更新特性，判断当前Tick的技能是否能够更新异常
        由于调用函数的位置是ScheduleEvent，所以一定是Hit事件发生时，
        所以，直接调用loading_mission.hitted_count数量就可以获得当前正在被结算的Hit次数。"""
        should_update = False
        if not _node.skill.anomaly_update_rule:
            if self.tick - 1 < _node.loading_mission.get_last_hit() <= self.tick:
                should_update = True
        else:
            if _node.skill.anomaly_update_rule == -1:
                should_update = True
            else:
                if (
                    _node.loading_mission.hitted_count
                    in _node.skill.anomaly_update_rule
                ):
                    should_update = True
        if should_update:
            update_anomaly(
                _node.skill.element_type,
                self.enemy,
                self.tick,
                self.data.event_list,
                self.data.char_obj_list,
                skill_node=_node,
                dynamic_buff_dict=self.data.dynamic_buff,
            )

    def solve_buff(self) -> None:
        """提前处理Buff实例"""
        Buff.buff_add(
            self.tick, self.data.loading_buff, self.data.dynamic_buff, self.data.enemy
        )
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
        cal_obj = Calculator(
            skill_node=event,
            character_obj=char_obj,
            enemy_obj=self.data.enemy,
            dynamic_buff=self.data.dynamic_buff,
        )
        snapshot = cal_obj.cal_snapshot()
        stun = cal_obj.cal_stun()
        dmg_expect = cal_obj.cal_dmg_expect()
        dmg_crit = cal_obj.cal_dmg_crit()
        hit_result = SingleHit(
            event.skill_tag, snapshot, stun, dmg_expect, dmg_crit, hitted_count
        )
        hit_result.skill_node = event
        if event.skill.follow_by:
            hit_result.proactive = False
        if event.hit_times == hitted_count and event.skill.heavy_attack:
            # 重攻击标签！
            hit_result.heavy_hit = True
        self.enemy.hit_received(hit_result, self.tick)

        Report.report_dmg_result(
            tick=self.tick,
            element_type=event.skill.element_type,
            skill_tag=event.skill_tag,
            dmg_expect=round(dmg_expect, 2),
            dmg_crit=round(dmg_crit, 2),
            stun=round(stun, 2),
            buildup=round(snapshot[1], 2),
            **self.data.enemy.dynamic.get_status(),
            UUID=event.UUID,
        )
        # enemy_dynamic=self.data.enemy.dynamic.__str__()

    def anomaly_event(self, event: AnB) -> None:
        """普通异常伤害处理分支逻辑"""
        cal_obj = CalAnomaly(
            anomaly_obj=event,
            enemy_obj=self.data.enemy,
            dynamic_buff=self.data.dynamic_buff,
        )
        dmg_anomaly = cal_obj.cal_anomaly_dmg()
        # TODO：异常伤害无法被enemy接收到，Enemy的血量更新是有问题的。
        Report.report_dmg_result(
            tick=self.tick,
            element_type=event.element_type,
            dmg_expect=round(dmg_anomaly, 2),
            is_anomaly=True,
            dmg_crit=round(dmg_anomaly, 2),
            stun=0,
            buildup=0,
            **self.data.enemy.dynamic.get_status(),
        )

    def disorder_event(self, event: Disorder):
        """紊乱处理分支逻辑"""
        cal_obj = CalDisorder(
            disorder_obj=event,
            enemy_obj=self.data.enemy,
            dynamic_buff=self.data.dynamic_buff,
        )
        dmg_disorder = cal_obj.cal_anomaly_dmg()
        stun = cal_obj.cal_disorder_stun()
        # TODO：紊乱伤害无法被enemy接收到，Enemy的血量更新是有问题的。
        self.data.enemy.update_stun(stun)
        Report.report_dmg_result(
            tick=self.tick,
            element_type=event.element_type,
            dmg_expect=round(dmg_disorder, 2),
            is_anomaly=True,
            is_disorder=True,
            stun=round(stun, 2),
            buildup=0,
            **self.data.enemy.dynamic.get_status(),
        )

    def polarity_disorder_event(self, event: PolarityDisorder):
        """极性紊乱处理分支逻辑"""
        cal_obj = CalPolarityDisorder(
            disorder_obj=event,
            enemy_obj=self.data.enemy,
            dynamic_buff=self.data.dynamic_buff,
        )
        dmg_disorder = cal_obj.cal_anomaly_dmg()
        Report.report_dmg_result(
            tick=self.tick,
            element_type=event.element_type,
            skill_tag="极性紊乱",
            dmg_expect=round(dmg_disorder, 2),
            is_anomaly=True,
            is_disorder=True,
            stun=0,
            buildup=0,
            **self.data.enemy.dynamic.get_status(),
        )

    def abloom_event(self, event: DirgeOfDestinyAnomaly):
        """薇薇安绽放处理分支逻辑"""
        cal_obj = CalAbloom(
            anomaly_obj=event,
            enemy_obj=self.data.enemy,
            dynamic_buff=self.data.dynamic_buff,
        )
        dmg_anomaly = cal_obj.cal_anomaly_dmg()
        # TODO：异常伤害无法被enemy接收到，Enemy的血量更新是有问题的。
        Report.report_dmg_result(
            tick=self.tick,
            element_type=event.element_type,
            skill_tag="绽放",
            dmg_expect=round(dmg_anomaly, 2),
            is_anomaly=True,
            dmg_crit=round(dmg_anomaly, 2),
            stun=0,
            buildup=0,
            **self.data.enemy.dynamic.get_status(),
        )

    def refresh_event(self, event: ScheduleRefreshData):
        """强制更新角色数据"""
        char_mapping = {
            character.NAME: character for character in self.data.char_obj_list
        }
        target: str = ""
        try:
            for target in event.sp_target:
                if target != "":
                    char_mapping[target].update_sp(event.sp_value)
            for target in event.decibel_target:
                if target != "":
                    char_mapping[target].update_decibel(event.decibel_value)
        except KeyError:
            raise ValueError(
                f"[Schedule] target: {target} not found in char_obj_list, check the alloc."
            )


if __name__ == "__main__":
    pass
