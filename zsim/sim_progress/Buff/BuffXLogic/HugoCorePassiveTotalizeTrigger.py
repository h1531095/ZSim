from sim_progress.Buff import Buff, JudgeTools, check_preparation, find_tick
from sim_progress.Enemy import Enemy
from define import HUGO_REPORT


class HugoCorePassiveTotalizeTriggerRecord:
    def __init__(self):
        self.char = None
        self.enemy: Enemy | None = None
        self.active_signal = None
        self.E_totalize_tag = "1291_CorePassive_E_EX"
        self.Q_totalize_tag = "1291_CorePassive_Q"
        self.totalize_buff_index = "Buff-角色-雨果-决算倍率增幅"
        self.preload_data = None


class HugoCorePassiveTotalizeTrigger(Buff.BuffLogic):
    def __init__(self, buff_instance):
        """雨果核心被动，决算触发器"""
        super().__init__(buff_instance)
        self.buff_instance: Buff = buff_instance
        self.buff_0: Buff | None = None
        self.record: HugoCorePassiveTotalizeTriggerRecord | None = None
        self.xjudge = self.special_judge_logic
        self.xhit = self.special_hit_logic

    def get_prepared(self, **kwargs):
        return check_preparation(self.buff_0, **kwargs)

    def check_record_module(self):
        if self.buff_0 is None:
            self.buff_0 = JudgeTools.find_exist_buff_dict()["雨果"][
                self.buff_instance.ft.index
            ]
        if self.buff_0.history.record is None:
            self.buff_0.history.record = HugoCorePassiveTotalizeTriggerRecord()
        self.record = self.buff_0.history.record

    def special_judge_logic(self, **kwargs):
        """敌人处于失衡状态时，强化E、大招触发"""
        self.check_record_module()
        self.get_prepared(char_CID=1291, enemy=1, preload_data=1)
        skill_node = kwargs.get("skill_node", None)
        if skill_node is None:
            return False
        from sim_progress.Preload import SkillNode

        if not isinstance(skill_node, SkillNode):
            raise TypeError(
                f"{self.buff_instance.ft.index}的xjudge函数获取到的skill_node不是SkillNode类型"
            )

        # 过滤不是自己的技能
        if "1291" not in skill_node.skill_tag:
            return False

        # 过滤不是E、大招的技能
        if skill_node.skill.trigger_buff_level not in [2, 6]:
            return False

        # 过滤掉可能进入Buff循环的决算？？大概率不可能吧，决算能进BuffLoad那真的是见鬼了
        if skill_node.skill.labels is not None:
            if "totalize" in skill_node.skill.labels:
                return False

        # 过滤不是最后一次命中的技能
        if skill_node.loading_mission is None:
            return False
        if not skill_node.loading_mission.is_last_hit(find_tick()):
            return False

        if self.record.active_signal is not None:
            raise ValueError(
                "雨果的决算触发器在运行时候发现存在就一个未被结算的信号，这是不允许的"
            )
        # 如果是6命，则无条件放行强化E
        if self.record.char.cinema == 6 and skill_node.skill.trigger_buff_level == 2:
            self.record.active_signal = skill_node.skill.trigger_buff_level
            return True
        else:
            # 否则，检测敌人是否处于失衡状态
            if self.record.enemy.dynamic.stun:
                self.record.active_signal = skill_node.skill.trigger_buff_level
                return True
            else:
                return False

    def special_hit_logic(self, **kwargs):
        """结算E、大招"""
        self.check_record_module()
        self.get_prepared(char_CID=1291, enemy=1, preload_data=1)
        if self.record.active_signal is None:
            raise ValueError(
                "雨果的决算触发器的Xjudge函数放行了，但是Xhit函数却没有获取到触发信号"
            )
        if not self.record.enemy.dynamic.stun:
            raise ValueError(
                "雨果的决算触发器的Xjudge函数有放行了，但是敌人并未处于失衡状态"
            )

        """准备数据"""
        event_list = JudgeTools.find_event_list()
        rest_tick = self.record.enemy.get_stun_rest_tick()
        ratio = (
            1000
            + min(300, rest_tick) / 60 * 280
            + min(600, max(rest_tick - 300, 0)) / 60 * 100
        )
        print(
            f"决算触发了，触发源为{"大招" if self.record.active_signal == 6 else "强化E"}！本次决算结算的失衡时间为{rest_tick}，结算倍率为{ratio}，"
        ) if HUGO_REPORT else None

        """先处理Buff"""
        from sim_progress.Buff.BuffAddStrategy import buff_add_strategy

        buff_index = self.record.totalize_buff_index
        buff_add_strategy(buff_index, specified_count=ratio, benifit_list=["雨果"])
        stun_value_feed_back_ratio = min(rest_tick / 60, 5) * 0.05

        """再生成决算的skill_node"""
        from sim_progress.Preload.SkillsQueue import spawn_node
        from sim_progress.Load import LoadingMission

        if self.record.active_signal == 2:
            node_tag = self.record.E_totalize_tag
        elif self.record.active_signal == 6:
            node_tag = self.record.Q_totalize_tag
        else:
            raise ValueError(
                "雨果的决算触发器的Xjudge函数放行了，但是给出的信号不是强化E、大招"
            )
        totalize_node = spawn_node(
            node_tag, find_tick(), self.record.preload_data.skills
        )
        """给予技能节点一个loading_mission"""
        totalize_node.loading_mission = LoadingMission(totalize_node)
        totalize_node.loading_mission.mission_start(find_tick())
        event_list.append(totalize_node)

        """失衡状态强制结算事件"""
        from sim_progress.data_struct import StunForcedTerminationEvent

        stun_event = StunForcedTerminationEvent(
            self.record.enemy,
            stun_value_feed_back_ratio,
            execute_tick=find_tick(),
            event_source="雨果",
        )
        event_list.append(stun_event)

        """重置信号"""
        self.record.active_signal = None
