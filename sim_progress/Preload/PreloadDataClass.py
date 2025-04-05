from sim_progress.Preload import SkillNode
from sim_progress.data_struct import NodeStack


class PreloadData:
    """循环于Preload阶段内部的数据"""
    def __init__(self, args):
        self.preload_action: list[SkillNode] = []    # 最终return返回给外部申请的数据结构
        self.skills = args     # 用于创建SkillNode，是SkillNode构造函数的必要参数。
        self.personal_node_stack: dict[int: NodeStack] = {}    # 个人的技能栈
        self.current_node_stack: NodeStack = NodeStack(length=5)      # Preload阶段的总技能栈
        self.latest_active_generation_node: SkillNode | None = None     # 最近一次主动生成的skillnode，#TODO：可能是无用参数！
        self.preload_action_list_before_confirm: list[tuple[str, bool]] = []        # 当前tick需要执行preload的SkillTag列表，列表中的元素是(skill_tag, active_generation)，其中，active_generation指的是动作是否是主动生成。
        self.name_box: list[str] | None = None
        self.char_data = None

    @property
    def operating_now(self) -> int | None:
        """返回正在操作的角色"""
        if self.latest_active_generation_node is None:
            return None
        _cid = int(self.latest_active_generation_node.skill_tag.split('_')[0])
        return _cid

    def push_node_in_swap_cancel(self, node: SkillNode):
        """合轴模式中的内部数据更新函数。将构造好的SkillNode加入preload_action中，同时更新Preload板块的内部数据。"""
        self.check_myself_before_push_node()
        self.preload_action.append(node)
        char_cid = int(node.skill_tag.split('_')[0])
        self.current_node_stack.push(node)
        if char_cid not in self.personal_node_stack:
            self.personal_node_stack[char_cid] = NodeStack(length=3)
        self.personal_node_stack[char_cid].push(node)
        if node.active_generation:
            self.latest_active_generation_node = node

    def check_myself_before_push_node(self):
        """Confirm阶段自检"""
        _active_generation_node_list = []
        for _node in self.preload_action:
            if _node.active_generation:
                _active_generation_node_list.append(_node)
        if len(_active_generation_node_list) > 1:
            raise ValueError(f'在一个Tick中检测到了多个主动技能！共有：{_active_generation_node_list}')

    def get_on_field_node(self, tick: int) -> SkillNode | None:
        """获取当前的前台技能"""
        return self.current_node_stack.get_on_field_node(tick)

    def chek_myself_before_start_preload(self, enemy, tick):
        """Preload阶段自检"""
        if self.preload_action:
            print(f'尚未被Load阶段处理的技能：{self.preload_action}')
        enemy.stun_judge(tick)

    def external_add_skill(self, skill_tuple: tuple[str, bool]):
        """外部Buff向下一个Tick添加技能的接口，通常用于协同攻击"""
        skill_tag, active_generation = skill_tuple
        self.preload_action_list_before_confirm.append(skill_tuple)

    def force_change_action(self, skill_node: SkillNode):
        """强制更新动作，用于技能强制顶替、被打断或是类似场合"""
        char_cid = int(skill_node.skill_tag.strip().split('_')[0])
        self.personal_node_stack[]





