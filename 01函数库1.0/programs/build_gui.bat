@echo off
chcp 936 >nul
rem ============================================================
rem  UTILS 函数库 · 图形化查找工具 编译脚本
rem  注意：本脚本以 GBK(ANSI) 编码保存，中文才不会乱码。
rem        （与 install_my_lib.bat 保持一致）
rem ============================================================
cd /d "%~dp0"
echo 正在编译图形化查找工具 ...
gcc -Wall -Wextra -finput-charset=UTF-8 -fexec-charset=GBK -I..\library -o utils_gui.exe utils_gui.c -mwindows -lcomctl32 -lshell32
if errorlevel 1 (
    echo.
    echo [ERROR] 编译失败，请检查 utils_gui.c 或 library\func_index.h 是否存在。
    pause
    exit /b 1
)
echo.
echo [OK] 编译成功：utils_gui.exe
echo 直接双击运行即可（程序会自动在 ..\library 中查找函数库）。
pause
