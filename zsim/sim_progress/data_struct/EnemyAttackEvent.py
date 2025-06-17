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
        self.last_start_tick: int = 0  # 进攻事件的开始时刻，也是进攻意图的展露时刻。
        self.last_end_tick: int = 0
        self.answered_action: list["SkillNode"] = []
        self.interaction_window_open_tick: int | None = (
            None  # 交互窗口开启的tick，即游戏中红黄光亮起的tick
        )
        self.interaction_window_close_tick: int | None = (
            None  # 交互窗口关闭的tick，即游戏中动作命中的时间点
        )
        self.hitted_count = 0   # 交互期间的命中计数
        self.answered_count = 0  # 交互期间的成功响应次数

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
        self.response_result_settlement()
        if tick is not None:
            self.last_end_tick = tick
        self.action = None
        self.answered_action = []

    def interrupted(self, tick: int):
        """中断当前进攻事件"""
        if self.action is None:
            raise ValueError("没有正在进行的进攻事件，无法中断！")
        print(
            f"敌人（{self.enemy.name}）的进攻事件：{self.action.tag}在第{tick}tick被中断！"
        ) if ENEMY_ATTACK_REPORT else None
        self.event_end(tick=tick)

    def end_check(self, tick: int):
        """检测当前进攻事件是否已经结束"""
        if not self.action:
            return
        if tick >= self.last_end_tick:
            print(
                f"敌人（{self.enemy.name}）的进攻事件：{self.action.tag}在第{tick}tick自然结束！"
            ) if ENEMY_ATTACK_REPORT else None
            self.event_end()

    @property
    def attacking(self) -> bool:
        """当前是否正在进行进攻事件"""
        return self.action is not None

    @property
    def is_answered(self) -> bool:
        """当前进攻事件是否已经被响应"""
        if not self.answered_action:
            return False
        else:
            for action in self.answered_action:
                """仅在检测到招架支援时，才返回True。只要不招架，那么单次进攻信号就可能被多次利用。"""
                if "parry_Aid" in action.skill_tag:
                    return True
            else:
                return False

    def is_in_response_window(self, tick: int) -> bool:
        """判断当前tick是否处于响应窗口内"""
        if not self.attacking:
            return False
        if (
            self.interaction_window_open_tick
            <= tick
            <= self.interaction_window_close_tick
        ):
            return True
        return False

    def get_rt(self) -> int:
        """获取玩家反应时间（RT），即玩家从看到敌人进攻到做出反应的时间。"""
        theta = ENEMY_ATK_PARAMETER_DICT.get("theta", None)
        if theta is None:
            raise ValueError("ENEMY_ATK_PARAMETER_DICT中没有theta参数，请检查配置！")
        Lp = ENEMY_ATK_PARAMETER_DICT.get("PlayerLevel", None)
        if Lp is None:
            raise ValueError(
                "ENEMY_ATK_PARAMETER_DICT中没有PlayerLevel参数，请检查配置！"
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
        Z = abs(
            self.enemy.sim_instance.rng_instance.normal_from_table()
        )  # 从RNG模块按正态分布获取一个0~1的随机数。
        RT = theta + math.e ** (mu + sigma * Z)
        rt_tick = round(RT / 1000 * 60)  # 将毫秒转化为帧（tick）

        return rt_tick

    def get_consecutive_response_windowget_response_window(self) -> tuple[int, int]:
        """获取红黄光亮起的时间点"""
        first_hit_tick = self.action.get_hit_tick() + self.last_start_tick
        Ta = ENEMY_ATK_PARAMETER_DICT.get("Taction")
        left_bound = max(
            self.last_start_tick, first_hit_tick - Ta
        )  # 如果怪物前摇很短，动作时间也很短，那么怪物攻击动作开始的时间就是黄光亮起的时间。
        right_bound = first_hit_tick
        return left_bound, right_bound


    def get_uncommon_response_window(self, another_ta: int) -> tuple[int, int]:
        """获取红黄光亮起的时间点，适用于非标准的进攻动作"""
        first_hit_tick = (
                self.action.get_hit_tick(another_ta=another_ta) + self.last_start_tick
        )
        Ta = another_ta
        left_bonud = max(self.last_start_tick, first_hit_tick - Ta)
        right_bound = first_hit_tick
        return left_bonud, right_bound

    def can_be_answered(self, rt_tick: int) -> tuple[bool, int, int]:
        """该函数用于判断当前进攻事件是否具有响应的可能，主要是时间判断。"""
        if not self.action:
            raise ValueError("调用can_be_answered函数时请确保存在进攻事件")
        if self.is_answered:
            print(
                f"当前动作：{self.action.tag}已经被{[_action.skill_tag for _action in self.answered_action]}响应过了！"
            )
            return False, 0, 0
        Lp = ENEMY_ATK_PARAMETER_DICT.get("PlayerLevel")
        Td = self.interaction_window_close_tick - self.interaction_window_open_tick
        first_hit_tick = self.action.get_hit_tick()
        if Lp <= 2:
            return rt_tick <= Td, rt_tick, Td
        else:
            return (
                rt_tick <= first_hit_tick,
                rt_tick,
                first_hit_tick,
            )

    def receive_response_node(self, skill_node: "SkillNode"):
        """对外接口，用于接收响应技能。"""
        pass

    def response_result_settlement(self):
        """响应结果结算函数，主要用于在进攻事件结束时，结算所有的响应结果。"""
        sim_instance = self.enemy.sim_instance
        char_on_field_cid: int = sim_instance.preload.preload_data.operating_now
        tick = sim_instance.tick
        if char_on_field_cid is None:
            raise ValueError("当前没有角色在操作，无法结束进攻事件！")
        if self.answered_action:
            effective_response_skill_tag_list = []
            for __response_node in self.answered_action:
                if __response_node.skill.char_obj.CID != char_on_field_cid:
                    """如果响应技能不是当前操作角色的技能，那么不算作有效响应。"""
                    continue
                if not __response_node.active_generation:
                    """如果响应技能不是主动技能，那么不算作有效响应。"""
                    continue
                if (
                    __response_node.labels is not None
                    and "additional_damage" in __response_node.labels
                ):
                    """如果技能拥有附加标签，那么该技能不算作有效响应。"""
                    continue
                if any(
                    [
                        sub_tag in __response_node.skill_tag
                        for sub_tag in ["parry", "dodge"]
                    ]
                ):
                    effective_response_skill_tag_list.append(__response_node.skill_tag)
                elif __response_node.skill.trigger_buff_level in [2, 4, 5, 6, 7, 8, 9]:
                    """如果回应技能中包含不会被打断的技能，那么也算作有效响应。"""
                    effective_response_skill_tag_list.append(__response_node.skill_tag)
            else:
                if effective_response_skill_tag_list:
                    print(
                        f"敌人（{self.enemy.name}）的进攻事件：{self.action.tag}在第{tick}tick被以下技能响应：{effective_response_skill_tag_list}"
                    ) if ENEMY_ATTACK_REPORT else None
                else:
                    print(
                        f"敌人（{self.enemy.name}）的进攻事件：{self.action.tag}在第{tick}tick没有被有效技能响应！"
                    ) if ENEMY_ATTACK_REPORT else None
        else:
            print("没有任何技能响应当前进攻事件！") if ENEMY_ATTACK_REPORT else None

    def blockable_check(self, tick: int) -> bool:
        """检查当前tick是否存在可以格挡的进攻信号"""
        if self.action is None:
            return False
        if self.action.get_hit_tick()
        return False
