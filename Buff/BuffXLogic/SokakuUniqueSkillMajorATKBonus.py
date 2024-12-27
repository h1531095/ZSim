from Buff import Buff, JudgeTools


class SokakuUniqueSkillMajorATKBonus(Buff.BuffLogic):
    """
    苍角的核心被动2：消耗涡流的展旗会叠加双倍的攻击力。
    程序对苍角的两个Buff是剥离处理的。
    Buff1是简单判定逻辑，只要有展旗，就一定触发。
    Buff2作为额外的层数，在判定出涡流下降沿时再触发。
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.xstart = self.special_start_logic
        self.xjudge = self.special_judge_logic
        self.dynamic_buff_list = None
        self.char = None
        self.buff_0 = None
        self.sub_exist_buff_dict = None

    def special_judge_logic(self):
        """
        检测到展旗的TAG后，去查当前的资源数量。
        由于执行本代码的阶段是Load阶段，而资源消耗事件是发生在Preload阶段的。
        所以，本阶段理论上能够检测到资源的下降沿。
        但是由于每次Buff都会新建，所以，这里的self是不能存历史资源的。
        必须存放在Buff_0.history.last_update_resource里面。
        """
        if self.char is None:
            self.char = JudgeTools.find_char_from_CID(1131)
        if self.sub_exist_buff_dict is None:
            all_name_order_box = JudgeTools.find_load_data().all_name_order_box
            next_char = all_name_order_box['苍角'][1]
            self.sub_exist_buff_dict = JudgeTools.find_exist_buff_dict()[next_char]
        if self.buff_0 is None:
            self.buff_0 = self.sub_exist_buff_dict['Buff-角色-苍角-核心被动-2']
        action_stack = JudgeTools.find_stack()
        action_now = action_stack.peek()
        resource_now = self.char.get_resources()[1]
        if action_now.mission_tag == '1131_E_EX_A':
            match_code = lambda a, b: a < b
            if JudgeTools.detect_edge((resource_now, self.buff_0.history.last_update_rescource), match_code):
                self.buff_0.history.last_update_rescource = resource_now
                return True
        self.buff_0.history.last_update_rescource = resource_now
        return False

    def special_start_logic(self):
        """
        展旗发动时，应该检索当前角色的面板攻击力。
        如果能顺利执行这个模块，那么意味着已经检测到下降沿。
        直接调取攻击力并按单倍计算即可。
        ——————————————————————————
        注意，这里不能按照技能说明，用双倍算，
        因为这个Buff2只是攻击力Buff的一半，另外一半的层数，在Buff1身上。
        """
        if self.char is None:
            self.char = JudgeTools.find_char_from_CID(1131)
        if self.sub_exist_buff_dict is None:
            all_name_order_box = JudgeTools.find_load_data().all_name_order_box
            next_char = all_name_order_box['苍角'][1]
            self.sub_exist_buff_dict = JudgeTools.find_exist_buff_dict()[next_char]
        if self.buff_0 is None:
            self.buff_0 = self.sub_exist_buff_dict['Buff-角色-苍角-核心被动-2']
        atk_now = self.char.statement.ATK
        count = min(atk_now * 0.2, 500)
        tick_now = JudgeTools.find_tick()
        self.buff_instance.simple_start(tick_now, self.sub_exist_buff_dict)
        # 先用simple_start把buff开起来。然后再修改层数。
        self.buff_instance.dy.count = count
        self.buff_instance.update_to_buff_0(self.buff_0)



