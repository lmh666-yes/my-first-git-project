@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title UTILS 函数库 · 图形化查找工具 · 编译脚本

rem ============================================================
rem  UTILS 函数库 · 图形化查找工具（utils_gui.exe）编译脚本
rem
rem  功能：把 utils_gui.c 编译成 Windows 图形程序 utils_gui.exe，
rem        用于按关键词 / 分类查找全部 1179 个函数、复制示例、
rem        并一键跳转 VS Code 查看源码。
rem
rem  本脚本会自动定位 MinGW 的 gcc，无需手动配置 PATH。
rem  编译输出：programs\utils_gui.exe（双击即可运行）。
rem
rem  注：本脚本以 UTF-8 保存，开头已 chcp 65001 切换代码页，中文正常显示。
rem ============================================================

:: 切到脚本所在目录（programs\，兼容中文路径）
cd /d "%~dp0"

echo.
echo ================================================
echo    UTILS 函数库 · 编译图形化查找工具
echo ================================================
echo.

:: ============ 1. 定位 MinGW 根目录 ============
set "MINGW_ROOT="

:: 优先从 PATH 中的 gcc.exe 反推 MinGW 根目录
for /f "delims=" %%i in ('where gcc 2^>nul') do (
    pushd "%%~dpi.." 2>nul
    set "candidate=!CD!"
    popd
    echo !candidate! | findstr /i "mingw" >nul
    if not errorlevel 1 (
        if exist "!candidate!\bin\gcc.exe" (
            set "MINGW_ROOT=!candidate!"
            goto :found
        )
    )
)

:: 备选：常见安装位置
if not defined MINGW_ROOT (
    for %%p in ("C:\MinGW" "C:\mingw64" "C:\TDM-GCC-64" "C:\msys64\mingw64" "D:\MinGW" "D:\mingw64") do (
        if exist "%%~p\bin\gcc.exe" set "MINGW_ROOT=%%~p"
    )
)

:found
if not defined MINGW_ROOT (
    echo [错误] 未找到 MinGW（找不到 gcc.exe）。
    echo        请安装 MinGW-w64，并将 bin 目录加入 PATH 后再试。
    echo.
    pause
    exit /b 1
)
set "GCC=%MINGW_ROOT%\bin\gcc.exe"
echo [信息] MinGW 根目录   = %MINGW_ROOT%

:: ============ 2. 检查源码与头文件 ============
if not exist "utils_gui.c" (
    echo [错误] 缺少 utils_gui.c 源码文件。
    pause
    exit /b 1
)
if not exist "..\library\func_index.h" (
    echo [错误] 缺少 ..\library\func_index.h（函数索引表）。
    pause
    exit /b 1
)

:: ============ 3. 编译图形工具 ============
echo [编译] 正在编译 utils_gui.exe（请稍候）...
"%GCC%" -Wall -Wextra -finput-charset=UTF-8 -fexec-charset=GBK -I..\library ^
        -o utils_gui.exe utils_gui.c -mwindows -lcomctl32 -lshell32
if errorlevel 1 (
    echo.
    echo [错误] 编译失败，请检查 utils_gui.c 与 ..\library\func_index.h 是否存在、
    echo        以及源码是否有语法错误。
    pause
    exit /b 1
)

:: ============ 4. 编译完成 ============
echo.
echo [完成] 编译成功，已生成 utils_gui.exe
echo        直接双击运行即可；也可以在本目录命令行输入 utils_gui 启动。
echo.
echo   提示：工具会自动到 ..\library 目录读取
echo         utils.h / utils_gen.h / utils.c / utils_gen.c 四个文件，
echo         因此请保持本程序的目录结构完整。
echo.
pause
