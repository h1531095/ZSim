import json
import os
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from define import results_dir


def _prepare_buff_timeline_data(df: pd.DataFrame) -> list[dict[str, Any]]:
    """将包含时间序列BUFF数据的DataFrame转换为适用于Plotly时间线的格式。

    Args:
        df (pd.DataFrame): 输入的DataFrame，第一列应为 'time_tick'，
                           其余列为各个BUFF的状态，列名为BUFF名称。
                           单元格中的值代表该BUFF在对应time_tick的状态值，
                           空值（NaN或None）表示BUFF在该tick不生效。

    Returns:
        list[dict[str, Any]]: 转换后的数据列表，每个字典代表一个BUFF生效的时间段，
                              包含 'Task' (BUFF名称), 'Start' (开始tick),
                              'Finish' (结束tick), 'Value' (BUFF值)。
    """
    timeline_data: list[dict[str, Any]] = []
    buff_columns = [col for col in df.columns if col != "time_tick"]

    for buff_name in buff_columns:
        start_tick: int | None = None
        current_value: Any = None

        # 遍历每个时间点
        for index, row in df.iterrows():
            tick = row["time_tick"]
            value = row[buff_name]

            # 检查值是否为 NaN 或 None
            is_nan_or_none = pd.isna(value)

            if start_tick is None:  # 当前没有记录BUFF段
                if not is_nan_or_none:  # 遇到新的有效值，开始记录
                    start_tick = tick
                    current_value = value
            else:  # 当前正在记录BUFF段
                # 值发生变化 或 遇到 NaN/None，结束上一段
                if is_nan_or_none or value != current_value:
                    timeline_data.append(
                        dict(
                            Task=buff_name,
                            Start=int(start_tick),
                            Finish=int(tick - 1),
                            Value=current_value,
                        )
                    )
                    # 如果当前值有效，则开始新的记录段
                    if not is_nan_or_none:
                        start_tick = tick
                        current_value = value
                    else:  # 遇到 NaN/None，重置状态
                        start_tick = None
                        current_value = None

        # 处理文件末尾仍在生效的BUFF段
        if start_tick is not None:
            timeline_data.append(
                dict(
                    Task=buff_name,
                    Start=int(start_tick),  # 转换为 int
                    Finish=int(
                        df["time_tick"].iloc[-1]
                    ),  # 结束于最后一个tick, 转换为 int
                    Value=current_value,
                )
            )

    return timeline_data


def _draw_buff_timeline_charts(all_buff_data: dict[str, list[dict[str, Any]]]) -> None:
    """根据处理后的BUFF数据绘制多个时间线图表。"""
    if not all_buff_data:
        st.warning("没有可用于绘制图表的BUFF数据。")
        return
    st.subheader("BUFF时间线: ")
    for file_key, buff_data in all_buff_data.items():
        if not buff_data:
            continue

        with st.expander(f"{file_key}"):
            df_timeline = pd.DataFrame(buff_data)

            # 确保时间列是数值类型
            df_timeline["Start"] = pd.to_numeric(df_timeline["Start"])
            df_timeline["Finish"] = pd.to_numeric(df_timeline["Finish"])

            # 准备悬停文本 - 仅使用 Value
            df_timeline["hover_text"] = df_timeline.apply(
                lambda row: f"层数: {row['Value']}",
                axis=1,
            )
            fig = go.Figure(
                data=[
                    go.Bar(
                        name=row["Task"],
                        x=[(row["Finish"] - row["Start"])],
                        base=[row["Start"]],
                        y=[row["Task"]],
                        orientation="h",
                        text=f"{row['Value']}",
                        hoverinfo="text",
                        hovertext=row["hover_text"],
                        marker=dict(opacity=0.7),
                    )
                    for _, row in df_timeline.iterrows()
                ]
            )
            fig.update_layout(
                title=f"{file_key} BUFF 时间线",
                xaxis_title="时间 (帧)",
                yaxis_title="BUFF名称",
                barmode="stack",
                yaxis=dict(autorange="reversed"),  # 反转Y轴
                height=max(400, len(df_timeline["Task"].unique()) * 30),  # 动态调整高度
                hovermode="closest",
                showlegend=False,  # 隐藏图例
            )
            st.plotly_chart(fig, use_container_width=True)


def _load_cached_buff_data(rid: int) -> dict[str, list[dict[str, Any]]] | None:
    """尝试从JSON缓存文件加载BUFF时间线数据。"""
    buff_log_path = os.path.join(results_dir, str(rid), "buff_log")
    json_file_path = os.path.join(buff_log_path, "buff_timeline_data.json")

    if os.path.exists(json_file_path):
        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # 加载失败，将视为缓存不存在
            return None
    return None


def _process_and_cache_buff_data(rid: int) -> dict[str, list[dict[str, Any]]] | None:
    """处理BUFF日志CSV文件，生成时间线数据，并缓存到JSON文件。

    此函数不处理UI反馈，仅负责数据处理和文件操作。

    Args:
        rid (int): 运行ID。

    Returns:
        Optional[dict[str, list[dict[str, Any]]]]: 处理后的BUFF时间线数据字典，
                                                   如果处理失败或无CSV文件则返回None。
                                                   如果找到CSV但处理后无数据，返回空字典 {}。
    """
    buff_log_path = os.path.join(results_dir, str(rid), "buff_log")
    json_file_path = os.path.join(buff_log_path, "buff_timeline_data.json")

    if not os.path.exists(buff_log_path):
        # 日志目录不存在，无法处理
        return None

    csv_files = [f for f in os.listdir(buff_log_path) if f.endswith(".csv")]
    if not csv_files:
        # 没有CSV文件，无需处理，但也无需创建JSON。返回空字典表示成功但无数据。
        return {}

    all_buff_data: dict[str, list[dict[str, Any]]] = {}
    processed_csv_files: list[str] = []
    has_processing_error = False

    for filename in csv_files:
        csv_file_path = os.path.join(buff_log_path, filename)
        df = pd.read_csv(csv_file_path)
        file_key = filename.replace(".csv", "")
        buff_data = _prepare_buff_timeline_data(df)
        all_buff_data[file_key] = buff_data
        processed_csv_files.append(csv_file_path)

    # 写入JSON缓存文件
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(all_buff_data, f, indent=4)

    # 删除原始CSV文件
    for csv_path in processed_csv_files:
        try:
            os.remove(csv_path)
        except Exception:
            print(f"删除文件 {csv_path} 时发生错误。")
            pass

    if has_processing_error:
        return None

    return all_buff_data


def process_buff_result(rid: int) -> None:
    """处理并展示指定运行ID的BUFF时间线结果。

    首先尝试加载缓存，如果失败则处理原始数据并缓存，然后绘制图表。

    Args:
        rid (int): 运行ID。
    """
    # 1. 尝试从缓存加载数据
    all_buff_data = _load_cached_buff_data(rid)

    if all_buff_data is not None:
        pass
    else:
        # 缓存未命中或加载失败，处理原始数据
        st.write("首次加载buff结果或缓存失效，正在处理数据，可能需要一些时间...")

        all_buff_data = _process_and_cache_buff_data(rid)

        if all_buff_data is None:
            st.error("处理BUFF日志数据时发生错误，无法生成结果。")
            return

    # 2. 绘制图表 (无论数据来自缓存还是新处理)
    if all_buff_data:
        _draw_buff_timeline_charts(all_buff_data)
    elif all_buff_data == {}:
        # 明确处理空字典的情况（无CSV文件但处理流程正常）
        st.info("没有可用于绘制图表的BUFF数据。")
