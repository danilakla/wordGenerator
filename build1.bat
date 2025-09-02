@echo off
REM ====== CONFIGURATION ======
set PYTHON_PATH=C:\Users\danila\AppData\Local\Programs\Python\Python310\python.exe
set MAIN_SCRIPT=main.py
set DIST_DIR=dist_full
set BUILD_DIR=build
set REQ=requirements.txt

REM ====== PREPARE ENV ======
echo [1/5] Installing dependencies...
"%PYTHON_PATH%" -m pip install --upgrade pip
"%PYTHON_PATH%" -m pip install -r %REQ%
"%PYTHON_PATH%" -m pip install nuitka

REM ====== CLEAN OLD BUILD ======
echo [2/5] Cleaning old build...
if exist %DIST_DIR% rmdir /s /q %DIST_DIR%
if exist %BUILD_DIR% rmdir /s /q %BUILD_DIR%

REM ====== BUILD WITH NUITKA ======
echo [3/5] Building executable with Nuitka...
"%PYTHON_PATH%" -m nuitka ^
  --standalone ^
  --onefile ^
  --enable-plugin=pylint-warnings ^
  --nofollow-import-to=PySide6 ^
  --enable-plugin=pyqt6 ^
  --include-plugin-directory=domain ^
  --include-plugin-directory=elements ^
  --include-plugin-directory=services ^
  --include-plugin-directory=ui\views ^
  --include-plugin-directory=util ^
  --include-data-dir=resource=resource ^
  --output-dir=%DIST_DIR% ^
  %MAIN_SCRIPT%

REM ====== COPY EXTRA FILES ======
echo [4/5] Copying extra dependencies...
xcopy /E /I /Y hwid_validate.pyd %DIST_DIR%\

REM ====== DONE ======
echo [5/5] Build complete! Files are in %DIST_DIR%
pause
