@echo off
chcp 65001 >nul
setlocal
title C 语言刷题软件 · 启动器

rem ============================================================
rem  C 语言刷题软件 · 启动封装
rem  1. 自动定位 Python（优先 py -3，其次 python）
rem  2. 若缺少 题库.json 则提示先运行 build_bank.py
rem  3. 启动 刷题软件.py 图形界面
rem ============================================================

cd /d "%~dp0"

if not exist "%~dp0刷题软件.py" (
    echo [错误] 未找到 刷题软件.py 主程序。
    echo.
    pause
    exit /b 1
)

if not exist "%~dp0题库.json" (
    echo [提示] 未找到 题库.json，正在尝试从 Word 文档生成题库 ...
    echo.
    where python >nul 2>nul && set "PY=python"
    where py >nul 2>nul && set "PY=py -3"
    if defined PY (
        %PY% "%~dp0build_bank.py"
    )
    if not exist "%~dp0题库.json" (
        echo [错误] 题库生成失败，请确认存在 嵌入式软件开发（中级）题库（含答案）.docx。
        echo.
        pause
        exit /b 1
    )
)

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)
if not defined PY (
    echo [错误] 未找到 Python 解释器。
    echo        请安装 Python 3 并勾选 "Add Python to PATH"。
    echo.
    pause
    exit /b 1
)

echo ================================================
echo    C 语言刷题软件
echo ================================================
echo [信息] 正在启动刷题软件，请稍候 ...
echo [提示] 关闭窗口即退出程序。
echo.
%PY% "%~dp0刷题软件.py"
if errorlevel 1 (
    echo.
    echo [错误] 程序异常退出（错误码 %errorlevel%）。
    echo.
    pause
    exit /b 1
)
exit /b 0
