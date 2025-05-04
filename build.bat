@echo off
set ROOT_DIR=%~dp0

echo 正在清理旧构建文件...
rd /s /q "%ROOT_DIR%dist" 2>nul
rd /s /q "%ROOT_DIR%build" 2>nul

echo 正在打包应用程序...
pyinstaller ^
  --onefile ^
  --noconfirm ^
  --clean ^
  --hidden-import=zsim ^
  --add-data "%ROOT_DIR%zsim\data;zsim/data" ^
  --add-data "%ROOT_DIR%docs;docs" ^
  "%ROOT_DIR%zsim\webview_app.py"

echo 打包完成，输出目录：%ROOT_DIR%dist
pause