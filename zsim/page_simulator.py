import json
import concurrent.futures
from run import go_subprocess

import streamlit as st


def page_simulator():
    st.title("ZZZ Simulator - 模拟器")
    from define import CONFIG_PATH

    MAX_WORKERS = 4

    @st.cache_resource
    def get_executor():
        return concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
        default_stop_tick = config["stop_tick"]

    @st.fragment
    def go_simulator():
        """启动模拟器"""
        # 初始化状态
        if "simulation_running" not in st.session_state:
            st.session_state["simulation_running"] = False

        stop_tick = st.number_input(
            "模拟时长（帧数，1秒=60帧）",
            min_value=1,
            max_value=65535,
            value=default_stop_tick,
            key="stop_tick",
            disabled=st.session_state["simulation_running"],
        )

        with open(CONFIG_PATH, "r+", encoding="utf-8") as f:
            config = json.load(f)
            config["stop_tick"] = stop_tick
            f.seek(0)
            json.dump(config, f, indent=4)
            f.truncate()

        # 启动模拟后自锁
        col1, col2 = st.columns(2)
        with col1:
            if (
                st.button("开始模拟", disabled=st.session_state["simulation_running"], type="primary")
                and not st.session_state["simulation_running"]
            ):
                st.session_state["simulation_running"] = True
                st.rerun(scope="fragment")
            elif not st.session_state["simulation_running"]:
                st.stop()
        with st.spinner("正在模拟中，这可能会持续数分钟，请稍候...", show_time=True):
            future = get_executor().submit(go_subprocess, stop_tick)
            result = future.result()
            st.text_area("模拟结果", result, height=400)
            st.session_state["simulation_running"] = False

        with col2:
            if st.button("重置模拟器", type="primary"):
                st.rerun(scope="fragment")

    go_simulator()


page_simulator()
