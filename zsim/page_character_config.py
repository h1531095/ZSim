import streamlit as st
import toml


def page_character_config():
    st.title("ZZZ Simulator - 角色配置")
    from zsim.define import saved_char_config
    from zsim.lib_webui.constants import default_chars

    if "name_box" in saved_char_config:
        default_chars = saved_char_config["name_box"]
    from zsim.lib_webui.constants import (
        char_options,
        equip_set2_options,
        equip_set4_options,
        weapon_options,
        weapon_profession_map,
        char_profession_map,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        name_box_0 = [
            st.selectbox(
                "角色1",
                char_options,
                index=char_options.index(default_chars[0])
                if len(default_chars) > 0
                else 0,
                key="char_select_0",
            )
        ]
    with col2:
        name_box_1 = [
            st.selectbox(
                "角色2",
                char_options,
                index=char_options.index(default_chars[1])
                if len(default_chars) > 1
                else 0,
                key="char_select_1",
            )
        ]
    with col3:
        name_box_2 = [
            st.selectbox(
                "角色3",
                char_options,
                index=char_options.index(default_chars[2])
                if len(default_chars) > 2
                else 0,
                key="char_select_2",
            )
        ]
    name_box = name_box_0 + name_box_1 + name_box_2
    if len(name_box) != 3:
        st.stop()
    if len(name_box) != len(set(name_box)):
        st.error("请选择三个不同的角色")
        st.stop()
    for name in name_box:
        with st.expander(f"{name}的配置"):
            col_weapon, col_level, col_cinema = st.columns(3)
            with col_weapon:
                show_adapted_weapon = st.session_state.get(
                    f"{name}_show_adapted_weapon", True
                )
                char_profession = char_profession_map.get(name)
                if show_adapted_weapon and char_profession:
                    filtered_weapon_options = [
                        w
                        for w in weapon_options
                        if weapon_profession_map.get(w) == char_profession
                    ]
                else:
                    filtered_weapon_options = list(weapon_options)
                if name in saved_char_config:
                    current_weapon = saved_char_config[name].get("weapon")
                else:
                    current_weapon = None
                # 如果当前音擎不在可选列表，或未设置，则默认选第一个
                if not filtered_weapon_options:
                    st.selectbox(
                        "音擎",
                        [],
                        key=f"{name}_weapon",
                    )
                else:
                    if current_weapon not in filtered_weapon_options:
                        current_weapon = filtered_weapon_options[0]
                    st.selectbox(
                        "音擎",
                        filtered_weapon_options,
                        index=filtered_weapon_options.index(current_weapon),
                        key=f"{name}_weapon",
                    )
                show_adapted_weapon = st.checkbox(
                    "只显示适配音擎",
                    value=show_adapted_weapon,
                    key=f"{name}_show_adapted_weapon",
                )
            with col_level:
                st.number_input(
                    "音擎精炼等级",
                    min_value=1,
                    max_value=5,
                    value=saved_char_config[name].get("weapon_level", 1)
                    if name in saved_char_config
                    else 1,
                    key=f"{name}_weapon_level",
                )
            with col_cinema:
                st.number_input(
                    "影画等级",
                    min_value=0,
                    max_value=6,
                    value=saved_char_config[name].get("cinema", 0)
                    if name in saved_char_config
                    else 0,
                    key=f"{name}_cinema_level",
                )
            equip_style = st.radio(
                "驱动盘搭配方式",
                ["4+2", "2+2+2"],
                index=0
                if name not in saved_char_config
                or "equip_style" not in saved_char_config[name]
                else (0 if saved_char_config[name]["equip_style"] == "4+2" else 1),
                key=f"{name}_equip_style",
            )
            col1, col2 = st.columns(2)
            with col1:
                if equip_style == "4+2":
                    st.selectbox(
                        "四件套",
                        equip_set4_options,
                        index=equip_set4_options.index(
                            saved_char_config[name]["equip_set4"]
                        )
                        if name in saved_char_config
                        and "equip_set4" in saved_char_config[name]
                        else 0,
                        key=f"{name}_equip_set4",
                    )
                    st.selectbox(
                        "二件套",
                        equip_set2_options,
                        index=equip_set2_options.index(
                            saved_char_config[name].get("equip_set2_a", "啄木鸟电音")
                        )
                        if name in saved_char_config
                        else 0,
                        key=f"{name}_equip_set2",
                    )
                else:
                    st.selectbox(
                        "二件套A",
                        equip_set2_options,
                        index=equip_set2_options.index(
                            saved_char_config[name].get("equip_set2_a", "啄木鸟电音")
                        )
                        if name in saved_char_config
                        else 0,
                        key=f"{name}_equip_set2A",
                    )
                    st.selectbox(
                        "二件套B",
                        equip_set2_options,
                        index=equip_set2_options.index(
                            saved_char_config[name].get("equip_set2_b", "啄木鸟电音")
                        )
                        if name in saved_char_config
                        and "equip_set2_b" in saved_char_config[name]
                        else 0,
                        key=f"{name}_equip_set2B",
                    )
                    st.selectbox(
                        "二件套C",
                        equip_set2_options,
                        index=equip_set2_options.index(
                            saved_char_config[name].get("equip_set2_c", "啄木鸟电音")
                        )
                        if name in saved_char_config
                        and "equip_set2_c" in saved_char_config[name]
                        else 0,
                        key=f"{name}_equip_set2C",
                    )
            with col2:
                from zsim.lib_webui.constants import (
                    main_stat4_options,
                    main_stat5_options,
                    main_stat6_options,
                )

                st.selectbox(
                    "四号位主词条",
                    main_stat4_options,
                    index=main_stat4_options.index(
                        saved_char_config[name].get("drive4", "攻击力%")
                    )
                    if name in saved_char_config
                    else 0,
                    key=f"{name}_main_stat4",
                )
                st.selectbox(
                    "五号位主词条",
                    main_stat5_options,
                    index=main_stat5_options.index(
                        saved_char_config[name].get("drive5", "攻击力%")
                    )
                    if name in saved_char_config
                    else 0,
                    key=f"{name}_main_stat5",
                )
                st.selectbox(
                    "六号位主词条",
                    main_stat6_options,
                    index=main_stat6_options.index(
                        saved_char_config[name].get("drive6 ", "攻击力%")
                    )
                    if name in saved_char_config
                    else 0,
                    key=f"{name}_main_stat6",
                )
            from zsim.lib_webui.constants import sc_max_value

            st.text("副词条数量：")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.number_input(
                    "攻击力%",
                    min_value=0,
                    max_value=sc_max_value,
                    value=saved_char_config[name].get("scATK_percent", 0)
                    if name in saved_char_config
                    else 0,
                    key=f"{name}_scATK_percent",
                )
                st.number_input(
                    "攻击力",
                    min_value=0,
                    max_value=sc_max_value,
                    value=saved_char_config[name].get("scATK", 0)
                    if name in saved_char_config
                    else 0,
                    key=f"{name}_scATK",
                )
            with col2:
                st.number_input(
                    "生命值%",
                    min_value=0,
                    max_value=sc_max_value,
                    value=saved_char_config[name].get("scHP_percent", 0)
                    if name in saved_char_config
                    else 0,
                    key=f"{name}_scHP_percent",
                )
                st.number_input(
                    "生命值",
                    min_value=0,
                    max_value=sc_max_value,
                    value=saved_char_config[name].get("scHP", 0)
                    if name in saved_char_config
                    else 0,
                    key=f"{name}_scHP",
                )
            with col3:
                st.number_input(
                    "防御力%",
                    min_value=0,
                    max_value=sc_max_value,
                    value=saved_char_config[name].get("scDEF_percent", 0)
                    if name in saved_char_config
                    else 0,
                    key=f"{name}_scDEF_percent",
                )
                st.number_input(
                    "防御力",
                    min_value=0,
                    max_value=sc_max_value,
                    value=saved_char_config[name].get("scDEF", 0)
                    if name in saved_char_config
                    else 0,
                    key=f"{name}_scDEF",
                )
            with col4:
                st.number_input(
                    "暴击率",
                    min_value=0,
                    max_value=sc_max_value,
                    value=saved_char_config[name].get("scCRIT", 0)
                    if name in saved_char_config
                    else 0,
                    key=f"{name}_scCRIT",
                )
                st.number_input(
                    "暴击伤害",
                    min_value=0,
                    max_value=sc_max_value,
                    value=saved_char_config[name].get("scCRIT_DMG", 0)
                    if name in saved_char_config
                    else 0,
                    key=f"{name}_scCRIT_DMG",
                )
            with col5:
                st.number_input(
                    "异常精通",
                    min_value=0,
                    max_value=sc_max_value,
                    value=saved_char_config[name].get("scAnomalyProficiency", 0)
                    if name in saved_char_config
                    else 0,
                    key=f"{name}_scAnomalyProficiency",
                )
                st.number_input(
                    "穿透值",
                    min_value=0,
                    max_value=sc_max_value,
                    value=saved_char_config[name].get("scPEN", 0)
                    if name in saved_char_config
                    else 0,
                    key=f"{name}_scPEN",
                )
            col1, col2 = st.columns(2)
            with col1:
                if name not in saved_char_config:
                    saved_char_config[name] = {}
                crit_balancing: bool = st.checkbox(
                    "使用暴击配平算法",
                    value=saved_char_config[name].get("crit_balancing", False),
                    key=f"{name}_crit_balancing",
                )
                if st.session_state.get(f"{name}_crit_rate_limit") is None:
                    st.session_state[f"{name}_crit_rate_limit"] = saved_char_config[
                        name
                    ].get("crit_rate_limit", 0.95)
                if crit_balancing:
                    st.number_input(
                        "暴击率上限",
                        min_value=0.0,
                        max_value=1.0,
                        value=st.session_state[f"{name}_crit_rate_limit"],
                        key=f"{name}_crit_rate_limit",
                        help="配平算法会将角色局外面板的暴击率限制在此值以下，适用于会吃到暴击率buff的情况，以防止溢出",
                    )
        char_config = {
            "name": name,
            "weapon": st.session_state[f"{name}_weapon"],
            "weapon_level": st.session_state[f"{name}_weapon_level"],
            "cinema": st.session_state[f"{name}_cinema_level"],
            "crit_balancing": st.session_state[f"{name}_crit_balancing"],
            "crit_rate_limit": st.session_state[f"{name}_crit_rate_limit"],
            "scATK_percent": st.session_state[f"{name}_scATK_percent"],
            "scATK": st.session_state[f"{name}_scATK"],
            "scHP_percent": st.session_state[f"{name}_scHP_percent"],
            "scHP": st.session_state[f"{name}_scHP"],
            "scDEF_percent": st.session_state[f"{name}_scDEF_percent"],
            "scDEF": st.session_state[f"{name}_scDEF"],
            "scAnomalyProficiency": st.session_state[f"{name}_scAnomalyProficiency"],
            "scPEN": st.session_state[f"{name}_scPEN"],
            "scCRIT": st.session_state[f"{name}_scCRIT"],
            "scCRIT_DMG": st.session_state[f"{name}_scCRIT_DMG"],
            "drive4": st.session_state[f"{name}_main_stat4"],
            "drive5": st.session_state[f"{name}_main_stat5"],
            "drive6": st.session_state[f"{name}_main_stat6"],
            "equip_style": st.session_state[f"{name}_equip_style"],
        }
        if st.session_state[f"{name}_equip_style"] == "4+2":
            char_config["equip_set4"] = st.session_state[f"{name}_equip_set4"]
            char_config["equip_set2_a"] = st.session_state[f"{name}_equip_set2"]
        else:
            char_config["equip_set2_a"] = st.session_state[f"{name}_equip_set2A"]
            char_config["equip_set2_b"] = st.session_state[f"{name}_equip_set2B"]
            char_config["equip_set2_c"] = st.session_state[f"{name}_equip_set2C"]
        st.session_state[f"{name}_config"] = char_config
    if not st.button("提交并保存角色配置"):
        st.stop()
    _config_to_save = {"name_box": name_box}
    for name in name_box:
        _config_to_save[name] = st.session_state[f"{name}_config"]
    saved_char_config.update(_config_to_save)
    from zsim.define import CHAR_CONFIG_FILE

    with open(CHAR_CONFIG_FILE, "w", encoding="utf-8") as f:
        toml.dump(saved_char_config, f)
    from zsim.lib_webui.process_char_config import display_character_panels

    display_character_panels(name_box)


page_character_config()
