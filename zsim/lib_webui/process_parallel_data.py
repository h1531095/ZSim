import asyncio
import json
import os
from typing import Any

import aiofiles
import plotly.graph_objects as go
import streamlit as st
from define import results_dir
from lib_webui.process_buff_result import show_buff_result
from lib_webui.process_dmg_result import show_dmg_result

from .constants import stats_trans_mapping
from .process_buff_result import prepare_buff_data_and_cache
from .process_dmg_result import prepare_dmg_data_and_cache

reversed_stats_trans_mapping = {v: k for k, v in stats_trans_mapping.items()}


def judge_parallel_result(rid: int | str) -> bool:
    """判断对应的rid是否为并行模式。

    Args:
        rid (int): 运行ID。

    Returns:
        bool: 如果是并行模式，则返回True；否则返回False。
    """
    result_dir = os.path.join(results_dir, str(rid))
    if not os.path.isdir(result_dir):
        return False

    parallel_config_path = os.path.join(result_dir, ".parallel_config.json")
    if not os.path.exists(parallel_config_path):
        return False

    try:
        with open(parallel_config_path, "r", encoding="utf-8") as f:
            parallel_config: dict = json.load(f)
        if not parallel_config.get("enabled", False):
            return False
    except (json.JSONDecodeError, IOError):
        # 如果文件读取或解析失败，也视为非并行模式
        return False

    # 检查是否存在至少一个包含 sub.parallel_config.json 的子目录
    for item in os.listdir(result_dir):
        sub_dir_path = os.path.join(result_dir, item)
        if os.path.isdir(sub_dir_path):
            sub_config_path = os.path.join(sub_dir_path, "sub.parallel_config.json")
            if os.path.exists(sub_config_path):
                return True

    return False


async def _process_sub_damage(sub_rid: str) -> None:
    """异步处理单个子目录的数据。

    Args:
        sub_rid (str): 子运行ID。
    """
    # prepare_dmg_data_and_cache 不是异步函数，使用 to_thread
    await asyncio.to_thread(prepare_dmg_data_and_cache, sub_rid)


async def _process_sub_buff(sub_rid: str) -> None:
    """异步处理单个子目录的数据。

    Args:
        sub_rid (str): 子运行ID。
    """
    await prepare_buff_data_and_cache(sub_rid)


async def prepare_parallel_data_and_cache(rid: int | str) -> None:
    """对并行模式的每一份报告进行数据预处理，并将结果缓存到本地（异步执行）。

    Args:
        rid (int | str): 运行ID。
    """
    result_dir = os.path.join(results_dir, str(rid))
    parallel_config_path = os.path.join(result_dir, ".parallel_config.json")

    try:
        with open(parallel_config_path, "r", encoding="utf-8") as f:
            parallel_config: dict = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        st.error(f"读取或解析并行配置文件 {parallel_config_path} 失败: {e}")
        return

    if parallel_config.get("adjust_sc", {}).get("enabled", False):
        merged_sc_file_path = os.path.join(result_dir, "merged_sc_data.json")
        if os.path.exists(merged_sc_file_path):
            return

    tasks = []

    for item in os.listdir(result_dir):
        sub_dir_path = os.path.join(result_dir, item)
        if os.path.isdir(sub_dir_path):
            sub_config_path = os.path.join(sub_dir_path, "sub.parallel_config.json")
            if os.path.exists(sub_config_path):
                sub_rid: str = os.path.join(str(rid), item)  # 子进程rid
                # 创建异步任务
                tasks.append(_process_sub_damage(sub_rid))

    # 并发执行所有任务
    if tasks:
        await asyncio.gather(*tasks)


# 统计并行模式的个子进程伤害归并结果
def merge_parallel_dmg_data(
    rid: int | str,
) -> dict[str, dict[str, dict[int | float, dict[str, float | None]]]]:
    """对并行模式的每一份报告进行数据预处理，并将结果缓存到本地。

    Args:
        rid (int): 运行ID。
    """
    result_dir = os.path.join(results_dir, str(rid))
    parallel_config_path = os.path.join(result_dir, ".parallel_config.json")

    with open(parallel_config_path, "r", encoding="utf-8") as f:
        parallel_config: dict = json.load(f)

    if parallel_config.get("adjust_sc", {}).get("enabled", False):
        # 属性收益曲线功能
        merged_sc_file_path = os.path.join(result_dir, "merged_sc_data.json")
        if os.path.exists(merged_sc_file_path):
            with open(merged_sc_file_path, "r", encoding="utf-8") as f:
                sc_merged_data = json.load(f)
        else:
            try:
                st.info("首次处理读取属性收益曲线数据，请稍等...")
                sc_merged_data = asyncio.run(merge_parallel_sc_data(rid))
                st.success("属性收益曲线数据合并完成！")
                # 将合并后的数据保存到 JSON 文件
                merged_sc_file_path = os.path.join(result_dir, "merged_sc_data.json")
                try:
                    with open(merged_sc_file_path, "w", encoding="utf-8") as f:
                        json.dump(sc_merged_data, f, indent=4, ensure_ascii=False)
                    st.success(f"合并的属性收益曲线数据已保存至 {merged_sc_file_path}")
                except IOError as e:
                    st.error(f"保存合并的属性收益曲线数据失败: {e}")

            except Exception as e:
                st.error(f"合并属性收益曲线数据时出错: {e}")
        return sc_merged_data
    else:
        return


