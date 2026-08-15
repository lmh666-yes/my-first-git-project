@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title UTILS 函数库 · 一键部署到 MinGW

rem ============================================================
rem  UTILS 函数库（1179 个函数 / 宏）· 一键部署到 MinGW
rem
rem  部署后，在任何目录写 C 程序只需：
rem      #include <utils.h>
rem      #include <multifunc.h>
rem      gcc 你的程序.c -lmylib -o 程序
rem  即可直接调用全部库函数，无需再把函数源码复制到你的项目目录。
rem
rem  本脚本会依次执行：
rem    1. 自动定位 MinGW（gcc）
rem    2. 复制 utils.h / utils_gen.h / func_index.h / multifunc.h 到头文件目录
rem    3. 分别编译 utils.c / utils_gen.c / multifunc.c
rem       （拆分编译：避免把 6000+ 行的 utils_gen.c 连带进 utils.c，导致卡顿）
rem    4. 用 ar 打包成静态库 libmylib.a 并安装到库目录
rem    5. 检查 gcc 是否在 PATH
rem    6. 可选：编译运行 verify_install.c 验证任意目录可直接调用
rem
rem  注：本脚本以 UTF-8 保存，开头已 chcp 65001 切换代码页，中文正常显示。
rem ============================================================

:: 切到脚本所在目录（兼容中文路径）
cd /d "%~dp0"

echo.
echo ================================================
echo    UTILS 函数库 · 一键部署到 MinGW
echo    当前版本：1179 个函数 / 宏
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
set "AR=%MINGW_ROOT%\bin\ar.exe"
echo [信息] MinGW 根目录   = %MINGW_ROOT%

:: ============ 2. 确定头文件 / 库目录 ============
:: MinGW-w64 头文件在「根目录\目标平台\include」，也可能是根目录\include
set "MINGW_TARGET=x86_64-w64-mingw32"
for /f "delims=" %%t in ('"%GCC%" -dumpmachine 2^>nul') do set "MINGW_TARGET=%%t"
set "INCLUDE_DIR=%MINGW_ROOT%\%MINGW_TARGET%\include"
set "LIB_DIR_A=%MINGW_ROOT%\%MINGW_TARGET%\lib"
set "LIB_DIR_B=%MINGW_ROOT%\lib"
if not exist "%INCLUDE_DIR%" mkdir "%INCLUDE_DIR%"
if not exist "%LIB_DIR_A%"  mkdir "%LIB_DIR_A%"
if not exist "%LIB_DIR_B%"  mkdir "%LIB_DIR_B%"
echo [信息] 头文件目录   = %INCLUDE_DIR%
echo [信息] 库文件目录   = %LIB_DIR_A%  或  %LIB_DIR_B%
echo.

:: ============ 3. 安装头文件 ============
echo [步骤 1/7] 安装头文件 ...
set "ERR=0"
if not exist "library\utils.h"         set ERR=1
if not exist "library\utils_gen.h"     set ERR=1
if not exist "library\func_index.h"    set ERR=1
if not exist "library\multifunc.h"     set ERR=1
if %ERR%==1 (
    echo [错误] 缺少源文件，请检查 library 目录是否完整。
    pause
    exit /b 1
)
copy /Y "library\utils.h"         "%INCLUDE_DIR%\" >nul
copy /Y "library\utils_gen.h"     "%INCLUDE_DIR%\" >nul
copy /Y "library\func_index.h"    "%INCLUDE_DIR%\" >nul
copy /Y "library\multifunc.h"     "%INCLUDE_DIR%\" >nul
if errorlevel 1 (
    echo [错误] 头文件复制失败，请检查目录权限。
    pause
    exit /b 1
)
echo [完成] 已安装 4 个头文件。

:: ============ 4. 拆分编译源码（避免卡顿） ============
echo [步骤 2/7] 编译 utils.c ...
"%GCC%" -c -O2 "library\utils.c" -o utils.o
if errorlevel 1 ( echo [错误] 编译 utils.c 失败。 & pause & exit /b 1 )
echo [完成] utils.c 编译完成。

