import json

from Buff.BuffAdd import buff_add
from Buff.BuffExist_Judge import buff_exist_judge
from Buff.BuffLoad import BuffLoadLoop
from Report import report_to_log
from define import EFFECT_FILE_PATH

with open('./config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
debug = config.get('debug')


# 这个index列表里面装的是乘区类型中所有的项目,也是buff效果作用的范围.
# 这个列表中的内容:在Buff效果.csv 中作为索引存在;而在 Event父类中,它们又包含了 info子类的部分内容 和 multiplication子类的全部内容,
# 在文件中,这个list被用在最后的buffchagne()函数中,作为中转字典的keylist存在
# 在重构本程序的过程中,我思考过是否要把这个巨大的indexlist按照乘区划分拆成若干,这意味着Event中的Multi子类或许可以独立出来成为一个单独的父类存在.
# 这样做的好处是:庞大复杂的Multi可以不用蜗居在Event下,结构更加清晰.但是坏处就是,Event和Multi必须1对1实例化,否则容易出现多个动作共用同一份乘区实例的情况,就很容易发生错误NTR(bushi


class Buff:
    """
    config字典的键值来自：触发判断.csv
    judge_config字典的键值来自：激活判断.csv
    """

    def __init__(self, config, judge_config):
        self.ft = self.BuffFeature(config)
        self.dy = self.BuffDynamic()
        self.sjc = self.BuffSimpleJudgeCondition(judge_config)
        self.logic = self.BuffLogic()
        self.history = self.BuffHistory()
        self.effect_dct = self.__lookup_buff_effect(self.ft.index)

    class BuffFeature:
        def __init__(self, config):
            self.simple_judge_logic = config['simple_judge_logic']  # 复杂判断逻辑,指的是buff在判断阶段(装载到Loading self dict的步骤中的复杂逻辑)
            self.simple_start_logic = config[
                'simple_start_logic']  # 复杂开始逻辑,指的是buff在触发后的初始化阶段,并不能按照csv的规则来简单初始化的,比如,buff最大持续时间不确定的,buff的起始层数不确定的等等
            self.simple_end_logic = config[
                'simple_end_logic']  # 复杂结束逻辑,指的是buff的结束不以常规buff的结束条件为约束的,比如消耗完层数才消失的,比如受击导致持续时间发生跳变的,
            self.simple_effect = config['simple_effect']  # 复杂效果逻辑,指的是buff的效果无法用常规的csv来记录的,比如随机增加攻击力的,或者其他的复杂buff效果;
            self.index = config['BuffName']  # buff的英文名,也是buff的索引
            self.is_weapon = config['is_weapon']  # buff是否是武器特效
            self.refinement = config['refinement']  # 武器特效的精炼等级
            self.bufffrom = config['from']  # buff的来源,可以是角色名,也可以是其他,这个字段用来和配置文件比对,比对成功则证明这个buff是可以触发的;
            self.name = config['name']  # buff的中文名字,包括一些buff效果的拆分,这里的中文名写的会比较细
            self.exist = config['exist']  # buff是否参与了计算,即是否允许被激活
            self.durationtype = config['durationtype']  # buff的持续时间类型,如果是True,就是有持续时间的,如果是False,就没有持续时间类型,属于瞬时buff.
            self.maxduration = config['maxduration']  # buff最大持续时间
            self.maxcount = config['maxcount']  # buff允许被叠加的最大层数
            self.step = config['incrementalstep']  # buff的自增步长,也可以理解为叠层事件发生时的叠层效率.
            self.prejudge = config['prejudge']  # buff的抬手判定类型,True是攻击抬手时会产生判定；False则是不会产生判定
            self.endjudge = config['endjudge']  # buff的结束判定类型，True是攻击或动作结束时会产生判定，False则不会产生判定。
            self.fresh = config['freshtype']  # buff的刷新类型,True是刷新层数时,刷新时间,False是刷新层数是,不影响时间.
            self.alltime = config['alltime']  # buff的永远生效类型,True是无条件永远生效,False是有条件
            self.hitincrease = config['hitincrease']  # buff的层数增长类型,True就增长层数 = 命中次数,而False是增长层数为固定值,取决于step数据;
            self.cd = config['increaseCD']  # buff的叠层内置CD
            self.add_buff_to = config['add_buff_to']  # 记录了buff会被添加给谁?
            self.is_debuff = config['is_debuff'] # 记录了这个buff是否是个debuff

    class BuffDynamic:
        def __init__(self):
            self.exist = False  # buff是否参与了计算,即是否允许被激活
            self.active = False  # buff当前的激活状态
            self.count = 0  # buff当前层数
            self.ready = True  # buff的可叠层状态,如果是True,就意味着是内置CD结束了,可以叠层,如果不是True,就不能叠层.
            self.startticks = 0  # buff上一次触发的时间(tick)
            self.endticks = 0  # buff计划课中,buff的结束时间
            self.settle_times = 0  # buff目前已经被结算过的次数
            self.buff_from = None   # debuff的专用属性，用于记录debuff的来源。

    class BuffLogic:
        def __init__(self):
            self.xstart = None
            self.xeffect = None
            self.xend = None
            self.xjudge = None

    class BuffSimpleJudgeCondition:
        def __init__(self, judgeconfig):
            self.id = judgeconfig['id']
            self.oname = judgeconfig['OfficialName']
            self.sp = judgeconfig['SpConsumption']
            self.spr = judgeconfig['SpRecovery_hit']
            self.fev = judgeconfig['FeverRecovery']
            self.eaa = judgeconfig['ElementAbnormalAccumlation']
            self.st = judgeconfig['SkillType']
            self.tbl = judgeconfig['TriggerBuffLevel']
            self.et = judgeconfig['ElementType']
            self.tc = judgeconfig['TimeCost']
            self.hn = judgeconfig['HitNumber']
            self.da = judgeconfig['DmgRelated_Attributes']
            self.sa = judgeconfig['StunRelated_Attributes']

    class BuffHistory:
        def __init__(self):
            """
            History是Buff的一个子类,主要记录了buff的触发历史,\n
            包括buff的上次结束时间,上次持续时间,激活次数以及结束次数.\n
            """
            self.last_end = 0  # buff上一次结束的时间
            self.active_times = 0  # buff迄今为止激活过的次数
            self.last_duration = 0  # buff上一次的持续时间
            self.end_times = 0  # buff结束过的次数

    @staticmethod
    def __lookup_buff_effect(index: str) -> dict:
        """
        根据索引获取buff效果字典。

        该方法从json文件中尝试读取所有buff效果数据
        找到后，将数据转换为字典并返回。

        参数:
        - index: buff索引。

        返回:
        - buff_effect: 包含buff效果的字典。
        """
        # 初始化一个空的字典来存储buff效果
        # 读取包含所有buff效果的CSV文件
        with open (EFFECT_FILE_PATH, 'r', encoding='utf-8') as f:
            all_buff_js = json.load(f)
        try:
            buff = all_buff_js[index]
        except KeyError as e:
            buff = {}
            report_to_log(f'[WARNING] {e}: 索引{index}没有找到，或buff效果json结构错误', level=4)
        return buff

    def ready_judge(self, timenow):
        """
        用来判断内置CD是否就绪
        """
        if not self.dy.ready:
            if timenow - self.dy.startticks >= self.ft.cd:
                self.dy.ready = True

    def end(self, timenow, exist_buff_dict: dict):
        """
        用来执行buff的结束
        """
        buff_0 = exist_buff_dict[self.ft.index]
        # buff_0就是buff的源头。位于exsist_buff_dict中。
        if not isinstance(buff_0, Buff):
            raise TypeError(f"{buff_0}不是Buff类！")
        # 在修改buff的状态时，对buff_0进行相同的修改。以保证状态同步。
        self.dy.active = False
        self.dy.count = 0
        buff_0.dy.active = False
        buff_0.dy.count = 0
        # 同时，更新buff_0的触发历史记录。
        buff_0.history.last_end = timenow
        buff_0.history.end_times += 1
        buff_0.history.last_duration = max(timenow - self.dy.startticks, 0)
        # 再把当前buff的实例化的history和buff源对齐
        self.history.last_end = buff_0.history.last_end
        self.history.end_times = buff_0.history.end_times
        self.history.last_duration = buff_0.history.last_duration
        # report_to_log(
        #     f'[Buff INFO]:{timenow}:{self.ft.name}第{buff_0.history.end_times}次结束;duration:{buff_0.history.last_duration}', level=3)

    def update(self, char_name: str, timenow, timecost, sub_exist_buff_dict: dict, sub_mission: str):
        if self.ft.index not in sub_exist_buff_dict:
            raise TypeError(f'{self.ft.index}并不存在于{char_name}的exist_buff_dict中！')
        buff_0 = sub_exist_buff_dict[self.ft.index]
        if buff_0.dy.active:
            self.dy.startticks = buff_0.dy.startticks
            self.dy.endticks = buff_0.dy.endticks
            self.dy.count = buff_0.dy.count
            self.dy.active = buff_0.dy.active
        if not isinstance(buff_0, Buff):
            raise TypeError(f'{buff_0}不是Buff类！')
        self.dy.active = True
        buff_0.dy.active = True
        buff_0.ready_judge(timenow)
        if not buff_0.dy.ready:
            # report_to_log(f"[Buff INFO]:{timenow}:{buff_0.ft.name}内置CD没就绪，并未成功触发", level=3)
            return
        if sub_mission == 'start':
            self.update_cause_start(timenow, timecost, sub_exist_buff_dict)
        elif sub_mission == 'end':
            if self.ft.endjudge:
                self.update_cause_end(timenow, sub_exist_buff_dict)
            else:
                self.end(timenow, sub_exist_buff_dict)
        elif sub_mission == 'hit':
            self.update_cause_hit(timenow, sub_exist_buff_dict)

    def update_to_buff_0(self, buff_0):
        """
        该方法往往衔接在buff更新后使用。
        由于在buff判定逻辑中，buff的层数、时间的刷新被视为重新激活了一个新的buff，
        所以，这个方法需要向exist_buff_dict中的buff源头，也就是buff_0传递一些当前buff的参数
        """
        if not isinstance(buff_0, Buff):
            raise TypeError(f'{buff_0}不是Buff类！')
        buff_0.dy.ready = self.dy.ready
        buff_0.dy.count = self.dy.count
        buff_0.dy.startticks = self.dy.startticks
        buff_0.dy.endticks = self.dy.endticks
        buff_0.history.active_times += 1
        # report_to_log(f'[Buff INFO]:{timenow}:{buff_0.ft.index}第{buff_0.history.active_times}次触发')

    def update_cause_start(self, timenow, timecost, exist_buff_dict: dict):
        buff_0 = exist_buff_dict[self.ft.index]
        if not isinstance(buff_0, Buff):
            raise TypeError(f'{buff_0}不是Buff类！')
        if self.ft.maxduration == 0:
            if not self.ft.hitincrease:
                # 所有瞬时buff中，非命中触发的那部分，绕开了“强化E伤害提高5%，且每命中一次再提高5%”这类buff
                self.dy.startticks = timenow
                self.dy.endticks = timenow + timecost
                if not self.ft.hitincrease:
                    self.dy.count = min(buff_0.dy.count + self.ft.step, self.ft.maxcount)
                self.dy.ready = False
                self.update_to_buff_0(buff_0)
        else:
            if self.ft.prejudge:
                # 所有具有持续时间的buff中，只有抬手就触发的这一类，会在start标签处更新。
                self.dy.startticks = timenow
                self.dy.endticks = timenow + self.ft.maxduration
                if not self.ft.hitincrease:
                    self.dy.count = min(buff_0.dy.count + self.ft.step, self.ft.maxcount)
                self.dy.ready = False
                self.update_to_buff_0(buff_0)
                # 这一类buff的层数计算往往非常直接，就是当前层数 + 步长；
                # 当前层数应该从buff_0处获取（通用步骤，其他类型的层数更新也是这个流程），
        # report_to_log(f"[Buff INFO]:{timenow}:{buff_0.ft.index}第{buff_0.history.active_times}次触发", level=3)

    def update_cause_end(self, timenow, exist_buff_dict):
        buff_0 = exist_buff_dict[self.ft.index]
        if not isinstance(buff_0, Buff):
            raise TypeError(f'{buff_0}不是Buff类！')
        # 指那些“强化E动作结束后，伤害增加X%”的buff,
        # 至于buff.end()并非在这个环节做出修改，而是应该在主循环开头，遍历DynamicBuffList的时候进行修改。
        if self.ft.endjudge:
            self.dy.startticks = timenow
            self.dy.endticks = timenow + self.ft.maxduration
            self.dy.count = min(buff_0.dy.count + self.ft.step, self.ft.maxcount)
            self.dy.ready = False
            self.update_to_buff_0(buff_0)
        # report_to_log(f"[Buff INFO]:{timenow}:{buff_0.ft.index}第{buff_0.history.active_times}次触发", level=3)

    def update_cause_hit(self, timenow, exist_buff_dict: dict):
        buff_0 = exist_buff_dict[self.ft.index]
        if not isinstance(buff_0, Buff):
            raise TypeError(f'{buff_0}不是Buff类！')

        if self.ft.hitincrease:
            # 处理非瞬时且可更新的buff（fresh = True 且 maxduration != 0）
            if self.ft.fresh:
                self.dy.startticks = timenow
                self.dy.endticks = timenow + self.ft.maxduration if self.ft.maxduration != 0 else buff_0.dy.endticks
            # 处理其他buff逻辑（fresh = False 或瞬时 buff）
            self.dy.count = min(buff_0.dy.count + self.ft.step, self.ft.maxcount)
            self.dy.ready = False
            self.update_to_buff_0(buff_0)
        # report_to_log(f"[Buff INFO]:{timenow}:{buff_0.ft.index}第{buff_0.history.active_times}次触发", level=3)



