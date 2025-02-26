import numpy as np
import pandas as pd
import math
from dataclasses import dataclass
from sim_progress.Character import Skill
from sim_progress.Enemy import Enemy
from sim_progress.data_struct import LinkedList
from sim_progress.Report import report_to_log
from define import INPUT_ACTION_LIST, APL_MODE, APL_PATH, SWAP_CANCEL, ENEMY_RANDOM_ATTACK, ENEMY_ATTACK_RESPONSE
from define import SWAP_CANCEL_MODE_COMPLETION_COEFFICIENT as SCK, SWAP_CANCEL_MODE_LAG_TIME as SCLT
# EXPLAIN：关于SCK和LT的作用：
"""
以上两个系数分别是：
①合轴操作完成度系数 SWAP_CANCEL_MODE_COMPLETION_COEFFICIENT （程序中通常引用为SCK）
②操作滞后系数 SWAP_CANCEL_MODE_LAG_TIME （程序中通常引用为SCLT），它们共同用于模拟玩家的合轴操作。
因为不可能任意操作都具有完美的完成度（在第2帧就完美切人+下一招出手），
人体机能限制、注意力不集中、可能存在的操作习惯以及其他因素，都会导致合轴操作的延后实施，
所以，这里通过设置一个系数来模拟玩家的操作滞后程度，在计算时，我会取用skill_node的时长（skill.ticks)，并且乘以SCK，
所计算出的结果与SCLT参数相比较，取较小值作为最终的滞后时间（防止较长的技能滞后严重，导致模拟失真）。
后续的升级方向：
在引入随机数生成器后，可以进一步基于两个参数的基本值，对这两个参数进行随机处理，从而真正模拟玩家在操作端的浮动。
"""
from . import SkillsQueue
from . import watchdog
from .SkillsQueue import SkillNode
from .APLModule import APLParser, APLExecutor
from collections import defaultdict
from sim_progress.RandomNumberGenerator import RNG


@dataclass
class PreloadData:
    def __init__(self, *args: Skill):
        self.preloaded_action = LinkedList()
        self.skills = args
        max_tick, skills_queue = SkillsQueue.get_skills_queue(pd.read_csv(INPUT_ACTION_LIST), *self.skills)
        self.max_tick: int = max_tick
        self.skills_queue: LinkedList = skills_queue
        if SWAP_CANCEL:
            """
            下面两个字典的作用：
            APL的部分代码需要查看“某角色的当前/上一个技能”，而非“整治队伍的当前/上一个技能”，
            这两个字典在本函数中的使用很少，但是会被APL模块反复调用，请不要删除。
            """
            self.personal_current_node: dict[int, SkillNode | None] = defaultdict(lambda: None)
            self.personal_last_node: dict[int, SkillNode | None] = defaultdict(lambda: None)
        self.current_node: SkillNode | None = None
        self.current_on_field_node_tag: str | None = None       # 这个记录同样是为了APL模块服务的，Preload阶段的两个主函数都用不到这个属性。只会执行更新。
        self.last_node: SkillNode | None = None


def stun_judge(enemy: Enemy) -> bool:
    """
    判断敌人是否处于 失衡 状态，并更新 失衡 状态
    """
    if not enemy.able_to_be_stunned:
        return False

    if enemy.dynamic.stun:
        # Stunned, count the time and reset when stun time is out.
        if enemy.stun_recovery_time <= enemy.dynamic.stun_tick:
            enemy.restore_stun()
        else:
            enemy.dynamic.stun_tick += 1
    else:
        # Not stunned, check the stun bar.
        if enemy.dynamic.stun_bar >= enemy.max_stun:
            enemy.dynamic.stun = True
    return enemy.dynamic.stun


