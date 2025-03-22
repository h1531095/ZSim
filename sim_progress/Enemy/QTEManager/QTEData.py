from sim_progress.data_struct import SingleHit


class QETDataUpdater:
    @classmethod
    def apply(cls, qte_data, single_qte, attr_name):
        raise NotImplemented


class SumStrategy(QETDataUpdater):
    """数值累加策略"""
    @classmethod
    def apply(cls, qte_data, single_qte, attr_name):
        single_qte_value = getattr(single_qte, attr_name, 0) or 0
        qte_data_value = getattr(qte_data, attr_name, 0) or 0
        setattr(qte_data, attr_name, single_qte_value + qte_data_value)


class ListMergeStrategy(QETDataUpdater):
    """列表合并策略"""
    @classmethod
    def apply(cls, qte_data, single_qte, attr_name):
        single_qte_value = getattr(single_qte, attr_name, []) or []
        qte_data_value = getattr(qte_data, attr_name, []) or []
        setattr(qte_data, attr_name, qte_data_value + single_qte_value)


class QTEData:
    def __init__(self, enemy_instance):
        """这个数据结构是管理怪物的QTE的总体数据的，它会随着Enemy类的初始化而一同初始化。
        其中的动态数据（比如qte_received_box qte_triggered_times等，会在每次进入失衡期之前进行重置。"""
        self.enemy_instance = enemy_instance  # 在初始化时，传入Enemy实例；
        self.qte_received_box: list[str] = []  # 用于接受QTE阶段输入的QTE skill_tag
        self.qte_triggered_times: int = 0  # 已经触发过几次QTE了
        self.qte_triggerable_times: int = enemy_instance.QTE_triggerable_times  # 最多可以触发几次QTE
        self.qte_activation_available = False  # 彩色失衡阶段
        self.single_qte = None  # 单次QTE的实例
        self.char_box = []  # 角色列表，用于在SingleQTE阶段进行角色的筛选
        self.__single_hit_check = lambda hit: all([
            hit.hitted_count == 1 or hit.heavy_attack,  # 第一跳、重击（通常为重攻击标签的最后一跳）均能通过判定，
            hit.proactive,  # 筛选出主动技能，所有的被动释放的技能都不能和QTE的激活行为进行互动。
        ])
        self.strategies_map = {
            'qte_received_box': ListMergeStrategy,
            'qte_triggered_times': SumStrategy
        }

    def _check_myself(self) -> bool:
        """该函数用于检查自身目前的状态，即当前是彩色失衡还是灰色失衡；"""
        if self.qte_triggered_times > self.qte_triggerable_times:
            raise ValueError(f'QTE的实际响应总次数为{self.qte_triggered_times}次，大于其最大次数{self.qte_triggerable_times}次！')
        if len(self.qte_received_box) > self.qte_triggered_times:
            raise ValueError(f'QTE总计包含了{len(self.qte_received_box)}个skill_tag，而实际的响应次数为{self.qte_triggered_times}次！')
        if self.qte_triggered_times < self.qte_triggerable_times:
            return True
        else:
            self.qte_activation_available = False
            return False


    def try_qte(self, hit: SingleHit):
        """
        该函数是QTEData的最外层接口，是核心调用函数。
        其核心作用为：用传入的SingleHit来尝试激发QTE。
        """
        # 0、 如果是非失衡状态或是灰色失衡状态，那么直接返回
        if not self.qte_activation_available:
            return

        # 1、可行性审查，这里，只有主动动作的第一跳、以及含有重击标签的、主动动作的最后一跳能够通过判定。
        if not self.single_hit_filter(hit):
            return


        # 2、是否存在已经激活的SingleQTE实例——连携阶段已经因重攻击而激发、SingleQTE实例也已经创建，但是尚未传入SingleHit的状态
        if self.single_qte is not None:
            if not isinstance(self.single_qte, SingleQTE):
                raise TypeError(f'QTEData的single_qte属性不是SingleQTE类！你往里放入了{type(self.single_qte)}！')
            # 2.1、尝试将已经通过可行性检查的SingleHit传入到SingleQTE中，进行数据更新，
            self.single_qte.receive_hit(hit)
        else:
            pass




    def single_hit_filter(self, hit: SingleHit):
        """
        该函数用于对传入的SingleHit进行筛选，并返回筛选结果。
        """
        return self.__single_hit_check(hit)

    def reset(self):
        """该函数用于在失衡期开始时的重置QTEdata中的动态数据"""
        self.qte_received_box = []
        self.qte_triggered_times = 0
        self.qte_activation_available = True
        self.single_qte = None

    def qte_start(self):
        """该函数用于QTE激发阶段时，构造一个single_qte 的实例"""
        pass

    def spawn_single_qte(self):
        pass


class SingleQTE:
    def __init__(self, qte_data: QTEData, active_from):
        self.qte_data = qte_data
        self.qte_received_box: list[str] = []           # 用于接受QTE阶段输入的QTE skill_t
        self.qte_triggerable_times: int = qte_data.qte_triggerable_times  # 最多可以触发几次QTE
        self.qte_activation_available = False       # 彩色失衡阶段
        if active_from not in self.qte_data.char_box:
            raise ValueError(f'激活QTE阶段的重攻击来源于{active_from}，但是该角色不存在于QTEData中！')
        self.available_char_list = [i for i in self.qte_data.char_box if i != active_from]  # 可响应本次QTE的角色
        self.__is_hitted = False             # 每个SingleHit都只会被响应一次，所以这里用一个bool变量来标记是否已经被响应过。

    def receive_hit(self, _single_hit: SingleHit):
        """SingleQTE接收SingleHit的方法"""
        if self.__is_hitted:
            raise ValueError(
                'SingleQTE实例已经响应过一次了！请检查函数逻辑，查找为何处会多次调用同一个SingleQTE的_receive_hit函数！')
        if not isinstance(_single_hit, SingleHit):
            raise TypeError( f'SingleQTE实例的_receive_hit函数被调用时，传入的single_hit参数不是SingleHit类！而是{type(_single_hit)}！')
        if _single_hit.hitted_count != 1:   # 如果传进来的不是第一跳，那直接return
            return
        self.qte_triggerable_times += 1  # 无论传进来的是哪一个hit的第一跳，都意味着响应了QTE
        if 'QTE' not in _single_hit.skill_tag:
            '''说明QTE被取消了'''
            print(f'取消QTE！')
        else:
            self.qte_received_box.append(_single_hit.skill_tag)
        self.__is_hitted = True
        self.merge_single_qte()

    def merge_single_qte(self):
        """SingleQTE向QTEData更新数据的方法"""
        for attr_name, strategy in self.qte_data.strategies_map.items():
            if hasattr(self, attr_name):
                strategy.apply(self.qte_data, self, attr_name)
        self.qte_data.single_qte = None

