import streamlit as st

# 页面导航
PAGES = {
    "功能选择": [
        st.Page("page_character_config.py", title="角色配置"),
        st.Page("page_simulator.py", title="模拟器"),
        st.Page("page_data_analysis.py", title="数据分析"),
        st.Page("page_apl_editor.py", title="APL编辑器"),
    ]
}


def main():
    st.set_page_config(layout="wide")
    pg = st.navigation(PAGES, expanded=True)
    pg.run()


if __name__ == "__main__":
    main()