echo [步骤 3/7] 编译 utils_gen.c（6000+ 行，请稍候）...
"%GCC%" -c -O2 "library\utils_gen.c" -o utils_gen.o
if errorlevel 1 ( echo [错误] 编译 utils_gen.c 失败。 & pause & exit /b 1 )
echo [完成] utils_gen.c 编译完成。

echo [步骤 4/7] 编译 multifunc.c ...
"%GCC%" -c -O2 "library\multifunc.c" -o multifunc.o
if errorlevel 1 ( echo [错误] 编译 multifunc.c 失败。 & pause & exit /b 1 )
echo [完成] multifunc.c 编译完成。

:: ============ 5. 打包静态库并安装 ============
echo [步骤 5/7] 打包 libmylib.a ...
"%AR%" rcs libmylib.a utils.o utils_gen.o multifunc.o
if errorlevel 1 ( echo [错误] 打包 libmylib.a 失败。 & pause & exit /b 1 )
copy /Y libmylib.a "%LIB_DIR_A%\" >nul
if errorlevel 1 ( echo [错误] 复制到 %LIB_DIR_A% 失败。 & pause & exit /b 1 )
copy /Y libmylib.a "%LIB_DIR_B%\" >nul
if errorlevel 1 ( echo [错误] 复制到 %LIB_DIR_B% 失败。 & pause & exit /b 1 )
echo [完成] 静态库已安装。

:: ============ 6. 清理临时文件 ============
echo [步骤 6/7] 清理临时文件 ...
del /q utils.o utils_gen.o multifunc.o libmylib.a 2>nul
echo [完成] 临时文件已清理。

:: ============ 7. 检查 gcc 是否在 PATH ============
echo [步骤 7/7] 检查 gcc 是否在 PATH ...
echo %PATH% | findstr /i /c:"%MINGW_ROOT%\bin" >nul
if errorlevel 1 (
    echo [提示] gcc 不在 PATH，无法在任意目录直接调用 gcc。
    set /p ADD_PATH="是否将 %MINGW_ROOT%\bin 加入用户 PATH？[Y/n] "
    if /i "!ADD_PATH!" neq "n" (
        set "USER_PATH="
        for /f "tokens=2,*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul ^| findstr /r /c:"^    Path"') do set "USER_PATH=%%b"
        if defined USER_PATH (
            setx PATH "!USER_PATH!;%MINGW_ROOT%\bin" >nul
        ) else (
            setx PATH "%MINGW_ROOT%\bin" >nul
        )
        echo [信息] 用户 PATH 已更新，新开命令行窗口后生效。
    )
) else (
    echo [完成] gcc 已在 PATH 中。
)

:: ============ 8. 可选：验证部署 ============
echo.
set /p RUN_TEST="是否运行验证程序（确认任意目录可直接调用）？[Y/n] "
if /i "!RUN_TEST!" neq "n" (
    echo [验证] 在临时目录编译并运行 verify_install.c ...
    if not exist "%TEMP%\mylib_test" mkdir "%TEMP%\mylib_test"
    copy /Y "tests\verify_install.c" "%TEMP%\mylib_test\" >nul
    pushd "%TEMP%\mylib_test"
    "%GCC%" verify_install.c -lmylib -o verify_install.exe
    if errorlevel 1 (
        echo [错误] 验证程序编译失败，请查看上方错误信息。
    ) else (
        verify_install.exe
        if errorlevel 1 (
            echo [错误] 验证程序运行失败。
        ) else (
            echo.
            echo [完成] 验证通过！你已可以在任意目录直接调用。
        )
    )
    popd
)

echo.
echo ================================================
echo   [完成] 函数库部署成功！
echo.
echo   之后在任何目录写 C 程序：
echo     #include ^<utils.h^>
echo     #include ^<multifunc.h^>
echo     gcc 你的程序.c -lmylib -o 程序
echo ================================================
pause
