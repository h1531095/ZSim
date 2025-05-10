#!/bin/bash

# 检查是否安装了uv
if ! command -v uv &> /dev/null; then
    echo "正在自动安装uv工具..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    if [ $? -ne 0 ]; then
        echo "安装失败，请手动安装"
        exit 1
    fi
fi

# 运行主程序
uv run ./zsim/webview_app.py