from Buff import Buff, JudgeTools


class SokakuUniqueSkillMinorATKBonus(Buff.BuffLogic):
    """
    这里是苍角的核心被动 1，核心被动1的触发无需复杂代码控制，
    只要释放了展旗，就会判定通过。
    但是，具体的层数，却是要根据苍角的面板攻击力实时调取的。
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.xstart = self.special_start_logic
        self.char = None
        self.buff_0 = None
        self.sub_exist_buff_dict = None

    def special_start_logic(self):
        """
        展旗发动时，应该检索当前角色的面板攻击力。
        """
        if self.char is None:
            self.char = JudgeTools.find_char_from_CID(1131)
        if self.sub_exist_buff_dict is None:
            all_name_order_box = JudgeTools.find_load_data().all_name_order_box
            next_char = all_name_order_box['苍角'][1]
            self.sub_exist_buff_dict = JudgeTools.find_exist_buff_dict()[next_char]
        if self.buff_0 is None:
            self.buff_0 = self.sub_exist_buff_dict['Buff-角色-苍角-核心被动-1']
        atk_now = self.char.statement.ATK
        count = min(atk_now * 0.2, 500)
        tick_now = JudgeTools.find_tick()
        self.buff_instance.simple_start(tick_now, self.sub_exist_buff_dict)
        self.buff_instance.dy.count = count
        self.buff_instance.update_to_buff_0(self.buff_0)




