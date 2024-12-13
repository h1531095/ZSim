from Buff import Buff
import sys
anomaly_name_list = ["frostbite", "assault", "shock", "burn", "corruption"]


class HailstormShrineIceBonus(Buff.BuffLogic):
    """
    该buff为雅专武的冰伤判定模块。
    它需要检测所有的属性异常，找它们的上升沿。
    或者是当前动作的trigger_buff_level为强化特殊技
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.xjudge = self.special_judge_logic
        self.anomaly_state = {name: False for name in anomaly_name_list}

    def special_judge_logic(self):
        main_module = sys.modules["__main__"]
        action_stack = main_module.load_data.action_stack
        enemy = main_module.schedule_data.enemy
        action_now = action_stack.peek()

        current_anomalies = {name: getattr(enemy.dynamic, name) for name in anomaly_name_list}
        # 判断总异常数量是否 >= 2
        if sum(current_anomalies.values()) >= 2 or sum(self.anomaly_state.values()) >= 2:
            raise ValueError("当前ticks总异常数量为2！")

        # 检查是否有状态变化或满足特殊技触发条件
        has_change = any(current_anomalies[name] != self.anomaly_state[name] for name in anomaly_name_list)
        if has_change or action_now.mission_node.skill.trigger_buff_level == 2:
            self.anomaly_state.update(current_anomalies)
            return True

        # 更新状态并返回
        self.anomaly_state.update(current_anomalies)
        return False

