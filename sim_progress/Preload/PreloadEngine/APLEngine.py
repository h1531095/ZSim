from .BasePreloadEngine import BasePreloadEngine
from sim_progress.Preload.APLModule import APLParser, APLClass
from define import APL_PATH


class APLEngine(BasePreloadEngine):
    """用于调动APL模块的Preload引擎"""
    def __init__(self, data):
        super().__init__(data)
        self.apl = APLClass(APLParser(file_path=APL_PATH).parse(mode=0))

    def run_myself(self, tick) -> tuple[str, int]:
        """APL模块运行的最终结果：技能名、最终通过的APL代码优先级"""
        return self.apl.execute(tick, mode=0)

    def reset_myself(self):
        """APL模块暂时没有任何需要Reset的地方！"""
        pass
