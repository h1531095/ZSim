from define import SWAP_CANCEL


def get_last_action(game_state: dict):
    """
    注意，这个函数获取的应该是上一个主动动作的名称，
    所以，这里调用的是preload_data.current_on_field_node
    """
    if SWAP_CANCEL:
        if game_state is None or game_state['preload'] is None:
            return False
        return game_state['preload'].preload_data.current_on_field_node_tag
    else:
        last_node = getattr(game_state['preload'].preload_data,'last_node', None)
        if last_node is None:
            return None
        output = last_node.skill_tag
        return output

