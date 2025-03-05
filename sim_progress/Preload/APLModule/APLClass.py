from .APLOperator import APLOperator
import json
import sys
from define import APL_NA_ORDER_PATH, SWAP_CANCEL
from sim_progress.Preload import SkillNode


class APLClass:
    """
    APL代码的执行部分。它会调用apl_condition并且轮询所有的APL代码，
    找出第一个符合条件的动作并且执行。
    """
    def __init__(self, all_apl_unit_list: list):
        self.game_state: dict | None = None
        self.actions_list = all_apl_unit_list
        try:
            json_path = APL_NA_ORDER_PATH
            with open(json_path, "r", encoding="utf-8") as file:
                self.NA_action_dict = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"初始化时发生错误: {e}")
            self.NA_action_dict = {}
        self.apl_operator: APLOperator | None = None

    def execute(self, mode: int):
        if self.game_state is None:
            self.get_game_state()
        if self.apl_operator is None:
            self.apl_operator = APLOperator(self.actions_list, self.game_state)
        cid, skill_tag = self.apl_operator.spawn_next_action()
        return self.perform_action(cid, skill_tag)

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
        """APL逻辑判定通过，执行动作！"""
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
                    '''部分角色默认的优先级最低的动作不是NA1而是SNA1'''
                    output = f'{CID}_SNA_1'
                else:
                    output = f'{CID}_NA_1'
        else:
            output = action
        return output

