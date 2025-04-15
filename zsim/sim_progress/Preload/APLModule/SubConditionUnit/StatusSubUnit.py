from .BaseSubConditionUnit import BaseSubConditionUnit
from sim_progress.Preload.APLModule.APLJudgeTools.FindCharacter import find_char
from sim_progress.Buff.JudgeTools import find_tick


class StatusSubUnit(BaseSubConditionUnit):
    def __init__(self, priority: int, sub_condition_dict: dict = None, mode=0):
        super().__init__(priority=priority, sub_condition_dict=sub_condition_dict, mode=mode)
        self.enemy = None

    class CheckHandler:
        @classmethod
        def handler(cls,  *args, **kwargs):
            raise NotImplementedError

    class StunHandler(CheckHandler):
        @classmethod
        def handler(cls, enemy):
            return enemy.dynamic.stun

    class QTETriggerableHandler(CheckHandler):
        @classmethod
        def handler(cls, enemy):
            return enemy.qte_manager.qte_data.qte_triggerable_times

    class QTETriggeredHandler(CheckHandler):
        @classmethod
        def handler(cls, enemy):
            return enemy.qte_manager.qte_data.qte_triggered_times

    class QTEActivationAvailableHandler(CheckHandler):
        @classmethod
        def handler(cls, enemy):
            return enemy.qte_manager.qte_data.qte_activation_available

    class AnomalyPctHandler(CheckHandler):
        def __init__(self, anomaly_number):
            self.anomaly_number = anomaly_number

        def handler(self, enemy):
            return enemy.anomaly_bars_dict[self.anomaly_number].get_buildup_pct()

    class StunPctHandler(CheckHandler):
        @classmethod
        def handler(cls,  enemy):
            return enemy.get_stun_percentage()

    class CharLastingNodeTagHandler(CheckHandler):
        @classmethod
        def handler(cls, char_cid, found_char_dict, game_state):
            tick = find_tick()
            char = find_char(found_char_dict, game_state, char_cid)
            return char.dynamic.lasting_node.spamming_info(tick)[1]

    class CharLastingNodeTickHandler(CheckHandler):
        @classmethod
        def handler(cls, char_cid, found_char_dict, game_state):
            tick = find_tick()
            char = find_char(found_char_dict, game_state, char_cid)
            return char.dynamic.lasting_node.spamming_info(tick)[2]

    class CharRepeatTimesHandler(CheckHandler):
        @classmethod
        def handler(cls, char_cid, found_char_dict, game_state):
            tick = find_tick()
            char = find_char(found_char_dict, game_state, char_cid)
            return char.dynamic.lasting_node.spamming_info(tick)[3]

    class CharOnFieldHandler(CheckHandler):
        @classmethod
        def handler(cls, char_cid, found_char_dict, game_state):
            char = find_char(found_char_dict, game_state, char_cid)
            return char.dynamic.on_field

    class SingleQTEHandler(CheckHandler):
        @classmethod
        def handler(cls, enemy):
            return enemy.qte_manager.qte_data.single_qte

    class CharAvailableHandler(CheckHandler):
        @classmethod
        def handler(cls, char_cid, found_char_dict, game_state):
            char = find_char(found_char_dict, game_state, char_cid)
            return char.is_available(find_tick())

    class ActiveAnomalyHandler(CheckHandler):
        @classmethod
        def handler(cls, enemy, *args, **kwargs):
            return enemy.dynamic.is_under_anomaly()

    class ShockHandler(CheckHandler):
        @classmethod
        def handler(cls, enemy):
            return enemy.dynamic.shock

    class BurnHandler(CheckHandler):
        @classmethod
        def handler(cls, enemy):
            return enemy.dynamic.burn

    class AssultHandler(CheckHandler):
        @classmethod
        def handler(cls, enemy):
            return enemy.dynamic.assult

    class FrostbiteHandler(CheckHandler):
        @classmethod
        def handler(cls, enemy):
            return enemy.dynamic.frostbite

    class FrostFrostbiteHandler(CheckHandler):
        @classmethod
        def handler(cls, enemy):
            return enemy.dynamic.frost_frostbite

    class CorruptionHandler(CheckHandler):
        @classmethod
        def handler(cls, enemy):
            return enemy.dynamic.corruption

    HANDLE_MAP = {
        'stun': StunHandler,
        'QTE_triggerable_times': QTETriggerableHandler,
        'QTE_triggered_times': QTETriggeredHandler,
        'anomaly_pct': AnomalyPctHandler,
        'lasting_node_tag': CharLastingNodeTagHandler,
        'lasting_node_tick': CharLastingNodeTickHandler,
        'on_field': CharOnFieldHandler,
        'QTE_activation_available': QTEActivationAvailableHandler,
        'single_qte': SingleQTEHandler,
        'repeat_times': CharRepeatTimesHandler,
        'stun_pct': StunPctHandler,
        'char_available': CharAvailableHandler,
        'is_under_anomaly': ActiveAnomalyHandler,
        'is_shock': ShockHandler,
        'is_burn': BurnHandler,
        'is_assult': AssultHandler,
        'is_frostbite': FrostbiteHandler,
        'is_frost_frostbite': FrostFrostbiteHandler,
        'is_corruption': CorruptionHandler,
    }

    def check_myself(self, found_char_dict, game_state, *args, **kwargs):
        if self.check_target == 'enemy':
            if self.enemy is None:
                self.enemy = game_state['schedule_data'].enemy

            if 'anomaly_pct' in self.check_stat:
                anomaly_number = int(self.check_stat[-1])
                handler = self.HANDLE_MAP['anomaly_pct'](anomaly_number)
            else:
                handler_cls = self.HANDLE_MAP.get(self.check_stat)
                handler = handler_cls() if handler_cls else None
            if not handler:
                raise ValueError(f'当前检查的check_stat为：{self.check_stat}，优先级为{self.priority}，暂无处理该属性的逻辑模块！')
            return self.spawn_result(handler.handler(self.enemy))
        else:
            '''既然check_target不是Enemy，那么一定是char的CID'''
            handler_cls = self.HANDLE_MAP.get(self.check_stat)
            handler = handler_cls() if handler_cls else None
            if not handler:
                raise ValueError(f'当前检查的check_stat为：{self.check_stat}，优先级为{self.priority}，暂无处理该属性的逻辑模块！')
            return self.spawn_result(handler.handler(int(self.check_target), found_char_dict, game_state))

