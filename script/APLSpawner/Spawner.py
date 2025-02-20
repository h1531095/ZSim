import streamlit as st
import pandas as pd
import sys

sys.path.append("F:/GithubProject/ZZZ_Calculator")
from define import CHARACTER_DATA_PATH


@st.cache_data
def load_char_data():
    """
    加载角色数据并缓存。
    """
    char_data = pd.read_csv(CHARACTER_DATA_PATH)
    char_name_list = char_data['name'].tolist()
    return char_name_list


def initialize_state():
    # 初始化应用程序

    if 'char_name_list' not in st.session_state:
        st.session_state.char_name_list = load_char_data()
    if 'selected_char_name_dict' not in st.session_state:
        st.session_state.selected_char_name_dict = {}
    if 'available_char_name_list' not in st.session_state:
        st.session_state.available_char_name_list = st.session_state.char_name_list
    if 'char_1' not in st.session_state:
        st.session_state.char_1 = None
    if 'char_2' not in st.session_state:
        st.session_state.char_2 = None
    if 'char_3' not in st.session_state:
        st.session_state.char_3 = None


def update_selected_char_name_dict(key: int):
    char_key = f'char_{key}'
    st.session_state.selected_char_name_dict[char_key] = st.session_state[char_key]

    selected_char_list = list(st.session_state.selected_char_name_dict.values())
    result = list(item for item in st.session_state.char_name_list if item not in selected_char_list)
    st.session_state.available_char_name_list = result

st.title('初始化：请选择参与模拟的角色！')
initialize_state()

char_1 = st.selectbox('角色1', st.session_state.available_char_name_list, index=0, key='char_1', on_change=lambda: update_selected_char_name_dict(1))
char_2 = st.selectbox('角色2', st.session_state.available_char_name_list, index=0, key='char_2', on_change=lambda: update_selected_char_name_dict(2))
char_3 = st.selectbox('角色3', st.session_state.available_char_name_list, index=0, key='char_3', on_change=lambda: update_selected_char_name_dict(3))

#print(st.session_state.available_char_name_list)
# print('================分割线===================')
# print(f'更新函数调用！发生改变的角色为{char_key}，更新为了{st.session_state.char_1}')
# print(f'所有角色列表：{st.session_state.char_name_list}')
# print(f'已经选取角色：{selected_char_list}, 当前角色字典：{st.session_state.selected_char_name_dict}')
# print(f'可选取角色为：{st.session_state.available_char_name_list}')