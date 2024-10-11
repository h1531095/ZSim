import pandas as pd
def init_weapon_primitive(weapon:str, weapon_level:int) -> None:
        """
        初始化武器属性
        """
        if weapon is not None:
            df = pd.read_csv('./data/weapon.csv')
            row_5 = df[df['weapon_ID'] == weapon] # 找到所有包含此武器的行
            if not row_5.empty:     # 检查是否找到匹配项
                row = row_5[row_5['level'] == weapon_level].to_dict('records') # 找到对应精炼等级的行，并转化为字典
                if row:
                    row = row[0]
                    print(row)
                else:
                    raise ValueError(f"请输入正确的精炼等级")
            else:
                raise ValueError(f"请输入正确的武器名称")
            
init_weapon_primitive('深海访客', 1)