import streamlit as st
import polars as pl
from lib_webui.constants import CHAR_CID_MAPPING

# 显示角色与CID对应表
def show_char_cid_mapping():
    st.markdown("### 附：角色与CID对应表")
    st.caption("角色与CID的对应关系仅与本模拟器内部功能有关")
    st.dataframe(pl.DataFrame(CHAR_CID_MAPPING))
    
show_char_cid_mapping()