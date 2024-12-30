from Buff import Buff, JudgeTools


class SteamOven(Buff.BuffLogic):
    """
    这段代码是人为刀俎的生效逻辑。根据能量返回层数。
    由于该效果要求在能量扣除后还能继续存在8秒，且每一层效果单独结算持续时间，
    应在每次更新时，都实时检测当前能量，并更新buff.dy.built_in_buff_box中的所有list。
    更新方式不是替换，而是类似于栈。
    这里不需要管过期tuples的移除，只需要管溢出tuples的移除即可。
    注意，这个Buff的复杂判断逻辑永远是False，但是只输出True。
    不能用Alltime参数来平替，因为这样会导致在Update_Buff函数中，本Buff会提前被送出循环，而跳过清理过期tuples的步骤。
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        # 初始化特定逻辑
        self.xjudge = self.special_judge_logic
        self.xeffect = self.special_effect_logic
        self.equipper = None
        self.char = None
        self.sub_exist_buff_dict = None
        self.buff_0 = None
        self.last_update_count = 0
        self.last_update_tick = 0

    def special_judge_logic(self):
        """
        由于人为刀俎的Buff实际上是按照all_time的规格在生效的，
        但是因为要用复杂逻辑来更新它的实际层数，所以不能用alltime来粗暴处理，
        否则，在UpdateBuff阶段，这个Buff会因为all_time参数是True而被筛掉，
        从而丧失自我更新、去除过期层数的能力。
        """
        return True

    def special_effect_logic(self):
        """
        真正的逻辑模块，首先是初始化，比如找出char、找到装备使用者等；
        然后是检查当前激活情况，如果当前buff尚未被激活，那么需要用simple_start激活一下。
        然后检查能量， 确定需要循环的次数（除以10并向下取整）
        确定这一次加入的tuple子单元的两个时间点（在单次函数执行过程中所添加的子层数的tuple都是相同的）
        """
        if self.equipper is None:
            self.equipper = JudgeTools.find_equipper("人为刀俎")
        if self.char is None:
            self.char = JudgeTools.find_char_from_name(self.equipper)
        if self.sub_exist_buff_dict is None:
            exist_buff_dict = JudgeTools.find_exist_buff_dict()
            self.sub_exist_buff_dict = exist_buff_dict[self.equipper]
        if self.buff_0 is None:
            self.buff_0 = self.sub_exist_buff_dict[self.buff_instance.ft.index]
        self.buff_instance.download_from_buff_0(self.buff_0)
        self.last_update_tick = self.buff_0.history.last_update_tick
        self.last_update_count = self.buff_0.dy.count
        tick_now = JudgeTools.find_tick()
        char_energy = self.char.sp
        new_count = char_energy // 10
        """
        层数无变化 或 有增长，返回新层数，更新信息；
        层数负增长，判断时间，如果大于8秒，则用新层数，更新信息，
        否则用老层数，不更新信息。
        """
        if new_count >= self.last_update_count:
            self.buff_0.dy.count = new_count
            self.buff_0.history.last_update_tick = tick_now
            output = new_count
        else:
            if tick_now - self.last_update_tick > 480:
                self.buff_0.dy.count = new_count
                self.buff_0.history.last_update_tick = tick_now
                output = new_count
            else:
                output = self.last_update_count
        output = min(output, self.buff_instance.ft.maxcount)
        # print(new_count, output, (self.last_update_count, self.last_update_tick))
        self.buff_instance.dy.startticks = tick_now
        self.buff_instance.dy.endticks = tick_now + self.buff_instance.ft.maxduration
        self.buff_instance.dy.count = output
        self.buff_instance.dy.active = True
        self.buff_instance.dy.is_changed = True
        self.buff_instance.update_to_buff_0(self.buff_0)








