from .BasePreloadEngine import BasePreloadEngine
from sim_progress.Preload.APLModule import APLParser, APLClass
from define import APL_PATH
from sim_progress.Preload import SkillsQueue, SkillNode


class APLEngine(BasePreloadEngine):
    """用于调动APL模块的Preload引擎"""
    def __init__(self, data, apl_path: str | None):
        super().__init__(data)
        if apl_path is None:
            apl_path = APL_PATH
        self.apl = APLClass(APLParser(file_path=apl_path).parse(mode=0))

    def run_myself(self, tick) -> SkillNode:
        """APL模块运行的最终结果：技能名、最终通过的APL代码优先级"""
        skill_tag, apl_priority = self.apl.execute(tick, mode=0)
        node = SkillsQueue.spawn_node(skill_tag, tick, self.data.skills, active_generation=True, apl_priority=apl_priority)
        return node

    def reset_myself(self):
        """APL模块暂时没有任何需要Reset的地方！"""
        pass
