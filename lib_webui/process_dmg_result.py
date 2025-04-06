import pandas as pd
import streamlit as st
from .constants import results_dir
import plotly.express as px

def process_dmg_result(rid: int) -> None:
    # 读取 CSV 文件
    csv_file_path = f'{results_dir}/{rid}/damage.csv'
    dmg_result_df: pd.DataFrame = pd.read_csv(csv_file_path)
    with st.expander('原始数据：'):
        st.dataframe(dmg_result_df)
    draw_line_chart(dmg_result_df) # 绘制伤害与失衡的折线图
    
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
        first_stun_index = filtered_df[filtered_df['失衡状态'] == True].index.min()
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