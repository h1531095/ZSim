from sim_progress.Preload.PreloadDataClass import PreloadData
from define import APL_MODE, SWAP_CANCEL
from .PreloadStrategy import SwapCancelStrategy


class PreloadClass:
    def __init__(self, args):
        self.preload_data = PreloadData(args)
        if SWAP_CANCEL:
            self.strategy = SwapCancelStrategy(self.preload_data)
        else:
            self.strategy = None

    def do_preload(self, tick, enemy, name_box, char_data):
        if self.preload_data.name_box is None:
            self.preload_data.name_box = name_box
        if self.preload_data.char_data is None:
            self.preload_data.char_data = char_data
        self.strategy.generate_actions(enemy, tick)

