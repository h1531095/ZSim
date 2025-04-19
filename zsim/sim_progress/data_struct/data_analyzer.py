from __future__ import annotations

from functools import lru_cache
from typing import Any, Sequence, TYPE_CHECKING

from sim_progress.Report import report_to_log

if TYPE_CHECKING:
    from sim_progress.Buff import Buff
    from sim_progress.Preload.SkillsQueue import SkillNode


@lru_cache(maxsize=128)
def cal_buff_total_bonus(
    enabled_buff: Sequence["Buff"], skill_node: "SkillNode" | None = None
) -> dict[str, float]:
    """
    计算角色buff的总加成。

    该方法首先读取buff效果的键值对，然后遍历角色身上的所有buff。
    对于每个buff，检查其是否为Buff类型，然后根据buff的计数（count）来计算总加成。

    参数:
    - char_buff: 包含角色所有buff的列表。
    """

    # 初始化动态语句字典，用于累加buff效果的值
    dynamic_statement: dict[str, float] = {}
    # 遍历角色身上的所有buff
    from sim_progress.Buff import Buff
    buff_obj: Buff
    for buff_obj in enabled_buff:
        # 确保buff是Buff类的实例
        if not isinstance(buff_obj, Buff):
            raise TypeError(f"{buff_obj} 不是Buff类型，无法计算！")
        else:
            # 检查buff是否激活
            if not buff_obj.dy.active:
                report_to_log(
                    f"[Warning] 动态buff列表中混入了未激活buff: {str(buff_obj)}，已跳过"
                )
                continue
            # 检查buff的标签是否与技能节点匹配
            if skill_node is not None:
                if not __check_buff_labels(buff_obj, skill_node):
                    continue
            # 获取buff的层数
            count = buff_obj.dy.count
            count = count if count > 0 else 0
            # 遍历buff的每个效果和对应的值，并将其累加

            for key, value in buff_obj.effect_dct.items():
                # 如果键值对在动态语句字典中，则累加值，否则初始化并赋值
                try:
                    dynamic_statement[key] = (
                        dynamic_statement.get(key, 0) + value * count
                    )
                except TypeError:
                    continue
    return dynamic_statement


def __check_buff_labels(buff: "Buff", skill_node: "SkillNode") -> bool:
    """
    检查 buff 的标签是否与 skill node 匹配。

    该方法用于验证 buff 的标签限制条件是否满足技能节点的要求。检查标签类型：
    1. only_skill: buff仅对特定技能标签生效
    2. only_label: buff仅对带有特定标签的技能生效

    参数:
        buff (Buff): 需要检查的buff对象
        skill_node (SkillNode): 技能节点对象

    返回:
        bool: 如果buff标签与技能节点匹配则返回True，否则返回False
    """
    # 定义允许的标签类型
    ALLOWED_LABELS = ["only_skill", "only_label"]
    # 获取buff的标签列表
    buff_labels: dict[str, Any] = buff.ft.label
    # 如果buff没有标签限制，则直接返回True
    if not buff_labels:
        return True
    
    # 获取技能节点的标签信息
    skill_tag: str = skill_node.skill_tag
    skill_labels: dict[str, Any] = skill_node.labels
    
    # 遍历buff的所有标签进行检查
    for label_key, label_value in buff_labels.items():
        if not label_value:
            continue
        if label_key in ALLOWED_LABELS:
            # 检查是否为特定技能限制
            if label_key == "only_skill":
                if skill_tag in label_value:
                    return True
            # 检查是否为特定标签限制
            elif label_key == "only_label":
                if label_value in skill_labels.keys():
                    return True
    return False