@echo off
chcp 65001 >nul
echo === 6900DMR 联系人转换工具 · 打包 ===
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [x] 未找到 python，请先安装 Python 3.10 以上版本。
  pause
  exit /b 1
)

python -m pip install --upgrade pyinstaller
if errorlevel 1 goto fail

echo.
echo --- 运行冒烟测试 ---
python tests\test_convert.py
if errorlevel 1 goto fail

echo.
echo --- 打包单文件 exe ---
python -m PyInstaller --onefile --clean --noconfirm --name "6900DMR-Contact-Tool" dmr_contact_converter.py
if errorlevel 1 goto fail

echo.
echo [OK] 产物：dist\6900DMR-Contact-Tool.exe
pause
exit /b 0

:fail
echo.
echo [x] 出错，请查看上方日志。
pause
exit /b 1
