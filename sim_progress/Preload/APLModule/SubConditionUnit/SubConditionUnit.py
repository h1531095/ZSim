from sim_progress.Preload.APLModule.APLJudgeTools import find_char, get_nested_value, find_buff, get_last_action
import re
from .BaseSubConditionUnit import BaseSubConditionUnit


class AttributeSubUnit(BaseSubConditionUnit):
    def __init__(self, priority: int, sub_condition_dict: dict = None, mode=0):
        super().__init__(priority=priority, sub_condition_dict=sub_condition_dict, mode=mode)

    def get_attribute_from_char(self, char):
        if self.check_stat == 'energy':
            return char.sp
        elif self.check_stat == 'decibel':
            return char.decibel
        elif self.check_stat == 'special_resource':
            return char.get_resources()[1]
        elif self.check_stat == 'special_state':
            if self.nested_stat_key_list:
                return get_nested_value(self.nested_stat_key_list, char.get_special_stats())
            else:
                '''大概率get_special_stats函数返回的值不会是一个单层结构，大部分都是多层的。所以，当前分支很可能永远都用不上。'''
                return char.get_special_stats()
        else:
            raise ValueError(f'子条件中的check_stat为：{self.check_stat}，优先级为{self.priority}，暂无处理该属性的逻辑模块！')

    def check_myself(self, found_char_dict, game_state: dict, *args, **kwargs):
        """处理 属性判定类 的子条件"""
        if len(self.check_target) != 4 or not bool(re.match(r'^-?\d+$', self.check_target)):
            '''检测self.check_target是否是4位int'''
            raise ValueError(f'子条件中的CID格式不对！{self.check_target}')
        char = find_char(found_char_dict, game_state, int(self.check_target))
        checked_value = self.get_attribute_from_char(char)
        result = self.spawn_result(checked_value)
        return result


class BuffSubUnit(BaseSubConditionUnit):
    def __init__(self, priority: int, sub_condition_dict: dict = None, mode=0):
        super().__init__(priority=priority, sub_condition_dict=sub_condition_dict, mode=mode)

    def check_myself(self, found_char_dict, game_state, *args, **kwargs):
        if len(self.check_target) != 4 or not bool(re.match(r'^-?\d+$', self.check_target)):
            '''检测self.check_target是否是4位int'''
            raise ValueError(f'子条件中的CID格式不对！{self.check_target}')
        buff_index = self.nested_stat_key_list[0]
        char = find_char(found_char_dict, game_state, int(self.check_target))
        buff = find_buff(game_state, char, buff_index)
        if self.check_stat == 'exist':
            if buff is not None:
                return self.spawn_result(True)
            else:
                return self.spawn_result(False)
        elif self.check_stat == 'count':
            if buff is not None:
                return self.spawn_result(buff.dy.count)
            else:
                return self.spawn_result(0)
        else:
            raise ValueError(f'未完成的解析条件！{self.check_stat}， 优先级为{self.priority}')


class ActionSubUnit(BaseSubConditionUnit):
    def __init__(self, priority: int, sub_condition_dict: dict = None, mode=0):
        super().__init__(priority=priority, sub_condition_dict=sub_condition_dict, mode=mode)

    def check_myself(self, found_char_dict, game_state, *args, **kwargs):
        """处理 动作判定类 的子条件"""
        if self.check_target == "after":
            if self.check_stat == 'skill_tag':
                checked_value = get_last_action(game_state)
                return self.spawn_result(checked_value)
            else:
                raise ValueError(f'子条件中的check_stat为：{self.check_stat}，优先级为{self.priority}，暂无处理该属性的逻辑模块！')
        else:
            raise ValueError(f'子条件中的check_target为：{self.check_target}，优先级为{self.priority}，暂无处理该目标类型的逻辑模块！')
