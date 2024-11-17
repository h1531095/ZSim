from dataclasses import dataclass

import pandas as pd
from tqdm import trange

import Skill_Class
from Enemy import Enemy
from LinkedList import LinkedList
from Report import report_to_log
from define import INPUT_ACTION_LIST
from . import SkillsQueue
from . import watchdog
from .SkillsQueue import SkillNode


@dataclass
class PreloadData:
    def __init__(self, *args: Skill_Class.Skill):
        self.preloaded_action = LinkedList()

        '''data = pd.DataFrame(    # only for test
            {'skill_tag': ['1221_NA_1', '1221_NA_2', '1221_NA_3', '1221_NA_4', '1221_NA_5']}
        )'''

        max_tick, skills_queue = SkillsQueue.get_skills_queue(pd.read_csv(INPUT_ACTION_LIST), *args)
        self.max_tick: int = max_tick
        self.skills_queue: LinkedList = skills_queue
        self.current_node: SkillNode | None = None
        self.last_node: SkillNode | None = None


def stun_judge(enemy) -> bool:
    """
    判断敌人是否处于 失衡 状态，并更新 失衡 状态
    """
    if not enemy.able_to_be_stunned:
        return False

    if enemy.dynamic.stun:
        # Stunned, count the time and reset when stun time is out.
        if enemy.stun_recovery_time <= enemy.dynamic.stun_tick:
            enemy.dynamic.stun = False
            enemy.dynamic.stun_bar = 0
            enemy.dynamic.stun_tick = 0
            enemy.restore_stun_recovery_time()
        else:
            enemy.dynamic.stun_tick += 1
    else:
        # Not stunned, check the stun bar.
        if enemy.dynamic.stun_bar >= enemy.max_stun:
            enemy.dynamic.stun = True
    return enemy.dynamic.stun


class Preload:
    """
    实现程序的 Preload 阶段

    须传入此次计算所用角色的技能对象，形式为一个元组：tuple[Skill_Class.Skill,...]

    包含 do_preload 方法，执行 Preload 的核心逻辑
    实例化后 执行 do_preload(tick) 即可对本 tick 所需执行的动作进行预加载，建议从0开始循环，这样它会更聪明
    """

    def __init__(self, *args: Skill_Class.Skill):
        self.preload_data = PreloadData(*args)
        self.skills_queue = self.preload_data.skills_queue

    def __str__(self):
        return f"Preload Data: \n{self.preload_data.preloaded_action}"

    def do_preload(self, tick: int, enemy: Enemy = None, name_box: list[str] = None, char_data = None):
        if isinstance(enemy, Enemy):
            stun_status: bool = stun_judge(enemy)
        if self.preload_data.current_node is None:
            this_node = self.skills_queue.pop_head()
            self.preload_data.current_node = this_node
        else:
            this_node = self.preload_data.current_node
        if this_node is not None:
            # 随技能Preload技能而起的逻辑
            if this_node.preload_tick <= tick:
                # Preload技能逻辑
                watchdog.watch_reverse_order(this_node, self.preload_data.last_node)
                self.preload_data.preloaded_action.add(this_node)
                report_to_log(f"[PRELOAD]:In tick: {tick}, {this_node.skill_tag} has been preloaded")
                self.preload_data.last_node = this_node
                self.preload_data.current_node = None
                # Preload 结算特殊资源、能量、喧响
                for char in char_data.char_obj_list:
                    char.special_resources(this_node)
                    char.update_sp_and_decibel(this_node)
            # 切人逻辑
            if (isinstance(name_box, list)
                    and all(isinstance(name, str) for name in name_box)
                    and this_node.skill.on_field):
                self.switch_char(name_box, this_node)



    @staticmethod
    def switch_char(name_box, this_node):
        name_index = name_box.index(this_node.char_name)
        # 更改前台角色（切人逻辑）
        if name_index == 1:
            name_switch = name_box.pop(0)
            name_box.append(name_switch)
        elif name_index == 2:
            name_switch = name_box.pop(0)
            name_box.append(name_switch)
            name_switch = name_box.pop(0)
            name_box.append(name_switch)


if __name__ == '__main__':
    skills = (Skill_Class.Skill(CID=1221), Skill_Class.Skill(CID=1191))
    p = Preload(*skills)
    for tick in trange(100000):
        p.do_preload(tick)
    print(p.preload_data.preloaded_action)
