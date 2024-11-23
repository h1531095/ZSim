import os

import pandas as pd
import streamlit as st

import Preload
import Report
# from main import init_data, char_data, schedule_data, load_data, global_stats, main_loop
import main
from Report import write_to_csv
from define import CHARACTER_DATA_PATH

init_data = main.init_data
char_data = main.char_data
schedule_data = main.schedule_data
load_data = main.load_data
main_loop = main.main_loop


# Streamlit UI
st.title("角色配置与运行")

# 下拉框选择角色
col1, col2, col3 = st.columns(3)
all_name_df = pd.read_csv(CHARACTER_DATA_PATH)
name_list = all_name_df['name'].tolist()
with col1:
    selected_char_0 = st.selectbox('选择角色1', name_list, index=name_list.index(main.InitData.name_box[0]))
with col2:
    selected_char_1 = st.selectbox('选择角色2', name_list, index=name_list.index(main.InitData.name_box[1]))
with col3:
    selected_char_2 = st.selectbox('选择角色3', name_list, index=name_list.index(main.InitData.name_box[2]))

# 输入框
char_0_inputs = {}
char_1_inputs = {}
char_2_inputs = {}

char_attr_to_zh_cn = {
    'name': '角色名',
    'weapon': '武器',
    'weapon_level': '武器精炼',
    'equip_set4': '四件套',
    'equip_set2_a': '二件套A',
    'drive4': '四号位',
    'drive5': '五号位',
    'drive6': '六号位',
    'scCRIT': '副词条暴击率',
    "scATK_percent" : '副词条攻击力%',
    "scATK": '副词条攻击力',
    "scHP_percent": '副词条生命值%',
    "scHP":'副词条生命值',
    "scDEF_percent" : '副词条防御力%',
    "scDEF" : '副词条防御力',
    "scAnomalyProficiency" : '副词条异常精通',
    "scPEN": '副词条穿透值',
}

for key, trans in char_attr_to_zh_cn.items():
    if key != 'name':
        with col1:
            char_0_inputs[key] = st.text_input(f'{trans}（角色1）', value=str(main.InitData.char_0.get(key, 0)))
        with col2:
            char_1_inputs[key] = st.text_input(f'{trans}（角色2）', value=str(main.InitData.char_1.get(key, 0)))
        with col3:
            char_2_inputs[key] = st.text_input(f'{trans}（角色3）', value=str(main.InitData.char_2.get(key, 0)))

# 初始化 session_state 变量
if 'submit_role_info' not in st.session_state:
    st.session_state.submit_role_info = False

if 'submit' not in st.session_state:
    st.session_state.submit = False

# 提交按钮
if st.button('提交角色信息'):
    st.session_state.submit_role_info = True
    st.session_state.submit = False  # 重置第二个按钮的状态

if st.session_state.submit_role_info:
    # 更新角色数据
    init_data.name_box = [selected_char_0, selected_char_1, selected_char_2]
    init_data.char_0.update(char_0_inputs)
    init_data.char_1.update(char_1_inputs)
    init_data.char_2.update(char_2_inputs)

    st.title("输入计算序列")
    # 读取 INPUT_ACTION_LIST
    INPUT_ACTION_LIST = pd.read_csv('./data/计算序列.csv')
    # 展示 CSV 文件，并允许用户修改
    edited_data = st.data_editor(INPUT_ACTION_LIST, num_rows="dynamic")

    # 提交按钮
    if st.button('提交'):
        st.session_state.submit = True
        st.session_state.submit_role_info = False

    if st.session_state.submit:

        with st.spinner('正在计算技能序列···'):
            # 将修改后的数据保存回 CSV 文件
            edited_data.to_csv('./data/计算序列.csv', index=False)
            # 运行主程序
            tick = 0
            main_loop()
            write_to_csv()
            print('\n')
        with st.spinner('等待IO完成···'):
            Report.log_queue.join()
            Report.result_queue.join()

        # 读取results中编号最大的csv文件
        results_dir = 'results'
        csv_files = [f for f in os.listdir(results_dir) if f.endswith('.csv')]

        if not csv_files:
            st.warning("结果目录中没有 CSV 文件。")
        else:
            # 提取文件名中的编号
            file_numbers = []
            for file in csv_files:
                try:
                    number = int(file.split('.')[0])  # 假设文件名格式为编号.csv
                    file_numbers.append((number, file))
                except ValueError:
                    continue

            if not file_numbers:
                st.warning("结果目录中没有符合格式的 CSV 文件。")
            else:
                # 找到编号最大的文件
                max_number, max_file = max(file_numbers, key=lambda x: x[0])

                # 读取编号最大的 CSV 文件
                file_path = os.path.join(results_dir, max_file)
                df = pd.read_csv(file_path)

                # 显示读取的 CSV 文件内容
                st.write(f"计算结果位于服务器的: {results_dir}/{max_file}，或者你可以下载到客户端")
                st.dataframe(df)

                # 计算瞬时dps
                df['cumulative_dmg_expect'] = df['dmg_expect'].cumsum()/df['tick']

                # 使用 st.line_chart 绘制折线图
                st.line_chart(df.set_index('tick')['cumulative_dmg_expect'], x_label='tick', y_label='cumulative_dmg_expect')

        st.success("程序执行完成！")
