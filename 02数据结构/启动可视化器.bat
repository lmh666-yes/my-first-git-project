@echo off
chcp 65001 >nul
setlocal
title C/C++ 数据结构可视化器 · 启动器

rem ============================================================
rem  C/C++ 数据结构可视化器 · 启动封装
rem  ------------------------------------------------------------
rem  功能：
rem    1. 自动定位 Python（优先 py -3，其次 python）
rem    2. 自动检查 tkinter 依赖是否可用
rem    3. 启动 visualizer.py 图形界面
rem
rem  说明：
rem    - 本脚本无需手动配置任何路径，双击即可运行
rem    - 关闭可视化器窗口后，程序自动退出
rem    - 若遇到错误，脚本会给出中文提示
rem ============================================================

:: 切到脚本所在目录（02数据结构\，兼容中文路径）
cd /d "%~dp0"

:: ---------- 1. 检查主程序是否存在 ----------
if not exist "%~dp0visualizer.py" (
    echo [错误] 未找到 visualizer.py 主程序，请检查文件是否完整。
    echo        本脚本应位于 02数据结构 目录中。
    echo.
    pause
    exit /b 1
)

:: ---------- 2. 自动定位 Python ----------
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)
if not defined PY (
    echo [错误] 未找到 Python 解释器。
    echo        请安装 Python 3 并勾选 "Add Python to PATH"。
    echo        下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: ---------- 3. 检查 tkinter 依赖 ----------
echo ================================================
echo    C/C++ 数据结构可视化器
echo ================================================
echo [信息] 使用 Python 命令: %PY%
echo [信息] 正在检查依赖（tkinter）...

%PY% -c "import tkinter" >nul 2>nul
if errorlevel 1 (
    echo.
    echo [错误] 缺少 tkinter（Python 图形库，属于标准库）。
    echo        请安装带 tkinter 的 Python 版本，
    echo        或重新安装 Python 时勾选 "tcl/tk and IDLE"。
    echo.
    pause
    exit /b 1
)
echo [信息] 依赖正常。

:: ---------- 4. 启动可视化器 ----------
echo [信息] 正在启动可视化器，请稍候 ...
echo [提示] 关闭窗口即退出程序。
echo.
%PY% "%~dp0visualizer.py"
echo.
echo [提示] 程序已退出。若上方有错误信息，请按提示解决后重试。
echo.
pause
