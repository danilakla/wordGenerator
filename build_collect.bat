@echo off
setlocal

set "ROOT=%~dp0"
set "DIST=%ROOT%dist"
set "DIST_FULL=%ROOT%dist_full"
set "PYTHONPATH=C:\Users\danila\AppData\Local\Programs\Python\Python310"

if exist "%DIST_FULL%" rmdir /s /q "%DIST_FULL%"
mkdir "%DIST_FULL%"

echo [*] Копируем main.exe
if exist "%DIST%\main.exe" copy "%DIST%\main.exe" "%DIST_FULL%\" >nul

for %%d in (domain elements services ui util resource) do (
    if exist "%ROOT%%%d" (
        echo [*] Копируем %%d
        xcopy "%ROOT%%%d" "%DIST_FULL%\%%d" /E /I /Y >nul
    )
)

if exist "%ROOT%config_hash.py" (
    echo [*] Копируем config_hash.py
    copy "%ROOT%config_hash.py" "%DIST_FULL%\" >nul
)

REM --- Явно копируем библиотеки ---
set "LIBS=PySide6 docx docxtpl dependency_injector PIL lxml dateutil latex2mathml PyQt6 PyMuPDF pymupdf docx2pdf mathml_to_latex cryptography"

for %%L in (%LIBS%) do (
    if exist "%PYTHONPATH%\Lib\site-packages\%%L" (
        echo [*] Копируем библиотеку %%L
        xcopy "%PYTHONPATH%\Lib\site-packages\%%L" "%DIST_FULL%\%%L" /E /I /Y >nul
    ) else (
        echo [!] Библиотека %%L не найдена
    )
)

REM --- Удаляем __pycache__, подавляем ошибки ---
echo [*] Удаляем __pycache__
for /d /r "%DIST_FULL%" %%d in (__pycache__) do (
    rd /s /q "%%d" 2>nul
)

echo [*] dist_full готов
endlocal
pause
