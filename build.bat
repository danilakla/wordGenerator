@echo off
setlocal EnableDelayedExpansion

:: ---------------- Настройки ----------------
set "PY310=C:\Users\danila\AppData\Local\Programs\Python\Python310"
set "MPRESS=C:\mpress\mpress.exe"

set "ROOT=%~dp0"
pushd "%ROOT%"

set BUILD=build
set DIST=dist

:: ---------------- Создание папок ----------------
if not exist "%BUILD%" mkdir "%BUILD%"
if not exist "%DIST%" mkdir "%DIST%"

:: ---------------- Копируем hwid_validate.pyd ----------------
if exist hwid_validate.pyd copy hwid_validate.pyd "%DIST%\" >nul 2>&1

:: ---------------- Cythonize main.py ----------------
echo [*] Cythonizing main.py...
"%PY310%\python.exe" -m cython --embed -3 main.py -o "%BUILD%\main.c"

:: ---------------- Компиляция main.exe ----------------
echo [*] Compile main.exe with MSVC...
cl "%BUILD%\main.c" /Fe:"%DIST%\main.exe" /I "%PY310%\include" "%PY310%\libs\python310.lib" /O2 /MD
if %ERRORLEVEL% NEQ 0 (
    echo [!] Main build failed
    exit /b 1
)

:: ---------------- Cythonize + compile modules to .pyd ----------------
echo [*] Building modules as .pyd...
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
    echo [*] Compiling %%f

    :: Получаем относительный путь каталога
    set "REL_DIR=%%~dpf"
    set "REL_DIR=!REL_DIR:%ROOT%=!"
    set "TARGET_DIR=%DIST%\!REL_DIR!"

    if not exist "!TARGET_DIR!" mkdir "!TARGET_DIR!"

    "%PY310%\python.exe" -m cython -3 "%%f" -o "%BUILD%\%%~nxf.c"
    cl /LD "%BUILD%\%%~nxf.c" /Fe:"!TARGET_DIR!\%%~nf.pyd" /I "%PY310%\include" "%PY310%\libs\python310.lib" /O2 /MD

    if !ERRORLEVEL! NEQ 0 (
        echo [!] Failed to compile %%f
        exit /b 1
    )

    :: добавляем пустой __init__.py (если нет)
    if not exist "!TARGET_DIR!\__init__.py" echo. > "!TARGET_DIR!\__init__.py"
)

:: ---------------- Упаковка MPRESS ----------------
echo [*] Pack main.exe with MPRESS...
"%MPRESS%" -s -m -b "%DIST%\main.exe"

:: ---------------- Расчёт SHA256 ----------------
echo [*] Calc SHA256 (post-pack)...
set "HASH="
for /f "tokens=2" %%h in ('powershell -Command "Get-FileHash ''%DIST%\main.exe'' -Algorithm SHA256 ^| Select-Object -ExpandProperty Hash"') do (
    set "HASH=%%h"
)
echo [*] SHA256: !HASH!

:: ---------------- Отправка хэша на сервер ----------------
echo [*] Sending exe hash to server...
"%PY310%\python.exe" -c "import requests; headers={'X-Admin-Key': 'VerySecretAdminKeyHere'}; r=requests.post('https://93.125.104.173:8444/admin/upload_hash', json={'exe_hash':'!HASH!','version':'v1.1.0'}, headers=headers, verify=False); print(r.text)"

echo [*] Build finished
popd
endlocal
pause
