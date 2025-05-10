@echo off

:: 检查是否安装了uv
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo 正在自动安装uv工具...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    if %errorlevel% neq 0 (
        echo 安装失败，请手动安装
        pause
        exit /b 1
    )
)

:: 运行主程序
uv run .\zsim\webview_app.py