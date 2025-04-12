from sim_progress.Preload import SkillNode
from .utils.filters import _skill_node_filter
from .character import Character

class Jane(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.passion: float = 0.0  # 狂热，0.0 ~ 100.0
        self.passion_stream: bool = False  # 狂热心流状态
        self.salchow_jump: int = 0  # 萨霍夫跳剩余次数

    def special_resources(self, *args, **kwargs) -> None:
        """模拟简的狂热心流"""
        # 输入类型检查
        skill_nodes: list[SkillNode] = _skill_node_filter(*args, **kwargs)
        for node in skill_nodes:
            if node.char_name != '简':
                continue
            
            labels = node.labels if node.labels is not None else {}
            passion_get = labels.get('passion_get', 0)
            passion_consume = labels.get('passion_consume', 0)
            self.passion_core(passion_get, passion_consume)
            

    def reset_passion(self) -> None:
        """重置狂热"""
        self.passion = 0.0
        self.passion_stream = False

    def check_salchow_jump(self) -> None:
        """检查萨霍夫跳次数"""
        max_jumps = 1 if self.cinema == 0 else 2
        if self.salchow_jump > max_jumps:
            raise ValueError("萨霍夫跳次数错误")
    
    def passion_core(self, passion_get: float, passion_consume: float) -> None:
        """狂热核心计算"""
        if not self.passion_stream:
            self.passion += passion_get
            if self.passion >= 100:
                self.passion = 100
                self.passion_stream = True
        else:
            self.passion -= passion_consume
            if self.passion <= 0:
                self.passion = 0
                self.passion_stream = False
    
    def get_resources(self) -> tuple[str, float]:
        return "狂热值", self.passion
    
    def get_special_stats(self, *args, **kwargs) -> dict[str, int | float | bool]:
        """获取简的特殊状态"""
        return {
            "狂热值": self.passion,
            "狂热心流": self.passion_stream,
            "萨霍夫跳剩余次数": self.salchow_jump
        }