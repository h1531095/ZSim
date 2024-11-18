import Buff.BuffAdd
import Buff.BuffLoad
from Buff import ScheduleBuffSettle
import Enemy
import Preload
import Report

from AnomalyBar import AnomalyBar as AnB

from AnomalyBar import Disorder
from Buff.BuffExist_Judge import buff_exist_judge
from Character import Character
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

    def __init__(self, dynamic_buff: dict, data, tick: int, exist_buff_dict: dict, *, loading_buff: dict = None, judging_buff: dict = None):

        self.data = data
        self.data.dynamic_buff = dynamic_buff
        self.judge_required_info_dict = data.judge_required_info_dict

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
            # EXPLAIN：mul是个类，包含了角色的所有信息，包括静态面板、动态面板。
            mul = MultiplierData(character_obj=char, dynamic_buff=self.data.dynamic_buff, enemy_obj=self.data.enemy)
            char.update_sp_and_decibel(mul)
        # 判断循环
        if self.data.event_list:
            self.solve_buff()  # 先处理优先级高的buff

            # 其余事件挨个处理
            for _ in range(len(self.data.event_list)):
                event = self.data.event_list.pop(0)
                # 添加buff
                if isinstance(event, Buff.Buff):
                    raise NotImplementedError(f"{type(event)}，目前不应存在于 event_list")
                elif isinstance(event, Preload.SkillNode):
                    if event.preload_tick <= self.tick:
                        self.skill_event(event)
                        self.judge_required_info_dict['skill_node'] = event
                elif isinstance(event, AnB):
                    self.anomaly_event(event)
                    self.judge_required_info_dict['anb'] = event
                elif isinstance(event, Disorder):
                    self.disorder_event(event)
                    self.judge_required_info_dict['disorder'] = event
                else:
                    raise NotImplementedError(f"{type(event)}，目前不应存在于 event_list")
                ScheduleBuffSettle(self.tick, self.exist_buff_dict, self.enemy, self.data.dynamic_buff)

            # 计算过程中如果又有新的事件生成，则继续循环
            if self.data.event_list:
                self.event_start()



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

    def skill_event(self, event: Preload.SkillNode) -> None:
        """SkillNode处理分支逻辑"""
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
        self.data.enemy.update_stun(stun)
        if snapshot[1] >= 0.0001:
            element_type_code = snapshot[0]
            updated_bar = self.data.enemy.anomaly_bars_dict[element_type_code]
            if isinstance(updated_bar, AnB):
                updated_bar.update_snap_shot(snapshot)

        Report.report_dmg_result(tick=self.tick,
                                 element_type=event.skill.element_type,
                                 skill_tag=event.skill_tag,
                                 dmg_expect=cal_obj.cal_dmg_expect(),
                                 dmg_crit=cal_obj.cal_dmg_crit(),
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


if __name__ == '__main__':
    char = Character(name='艾莲')
    skills = char.skill_object
    p = Preload.Preload(skills)
    skill = p.preload_data.skills_queue[0]
    enemy = Enemy.Enemy()
    name_box = ['艾莲', '苍角', '莱卡恩']
    Judge_list_set = [['艾莲', '深海访客', '极地重金属'], ['苍角', '含羞恶面', '自由蓝调'],
                      ['莱卡恩', '拘缚者', '镇星迪斯科']]
    weapon_dict = {'艾莲': ['深海访客', 1], '苍角': ['含羞恶面', 5], '莱卡恩': ['拘缚者', 1]}
    exist_buff_dict = buff_exist_judge(name_box, Judge_list_set, weapon_dict)
    all_match, judge_condition_dict, active_condition_dict = Buff.BuffLoad.BuffInitialize('Ellen_PassiveSkill',
                                                                                          exist_buff_dict['艾莲'])
    buff = Buff.Buff(active_condition_dict, judge_condition_dict)
    test_md = Calculator(skill, char, enemy, {'艾莲': [buff]})
    pass