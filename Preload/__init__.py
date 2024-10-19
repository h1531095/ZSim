from dataclasses import dataclass

import numpy as np
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
    def __init__(self):
        self.preloaded_action = LinkedList()

        '''data = pd.DataFrame(    # only for test
            {'skill_tag': ['1221_NA_1', '1221_NA_2', '1221_NA_3', '1221_NA_4', '1221_NA_5']}
        )'''
        skills = (Skill_Class.Skill(CID=1191), Skill_Class.Skill(CID=1221))
        self.skills_queue: LinkedList = SkillsQueue.get_skills_queue(INPUT_ACTION_LIST, skills[0], skills[1])
        self.current_node: SkillNode = None
        self.last_node: SkillNode = None

class Preload:
    def __init__(self):
        self.preload_data = PreloadData()
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

# if __name__ == '__main__':
#     p = Preload()
#     for tick in trange(100000):
#         p.do_preload(tick)
#     print(p.preload_data.preloaded_action)