def draw_sc_attr_graph(
    sc_merged_data: dict[str, dict[str, dict[int | float, dict[str, float | None]]]],
) -> None:
    # 绘制折线图
    if sc_merged_data:
        for char_name, char_data in sc_merged_data.items():
            fig = go.Figure()
            has_data = False  # 标记是否有数据添加到图表中

            for sc_name, sc_values_results in char_data.items():
                # sc_values_results 的结构现在是 {sc_value: {"result": float, "rate": float | None}}
                # 数据在 merge_parallel_sc_data 中已经按 sc_value 排序
                if not sc_values_results:
                    st.warning(
                        f"角色 '{char_name}' 的词条 '{sc_name}' 没有数据，跳过绘制。"
                    )
                    continue

                # 提取 x 值 (词条值) 和 y 值 (收益率)
                x_values_raw = list(sc_values_results.keys())
                # 提取预计算的收益率，跳过第一个点（收益率通常为None）
                y_values_rate = [
                    data.get("rate") for data in sc_values_results.values()
                ]

                # 尝试将 x 值转换为浮点数
                try:
                    x_values = [float(x) for x in x_values_raw]
                except ValueError:
                    st.warning(
                        f"角色 '{char_name}' 的词条 '{sc_name}' 包含非数值的 x 值，跳过绘制。"
                    )
                    continue

                # 确保有足够的数据点来绘制收益率（至少需要两个原始点才能计算一个收益率点）
                if len(x_values) < 2:
                    st.warning(
                        f"角色 '{char_name}' 的词条 '{sc_name}' 数据点不足 (<2)，无法绘制收益率曲线。"
                    )
                    continue

                # 过滤掉第一个点的 x 值和 y 值（因为第一个点没有收益率）
                # 同时处理 y_values_rate 中可能存在的 None 值
                plot_x_values = []
                plot_y_values = []
                for i in range(1, len(x_values)):
                    if y_values_rate[i] is not None:
                        plot_x_values.append(x_values[i])
                        plot_y_values.append(y_values_rate[i])

                if not plot_x_values:
                    st.warning(
                        f"角色 '{char_name}' 的词条 '{sc_name}' 没有有效的收益率数据点，跳过绘制。"
                    )
                    continue

                fig.add_trace(
                    go.Scatter(
                        x=plot_x_values,  # 使用过滤后的 x 值
                        y=plot_y_values,  # 使用过滤后的 y 值 (收益率)
                        mode="lines+markers",
                        name=reversed_stats_trans_mapping.get(sc_name, sc_name),
                        connectgaps=False,  # 不连接 None 值造成的断点
                    )
                )
                has_data = True

            if has_data:
                # 计算整数刻度 (基于原始的所有 x_values)
                try:
                    # 确保只使用数值类型的 x 值
                    numeric_x_values = [
                        x for x in x_values if isinstance(x, (int, float))
                    ]
                    if not numeric_x_values:
                        raise ValueError("No numeric x values found")
                    min_x = min(numeric_x_values)
                    max_x = max(numeric_x_values)
                    # 生成从最小整数到最大整数的所有整数刻度
                    integer_ticks = list(
                        range(
                            int(min_x) if min_x == int(min_x) else int(min_x) + 1,
                            int(max_x) + 1,
                        )
                    )
                    # 如果最小值本身是整数，也包含它
                    if isinstance(min_x, int) or (
                        isinstance(min_x, float) and min_x.is_integer()
                    ):
                        if int(min_x) not in integer_ticks:
                            integer_ticks.insert(0, int(min_x))
                    integer_ticks.sort()  # 确保刻度排序
                except ValueError:  # 如果 x_values 为空或不包含数字
                    integer_ticks = []

                # fmt: off
                fig.update_layout(
                        title=f"{char_name} - 属性收益曲线",
                        xaxis_title="词条数",
                        yaxis_title="收益率",  # 更新 Y 轴标题
                        hovermode="x unified",
                        yaxis=dict(tickformat=".2%"),  # 将 Y 轴格式化为百分比
                        xaxis=dict(
                            tickmode="array" if integer_ticks else "auto",  # 如果有计算出的整数刻度则使用array模式
                            tickvals=integer_ticks if integer_ticks else None,  # 设置刻度值为整数
                            tickformat="d",  # 强制显示为整数
                        ),
                    )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"角色 '{char_name}' 没有足够的数据来绘制组合图表。")
                # fmt: on
    else:
        st.warning("没有可用于绘制属性收益曲线的数据。")


