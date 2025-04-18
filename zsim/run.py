import subprocess
import sys
import argparse


def go_webui():
    """启动Streamlit服务"""
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "zsim/webui.py"])
    except Exception as e:
        print(f"错误：启动Streamlit失败 - {str(e)}")
        sys.exit(1)


def go_cli():
    """启动命令行界面"""
    try:
        subprocess.run([sys.executable, "zsim/main.py"])
    except Exception as e:
        print(f"错误：启动命令行界面失败 - {str(e)}")
        sys.exit(1)


def go_help():
    """显示帮助信息"""
    print("ZZZ模拟器")
    print("命令列表：")
    print("  run: 启动webui")
    print("  c: 使用main.py运行保存的配置")
    confirm_launch()


def confirm_launch():
    """交互式确认启动"""
    CHOICES = {"run": go_webui, "c": go_cli, "help": go_help}
    choice = input("输入run启动模拟器页面，输入help查看选项：").lower()
    if choice in CHOICES.keys():
        CHOICES[choice]()
    else:
        print("操作已取消")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="ZZZ Simulator")
    parser.add_argument("command", nargs="?", default=None, help="子命令（例如：run）")
    args = parser.parse_args()

    if args.command == "run":
        go_webui()
    elif args.command == "c":
        go_cli()
    else:
        print("ZZZ模拟器\n")
        confirm_launch()


if __name__ == "__main__":
    main()
