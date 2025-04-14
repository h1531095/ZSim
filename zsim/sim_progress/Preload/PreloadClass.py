from sim_progress.Preload.PreloadDataClass import PreloadData
from define import SWAP_CANCEL
from .PreloadStrategy import SwapCancelStrategy


class PreloadClass:
    def __init__(self, skills, *, load_data, **kwargs):
        apl_path = kwargs.get("apl_path", None)
        self.preload_data = PreloadData(skills, load_data=load_data)
        if SWAP_CANCEL:
            # 合轴模式，使用输入的APL路径
            self.strategy = SwapCancelStrategy(self.preload_data, apl_path) 
        else:
            self.strategy = None

    def do_preload(self, tick, enemy, name_box, char_data):
        if self.preload_data.name_box is None:
            self.preload_data.name_box = name_box
        if self.preload_data.char_data is None:
            self.preload_data.char_data = char_data
        self.strategy.generate_actions(enemy, tick)

    def reset_myself(self, namebox):
        self.preload_data.reset_myself(namebox)
