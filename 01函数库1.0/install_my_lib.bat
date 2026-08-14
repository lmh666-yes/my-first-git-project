@echo off
setlocal enabledelayedexpansion
chcp 936 >nul
title UTILS 函数库一键部署

rem ============================================================
rem  UTILS 函数库 · 一键部署到 MinGW
rem  运行本脚本后，在任何目录新建 C 程序只需：
rem      #include <utils.h>
rem      #include <multifunc.h>
rem      gcc 你的程序.c -lmylib -o 程序
rem  即可直接调用全部函数，无需再把函数源码复制到工程目录。
rem
rem  注意：本脚本必须用 GBK(ANSI) 编码保存，中文才不会乱码。
rem ============================================================

:: 无论从哪里调用，都先切到脚本所在目录
cd /d "%~dp0"

echo.
echo ================================================
echo    UTILS 函数库 · 一键部署到 MinGW
echo    （当前版本：1157 个函数 / 宏）
echo ================================================
echo.

:: ============ 1. 定位 MinGW 根目录 ============
set "MINGW_ROOT="

:: 方法一：从 PATH 中的 gcc.exe 推导（bin 的上一级即根目录）
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

:: 方法二：尝试常见安装位置
if not defined MINGW_ROOT (
    for %%p in ("C:\MinGW" "C:\mingw64" "C:\TDM-GCC-64" "C:\msys64\mingw64" "D:\MinGW" "D:\mingw64") do (
        if exist "%%~p\bin\gcc.exe" set "MINGW_ROOT=%%~p"
    )
)

:found
if not defined MINGW_ROOT (
    echo [错误] 未找到 MinGW，找不到 gcc.exe。
    echo        请安装 MinGW-w64，或把其 bin 目录加入 PATH 后重试。
    echo.
    pause
    exit /b 1
)
echo [信息] MinGW 根目录   ：%MINGW_ROOT%

:: ============ 2. 确定头文件 / 库目录 ============
:: MinGW-w64 头文件在【根目录\目标平台\include】，不是根目录\include
set "MINGW_TARGET=x86_64-w64-mingw32"
for /f "delims=" %%t in ('"%MINGW_ROOT%\bin\gcc.exe" -dumpmachine 2^>nul') do set "MINGW_TARGET=%%t"
set "INCLUDE_DIR=%MINGW_ROOT%\%MINGW_TARGET%\include"
set "LIB_DIR_A=%MINGW_ROOT%\%MINGW_TARGET%\lib"
set "LIB_DIR_B=%MINGW_ROOT%\lib"
if not exist "%INCLUDE_DIR%" mkdir "%INCLUDE_DIR%"
if not exist "%LIB_DIR_A%"  mkdir "%LIB_DIR_A%"
if not exist "%LIB_DIR_B%"  mkdir "%LIB_DIR_B%"
echo [信息] 头文件目录   ：%INCLUDE_DIR%
echo [信息] 库文件目录   ：%LIB_DIR_A%  和  %LIB_DIR_B%
echo.

:: ============ 3. 复制头文件 ============
echo [步骤 1/5] 复制头文件 ...
set "ERR=0"
if not exist "library\utils.h"         set ERR=1
if not exist "library\utils_gen.h"     set ERR=1
if not exist "library\func_index.h"    set ERR=1
if not exist "library\multifunc.h" set ERR=1
if %ERR%==1 (
    echo [错误] 缺少源文件，请检查 library 目录是否完整。
    pause
    exit /b 1
)
copy /Y "library\utils.h"           "%INCLUDE_DIR%\" >nul
copy /Y "library\utils_gen.h"       "%INCLUDE_DIR%\" >nul
copy /Y "library\func_index.h"      "%INCLUDE_DIR%\" >nul
copy /Y "library\multifunc.h" "%INCLUDE_DIR%\" >nul
if errorlevel 1 (
    echo [错误] 头文件复制失败，请检查目录权限。
    pause
    exit /b 1
)
echo [完成] 已安装 4 个头文件。

