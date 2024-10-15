from Skill_Class import Skill
from LinkedList import LinkedList
import pandas as pd

preload_skills = [] # 留一个全局接口，可能没用其实
skills_queue = LinkedList() # 新建全局链表对象，用于储存技能节点

class SkillNode:
    def __init__(self, skill:Skill.InitSkill, preload_tick:int):
        self.skill_tag = skill.skill_tag
        self.preload_tick = skill.ticks + preload_tick
        self.hit_times = skill.hit_times
        self.skill = skill

def read_skill_data(preload_table: pd.DataFrame, skills: Skill):
    """提取dataframe中，‘skill_tag’列的信息"""
    global preload_skills
    try:
        preload_skills = preload_table['skill_tag'] # 传入的数据帧必须包含skill_tag列
    except KeyError:
        print(f"提供错误的预加载序列表，请检查输入")

    if not preload_skills.empty:
        preload_skills = preload_skills.tolist()

    preload_tick_stamp = 0
    for skill in preload_skills:
        i = skills.skills_dict[skill].tick
        preload_tick_stamp += i
        skills_queue.add(SkillNode(skill, preload_tick_stamp))

if __name__ == '__main__':
    test = {
        'skill_tag': ['1221_NA_1', '1221_NA_2', '1221_NA_3', '1221_NA_4', '1221_NA_5']
    }
    test_skill_dataframe = pd.DataFrame(test)
    test_object = Skill(CID=1221)
    read_skill_data(test_skill_dataframe, test_object)
    pass