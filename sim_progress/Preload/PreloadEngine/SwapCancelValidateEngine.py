import math
from .BasePreloadEngine import BasePreloadEngine
from sim_progress.Preload import SkillNode
from define import SWAP_CANCEL_MODE_COMPLETION_COEFFICIENT as SCK, SWAP_CANCEL_MODE_LAG_TIME as SCLT
# EXPLAIN：关于SCK和LT的作用：
"""
以上两个系数分别是：
①合轴操作完成度系数 SWAP_CANCEL_MODE_COMPLETION_COEFFICIENT （程序中通常引用为SCK）
②操作滞后系数 SWAP_CANCEL_MODE_LAG_TIME （程序中通常引用为SCLT），它们共同用于模拟玩家的合轴操作。
因为不可能任意操作都具有完美的完成度（在第2帧就完美切人+下一招出手），
人体机能限制、注意力不集中、可能存在的操作习惯以及其他因素，都会导致合轴操作的延后实施，
所以，这里通过设置一个系数来模拟玩家的操作滞后程度，在计算时，我会取用skill_node的时长（skill.ticks)，并且乘以SCK，
所计算出的结果与SCLT参数相比较，取较小值作为最终的滞后时间（防止较长的技能滞后严重，导致模拟失真）。
后续的升级方向：
在引入随机数生成器后，可以进一步基于两个参数的基本值，对这两个参数进行随机处理，从而真正模拟玩家在操作端的浮动。
"""


class SwapCancelValidateEngine(BasePreloadEngine):
    """该引擎的作用是：判断当前传入的APL运行结果是否满足合轴的需求"""
    def __init__(self, data):
        super().__init__(data)
        self.validators = [
            self._validate_char_avaliable,
            self._validate_swap_tick,
            self._validate_qte_activation
        ]

    @property
    def external_update_signal(self):
        return True if self.data.preload_action_list_before_confirm else False

    def run_myself(self, skill_tag: str, tick: int, **kwargs) -> bool:
        """合轴可行性分析基本分为以下几个步骤：
        1、当前涉及角色是否有空
        2、合轴时间是否符合
        3、确认合轴后，将skill_tag和主动参数 打包成tuple"""
        apl_priority = kwargs.get('apl_priority', 0)
        self.active_signal = False
        if not self._validate_char_avaliable(skill_tag=skill_tag, tick=tick):
            return False
        if not self._validate_swap_tick(skill_tag=skill_tag, tick=tick):
            return False
        if self._validate_qte_activation(tick=tick):
            return False
        self.data.preload_action_list_before_confirm.append((skill_tag, True, apl_priority))
        self.active_signal = True
        return True

    def _validate_char_avaliable(self, **kwargs) -> bool:
        """角色是否可以获取的判定"""
        skill_tag = kwargs['skill_tag']
        if skill_tag == 'wait':
            return False
        tick = kwargs['tick']
        cid = int(skill_tag.split('_')[0])
        char_stack = self.data.personal_node_stack.get(cid, None)
        if char_stack is None:
            '''角色当前没有正在发生的Node，有空'''
            return True
        char_latest_node = char_stack.peek()
        if char_latest_node is None:
            '''角色当前没有正在发生的Node，有空'''
            return True

        '''角色当前有一个正在发生的Node，没空！'''
        if char_latest_node.end_tick > tick:
            return False

        '''
        虽然角色目前有空，但是当前tick正好添加了一个Ta的动作，
        不管这个动作是主动的还是被动的，都意味着当前tick本角色没空。
        '''
        for _tuples in self.data.preload_action_list_before_confirm:
            _tag = _tuples[0]
            if cid == int(_tag.split('_')[0]):
                return False

        '''此时，角色有空，且没有强制任务，接下来要根据当前前台的技能情况来继续展开讨论'''
        node_on_field = self.data.get_on_field_node(tick)

        '''角色有空，并且当前前台技能是None，即当前skill_tag是第一个技能！'''
        if node_on_field is None:
            return True

        '''角色有空，当前前台技能是其他角色的，此时要针对切人CD和技能Tag进行检查'''
        if int(node_on_field.skill_tag.split('_')[0]) != cid:
            if tick - char_latest_node.end_tick < 60:
                '''查了一下时间，竟然是1秒内刚切下去的'''
                if 'Aid' not in skill_tag or 'QTE' not in skill_tag:
                    '''如果不是支援类和连携技这种无视切人CD的技能，那么此时角色是切不出来的'''
                    return False

        '''其他剩下的所有情况，都返回True'''
        return True

    @staticmethod
    def spawn_lag_time(node: SkillNode) -> int:
        """
        生成滞后时间，关于函数中两个参数SCK和SCLT的含义，请参考本文件开头的注释。
        这里返回的lag_time是经过向上取整的。
        """
        lag_time = math.ceil(min(node.skill.ticks * SCK, SCLT))
        return lag_time

    def _validate_swap_tick(self, **kwargs):
        """针对当前技能的合轴时间的检测"""
        skill_tag = kwargs['skill_tag']
        tick = kwargs['tick']
        current_node_on_field = self.data.get_on_field_node(tick)
        if current_node_on_field is None:
            return True
        swap_lag_tick = self.spawn_lag_time(current_node_on_field)
        if swap_lag_tick + current_node_on_field.skill.swap_cancel_ticks + current_node_on_field.preload_tick > tick:
            return False
        else:
            return True

    def _validate_qte_activation(self, **kwargs) -> bool:
        """针对当前技能的QTE是否处于激活状态的检测，当检查到有角色正在释放QTE时，返回True"""
        tick = kwargs['tick']
        for _cid, stack in self.data.personal_node_stack.items():
            if stack.peek() is None:
                continue
            node_now = stack.peek()
            if node_now.end_tick > tick:
                if "QTE" in node_now.skill_tag:
                    return True
            continue
        else:
            return False

    def check_myself(self):
        if self.data.preload_action_list_before_confirm:
            self.active_signal = True
