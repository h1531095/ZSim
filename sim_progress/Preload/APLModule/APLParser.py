import os.path
from typing import Sequence


class APLParser:
    def __init__(self, apl_code: str | None = None, file_path: str | None = None):
        # 如果传入APL代码，使用它；如果传入文件路径，则从文件中读取
        if apl_code is not None:
            self.apl_code = apl_code
        elif file_path is not None:
            self.apl_code = self._read_apl_from_file(file_path)
        else:
            raise ValueError("Either apl_code or file_path must be provided.")

    @staticmethod
    def _read_apl_from_file(file_path: str) -> str:
        """从文件中读取APL代码。"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return ""

    def parse(self, mode: int) -> list[dict[str, Sequence[str]]]:
        """
        apl_code本来是一大串str，现在要通过这个函数，将其变为列表内含多字典的模式。
        action下面存的应该是技能ID或是Skill的Triggle_Buff_Level，
        而conditions下面存的则是发动动作的条件。
        这一步应该在初始化的时候执行。
        """
        actions = []
        priority = 0
        if mode == 0:
            priority = 1
            selected_char_cid = []
        for line in self.apl_code.splitlines():
            # 去除空白字符并清理行内注释
            line = line.split("#", 1)[0].strip()
            # 忽略空行
            if not line:
                continue
            try:
                if mode == 0:
                    # 0. 更新CID，
                    if int(line[:4]) not in selected_char_cid:
                        selected_char_cid.append(int(line[:4]))
                # 1. 按 '|' 分割字符串
                parts = line.split('|')
                if len(parts) < 3:
                    raise ValueError(f"Invalid format: {line}")

                # 2. 提取 CID
                CID = parts[0]
                apl_type = parts[1]
                # 3. 提取 action_name 和条件部分
                action_name = parts[2]
                conditions = parts[3:]  # 从第4个元素开始作为条件列表

                # 4. 记录解析后的数据
                actions.append({
                    "CID": CID,
                    "type": apl_type.strip(),
                    "action": action_name.strip(),
                    "conditions": [cond.strip() for cond in conditions if cond.strip()],
                    "priority": priority
                })
                if mode == 0:
                    priority += 1
            except Exception as e:
                print(f"Error parsing line: {line}, Error: {e}")
                continue
        if mode == 0:
            """
            这个if分枝的功能是：部分角色可能因角色特性而存在一些默认优先级最高的行为，
            在APL代码进行解析和拆分时，这些优先级最高的代码会被安插在所有APL的最前端。
            如果某角色存在着优先级永远最高的默认手法，则可以用这个功能实现，把对应的APL逻辑写到DefaultConfig中即可。
            但是注意，DefaultConfig中的所有APL代码均会以最高优先级进行执行，
            所以一般情况下还是推荐对APL进行全面定制
            """
            for cid in selected_char_cid:
                dir_path = './data/APLData/default_APL'
                default_file_name = f'{cid}.txt'
                full_path = dir_path + '/' + default_file_name
                if not os.path.isfile(full_path):
                    continue
                else:
                    default_action = APLParser(file_path=full_path).parse(mode=1)
                    actions[:0] = default_action
        return renumber_priorities(actions)


def renumber_priorities(data_list):
    seen = set()  # 记录已使用的优先级值
    current_max = -1  # 跟踪当前最大有效优先级

    for item in data_list:
        original = item["priority"]

        # 策略1：优先保持原有数值（如果未被占用）
        if original not in seen:
            seen.add(original)
            current_max = max(current_max, original)
        # 策略2：分配当前最大+1（当原值已被占用时）
        else:
            current_max += 1
            item["priority"] = current_max
            seen.add(current_max)

    return data_list


if __name__ == "__main__":
    from define import APL_PATH
    code = '1211|action+=|1211_NA_1|status.enemy:stun==True|!buff.1091:exist→Buff-角色-丽娜-核心被动-穿透率==True'
    # actions_list = APLParser(file_path=APL_PATH).parse(mode=0)
    actions_list = APLParser(apl_code=code).parse(mode=0)
    for sub_dict in actions_list:
        print(sub_dict)
