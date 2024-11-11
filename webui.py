import os
from dataclasses import dataclass, field

import pandas as pd
import streamlit as st

import Buff
import Load
import Preload
import Report
import ScheduledEvent as ScE
from CharSet_new import Character
from Enemy import Enemy
from Report import write_to_csv
from Update_Buff import update_dynamic_bufflist
from define import CHARACTER_DATA_PATH


# 定义数据类
@dataclass
class InitData:
    name_box = ['艾莲', '苍角', '莱卡恩']
    Judge_list_set = [['艾莲', '深海访客', '极地重金属'],
                      ['苍角', '含羞恶面', '自由蓝调'],
                      ['莱卡恩', '拘缚者', '镇星迪斯科']]
    char_0 = {'name' : name_box[0],
              'weapon': '深海访客', 'weapon_level': 1,
              'equip_set4': '极地重金属', 'equip_set2_a': '啄木鸟电音',
              'drive4' : '暴击率', 'drive5' : '攻击力%', 'drive6' : '攻击力%',
              'scATK_percent': 10, 'scCRIT': 20}
    char_1 = {'name' : name_box[1],
              'weapon': '含羞恶面', 'weapon_level': 5,
              'equip_set4': '摇摆爵士', 'equip_set2_a': '自由蓝调',
              'drive4' : '暴击率', 'drive5' : '攻击力%', 'drive6' : '能量自动回复%',
              'scATK_percent': 10, 'scCRIT': 20}
    char_2 = {'name' : name_box[2],
              'weapon': '拘缚者', 'weapon_level': 1,
              'equip_set4': '震星迪斯科', 'equip_set2_a': '摇摆爵士',
              'drive4' : '暴击率', 'drive5' : '攻击力%', 'drive6' : '冲击力%',
              'scATK_percent': 10, 'scCRIT': 20}
    weapon_dict = {name_box[0]: [char_0['weapon'], char_0['weapon_level']],
                   name_box[1]: [char_1['weapon'], char_1['weapon_level']],
                   name_box[2]: [char_2['weapon'], char_2['weapon_level']]}

@dataclass
class CharacterData:
    char_obj_list: list[Character] = field(init=False)
    InitData: InitData

    def __post_init__(self):
        self.char_obj_list = []
        if self.InitData.name_box:
            i = 0
            for _ in self.InitData.name_box:
                char_dict = getattr(InitData, f'char_{i}')
                char_obj = Character(**char_dict)
                self.char_obj_list.append(char_obj)
                i += 1

@dataclass
class LoadData:
    name_box: list
    Judge_list_set: list
    weapon_dict: dict
    exist_buff_dict: dict = field(init=False)
    load_mission_dict = {}
    LOADING_BUFF_DICT = {}
    name_dict = {}

    def __post_init__(self):
        self.exist_buff_dict = Buff.buff_exist_judge(self.name_box, self.Judge_list_set, self.weapon_dict)

@dataclass
class ScheduleData:
    event_list = []
    loading_buff = {}
    dynamic_buff = {}
    enemy: Enemy
    char_obj_list: list[Character]

@dataclass
class GlobalStats:
    DYNAMIC_BUFF_DICT = {}
    name_box: list
    def __post_init__(self):
        for name in self.name_box + ['enemy']:
            self.DYNAMIC_BUFF_DICT[name] = []

def main_loop(stop_tick: int | None = None):
    tick = 0
    while True:
        # Tick Update
        update_dynamic_bufflist(global_stats.DYNAMIC_BUFF_DICT, tick, load_data.exist_buff_dict, schedule_data.enemy)

        # Preload
        preload.do_preload(tick, schedule_data.enemy)
        preload_list = preload.preload_data.preloaded_action

        if stop_tick is None:
            if len(preload.preload_data.skills_queue) == 0:
                stop_tick = tick + 120
        elif tick >= stop_tick:
            break

        # Load
        if preload_list:
            Load.SkillEventSplit(preload_list, load_data.load_mission_dict, load_data.name_dict, tick)
        Buff.BuffLoadLoop(tick, load_data.load_mission_dict, load_data.exist_buff_dict, load_data.name_box, load_data.LOADING_BUFF_DICT)
        Buff.buff_add(tick, load_data.LOADING_BUFF_DICT, global_stats.DYNAMIC_BUFF_DICT, schedule_data.enemy)
        Load.DamageEventJudge(tick, load_data.load_mission_dict, schedule_data.enemy, schedule_data.event_list)

        # ScheduledEvent
        scheduled = ScE.ScheduledEvent(global_stats.DYNAMIC_BUFF_DICT, schedule_data, tick)
        scheduled.event_start()

        tick += 1
        print(f"\r{tick}", end='')

# Streamlit UI
st.title("角色配置与运行")

# 下拉框选择角色
col1, col2, col3 = st.columns(3)
all_name_df = pd.read_csv(CHARACTER_DATA_PATH)
name_list = all_name_df['name'].tolist()
with col1:
    selected_char_0 = st.selectbox('选择角色1', name_list, index=name_list.index('艾莲'))
with col2:
    selected_char_1 = st.selectbox('选择角色2', name_list, index=name_list.index('苍角'))
with col3:
    selected_char_2 = st.selectbox('选择角色3', name_list, index=name_list.index('莱卡恩'))

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
            char_0_inputs[key] = st.text_input(f'{trans}（角色1）', value=str(InitData.char_0.get(key, 0)))
        with col2:
            char_1_inputs[key] = st.text_input(f'{trans}（角色2）', value=str(InitData.char_1.get(key, 0)))
        with col3:
            char_2_inputs[key] = st.text_input(f'{trans}（角色3）', value=str(InitData.char_2.get(key, 0)))

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
    init_data = InitData()
    init_data.name_box = [selected_char_0, selected_char_1, selected_char_2]
    init_data.char_0.update(char_0_inputs)
    init_data.char_1.update(char_1_inputs)
    init_data.char_2.update(char_2_inputs)

    # 初始化其他数据
    char_data = CharacterData(init_data)
    load_data = LoadData(
        name_box=init_data.name_box,
        Judge_list_set=init_data.Judge_list_set,
        weapon_dict=init_data.weapon_dict
    )
    schedule_data = ScheduleData(enemy=Enemy(), char_obj_list=char_data.char_obj_list)
    global_stats = GlobalStats(name_box=init_data.name_box)

    # 初始化预加载数据
    skills = (char.skill_object for char in char_data.char_obj_list)

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
        # 将修改后的数据保存回 CSV 文件
        edited_data.to_csv('./data/计算序列.csv', index=False)

        preload = Preload.Preload(*skills)

        # 运行主程序
        main_loop()
        write_to_csv()

        Report.log_queue.join()
        Report.result_queue.join()

        # 读取results中编号最大的csv文件
        results_dir = './results'
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
                st.write(f"计算结果位于: {max_file}")
                st.dataframe(df)

                # 计算 dmg_expect 列的累加值
                df['cumulative_dmg_expect'] = df['dmg_expect'].cumsum()

                # 使用 st.line_chart 绘制折线图
                st.line_chart(df.set_index('tick')['cumulative_dmg_expect'])

        st.success("程序执行完成！")
