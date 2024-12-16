import apl_condition


class APLExecutor:
    """
    APL代码的执行部分。它会调用apl_condition并且轮询所有的APL代码，
    找出第一个符合条件的动作并且执行。
    """
    def __init__(self, actions: list, game_state: dict):
        self.actions_list = actions
        self.game_state = game_state

    def execute(self):
        for action in self.actions_list:
            if all(apl_condition.APLCondition(self.game_state).evaluate(cond) for cond in action["conditions"]):
                self.perform_action(action["action"])
                break  # 找到第一个符合条件的动作并执行


    def perform_action(self, action: str):
        print(f"Executing action: {action}")
        # 在这里调用实际的技能或效果逻辑
