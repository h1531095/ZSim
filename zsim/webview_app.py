import webview
import subprocess
import sys
import threading
import time
import signal
import os
import socket
from typing import Optional

streamlit_process: Optional[subprocess.Popen[bytes]] = None
streamlit_port: int = 8501  # 默认端口


def find_available_port(start_port: int = 8501) -> int:
    """查找一个可用的网络端口。

    Args:
        start_port: 开始搜索的端口号。

    Returns:
        一个可用的端口号。

    Raises:
        RuntimeError: 如果在合理范围内找不到可用端口。
    """
    port = start_port
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
                print(f"找到可用端口: {port}")
                return port
            except OSError:
                print(f"端口 {port} 已被占用，尝试下一个...")
                port += 1
    raise RuntimeError("找不到可用的端口来启动 Streamlit")


def start_streamlit() -> None:
    """在后台启动 Streamlit 服务。"""
    global streamlit_process, streamlit_port
    try:
        # 查找可用端口
        streamlit_port = find_available_port()

        # 使用 Popen 启动 Streamlit，以便稍后可以终止它
        # 注意：根据操作系统和环境，可能需要调整命令
        # 使用 os.setsid 或 subprocess.CREATE_NEW_PROCESS_GROUP 来确保子进程独立
        preexec_fn = None
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            preexec_fn = os.setsid

        streamlit_command = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "zsim/webui.py",
            "--server.headless",
            "true",
            "--server.port",
            str(streamlit_port),
        ]

        streamlit_process = subprocess.Popen(
            streamlit_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=preexec_fn,
            creationflags=creationflags,
        )
        print(f"Streamlit 进程已在端口 {streamlit_port} 启动，PID: {streamlit_process.pid}")
        # 等待一段时间确保 Streamlit 启动
        time.sleep(5)
    except Exception as e:
        print(f"错误：启动 Streamlit 失败 - {e}")
        # 如果启动失败，尝试清理可能存在的进程
        stop_streamlit()
        sys.exit(1)


def stop_streamlit() -> None:
    """停止后台运行的 Streamlit 服务。"""
    global streamlit_process
    if streamlit_process and streamlit_process.poll() is None:
        print(f"正在尝试终止 Streamlit 进程 (PID: {streamlit_process.pid})...")
        try:
            if sys.platform == "win32":
                # 在 Windows 上，使用 CTRL_BREAK_EVENT 发送信号到整个进程组
                streamlit_process.send_signal(signal.CTRL_BREAK_EVENT)
                # 等待一段时间让进程响应信号
                time.sleep(2)
                # 如果进程仍然存在，强制终止
                if streamlit_process.poll() is None:
                    print("Streamlit 进程未响应信号，强制终止...")
                    streamlit_process.terminate()  # 尝试温和终止
                    time.sleep(1)
                    if streamlit_process.poll() is None:
                        streamlit_process.kill()  # 强制终止
            else:
                # 在 Unix-like 系统上，发送 SIGTERM 到进程组
                os.killpg(os.getpgid(streamlit_process.pid), signal.SIGTERM)
                time.sleep(2)
                if streamlit_process.poll() is None:
                    print("Streamlit 进程未响应 SIGTERM，发送 SIGKILL...")
                    os.killpg(os.getpgid(streamlit_process.pid), signal.SIGKILL)

            # 等待进程终止
            streamlit_process.wait(timeout=5)
            print("Streamlit 进程已终止。")
        except ProcessLookupError:
            print("Streamlit 进程未找到，可能已经停止。")
        except Exception as e:
            print(f"错误：停止 Streamlit 进程时出错 - {e}")
        finally:
            streamlit_process = None
    else:
        print("Streamlit 进程未运行或已停止。")


def on_closed() -> None:
    """pywebview 窗口关闭时的回调函数。"""
    print("Webview 窗口已关闭，正在停止 Streamlit...")
    stop_streamlit()


if __name__ == "__main__":
    # 在单独的线程中启动 Streamlit
    # start_streamlit 会更新全局变量 streamlit_port
    streamlit_thread = threading.Thread(target=start_streamlit, daemon=True)
    streamlit_thread.start()

    # 创建 pywebview 窗口
    window = webview.create_window(
        "ZZZ 模拟器", f"http://localhost:{streamlit_port}", width=1280, height=720
    )

    # 注册窗口关闭事件
    window.events.closed += on_closed

    # 启动 pywebview 事件循环
    # 使用 debug=True 可以在开发时提供更多信息
    webview.start(debug=True)

    print("应用程序退出。")
