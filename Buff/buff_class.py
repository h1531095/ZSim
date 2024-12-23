import json
import importlib
from functools import lru_cache
import numpy as np
from Report import report_to_log
from define import EFFECT_FILE_PATH
import importlib.util
import pandas as pd

with open('./config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)
debug = config.get('debug')
use_cache = False
# 如果禁用缓存，每次都创建新的实例

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
    _instance_cache = {}
    _max_cache_size = 256

    def __new__(cls, config: dict = None, judge_config: dict = None):
        if not use_cache:
            return super(Buff, cls).__new__(cls)
        # 如果是深拷贝操作，直接返回已有实例
        if config is None and judge_config is None:
            return super(Buff, cls).__new__(cls)

        # 将配置字典转换为 hashable，以便用作缓存的键
        cache_key = hash((tuple(sorted(config.items())), tuple(sorted(judge_config.items()))))

        # 检查缓存中是否存在相同的实例
        if cache_key in cls._instance_cache:
            return cls._instance_cache[cache_key]

        # 检查缓存溢出例
        if len(cls._instance_cache) >= cls._max_cache_size:
            # 移除最旧的实例
            cls._instance_cache.popitem()

        # 如果不存在，则创建新实例
        instance = super(Buff, cls).__new__(cls)
        cls._instance_cache[cache_key] = instance
        return instance

    @staticmethod
    def create_new_from_existing(existing_instance):
        """
        通过复制已有实例的状态来创建新实例
        该方法主要用于BuffAddStrategy函数。
        """
        new_instance = Buff.__new__(Buff)  # 不调用构造函数
        new_instance.__dict__ = existing_instance.__dict__.copy()  # 复制原实例的属性
        return new_instance

    def __init__(self, config: pd.Series, judge_config: pd.Series):
        if not hasattr(self, 'ft'):
            self.ft = self.BuffFeature(config)
            self.dy = self.BuffDynamic()
            self.sjc = self.BuffSimpleJudgeCondition(judge_config)
            self.logic = self.BuffLogic(self)
            self.history = self.BuffHistory()
            self.effect_dct = self.__lookup_buff_effect(self.ft.index)
        else:
            self.history.active_times += 1
    # 调用特殊的逻辑加载函数
        self.buff_config = self.load_config()
        self.load_special_judge_config()

    def load_config(self):
        """
        加载 Buff 配置文件
        """
        with open('./Buff/buff_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_special_judge_config(self):
        """
        根据Buff的特性选择是否加载特殊的逻辑模块。
        动态加载适应于当前Buff实例的复杂逻辑模块。
        """
        try:
            index = self.ft.index
            config = self.buff_config.get(index)
            if config:
                module_name = config["module"]
                class_name = config["class"]
                # 动态加载模块
                module = importlib.import_module(module_name, package='Buff')
                logic_class = getattr(module, class_name)
                self.logic = logic_class(self)
            else:
                # 默认逻辑
                pass
        except ModuleNotFoundError:
            # 处理模块找不到的情况
            print(f"Module for {self.ft.index} not found. Falling back to default logic.")
            pass

    class BuffFeature:
        bf_instance_cache = {}
        max_cache_size = 256

        def __new__(cls, config):
            cache_key = hash(tuple(sorted(config.items())))
            if cache_key in cls.bf_instance_cache:
                return cls.bf_instance_cache[cache_key]
            instance = super(Buff.BuffFeature, cls).__new__(cls)

            if len(cls.bf_instance_cache) >= cls.max_cache_size:
                cls.bf_instance_cache.popitem()

            cls.bf_instance_cache[cache_key] = instance
            return instance

        def __init__(self, config):
            if not hasattr(self, 'name'):
                self.simple_judge_logic = config['simple_judge_logic']  # 复杂判断逻辑,
                self.simple_start_logic = config[
                    'simple_start_logic']  # 复杂开始逻辑,指的是buff的start方式比较特殊，需要代码控制
                self.simple_end_logic = config[
                    'simple_end_logic']  # 复杂结束逻辑,指的是buff的结束不以常规buff的结束条件为约束的,比如消耗完层数才消失的,比如受击导致持续时间发生跳变的,
                self.simple_hit_logic = config['simple_hit_logic']  # 复杂的命中判定逻辑
                self.simple_effect_logic = config['simple_effect_logic']     # 复杂的生效逻辑，和simple_start对应
                """
                注意，此处的xeffect往往与xjudge进行配合。因为xjudge会导致buff在BuffLoad函数中进入else分支，
                如果某buff既有复杂的judge_logic，又有复杂的start/hit/end_logic，
                那么后者就应该使用xeffect来写，要不然就会进入simple_start分支而导致代码块无法执行。
                """
                self.simple_exit_logic = config['simple_exit_logic']    # 复杂退出逻辑
                self.index = config['BuffName']  # buff的英文名,也是buff的索引
                self.is_weapon = config['is_weapon']  # buff是否是武器特效
                self.refinement = config['refinement']  # 武器特效的精炼等级
                self.bufffrom = config['from']  # buff的来源,可以是角色名,也可以是其他,这个字段用来和配置文件比对,比对成功则证明这个buff是可以触发的;
                self.description = config['description']  # buff的中文名字,包括一些buff效果的拆分,这里的中文名写的会比较细
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
                self.schedule_judge = config['schedule_judge']  # 记录了这个buff是否需要在schedule阶段处理。
                self.backend_acitve = config['backend_acitve']  # 记录了这个buff是否需要在后台才能触发

                self.individual_settled = config['individual_settled']    # 记录了这个buff的叠层是否是独立结算
                """
                在20241116的更新中，更新了新的buff结算逻辑，针对“层数独立结算”的buff，
                在BuffFeature下新增了一个参数：individual_settled
                buff在更新或者新建实例时，应该检测该参数是否为True，
                如果是True，则应该检索当前DYNAMIC_BUFF_DICT中的buff是否存在，
                如果存在，则应该直接更新self.dy.built_in_buff_box。
                """
                self.operator = config.get('operator', None)
                self.passively_updating = config.get('passively_updating', None)
                """
                在20241130的更新中，新增了passively_updating这一参数。
                在初始化阶段、生成exist_buff_dict以及一众buff_0时，
                会根据对应的添加逻辑，修改这一参数。这一参数可以标志出该buff是否应该由当前角色的行为触发。
                这样就可以避免“艾莲的强化E会意外触发苍角核心被动的攻击力buff”
                """

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
            self.built_in_buff_box = []    # 如果self.ft.single_deal是True，则需要创建这个list。
            """
            在20241117的更新中，我们新增了built_in_buff_box属性，该属性需要和self.ft.individual_settled进行配合。
            如果该参数为True，则在单独结算Buff时，将buff的startticks和endticks以[start，end]的格式存入列表，然后写入这个box。
            """
            self.is_changed = False
            """
            在20241115的更新中，新增了buff.dy.is_change属性。
            该字段记录了当前buff是否已经成功被变更属性。通过该字段就可以区分进入update函数的buff是否真实地改变了数据，
            而update_to_buff_0的函数也需要严格根据这个参数的情况来执行。
            这能够避免某些本应在hit处更新的buff，于start处执行了update函数，被分入start分支后，
            该buff虽然没有改变属性，但是无条件执行了update_to_buff_0，
            从而污染了源头数据。导致部分叠层、以及其他属性变更出现问题。
            """

    class BuffLogic:
        """
        这是记录所有的复杂逻辑的子类。由于所有的复杂逻辑的调用，都必须从BuffLoadLoop开始。
        所以，再复杂的Buff也需要在CSV数据库中输入对应的index以及其他基本属性，使其能够顺利进入BuffLoadLoop。
        而真正调用Xlogic模块的地方实际上有两个。Xjudge会在BuffLoadLoop中调用的BuffJudge函数的一个分支中被执行，最终抛出的是布尔值。
        第二处则是在Buff.update()函数。为了保证所有的Xlogic都有方式被正确调用，所以，我将复杂的触发逻辑分为了Start、Hit和End三类。
        它们会在各自的分支中被调用。
        """
        def __init__(self, buff_instance):
            self.buff = buff_instance
            self.xjudge = None  # 判断逻辑
            self.xstart = None  # 复杂的开始逻辑
            self.xhit = None  # 复杂的命中更新逻辑
            self.xend = None  # 结束逻辑
            self.xeffect = None     # 生效逻辑
            self.xexit = None  # 退出逻辑

        def special_judge_logic(self):
            pass

        def special_start_logic(self):
            # 这里可以实现特定的开始逻辑
            pass

        def special_hit_logic(self):
            # 这里可以实现特定的命中逻辑
            pass

        def special_end_logic(self):
            # 这里可以实现特定的结束逻辑
            pass

        def special_effect_logic(self):
            pass

        def special_exit_logic(self):
            pass

    class BuffSimpleJudgeCondition:

        sjc_instance_cache = {}
        max_size = 128

        def __new__(cls, judgeconfig):
            cache_key = hash(tuple(sorted(judgeconfig.items())))
            if cache_key in cls.sjc_instance_cache:
                return cls.sjc_instance_cache[cache_key]
            instance = object.__new__(cls)

            if len(cls.sjc_instance_cache) >= cls.max_size:
                cls.sjc_instance_cache.popitem()

            cls.sjc_instance_cache[cache_key] = instance
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
            self.real_count = 0  # 莱特组队被动专用的字段，用于记录实层。

    def get_my_count(self):
        """
        获取层数现在要用这个层数了，不能直接获取self.dy.count了
        """
        if self.ft.individual_settled:
            count = len(self.dy.built_in_buff_box)
        else:
            count = self.dy.count
        return count

    def __lookup_buff_effect(self, index: str) -> dict:
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
        all_buff_js = self.__convert_buff_js(EFFECT_FILE_PATH)
        try:
            buff = all_buff_js[index]
        except KeyError as e:
            buff = {}
            report_to_log(f'[WARNING] {e}: 索引{index}没有找到，或buff效果json结构错误', level=4)
        return buff

    @staticmethod
    @lru_cache(maxsize=64)
    def __convert_buff_js(csv_file):
        df = pd.read_csv(csv_file)
        width = int(np.ceil(df.shape[1] / 2))
        # 初始化结果字典
        result = {}
        # 遍历 DataFrame 的每一行
        for index, row in df.iterrows():
            name = row['名称']
            value = {}
            # 处理 key-value 对
            for i in range(1, width):
                try:
                    key = row[f'key{i}']
                    val = row[f'value{i}']
                    if pd.notna(key) and pd.notna(val):
                        value[key] = float(val)
                except KeyError:
                    continue
            result[name] = value
        return result

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
        self.dy.built_in_buff_box = []
        buff_0.dy.active = False
        buff_0.dy.count = 0
        # 同时，更新buff_0的触发历史记录。
        buff_0.history.last_end = timenow
        buff_0.history.end_times += 1
        buff_0.history.last_duration = max(timenow - self.dy.startticks, 0)
        buff_0.dy.built_in_buff_box = []
        # 再把当前buff的实例化的history和buff源对齐
        self.history.last_end = buff_0.history.last_end
        self.history.end_times = buff_0.history.end_times
        self.history.last_duration = buff_0.history.last_duration
        # report_to_log(
        #     f'[Buff INFO]:{timenow}:{self.ft.name}第{buff_0.history.end_times}次结束;duration:{buff_0.history.last_duration}', level=3)

    def simple_start(self, timenow: int, sub_exist_buff_dict: dict):
        """
        sub_exist_buff_dict = exist_buff_dict[角色名]
        角色名指的是当前的前台角色。
        该方法是buff的默认激活方法。它会以最常见的策略激活buff。
        让buff具有最基本的start、end两个时间点，以及最基本的层数，
        并且更新好Buff的内置CD，最后将所有的信息改动回传给buff0
        """
        buff_0 = sub_exist_buff_dict[self.ft.index]
        self.dy.active = True
        self.dy.startticks = timenow
        self.dy.endticks = timenow + self.ft.maxduration
        self.dy.count = min(buff_0.dy.count + self.ft.step, self.ft.maxcount)
        if self.ft.individual_settled:
            self.dy.built_in_buff_box.append((self.dy.startticks, self.dy.endticks))
        self.update_to_buff_0(buff_0)

    def individual_setteled_update(self, duration, timenow):
        """
        各层数单独结算类的buff的更新函数
        会首先检查内置的box的容量情况，如果box满了会先进行pop(0)，然后append
        最后，更新自身的count
        """
        start = timenow
        end = timenow + duration
        if len(self.dy.built_in_buff_box) == self.ft.maxcount:
            if len(self.dy.built_in_buff_box) > self.ft.maxcount:
                # 溢出报错
                raise ValueError(f'box的当前大小是{len(self.dy.built_in_buff_box)}，超过了最大容量{self.ft.index}')
            # 说明此时box的含量已经满了，所以把最老的pop出来。
            self.dy.built_in_buff_box.pop(0)
        # 不管是否pop，都需要append
        self.dy.built_in_buff_box.append((start, end))
        self.dy.count = len(self.dy.built_in_buff_box)
        self.dy.endticks = end
        self.dy.active = True
        self.dy.ready = False
        self.dy.is_changed = True

    def update(self, char_name: str, timenow, timecost, sub_exist_buff_dict: dict, sub_mission: str):
        """
        该函数只负责buff的时间更新。buff该不该进行更新，并不是该函数的负责范围。
        往往是在外部函数判断出某个buff需要触发后（通常是新建一个Buff实例）
        根据Buff的更新特性（比如fresh、Prejudge等参数）以及对应正在发生的子任务节点，对应的处理buff的dynamic属性。
        """
        if self.ft.index not in sub_exist_buff_dict:
            raise TypeError(f'{self.ft.index}并不存在于{char_name}的exist_buff_dict中！')
        buff_0 = sub_exist_buff_dict[self.ft.index]
        if self.ft.alltime:
            self.dy.active = True
            self.dy.count = 1
            self.dy.is_changed = True
            self.dy.startticks = timenow
            self.update_to_buff_0(buff_0)
            return
        if buff_0.dy.active:
            """
            如果update函数运行时，检测到Buff0已经active，则意味着我们需要更新一个已经被激活的buff。
            首先，应该将自身的主要数据与Buff0对齐，这是前提条件。这所有的东西主要是为了叠层服务的。
            当然那，不用担心这一步会污染startticks和endticks，因为后面该对这两个东西做出改动的函数，都会改动它们。
            不该做出改动的，那自然不需要改，也是符合需求的。
            """
            self.dy.startticks = buff_0.dy.startticks
            self.dy.endticks = buff_0.dy.endticks
            self.dy.count = buff_0.dy.count
            self.dy.active = buff_0.dy.active
            self.dy.built_in_buff_box = buff_0.dy.built_in_buff_box
        if not isinstance(buff_0, Buff):
            raise TypeError(f'{buff_0}不是Buff类！')
        buff_0.ready_judge(timenow)
        if not buff_0.dy.ready:
            report_to_log(f"[Buff INFO]:{timenow}:{buff_0.ft.description}内置CD没就绪，并未成功触发", level=3)
            return
        """
        在执行所有分支之前，自然要判断buff的就绪情况。如果Buff没有就绪，那么一切都是白扯。
        因为self自身是刚刚实例化的Buff，肯定是新鲜的，所以，ready的判断要去exist buff dict中的buff0执行，
        那里记录着buff的最新情况。
        ready检测不通过直接return——cd没转好，所以就算能够触发，也是不会触发的。
        """
        if sub_mission == 'start':
            self.update_cause_start(timenow, timecost, sub_exist_buff_dict)
        elif sub_mission == 'end':
            if self.ft.endjudge:
                self.update_cause_end(timenow, sub_exist_buff_dict)
        elif sub_mission == 'hit':
            self.update_cause_hit(timenow, sub_exist_buff_dict, timecost)

    def update_to_buff_0(self, buff_0):
        """
        该方法往往衔接在buff更新后使用。
        由于在buff判定逻辑中，buff的层数、时间的刷新被视为重新激活了一个新的buff，
        所以，这个方法需要向exist_buff_dict中的buff源头，也就是buff_0传递一些当前buff的参数
        """
        if not isinstance(buff_0, Buff):
            raise TypeError(f'{buff_0}不是Buff类！')
        buff_0.dy.active = self.dy.active
        buff_0.dy.ready = self.dy.ready
        buff_0.dy.count = self.dy.count
        buff_0.dy.startticks = self.dy.startticks
        buff_0.dy.endticks = self.dy.endticks
        buff_0.dy.built_in_buff_box = self.dy.built_in_buff_box
        buff_0.history.active_times += 1
        # report_to_log(f'[Buff INFO]:{timenow}:{buff_0.ft.index}第{buff_0.history.active_times}次触发')

    def update_cause_start(self, timenow, timecost, exist_buff_dict: dict):
        buff_0 = exist_buff_dict[self.ft.index]
        if not isinstance(buff_0, Buff):
            raise TypeError(f'{buff_0}不是Buff类！')
        if not self.ft.simple_start_logic:
            # EXAMPLE：Buff触发时，随机获得层数。
            self.logic.xstart()
            self.dy.is_changed = True
            if self.dy.is_changed:
                self.update_to_buff_0(buff_0)
        if self.ft.maxduration == 0:    # 瞬时buff
            if not self.ft.hitincrease:     # 命中不叠层
                """
                所有瞬时buff（maxduration=0）中，非命中触发的那部分，
                本质上是把瞬时buff看做是一个持续时间为招式持续时间的buff。
                所有的“普攻伤害增加”类型的Buff，都是这个逻辑处理的。在出招时候（start）就已经加上了，而在End之后自动结束。
                确保该招式内的所有Hit都能享受到加成。
                但是，这个函数处理不了在招式内叠层的Buff，在逻辑上绕开了“强化E伤害提高5%，且每命中一次再提高5%”这类buff
                就以这个Buff例子为例，这个Buff是Hit事件才会触发的，在Start函数中应该毫无作为，所以必须绕开。
                """
                self.dy.active = True
                if self.ft.individual_settled:
                    """
                    单独结算的Buff处理逻辑。
                    """
                    # EXAMPLE：发动普攻时，使当前招式伤害增加X%，每层效果独立结算。
                    self.individual_setteled_update(timecost, timenow)
                else:
                    # EXAMPLE：发动普攻时，使当前招式伤害增加X%，
                    self.dy.startticks = timenow
                    self.dy.endticks = timenow + timecost
                    self.dy.count = min(buff_0.dy.count + self.ft.step, self.ft.maxcount)
                    self.dy.ready = False
                    self.dy.is_changed = True
        else:
            if self.ft.prejudge:
                """
                所有具有持续时间的buff中，只有抬手就触发的这一类，会在start标签处更新。
                再次强调：但凡是Hit触发的buff，在start标签处都不会做任何改变。
                并且，本质上prejudge和hit_increase两个参数在数据库中就是互斥的，
                除非，某个Buff在技能抬手就触发，同时还会因为命中而叠层（那也太傻逼了，虽然我觉得这不远了。到时候出问题了记得踢我。）
                """
                # FIXME：某个Buff在技能抬手就触发，同时还会因为命中而叠层 的逻辑等待拓展
                if self.ft.individual_settled:
                    # EXAMPLE：发动普攻时，使攻击力提升，每次触发独立结算持续时间。
                    self.individual_setteled_update(self.ft.maxduration, timenow)
                else:
                    # EXAMPLE：发动普攻时，使攻击力提升，重复触发刷新持续时间
                    self.dy.active = True
                    self.dy.startticks = timenow
                    self.dy.endticks = timenow + self.ft.maxduration
                    if not self.ft.hitincrease:
                        self.dy.count = min(buff_0.dy.count + self.ft.step, self.ft.maxcount)
                    self.dy.ready = False
                    self.dy.is_changed = True
                    """ 
                    所有因start标签而更新的buff，它们的底层逻辑往往和Hit更新互斥，
                    它们的层数计算往往非常直接，就是当前层数 + 步长；
                    而想要做到所谓的“层数叠加了”，那么当前层数应该从buff_0处获取（这是通用步骤，其他类型的层数更新也是这个流程）
                    总体层数又被min函数掐死，不用担心移除。
                    """
        if self.dy.is_changed:
            self.update_to_buff_0(buff_0)

        # report_to_log(f"[Buff INFO]:{timenow}:{buff_0.ft.index}第{buff_0.history.active_times}次触发", level=3)

    def update_cause_end(self, timenow, exist_buff_dict):
        """
        这个函数一般不会用到，因为不会有动作结束才触发的傻逼buff逻辑。
        “艾莲踩了你一脚，你当场不敢发作但是等艾莲转身离开，你触发硬度+3，持续30秒？
        还是那句话，因动作结束而触发的Buff就是傻逼，好在这里不需要判断是不是Prejudge了。
        """
        buff_0 = exist_buff_dict[self.ft.index]
        if self.ft.simple_end_logic:
            if not isinstance(buff_0, Buff):
                raise TypeError(f'{buff_0}不是Buff类！')
            # 至于buff.end()并非在这个环节做出修改，而是应该在主循环开头，遍历DynamicBuffList的时候进行修改。
            if self.ft.endjudge:
                if self.ft.individual_settled:
                    self.individual_setteled_update(self.ft.maxduration, timenow)
                else:
                    # EXAMPLE：普攻结束后，伤害增加X%，重复触发刷新持续时间。
                    self.dy.active = True
                    self.dy.startticks = timenow
                    self.dy.endticks = timenow + self.ft.maxduration
                    self.dy.count = min(buff_0.dy.count + self.ft.step, self.ft.maxcount)
                    self.dy.ready = False
                    self.dy.is_changed = True
            # report_to_log(f"[Buff INFO]:{timenow}:{buff_0.ft.index}第{buff_0.history.active_times}次触发", level=3)
        else:
            # EXAMPLE：普攻结束后，随机获得1~10层的攻击力Buff。
            self.logic.xend()
            self.dy.is_changed = True
        if self.dy.is_changed:
            self.update_to_buff_0(buff_0)

    def update_cause_hit(self, timenow, exist_buff_dict: dict, timecost):
        """
        这里是最常用的代码，大部分的buff都是hit标签更新。
        当然，第一层就要过hitincrease筛选，但凡不满足的，我hit一万次你也触发不了。
        然后就是那些沟槽的 重复触发但不刷新时间的buff（fresh == False）
        在处理这些Buff的时候必须忍住不要更新startticks，要不然就全丸辣！
        """
        buff_0 = exist_buff_dict[self.ft.index]
        if not isinstance(buff_0, Buff):
            raise TypeError(f'{buff_0}不是Buff类！')
        if not buff_0.dy.active:
            # 新触发的buff
            if buff_0.ft.maxduration == 0:
                endticks = timenow + timecost
            else:
                endticks = timenow + buff_0.ft.maxduration
        else:
            # 已经触发了buff
            endticks = self.dy.endticks
        if not self.ft.simple_hit_logic:
            self.logic.xhit()
            self.dy.is_changed = True
            self.update_to_buff_0(buff_0)
            return
        if not self.ft.hitincrease:
            # EXPLAIN：如果hitincrease是False，则意味着在本函数内完全没有更新的可能，直接return就行。
            return
        if self.ft.fresh:       # 处理可更新的buff（fresh = True）
            # EXPLAIN：fresh参数和individual_settled是否等价？不，前者是命中时间完全不修改endticks，而后者则是独立结算机制。
            #  在判定逻辑的优先级上，fresh和individual_settled包含关系，如果fresh为FALSE，那么无论层数是否独立结算，都会表现为相同的结果。
            #  所以，只有fresh为True的buff，才有被区分是否独立结算的意义。
            if self.ft.individual_settled:
                # EXAMPLE：普攻命中时，攻击力提高3%，层数之间独立结算。
                self.individual_setteled_update(self.ft.maxduration, timenow)
                if self.ft.maxduration == 0:
                    # EXAMPLE：普攻期间命中时，攻击力提高3%，层数之间独立结算。
                    # 如果maxduration是0，那么endticks是不能变的。要还原回来。
                    self.dy.endticks = endticks
                self.dy.is_changed = True
            else:
                # EXAMPLE: 命中可叠层，且持续时间刷新。
                # EXAMPLE：所有的具有复杂判断逻辑但是光环类的Debuff会在这里被处理。
                self.dy.startticks = timenow
                """
                这里还没完呢，startticks虽然更新了，但是endticks要不要更新还得看buff是否是瞬时buff。
                瞬时buff到点结束，那就不能改变，只能照抄buff_0，
                只有非瞬时buff，才会因hit刷新了持续时间而更新endticks。
                """
                self.dy.endticks = timenow + self.ft.maxduration if self.ft.maxduration != 0 else endticks
                self.dy.count = min(buff_0.dy.count + self.ft.step, self.ft.maxcount)
        else:
            """
            处理剩下的其他buff逻辑（fresh = False 或瞬时 buff）
            这些buff都是startticks不允许更新的，endticks也是如此。
            """
            if not self.ft.individual_settled:
                # EXAMPLE：强化E持续期间，命中一次叠层一次。
                self.dy.count = min(buff_0.dy.count + self.ft.step, self.ft.maxcount)

        self.dy.ready = False
        self.dy.active = True
        self.dy.is_changed = True
    # report_to_log(f"[Buff INFO]:{timenow}:{buff_0.ft.index}第{buff_0.history.active_times}次触发", level=3)
        if self.dy.is_changed:
            self.update_to_buff_0(buff_0)

    def __str__(self) -> str:
        return f'Buff: {self.ft.description}'
