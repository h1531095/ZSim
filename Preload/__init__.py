import pandas as pd

from LinkedList import LinkedList
from Preload import SkillsQueue
from Preload import watchdog

class PreloadAttribute:
    data = pd.DataFrame(    # only for test
        {'skill_tag': ['1221_NA_1', '1221_NA_2', '1221_NA_3', '1221_NA_4', '1221_NA_5']}
    )
    skills_queue = SkillsQueue.get_skills_queue(preload_table=data, skills=skill)
    current_node: LinkedList = None
    last_node: LinkedList = None

class Preload:
    def __init__(self):
        self.skills_queue = SkillsQueue.get_skills_queue()