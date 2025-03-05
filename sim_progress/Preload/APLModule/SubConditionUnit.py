from .APLJudgeTools import check_number_type, find_char, get_nested_value, find_buff, get_last_action
from abc import ABC, abstractmethod
import re


class BaseSubConditionUnit(ABC):
    def __init__(self, priority: int, sub_condition_dict: dict = None, mode=0):
        """单个APL判断条件的对象基类。"""
        self.logic_mode = mode
        self.priority = priority
        if sub_condition_dict is None:
            self.no_condition = True
        else:
            self.no_condition = False
        self.check_target = sub_condition_dict['target']  # 检查目标 比如enemy，self，或者角色ID
        self.check_stat = None
        self.nested_stat_key_list = []
        '''
        在check_stat难免会碰到多层的嵌套结构，在APL中，统一用'→'来表示嵌套结构，这个list就是用来装这些嵌套的key的。
        目前，nested_stat_key_list只为char.get_special_states函数服务
        '''
        if '→' in sub_condition_dict['stat']:  # 被检查的参数，这里有很多，不一一列举。
            self.check_stat = sub_condition_dict['stat'].split('→')[0]
            self.nested_stat_key_list = sub_condition_dict['stat'].split('→')[1:]
        else:
            self.check_stat = sub_condition_dict['stat']
        self.operation_type = sub_condition_dict['operation_type']  # 计算类型，主要是比较符和调用符
        self.check_value = check_number_type(sub_condition_dict['value'])  # 参与计算的值 或者调用的函数名

    @abstractmethod
    def check_myself(self,found_char_dict, game_state, *args, **kwargs):
        pass

    def spawn_result(self, value=None):
        """根据self.operation_type中的匿名函数来输出结果的函数"""
        # value = check_number_type(value)
        result = self.operation_type(value, self.check_value)
        # print(f'result：{value, self.check_value, str(self.operation_type), result}')
        return self.translate_result(result)

    def translate_result(self, result):
        if self.logic_mode == 0:
            return result
        else:
            return not result


class StatusSubUnit(BaseSubConditionUnit):
    def __init__(self, priority: int, sub_condition_dict: dict = None, mode=0):
        super().__init__(priority=priority, sub_condition_dict=sub_condition_dict, mode=mode)

    def check_myself(self, found_char_dict, game_state, *args, **kwargs):
        if self.check_target == 'enemy':
            enemy = game_state['schedule_data'].enemy
            if self.check_stat == 'stun':
                checked_value = enemy.dynamic.stun
                return self.spawn_result(checked_value)
            elif self.check_stat == 'QTE_triggerable_times':
                checked_value = enemy.QTE_triggerable_times
                return self.spawn_result(checked_value)
            elif self.check_stat == 'QTE_triggered_times':
                checked_value = enemy.dynamic.QTE_triggered_times
                return self.spawn_result(checked_value)
            elif 'anomaly_pct' in self.check_stat:
                anomaly_number = int(self.check_stat[-1])
                checked_value = enemy.anomaly_bars_dict[anomaly_number].get_buildup_pct()
                return self.spawn_result(checked_value)
            else:
                raise ValueError(f'子条件中的check_stat为：{self.check_stat}，优先级为{self.priority}，暂无处理该属性的逻辑模块！')
    # else:
    #     '''self.check_target 不是enemy就是角色，所以这个分支就是角色了。'''
    #     try:
    #         chra_cid = int(self.check_target)
    #     except TypeError:
    #         raise TypeError(f'在status.CID类的条件解析中，获取CID失败！出问题字段为：{self.check_target}')
    #     # raise ValueError(f'子条件中的check_target为：{self.check_target}，优先级为{self.priority}，暂无处理该目标类型的逻辑模块！')


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
                return self.operation_type(True, self.check_value)
            else:
                return self.operation_type(False, self.check_value)
        elif self.check_stat == 'count':
            if buff is not None:
                return self.operation_type(buff.dy.count, self.check_value)
            else:
                return self.operation_type(0, self.check_value)
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
