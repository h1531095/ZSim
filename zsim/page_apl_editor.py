import streamlit as st


def page_apl_editor():
    st.title("ZZZ Simulator - APL编辑器")
    from lib_webui.process_apl_editor import listed_alp_options

    listed_alp_options()


page_apl_editor()
