from .apl_condition import APLCondition
import json
import sys
from define import APL_NA_ORDER_PATH


class APLExecutor:
    """
    APL代码的执行部分。它会调用apl_condition并且轮询所有的APL代码，
    找出第一个符合条件的动作并且执行。
    """
    def __init__(self, actions: list):
        self.game_state = None
        self.actions_list = actions
        try:
            json_path = APL_NA_ORDER_PATH
            with open(json_path, "r", encoding="utf-8") as file:
                self.NA_action_dict = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"初始化时发生错误: {e}")
            self.NA_action_dict = {}

    def execute(self):
        if self.game_state is None:
            self.get_game_state()
        # 找到第一个符合条件的动作并执行
        for action in self.actions_list:
            if action['conditions']:
                if all(APLCondition(self.game_state).evaluate(action, cond) for cond in action['conditions']):
                    return self.perform_action(action['CID'], action["action"])
            else:
                return self.perform_action(action['CID'], action["action"])

    def get_game_state(self):
        if self.game_state is None:
            try:
                # 延迟从 sys.modules 获取字典A，假设 main 模块中已定义字典 A
                main_module = sys.modules['__main__']
                if main_module is None:
                    raise ImportError("Main module not found.")
                self.game_state = main_module.game_state  # 获取 main 中的 A
            except Exception as e:
                print(f"Error loading dictionary A: {e}")
        return self.game_state

    def perform_action(self, CID, action: str):
        self.game_state = self.get_game_state()
        if action == 'auto_NA':
            last_action = self.game_state['preload'].preload_data.last_node.skill_tag
            if last_action in self.NA_action_dict[CID]:
                output = self.NA_action_dict[CID][last_action]
            elif last_action is None:
                output = f'{CID}_NA_1'
            else:
                output = f'{CID}_NA_1'
        else:
            output = action

        return output

