@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   Install personal C library to MinGW
echo ========================================
echo.

:: Run from the script's own folder, no matter where it is invoked from
cd /d "%~dp0"

:: ============ 1. Locate the MinGW root ============
set "MINGW_ROOT="

:: Method 1: derive from gcc.exe found in PATH (parent of bin is the root)
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

:: Method 2: try common install locations
if not defined MINGW_ROOT (
    for %%p in ("C:\MinGW" "C:\mingw64" "C:\TDM-GCC-64" "C:\msys64\mingw64" "D:\MinGW" "D:\mingw64") do (
        if exist "%%~p\bin\gcc.exe" set "MINGW_ROOT=%%~p"
    )
)

:found
if not defined MINGW_ROOT (
    echo [ERROR] MinGW not found - gcc.exe not located.
    echo Please install MinGW-w64, or add its bin folder to PATH and retry.
    pause
    exit /b 1
)

echo [INFO] MinGW root       : %MINGW_ROOT%

:: ============ 2. Determine gcc's header / library search dirs ============
:: MinGW-w64 searches headers in <root>\<target>\include (NOT <root>\include).
set "MINGW_TARGET=x86_64-w64-mingw32"
for /f "delims=" %%t in ('"%MINGW_ROOT%\bin\gcc.exe" -dumpmachine 2^>nul') do set "MINGW_TARGET=%%t"
set "INCLUDE_DIR=%MINGW_ROOT%\%MINGW_TARGET%\include"
set "LIB_DIR=%MINGW_ROOT%\lib"
if not exist "%INCLUDE_DIR%" mkdir "%INCLUDE_DIR%"
if not exist "%LIB_DIR%" mkdir "%LIB_DIR%"
echo [INFO] Header directory : %INCLUDE_DIR%
echo [INFO] Library directory: %LIB_DIR%
echo.

:: ============ 3. Copy header files ============
echo [Step 1/4] Copying header files ...
copy /Y "utils\utils.h" "%INCLUDE_DIR%\" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy utils\utils.h
    pause
    exit /b 1
)
copy /Y "framework\multifunc.h" "%INCLUDE_DIR%\" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy framework\multifunc.h
    pause
    exit /b 1
)
echo [OK] Headers installed.

:: ============ 4. Build the static library ============
echo [Step 2/4] Compiling sources ...
gcc -c "utils\utils.c" -o utils.o
if errorlevel 1 (
    echo [ERROR] Failed to compile utils\utils.c
    pause
    exit /b 1
)
gcc -c "framework\multifunc.c" -o multifunc.o
if errorlevel 1 (
    echo [ERROR] Failed to compile framework\multifunc.c
    pause
    exit /b 1
)
echo [OK] Compilation done.

echo [Step 3/4] Packing static library ...
ar rcs libmylib.a utils.o multifunc.o
if errorlevel 1 (
    echo [ERROR] Failed to pack the static library
    pause
    exit /b 1
)
copy /Y libmylib.a "%LIB_DIR%\" >nul
if errorlevel 1 (
    echo [ERROR] Failed to copy libmylib.a
    pause
    exit /b 1
)
echo [OK] Static library installed to %LIB_DIR%.

:: ============ 5. Clean up intermediate files ============
del utils.o multifunc.o libmylib.a >nul 2>&1

:: ============ 6. Make sure gcc is on PATH (callable from anywhere) ============
echo.
echo %PATH% | findstr /i /c:"%MINGW_ROOT%\bin" >nul
if errorlevel 1 (
    echo [NOTE] gcc is NOT on PATH, so "gcc" cannot be run from anywhere.
    set /p ADD_PATH="Add %MINGW_ROOT%\bin to your user PATH? [Y/n] "
    if /i "!ADD_PATH!" neq "n" (
        set "USER_PATH="
        for /f "tokens=2,*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul ^| findstr /r /c:"^    Path"') do set "USER_PATH=%%b"
        if defined USER_PATH (
            setx PATH "!USER_PATH!;%MINGW_ROOT%\bin" >nul
        ) else (
            setx PATH "%MINGW_ROOT%\bin" >nul
        )
        echo [INFO] User PATH updated. It takes effect in new command windows.
    )
) else (
    echo [OK] gcc is already on PATH; callable from anywhere.
)

:: ============ 7. Optional: compile and run the test program ============
echo.
set /p RUN_TEST="Compile and run test_lib.c to verify the install? [Y/n] "
if /i "!RUN_TEST!" neq "n" (
    echo [Step 4/4] Compiling and running the test program ...
    gcc test_lib.c -lmylib -o test_lib.exe
    if errorlevel 1 (
        echo [ERROR] Test program failed to compile. See messages above.
    ) else (
        test_lib.exe
        echo.
        if errorlevel 1 (
            echo [NOTE] Test program exited with an error. Check output above.
        ) else (
            echo [OK] Test passed. The library works from anywhere.
        )
    )
)

echo ========================================
echo [DONE] Installation finished.
echo From now on, in any C program you can write:
echo   #include ^<utils.h^>
echo   #include ^<multifunc.h^>
echo Compile with:  gcc your_program.c -lmylib -o program
echo ========================================
pause