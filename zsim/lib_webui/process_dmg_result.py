import pandas as pd
import plotly.express as px
import streamlit as st

from sim_progress.Character.skill_class import lookup_name_or_cid
from .constants import results_dir, element_mapping


def process_dmg_result(rid: int) -> None:
    # 读取伤害数据 CSV 文件
    try:
        csv_file_path = f'{results_dir}/{rid}/damage.csv'
        dmg_result_df: pd.DataFrame = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        st.error(f'未找到文件：{csv_file_path}')
        return
    with st.expander('原始数据：'):
        st.dataframe(dmg_result_df)
    draw_line_chart(dmg_result_df) # 绘制伤害与失衡的折线图
    uuid_df = sort_df_by_UUID(dmg_result_df) # 按UUID排序
    with st.expander('按UUID排序后的数据：'):
        st.dataframe(uuid_df)
    draw_char_chart(uuid_df) # 绘制角色相关信息的图标
    draw_char_timeline(dmg_result_df) # 绘制技能相关信息的图标
    
def draw_line_chart(dmg_result_df: pd.DataFrame) -> None:
    with st.expander('伤害与失衡曲线：'):
        # 时间-伤害分布
        st.subheader('时间-伤害分布')
        # 要确保纵轴标题与变量名称改变，需要设置 `labels` 参数
        fig = px.line(dmg_result_df, x='tick', y=['dmg_expect', 'dmg_crit'], 
                      labels={'tick': '时间（帧数）', 'value': '伤害值', 'variable': '数据类型', 'dmg_expect': '期望伤害', 'dmg_crit': '暴击伤害'})
        st.plotly_chart(fig)
        
        # 时间-DPS分布
        dmg_result_df['dps'] = dmg_result_df['dmg_expect'].cumsum() / dmg_result_df['tick'] * 60
        st.subheader('时间-DPS分布')
        fig = px.line(dmg_result_df, x='tick', y='dps', labels={'tick': '时间（帧数）', 'dps': 'DPS'})
        st.plotly_chart(fig)
        
        # 时间-失衡值分布
        st.subheader('时间-失衡值分布')
        if '失衡状态' in dmg_result_df.columns:
            dmg_result_df.loc[dmg_result_df['失衡状态'], 'stun'] = 0
        filtered_df = dmg_result_df
        fig = px.line(filtered_df, x='tick', y='stun', labels={'tick': '时间（帧数）', 'stun': '失衡值'})
        st.plotly_chart(fig)
        
        # 时间-失衡效率分布
        # 找到第一次失衡状态为True的索引
        first_stun_index = filtered_df[filtered_df['失衡状态'] == True].index.min()  # noqa: E712
        if pd.notna(first_stun_index):
            # 只计算第一次失衡状态为True之前的失衡效率
            filtered_df.loc[:first_stun_index, 'stun_efficiency'] = filtered_df.loc[:first_stun_index, 'stun'].cumsum() / filtered_df.loc[:first_stun_index, 'tick'] * 60
            filtered_df.loc[first_stun_index + 1:, 'stun_efficiency'] = None
        else:
            # 如果没有失衡状态为True的情况，计算全部的失衡效率
            filtered_df['stun_efficiency'] = filtered_df['stun'].cumsum() / filtered_df['tick'] * 60
        st.subheader('时间-失衡效率分布')
        fig = px.line(filtered_df, x='tick', y='stun_efficiency', labels={'tick': '时间（帧数）', 'stun_efficiency': '失衡效率（每秒）'})
        st.plotly_chart(fig)

def sort_df_by_UUID(dmg_result_df: pd.DataFrame) -> pd.DataFrame:
    # 检查必要的列是否存在
    required_columns = ['skill_tag', 'dmg_expect', 'stun', 'buildup', 'UUID']
    for col in required_columns:
        if col not in dmg_result_df.columns:
            raise ValueError(f"DataFrame 中缺少必要的列: {col}")
    
    result_data = []
    
    # 提取全部UUID
    all_UUID = dmg_result_df['UUID'].unique()
    # 按UUID遍历，将每个相同UUID的伤害期望、失衡值、积蓄值相加，并保留skill_tag
    for UUID in all_UUID:
        # 找到所有UUID相同的行（不再使用dropna()）
        same_UUID_rows = dmg_result_df[dmg_result_df['UUID'] == UUID]
        # 计算期望伤害、失衡值、积蓄值的总和（使用fillna(0)确保计算）
        dmg_expect_sum = same_UUID_rows['dmg_expect'].fillna(0).sum()
        stun_sum = same_UUID_rows['stun'].fillna(0).sum()
        buildup_sum = same_UUID_rows['buildup'].fillna(0).sum()
        # 获取第一个非空的skill_tag
        skill_tags = same_UUID_rows['skill_tag'].dropna()
        skill_tag = skill_tags.iloc[0] if len(skill_tags) > 0 else None
        element_type = same_UUID_rows['element_type'].iloc[0] if len(same_UUID_rows['element_type']) > 0 else None
        cid = skill_tag[0:4] if skill_tag is not None else None
        name, _ = lookup_name_or_cid(cid = cid) if cid is not None else (None, None)
        
        result_data.append({
            'UUID': UUID,
            'name': name,
            'element_type': element_type,
            'cid': cid,
            'skill_tag': skill_tag,
            'dmg_expect_sum': dmg_expect_sum,
            'stun_sum': stun_sum,
            'buildup_sum': buildup_sum
        })
    
    # 将列表转换为DataFrame并返回
    return pd.DataFrame(result_data)

