from dataclasses import dataclass

import pandas as pd
from tqdm import trange

import Skill_Class
from LinkedList import LinkedList
from Preload import SkillsQueue
from Preload import watchdog
from Preload.SkillsQueue import SkillNode
from Report import report_to_log

INPUT_ACTION_LIST = pd.read_csv('./data/计算序列.csv')


@dataclass
class PreloadData:
    def __init__(self, *args: tuple[Skill_Class.Skill, ...]):
        self.preloaded_action = LinkedList()

        '''data = pd.DataFrame(    # only for test
            {'skill_tag': ['1221_NA_1', '1221_NA_2', '1221_NA_3', '1221_NA_4', '1221_NA_5']}
        )'''
        self.skills_queue: LinkedList = SkillsQueue.get_skills_queue(INPUT_ACTION_LIST, *args)
        self.current_node: SkillNode = None
        self.last_node: SkillNode = None


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

    def do_preload(self, tick: int):
        if self.preload_data.current_node is None:
            this_node = self.skills_queue.pop_head()
            self.preload_data.current_node = this_node
        else:
            this_node = self.preload_data.current_node
        if this_node is not None:
            if this_node.preload_tick <= tick:
                watchdog.watch_reverse_order(this_node, self.preload_data.last_node)
                self.preload_data.preloaded_action.add(this_node)
                report_to_log(f"[PRELOAD]:In tick: {tick}, {this_node.skill_tag} has been preloaded")
                self.preload_data.last_node = this_node
                self.preload_data.current_node = None


if __name__ == '__main__':
    p = Preload(Skill_Class.Skill(CID=1221), Skill_Class.Skill(CID=1191))
    for tick in trange(100000):
        p.do_preload(tick)
    print(p.preload_data.preloaded_action)
