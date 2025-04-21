import subprocess
import sys
import argparse
from typing import Literal
from pydantic import BaseModel, Field


class MainArgs(BaseModel):
    """main.py 的命令行参数模型"""

    stop_tick: int | None = Field(None, description="指定模拟的tick数量")
    mode: Literal["normal", "parallel"] | None = Field(None, description="运行模式")
    adjust_char: Literal[1, 2, 3] | None = Field(None, description="调整的角色相对位置")
    sc_name: str | None = Field(None, description="要调整的副词条名称")
    sc_value: int | None = Field(None, description="要调整的副词条数量")
    run_turn_uuid: str | None = Field(None, description="本轮次并行运行的uuid")
    remove_equip: bool | None = Field(None, description="移除装备")


def go_webui():
    """启动Streamlit服务"""
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "zsim/webui.py"])
    except Exception as e:
        print(f"错误：启动Streamlit失败 - {str(e)}")
        sys.exit(1)


def go_cli(args: MainArgs = MainArgs()):
    """启动命令行界面，并根据提供的 MainArgs 对象传递参数。

    Args:
        args (MainArgs): 包含传递给 main.py 的参数的对象。
                       默认为一个空的 MainArgs 对象，表示不传递额外参数。
    """
    try:
        command = [sys.executable, "zsim/main.py"]
        for field, value in args.model_dump(exclude_none=True).items():
            if isinstance(value, bool):
                if value:
                    command.append(f"--{field.replace('_', '-')}")
            else:
                command.extend([f"--{field.replace('_', '-')}", str(value)])

        subprocess.run(command)
    except Exception as e:
        print(f"错误：启动命令行界面失败 - {str(e)}")
        sys.exit(1)


def go_single_subprocess(stop_tick: int):
    """启动单个子进程"""
    try:
        results = []
        command = [sys.executable, "zsim/main.py", "--stop-tick", str(stop_tick)]
        proc = subprocess.run(command, capture_output=True, text=True)
        results.append(proc.stdout.strip())
        return "\n".join(results)
    except Exception as e:
        return f"错误：启动子进程失败 - {str(e)}"


def go_parallel_subprocess(args: MainArgs):
    """根据提供的 MainArgs 对象启动并行模式子进程。

    注意：此函数会强制将 'mode' 参数设置为 'parallel'。

    Args:
        args (MainArgs): 包含传递给 main.py 的参数的对象。
                       其中的 'mode' 参数会被忽略并强制设为 'parallel'。
    """
    try:
        command = [sys.executable, "zsim/main.py"]
        # 强制设置 mode 为 parallel，即使 args 中有其他值
        args_dict = args.model_dump(exclude_none=True)
        args_dict["mode"] = "parallel"  # 确保 mode 是 parallel

        for field, value in args_dict.items():
            if field == "mode" and value != "parallel":  # 跳过非 parallel 的 mode
                continue
            if isinstance(value, bool):
                if value:
                    command.append(f"--{field.replace('_', '-')}")
            else:
                command.extend([f"--{field.replace('_', '-')}", str(value)])

        # 注意：并行模式可能需要更复杂的处理
        proc = subprocess.run(command, capture_output=True, text=True, check=True)
        return proc.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"错误：启动子进程失败 - {e.stderr}"
    except Exception as e:
        return f"错误：启动子进程失败 - {str(e)}"


def go_help():
    """显示帮助信息"""
    print("ZZZ模拟器")
    print("命令列表：")
    print("  run: 启动webui")
    print("  c: 使用main.py运行保存的配置")
    confirm_launch()


def confirm_launch():
    """交互式确认启动"""
    # 注意：这里调用 go_cli 时未使用参数，如果需要从交互式输入获取参数，需修改
    CHOICES = {"run": go_webui, "c": go_cli, "help": go_help}
    choice = input("输入run启动模拟器页面，输入c运行命令行，输入help查看选项：").lower()
    if choice in CHOICES.keys():
        if choice == "c":
            # 如果选择 'c'，调用 go_cli 时不传递特定参数，使用默认值
            CHOICES[choice]()
        else:
            CHOICES[choice]()
    else:
        print("操作已取消")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="ZZZ Simulator")
    parser.add_argument(
        "command", nargs="?", default=None, help="子命令（例如：run, c）"
    )
    # 未来可以扩展这里，使其能解析 main.py 的参数并传递给 go_cli
    args = parser.parse_args()

    if args.command == "run":
        go_webui()
    elif args.command == "c":
        # 调用 go_cli 时不传递特定参数，使用默认值
        go_cli()
    else:
        print("ZZZ模拟器\n")
        confirm_launch()


if __name__ == "__main__":
    main()
