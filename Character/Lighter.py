import sys

from Preload import SkillNode
from Report import report_to_log
from .character import Character
from .filters import _skill_node_filter


class Lighter(Character):
    def __init__(self,
                 name: str = '', CID: int = None,  # 角色名字和CID-必填至少一个
                 weapon=None, weapon_level=1,  # 武器名字-选填项
                 equip_set4=None, equip_set2_a=None, equip_set2_b=None, equip_set2_c=None,  # 驱动盘套装-选填项
                 drive4=None, drive5=None, drive6=None,  # 驱动盘主词条-选填项
                 scATK_percent=0, scATK=0, scHP_percent=0, scHP=0, scDEF_percent=0, scDEF=0, scAnomalyProficiency=0,
                 scPEN=0, scCRIT=0,  # 副词条数量-选填项
                 sp_limit=120  # 能量上限-默认120
                 ):
        super().__init__(
                name, CID,
                weapon, weapon_level,
                equip_set4, equip_set2_a, equip_set2_b, equip_set2_c,
                drive4, drive5, drive6,
                scATK_percent, scATK, scHP_percent, scHP, scDEF_percent, scDEF, scAnomalyProficiency, scPEN, scCRIT,
                sp_limit)
        self.morale: int = 4000  # 士气初始40 整形为4000
        self.last_tick: int = 0

    def special_resources(self, *args, **kwargs) -> None:
        """
        模拟莱特的士气机制

        判断目前的时间，与上一次激活时做差，并更新士气值
        确保士气值不超过100

        将传入的skill_node消耗的能量转为士气值
        需要消耗士气时对应扣除
        """
        # 输入类型检查
        skill_nodes: list[SkillNode] = _skill_node_filter(*args, **kwargs)
        # 对输入的skill_node进行遍历
        for node in skill_nodes:
            # 累加逻辑
            if self.morale < 10000:
                # 消耗能量及时更新
                sp_consume = node.skill.sp_consume
                if sp_consume > 0:
                    self.morale += sp_consume * 26

            if '1161' not in node.skill_tag:
                continue
            # 递减逻辑
            if node.skill_tag == '1161_NA_5_SH_EX':
                self.morale -= 1000
                report_to_log(f"[Character] 莱特的士气消耗至 {self.morale / 100:.2f}")
            elif node.skill_tag == '1161_NA_5_CoH_EX':
                self.morale -= 9000
                # print(f'检测到士气消耗动作，当前士气（处理前）：{self.morale}（处理后）：{self.morale / 100:.2f}')
                # TODO：这里需要一个函数来控制“夹断”技能的数据。思路：\n
                #       1、根据当前SkillNode类复制一个出来（__dict__），\n
                #       2、根据资源消耗量算出缩放比例，\n
                #       3、根据缩放比例修改新的复制SkillNode的所有数据。\n
                #       4、传给下一个环节。

                # FIXME: 20241208：
                #  观察到莱特的士气貌似只有首轮具有阈值，次轮开始就失效了
                report_to_log(f"[Character] 莱特的士气消耗至 {self.morale / 100:.2f}")


            if self.morale < 0:
                report_to_log(f"[Character] 莱特的士气消耗至 {self.morale / 100:.2f}, 请检查")
                self.morale = 0

        # 时间每 6 ticks 更新
        main_module = sys.modules['__main__']
        tick: int = main_module.tick
        if (minus := tick - self.last_tick) >= 6:
            self.morale += minus // 6 * 29     # 地板除保证整形对齐
            self.last_tick = tick - minus % 6   # 求余以保证余数不计入本次计算
        self.morale = min(self.morale, 10000)

    def get_resources(self, *args, **kwargs) -> tuple[str | None, int | float | None]:
        return '士气', self.morale / 100
