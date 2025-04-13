import sys


def get_game_state():
    try:
        # 延迟从 sys.modules 获取字典A，假设 main 模块中已定义字典 A
        main_module = sys.modules['simulator.main_loop']
        if main_module is None:
            raise ImportError("Main module not found.")
        game_state = main_module.game_state  # 获取 main 中的 A
    except Exception as e:
        print(f"Error loading dictionary A: {e}")
    return game_state