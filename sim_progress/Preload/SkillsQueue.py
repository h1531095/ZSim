import pandas as pd
from define import APL_MODE
from sim_progress.data_struct.LinkedList import LinkedList
from sim_progress.Report import report_to_log
from sim_progress.Character.skill_class import Skill


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
        self.end_tick: int = self.preload_tick + self.skill.ticks

    def __str__(self) -> str:
        return f"SkillNode: {self.skill_tag}"


def spawn_node(tag: str, preload_tick: int, *skills: Skill) -> SkillNode:
    """
    通过输入的tag和preload_tick，直接创建SkillNode。
    """
    for obj in skills:
        if tag in obj.skills_dict.keys():
            node = SkillNode(obj.skills_dict[tag], preload_tick)
            return node
    else:
        raise ValueError(f"预加载技能 {tag} 不存在于输入的 Skill 类中，请检查输入")


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
    try:
        preload_skills: pd.Series = preload_table['skill_tag']  # 传入的数据必须包含 skill_tag 列
    except KeyError:
        print(f"提供错误的预加载序列表，请检查输入")

    # 确保技能列表不为空
    if not preload_skills.empty:
        preload_skills_list: list[str] = preload_skills.tolist()
    else:
        raise ValueError("预加载序技能列表为空")

    preload_tick_stamps = {skill.CID: 0 for skill in skills}
    if not APL_MODE:
        for tag in preload_skills_list:
            cid = int(tag[:4])  # 提取tag的前四个字符作为key
            if cid not in preload_tick_stamps:
                raise ValueError(f"技能 {tag} 的CID不在输入的技能列表中，请检查输入")

            try:
                # 在__main__中寻找tick变量，并与preload_tick_stamp比较
                tick = globals().get('tick', 0)
                preload_tick_stamp = max(preload_tick_stamps[cid], tick)     # 取最大值作为preload_tick_stamp
                node = spawn_node(tag, preload_tick_stamp, *skills)
                skills_queue.add(node)
                preload_tick_stamps[cid] = preload_tick_stamp + node.skill.ticks  # 更新preload_tick_stamp
                report_to_log(f"[PRELOAD]:预加载节点 {tag} 已创建，将在 {preload_tick_stamps[cid]} 执行", level=2)
            except ValueError as e:
                raise ValueError(str(e))

    return max(preload_tick_stamps.values()), skills_queue

if __name__ == '__main__':
    pass