def draw_char_chart(uuid_df: pd.DataFrame) -> None:
    with st.expander('角色参与度分布情况：'):
        cols = st.columns(2)
        # 角色伤害占比分布
        with cols[0]:
            st.subheader('角色伤害占比')
            char_dmg_df = uuid_df.groupby('name')['dmg_expect_sum'].sum().reset_index()
            fig = px.pie(char_dmg_df, names='name', values='dmg_expect_sum', labels={'name': '角色', 'dmg_expect_sum': '期望伤害总和'})
            st.plotly_chart(fig)
        # 角色失衡占比分布
        with cols[1]:
            st.subheader('角色失衡占比')
            char_stun_df = uuid_df.groupby('name')['stun_sum'].sum().reset_index()
            fig = px.pie(char_stun_df, names='name', values='stun_sum', labels={'name': '角色', 'stun_sum': '失衡值总和'})
            st.plotly_chart(fig)
        
        # 每个角色的各技能输出占比分布-条形图
        char_skill_dmg_df = uuid_df.groupby(['name', 'skill_tag'])['dmg_expect_sum'].sum().reset_index()
        # 创建一个新的Streamlit列布局
        cols = st.columns(len(char_skill_dmg_df['name'].unique()))
        col_index = 0
        for name, group in char_skill_dmg_df.groupby('name'):
            with cols[col_index]:
                st.subheader(f'{name}各技能输出占比')
                fig = px.pie(group, names='skill_tag', values='dmg_expect_sum', labels={'skill_tag': '技能标签', 'dmg_expect_sum': '期望伤害总和'})
                st.plotly_chart(fig)
            col_index += 1

        # 每个角色各属性的积蓄占比
        char_element_df = uuid_df.groupby(['name','element_type'])['buildup_sum'].sum().reset_index()
        # 创建一个新的Streamlit列布局
        cols = st.columns(len(char_element_df['element_type'].unique()))
        col_index = 0
        for element in char_element_df['element_type'].unique():
            element_df = char_element_df[char_element_df['element_type'] == element]
            with cols[col_index]:
                st.subheader(f'{element_mapping[element]}积蓄来源占比')
                fig = px.pie(element_df, names='name', values='buildup_sum', labels={'name': '角色', 'buildup_sum': '积蓄值总和'})
                st.plotly_chart(fig)
            col_index += 1

def draw_char_timeline(dmg_result_df: pd.DataFrame) -> None:
    # 验证输入数据是否包含所需列
    required_columns = ['冻结', '霜寒', '畏缩', '感电', '灼烧', '侵蚀', '烈霜霜寒', 'tick']
    missing_cols = [col for col in required_columns if col not in dmg_result_df.columns]
    if missing_cols:
        st.error(f'输入数据缺少必要的列: {missing_cols}')
        return

    def find_consecutive_true_ranges(df, column):
        ranges = []
        start = None
        for i, row in df.iterrows():
            if row[column]:
                if start is None:
                    start = row['tick']
            else:
                if start is not None:
                    prev_tick = df['tick'].iloc[i - 1]
                    ranges.append((start, prev_tick))
                    start = None
        if start is not None:
            ranges.append((start, df['tick'].iloc[-1]))
        return ranges
    
    with st.expander('异常时间线：'):
        columns = ['冻结', '霜寒', '畏缩', '感电', '灼烧', '侵蚀', '烈霜霜寒']
        gantt_data = []
        for col in columns:
            ranges = find_consecutive_true_ranges(dmg_result_df, col)
            for start, end in ranges:
                gantt_data.append({
                    'Task': col,
                    'Start': start,
                    'Finish': end
                })
        gantt_df = pd.DataFrame(gantt_data)
            
        if not gantt_df.empty:
            # 计算每个任务的持续时间
            gantt_df['Duration'] = gantt_df['Finish'] - gantt_df['Start']
            fig = px.bar(gantt_df, x='Duration', y='Task', 
                        base='Start', orientation='h',
                        labels={'Start': '开始时间(帧)', 'Duration': '持续时间(帧)', 'Task': '状态类型'})
            st.plotly_chart(fig)
        else:
            st.warning('没有找到任何连续的状态数据')
    # with st.expander('时间线数据：'):
    #     st.dataframe(gantt_df)        
           