async def _read_json_file(file_path: str) -> dict[str, Any]:
    """异步读取JSON文件。

    Args:
        file_path (str): JSON文件路径。

    Returns:
        dict[str, Any]: 读取到的JSON内容，如果失败则返回空字典。
    """
    try:
        async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
            content = await f.read()
        return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
        # TODO: 使用更健壮的日志记录
        print(f"Error reading JSON file {file_path}: {e}")
        return {}


async def merge_parallel_sc_data(
    rid: int | str,
) -> dict[str, dict[str, dict[int | float, dict[str, float | None]]]]:
    """读取所有子进程的属性收益曲线数据，合并并计算收益率。

    Args:
        rid (int | str): 运行ID。

    Returns:
        dict[str, dict[str, dict[int | float, dict[str, float | None]]]]: {
            角色名(adjust_char): {
                词条名(sc_name): {
                    词条值(sc_value): {
                        "result": 原始结果(sc_result: float),
                        "rate": 收益率(rate_of_return: float | None)
                    }
                }
            }
        }
    """
    result_dir = os.path.join(results_dir, str(rid))
    all_sc_data: dict[str, dict[str, dict[int | float, float]]] = {}
    tasks = []
    sub_dir_paths_map: dict[int, str] = {}  # 存储 task index 到 sub_dir_path 的映射

    # 收集需要读取的文件路径
    task_index = 0
    for item in os.listdir(result_dir):
        sub_dir_path = os.path.join(result_dir, item)
        if os.path.isdir(sub_dir_path):
            sub_config_path = os.path.join(sub_dir_path, "sub.parallel_config.json")
            dmg_attribution_path = os.path.join(sub_dir_path, "damage_attribution.json")

            if os.path.exists(sub_config_path) and os.path.exists(dmg_attribution_path):
                # 添加读取配置文件的任务
                tasks.append(_read_json_file(sub_config_path))
                sub_dir_paths_map[task_index] = sub_dir_path  # 记录config对应的目录
                task_index += 1
                # 添加读取伤害数据的任务
                tasks.append(_read_json_file(dmg_attribution_path))
                sub_dir_paths_map[task_index] = sub_dir_path  # 记录dmg对应的目录
                task_index += 1

    # 并发执行所有文件读取任务
    if not tasks:
        print(f"在 {result_dir} 中未找到有效的子进程结果目录。")
        return {}

    results = await asyncio.gather(*tasks)

    # 处理读取结果
    i = 0
    while i < len(results):
        sub_config: dict[str, Any] = results[i]
        sc_data: dict[str, Any] = results[i + 1]
        current_sub_dir = sub_dir_paths_map.get(i, "未知子目录")  # 获取对应的子目录路径
        i += 2

        if not sub_config:
            print(
                f"警告：跳过子目录 {current_sub_dir}，因为 sub.parallel_config.json 读取失败或为空。"
            )
            continue
        if not sc_data:
            print(
                f"警告：跳过子目录 {current_sub_dir}，因为 damage_attribution.json 读取失败或为空。"
            )
            continue

        adjust_char: str | None = sub_config.get("adjust_char")
        sc_name: str | None = sub_config.get("sc_name")
        # sc_value 可能是 int 或 float
        sc_value_raw: Any = sub_config.get("sc_value")
        sc_value: int | float | None = None
        if isinstance(sc_value_raw, (int, float)):
            sc_value = sc_value_raw

        if adjust_char is None or sc_name is None or sc_value is None:
            print(
                f"警告：跳过子目录 {current_sub_dir}，缺少必要的配置信息 (adjust_char, sc_name, sc_value)。"
            )
            continue

        # damage_attribution.json 处理
        char_dmg_data: dict[str, Any] | None = sc_data.get(adjust_char)
        if char_dmg_data is None:
            print(
                f"警告：跳过子目录 {current_sub_dir}，在 damage_attribution.json 中未找到角色 '{adjust_char}' 的数据。"
            )
            continue

        # 伤害数据包含 direct_damage 和 anomaly_damage
        direct_damage: float = char_dmg_data.get("direct_damage", 0.0)
        anomaly_damage: float = char_dmg_data.get("anomaly_damage", 0.0)
        sc_result: float = direct_damage + anomaly_damage

        # 填充结果字典
        if adjust_char not in all_sc_data:
            all_sc_data[adjust_char] = {}
        if sc_name not in all_sc_data[adjust_char]:
            all_sc_data[adjust_char][sc_name] = {}

        # 检查 sc_value 是否已存在，如果存在则打印警告（理论上并行配置不应重复）
        if sc_value in all_sc_data[adjust_char][sc_name]:
            print(
                f"警告：在角色 '{adjust_char}' 的词条 '{sc_name}' 中，词条值 '{sc_value}' 重复出现。来自子目录: {current_sub_dir}"
            )

        # 存储原始结果
        all_sc_data[adjust_char][sc_name][sc_value] = {
            "result": sc_result,
            "rate": None,
        }

    # 对每个词条的值按 sc_value 排序并计算收益率
    for char_name, char_data in all_sc_data.items():
        for sc_name_key, sc_values_data in char_data.items():
            # 按 sc_value 排序
            try:
                # 尝试将键转换为浮点数进行排序
                sorted_items = sorted(
                    sc_values_data.items(), key=lambda item: float(item[0])
                )
            except ValueError:
                # 如果转换失败，按原始键（字符串）排序
                sorted_items = sorted(sc_values_data.items())

            # 更新排序后的字典，并计算收益率
            sorted_sc_data: dict[int | float, dict[str, float | None]] = {}
            previous_result: float | None = None
            for i, (sc_val, data) in enumerate(sorted_items):
                current_result = data["result"]
                rate = None
                if i > 0 and previous_result is not None and previous_result != 0:
                    rate = (current_result / previous_result) - 1

                sorted_sc_data[sc_val] = {"result": current_result, "rate": rate}
                previous_result = current_result

            # 用包含收益率的排序后字典替换原来的字典
            all_sc_data[char_name][sc_name_key] = sorted_sc_data

    return all_sc_data


