from .NAManagerClasses import YanagiNAManager
from .BaseNAManager import BaseNAManager
from zsim.define import YANAGI_NA_ORDER, APL_NA_ORDER_PATH
import json

NA_RULE_INVENTORY_PATH = {
    1221: YANAGI_NA_ORDER
}

NA_MANAGER_MAP = {
    1221: YanagiNAManager
}


def na_manager_factory(char_obj) -> BaseNAManager:
    char_cid = char_obj.CID
    if char_cid in NA_RULE_INVENTORY_PATH:
        path = NA_RULE_INVENTORY_PATH.get(char_cid)
    else:
        path = APL_NA_ORDER_PATH
    if char_cid in NA_MANAGER_MAP:
        with open(path, "r", encoding="utf-8") as file:
            na_dict = json.load(file)
            return NA_MANAGER_MAP.get(char_cid)(char_obj, na_dict)
    else:
        with open(path, "r", encoding="utf-8") as file:
            all_default_na_dict = json.load(file)
            char_na_dict = all_default_na_dict.get(str(char_cid))
            dict_input = {'default': char_na_dict}
            return BaseNAManager(char_obj, dict_input)


if __name__ == '__main__':
    na_manager = na_manager_factory(1300)
    print(na_manager.na_rule_selector())
