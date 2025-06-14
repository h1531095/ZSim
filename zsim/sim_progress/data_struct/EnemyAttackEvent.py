from define import ENEMY_ATTACK_REPORT, ENEMY_ATK_PARAMETER_DICT
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sim_progress.Enemy.EnemyAttack.EnemyAttackClass import EnemyAttackAction
    from sim_progress.Enemy import Enemy
    from sim_progress.Preload import SkillNode


class EnemyAttackEventManager:
    def __init__(self, enemy_instance: "Enemy"):
        """进攻事件对象，负责管理敌人进攻的相关动态信息。"""
        self.enemy: "Enemy" = enemy_instance
        self.action: "None | EnemyAttackAction" = None
        self.last_start_tick: int = 0
        self.last_end_tick: int = 0
        self.answered_action: "SkillNode | None" = None
        self.interaction_window_open_tick: int | None = (
            None  # 交互窗口开启的tick，即游戏中红黄光亮起的tick
        )
        self.interaction_window_close_tick: int | None = (
            None  # 交互窗口关闭的tick，即游戏中动作命中的时间点
        )

    def event_start(self, action: "EnemyAttackAction", start_tick: int):
        """开始一个进攻事件"""
        self.action = action
        self.last_start_tick = start_tick
        self.last_end_tick = start_tick + action.duration
        response_window: tuple[int, int] = self.get_response_window()
        self.interaction_window_open_tick = response_window[0]
        self.interaction_window_close_tick = response_window[1]

        print(
            f"敌人（{self.enemy.name}）开始了进攻事件：{action.tag}，持续时间为{action.duration}tick"
        ) if ENEMY_ATTACK_REPORT else None

    def event_end(self, tick: int = None):
        """结束一个进攻事件"""
        if self.action is None:
            raise ValueError("没有正在进行的进攻事件，无法结束！")
        if tick is not None:
            self.last_end_tick = tick
        self.action = None

    def interrupted(self, tick: int):
        """中断当前进攻事件"""
        if self.action is None:
            raise ValueError("没有正在进行的进攻事件，无法中断！")
        print(
            f"敌人（{self.enemy.name}）的进攻事件：{self.action.tag}在第{tick}tick被中断！"
        ) if ENEMY_ATTACK_REPORT else None
        self.event_end(tick=tick)

    @property
    def attacking(self) -> bool:
        """当前是否正在进行进攻事件"""
        return self.action is not None

    @property
    def is_answered(self) -> bool:
        """当前进攻事件是否已经被响应"""
        return self.answered_action is not None

    def get_rt(self) -> int:
        """获取玩家反应时间（RT），即玩家从看到敌人进攻到做出反应的时间。"""
        theta = ENEMY_ATK_PARAMETER_DICT.get("theta", None)
        if theta is None:
            raise ValueError("ENEMY_ATK_PARAMETER_DICT中没有theta参数，请检查配置！")
        Lp = ENEMY_ATK_PARAMETER_DICT.get("player_level", None)
        if Lp is None:
            raise ValueError(
                "ENEMY_ATK_PARAMETER_DICT中没有player_level参数，请检查配置！"
            )
        c = ENEMY_ATK_PARAMETER_DICT.get("c", None)
        if c is None:
            raise ValueError("ENEMY_ATK_PARAMETER_DICT中没有c参数，请检查配置！")
        Tbase = ENEMY_ATK_PARAMETER_DICT.get("Tbase", None)
        if Tbase is None:
            raise ValueError("ENEMY_ATK_PARAMETER_DICT中没有Tbase参数，请检查配置！")
        delta = ENEMY_ATK_PARAMETER_DICT.get("delta", None)
        if delta is None:
            raise ValueError("ENEMY_ATK_PARAMETER_DICT中没有delta参数，请检查配置！")
        sigma = c / (Lp**0.3)  # 计算方差
        Ta = Tbase + delta * (3 - Lp)  # 根据玩家水平计算对应中位数
        mu = math.log(Ta - theta) - sigma**2 / 2  # 计算均值
        Z = (
            self.enemy.sim_instance.rng_instance.normal_from_table()
        )  # 从RNG模块按正态分布获取一个0~1的随机数。
        RT = theta + math.e ** (mu + theta * Z)
        rt_tick = round(RT / 1000 * 60)  # 将毫秒转化为帧（tick）
        return rt_tick

    def get_response_window(self) -> tuple[int, int]:
        """获取红黄光亮起的时间点"""
        first_hit_tick = self.action.get_first_hit() + self.last_start_tick
        Ta = ENEMY_ATK_PARAMETER_DICT.get("Taction")
        left_bound = max(
            self.last_start_tick, first_hit_tick - Ta
        )  # 如果怪物前摇很短，动作时间也很短，那么怪物攻击动作开始的时间就是黄光亮起的时间。
        right_bound = first_hit_tick
        return left_bound, right_bound
