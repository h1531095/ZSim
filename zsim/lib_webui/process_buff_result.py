import json
import os
import asyncio
import aiofiles
import aiofiles.os
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

        # 按行遍历每个tick
        for index, row in df.iterrows():
            tick = row["time_tick"]
            value = row[buff_name]

            # 检查值是否为 NaN 或 None，用作判断
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


def _load_cached_buff_data(rid: int | str) -> dict[str, list[dict[str, Any]]] | None:
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


async def prepare_buff_data_and_cache(
    rid: int | str,
) -> dict[str, list[dict[str, Any]]] | None:
    """异步处理BUFF日志CSV文件，生成时间线数据，并缓存到JSON文件。

    此函数不处理UI反馈，仅负责数据处理和文件操作。

    Args:
        rid (int | str): 运行ID。

    Returns:
        dict[str, list[dict[str, Any]]] | None: 处理后的BUFF时间线数据字典，
                                                如果处理失败或无CSV文件则返回None。
                                                如果找到CSV但处理后无数据，返回空字典 {}。
    """
    buff_log_path = os.path.join(results_dir, str(rid), "buff_log")
    json_file_path = os.path.join(buff_log_path, "buff_timeline_data.json")

    if not await aiofiles.os.path.exists(buff_log_path):
        # 日志目录不存在，无法处理
        return None

    try:
        all_files = await aiofiles.os.listdir(buff_log_path)
        csv_files = [f for f in all_files if f.endswith(".csv")]
    except FileNotFoundError:
        # listdir 可能在目录刚创建时失败，或者权限问题
        return None
    except Exception as e:
        print(f"列出目录 {buff_log_path} 时发生错误: {e}")
        return None

    if not csv_files:
        # 没有CSV文件，无需处理，但也无需创建JSON。返回空字典表示成功但无数据。
        return {}

    all_buff_data: dict[str, list[dict[str, Any]]] = {}
    processed_csv_files: list[str] = []
    tasks = []

    async def process_csv(filename: str):
        nonlocal all_buff_data, processed_csv_files
        csv_file_path = os.path.join(buff_log_path, filename)
        try:
            # 使用 asyncio.to_thread 在单独的线程中运行同步的 pandas 操作
            df = await asyncio.to_thread(pd.read_csv, csv_file_path)
            file_key = filename.replace(".csv", "")
            # _prepare_buff_timeline_data 本身是同步的，可以在这里直接调用
            buff_data = _prepare_buff_timeline_data(df)
            all_buff_data[file_key] = buff_data
            processed_csv_files.append(csv_file_path)
        except Exception as e:
            print(f"处理文件 {csv_file_path} 时发生错误: {e}")
            # 可以选择在这里标记错误，或者让 gather 捕获
            raise  # 重新抛出异常，让 gather 知道有错误

    # 为每个CSV文件创建一个处理任务
    for filename in csv_files:
        tasks.append(process_csv(filename))

    # 并发执行所有CSV处理任务
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 检查是否有处理错误
    has_processing_error = any(isinstance(res, Exception) for res in results)

    if has_processing_error:
        print("处理CSV文件时至少发生一个错误。")
        return None

    # 如果没有处理错误或者决定即使有错误也要继续
    if all_buff_data:  # 确保有数据才写入
        try:
            # 异步写入JSON缓存文件
            async with aiofiles.open(json_file_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(all_buff_data, indent=4, ensure_ascii=False))
        except Exception as e:
            print(f"写入JSON文件 {json_file_path} 时发生错误: {e}")
            has_processing_error = True  # 标记写入错误

    # 异步删除原始CSV文件
    if processed_csv_files:
        delete_tasks = [
            aiofiles.os.remove(csv_path) for csv_path in processed_csv_files
        ]
        delete_results = await asyncio.gather(*delete_tasks, return_exceptions=True)
        for i, res in enumerate(delete_results):
            if isinstance(res, Exception):
                print(f"删除文件 {processed_csv_files[i]} 时发生错误: {res}")
                # 删除失败通常不认为是关键错误，只打印日志

    # 如果在处理或写入JSON时发生错误，返回None
    if has_processing_error:
        return None

    return all_buff_data


def show_buff_result(rid: int | str) -> None:
    """显示指定运行ID的BUFF结果，优先从缓存加载，否则处理CSV并缓存。"""
    st.header(f"运行 {rid} 的 BUFF 分析")

    # 尝试加载缓存数据
    cached_data = _load_cached_buff_data(rid)

    if cached_data is not None:
        st.info("从缓存加载BUFF数据。")
        all_buff_data = cached_data
    else:
        st.info("未找到缓存，正在处理BUFF日志文件...")
        # 注意：Streamlit 本身不是异步框架，直接 await 会阻塞
        # 需要在 Streamlit 环境中运行异步代码，通常使用 asyncio.run() 或类似机制
        # 但这会阻塞 Streamlit 的执行线程。更好的方法是启动一个后台任务
        # 或者，如果此函数总是在异步上下文中调用，则可以直接 await
        # 假设此函数可能在同步上下文被调用，我们需要处理这种情况
        try:
            # 尝试获取或创建事件循环来运行异步函数
            loop = asyncio.get_running_loop()
            # 如果在异步环境，直接 await
            all_buff_data = loop.run_until_complete(prepare_buff_data_and_cache(rid))
        except RuntimeError:  # 没有正在运行的事件循环
            # 在同步环境，需要创建一个新的事件循环来运行
            all_buff_data = asyncio.run(prepare_buff_data_and_cache(rid))

        if all_buff_data is None:
            st.error("处理BUFF日志文件失败。")
            return
        elif not all_buff_data:
            st.warning("在日志目录中未找到BUFF相关的CSV文件。")
            # 即使没有数据，也绘制一个空状态或提示
            _draw_buff_timeline_charts({})  # 传递空字典以显示无数据消息
            return
        else:
            st.success("BUFF日志处理完成并已缓存。")

    # 绘制图表
    _draw_buff_timeline_charts(all_buff_data)
