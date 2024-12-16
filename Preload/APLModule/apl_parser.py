class APLParser:
    def __init__(self, apl_code: str):
        self.apl_code = apl_code

    def parse(self):
        """
        apl_code本来是一大串str，现在要通过这个函数，将其变为dict模式。
        action下面存的应该是技能ID或是Skill的Triggle_Buff_Level，
        而conditions下面存的则是发动动作的条件。
        这一步应该在初始化的时候执行。
        """
        actions = []
        for line in self.apl_code.splitlines():
            # 去除空白字符并清理行内注释
            line = line.split("#", 1)[0].strip()
            # 忽略空行
            if not line:
                continue
            try:
                # 1. 按 '|' 分割字符串
                parts = line.split('|')
                if len(parts) < 3:
                    raise ValueError(f"Invalid format: {line}")

                # 2. 提取 CID
                CID = parts[0]

                # 3. 提取 action_name 和条件部分
                action_name = parts[2]
                conditions = parts[3:]  # 从第4个元素开始作为条件列表

                # 4. 记录解析后的数据
                actions.append({
                    "CID": CID,
                    "action": action_name.strip(),
                    "conditions": [cond.strip() for cond in conditions if cond.strip()]
                })
            except Exception as e:
                print(f"Error parsing line: {line}, Error: {e}")
                continue

        return actions


if __name__ == "__main__":
    apl_code = """
    1091|actions+=|1091_NA_1|condition1|condition2
    1091|actions+=|1091_NA_2|condition1
    1091|actions+=|1091_NA_3|condition1|condition2|condition3
    """
    actions_list = APLParser(apl_code).parse()
    print(actions_list)
