import asyncio
import json
import os
from typing import Any

import aiofiles
import plotly.graph_objects as go
import streamlit as st
from define import results_dir

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


async def _process_sub_directory(sub_rid: str) -> None:
    """异步处理单个子目录的数据。

    Args:
        sub_rid (str): 子运行ID。
    """
    # prepare_dmg_data_and_cache 不是异步函数，使用 to_thread
    await asyncio.to_thread(prepare_dmg_data_and_cache, sub_rid)
    await prepare_buff_data_and_cache(sub_rid)


async def prepare_parallel_data_and_cache(rid: int | str) -> None:
    """对并行模式的每一份报告进行数据预处理，并将结果缓存到本地（异步执行）。

    Args:
        rid (int | str): 运行ID。
    """
    result_dir = os.path.join(results_dir, str(rid))
    tasks = []

    for item in os.listdir(result_dir):
        sub_dir_path = os.path.join(result_dir, item)
        if os.path.isdir(sub_dir_path):
            sub_config_path = os.path.join(sub_dir_path, "sub.parallel_config.json")
            if os.path.exists(sub_config_path):
                sub_rid: str = os.path.join(str(rid), item)  # 子进程rid
                # 创建异步任务
                tasks.append(_process_sub_directory(sub_rid))

    # 并发执行所有任务
    if tasks:
        await asyncio.gather(*tasks)


# 统计并行模式的个子进程伤害归并结果
def merge_parallel_dmg_data(rid: int | str) -> None:
    """对并行模式的每一份报告进行数据预处理，并将结果缓存到本地。

    Args:
        rid (int): 运行ID。
    """
    result_dir = os.path.join(results_dir, str(rid))
    parallel_config_path = os.path.join(result_dir, ".parallel_config.json")
    if not os.path.exists(parallel_config_path):
        st.error(f"并行配置文件 {parallel_config_path} 不存在！")
        return

    try:
        with open(parallel_config_path, "r", encoding="utf-8") as f:
            parallel_config: dict = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        st.error(f"读取或解析并行配置文件 {parallel_config_path} 失败: {e}")
        return

    if parallel_config.get("adjust_sc", {}).get("enabled", False):
        # 属性收益曲线功能
        merged_sc_file_path = os.path.join(result_dir, "merged_sc_data.json")
        if os.path.exists(merged_sc_file_path):
            with open(merged_sc_file_path, "r", encoding="utf-8") as f:
                sc_merged_data = json.load(f)
        else:
            try:
                st.info(
                    f"首次尝试从 {merged_sc_file_path} 读取属性收益曲线数据，请稍等..."
                )
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
        # 绘制折线图
        if sc_merged_data:
            for char_name, char_data in sc_merged_data.items():
                fig = go.Figure()
                has_data = False  # 标记是否有数据添加到图表中

                for sc_name, sc_values_results in char_data.items():
                    # 确保键是数值类型并排序
                    try:
                        sorted_items = sorted(
                            sc_values_results.items(), key=lambda item: float(item[0])
                        )
                    except ValueError:
                        # 如果转换失败（例如键不是数字字符串），按原始键排序
                        sorted_items = sorted(sc_values_results.items())

                    # 使用排序后的原始数据
                    if not sorted_items:
                        st.warning(
                            f"角色 '{char_name}' 的词条 '{sc_name}' 没有数据，跳过绘制。"
                        )
                        continue

                    x_values_raw = [item[0] for item in sorted_items]
                    y_values_raw = [float(item[1]) for item in sorted_items]

                    # 检查 x_values_raw 是否包含非数值类型，以防万一
                    try:
                        x_values = [float(x) for x in x_values_raw]
                    except ValueError:
                        st.warning(
                            f"角色 '{char_name}' 的词条 '{sc_name}' 包含非数值的 x 值，跳过绘制。"
                        )
                        continue

                    if not x_values or not y_values_raw or len(x_values) < 1:
                        st.warning(
                            f"角色 '{char_name}' 的词条 '{sc_name}' 数据不足，无法计算收益率或绘制图表。"
                        )
                        continue

                    # 计算收益率
                    y_values_rate = [None] * len(y_values_raw)  # 初始化为 None
                    if len(y_values_raw) > 0:
                        for i in range(1, len(y_values_raw)):
                            if y_values_raw[i - 1] != 0:
                                y_values_rate[i] = (
                                    y_values_raw[i] / y_values_raw[i - 1]
                                ) - 1
                            else:
                                # 如果前一个值为0，则无法计算比率，设为 None
                                y_values_rate[i] = None

                    fig.add_trace(
                        go.Scatter(
                            x=x_values,
                            y=y_values_rate,
                            mode="lines+markers",
                            name=reversed_stats_trans_mapping[sc_name],
                            connectgaps=False,
                        )
                    )
                    has_data = True

                if has_data:
                    # 计算整数刻度 (基于原始 x_values)
                    try:
                        min_x = min(x for x in x_values if isinstance(x, (int, float)))
                        max_x = max(x for x in x_values if isinstance(x, (int, float)))
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
                            integer_ticks.insert(0, int(min_x))
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

    else:
        st.info("未启用属性收益曲线调整功能。")
        return


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
) -> dict[str, dict[str, dict[int | float, float]]]:
    """读取所有子进程的属性收益曲线数据并合并。

    Args:
        rid (int | str): 运行ID。

    Returns:
        dict[str, dict[str, dict[int | float, float]]]: {
            角色名(adjust_char): {
                词条名(sc_name): {
                    词条值(sc_value): 结果(sc_result: float)
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

        all_sc_data[adjust_char][sc_name][sc_value] = sc_result

    # 对每个词条的值按 sc_value 排序 (可选，但通常有用)
    for char_data in all_sc_data.values():
        for sc_name_key in char_data:
            # 使用 sorted 创建排序后的列表，然后转换为字典
            sorted_items = sorted(char_data[sc_name_key].items())
            char_data[sc_name_key] = dict(sorted_items)

    return all_sc_data


def process_parallel_result(rid: int | str) -> None:
    """处理并行模式的结果。

    Args:
        rid (int): 运行ID。
    """
    # 1. 预处理每个子目录的数据（伤害、Buff等）
    with st.spinner("开始预处理并行子目录数据，初次处理会持续一段时间...", show_time=True):
        try:
            asyncio.run(prepare_parallel_data_and_cache(rid))
        except Exception as e:
            st.error(f"预处理子目录数据时出错: {e}")
            return

    # 2. 合并需要聚合的数据（例如属性收益曲线）
    merge_parallel_dmg_data(rid)

    # TODO: 添加其他并行结果的处理逻辑，例如生成聚合报告、绘制对比图表等。
    st.warning("并行模式的结果合并与展示功能仍在开发中。", icon="⚠️")
