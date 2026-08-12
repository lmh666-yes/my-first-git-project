@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   安装个人 C 工具库到 MinGW
echo ========================================
echo.

:: 1. 查找 MinGW 的根目录
set "MINGW_ROOT="
for /f "delims=" %%i in ('where gcc 2^>nul') do (
    set "gcc_path=%%i"
    set "bin_dir=!gcc_path!..\.."
    echo !bin_dir! | findstr /i "mingw" >nul
    if !errorlevel! equ 0 (
        set "MINGW_ROOT=!bin_dir!"
        goto :found
    )
)

:: 如果没找到，尝试常用路径
if not defined MINGW_ROOT (
    if exist "C:\MinGW" set "MINGW_ROOT=C:\MinGW"
    if exist "C:\mingw64" set "MINGW_ROOT=C:\mingw64"
    if exist "D:\MinGW" set "MINGW_ROOT=D:\MinGW"
)

:found
if not defined MINGW_ROOT (
    echo [错误] 未找到 MinGW 安装目录，请确认已安装 MinGW。
    pause
    exit /b 1
)

echo [信息] 检测到 MinGW 根目录: %MINGW_ROOT%
echo.

:: 2. 设置目录路径
set "INCLUDE_DIR=%MINGW_ROOT%\include"
set "LIB_DIR=%MINGW_ROOT%\lib"
if not exist "%INCLUDE_DIR%" mkdir "%INCLUDE_DIR%"
if not exist "%LIB_DIR%" mkdir "%LIB_DIR%"

:: 3. 复制头文件
echo [步骤 1] 复制头文件到 %INCLUDE_DIR% ...
copy /Y "utils\utils.h" "%INCLUDE_DIR%\" >nul
if %errorlevel% neq 0 (
    echo [错误] 复制 utils.h 失败
    pause
    exit /b 1
)
copy /Y "framework\multifunc.h" "%INCLUDE_DIR%\" >nul
if %errorlevel% neq 0 (
    echo [错误] 复制 multifunc.h 失败
    pause
    exit /b 1
)
echo [成功] 头文件复制完成。

:: 4. 编译静态库
echo [步骤 2] 编译工具库 ...
gcc -c utils\utils.c -o utils.o
if %errorlevel% neq 0 (
    echo [错误] 编译 utils.c 失败
    pause
    exit /b 1
)
gcc -c framework\multifunc.c -o multifunc.o
if %errorlevel% neq 0 (
    echo [错误] 编译 multifunc.c 失败
    pause
    exit /b 1
)

echo [步骤 3] 打包静态库 ...
ar rcs libmylib.a utils.o multifunc.o
if %errorlevel% neq 0 (
    echo [错误] 打包静态库失败
    pause
    exit /b 1
)

echo [步骤 4] 复制 libmylib.a 到 %LIB_DIR% ...
copy /Y libmylib.a "%LIB_DIR%\" >nul
if %errorlevel% neq 0 (
    echo [错误] 复制库文件失败
    pause
    exit /b 1
)

:: 5. 清理
del utils.o multifunc.o libmylib.a >nul 2>&1

echo ========================================
echo [成功] 工具库安装完成！
echo 您现在可以在任何 C 程序中：
echo   #include ^<utils.h^>
echo   #include ^<multifunc.h^>
echo 编译时链接：gcc main.c -lmylib -o main
echo ========================================
pause