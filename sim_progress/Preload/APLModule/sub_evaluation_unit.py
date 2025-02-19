import re
from define import SWAP_CANCEL, compare_methods_mapping
from sim_progress.Character import Character


class sub_evaluation_unit:
    def __init__(self, priority: int = 0, all_condition_list: list = None):
        """
        在2025.2.19的更新中，为了优化APL模块的性能，我决定重写APL逻辑，用类来承载apl的子逻辑模块，
        这种载体名为：子条件判定单元，Sub (Condition) Evaluation Unit
        在构建这些“子条件类”的时候，需要传入优先级以及子条件（可能是字符串或者是列表），还有动作参数。
        """
        self.priority = priority    # 优先级，也是判定单元在APLCondition.condtion_inventory中的key
        self.sub_condition_list = []    # 子任务列表
        self.result_box = []
        '''由于传入的condition可能是并列的多个条件，所以这里要考虑str与list两种情况，并统一转化为list'''
        if isinstance(all_condition_list, list):
            self.condition_code_list = all_condition_list
        else:
            raise ValueError(f'传入的all_condition_list参数不是列表！{all_condition_list}')

        '''接下来，要针对condition_list进行解析'''
        for sub_cond in self.condition_code_list:
            _sub_condition = spawn_sub_condition(priority, sub_cond)
            if not isinstance(_sub_condition, sub_condition):
                raise ValueError(f'构造sub_condition对象失败！')
            self.sub_condition_list.append(_sub_condition)

    def run_myself(self, found_char_dict, game_state):
        self.result_box = []
        """子逻辑单元运行函数，只有包含的所有的子条件全部输出True，才会返回True，否则就返回False"""
        for sub_cond in self.sub_condition_list:
            result = sub_cond.check_myself(found_char_dict, game_state)
            self.result_box.append(result)
            if not result:
                return False
        else:
            # print(f'apl判定通过！当前优先级为{self.priority}，条件情况为：{self.result_box}, 总条件情况为：{self.condition_code_list}')
            return True


class sub_condition:
    """ 子条件的类，内含有apl子条件的解构，以及自判定。"""
    def __init__(self, priority: int, sub_condition_dict: dict = None, mode=0):
        """
        这里的mode记录了字逻辑模块的逻辑需求，
        0：正常逻辑：运行结果True，输出True
        1：非逻辑：运行结果False，输出True
        该参数的运用将在self.check_myself函数中体现。
        """
        self.logic_mode = mode
        self.priority = priority
        if sub_condition_dict is None:
            self.no_condition = True
        else:
            self.no_condition = False
            if sub_condition_dict['type'] not in ['status', 'attribute', 'buff', 'action', 'special']:
                raise ValueError(f'不正确的条件类型！{sub_condition_dict["type"]}')
            self.condition_dict = sub_condition_dict
            self.condition_type = sub_condition_dict['type']    # 条件类型，共有五类，状态，属性，Buff，动作，special
            self.check_target = sub_condition_dict['target']    # 检查目标 比如enemy，self，或者角色ID

            self.nested_stat_key_list = []
            '''
            在check_stat难免会碰到多层的嵌套结构，在APL中，统一用'→'来表示嵌套结构，这个list就是用来装这些嵌套的key的。
            目前，nested_stat_key_list只为char.get_special_states函数服务
            '''
            if '→' in sub_condition_dict['stat']:          # 被检查的参数，这里有很多，不一一列举。
                self.check_stat = sub_condition_dict['stat'].split('→')[0]
                self.nested_stat_key_list = sub_condition_dict['stat'].split('→')[1:]
            else:
                self.check_stat = sub_condition_dict['stat']
            self.operation_type = sub_condition_dict['operation_type']  # 计算类型，主要是比较符和调用符
            self.check_value = check_number_type(sub_condition_dict['value'])      # 参与计算的值 或者调用的函数名

    def check_myself(self, found_char_dict: dict, game_state: dict):
        if self.no_condition:
            return True
        if self.condition_type == 'status':
            result = self.check_status_condition(game_state)
        elif self.condition_type == 'attribute':
            result = self.check_attribute_condition(found_char_dict, game_state)
        elif self.condition_type == 'buff':
            result = self.check_buff_condition(found_char_dict, game_state)
        elif self.condition_type == 'action':
            result = self.check_action_condition(game_state)
        elif self.condition_type == 'special':
            raise ValueError(f'special类的APL解析，是当前尚未开发的功能！优先级为{self.priority}，')
        else:
            '''大概率不会触发，属于重复检测'''
            raise ValueError(f'不正确的条件类型！{self.condition_type}')
        if self.logic_mode == 0:
            return result
        else:
            return not result

    def spawn_result(self, value=None):
        """根据self.operation_type中的匿名函数来输出结果的函数"""
        value = check_number_type(value)
        result = self.operation_type(value, self.check_value)
        # print(f'result：{value, self.check_value, str(self.operation_type), result}')
        return result

    def check_status_condition(self, game_state: dict):
        """处理 状态判定类 的子条件"""
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
        else:
            raise ValueError(f'子条件中的check_target为：{self.check_target}，优先级为{self.priority}，暂无处理该目标类型的逻辑模块！')

    def check_action_condition(self, game_state: dict):
        """处理 动作判定类 的子条件"""
        if self.check_target == "after":
            if self.check_stat == 'skill_tag':
                checked_value = get_last_action(game_state)
                return self.spawn_result(checked_value)
            else:
                raise ValueError(f'子条件中的check_stat为：{self.check_stat}，优先级为{self.priority}，暂无处理该属性的逻辑模块！')
        else:
            raise ValueError(f'子条件中的check_target为：{self.check_target}，优先级为{self.priority}，暂无处理该目标类型的逻辑模块！')

    def check_attribute_condition(self, found_char_dict: dict, game_state: dict):
        """处理 属性判定类 的子条件"""
        if len(self.check_target) != 4 or not bool(re.match(r'^-?\d+$', self.check_target)):
            '''检测self.check_target是否是4位int'''
            raise ValueError(f'子条件中的CID格式不对！{self.check_target}')
        char = find_char(found_char_dict, game_state, int(self.check_target))
        checked_value = self.get_attribute_from_char(char)
        result = self.spawn_result(checked_value)
        return result

    def check_buff_condition(self, found_char_dict: dict, game_state: dict):
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

    def get_attribute_from_char(self, char: Character):
        if self.check_stat == 'energy':
            return char.sp
        elif self.check_stat == 'decibel':
            return char.decibel
        elif self.check_stat == 'special_resource':
            return char.get_resources()
        elif self.check_stat == 'special_state':
            if self.nested_stat_key_list:
                return get_nested_value(self.nested_stat_key_list, char.get_special_stats())
            else:
                '''大概率get_special_stats函数返回的值不会是一个单层结构，大部分都是多层的。所以，当前分支很可能永远都用不上。'''
                return char.get_special_stats()
        else:
            raise ValueError(f'子条件中的check_stat为：{self.check_stat}，优先级为{self.priority}，暂无处理该属性的逻辑模块！')