:: ============ 4. 编译源码（-O2 优化） ============
echo [步骤 2/5] 编译源码 ...
gcc -c -O2 "library\utils.c" -o utils.o
if errorlevel 1 (
    echo [错误] 编译 library\utils.c 失败，请检查上方错误信息。
    pause
    exit /b 1
)
gcc -c -O2 "library\multifunc.c" -o multifunc.o
if errorlevel 1 (
    echo [错误] 编译 library\multifunc.c 失败，请检查上方错误信息。
    pause
    exit /b 1
)
echo [完成] 编译完成。

:: ============ 5. 打包并安装静态库 ============
echo [步骤 3/5] 打包静态库 libmylib.a ...
ar rcs libmylib.a utils.o multifunc.o
if errorlevel 1 (
    echo [错误] 打包 libmylib.a 失败。
    pause
    exit /b 1
)
copy /Y libmylib.a "%LIB_DIR_A%\" >nul
if errorlevel 1 (
    echo [错误] 复制 libmylib.a 到 %LIB_DIR_A% 失败。
    pause
    exit /b 1
)
copy /Y libmylib.a "%LIB_DIR_B%\" >nul
if errorlevel 1 (
    echo [错误] 复制 libmylib.a 到 %LIB_DIR_B% 失败。
    pause
    exit /b 1
)
echo [完成] 静态库已安装。

:: ============ 6. 清理临时文件 ============
del /q utils.o multifunc.o libmylib.a 2>nul
echo [步骤 4/5] 临时文件已清理。

:: ============ 7. 确保 gcc 在 PATH ============
echo [步骤 5/5] 检查 gcc 是否在 PATH ...
echo %PATH% | findstr /i /c:"%MINGW_ROOT%\bin" >nul
if errorlevel 1 (
    echo [提示] gcc 不在 PATH，无法在任意目录直接运行 gcc。
    set /p ADD_PATH="是否把 %MINGW_ROOT%\bin 加入用户 PATH？[Y/n] "
    if /i "!ADD_PATH!" neq "n" (
        set "USER_PATH="
        for /f "tokens=2,*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul ^| findstr /r /c:"^    Path"') do set "USER_PATH=%%b"
        if defined USER_PATH (
            setx PATH "!USER_PATH!;%MINGW_ROOT%\bin" >nul
        ) else (
            setx PATH "%MINGW_ROOT%\bin" >nul
        )
        echo [信息] 用户 PATH 已更新，新开的命令行窗口生效。
    )
) else (
    echo [完成] gcc 已在 PATH 中。
)

:: ============ 8. 在临时目录验证：任意目录可用 ============
echo.
set /p RUN_TEST="是否编译运行验证程序，确认任意目录可用？[Y/n] "
if /i "!RUN_TEST!" neq "n" (
    echo [验证] 在临时目录编译并运行验证程序 ...
    if not exist "%TEMP%\mylib_test" mkdir "%TEMP%\mylib_test"
    copy /Y "tests\verify_install.c" "%TEMP%\mylib_test\" >nul
    pushd "%TEMP%\mylib_test"
    gcc verify_install.c -lmylib -o verify_install.exe
    if errorlevel 1 (
        echo [错误] 验证程序编译失败，请检查上方错误信息。
    ) else (
        verify_install.exe
        if errorlevel 1 (
            echo [错误] 验证程序运行失败。
        ) else (
            echo.
            echo [完成] 验证通过！函数库已可以从任意目录直接调用。
        )
    )
    popd
)

echo.
echo ================================================
echo   [完成] 部署结束！
echo.
echo   之后在任何目录写 C 程序：
echo     #include ^<utils.h^>
echo     #include ^<multifunc.h^>
echo     gcc 你的程序.c -lmylib -o 程序
echo ================================================
pause
