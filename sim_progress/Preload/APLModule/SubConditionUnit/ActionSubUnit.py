from sim_progress.Preload.APLModule.APLJudgeTools import get_last_action
from sim_progress.Preload.APLModule.SubConditionUnit import BaseSubConditionUnit


class ActionSubUnit(BaseSubConditionUnit):
    def __init__(self, priority: int, sub_condition_dict: dict = None, mode=0):
        super().__init__(priority=priority, sub_condition_dict=sub_condition_dict, mode=mode)

    class ActionCheckHandler:
        @classmethod
        def handler(cls, *args, **kwargs):
            raise NotImplementedError

    class LatestActionTagHandler(ActionCheckHandler):
        @classmethod
        def handler(cls, game_state):
            return get_last_action(game_state)

    ActionHandlerMap = {
        'skill_tag': LatestActionTagHandler
    }

    def check_myself(self, found_char_dict, game_state, *args, **kwargs):
        """处理 动作判定类 的子条件"""
        if self.check_target == "after":
            handler_cls = self.ActionHandlerMap.get(self.check_stat)
            handler = handler_cls() if handler_cls else None
            if not handler:
                raise ValueError(f'当前检查的check_stat为：{self.check_stat}，优先级为{self.priority}，暂无处理该属性的逻辑模块！')
            return self.spawn_result(handler.handler(game_state))
        #     if self.check_stat == 'skill_tag':
        #         checked_value = get_last_action(game_state)
        #         return self.spawn_result(checked_value)
        #     else:
        #         raise ValueError(f'子条件中的check_stat为：{self.check_stat}，优先级为{self.priority}，暂无处理该属性的逻辑模块！')
        # else:
        #     raise ValueError(f'子条件中的check_target为：{self.check_target}，优先级为{self.priority}，暂无处理该目标类型的逻辑模块！')
