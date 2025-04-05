from pathlib import Path

import pandas as pd
import streamlit as st
import toml

# 页面导航
PAGES = {
    "角色配置": "character_config",
    "模拟器": "simulator",
    "数据分析": "data_analysis",
}

def character_config():
    """角色配置页面"""
    st.title("ZZZ Simulator - 角色配置")
    
    from define import saved_char_config
    
    # 设置默认角色选择
    from lib_webui.constants import default_chars
    if "name_box" in saved_char_config:
        default_chars = saved_char_config["name_box"]

    from lib_webui.constants import char_options, weapon_options, equip_set4_options, equip_set2_options
    # 初始化选择框
    col1, col2, col3 = st.columns(3)
    with col1:
        name_box_0 = [st.selectbox('角色1', char_options, 
                            index=char_options.index(default_chars[0]) if len(default_chars) > 0 else 0, 
                            key='char_select_0')]
    with col2:
        name_box_1 = [st.selectbox('角色2', char_options, 
                            index=char_options.index(default_chars[1]) if len(default_chars) > 1 else 0, 
                            key='char_select_1')]
    with col3:
        name_box_2 = [st.selectbox('角色3', char_options, 
                            index=char_options.index(default_chars[2]) if len(default_chars) > 2 else 0, 
                            key='char_select_2')]
    name_box: list[str] = name_box_0 + name_box_1 + name_box_2

    # 检查是否已选三个角色
    if len(name_box) != 3:
        st.stop()

    # 检查name_box是否有重复项
    if len(name_box) != len(set(name_box)):
        st.error('请选择三个不同的角色')
        st.stop()

    for name in name_box:
        with st.expander(f'{name}的配置'):
            col_weapon, col_level, col_cinema = st.columns(3)
            with col_weapon:
                st.selectbox(f'音擎', weapon_options,
                             index=weapon_options.index(saved_char_config[name]['weapon']) if name in saved_char_config else 0, 
                             key=f'{name}_weapon')
            with col_level:
                st.number_input(f'音擎精炼等级', min_value=1, max_value=5, 
                              value=saved_char_config[name]['weapon_level'] if name in saved_char_config else 1, 
                              key=f'{name}_weapon_level')
            with col_cinema:
                st.number_input(f'影画等级', min_value=0, max_value=6, 
                              value=saved_char_config[name]['cinema'] if name in saved_char_config else 0, 
                              key=f'{name}_cinema_level')
            
            equip_style = st.radio(f'驱动盘搭配方式', ['4+2', '2+2+2'], 
                                 index=0 if name not in saved_char_config or 'equip_style' not in saved_char_config[name] else (0 if saved_char_config[name]['equip_style'] == '4+2' else 1),
                                 key=f'{name}_equip_style')
            col1, col2 = st.columns(2)
            with col1:
                if equip_style == '4+2':
                    st.selectbox(f'四件套', equip_set4_options, 
                                     index=equip_set4_options.index(saved_char_config[name]['equip_set4']) if name in saved_char_config and 'equip_set4' in saved_char_config[name] else 0, 
                                     key=f'{name}_equip_set4')
                    st.selectbox(f'二件套', equip_set2_options, 
                                     index=equip_set2_options.index(saved_char_config[name]['equip_set2_a']) if name in saved_char_config else 0, 
                                     key=f'{name}_equip_set2')
                else:
                    st.selectbox(f'二件套A', equip_set2_options, 
                                     index=equip_set2_options.index(saved_char_config[name]['equip_set2_a']) if name in saved_char_config else 0, 
                                     key=f'{name}_equip_set2A')
                    st.selectbox(f'二件套B', equip_set2_options, 
                                     index=equip_set2_options.index(saved_char_config[name]['equip_set2_b']) if name in saved_char_config and 'equip_set2_b' in saved_char_config[name] else 0, 
                                     key=f'{name}_equip_set2B')
                    st.selectbox(f'二件套C', equip_set2_options, 
                                     index=equip_set2_options.index(saved_char_config[name]['equip_set2_c']) if name in saved_char_config and 'equip_set2_c' in saved_char_config[name] else 0, 
                                     key=f'{name}_equip_set2C')
            with col2:
            # 主词条选择
                from lib_webui.constants import main_stat4_options, main_stat5_options, main_stat6_options
                st.selectbox(f'四号位主词条', main_stat4_options, 
                                     index=main_stat4_options.index(saved_char_config[name]['drive4']) if name in saved_char_config else 0, 
                                     key=f'{name}_main_stat4')
                st.selectbox(f'五号位主词条', main_stat5_options, 
                                     index=main_stat5_options.index(saved_char_config[name]['drive5']) if name in saved_char_config else 0, 
                                     key=f'{name}_main_stat5')
                st.selectbox(f'六号位主词条', main_stat6_options, 
                                     index=main_stat6_options.index(saved_char_config[name]['drive6']) if name in saved_char_config else 0, 
                                     key=f'{name}_main_stat6')
            
            # 副词条数量输入
            from lib_webui.constants import sc_max_value
            st.text(f'副词条数量：')
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.number_input(f'攻击力%', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scATK_percent'] if name in saved_char_config else 0, key=f'{name}_scATK_percent')
                st.number_input(f'攻击力', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scATK'] if name in saved_char_config else 0, key=f'{name}_scATK')
            with col2:
                st.number_input(f'生命值%', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scHP_percent'] if name in saved_char_config else 0, key=f'{name}_scHP_percent')
                st.number_input(f'生命值', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scHP'] if name in saved_char_config else 0, key=f'{name}_scHP')
            with col3:
                st.number_input(f'防御力%', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scDEF_percent'] if name in saved_char_config else 0, key=f'{name}_scDEF_percent')
                st.number_input(f'防御力', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scDEF'] if name in saved_char_config else 0, key=f'{name}_scDEF')
            with col4:
                st.number_input(f'暴击率', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scCRIT'] if name in saved_char_config else 0, key=f'{name}_scCRIT')
                st.number_input(f'暴击伤害', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scCRIT_DMG'] if name in saved_char_config else 0, key=f'{name}_scCRIT_DMG')
            with col5:
                st.number_input(f'异常精通', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scAnomalyProficiency'] if name in saved_char_config else 0, key=f'{name}_scAnomalyProficiency')
                st.number_input(f'穿透值', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scPEN'] if name in saved_char_config else 0, key=f'{name}_scPEN')
            
            # 暴击配平算法开关
            st.checkbox(f'使用暴击配平算法', value=saved_char_config[name]['crit_balancing'] if name in saved_char_config else False, key=f'{name}_crit_balancing')
            
        # 将角色配置整理为字典
        char_config = {
            'name': name,
            'weapon': st.session_state[f'{name}_weapon'],
            'weapon_level': st.session_state[f'{name}_weapon_level'],
            'cinema': st.session_state[f'{name}_cinema_level'],
            'crit_balancing': st.session_state[f'{name}_crit_balancing'],
            'scATK_percent': st.session_state[f'{name}_scATK_percent'],
            'scATK': st.session_state[f'{name}_scATK'],
            'scHP_percent': st.session_state[f'{name}_scHP_percent'],
            'scHP': st.session_state[f'{name}_scHP'],
            'scDEF_percent': st.session_state[f'{name}_scDEF_percent'],
            'scDEF': st.session_state[f'{name}_scDEF'],
            'scAnomalyProficiency': st.session_state[f'{name}_scAnomalyProficiency'],
            'scPEN': st.session_state[f'{name}_scPEN'],
            'scCRIT': st.session_state[f'{name}_scCRIT'],
            'scCRIT_DMG': st.session_state[f'{name}_scCRIT_DMG'],
            'drive4': st.session_state[f'{name}_main_stat4'],
            'drive5': st.session_state[f'{name}_main_stat5'],
            'drive6': st.session_state[f'{name}_main_stat6'],
            'equip_style': st.session_state[f'{name}_equip_style']
        }
        
        if st.session_state[f'{name}_equip_style'] == '4+2':
            char_config['equip_set4'] = st.session_state[f'{name}_equip_set4']
            char_config['equip_set2_a'] = st.session_state[f'{name}_equip_set2']
        else:
            char_config['equip_set2_a'] = st.session_state[f'{name}_equip_set2A']
            char_config['equip_set2_b'] = st.session_state[f'{name}_equip_set2B']
            char_config['equip_set2_c'] = st.session_state[f'{name}_equip_set2C']
        
        # 将角色配置存入session_state
        st.session_state[f'{name}_config'] = char_config

    # 提交按钮
    if not st.button('提交并保存角色配置'):
        st.stop()
        
    # 保存配置到TOML文件
    config_to_save = {"name_box": name_box}
    for name in name_box:
        config_to_save[name] = st.session_state[f"{name}_config"]
    
    with open(config_file, "w", encoding="utf-8") as f:
        toml.dump(config_to_save, f)

    # 收集所有角色配置
    all_char_configs = []
    for name in name_box:
        all_char_configs.append(st.session_state[f'{name}_config'])

        # 转换为DataFrame展示
        st.title("角色配置信息")
        for i, config in enumerate(all_char_configs):
            st.subheader(f"角色{i+1}: {config['name']}")
            df = pd.DataFrame.from_dict(config, orient='index', columns=['值'])
            # 确保所有值转换为字符串类型以避免Arrow序列化错误
            df['值'] = df['值'].astype(str)
            st.dataframe(df)

def simulator():
    st.title("ZZZ Simulator - 模拟器")
    st.write("模拟器功能开发中...")

def data_analysis():
    st.title("ZZZ Simulator - 数据分析")
    st.write("数据分析功能开发中...")


if __name__ == "__main__":
    # 初始化session_state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "character_config"
    
    # 侧边栏导航
    with st.sidebar:
        st.title("导航菜单")
        st.markdown(
        """
        <style>
            div[data-testid="stButton"] button {
                border: none !important;
                background: none !important;
                box-shadow: none !important;
            }
        </style>
        """, 
        unsafe_allow_html=True)
        for page_name, page_func_name in PAGES.items():
            if st.button(page_name):
                st.session_state.current_page = page_func_name
    
    # 根据当前页面显示内容
    if st.session_state.current_page == "character_config":
        character_config()
    elif st.session_state.current_page == "simulator":
        simulator()
    elif st.session_state.current_page == "data_analysis":
        data_analysis()
