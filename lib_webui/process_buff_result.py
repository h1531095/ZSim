import pandas as pd
import plotly.express as px
import streamlit as st
import os

from .constants import results_dir

def process_buff_result(rid: int) -> None:
    # 读取伤害数据 CSV 文件
    try:
        buff_log_path = f'{results_dir}/{rid}/buff_log/'
        buff_logs: dict[str, pd.DataFrame] = {}
        
        # 仅处理CSV文件
        for filename in [f for f in os.listdir(buff_log_path) if f.endswith('.csv')]:
            csv_file_path = os.path.join(buff_log_path, filename)
            df = pd.read_csv(csv_file_path)
            buff_logs[filename.replace('.csv', '')] = df
            
    except FileNotFoundError:
        st.error(f'未找到文件：{buff_log_path}')
        return
    
    st.markdown("处理buff时间线将花费较长时间，请耐心等待")
    
    # 处理绘图逻辑
    for filename, df in buff_logs.items():
        with st.expander(f"{filename} 的BUFF时间线"):
            # 准备数据 - 按buff名称和层数分组，记录开始和结束时间
            buff_data = []
            for buff in df.columns[1:]:  # 跳过time_tick列
                # 找出所有非空行
                active_rows = df[df[buff].notna()]
                if not active_rows.empty:
                    # 逐个遍历数据点
                    prev_level = None
                    start_tick = None
                    for _, row in active_rows.iterrows():
                        current_level = row[buff]
                        if prev_level is None:
                            # 第一个数据点
                            if pd.isna(current_level):
                                continue
                            prev_level = current_level
                            start_tick = row['time_tick']
                        elif current_level != prev_level:
                            # 遇到不同的层数，记录前一段
                            buff_data.append({
                                'Buff': buff,
                                'Start': start_tick,
                                'End': row['time_tick'] - 1,
                                '层数': prev_level,
                                'Duration': row['time_tick'] - start_tick
                            })
                            # 开始新的一段
                            prev_level = current_level
                            start_tick = row['time_tick']
                    
                    # 记录最后一段
                    if prev_level is not None:
                        buff_data.append({
                            'Buff': buff,
                            'Start': start_tick,
                            'End': active_rows.iloc[-1]['time_tick'],
                            '层数': prev_level,
                            'Duration': active_rows.iloc[-1]['time_tick'] - start_tick
                        })
            
            if buff_data:
                buff_df = pd.DataFrame(buff_data)
                
                # 创建合并后的时间线图表
                fig = px.bar(
                    buff_df,
                    x='Duration',
                    y='Buff',
                    color='层数',
                    base='Start',
                    orientation='h',
                    height=400 + len(df.columns[1:])*30,
                    title=f'{filename}的BUFF覆盖情况',
                    labels={'Start': '开始时刻', 'Duration': '结束时刻', 'Buff': ''}
                )
                
                # 优化图表样式
                fig.update_layout(
                    showlegend=True,
                    margin=dict(l=50, r=50, t=40, b=20),
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("没有找到有效的BUFF数据")
    