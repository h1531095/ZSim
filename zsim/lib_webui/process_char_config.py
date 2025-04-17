import streamlit as st
from define import saved_char_config
from sim_progress import character_factory


def display_character_panels(name_box: list[str]) -> None:
    all_char_configs = [
        saved_char_config.get(name) for name in name_box if name in saved_char_config
    ]
    characters = []
    for config in all_char_configs:
        if config:
            character = character_factory(**config)
            characters.append(character)
    st.subheader("角色局外面板")
    cols = st.columns(len(characters))
    for i, character in enumerate(characters):
        with cols[i]:
            with st.expander(character.NAME, expanded=False):
                statement = character.statement.statement
                col_left, col_right = st.columns(2)
                with col_left:
                    st.markdown(
                        f"<div style='border: 1px solid #262730; border-radius: 5px; padding: 5px; margin-bottom: 5px; display: flex; justify-content: space-between;'>攻击力: <span style='text-align: right'>{statement.get('ATK', 0):.2f}</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='border: 1px solid #262730; border-radius: 5px; padding: 5px; margin-bottom: 5px; display: flex; justify-content: space-between;'>暴击率: <span style='text-align: right'>{statement.get('CRIT_rate', 0):.2%}</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='border: 1px solid #262730; border-radius: 5px; padding: 5px; margin-bottom: 5px; display: flex; justify-content: space-between;'>暴击伤害: <span style='text-align: right'>{statement.get('CRIT_damage', 0):.2%}</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='border: 1px solid #262730; border-radius: 5px; padding: 5px; margin-bottom: 5px; display: flex; justify-content: space-between;'>生命值: <span style='text-align: right'>{statement.get('HP', 0):.2f}</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='border: 1px solid #262730; border-radius: 5px; padding: 5px; margin-bottom: 5px; display: flex; justify-content: space-between;'>防御力: <span style='text-align: right'>{statement.get('DEF', 0):.2f}</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='border: 1px solid #262730; border-radius: 5px; padding: 5px; margin-bottom: 5px; display: flex; justify-content: space-between;'>穿透率: <span style='text-align: right'>{statement.get('PEN_ratio', 0):.2%}</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='border: 1px solid #262730; border-radius: 5px; padding: 5px; margin-bottom: 5px; display: flex; justify-content: space-between;'>穿透值: <span style='text-align: right'>{statement.get('PEN_numeric', 0):.2f}</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='border: 1px solid #262730; border-radius: 5px; padding: 5px; margin-bottom: 5px; display: flex; justify-content: space-between;'>能量自动回复: <span style='text-align: right'>{statement.get('sp_regen', 0):.2f}</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='border: 1px solid #262730; border-radius: 5px; padding: 5px; margin-bottom: 5px; display: flex; justify-content: space-between;'>冲击力: <span style='text-align: right'>{statement.get('IMP', 0):.2f}</span></div>",
                        unsafe_allow_html=True,
                    )
                with col_right:
                    st.markdown(
                        f"<div style='border: 1px solid #262730; border-radius: 5px; padding: 5px; margin-bottom: 5px; display: flex; justify-content: space-between;'>冰属性伤害: <span style='text-align: right'>{statement.get('ICE_DMG_bonus', 0):.2%}</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='border: 1px solid #262730; border-radius: 5px; padding: 5px; margin-bottom: 5px; display: flex; justify-content: space-between;'>火属性伤害: <span style='text-align: right'>{statement.get('FIRE_DMG_bonus', 0):.2%}</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='border: 1px solid #262730; border-radius: 5px; padding: 5px; margin-bottom: 5px; display: flex; justify-content: space-between;'>物理属性伤害: <span style='text-align: right'>{statement.get('PHY_DMG_bonus', 0):.2%}</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='border: 1px solid #262730; border-radius: 5px; padding: 5px; margin-bottom: 5px; display: flex; justify-content: space-between;'>以太属性伤害: <span style='text-align: right'>{statement.get('ETHER_DMG_bonus', 0):.2%}</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='border: 1px solid #262730; border-radius: 5px; padding: 5px; margin-bottom: 5px; display: flex; justify-content: space-between;'>电属性伤害: <span style='text-align: right'>{statement.get('ELECTRIC_DMG_bonus', 0):.2%}</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='border: 1px solid #262730; border-radius: 5px; padding: 5px; margin-bottom: 5px; display: flex; justify-content: space-between;'>异常精通: <span style='text-align: right'>{statement.get('AP', 0):.2f}</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div style='border: 1px solid #262730; border-radius: 5px; padding: 5px; margin-bottom: 5px; display: flex; justify-content: space-between;'>异常掌控: <span style='text-align: right'>{statement.get('AM', 0):.2f}</span></div>",
                        unsafe_allow_html=True,
                    )
