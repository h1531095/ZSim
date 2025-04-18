import json
import subprocess
import sys
import threading
import time
from queue import Empty, Queue

import streamlit as st

if "sim_process" not in st.session_state:
    st.session_state.sim_process = None
if "output" not in st.session_state:
    st.session_state.output = []

output_queue = Queue()


def enqueue_output(pipe, queue):
    for line in iter(pipe.readline, ""):
        queue.put(line)
    pipe.close()


def star_simulator(stop_tick):
    if st.session_state.sim_process is None:
        command = [sys.executable, "zsim/main.py", "--stop_tick", str(stop_tick)]
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
        st.session_state.sim_process = proc
        threading.Thread(
            target=enqueue_output, args=(proc.stdout, output_queue), daemon=True
        ).start()


def reset_simulator():
    if st.session_state.sim_process is not None:
        st.session_state.sim_process.terminate()
        # Optionally wait for the process to terminate
        try:
            st.session_state.sim_process.wait(timeout=1)  # Wait for 1 second
        except subprocess.TimeoutExpired:
            # Force kill if terminate doesn't work quickly
            st.session_state.sim_process.kill()
            st.session_state.sim_process.wait()  # Wait for kill to complete
        except Exception as e:
            st.error(f"Error terminating process: {e}")  # Log potential errors
        finally:
            st.session_state.sim_process = None

        st.session_state.output = []
        # Clear the queue more robustly
        while not output_queue.empty():
            try:
                output_queue.get_nowait()
            except Empty:
                break
        # Force a rerun to update the UI state immediately

        st.rerun()


def page_simulator():
    st.title("ZZZ Simulator - 模拟器")
    from define import CONFIG_PATH

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
        default_stop_tick = config["stop_tick"]
    stop_tick = st.number_input(
        "模拟时长（帧数，1秒=60帧）",
        min_value=1,
        max_value=65535,
        value=default_stop_tick,
        key="stop_tick",
    )
    col1, col2 = st.columns(2)
    with col1:
        if not st.button("开始模拟"):
            st.stop()
    with col2:
        if st.button("重置模拟器"):
            reset_simulator()

    st.write(f"开始模拟，时长: {stop_tick} ticks")
    output_placeholder = st.empty()

    with st.spinner("正在模拟中，这可能会持续数分钟，请稍候..."):
        star_simulator(stop_tick)
        while (
            st.session_state.sim_process and st.session_state.sim_process.poll() is None
        ):
            try:
                line = output_queue.get_nowait()
                st.session_state.output.append(line)
            except Empty:
                pass

            if st.session_state.output:
                output_placeholder.code("\n".join(st.session_state.output[-20:]))

            # time.sleep(0.1)

    if st.session_state.output:
        output_placeholder.code("\n".join(st.session_state.output[-20:]))

    with open(CONFIG_PATH, "r+", encoding="utf-8") as f:
        config = json.load(f)
        config["stop_tick"] = stop_tick
        f.seek(0)
        json.dump(config, f, indent=4)
        f.truncate()


page_simulator()
