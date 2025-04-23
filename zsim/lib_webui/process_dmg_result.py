import json
import os
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st
from define import ANOMALY_MAPPING
from sim_progress.Character.skill_class import lookup_name_or_cid

from .constants import element_mapping, results_dir


def _load_dmg_data(rid: int | str) -> pd.DataFrame | None:
    """加载指定运行ID的伤害数据CSV文件。

    Args:
        rid (int): 运行ID。

    Returns:
        Optional[pd.DataFrame]: 加载的伤害数据DataFrame，如果文件未找到则返回None。
    """
    try:
        csv_file_path = f"{results_dir}/{rid}/damage.csv"
        return pd.read_csv(csv_file_path)
    except FileNotFoundError:
        st.error(f"未找到文件：{csv_file_path}")
        return None


def prepare_line_chart_data(dmg_result_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """准备用于绘制伤害与失衡曲线图的数据。

    Args:
        dmg_result_df (pd.DataFrame): 原始伤害数据。

    Returns:
        dict[str, Any]: 包含处理后数据的字典，用于绘制折线图。
            - 'line_chart_df': 包含时间、伤害、DPS、失衡值、失衡效率的DataFrame。
    """
    processed_df = dmg_result_df.copy()
    # 计算DPS
    processed_df["dps"] = (
        processed_df["dmg_expect"].cumsum() / processed_df["tick"] * 60
    )

    # 处理失衡值
    if "失衡状态" in processed_df.columns:
        processed_df.loc[processed_df["失衡状态"], "stun"] = 0

    # 计算失衡效率
    first_stun_index = processed_df[processed_df["失衡状态"] == True].index.min()  # noqa: E712
    if pd.notna(first_stun_index):
        processed_df.loc[:first_stun_index, "stun_efficiency"] = (
            processed_df.loc[:first_stun_index, "stun"].cumsum()
            / processed_df.loc[:first_stun_index, "tick"]
            * 60
        )
        processed_df.loc[first_stun_index + 1 :, "stun_efficiency"] = None
    else:
        processed_df["stun_efficiency"] = (
            processed_df["stun"].cumsum() / processed_df["tick"] * 60
        )

    return {"line_chart_df": processed_df}


def draw_line_chart(chart_data: dict[str, Any]) -> None:
    """绘制伤害与失衡曲线图。

    Args:
        chart_data (Dict[str, Any]): 包含绘制图表所需数据的字典。
    """
    df = chart_data["line_chart_df"]
    with st.expander("伤害与失衡曲线："):
        # 时间-伤害分布
        st.subheader("时间-伤害分布")
        fig_dmg = px.line(
            df,
            x="tick",
            y=["dmg_expect", "dmg_crit"],
            labels={
                "tick": "时间（帧数）",
                "value": "伤害值",
                "variable": "数据类型",
                "dmg_expect": "期望伤害",
                "dmg_crit": "暴击伤害",
            },
        )
        st.plotly_chart(fig_dmg)

        # 时间-DPS分布
        st.subheader("时间-DPS分布")
        fig_dps = px.line(
            df,
            x="tick",
            y="dps",
            labels={"tick": "时间（帧数）", "dps": "DPS"},
        )
        st.plotly_chart(fig_dps)

        # 时间-失衡值分布
        st.subheader("时间-失衡值分布")
        fig_stun = px.line(
            df,
            x="tick",
            y="stun",
            labels={"tick": "时间（帧数）", "stun": "失衡值"},
        )
        st.plotly_chart(fig_stun)

        # 时间-失衡效率分布
        st.subheader("时间-失衡效率分布")
        fig_stun_eff = px.line(
            df,
            x="tick",
            y="stun_efficiency",
            labels={"tick": "时间（帧数）", "stun_efficiency": "失衡效率（每秒）"},
        )
        st.plotly_chart(fig_stun_eff)


def sort_df_by_UUID(dmg_result_df: pd.DataFrame) -> pd.DataFrame:
    """按UUID对伤害数据进行分组和聚合。

    Args:
        dmg_result_df (pd.DataFrame): 原始伤害数据。

    Returns:
        pd.DataFrame: 按UUID聚合后的数据，包含每个UUID的总伤害、总失衡、总积蓄等信息。

    Raises:
        ValueError: 如果DataFrame缺少必要的列。
    """
    required_columns = [
        "skill_tag",
        "dmg_expect",
        "stun",
        "buildup",
        "UUID",
        "is_anomaly",
    ]
    for col in required_columns:
        if col not in dmg_result_df.columns:
            raise ValueError(f"DataFrame 中缺少必要的列: {col}")

    result_data = []
    all_UUID = dmg_result_df["UUID"].unique()

    for UUID in all_UUID:
        same_UUID_rows = dmg_result_df[dmg_result_df["UUID"] == UUID]
        dmg_expect_sum = same_UUID_rows["dmg_expect"].fillna(0).sum()
        stun_sum = same_UUID_rows["stun"].fillna(0).sum()
        buildup_sum = same_UUID_rows["buildup"].fillna(0).sum()

        skill_tags = same_UUID_rows["skill_tag"].dropna()
        skill_tag = skill_tags.iloc[0] if not skill_tags.empty else None
        is_anomaly = same_UUID_rows["is_anomaly"].iloc[0]
        element_types = same_UUID_rows["element_type"].dropna()
        element_type = element_types.iloc[0] if not element_types.empty else None

        cid: int | str | None = None
        name: str | None = None
        if skill_tag:
            cid_str = skill_tag[0:4]
            try:
                name, cid_lookup = lookup_name_or_cid(cid=cid_str)
                cid = cid_lookup
            except ValueError:
                name = skill_tag  # 如果查找失败，使用skill_tag作为名字
                cid = None

        result_data.append(
            {
                "UUID": UUID,
                "name": name,
                "element_type": element_type,
                "is_anomaly": is_anomaly,
                "cid": cid,
                "skill_tag": skill_tag,
                "dmg_expect_sum": dmg_expect_sum,
                "stun_sum": stun_sum,
                "buildup_sum": buildup_sum,
            }
        )

    return pd.DataFrame(result_data)


def prepare_char_chart_data(uuid_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """准备用于绘制角色参与度分布图的数据。

    Args:
        uuid_df (pd.DataFrame): 按UUID聚合后的伤害数据。

    Returns:
        Dict[str, Any]: 包含绘制饼图所需数据的字典。
            - 'char_dmg_df': 按角色分组的伤害总和。
            - 'char_stun_df': 按角色分组的失衡总和。
            - 'char_skill_dmg_df': 按角色和技能标签分组的伤害总和。
            - 'char_element_df': 按角色和元素类型分组的积蓄总和。
    """
    # 各伤害来源占比
    char_dmg_df = (
        uuid_df[uuid_df["dmg_expect_sum"] > 0]
        .groupby(["name", "is_anomaly"])["dmg_expect_sum"]
        .sum()
        .reset_index()
    )

    # 角色失衡占比
    char_stun_df = (
        uuid_df[uuid_df["stun_sum"] > 0].groupby("name")["stun_sum"].sum().reset_index()
    )

    # 角色技能输出占比
    filtered_skill_df = uuid_df[uuid_df["cid"].notna()]
    char_skill_dmg_df = (
        filtered_skill_df.groupby(["name", "skill_tag"])["dmg_expect_sum"]
        .sum()
        .reset_index()
    )

    # 角色属性积蓄占比
    filtered_buildup_df = uuid_df[uuid_df["buildup_sum"] > 0]
    char_element_df = (
        filtered_buildup_df.groupby(["name", "element_type"])["buildup_sum"]
        .sum()
        .reset_index()
    )

    return {
        "char_dmg_df": char_dmg_df,
        "char_stun_df": char_stun_df,
        "char_skill_dmg_df": char_skill_dmg_df,
        "char_element_df": char_element_df,
    }


def draw_char_chart(chart_data: dict[str, pd.DataFrame]) -> None:
    """绘制角色参与度分布图。

    Args:
        chart_data (Dict[str, Any]): 包含绘制图表所需数据的字典。
    """
    char_dmg_df = chart_data["char_dmg_df"]
    char_stun_df = chart_data["char_stun_df"]
    char_skill_dmg_df = chart_data["char_skill_dmg_df"]
    char_element_df = chart_data["char_element_df"]

    with st.expander("角色参与度分布情况："):
        cols1 = st.columns(2)
        # 角色伤害占比分布
        with cols1[0]:
            st.subheader("队伍伤害来源占比")
            if not char_dmg_df.empty:
                fig_dmg_pie = px.pie(
                    char_dmg_df,
                    names="name",
                    values="dmg_expect_sum",
                    labels={"name": "来源", "dmg_expect_sum": "期望伤害总和"},
                )
                st.plotly_chart(fig_dmg_pie)
            else:
                st.info("没有非零伤害数据可供显示")

        # 角色失衡占比分布
        with cols1[1]:
            st.subheader("队伍失衡来源占比")
            if not char_stun_df.empty:
                fig_stun_pie = px.pie(
                    char_stun_df,
                    names="name",
                    values="stun_sum",
                    labels={"name": "来源", "stun_sum": "失衡值总和"},
                )
                st.plotly_chart(fig_stun_pie)
            else:
                st.info("没有非零失衡值数据可供显示")

        # 每个角色的各技能输出占比分布
        st.subheader("各角色技能输出占比")
        unique_names = char_skill_dmg_df["name"].unique()
        if len(unique_names) > 0:
            cols2 = st.columns(len(unique_names))
            col_index = 0
            for name, group in char_skill_dmg_df.groupby("name"):
                with cols2[col_index]:
                    st.caption(f"{name}")  # 使用caption代替subheader以节省空间
                    fig_skill_pie = px.pie(
                        group,
                        names="skill_tag",
                        values="dmg_expect_sum",
                        labels={
                            "skill_tag": "技能标签",
                            "dmg_expect_sum": "期望伤害总和",
                        },
                    )
                    st.plotly_chart(fig_skill_pie)
                col_index += 1
        else:
            st.info("没有角色技能伤害数据可供显示")

        # 每个角色各属性的积蓄占比
        st.subheader("各属性积蓄来源占比")
        unique_elements = char_element_df["element_type"].unique()
        if len(unique_elements) > 0:
            cols3 = st.columns(len(unique_elements))
            col_index = 0
            for element in unique_elements:
                element_df = char_element_df[char_element_df["element_type"] == element]
                element_name = element_mapping.get(element, element)  # 获取元素中文名
                with cols3[col_index]:
                    st.caption(f"{element_name}")  # 使用caption代替subheader
                    fig_buildup_pie = px.pie(
                        element_df,
                        names="name",
                        values="buildup_sum",
                        labels={"name": "角色", "buildup_sum": "积蓄值总和"},
                    )
                    st.plotly_chart(fig_buildup_pie)
                col_index += 1
        else:
            st.info("没有属性积蓄数据可供显示")


def _find_consecutive_true_ranges(
    df: pd.DataFrame, column: str
) -> list[tuple[int, int]]:
    """查找DataFrame列中连续为True的范围。

    Args:
        df (pd.DataFrame): 输入的DataFrame，需要包含 'tick' 列。
        column (str): 要查找的布尔列名。

    Returns:
        list[tuple[int, int]]: 一个包含 (开始tick, 结束tick) 元组的列表。
    """
    ranges = []
    start = None
    for i, row in df.iterrows():
        if row[column]:
            if start is None:
                start = row["tick"]
        else:
            if start is not None:
                # 结束tick应该是上一个为True的tick
                prev_tick = df["tick"].iloc[i - 1] if i > 0 else start
                ranges.append((start, prev_tick))
                start = None
    # 处理最后一个区间（如果存在）
    if start is not None:
        ranges.append((start, df["tick"].iloc[-1]))
    return ranges


def prepare_timeline_data(dmg_result_df: pd.DataFrame) -> pd.DataFrame | None:
    """准备用于绘制异常状态时间线的数据。

    Args:
        dmg_result_df (pd.DataFrame): 原始伤害数据。

    Returns:
        Optional[pd.DataFrame]: 用于绘制Gantt图的DataFrame，如果缺少列或无数据则返回None。
    """
    required_columns = [
        "冻结",
        "霜寒",
        "畏缩",
        "感电",
        "灼烧",
        "侵蚀",
        "烈霜霜寒",
        "tick",
    ]
    missing_cols = [col for col in required_columns if col not in dmg_result_df.columns]
    if missing_cols:
        st.error(f"输入数据缺少必要的列: {missing_cols}")
        return None

    columns_to_check = ["冻结", "霜寒", "畏缩", "感电", "灼烧", "侵蚀", "烈霜霜寒"]
    gantt_data = []
    for col in columns_to_check:
        if col in dmg_result_df.columns:
            ranges = _find_consecutive_true_ranges(dmg_result_df, col)
            for start, end in ranges:
                gantt_data.append({"Task": col, "Start": start, "Finish": end})

    if not gantt_data:
        return None

    gantt_df = pd.DataFrame(gantt_data)
    gantt_df["Duration"] = (
        gantt_df["Finish"] - gantt_df["Start"] + 1
    )  # 持续时间包含首尾
    return gantt_df


def draw_char_timeline(gantt_df: pd.DataFrame | None) -> None:
    """绘制异常状态时间线（Gantt图）。

    Args:
        gantt_df: 用于绘制Gantt图的数据，如果为None则不绘制。
    """
    with st.expander("异常时间线："):
        if gantt_df is not None and not gantt_df.empty:
            fig_timeline = px.bar(
                gantt_df,
                x="Duration",
                y="Task",
                base="Start",
                orientation="h",
                labels={
                    "Start": "开始时间(帧)",
                    "Duration": "持续时间(帧)",
                    "Task": "状态类型",
                },
            )
            st.plotly_chart(fig_timeline)
        else:
            st.warning("没有找到任何连续的状态数据")




def calculate_and_save_anomaly_attribution(
    rid: int, char_dmg_df: pd.DataFrame, char_element_df: pd.DataFrame
) -> None:
    """计算并保存异常伤害归因。

    Args:
        rid (int): 运行ID。
        char_dmg_df (pd.DataFrame): 角色直接伤害数据。
        char_element_df (pd.DataFrame): 角色元素积蓄数据。
    """
    output_path = f"{results_dir}/{rid}/damage_attribution.json"
    # 检查文件是否已存在
    if os.path.exists(output_path):
        return
    # 计算每种元素类型的异常总伤害
    anomaly_name_list = list(ANOMALY_MAPPING.values()) + ["极性紊乱", "异放"]
    anomaly_damage_totals = {element: 0 for element in anomaly_name_list}
    for anomaly_name in anomaly_name_list:
        if anomaly_name in char_dmg_df["name"].values:
            for _, row in char_dmg_df.iterrows():
                if anomaly_name in row["name"]:
                    anomaly_damage_totals[anomaly_name] += row["dmg_expect_sum"]

    # 初始化一个包含所有角色的字典
    all_characters = set(char_dmg_df[~char_dmg_df["is_anomaly"]]["name"]).union(
        set(char_element_df["name"])
    )

    # 初始化角色伤害数据
    attribution_data: dict[str, str] = {
        name: {"direct_damage": 0, "anomaly_damage": 0} for name in all_characters
    }

    # 处理只打出直伤的角色
    for _, row in char_dmg_df.iterrows():
        name = row["name"]
        is_anomaly = row["is_anomaly"]
        direct_damage = row["dmg_expect_sum"]

        # 更新角色的直接伤害
        if not is_anomaly:
            attribution_data[name]["direct_damage"] = direct_damage

    # 分配异常伤害到角色
    for _, row in char_element_df.iterrows():
        name = row["name"]
        element_type = row["element_type"]
        buildup_sum = row["buildup_sum"]
        anomaly_name = ANOMALY_MAPPING[element_type]
        total_anomaly_damage = anomaly_damage_totals[anomaly_name]

        # 计算角色的异常伤害归因
        if total_anomaly_damage > 0:
            anomaly_damage_attribution = (
                buildup_sum
                / char_element_df[char_element_df["element_type"] == element_type][
                    "buildup_sum"
                ].sum()
            ) * total_anomaly_damage
        else:
            anomaly_damage_attribution = 0

        # 更新角色的异常伤害
        attribution_data[name]["anomaly_damage"] += anomaly_damage_attribution

    # 处理极性紊乱和异放
    for anomaly_name in ["极性紊乱", "异放"]:
        total_anomaly_damage = anomaly_damage_totals.get(anomaly_name, 0)
        if total_anomaly_damage > 0:
            if anomaly_name == "极性紊乱":
                for key in attribution_data:
                    if key == "柳":
                        attribution_data[key]["anomaly_damage"] += total_anomaly_damage
            if anomaly_name == "异放":
                for key in attribution_data:
                    if key == "薇薇安":
                        attribution_data[key]["anomaly_damage"] += total_anomaly_damage

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(attribution_data, f, ensure_ascii=False, indent=4)


def prepare_dmg_data_and_cache(rid: int | str) -> dict[str, pd.DataFrame] | None:
    """准备并缓存伤害分析所需的数据。

    Args:
        rid (int): 运行ID。

    Returns:
        Optional[dict[str, pd.DataFrame]]: 包含预处理后的数据的字典，
        如果没有数据则返回None。
    """
    dmg_result_df = _load_dmg_data(rid)
    if dmg_result_df is None:
        return None
    uuid_df = sort_df_by_UUID(dmg_result_df)
    char_chart_data = prepare_char_chart_data(uuid_df)
    # st.write(char_chart_data)
    calculate_and_save_anomaly_attribution(
        rid, char_chart_data["char_dmg_df"], char_chart_data["char_element_df"]
    )
    return {
        "dmg_result_df": dmg_result_df,
        "char_dmg_df": char_chart_data["char_dmg_df"],
        "uuid_df": uuid_df,
        "char_chart_data": char_chart_data,
    }


def show_dmg_result(rid: int | str) -> None:
    """处理并显示指定运行ID的伤害分析结果。

    Args:
        rid (int): 运行ID。
    """
    prepared_data_dict = prepare_dmg_data_and_cache(rid)
    uuid_df = prepared_data_dict["uuid_df"]
    char_chart_data = prepared_data_dict["char_chart_data"]
    dmg_result_df = prepared_data_dict["dmg_result_df"]
    
    if dmg_result_df is None:
        return

    with st.expander("原始数据："):
        st.dataframe(dmg_result_df)
    
    with st.expander("按UUID排序后的数据："):
        st.dataframe(uuid_df)
    # 准备并绘制折线图
    line_chart_data = prepare_line_chart_data(dmg_result_df)
    draw_line_chart(line_chart_data)

    # 准备并绘制角色分布图
    draw_char_chart(char_chart_data)

    # 准备并绘制时间线图
    timeline_data = prepare_timeline_data(dmg_result_df)
    draw_char_timeline(timeline_data)
