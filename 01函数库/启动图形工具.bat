@echo off
chcp 65001 >nul
title UTILS 函数库 · 图形化查找工具

rem ============================================================
rem  UTILS 函数库 · 图形化查找工具（utils_gui.exe）启动封装
rem
rem  双击本脚本即可启动图形化函数查询工具：
rem   - 搜索 / 分类筛选 1179 个函数
rem   - 查看函数说明、调用示例、实现源码
rem   - 一键跳转 VS Code、复制函数名/示例/源码
rem
rem  若尚未编译 utils_gui.exe，会自动调用 build_gui.bat 先编译。
rem ============================================================

:: 切到脚本所在目录（01函数库\，兼容中文路径）
cd /d "%~dp0"

:: 若可执行文件不存在，先自动编译
if not exist "programs\utils_gui.exe" (
    echo [提示] 未找到 utils_gui.exe，正在自动编译 ...
    call "programs\build_gui.bat"
)

:: 启动图形化查找工具
if exist "programs\utils_gui.exe" (
    start "" "programs\utils_gui.exe"
) else (
    echo [错误] utils_gui.exe 编译失败，请检查 MinGW 环境。
    pause
)
