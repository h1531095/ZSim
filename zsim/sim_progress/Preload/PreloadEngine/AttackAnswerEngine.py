from .BasePreloadEngine import BasePreloadEngine
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sim_progress.Character import Character
    from sim_progress.Enemy import Enemy
    from simulator.simulator_class import Simulator


class AttackAnswerEngine(BasePreloadEngine):
    """进攻响应引擎，主要负责敌人进攻动作抛出，以及角色动作响应相关的内容；"""
    def __init__(self, data):
        super().__init__(data)
        self.game_state = None
        self.found_char_dict: dict[int, "Character"] = {}
        self.enemy: "Enemy | None" = None
        self.sim_instance: "Simulator | None" = None
        self.enemy_attack_instance = None

    def run_myself(self, *args, **kwargs):
        self.try_spawn_enemy_attack()

    def try_spawn_enemy_attack(self):
        """调用Enemy对象下的进攻模组，并且生成一次攻击，同时打包成事件存入本地"""
        if self.sim_instance is None:
            self.sim_instance = self.data.sim_instance
        if self.enemy is None:
            self.enemy = self.sim_instance.schedule_data.enemy
        if self.enemy.attack_method.random_attack:
            self.enemy.attack_method.probablity_driven_action_selection(current_tick=self.sim_instance.tick)
        else:
            self.enemy.attack_method.time_anchored_action_selection(current_tick=self.sim_instance.tick)