def process_parallel_result(rid: int | str) -> None:
    """处理并行模式的结果。

    Args:
        rid (int): 运行ID。
    """
    result_dir = os.path.join(results_dir, str(rid))

    # 1. 预处理每个子目录的数据（伤害、Buff等）
    with st.spinner(
        "开始预处理并行子目录数据，初次处理会持续一段时间...", show_time=True
    ):
        asyncio.run(prepare_parallel_data_and_cache(rid))


    # 2. 合并需要聚合的数据（例如属性收益曲线）
    sc_merged_data = merge_parallel_dmg_data(rid)
    # 3. 绘制图表
    draw_sc_attr_graph(sc_merged_data)

    # 4. 获取有效的子目录列表
    sub_dirs = []
    if os.path.isdir(result_dir):
        for item in os.listdir(result_dir):
            sub_dir_path = os.path.join(result_dir, item)
            if os.path.isdir(sub_dir_path):
                sub_config_path = os.path.join(sub_dir_path, "sub.parallel_config.json")
                if os.path.exists(sub_config_path):
                    sub_dirs.append(item)  # 添加子目录名称

    st.markdown("--- ")
    st.write("选择要查看的子进程报告")
    col1, col2 = st.columns(2)
    with col1:
        # 5. 添加下拉选择框以选择子进程报告
        if sub_dirs:
            selected_sub_dir = st.selectbox(
                "选择要查看的子进程报告",
                options=sub_dirs,
                key=f"selectbox_sub_dir_{rid}",
                label_visibility="collapsed",
            )
            selected_key = f"{rid}\{selected_sub_dir}"

        else:
            st.info("未找到有效的子进程结果目录。")

    with col2:
        # 6. 提供按钮处理全部buff结果以节约储存
        if st.button(
            "处理全部BUFF结果",
            key=f"toggle_buff_{selected_key}",
            help="处理所有buff结果可以节约大量储存空间，但耗时较长",
        ):
            with st.spinner("开始处理所有子进程BUFF结果...", show_time=True):

                async def process_all_sub_buff():
                    """处理所有子进程的BUFF结果。"""
                    tasks = []
                    for sub_dir in sub_dirs:
                        sub_rid = f"{rid}\{sub_dir}"
                        tasks.append(_process_sub_buff(sub_rid))
                    await asyncio.gather(*tasks)

                asyncio.run(process_all_sub_buff())

    if st.button("显示子进程伤害结果", key=f"toggle_dmg_{selected_key}"):
        show_dmg_result(selected_key)
        show_buff_result(selected_key)

    # TODO: 添加其他并行结果的处理逻辑，例如生成聚合报告、绘制对比图表等。
    st.warning("并行模式的结果合并与展示功能仍在开发中。", icon="⚠️")
