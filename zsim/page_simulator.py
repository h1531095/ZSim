import streamlit as st
import timeit
import gc
import json
from sim_progress import Report
from sim_progress.Report import write_to_csv
from simulator.main_loop import main_loop

def page_simulator():
    st.title("ZZZ Simulator - 模拟器")
    from define import CONFIG_PATH
    with open(CONFIG_PATH, "r", encoding='utf-8') as f:
        config = json.load(f)
        default_stop_tick = config["stop_tick"]
    stop_tick = st.number_input("模拟时长（帧数，1秒=60帧）", min_value=1, max_value=65535, value=default_stop_tick, key="stop_tick")
    if not st.button("开始模拟"):
        st.stop()
    st.write(f"开始模拟，时长: {stop_tick} ticks")
    with st.spinner('正在模拟中，请稍候...'):
        elapsed_time = timeit.timeit(lambda: main_loop(stop_tick), number=1)
    with st.spinner('正在等待IO结束...', show_time = True):
        write_to_csv()
        Report.log_queue.join()
        Report.result_queue.join()
        gc.collect()
    st.success(f"模拟完成！耗时: {elapsed_time:.2f}秒，请前往数据分析查看结果。")
    st.error("注意，目前程序无法保证第二次模拟的准确性，请刷新网页再尝试")
    with open(CONFIG_PATH, "r+", encoding='utf-8') as f:
        config = json.load(f)
        config["stop_tick"] = stop_tick
        f.seek(0)
        json.dump(config, f, indent=4)
        f.truncate()
        
page_simulator()