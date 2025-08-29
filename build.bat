@echo off
setlocal EnableDelayedExpansion

:: ---------------- Настройки ----------------
set PY310=C:\Users\danila\AppData\Local\Programs\Python\Python310
set MPRESS=C:\mpress\mpress.exe

set ROOT=%~dp0
pushd %ROOT%

set BUILD=build
set DIST=dist
set OBFUSCATED=build\obf

:: ---------------- Создание папок ----------------
if not exist "%BUILD%" mkdir "%BUILD%"
if not exist "%DIST%" mkdir "%DIST%"
if not exist "%OBFUSCATED%" mkdir "%OBFUSCATED%"

:: ---------------- Обфускация через PyArmor ----------------
echo [*] Obfuscating Python sources with PyArmor...
%PY310%\python.exe -m pyarmor obfuscate --recursive --output %OBFUSCATED% main.py domain\ util\ elements\ services\ ui\views\

:: ---------------- Cythonize main.py ----------------
echo [*] Cythonizing main.py...
%PY310%\python.exe -m cython --embed %OBFUSCATED%\main.py -o %BUILD%\main.c

:: ---------------- Cythonize модули ----------------
echo [*] Cythonizing modules...
for %%f in (
    %OBFUSCATED%\domain\*.py
    %OBFUSCATED%\domain\parserManager\*.py
    %OBFUSCATED%\domain\styleManager\*.py
    %OBFUSCATED%\domain\wordManager\*.py
    %OBFUSCATED%\elements\*.py
    %OBFUSCATED%\services\*.py
    %OBFUSCATED%\ui\views\*.py
    %OBFUSCATED%\util\*.py
) do (
    %PY310%\python.exe -m cython %%f -o %BUILD%\%%~nxf.c
)

:: ---------------- Компиляция через MSVC ----------------
echo [*] Compile all .c files with MSVC...
set C_FILES=
for %%f in (%BUILD%\*.c) do (
    set C_FILES=!C_FILES! %%f
)

cl !C_FILES! /Fe:%DIST%\main.exe /I %PY310%\include %PY310%\libs\python310.lib /O2 /MD

if %ERRORLEVEL% NEQ 0 (
    echo [!] Build failed
    exit /b 1
)

:: ---------------- Упаковка MPRESS ----------------
echo [*] Pack with MPRESS...
"%MPRESS%" -s -m -b "%DIST%\main.exe"

:: ---------------- Расчёт SHA256 ----------------
echo [*] Calc SHA256 (post-pack)...
for /f "tokens=2" %%h in ('powershell -Command "Get-FileHash ''%DIST%\main.exe'' -Algorithm SHA256 ^| Select-Object -ExpandProperty Hash"') do (
    set HASH=%%h
)

:: ---------------- Отправка хэша на сервер ----------------
echo [*] Sending exe hash to server...
%PY310%\python.exe -c "import requests, os; headers={'X-Admin-Key': os.environ.get('ADMIN_KEY','changeme_admin_key')}; r=requests.post('https://your-server.example/admin/upload_hash', json={'exe_hash':'%HASH%','version':'v1.0.0'}, headers=headers); print(r.text)"

echo [*] Build finished
popd
endlocal
pause
