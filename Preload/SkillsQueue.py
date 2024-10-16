from Report import report_to_log
from Skill_Class import Skill
from LinkedList import LinkedList
import pandas as pd

preload_skills = []  # 留一个全局接口，可能没用其实


class SkillNode:
    def __init__(self, skill: Skill.InitSkill, preload_tick: int):
        self.skill_tag = skill.skill_tag
        self.preload_tick = skill.ticks + preload_tick
        self.hit_times = skill.hit_times
        self.skill = skill


def get_skills_queue(preload_table: pd.DataFrame,
                     skills: Skill,
                     **kwargs: Skill) -> LinkedList:
    """
    提取dataframe中，‘skill_tag’列的信息
    并将其与输入的 Skill 类比对
    可输入任意数量的 Skill 类比对。

    示例：
    get_skills_queue(dataframe,
                     skills = Skill( name='艾莲'),
                     skills_2 = Skill(name = '苍角'),
                     skills_3 = Skill(name = '莱卡恩'))

    返回：一个链表
    """
    skills_queue = LinkedList()  # 用于储存技能节点
    _skills_objects = [skills]
    for arg in kwargs:
        _skills_objects.append(arg)
    global preload_skills
    try:
        preload_skills = preload_table['skill_tag']  # 传入的数据帧必须包含skill_tag列
    except KeyError:
        print(f"提供错误的预加载序列表，请检查输入")

    if not preload_skills.empty:
        preload_skills = preload_skills.tolist()
    else:
        raise ValueError("预加载序技能列表为空")

    # 底下套了三层但没办法，看注释吧
    preload_tick_stamp = 0  # 初始化预加载的tick
    node = None
    # 首先遍历所提供的技能列表的所有tag
    for tag in preload_skills:
        # 对这些tag进行判断：是否存在与_skills_objects所记录的某一个对象中
        for obj in _skills_objects:  # 遍历包含输入的全部 Skill 对象的字典
            # 核对 Skill.skills_dict 字典中的键值，即这名角色的全部技能 Tag
            if tag in obj.skills_dict.keys():
                # 获取到这个技能的tick，并累加到 preload_tick_stamp
                tick = obj.skills_dict[tag].tick
                preload_tick_stamp += tick
                # 生成链表
                node = SkillNode(obj.skills_dict[tag], preload_tick_stamp)
        if node is None:
            raise AttributeError(f"预加载技能 {tag} 不存在于输入的 Skill 类中，请检查输入")
        else:
            skills_queue.add(node)
            node = None
    return skills_queue


if __name__ == '__main__':
    test = {
        'skill_tag': ['1221_NA_1', '1221_NA_2', '1221_NA_3', '1221_NA_4', '1221_NA_5']
    }
    test_skill_dataframe = pd.DataFrame(test)
    test_object = Skill(CID=1221)
    get_skills_queue(test_skill_dataframe, test_object)
    pass
