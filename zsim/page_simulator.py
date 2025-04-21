import concurrent.futures
import json
import uuid  # 导入 uuid 模块
import os

import psutil
import streamlit as st
from lib_webui.constants import stats_trans_mapping
from run import MainArgs, go_parallel_subprocess, go_single_subprocess


def page_simulator():
    st.title("ZZZ Simulator - 模拟器")
    from define import CONFIG_PATH

    # 获取当前计算机的物理核心数量
    MAX_WORKERS = psutil.cpu_count(logical=False)

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
        st.write(
            '<div title="单位为 tick（帧），1秒 = 60 ticks">模拟时长（tick）:</div>',
            unsafe_allow_html=True,
        )
        st.write("")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            stop_tick = st.number_input(
                "模拟时长",
                min_value=1,
                max_value=65535,
                value=default_stop_tick,
                key="stop_tick",
                help="单位为 tick（帧），1秒 = 60 ticks",
                disabled=st.session_state["simulation_running"],
                label_visibility="collapsed",
            )
            if stop_tick != default_stop_tick:
                with open(CONFIG_PATH, "r+", encoding="utf-8") as f:
                    config = json.load(f)
                    config["stop_tick"] = stop_tick
                    f.seek(0)
                    json.dump(config, f, indent=4)
                    f.truncate()
        with col2:
            st.button(
                "查看角色配置（未实装）",
                use_container_width=True,
                disabled=st.session_state["simulation_running"],
            )

        with col3:
            st.button(
                "APL选择（未实装）",
                use_container_width=True,
                disabled=st.session_state["simulation_running"],
            )

        with col4:

            @st.dialog("模拟器配置", width="large")
            def go_config():
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    parallel_cfg = config["parallel_mode"]
                default_mode = parallel_cfg["enabled"]
                # st.write(parallel_cfg)
                mode = st.radio(
                    "运行模式",
                    ["单进程", "多进程"],
                    index=default_mode,
                    horizontal=True,
                )
                if mode == "单进程":
                    st.write(
                        '<p style="color: gray;">单进程模式下，模拟器将进行单次模拟。角色配置、模拟时长、APL都有专门的配置项管理，你不需要对此模式进行进行额外配置</p>',
                        unsafe_allow_html=True,
                    )
                elif mode == "多进程":
                    st.write(
                        '<p style="color: gray;">多进程模式下，模拟器将按照一定规律执行多次模拟，最大可利用的核心数为你的物理核心数。</p>',
                        unsafe_allow_html=True,
                    )
                    # 调整角色的相对位置
                    default_adjust_char = int(parallel_cfg["adjust_char"])
                    adjust_char = st.radio(
                        "调整角色",
                        ["1号", "2号", "3号"],
                        index=default_adjust_char - 1,
                        help="以队伍配置中的顺序进行选择",
                        horizontal=True,
                    )
                    # 模拟功能
                    # TODO 添加额外功能后这里需要default_function
                    selected_func = st.radio(
                        "模拟功能",
                        [
                            "属性收益曲线",
                            "音擎伤害期望对比",
                            "驱动盘四件套对比",
                            "APL对比",
                            "单次失衡爆发对比",
                            "失衡效率对比",
                            "异常积蓄效率对比",
                        ],
                        help="选择模拟功能",
                        horizontal=True,
                    )
                    if selected_func == "属性收益曲线":
                        st.write(
                            '<p style="color: gray;">将指定种类的属性按照单个副词条的模型量进行步进增加，分别计算伤害期望</p>',
                            unsafe_allow_html=True,
                        )
                        # 模拟范围
                        default_sc_range = parallel_cfg["adjust_sc"]["sc_range"]
                        sc_range: tuple[int] = st.slider(
                            "模拟词条数范围",
                            min_value=0,
                            max_value=50,
                            value=default_sc_range,
                            step=1,
                        )
                        col_sc_select = st.columns([2, 1])
                        with col_sc_select[0]:
                            # 模拟词条种类
                            default_sc_list = parallel_cfg["adjust_sc"]["sc_list"]
                            sc_list = st.multiselect(
                                "模拟词条种类",
                                stats_trans_mapping.keys(),
                                default=default_sc_list,
                                help="选择要模拟的词条种类",
                            )
                            st.write(
                                '<p style="color: gray;">右侧选择框的解释：</br>勾选：避免稀释或转模产生影响；</br>不勾选：避免异常/直伤占比变化产生影响；</br>你做不到两全其美</br>一般来说，异常角色带精通主词条就去掉掌控的勾，反之亦然</p>',
                                unsafe_allow_html=True,
                            )
                        with col_sc_select[1]:
                            # 控制对应词条是否需要移除其他主副词条
                            st.write(
                                '<p style="color: gray;">清除主副词条开关：</p>',
                                unsafe_allow_html=True,
                            )
                            tmp_dict = {}
                            for sc in sc_list:
                                tmp_dict[sc] = st.checkbox(
                                    f"{sc}",
                                    value=True if sc != "异常掌控" else False,
                                    help="勾选后，将在模拟时移除主副词条，不适用于移除装备后会导致词条本身影响输出占比产生变化的情况，一般情况下，你只需要关注异常角色的异常掌控/异常精通",
                                )
                            remove_equip_list = list(
                                key for key, value in tmp_dict.items() if value
                            )
                    else:
                        st.error("此功能暂未实现")

                if st.button("保存配置"):
                    mode_bool = True if mode == "多进程" else False
                    with open(CONFIG_PATH, "r+", encoding="utf-8") as f:
                        config = json.load(f)
                        config["parallel_mode"]["enabled"] = mode_bool
                        config["parallel_mode"]["adjust_char"] = int(
                            adjust_char.split("号")[0]
                        )
                        if selected_func == "属性收益曲线":
                            config["parallel_mode"]["adjust_sc"] = {
                                "enabled": True,
                                "sc_range": sc_range,
                                "sc_list": sc_list,
                                "remove_equip_list": remove_equip_list,
                            }
                        else:
                            config["parallel_mode"]["adjust_sc"] = {
                                "enabled": False,
                                "sc_range": [0, 50],
                                "sc_list": [],
                            }
                        config["parallel_mode"]["adjust_weapon"] = {
                            "enabled": False,
                            "weapon_list": [],
                        }
                        f.seek(0)
                        json.dump(config, f, indent=4)
                        f.truncate()
                    st.rerun(scope="fragment")

            if st.button(
                "模拟器配置",
                use_container_width=True,
                disabled=st.session_state["simulation_running"],
            ):
                go_config()
        # 启动模拟后自锁
        col1, col2 = st.columns([8, 1])
        with col1:
            # 加载config
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
                parallel_cfg = config["parallel_mode"]
            if not parallel_cfg["enabled"]:
                # 单进程模式
                if (
                    st.button(
                        "开始模拟-单进程",
                        disabled=st.session_state["simulation_running"],
                        type="primary",
                    )
                    and not st.session_state["simulation_running"]
                ):
                    st.session_state["simulation_running"] = True
                    st.rerun(scope="fragment")
                elif not st.session_state["simulation_running"]:
                    st.stop()
                with st.spinner(
                    "单进程模拟中，这可能会持续数十秒，请稍候...", show_time=True
                ):
                    future = get_executor().submit(go_single_subprocess, stop_tick)
                    result = future.result()
                    st.text_area(
                        "模拟完成，请前往数据分析查看结果，进程输出：",
                        result,
                        height=400,
                    )
                    st.session_state["simulation_running"] = False
            elif parallel_cfg["enabled"]:
                # 多进程模式
                st.write(
                    f"多进程模式：模拟{parallel_cfg['adjust_sc']['enabled'] and '属性收益曲线' or '未选择功能'}"
                )
                if st.button(
                    "开始模拟-多进程",
                    disabled=st.session_state["simulation_running"],
                    type="primary",
                ):
                    st.session_state["simulation_running"] = True
                    st.rerun(scope="fragment")
                elif not st.session_state["simulation_running"]:
                    st.stop()
                with st.spinner(
                    "多进程模拟中，这可能会持续数十秒，请稍候...", show_time=True
                ):
                    # 每个进程的参数
                    args_list = []
                    run_turn_uuid = str(uuid.uuid4())  # 为本轮并行运行生成统一的UUID
                    result_dir = "./results/" + run_turn_uuid + "/.parallel_config.json"
                    os.makedirs(
                        os.path.dirname(result_dir), exist_ok=True
                    )  # 创建结果文件夹
                    # 将配置存入文件
                    with open(result_dir, "w", encoding="utf-8") as f:
                        json.dump(parallel_cfg, f, indent=4)

                    adjust_sc_cfg = parallel_cfg["adjust_sc"]
                    sc_list = adjust_sc_cfg["sc_list"]
                    sc_range_start, sc_range_end = adjust_sc_cfg["sc_range"]
                    remove_equip_list = adjust_sc_cfg.get(
                        "remove_equip_list", []
                    )  # 获取需要移除装备的词条列表，如果不存在则为空列表
                    for sc_name in sc_list:
                        for sc_value in range(sc_range_start, sc_range_end + 1):
                            args = MainArgs()
                            args.stop_tick = stop_tick
                            args.mode = "parallel"
                            args.adjust_char = parallel_cfg[
                                "adjust_char"
                            ]  # 添加调整角色参数
                            args.sc_name = stats_trans_mapping[sc_name]
                            args.sc_value = sc_value
                            args.run_turn_uuid = run_turn_uuid  # 设置统一的UUID
                            # 检查当前 sc_name 是否在 remove_equip_list 中
                            if sc_name in remove_equip_list:
                                args.remove_equip = True
                            else:
                                args.remove_equip = False  # 默认不移除装备

                            args_list.append(args)

                    # 启动多进程
                    futures = [
                        get_executor().submit(go_parallel_subprocess, args)
                        for args in args_list
                    ]
                    # TODO: 处理 futures 的结果，例如显示进度或汇总结果
                    results = [
                        future.result()
                        for future in concurrent.futures.as_completed(futures)
                    ]
                    st.write("模拟完成，请前往数据分析查看结果")
                    # del results
                    # 循环显示每个进程的输出结果
                    for i, result in enumerate(results, 1):
                        with st.expander(f"进程 {i} 输出结果"):
                            st.text_area(
                                f"进程 {i} 输出结果:",
                                result,
                                height=400,
                                label_visibility="collapsed",
                            )
                    st.session_state["simulation_running"] = False

        with col2:
            if st.button("重置模拟器", type="primary", use_container_width=True):
                st.rerun(scope="fragment")

    go_simulator()


page_simulator()
