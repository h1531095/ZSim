import pandas as pd

import Skill_Class
from LinkedList import LinkedList
from Preload import SkillsQueue
from Preload import watchdog
from dataclasses import dataclass

from Preload.SkillsQueue import SkillNode


@dataclass
class PreloadData:
    preloaded_action = LinkedList()
    data = pd.DataFrame(    # only for test
        {'skill_tag': ['1221_NA_1', '1221_NA_2', '1221_NA_3', '1221_NA_4', '1221_NA_5']}
    )
    skills = (Skill_Class.Skill(CID=1191), Skill_Class.Skill(CID=1221))
    skills_queue = SkillsQueue.get_skills_queue(data, skills[0], skills[1])
    current_node: SkillNode = None
    last_node: SkillNode = None

class Preload:
    def __init__(self):
        self.preload_data = PreloadData()
        self.skills_queue = self.preload_data.skills_queue

    def do_preload(self, tick: int):
        if self.preload_data.current_node is None:
            this_node = next(iter(self.skills_queue))
            self.preload_data.current_node = this_node
        else:
            this_node = self.preload_data.current_node
        if this_node.preload_tick == tick:
            watchdog.watch_reverse_order(this_node, self.preload_data.last_node)
            self.preload_data.preloaded_action.add(this_node)
            self.preload_data.last_node = this_node
            self.preload_data.current_node = None