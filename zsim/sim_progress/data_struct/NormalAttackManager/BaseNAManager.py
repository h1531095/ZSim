from abc import ABC, abstractmethod

from attr.validators import is_callable


class BaseNAManager(ABC):
    def __init__(self, char_obj, rule_inventory_dict: dict):
        self.char = char_obj
        self.na_rule_inventory: dict = rule_inventory_dict
        self.RULE_MAP: dict = {'default': lambda: True}
        self.special_first_hit_list = [1141]

    @property
    def first_hit(self):
        """首次普攻"""
        return str(self.char.CID) + "_NA_1" if self.char.CID not in self.special_first_hit_list else str(self.char.CID) + "_SNA_1"

    def na_rule_selector(self) -> dict:
        """选择普攻策略！"""
        for rule_name, check_func in self.RULE_MAP.items():
            if check_func():
                return self.na_rule_inventory[rule_name]
        else:
            return self.na_rule_inventory['default']

    def spawn_out_na(self, skill_node):
        """生成普攻"""
        _na_dict = self.na_rule_selector()
        if skill_node.skill_tag in _na_dict:
            return _na_dict[skill_node.skill_tag]
        else:
            return self.first_hit

