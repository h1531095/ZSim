from sim_progress.Preload import SkillNode
from sim_progress.Preload.PreloadEngine import BasePreloadEngine
from sim_progress.Preload.APLModule.APLJudgeTools import get_game_state


class ForceAddEngine(BasePreloadEngine):
    """该引擎的主要作用是：在技能结束时，检索它们的后置技能，并且执行添加"""
    def __init__(self, data):
        super().__init__(data)
        self.game_state = None
        self.found_char_dict = {}

    def run_myself(self):
        """当每个node结束时，都应该调用这个函数来判断强制添加。"""
        self.active_signal = False
        for stack in self.data.personal_node_stack.values():
            node = stack.peek()
            if node is None:
                return
            if not isinstance(node, SkillNode):
                raise TypeError("传入给ForceAddEngine的参数必须是SkillNode实例！")
            follow_up: list = node.skill.follow_up
            if not follow_up:
                return
            conditions_unit: list = node.skill.force_add_condition_APL
            should_force_add, index = self.prcoess_force_add_apl(conditions_unit)
            if should_force_add:
                self.check_char(follow_up, index, node)
                self.data.preload_action_list_before_confirm.append((follow_up[index], False))
                self.active_signal = True

    def check_char(self, follow_up, index, node):
        """
        该函数的作用：确保：B角色技能在强制预载时，并没有动作存在即可。
        如果程序流程合理，这个函数是不会被执行的。
        """
        follow_up_skill_CID = int(follow_up[index][:4])
        follow_up_skill_add_tick = node.end_tick
        if node.end_tick < self.data.personal_node_stack.peek().end_tick:
            raise ValueError(
                f"出现了不应该出现的情况！技能{follow_up[index]}理应在{node.skill_tag}之后、于{follow_up_skill_add_tick}执行，但是此时角色{follow_up_skill_CID}尚有动作存在。")

    def prcoess_force_add_apl(self, conditions_unit):
        """强制添加动作的前置判定，有APL模块则运行模块，无APL模块则直接通过。"""
        should_force_add = True
        index = 0
        if conditions_unit and self.game_state is None:
            self.game_state = get_game_state()
        if conditions_unit:
            """存在条件类APL判定"""
            for unit in conditions_unit:
                _apl_result, result_box = unit.check_all_sub_units(self.found_char_dict, self.game_state)
                if not _apl_result:
                    should_force_add = False
                    index += 1
                else:
                    return should_force_add, index
        else:
            return should_force_add, index

