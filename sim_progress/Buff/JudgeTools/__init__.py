from .DetectEdges import detect_edge
from .FindCharFromCID import find_char_from_CID
from .FindMain import *
from .FindCharFromName import find_char_from_name
from .FindEquipper import find_equipper


def check_preparation(buff_0, **kwargs):
    """
    这是一个综合函数。根据传入的参数，来执行不同的内容。
    """
    # 先决条件检查
    if buff_0.history.record is None:
        raise ValueError(f'buff_0的record模块尚未初始化！！！')
    record = buff_0.history.record

    # 参数获取
    equipper: str = kwargs.get("equipper")
    char_CID: int = kwargs.get("char_CID")
    char_NAME: str = kwargs.get("char_NAME")
    enemy = kwargs.get("enemy")
    sub_exist_buff_dict = kwargs.get("sub_exist_buff_dict")
    dynamic_buff_list = kwargs.get("dynamic_buff_list")
    action_stack = kwargs.get("action_stack")
    event_list = kwargs.get("event_list")
    trigger_buff_0 = kwargs.get("trigger_buff_0")
    preload_data = kwargs.get("preload_data")

    # 参数正确性检查
    if sub_exist_buff_dict and char_NAME is None and char_CID is None and equipper is None:
        raise ValueError(f'在查询sub_exist_buff_dict的同时，应保证传入char_CID/char_NAME/equipper中的一个参数')

    # 函数主体部分
    if equipper:
        if record.equipper is None:
            record.equipper = find_equipper(equipper)
        if record.char is None:
            record.char = find_char_from_name(record.equipper)
    if char_CID:
        if record.char is None:
            record.char = find_char_from_CID(char_CID)
    if char_NAME:
        if record.char is None:
            record.char = find_char_from_name(char_NAME)

    if sub_exist_buff_dict:
        if record.char is None:
            raise ValueError(f'在buff_0.history.record 中并未读取到对应的char')
        if record.sub_exist_buff_dict is None:
            record.sub_exist_buff_dict = find_exist_buff_dict()[record.char.NAME]
    if enemy:
        if record.enemy is None:
            record.enemy = find_enemy()
    if dynamic_buff_list:
        if record.dynamic_buff_list is None:
            record.dynamic_buff_list = find_dynamic_buff_list()
    if action_stack:
        if record.action_stack is None:
            record.action_stack = find_stack()
    if event_list:
        print('event_list放在record中很有可能不会随动！！注意！')
        if record.event_list is None:
            record.event_list = find_event_list()
    if trigger_buff_0:
        if not isinstance(trigger_buff_0, tuple):
            raise TypeError(f'输入的参数必须是tuple！')
        if record.trigger_buff_0 is None:
            operator = trigger_buff_0[0]
            buff_index = trigger_buff_0[1]
            if operator == 'equipper':
                if record.equipper is None:
                    record.equipper = find_equipper(operator)
                operator = record.equipper
            sub_exist_buff_dict = find_exist_buff_dict()[operator]
            founded_list = []
            for _buff_founded in sub_exist_buff_dict.values():
                if buff_index in _buff_founded.ft.index:
                    founded_list.append(_buff_founded)
            if len(founded_list) != 1:
                raise ValueError(f'在{operator}的sub_exist_buff_dict中找到了{len(founded_list)}个{buff_index}')
            record.trigger_buff_0 = founded_list[0]
    if preload_data:
        if record.preload_data is None:
            record.preload_data = find_preload_data()




