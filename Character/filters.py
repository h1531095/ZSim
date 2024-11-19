from Preload import SkillNode
from ScheduledEvent import MultiplierData

def _skill_node_filter(*args, **kwargs) -> list[SkillNode]:
    """过滤出输入的 SKillNode，并作为列表返回"""
    skill_nodes: list[SkillNode] = []
    for arg in args:
        if isinstance(arg, SkillNode):
            skill_nodes.append(arg)
    for value in kwargs.values():
        if isinstance(value, SkillNode):
            skill_nodes.append(value)
    return skill_nodes

def _multiplier_filter(*args, **kwargs) -> list[MultiplierData]:
    """过滤出输入的 乘区数据，并作为列表返回"""
    multiplier_data: list[MultiplierData] = []
    for arg in args:
        if isinstance(arg, MultiplierData):
            multiplier_data.append(arg)
    for value in kwargs.items():
        if isinstance(value, MultiplierData):
            multiplier_data.append(value)
    return multiplier_data