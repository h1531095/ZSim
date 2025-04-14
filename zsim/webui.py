import gc
import timeit

import streamlit as st
import toml

from sim_progress import Report
from sim_progress.Report import write_to_csv
from simulator.main_loop import main_loop

# 页面导航
PAGES = {
    "角色配置": "character_config",
    "模拟器": "simulator",
    "数据分析": "data_analysis",
    "APL编辑器": "apl_editor",
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
                st.selectbox('音擎', weapon_options,
                             index=weapon_options.index(saved_char_config[name]['weapon']) if name in saved_char_config else 0, 
                             key=f'{name}_weapon')
            with col_level:
                st.number_input('音擎精炼等级', min_value=1, max_value=5, 
                              value=saved_char_config[name]['weapon_level'] if name in saved_char_config else 1, 
                              key=f'{name}_weapon_level')
            with col_cinema:
                st.number_input('影画等级', min_value=0, max_value=6, 
                              value=saved_char_config[name]['cinema'] if name in saved_char_config else 0, 
                              key=f'{name}_cinema_level')
            
            equip_style = st.radio('驱动盘搭配方式', ['4+2', '2+2+2'], 
                                 index=0 if name not in saved_char_config or 'equip_style' not in saved_char_config[name] else (0 if saved_char_config[name]['equip_style'] == '4+2' else 1),
                                 key=f'{name}_equip_style')
            col1, col2 = st.columns(2)
            with col1:
                if equip_style == '4+2':
                    st.selectbox('四件套', equip_set4_options, 
                                     index=equip_set4_options.index(saved_char_config[name]['equip_set4']) if name in saved_char_config and 'equip_set4' in saved_char_config[name] else 0, 
                                     key=f'{name}_equip_set4')
                    st.selectbox('二件套', equip_set2_options, 
                                     index=equip_set2_options.index(saved_char_config[name]['equip_set2_a']) if name in saved_char_config else 0, 
                                     key=f'{name}_equip_set2')
                else:
                    st.selectbox('二件套A', equip_set2_options, 
                                     index=equip_set2_options.index(saved_char_config[name]['equip_set2_a']) if name in saved_char_config else 0, 
                                     key=f'{name}_equip_set2A')
                    st.selectbox('二件套B', equip_set2_options, 
                                     index=equip_set2_options.index(saved_char_config[name]['equip_set2_b']) if name in saved_char_config and 'equip_set2_b' in saved_char_config[name] else 0, 
                                     key=f'{name}_equip_set2B')
                    st.selectbox('二件套C', equip_set2_options, 
                                     index=equip_set2_options.index(saved_char_config[name]['equip_set2_c']) if name in saved_char_config and 'equip_set2_c' in saved_char_config[name] else 0, 
                                     key=f'{name}_equip_set2C')
            with col2:
            # 主词条选择
                from lib_webui.constants import main_stat4_options, main_stat5_options, main_stat6_options
                st.selectbox('四号位主词条', main_stat4_options, 
                                     index=main_stat4_options.index(saved_char_config[name]['drive4']) if name in saved_char_config else 0, 
                                     key=f'{name}_main_stat4')
                st.selectbox('五号位主词条', main_stat5_options, 
                                     index=main_stat5_options.index(saved_char_config[name]['drive5']) if name in saved_char_config else 0, 
                                     key=f'{name}_main_stat5')
                st.selectbox('六号位主词条', main_stat6_options, 
                                     index=main_stat6_options.index(saved_char_config[name]['drive6']) if name in saved_char_config else 0, 
                                     key=f'{name}_main_stat6')
            
            # 副词条数量输入
            from lib_webui.constants import sc_max_value
            st.text('副词条数量：')
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.number_input('攻击力%', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scATK_percent'] if name in saved_char_config else 0, key=f'{name}_scATK_percent')
                st.number_input('攻击力', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scATK'] if name in saved_char_config else 0, key=f'{name}_scATK')
            with col2:
                st.number_input('生命值%', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scHP_percent'] if name in saved_char_config else 0, key=f'{name}_scHP_percent')
                st.number_input('生命值', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scHP'] if name in saved_char_config else 0, key=f'{name}_scHP')
            with col3:
                st.number_input('防御力%', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scDEF_percent'] if name in saved_char_config else 0, key=f'{name}_scDEF_percent')
                st.number_input('防御力', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scDEF'] if name in saved_char_config else 0, key=f'{name}_scDEF')
            with col4:
                st.number_input('暴击率', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scCRIT'] if name in saved_char_config else 0, key=f'{name}_scCRIT')
                st.number_input('暴击伤害', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scCRIT_DMG'] if name in saved_char_config else 0, key=f'{name}_scCRIT_DMG')
            with col5:
                st.number_input('异常精通', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scAnomalyProficiency'] if name in saved_char_config else 0, key=f'{name}_scAnomalyProficiency')
                st.number_input('穿透值', min_value=0, max_value=sc_max_value, value=saved_char_config[name]['scPEN'] if name in saved_char_config else 0, key=f'{name}_scPEN')
            
            # 暴击配平算法开关
            st.checkbox('使用暴击配平算法', value=saved_char_config[name]['crit_balancing'] if name in saved_char_config else False, key=f'{name}_crit_balancing')
            
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
    _config_to_save = {"name_box": name_box}
    for name in name_box:
        _config_to_save[name] = st.session_state[f"{name}_config"]
    # 更新 saved_char_config, 并将其写入文件
    saved_char_config.update(_config_to_save)
    from define import char_config_file
    with open(char_config_file, "w", encoding="utf-8") as f:
        toml.dump(saved_char_config, f)

    # 调用封装的函数
    from lib_webui.process_char_config import display_character_panels
    display_character_panels(name_box)

def simulator():
    st.title("ZZZ Simulator - 模拟器")
    import json
    from define import CONFIG_PATH
    with open(CONFIG_PATH, "r", encoding='utf-8') as f:
        config = json.load(f)
        default_stop_tick = config["stop_tick"]
    
    # 添加stop_tick输入框
    stop_tick = st.number_input("模拟时长（帧数，1秒=60帧）", min_value=1, max_value=65535, value=default_stop_tick, key="stop_tick")
    
    # 添加开始模拟按钮
    if not st.button("开始模拟"):
        st.stop()

    st.write(f"开始模拟，时长: {stop_tick} ticks")
    
    # 显示加载中的圈圈
    with st.spinner('正在模拟中，请稍候...'):
        # 执行模拟
        elapsed_time = timeit.timeit(lambda: main_loop(stop_tick), number=1)
    
    with st.spinner('正在等待IO结束...'):
        write_to_csv()
        Report.log_queue.join()
        Report.result_queue.join()
        gc.collect()
    
    st.success(f"模拟完成！耗时: {elapsed_time:.2f}秒，请前往数据分析查看结果。")
    st.error("注意，目前程序无法保证第二次模拟的准确性，请刷新网页再尝试")
    
    # 保存stop_tick到config.json
    with open(CONFIG_PATH, "r+", encoding='utf-8') as f:
        config = json.load(f)
        config["stop_tick"] = stop_tick
        f.seek(0)
        json.dump(config, f, indent=4)
        f.truncate()

def data_analysis():
    st.title("ZZZ Simulator - 数据分析")
    from lib_webui.clean_results_cache import get_all_results, rename_result
    from lib_webui.constants import IDDuplicateError
    # 添加一个选择框来选择要查看的ID，以及一个按钮来刷新ID列表
    col1, col2, col3 = st.columns(3)
    with col1:
        id_cache: dict = get_all_results()
        options = list(id_cache.keys())[::-1]  # 使用切片反转列表
        selected_key = st.selectbox("选择你要查看的结果", options)  # 反转后默认选第一个
    with col2:
        st.markdown('备注信息')
        st.markdown(f'<span style="color:gray;">{id_cache[selected_key] if id_cache else None}</span>', unsafe_allow_html=True)
    with col3:
        # 提供一个按钮，弹出一个窗口来重命名当前选中的ID与备注信息
        with st.expander("重命名选中的结果"):
            new_name = st.text_input("请输入新的ID", value=selected_key)
            new_comment = st.text_input("请输入新的备注信息", value=id_cache[selected_key] if id_cache else None)
            if st.button("保存"):
                try:
                    rename_result(selected_key, new_name, new_comment)
                    st.success("重命名成功！")
                    st.rerun()  # 刷新页面以更新显示
                except FileNotFoundError:
                    st.warning("请检查文件是否存在或ID是否正确。", icon="⚠️")
                except IDDuplicateError as e:
                    st.warning(e, icon="⚠️")
        
    # 添加一个按钮来开始分析
    if not st.button("开始分析"):
        st.stop()
    # 处理伤害结果
    from lib_webui.process_dmg_result import process_dmg_result
    process_dmg_result(selected_key)
    # 处理Buff结果
    from lib_webui.process_buff_result import process_buff_result
    process_buff_result(selected_key)


def apl_editor():
    st.title("ZZZ Simulator - APL编辑器")
    st.write("这是APL编辑器页面，您可以在这里编辑APL相关设置。")

if __name__ == "__main__":
    # 设置页面布局为宽屏
    st.set_page_config(layout="wide")
    
    # 初始化session_state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "character_config"
    
    # 侧边栏导航
    with st.sidebar:
        st.title("导航菜单")
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
    elif st.session_state.current_page == "apl_editor":
        apl_editor()
