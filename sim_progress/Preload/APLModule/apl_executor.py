from .apl_condition import APLCondition
import json
import sys
from define import APL_NA_ORDER_PATH, SWAP_CANCEL
from sim_progress.Preload import SkillNode


class APLExecutor:
    """
    APL代码的执行部分。它会调用apl_condition并且轮询所有的APL代码，
    找出第一个符合条件的动作并且执行。
    """
    def __init__(self, actions: list):
        self.game_state: dict | None = None
        self.actions_list = actions
        try:
            json_path = APL_NA_ORDER_PATH
            with open(json_path, "r", encoding="utf-8") as file:
                self.NA_action_dict = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"初始化时发生错误: {e}")
            self.NA_action_dict = {}
        self.apl: APLCondition | None = None

    def execute(self, mode: int):
        if self.game_state is None:
            self.get_game_state()
        if self.apl is None:
            self.apl = APLCondition(self.game_state)

        # 找到第一个符合条件的动作并执行
        for action in self.actions_list:
            """
            在20250120的版本更新中，新增了action.force+=的APL类型，
            该类型的动作会强制执行，无视条件，但并不是在execute函数中执行，所以，这里直接跳过。
            """
            if mode == 0:
                if ".force+=" in action['type']:
                    continue
            elif mode == 1:
                if ".force+=" not in action['type']:
                    continue
            else:
                raise ValueError("输入的mode参数错误！")
            conditions = action.get('conditions', None)
            # TODO：切人CD的判断
            #  1、该行内容是否涉及换人，如果为True，则检查切人CD；
            #  2、判断子条件

            # 如果没有条件，直接执行
            if not conditions:
                return self.perform_action(action['CID'], action["action"])
            # 检查条件
            for cond in conditions:
                if "/or/" in cond:
                    cond_new = cond.split("/or/")
                else:
                    cond_new = cond
                # 如果 cond 是字符串，evaluate 返回 False 则跳过该动作
                if isinstance(cond_new, str):
                    if not self.distinguish_bool_logic(action, cond_new):
                        break
                # 如果 cond 是列表，只有所有 sub_cond 都为 False 才跳过该动作
                elif isinstance(cond_new, list):
                    if any(self.distinguish_bool_logic(action, sub_cond) for sub_cond in cond_new):
                        continue
                    else:
                        break
            else:
                # 如果所有条件都通过，执行动作并退出
                return self.perform_action(action['CID'], action["action"])



    def get_game_state(self) -> dict | None:
        if self.game_state is None:
            try:
                # 延迟从 sys.modules 获取字典A，假设 main 模块中已定义字典 A
                main_module = sys.modules['simulator.main_loop']
                if main_module is None:
                    raise ImportError("Main module not found.")
                self.game_state = main_module.game_state  # 获取 main 中的 A
            except Exception as e:
                print(f"Error loading dictionary A: {e}")
        return self.game_state

    def perform_action(self, CID: int, action: str) -> str:
        self.game_state = self.get_game_state()
        if action == 'auto_NA':
            last_action: SkillNode | None = None
            if self.game_state is not None and 'preload' in self.game_state:
                if SWAP_CANCEL:
                    last_action = self.game_state['preload'].preload_data.current_node
                else:
                    last_action = self.game_state['preload'].preload_data.last_node
            if last_action is None:
                output = f'{CID}_NA_1'
            elif last_action.skill_tag in self.NA_action_dict[CID]:
                output = self.NA_action_dict[CID][last_action.skill_tag]
            else:
                if CID in ['1141']:
                    output = f'{CID}_SNA_1'
                else:
                    output = f'{CID}_NA_1'
        else:
            output = action
        return output

    def distinguish_bool_logic(self, action: dict, cond: str):
        if not cond:
            raise ValueError(f'当前{action["action"]}的condition为空！')
        if self.apl is None:
            raise ValueError("APLCondition is not initialized.")
        
        if cond.startswith("!"):
            cond_new = cond[1:]
            return not self.apl.evaluate(action, cond_new)
        else:
            return self.apl.evaluate(action, cond)