import streamlit as st
from lib_webui.clean_results_cache import delete_result, get_all_results, rename_result
from lib_webui.constants import IDDuplicateError


def page_data_analysis():
    st.title("ZZZ Simulator - 数据分析")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        id_cache = get_all_results()
        options = list(id_cache.keys())[::-1]
        selected_key = st.selectbox("选择你要查看的结果", options)
    with col2:
        st.markdown("备注信息")
        st.markdown(
            f'<span style="color:gray;">{id_cache[selected_key] if id_cache else None}</span>',
            unsafe_allow_html=True,
        )
    with col3:

        @st.dialog("重命名结果")
        def rename_dialog():
            new_name = st.text_input("请输入新的ID", value=selected_key)
            new_comment = st.text_input(
                "请输入新的备注信息", value=id_cache[selected_key] if id_cache else None
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("保存", key="save_rename", use_container_width=True):
                    try:
                        rename_result(selected_key, new_name or "", new_comment or "")
                        st.rerun()
                    except FileNotFoundError:
                        st.warning("请检查文件是否存在或ID是否正确。", icon="⚠️")
                    except IDDuplicateError as e:
                        st.warning(e, icon="⚠️")
            with col2:
                if st.button("取消", key="cancel_rename", use_container_width=True):
                    st.rerun()

        if st.button("重命名", use_container_width=True):
            rename_dialog()
    with col4:

        @st.dialog("删除结果")
        def delete_dialog():
            st.warning(f"你确定要删除 {selected_key} 吗？", icon="⚠️")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    "确定", key="confirm_del_result", use_container_width=True
                ):
                    delete_result(selected_key)
                    st.rerun()
            with col2:
                if st.button("取消", key="cancel", use_container_width=True):
                    st.rerun()

        if st.button("删除", use_container_width=True):
            delete_dialog()

    if not st.toggle("开启数据分析"):
        st.stop()
    from lib_webui.process_dmg_result import process_dmg_result

    process_dmg_result(selected_key)

    from lib_webui.process_buff_result import process_buff_result

    process_buff_result(selected_key)


page_data_analysis()
