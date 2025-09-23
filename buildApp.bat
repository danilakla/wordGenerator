@echo off
REM ====== CONFIGURATION ======
set PYTHON_PATH=C:\Users\danila\AppData\Local\Programs\Python\Python310\python.exe
set MAIN_SCRIPT=main.py
set DIST_DIR=dist_full
set BUILD_DIR=build
set REQ=requirements.txt
set TARGET_EXE=main.exe
set VERSION=1.0.0
set SERVER_URL=https://93.125.104.173:8444/admin/upload_hash
set ADMIN_KEY=VerySecretAdminKeyHere

REM ====== PREPARE ENV ======
echo [1/7] Installing dependencies...
"%PYTHON_PATH%" -m pip install --upgrade pip
"%PYTHON_PATH%" -m pip install -r %REQ%
"%PYTHON_PATH%" -m pip install nuitka
"%PYTHON_PATH%" -m pip uninstall PySide6 -y  


REM ====== CLEAN OLD BUILD ======
echo [2/7] Cleaning old build...
if exist %DIST_DIR% rmdir /s /q %DIST_DIR%
if exist %BUILD_DIR% rmdir /s /q %BUILD_DIR%

REM ====== BUILD WITH NUITKA ======
echo [3/7] Building executable with Nuitka...
"%PYTHON_PATH%" -m nuitka ^
  --mingw64 ^
  --standalone ^
  --onefile ^
  --lto=no ^
  --enable-plugin=pylint-warnings ^
  --nofollow-import-to=PySide6,pandas,numpy,scipy ^
  --enable-plugin=pyqt6 ^
  --include-data-dir="D:\projects\demo\wordGenerator\.venv\Lib\site-packages\latex2mathml=latex2mathml" ^
  --include-plugin-directory=domain ^
  --include-plugin-directory=elements ^
  --include-plugin-directory=services ^
  --include-plugin-directory=ui\views ^
  --include-plugin-directory=util ^
  --output-dir=%DIST_DIR% ^
  %MAIN_SCRIPT%


REM ====== COPY EXTRA FILES ======
echo [4/7] Copying extra dependencies...
xcopy /E /I /Y cpuid.dll %DIST_DIR%\
xcopy /E /I /Y resource %DIST_DIR%\resource\

REM ====== CALCULATE HASH ======
echo [5/7] Calculating SHA256 hash...
for /f "tokens=* usebackq" %%h in (`powershell -command "(Get-FileHash '%DIST_DIR%\%TARGET_EXE%' -Algorithm SHA256).Hash.ToLower()"`) do set FILE_HASH=%%h
echo Hash: %FILE_HASH%


REM ====== SEND HASH TO SERVER ======
echo [6/7] Sending hash to server...
curl -k -X POST "%SERVER_URL%" ^
  -H "X-Admin-Key: %ADMIN_KEY%" ^
  -H "Content-Type: application/json" ^
  -d "{\"exe_hash\": \"%FILE_HASH%\", \"version\": \"%VERSION%\"}"



REM ====== DONE ======
echo [7/7] Build complete! Files are in %DIST_DIR%
pause
