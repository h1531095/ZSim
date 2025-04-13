import subprocess
import sys


def check_streamlit():
    """检查streamlit是否已安装"""
    try:
        import streamlit
        print("Streamlit已安装")
    except ImportError:
        print("正在安装Streamlit...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])

def run_streamlit():
    """启动Streamlit服务"""
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "webui.py"])
    except Exception as e:
        print(f"错误：启动Streamlit失败 - {str(e)}")
        sys.exit(1)

def main():
    print("正在启动ZZZ模拟器...")
    run_streamlit()

if __name__ == "__main__":
    main()