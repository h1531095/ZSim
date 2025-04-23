from sim_progress.Preload.APLModule.APLJudgeTools import (
    get_last_action,
    check_cid,
    get_personal_node_stack,
)
from sim_progress.Preload.APLModule.SubConditionUnit import BaseSubConditionUnit


class ActionSubUnit(BaseSubConditionUnit):
    def __init__(self, priority: int, sub_condition_dict: dict = None, mode=0):
        super().__init__(
            priority=priority, sub_condition_dict=sub_condition_dict, mode=mode
        )

    class ActionCheckHandler:
        @classmethod
        def handler(cls, *args, **kwargs):
            raise NotImplementedError

    class LatestActionTagHandler(ActionCheckHandler):
        @classmethod
        def handler(cls, game_state):
            return get_last_action(game_state)

    class StrictLinkedHandler(ActionCheckHandler):
        """强衔接判定，技能skill_tag符合的同时，还需要上一个动作刚好结束。"""

        @classmethod
        def handler(cls, char_cid: int, game_state, tick: int) -> str | None:
            char_stack = get_personal_node_stack(game_state).get(char_cid, None)
            if char_stack is None:
                return None
            else:
                for i in range(char_stack.length):
                    current_node = char_stack.peek_index(i)
                    if current_node is None:
                        return None
                    if current_node.skill.labels is not None and 'additional_damage' in current_node.skill.labels:
                        continue
                    else:
                        if current_node.end_tick != tick:
                            return None
                        return current_node.skill_tag
                else:
                    return None

    class LenientLinkedHandler(ActionCheckHandler):
        @classmethod
        def handler(cls, char_cid: int, game_state, tick: int) -> str | None:
            char_stack = get_personal_node_stack(game_state).get(char_cid, None)
            if char_stack is None:
                return None
            for i in range(char_stack.length):
                current_node = char_stack.peek_index(i)
                if current_node is None:
                    return None
                if current_node.skill.labels is not None and 'additional_damage' in current_node.skill.labels:
                    continue
                else:
                    return current_node.skill_tag
            else:
                return None

    class FirstActionHandler(ActionCheckHandler):
        @classmethod
        def handler(cls, char_cid: int, game_state, tick: int) -> bool:
            char_stack = get_personal_node_stack(game_state).get(char_cid, None)
            if char_stack is None:
                return True
            else:
                current_node = char_stack.peek()
                if current_node is None:
                    return True
            return False

    ActionHandlerMap = {
        "skill_tag": LatestActionTagHandler,
        "strict_linked_after": StrictLinkedHandler,
        "lenient_linked_after": LenientLinkedHandler,
        "first_action": FirstActionHandler,
    }

    def check_myself(self, found_char_dict, game_state, *args, **kwargs):
        """处理 动作判定类 的子条件"""
        handler_cls = self.ActionHandlerMap.get(self.check_stat)
        handler = handler_cls() if handler_cls else None
        if not handler:
            raise ValueError(
                f"当前检查的check_stat为：{self.check_stat}，优先级为{self.priority}，暂无处理该属性的逻辑模块！"
            )
        if self.check_target == "after":
            return self.spawn_result(handler.handler(game_state))
        else:
            """check_target 不是 after（其实已经弃用了），就是CID"""
            from sim_progress.Buff.JudgeTools import find_tick

            check_cid(self.check_target)
            char_cid = int(self.check_target)
            tick = find_tick()
            return self.spawn_result(handler.handler(char_cid, game_state, tick))
        #     if self.check_stat == 'skill_tag':
        #         checked_value = get_last_action(game_state)
        #         return self.spawn_result(checked_value)
        #     else:
        #         raise ValueError(f'子条件中的check_stat为：{self.check_stat}，优先级为{self.priority}，暂无处理该属性的逻辑模块！')
        # else:
        #     raise ValueError(f'子条件中的check_target为：{self.check_target}，优先级为{self.priority}，暂无处理该目标类型的逻辑模块！')