class Preload:
    """
    预载动作的模块，负责生成新的SkillNode。
    非APL模式下，它会根据data中的「计算序列.csv」中的内容，按照顺序不断生成新的SkillNode。
    APL模式下，它会根据APL的代码，根据逻辑生成新的SkillNode。
    而在合轴模式（SWAP_CANCEL）下，它会根据适当地提前一些tick，生成新的SkillNode。
    """
    def __init__(self, *args: Skill):
        self.preload_data = PreloadData(*args)
        self.skills_queue: LinkedList = self.preload_data.skills_queue
        if not APL_MODE and SWAP_CANCEL:
            raise Warning("本次模拟开启了合轴模式但是没有开启APL模式！可能导致很多BUG！合轴模式下-强烈-建议开启APL模式！")
        self.preloaded_action_list = []                        # 记录本tick需要预载的动作（包含主动 和 强制）
        self.force_add_box = defaultdict(dict)           # 记录强制预载的skill_node-->{CID: {tick: skill_tag(str)}}
        if SWAP_CANCEL:
            self.start_tick_stamps = defaultdict(int)             # 记录每个角色动作的起始时间
            self.end_tick_stamps = defaultdict(int)              # 记录每个角色动作的结束时间
        if APL_MODE:
            self.apl_action_list = APLParser(file_path=APL_PATH).parse()
            self.apl_executor = APLExecutor(self.apl_action_list)
            self.apl_preload_tick = 0
            self.apl_next_end_tick = 0

    def __str__(self):
        return f"Preload Data: \n{self.preload_data.preloaded_action}"

    def do_preload(self, tick: int, enemy: Enemy | None = None, name_box: list[str] | None = None, char_data=None):
        """
        根据APL以及合轴规则，产出最高优先级的动作。
        """
        if SWAP_CANCEL:
            self.preload_action_by_swap_cancel(char_data, name_box, tick, enemy)
        else:
            self.preload_action_by_sequence(char_data, name_box, tick)

    def preload_action_by_sequence(self, char_data, name_box, tick):
        """
        非合轴模式下生成、更新skill_node的逻辑！
        """
        if self.preload_data.current_node is None and self.apl_next_end_tick <= tick:
            """
            由于，第一个动作在第0帧进行Preload后，会立刻被拿去算，所以，在第1帧，程序就会检测到self.current_node is None，遂开始生成新的Node。
            这会导致APL模块在根据 当前tick的状态 去生成一个未来的动作，在诸如QTE、或是其他特殊手法的场合，会导致技能重复释放等问题。
            所以，在20241226的更新中，我们为生成新Node的逻辑新增了  self.apl_next_end_tick <= tick 的判定条件，
            确保上一个动作彻底结束了（子标签为end），才会生成新动作。
            这主要是为了屏蔽第一个动作和第二个动作在第0帧、第1帧进行preload的问题。
            """
            if APL_MODE:
                # When APL is Enabled, we will use APL to preload skills.
                apl_output_skill: str = self.apl_executor.execute(mode=0)  # Try to get the next skill to preload.
                node: SkillNode = SkillsQueue.spawn_node(
                    apl_output_skill,
                    self.apl_preload_tick,
                    *self.preload_data.skills)  # generate a SkillNode through the tag and preload tick.
                self.skills_queue.insert(node)  # Insert the node into the queue.
                self.apl_preload_tick += node.skill.ticks  # Update the preload tick.
                self.apl_next_end_tick = node.end_tick
            this_node = self.skills_queue.pop_head()
            self.preload_data.current_node = this_node
        else:
            this_node = self.preload_data.current_node
        if this_node is not None:
            self.add_node(char_data, name_box, tick, this_node)

    def process_node(self, char_data, name_box, skill_tag, tick):
        """
        该函数的作用是根据输入的skill_tag，执行skill_node的添加。
        这里的mode主要是给add_node函数用的，用于区分是主动添加还是被动添加。
        """
        self.preload_node(skill_tag, tick)
        if self.preloaded_action_list:
            self.add_node(char_data, name_box, tick, node=None)

    def preload_action_by_swap_cancel(self, char_data, name_box, tick, enemy: Enemy):
        """
        合轴模式下的另一种preload逻辑，也是swap功能的主函数，共有以下几个步骤：
        0、初始化、准备工作（主要是常用变量和信息的提取），并且运行一次APL，获得当前tick最高优先级的动作名，即skill_tag
        1、处理skill_tag为首个动作的情况
        2、判断skill_tag所隶属的角色是否有空——主要影响current_char_available的值。
        3、遍历所有角色的强制预载动作，如果有符合条件的，则进行预载，若skill_tag所属的角色也干了，那么就修改current_char_available为False
        4、处理主动动作。由于第三步是每个tick都需要进行的，所以哪怕当前角色没空，也不能立刻return，
            所以设计了一个current_char_available变量，来储存前三步的判定结果。
            在本步骤中，如果current_char_available为True，再执行后续步骤。（分支逻辑比较复杂，这里不过多赘述，欲知详情请直接查看代码分支中的注释）
        """
        if not APL_MODE:
            '''
            尝试关了一下APL单独跑这个合轴模式，根本用不了，太爆炸了
            所以这里直接改报错了。目前没精力让这个合轴功能去适配经典模式，暂时先这样。
            '''
            raise ValueError("合轴模式下必须开启APL模式！")
        # 0、初始化、准备工作、获取skill_tag
        current_char_available = True   # 当前角色是否可以进行下一个动作
        skill_tag: str = self.apl_executor.execute(mode=0)
        current_node_CID = int(skill_tag[:4])

        # 1、处理skill_tag为首个动作的情况
        if self.preload_data.last_node is None and self.preload_data.current_node is None:
            """首个动作的处理"""
            self.process_node(char_data, name_box, skill_tag, tick)
            self.preload_data.current_on_field_node_tag = skill_tag
            return

        # 敌人进攻与角色响应模块
        stun_status: bool = stun_judge(enemy)
        if not stun_status and ENEMY_RANDOM_ATTACK:
            enemy_attack_action = enemy.attack_method.select_action(tick)
            if enemy_attack_action is not None:
                print(enemy_attack_action.tag)

        # 2、判断skill_tag所隶属的角色是否有空
        if self.end_tick_stamps[current_node_CID] > tick:
            # 如果当前角色已经有动作，那么skill_tag就无法作为当前角色的下一个动作
            current_char_available = False

        # 3、处理强制预载动作
        for char_CIDs, mission_dict in self.force_add_box.items():
            """优先处理强制添加类的技能（这个环节无关skill_tag的具体内容，每个tick都是需要执行的）"""
            if not mission_dict:
                # 若当前角色没有强制预载动作任务，那就直接跳过
                continue
            for force_add_ticks in list(mission_dict.keys()):
                if force_add_ticks <= tick:
                    nodes_tag = mission_dict.pop(force_add_ticks)
                    if char_CIDs == current_node_CID:
                        current_char_available = False
                        self.preload_data.current_on_field_node_tag = skill_tag
                    self.process_node(char_data, name_box, nodes_tag, tick)

        # 4、处理主动动作
        if current_char_available:
            """
            如果经过了所有强制预载动作的检查后，curreent_char_available仍为True，
            说明当前tick，APL抛出的skill_tag理论上就可以作为当前角色的下一个动作，
            但是此时还是不能无脑执行process_node函数进行添加，
            因为还需要针对当前node的情况进行更加细致的判断。
            """
            if self.preload_data.current_node.skill_tag[:4] == skill_tag[:4]:
                """
                角色CID无变化，说明主动动作skill_tag并未涉及切人。那么直接执行process_node函数即可。
                因为在之前就已经判断过了skill_tag所属的角色是否有正在进行的主动动作，
                既然已经进入到了这个分支，那么说明current_char_available已经为True，也就是说当前角色是空闲的，
                所以此处不需要再进行相同的判断，直接执行process_node即可。
                """
                self.process_node(char_data, name_box, skill_tag, tick)
                self.preload_data.current_on_field_node_tag = skill_tag
            else:
                """
                但若是角色CID发生了变化，说明主动动作skill_tag需要切人。
                那么这里就需要执行切人判定逻辑。主要是集中在lag_time的判定上。
                """
                should_swap = self.judge_swap_cancel_node(tick, skill_tag, mode=2)
                if should_swap:
                    self.process_node(char_data, name_box, skill_tag, tick)
                    self.preload_data.current_on_field_node_tag = skill_tag

    def add_node(self, char_data, name_box, tick, node: SkillNode | None):
        """
        正式向self.preloaded_action_list中添加预载动作的函数。
            注意，该函数只负责添加主动动作，不负责添加被动动作。
            被动动作的处理逻辑是绕开current_node和last_node、而直接添加到preloaded_action_list中的
        这个函数既要服务于老模式，又要服务于新的SWAP_CANCEL模式。
        """
        if node and isinstance(node, SkillNode):
            # 随技能Preload技能而起的逻辑
            if node.preload_tick <= tick:
                # Preload技能逻辑
                watchdog.watch_reverse_order(node, self.preload_data.last_node)
                self.preload_data.preloaded_action.add(node)
                report_to_log(f"[PRELOAD]:In tick: {tick}, {node.skill_tag} has been preloaded")
                if SWAP_CANCEL:
                    """
                    current_node与last_node的含义是“全队的当前动作/上一个动作”，这是包含了主动动作和强制预载动作的；
                    而为了让APL模块（特别是其after功能）能够正确识别到某角色的当前/上一个技能，
                    我们先要在这里同步修改preload_data下面的两个personal字典。
                    """
                    CID = int(node.skill_tag[:4])
                    self.preload_data.last_node = self.preload_data.current_node
                    self.preload_data.current_node = node
                    self.preload_data.personal_last_node[CID] = self.preload_data.personal_current_node[CID]
                    self.preload_data.personal_current_node[CID] = node
                else:
                    self.preload_data.last_node = node
                    self.preload_data.current_node = None
                # Preload 结算特殊资源、能量、喧响
                for char in char_data.char_obj_list:
                    char.update_sp_and_decibel(node)
                    char.special_resources(node)
                # 切人逻辑
                if (isinstance(name_box, list)
                        and all(isinstance(name, str) for name in name_box)
                        and node.skill.on_field):
                    self. switch_char(name_box, node)
                self.process_force_add_skill_tag(node)

        # 递归部分，
        # 虽然随着本函数的不断修改，递归部分的作用很小了，甚至在主函数逻辑重写后，就很少会发生递归调用了
        # 但是为了保留代码的可拓展性和完整性，我还是保留了这部分代码。
        elif node is None:
            if self.preloaded_action_list:
                nodes = self.preloaded_action_list.pop()
                if isinstance(nodes, SkillNode):
                    self.add_node(char_data, name_box, tick, nodes)
                else:
                    raise TypeError("递归过程中传入的参数不是SkillNode对象！")
                self.add_node(char_data, name_box, tick, node=None)
        else:
            raise TypeError("传入的参数既不是SkillNode对象也不是列表！")

    def process_force_add_skill_tag(self, node):
        """
        该函数的作用是，检查传入的node是否存在后续强制添加的技能，
        如果存在，则将其录入到self.force_add_box中。
        ================================================
        该函数只在add_node的最后一步调用，所以，每次执行add_node函数，都只会处理处理一个强制添加技能，
        因为每个技能最多只会存在一个后续强制添加技能。
        如果技能A后续的强制添加涉及到多个技能，
        则这些技能只会在上一个强制添加技能被添加后，才会被添加到self.force_add_box中，
        而不是在A技能被添加后立刻全部添加。
        """
        if node.skill.follow_up is not np.nan:
            """
            存在后续node
            """
            follow_up_tag: str = self.preload_data.current_node.skill.follow_up
            follow_up_skill_CID = int(follow_up_tag[:4])
            follow_up_skill_add_tick = self.preload_data.current_node.end_tick
            if self.preload_data.current_node.end_tick < self.end_tick_stamps[follow_up_skill_CID]:
                """
                这里检查的情况是：如果A角色的技能会强制预载B角色的技能时，
                那么B角色自己的end_tick_stamps中的记录的值（也就是B角色上一个动作的结束时间），
                应该小于A角色的当前动作的结束时间（也就是被强制预载的B的技能的执行时间）；
                换一种说法，这里是要确保：B角色技能在强制预载时，并没有动作存在即可。
                如果程序流程合理，这个分支是不会被执行的。所以，这个分支是一个报错分支。
                """
                raise ValueError(
                    f"出现了不应该出现的情况！技能{follow_up_tag}理应在{self.preload_data.current_node.skill_tag}之后、于{follow_up_skill_add_tick}执行，但是此时角色{follow_up_skill_CID}尚有动作存在。")
            self.force_add_box[follow_up_skill_CID][follow_up_skill_add_tick] = follow_up_tag

    def preload_node(self, skill_tag, tick):
        """
        预载skill_node的函数。该函数负责通过输入的skill_tag以及tick，构建SkillNode对象，
        并且更新self下的start_tick_stamps和end_tick_stamps，
        最后，将构造出的node放入self.preloaded_action_list中。
        """
        CID = int(skill_tag[:4])
        node = SkillsQueue.spawn_node(skill_tag, tick, *self.preload_data.skills)
            # 确定了合轴操作的执行后，首先更新start_tick 与end_tick。
        self.update_preload_info(info_tuple=(CID, tick), mode=0)
        self.update_preload_info(info_tuple=(CID, node.end_tick), mode=1)
        self.preloaded_action_list.append(node)

    def update_preload_info(self,  *,  info_tuple: tuple[int, int], mode: int):
        """更新预载信息，主要是记录每个角色的起始时间和结束时间。"""
        if mode == 0:
            """处理preload tick的更新。"""
            self.start_tick_stamps[info_tuple[0]] = info_tuple[1]
        elif mode == 1:
            """处理end tick的更新。"""
            self.end_tick_stamps[info_tuple[0]] = info_tuple[1]
        else:
            raise ValueError("mode参数错误！")

    def judge_swap_cancel_node(self, tick: int, skill_tag: str, *, mode: int):
        """用于判断当前构造出的node是否能够用来合轴"""
        if mode in [0, 1]:      # 目前，这个分支已经被废弃了，基本用不到（主函数结构改变之后，这个分支的必要性就已经不存在）
            """
            第一个动作 或者 同角色的动作，不用判断，默认通过。
            因为这两种情况涉及的判断是前置的，早就已经完成了，
            """
            return True
        elif mode == 2:     # 这个分支是目前的主要分支
            """
            当涉及到切人动作时，需要额外判断当前技能是否能够被合轴。
            如果不能，那么就算前置的合轴条件（主要是针对时间[lag_time]的判定）都满足，也不能进行合轴
            """
            current_node_CID = int(skill_tag[:4])
            lag_time = self.spawn_lag_time(self.preload_data.current_node)
            current_node = self.preload_data.current_node
            if current_node.end_tick <= tick:
                """
                若是当前技能已经结束，那么就算是涉及到切人动作，也不需要进行额外判断了，直接返回TRUE即可。
                
                PS：
                这个if分支看似普通，甚至多余，但是却是swap_cancel中极其重要和底层的一个分支。
                为了确定该分支位置以及功能，我前后总计耗费了10个多小时来进行研究和debug，期间swap_cancel主函数甚至经历了重写，
                太痛苦了以至于必须要吐槽和解释一下。
                
                在这个位置对endtick进行判断并非多余，而是必须。
                因为在swap_cancel模式下，基本不会存在“前后两个技能涉及切人，但是后者会乖乖等到前者结束后才抛出”的情况，
                若是同角色的两个不同技能，那么就不会调用本函数，更不会进入这个分支。
                这个分支的存在，主要就是为了处理类似于“雅正在打连携技A，后面还会接着打B和C，但是此时丽娜发现buff断了，想要切上来A一下”这类情况。
                我们希望雅在ABC都打完后，丽娜再切上来。
                但是如果没有这个分支，那么self.preload_data.current_node就会永远定格在C上，然后永远会因为C技能是无法切人的技能，而导致输出False，从而导致这个tick无法抛出技能
                整个Preload阶段就会卡在C技能这里，后面再也打不出一个技能来，全队停转
                所以，这个地方的结束判断是必须的，它能够让主函数在被连携技、大招等无法合轴的技能阻滞时，及时重启.
                """
                return True
            if current_node.skill.swap_cancel_ticks == current_node.skill.ticks:
                """
                此处的筛选会选出全部合轴滞后时间与自身持续时间相同的技能，
                这些技能是不能合轴的。
                """
                return False
            if tick - self.start_tick_stamps.get(current_node_CID, 0) <= 60:
                """如果当前需要切出来的角色，在60ticks内刚刚才切出来过，那么就意味着该角色还未完全退场，也就是常说的切人CD没好。"""
                if all(x not in skill_tag for x in ['Aid', '_QTE']):
                    """这里检测的是一些无视CD的切人行为。比如QTE和支援类技能。"""
                    # TODO：首先，这里的支援类技能的抛出，完全依赖于APL的“after”条件的控制，
                    #  但是实际上，支援类技能的抛出，本应是“快速支援亮起”，目前这个功能暂且没有实现。
                    #  也就是说，以后在APL中，快速支援的抛出应该是利用status模块来查询指定角色的“快速支援的亮起状态”，而非用after模块来粗暴对比skill_tag。
                    return False
            if current_node.preload_tick + current_node.skill.swap_cancel_ticks + lag_time > tick:
                return False
            else:
                return True
        else:
            raise ValueError("mode参数错误！")

    @staticmethod
    def spawn_lag_time(node: SkillNode):
        """
        生成滞后时间，关于函数中两个参数SCK和SCLT的含义，请参考本文件开头的注释。
        这里返回的lag_time是经过向上取整的。
        """
        lag_time = math.ceil(min(node.skill.ticks * SCK, SCLT))
        return lag_time

    @staticmethod
    def switch_char(name_box: list[str], this_node: SkillNode) -> None:
        name_index = name_box.index(this_node.char_name)
        # 更改前台角色（切人逻辑）
        if name_index == 1:
            name_switch = name_box.pop(0)
            name_box.append(name_switch)
        elif name_index == 2:
            name_switch = name_box.pop(0)
            name_box.append(name_switch)
            name_switch = name_box.pop(0)
            name_box.append(name_switch)
