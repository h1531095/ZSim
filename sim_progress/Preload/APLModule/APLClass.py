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
        self.preload_data = None
        self.actions_list = all_apl_unit_list
        try:
            json_path = APL_NA_ORDER_PATH
            with open(json_path, "r", encoding="utf-8") as file:
                self.NA_action_dict = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"初始化时发生错误: {e}")
            self.NA_action_dict = {}
        self.apl_operator: APLOperator | None = None
        self.repeat_action: tuple[str, int] = ('', 0)

    def execute(self, tick, mode: int) -> tuple[str, int]:
        if self.game_state is None:
            self.get_game_state()
        if self.apl_operator is None:
            self.apl_operator = APLOperator(self.actions_list, self.game_state)
        cid, skill_tag, apl_priority = self.apl_operator.spawn_next_action()
        return self.perform_action(cid, skill_tag, tick), apl_priority

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

    def perform_action(self, CID: int, action: str, tick: int) -> str:
        """APL逻辑判定通过，执行动作！"""
        if self.game_state is None:
            self.game_state = self.get_game_state()
        if self.preload_data is None:
            self.preload_data = self.game_state.get('preload').preload_data
        output = self.action_processor(CID, action)
        return output

    def action_processor(self, CID, action) -> str:
        """用于生成动作"""
        last_action: SkillNode | None
        if action == 'auto_NA':
            stack = self.preload_data.personal_node_stack.get(CID, None)
            if stack is None:
                last_action = None
            else:
                last_action = stack.peek()
            if (last_action is None or
                    CID != self.preload_data.operating_now):
                '''没有第一个动作时，直接派生第一段普攻'''
                output = self.spawn_default_action(CID)
            elif last_action.skill_tag in self.NA_action_dict[str(CID)]:
                output = self.NA_action_dict[str(CID)][last_action.skill_tag]
            else:
                output = self.spawn_default_action(CID)
        else:
            output = action
        return output

    @staticmethod
    def spawn_default_action(cid: int) -> str:
        """用来生成第一段普攻。"""
        if cid in [1141]:
            return f'{cid}_SNA_1'
        else:
            return f'{cid}_NA_1'







