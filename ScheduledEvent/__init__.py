import Report
import Buff.BuffAdd
import Buff.BuffLoad
import Enemy
import Preload
# from main import ScheduleData
from Anomaly import AnomalyEffect as AnE
from Buff.BuffExist_Judge import buff_exist_judge
from ScheduledEvent.Calculator import Calculator
from CharSet_new import Character


class ScheduledEvent:
    """
    计划事件方法类

    主逻辑链 self.event_start()：
    1、读取计划事件列表，将其中所有的buff示例排到列表最靠前的位置。self.sort_events()
    2、遍历事件列表，从开始到结束，将每一个事件派发到分支逻辑链内进行处理
    """

    def __init__(self,dynamic_buff: dict, data, tick: int, *, loading_buff: dict = None):

        self.data = data
        self.data.dynamic_buff = dynamic_buff

        if loading_buff is None:
            loading_buff = {}
        elif not isinstance(loading_buff, dict):
            raise ValueError(f'loading_buff参数必须为字典，但你输入了{loading_buff}')

        if not isinstance(tick, int):
            raise ValueError(f'tick参数必须为整数，但你输入了{tick}')

        # 更新Data
        self.tick = tick
        self.data.loading_buff = loading_buff

    def event_start(self):
        """Schedule主逻辑"""

        # 判断循环
        if self.data.event_list:
            self.solve_buff()  # 先处理优先级高的buff
            for event in self.data.event_list[:]:
                # 添加buff
                if isinstance(event, Buff.Buff):
                    raise NotImplementedError(f"{type(event)}，目前不应存在于 event_list")
                elif isinstance(event, Preload.SkillNode):
                    if event.preload_tick <= self.tick:
                        self.skill_event(event)
                        self.data.event_list.remove(event)
                elif isinstance(event, AnE):
                    raise NotImplementedError
                else:
                    raise NotImplementedError(f"Wrong event type: {type(event)}")

    def solve_buff(self) -> None:
        """提前处理Buff实例"""
        Buff.BuffAdd.buff_add(self.tick, self.data.loading_buff, self.data.dynamic_buff, self.data.enemy)
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
        # TODO 对接 Anomaly
        # 对接 Enemy 失衡条
        stun = cal_obj.cal_stun()
        self.data.enemy.update_stun(stun)

        Report.report_dmg_result(tick=self.tick,
                                 element_type=event.skill.element_type,
                                 skill_tag=event.skill_tag,
                                 dmg_expect=cal_obj.cal_dmg_expect(),
                                 dmg_crit=cal_obj.cal_dmg_crit(),
                                 stun = stun,
                                 stun_status = self.data.enemy.dynamic.stun
                                 )


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