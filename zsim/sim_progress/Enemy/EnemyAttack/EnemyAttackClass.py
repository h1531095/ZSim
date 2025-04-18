import numpy as np
from define import ENEMY_ATTACK_METHOD_CONFIG, ENEMY_ATTACK_ACTION
from collections import defaultdict
import pandas as pd
from sim_progress.RandomNumberGenerator import RNG


"""
    EnemyAttack模块相关的数据结构以及程序逻辑设计如下（2025.1.30）：
    1、新建一个数据库（暂时用CSV来执行），里面记录了Enemy的各种进攻动作，由独立的ID作为索引。（包含了默认动作）
    2、新建一个Json，用来记录不同敌人的进攻策略，其中包含了各种数据库中的动作ID，以及它们对应的几率。（包含了默认的策略）
        Json的键值是一个独立的ID，可以是数字，也可以是字符串。
    3、在Enemy类下，更新一个新的字段（包括EnemyClass以及对应的Enemy.csv），用来存放不同敌人的策略ID，
    4、初始化时，根据Enemy.attack.策略ID→对应的攻击策略→对应的攻击动作ID（多个）→构造EnemyAttack实例（多个）→存放到Enemy.attack.attack_method下
        4.1、每个攻击动作都会构造一个单独的EnemyAttackAction实例，这些实例会被存到EnemyAttackMethod实例下，并且有各自的几率。
    5、调用时，利用EnemyAttack.attack_event_spawn函数，生成本次发生的攻击事件，并且抛出，被Preload获取。
        5.1、首先，不同的攻击动作有各自的内置CD，以及有各自的不同属性，而EnemyAttack
"""

method_file = pd.read_csv(ENEMY_ATTACK_METHOD_CONFIG, index_col="ID")
action_file = pd.read_csv(ENEMY_ATTACK_ACTION, index_col="ID")


class EnemyAttackMethod:
    """含有若干个进攻动作的进攻策略"""

    def __init__(self, ID: int = 0):
        self.action_set = defaultdict()
        self.last_start_tick = 0
        self.last_end_tick = 0
        self.ready = False
        rate_list = method_file.loc[ID]["action_rate"].split("|")
        if sum(float(i) for i in rate_list) > 1:
            raise ValueError("动作总权重超过1，请检查配置")
        single_action_id_list = method_file.loc[ID]["action_set"].split("|")
        if len(rate_list) != len(single_action_id_list):
            raise ValueError("动作总数与概率总数不符，请检查配置")
        self.rest_tick = method_file.loc[ID]["rest_tick"]
        self.description = method_file.loc[ID]["discription"]  # FIXME
        self.name = method_file.loc[ID]["method_name"]
        for i in range(len(single_action_id_list)):
            action_id = single_action_id_list[i]
            action_rate = float(rate_list[i])
            enemy_attack_action = EnemyAttackAction(int(action_id))
            self.action_set[action_rate] = enemy_attack_action

    def ready_check(self, current_tick: int):
        """判断敌人进攻的内置CD"""
        if not self.ready:
            if current_tick - self.last_end_tick >= self.rest_tick:
                self.ready = True
        return self.ready

    def select_action(self, current_tick: int):
        """根据概率选择一个进攻动作"""
        cumulative_probability = 0  # 累积概率，这个数字没有实际意义，只是为了方便计算，每次函数运行时都初始化为0
        select_seed = RNG().random_float()
        if not self.ready_check(current_tick):
            return None
        for _rate, _action in self.action_set.items():
            cumulative_probability += _rate
            if cumulative_probability >= select_seed:
                self.last_start_tick = current_tick
                self.last_end_tick = current_tick + _action.duration
                self.ready = False
                return _action
        else:
            """如果循环结束，还没有选中任何一个动作，说明无事发生，返回None"""
            return None

    def reset_myself(self):
        """重构EnemyAttack方法！"""
        self.last_start_tick = 0
        self.last_end_tick = 0
        self.ready = False


class EnemyAttackAction:
    """敌人的单个进攻动作"""

    def __init__(self, ID: int):
        if ID == 0:
            raise ValueError("EnemyAttackAction实例化所用的ID为0，请检查配置信息！")
        self.action_dict = action_file.loc[ID].to_dict()
        self.tag = self.action_dict.get("tag", "")
        self.description = self.action_dict.get("description", "")
        self.hit = int(self.action_dict.get("hit", 0))
        if self.hit <= 0:
            raise ValueError("hit参数必须大于0，请检查配置信息！")
        self.duration = float(self.action_dict.get("duration", 0))
        if self.duration <= 0:
            raise ValueError("duration参数必须大于0，请检查配置信息！")
        self.cd = int(self.action_dict.get("cd", 0))
        self.hit_list = self.action_dict.get("hit_list", None)
        if self.hit_list is None or self.hit_list is np.nan:
            # 在未提供hit_list的情况下，默认hit均匀分布，所以直接根据hit和duration来产生hit_list，
            self.hit_list = list(
                (self.duration / (self.hit + 1)) * (i + 1) for i in range(int(self.hit))
            )
        else:
            self.hit_list = self.hit_list.split("|")
        self.blockable_list = self.action_dict.get("blockable_list", None)
        if self.blockable_list is None or self.blockable_list is np.nan:
            self.blockable_list = [False] * self.hit
        else:
            self.blockable_list = self.blockable_list.split("|")
        self.interruption_level_list = self.action_dict.get(
            "interruption_level_list", None
        )
        if (
            self.interruption_level_list is None
            or self.interruption_level_list is np.nan
        ):
            self.interruption_level_list = [1] * self.hit
        else:
            self.interruption_level_list = self.interruption_level_list.split("|")
        self.effect_radius_list = self.action_dict.get("effect_radius_list", None)
        # TODO：暂时不考虑由技能范围不同而对命中率造成的影响，统一按照100%命中来处理，
        self.stoppable = self.action_dict.get("stoppable", False)

    def block_judge(self, char_action):
        pass


if __name__ == "__main__":
    method = EnemyAttackMethod()
    print(f"{method.name},{method.description}")
    count = 0
    for rate, action in method.action_set.items():
        print(
            f"事件{count + 1}，几率{rate}，动作集{action.hit_list}，是否可被格挡：{action.blockable_list}，\n打断等级{action.interruption_level_list}，效果半径{action.effect_radius_list}，是否可被打断{action.stoppable}"
        )
        count += 1