def get_last_action(game_state: dict):
    """
    注意，这个函数获取的应该是上一个主动动作的名称，
    所以，这里调用的是preload_data.current_on_field_node
    """
    if SWAP_CANCEL:
        return game_state['preload'].preload_data.current_on_field_node_tag
    else:
        last_node = getattr(game_state['preload'].preload_data,'last_node', None)
        if last_node is None:
            return None
        output = last_node.skill_tag
        return output


def find_buff(game_state: dict, char, buff_index):
    """
    根据buff的index来找到buff
    通常用于判断“当前是否有该Buff激活”
    """
    for buffs in game_state["global_stats"].DYNAMIC_BUFF_DICT[char.NAME]:
        if buffs.ft.index == buff_index:
            return buffs
    else:
        return None


def check_number_type(text):
    """
    将文本的整型、浮点数、布尔值、元组转化为正常格式，纯文本不变、若是类型不是文本则直接输出。
    :param text: 输入的参数，可能是文本或已经正确的类型
    :return: 转换后的值
    """
    if isinstance(text, str):
        # 尝试转换为整型
        try:
            return int(text)
        except ValueError:
            pass
        # 尝试转换为浮点数
        try:
            return float(text)
        except ValueError:
            pass
        # 尝试转换为布尔值
        if text.lower() in ['true', 'false']:
            return text.lower() == 'true'
        # 尝试转换为元组
        if text.startswith('(') and text.endswith(')'):
            try:
                # 去除括号并分割元素
                elements = text[1:-1].split(',')
                # 递归处理每个元素
                return tuple(check_number_type(elem.strip()) for elem in elements)[1]
            except ValueError:
                pass
        # 如果以上转换都失败，返回原文本
        return text
    elif isinstance(text, tuple):
        # 如果是元组，递归处理每个元素
        return tuple(check_number_type(elem) for elem in text)[1]
    else:
        # 如果不是文本类型，直接返回
        return text


def find_char(found_char_dict: dict, game_state: dict, CID: int) -> Character:
    """
    根据提供的CID，找到对应的char，并且返回、保存在self.found_char_dict中。
    每次调用时，会先检查是否在self.found_char_dict中。如果找不到，再扔出去。
    """
    if CID in found_char_dict.keys():
        return found_char_dict[CID]
    char: Character
    for char in game_state["char_data"].char_obj_list:
        if char.CID == int(CID):
            found_char_dict[char.CID] = char
            return char
    else:
        raise ValueError(f'未找到CID为{CID}的角色！')


def get_nested_value(key_list: list, data):
    """递归获取嵌套结构中的值，一挖到底"""
    if not key_list:
        return data
    if len(key_list) > 1:
        key = key_list[0]
        if isinstance(data, dict) and key in data:
            return get_nested_value(data[key], key_list[1:])
        elif isinstance(data, list | tuple) and isinstance(key, int) and 0 <= key < len(data):
            return get_nested_value(data[key], key_list[1:])
    elif len(key_list) == 1:
        key = key_list[0]
        if isinstance(data, dict) and key in data:
            return data[key]
        elif isinstance(data, list | tuple) and isinstance(key, int) and 0 <= key < len(data):
            return data[key]
        else:
            raise ValueError(f'无法解析的数据类型！{data, type(data)}')

    # elif hasattr(data, key):  # 处理类对象
    #     return get_nested_value(getattr(data, key), key_list[1:])
    # else:
    #     raise ValueError(f'无法解析的数据类型！{data, type(data)}')


def spawn_sub_condition(priority: int, sub_condition_code: str = None):
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
    sub_condition_output = sub_condition(priority, sub_condition_dict, mode=logic_mode)
    return sub_condition_output








