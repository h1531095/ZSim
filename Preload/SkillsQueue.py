import pandas as pd

from LinkedList import LinkedList
from Report import report_to_log
from Character.skill_class import Skill

preload_skills = []  # 留一个全局接口，可能没用其实


class SkillNode:
    def __init__(self, skill: Skill.InitSkill, preload_tick: int):
        """
        预加载技能节点

        包含：
        1、部分需要立即调用的信息；
        2、整个 Skill.InitSkill 对象，包含了技能的全部信息，用于计算器调用
        """
        self.skill_tag: str = skill.skill_tag
        self.char_name: str = skill.char_name
        self.preload_tick: int = preload_tick
        self.hit_times: int = skill.hit_times
        self.skill: Skill.InitSkill = skill

    def __str__(self) -> str:
        return f"SkillNode: {self.skill_tag}"



def get_skills_queue(preload_table: pd.DataFrame,
                     *skills: Skill,
                     ) -> tuple[int, LinkedList]:
    """
    提取dataframe中，‘skill_tag’列的信息
    并将其与输入的 Skill 类比对
    可输入任意数量的 Skill 类比对。

    示例：
    get_skills_queue(dataframe,
                     skills = Skill( name='艾莲'),
                     skills_2 = Skill(name = '苍角'),
                     skills_3 = Skill(name = '莱卡恩'))

    返回：一个链表，包含全部可被预加载的 SkillNode
    """
    # 输入类型检查
    if not isinstance(preload_table, pd.DataFrame):
        raise TypeError("预加载序列表必须是 pandas.DataFrame 类型")
    if not all(isinstance(x, Skill) for x in skills):
        raise TypeError("输入的技能必须是 Skill 类")

    skills_queue = LinkedList()  # 用于储存技能节点
    global preload_skills
    try:
        preload_skills = preload_table['skill_tag']  # 传入的数据必须包含 skill_tag 列
    except KeyError:
        print(f"提供错误的预加载序列表，请检查输入")

    # 确保技能列表不为空
    if not preload_skills.empty:
        preload_skills = preload_skills.tolist()
    else:
        raise ValueError("预加载序技能列表为空")

    # 底下套了三层但没办法，看注释吧
    preload_tick_stamp: int = 0  # 初始化预加载的tick
    # 首先遍历所提供的技能列表的所有tag
    for tag in preload_skills:
        # 对这些tag进行判断：是否存在与_skills_objects所记录的某一个对象中
        found = False
        for obj in skills:  # 遍历包含输入的全部 Skill 对象的字典
            # 核对 Skill.skills_dict 字典中的键值，即这名角色的全部技能 Tag
            if tag in obj.skills_dict.keys():
                found = True
                # 生成链表
                node = SkillNode(obj.skills_dict[tag], preload_tick_stamp)
                # 获取到这个技能的tick，并累加到 preload_tick_stamp
                skill_ticks = obj.skills_dict[tag].ticks
                preload_tick_stamp += skill_ticks
                report_to_log(f"[PRELOAD]:预加载节点 {node.skill_tag} 已创建，将在 {node.preload_tick} 执行", level=2)
                skills_queue.add(node)
                break
        if not found:
            raise ValueError(f"预加载技能 {tag} 不存在于输入的 Skill 类中，请检查输入")
    return preload_tick_stamp, skills_queue

# TODO：写一个自动判断下一个动作的模块。


if __name__ == '__main__':
    test = {
        'skill_tag': ['1221_NA_1', '1221_NA_2', '1221_NA_3', '1221_NA_4', '1221_NA_5']
    }
    test_skill_dataframe = pd.DataFrame(test)
    test_object = Skill(CID=1221)
    skill_queue = get_skills_queue(test_skill_dataframe, test_object)
    for _ in skill_queue:
        print(_.skill_tag, _.preload_tick)

