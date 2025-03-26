from abc import ABC, abstractmethod
from sim_progress.Preload.PreloadEngine import APLEngine, ForceAddEngine, ConfirmEngine, SwapCancelValidateEngine


class BasePreloadStrategy(ABC):
    """基础策略，无论是什么策略，都会包含 APL、强制添加技能以及最终技能确认三个引擎。"""
    def __init__(self, data):
        self.data = data
        self.apl_engine = APLEngine(data)
        self.force_add_engine = ForceAddEngine(data)
        self.confirm_engine = ConfirmEngine(data)

    @abstractmethod
    def generate_actions(self, *args, **kwargs):
        pass


class SwapCancelStrategy(BasePreloadStrategy):
    def __init__(self, data):
        super().__init__(data)
        self.swap_cancel_engine = SwapCancelValidateEngine(data)

    def generate_actions(self, enemy, tick: int):
        """合轴逻辑"""
        # 0、自检
        self.data.chek_myself_before_start_preload(enemy, tick)

        # 1、APL引擎抛出本tick的主动动作
        apl_skill_tag, priority = self.apl_engine.run_myself(tick)
        # print(apl_skill_tag, priority)

        #  2、ForceAdd引擎处理旧有的强制添加逻辑；
        self.force_add_engine.run_myself(tick)

        #  3、SwapCancel引擎 判定当前tick和技能是否能够成功合轴
        self.swap_cancel_engine.run_myself(apl_skill_tag, tick)

        if self.swap_cancel_engine.active_signal or self.force_add_engine.active_signal:
            #  4、Confirm引擎 清理data.preload_action_list_before_confirm，
            self.confirm_engine.run_myself(tick)


class SequenceStrategy(BasePreloadStrategy):
    def generate_actions(self):
        # 封装顺序生成逻辑
        pass
