import streamlit as st

def page_apl_editor():
    st.title("ZZZ Simulator - APL编辑器")
    st.write("这是APL编辑器页面，您可以在这里编辑APL相关设置。")
    from lib_webui.process_apl_editor import process_apl_editor
    process_apl_editor()
    
page_apl_editor()