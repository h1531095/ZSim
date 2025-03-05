from .SubConditionUnit import *
from define import compare_methods_mapping
from abc import ABC, abstractmethod


class APLUnit(ABC):
    def __init__(self):
        """一行APL就是一个APLUnit，它是所有APLUnit的基类。"""
        self.priority = 0
        self.char_CID = None
        self.break_when_found_action = True
        self.result = None
        self.sub_conditions_unit_list = []

    @abstractmethod
    def check_all_sub_units(self, found_char_dict, game_state):
        pass


class ActionAPLUnit(APLUnit):
    def __init__(self, apl_unit_dict: dict):
        """动作类APL，目前也只有这一种APL类型。"""
        super().__init__()
        self.char_CID = apl_unit_dict['CID']
        self.priority = apl_unit_dict['priority']
        self.break_when_found_action = True
        self.result = apl_unit_dict['action']
        for condition_str in apl_unit_dict['conditions']:
            self.sub_conditions_unit_list.append(spawn_sub_condition(self.priority, condition_str))

    def check_all_sub_units(self, found_char_dict, game_state):
        """单行APL的逻辑函数：检查所有子条件并且输出结果"""
        if not self.sub_conditions_unit_list:
            '''无条件直接输出True'''
            return True
        for sub_units in self.sub_conditions_unit_list:
            if not isinstance(sub_units, BaseSubConditionUnit):
                raise TypeError(f'ActionAPLUnit类的sub_conditions_unit_list中的对象构建不正确！')
            if not sub_units.check_myself(found_char_dict, game_state):
                return False
        else:
            return True


def spawn_sub_condition(priority: int, sub_condition_code: str = None) -> ActionSubUnit | BuffSubUnit | StatusSubUnit | AttributeSubUnit | ActionSubUnit:
    """解构apl子条件字符串，并且组建出构建sub_condition类需要的构造字典"""
    logic_mode = 0
    sub_condition_dict = {}
    code_head = sub_condition_code.split(':')[0]
    if 'special' not in code_head and '.' not in code_head:
        raise ValueError(f'不正确的条件代码！{sub_condition_code}')
    if code_head.startswith('!'):
        code_head = code_head[1:]
        logic_mode = 1
    sub_condition_dict['type'] = code_head.split('.')[0]
    sub_condition_dict['target'] = code_head.split('.')[1]
    code_body = sub_condition_code.split(':')[1]
    for _operator in ['>=', '<=', '==', '>', '<', '!=']:
        if _operator in code_body:
            sub_condition_dict['operation_type'] = compare_methods_mapping[_operator]
            sub_condition_dict['stat'] = code_body.split(_operator)[0]
            sub_condition_dict['value'] = code_body.split(_operator)[1]
            break
    else:
        raise ValueError(f'不正确的计算符！{code_body}')
    sub_condition_output = sub_condition_unit_factory(priority, sub_condition_dict, mode=logic_mode)
    return sub_condition_output


def sub_condition_unit_factory(priority: int, sub_condition_dict: dict = None, mode=0):
    """根据传入的dict，来构建不同的子条件单元"""
    condition_type = sub_condition_dict['type']
    if condition_type not in ['status', 'attribute', 'buff', 'action', 'special']:
        raise ValueError(f'不正确的条件类型！{sub_condition_dict["type"]}')
    if condition_type == 'status':
        return StatusSubUnit(priority, sub_condition_dict, mode)
    elif condition_type == 'attribute':
        return AttributeSubUnit(priority, sub_condition_dict, mode)
    elif condition_type == 'buff':
        return BuffSubUnit(priority, sub_condition_dict, mode)
    elif condition_type == 'action':
        return ActionSubUnit(priority, sub_condition_dict, mode)
    elif condition_type == 'special':
        raise ValueError(f'special类的APL解析，是当前尚未开发的功能！优先级为{priority}，')
