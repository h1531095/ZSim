# character_switch.py

def update_index(current_index, length, action):
    # 根据动作类型更新索引
    if action == 'switch':
        return (current_index + 1) % length
    elif action == 'bwswitch':
        return (current_index - 1 + length) % length
    # 如果动作不是 'switch' 或 'bwswitch'，保持索引不变
    return current_index


def get_characters(characterbox_now, index):
    length = len(characterbox_now)
    character_now = characterbox_now[index]
    character_before = characterbox_now[(index - 1 + length) % length]
    character_next = characterbox_now[(index + 1) % length]
    return character_now, character_before, character_next


def process_action(characterbox_now, action, current_index):
    # 更新角色索引
    current_index = update_index(current_index, len(characterbox_now), action)
    # 获取当前、前一个和下一个角色
    return get_characters(characterbox_now, current_index), current_index
