import subprocess
import sys
import argparse


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
        subprocess.run([sys.executable, "-m", "streamlit", "run", "zsim/webui.py"])
    except Exception as e:
        print(f"错误：启动Streamlit失败 - {str(e)}")
        sys.exit(1)

def confirm_launch():
    """交互式确认启动"""
    choice = input("是否立即启动模拟器？(y/n): ").lower()
    if choice == 'y':
        run_streamlit()
    else:
        print("操作已取消")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description='ZZZ Simulator')
    parser.add_argument('command', nargs='?', default=None, help='子命令（例如：run）')
    args = parser.parse_args()

    if args.command == 'run':
        run_streamlit()
    else:
        print("ZZZ模拟器命令行界面\n")
        confirm_launch()

if __name__ == "__main__":
    main()