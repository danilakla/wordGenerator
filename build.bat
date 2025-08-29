@echo off
setlocal EnableDelayedExpansion

set PY311=C:\Users\danila\AppData\Local\Programs\Python\Python310
set MPRESS=C:\mpress\mpress.exe

set ROOT=%~dp0
pushd %ROOT%

set BUILD=build
set DIST=dist

if not exist "%BUILD%" mkdir "%BUILD%"
if not exist "%DIST%" mkdir "%DIST%"

echo [*] Cythonize main.py
%PY311%\python.exe -m cython --embed main.py -o %BUILD%\main.c

echo [*] Cythonize modules
for %%f in (
    domain\*.py
    domain\parserManager\*.py
    domain\styleManager\*.py
    domain\wordManager\*.py
    elements\*.py
    services\*.py
    ui\views\*.py
    util\*.py
) do (
    %PY311%\python.exe -m cython %%f -o %BUILD%\%%~nxf.c
)

echo [*] Compile all .c files with MSVC
set C_FILES=
for %%f in (%BUILD%\*.c) do (
    set C_FILES=!C_FILES! %%f
)

cl !C_FILES! /Fe:%DIST%\main.exe /I %PY311%\include %PY311%\libs\python310.lib /O2 /MD

if %ERRORLEVEL% NEQ 0 (
    echo [!] Build failed
    exit /b 1
)

echo [*] Pack with MPRESS
"%MPRESS%" -s -m -b "%DIST%\main.exe"

echo [*] Calc SHA256 (post-pack)
for /f "tokens=2" %%h in ('powershell -Command "Get-FileHash ''%DIST%\main.exe'' -Algorithm SHA256 ^| Select-Object -ExpandProperty Hash"') do (
    set HASH=%%h
)

echo [*] Writing config_hash.py
echo EXPECTED_HASH = "%HASH%" > %ROOT%\config_hash.py

echo [*] Build finished
popd
endlocal
pause
