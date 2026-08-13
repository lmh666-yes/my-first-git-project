@echo off
cd /d "%~dp0"
echo 正在编译图形化查找工具 ...
gcc -Wall -Wextra -I..\lib -o utils_gui.exe utils_gui.c -mwindows -lcomctl32 -lshell32
if errorlevel 1 (
    echo.
    echo [ERROR] 编译失败，请检查 utils_gui.c 或 lib\func_index.h 是否存在。
    pause
    exit /b 1
)
echo.
echo [OK] 编译成功：utils_gui.exe
echo 直接双击运行即可（程序会自动在 ..\lib 中查找函数库）。
pause
