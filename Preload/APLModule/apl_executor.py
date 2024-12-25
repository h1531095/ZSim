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
        self.apl = None

    def execute(self):
        if self.game_state is None:
            self.get_game_state()
        if self.apl is None:
            self.apl = APLCondition(self.game_state)

        # 找到第一个符合条件的动作并执行
        for action in self.actions_list:
            conditions = action.get('conditions', None)

            # 如果没有条件，直接执行
            if not conditions:
                self.perform_action(action['CID'], action["action"])
                return

            # 检查条件
            for cond in conditions:
                # 如果 cond 是字符串，evaluate 返回 False 则跳过该动作
                if isinstance(cond, str):
                    if not self.apl.evaluate(action, cond):
                        break
                # 如果 cond 是列表，只有所有 sub_cond 都为 False 才跳过该动作
                elif "/or/" in cond:
                    cond_list = cond.split("/or/")
                    if not any(self.apl.evaluate(action, sub_cond) for sub_cond in cond_list):
                        break
            else:
                # 如果所有条件都通过，执行动作并退出
                self.perform_action(action['CID'], action["action"])
                return

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
            last_action = self.game_state['preload'].preload_data.last_node
            if last_action is None:
                output = f'{CID}_NA_1'
            elif last_action.skill_tag in self.NA_action_dict[CID]:
                output = self.NA_action_dict[CID][last_action.skill_tag]
            else:
                output = f'{CID}_NA_1'
        else:
            output = action

        return output

