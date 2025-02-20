import streamlit as st
import pandas as pd
import sys
import platform

os_name = platform.system()
if os_name == "Windows":
    sys.path.append("F:/GithubProject/ZZZ_Calculator")
elif os_name == "Darwin":
    sys.path.append("/Users/steinway/Code/ZZZ_Calculator")
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
    if 'available_char_name_dict' not in st.session_state:
        st.session_state.available_char_name_dict = {'char_1': st.session_state.char_name_list,
                                                     'char_2': st.session_state.char_name_list,
                                                     'char_3': st.session_state.char_name_list}
    if 'char_1' not in st.session_state:
        st.session_state.char_1 = None
    if 'char_2' not in st.session_state:
        st.session_state.char_2 = None
    if 'char_3' not in st.session_state:
        st.session_state.char_3 = None


def update_selected_char_name_dict(key: int):
    """更新选中的角色并刷新其他下拉框"""
    # 获取当前选择的值
    current_value = st.session_state[f"char_{key}"]
    _saved_char_dict = {}
    # 保存A、C的当前选择
    for i in range(1, 4):
        _saved_char_dict.update({f"char_{i}": getattr(st.session_state, f"char_{i}", None)})
    print(_saved_char_dict)

    # 更新选中字典
    st.session_state.selected_char_name_dict[f"char_{key}"] = current_value

    # 计算可用角色列表
    selected_chars = [
        v for k, v in st.session_state.selected_char_name_dict.items()
        if v is not None
    ]
    available_chars = [
        char for char in st.session_state.char_name_list
        if char not in selected_chars
    ]

    for i in range(1, 4):
        _char_key = f"char_{i}"
        if i == key:
            continue
        else:
            st.session_state.available_char_name_dict[_char_key] = available_chars
            setattr(st.session_state, f"char_{i}", _saved_char_dict[_char_key])


st.title('初始化：请选择参与模拟的角色！')
initialize_state()

cols = st.columns(3)
with cols[0]:
    st.selectbox(
        '角色1',
        st.session_state.available_char_name_dict['char_1'],
        key='char_1',
        on_change=lambda: update_selected_char_name_dict(1),
    )
with cols[1]:
    st.selectbox(
        '角色2',
        st.session_state.available_char_name_dict['char_2'],
        key='char_2',
        on_change=lambda: update_selected_char_name_dict(2)
    )
with cols[2]:
    st.selectbox(
        '角色3',
        st.session_state.available_char_name_dict['char_3'],
        key='char_3',
        on_change=lambda: update_selected_char_name_dict(3)
    )

# print(st.session_state.available_char_name_list)
# print('================分割线===================')
# print(f'更新函数调用！发生改变的角色为{char_key}，更新为了{st.session_state.char_1}')
# print(f'所有角色列表：{st.session_state.char_name_list}')
# print(f'已经选取角色：{selected_char_list}, 当前角色字典：{st.session_state.selected_char_name_dict}')
# print(f'可选取角色为：{st.session_state.available_char_name_list}')
