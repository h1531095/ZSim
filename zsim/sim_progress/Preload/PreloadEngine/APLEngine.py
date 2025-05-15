from .BasePreloadEngine import BasePreloadEngine
from sim_progress.Preload.APLModule import APLManager
from define import APL_PATH
from sim_progress.Preload import SkillsQueue, SkillNode


class APLEngine(BasePreloadEngine):
    """用于调动APL模块的Preload引擎"""

    def __init__(self, data, apl_path: str | None = None):
        super().__init__(data)
        self.apl_manager = APLManager()

        if apl_path is None:
            apl_path = APL_PATH
        elif not apl_path.endswith(".txt") or not apl_path.endswith(".toml"):
            # 如果提供的是APL名称而不是完整路径
            found_path = self.apl_manager.get_apl_path(apl_path)
            if found_path:
                apl_path = found_path

        self.apl = self.apl_manager.load_apl(apl_path, mode=0)

    def run_myself(self, tick) -> SkillNode | None:
        """APL模块运行的最终结果：技能名、最终通过的APL代码优先级"""
        skill_tag, apl_priority, apl_unit = self.apl.execute(tick, mode=0)
        if skill_tag == "wait":
            return None
        node = SkillsQueue.spawn_node(
            skill_tag,
            tick,
            self.data.skills,
            active_generation=True,
            apl_priority=apl_priority,
            apl_unit=apl_unit,
        )
        return node

    def reset_myself(self):
        """APL模块暂时没有任何需要Reset的地方！"""
        pass

    def get_available_apls(self) -> list[str]:
        """获取所有可用的APL文件列表"""
        return self.apl_manager.list_available_apls()
