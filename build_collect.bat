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



echo [*] Копируем ресурсы
if exist "%ROOT%resource" (
    xcopy "%ROOT%resource" "%DIST_FULL%\resource" /E /I /Y >nul
)

REM --- Явно копируем необходимые библиотеки ---
set "LIBS=PySide6 docx docxtpl dependency_injector PIL lxml dateutil latex2mathml PyQt6 PyMuPDF pymupdf docx2pdf mathml_to_latex cryptography"

for %%L in (%LIBS%) do (
    if exist "%PYTHONPATH%\Lib\site-packages\%%L" (
        echo [*] Копируем библиотеку %%L
        xcopy "%PYTHONPATH%\Lib\site-packages\%%L" "%DIST_FULL%\%%L" /E /I /Y >nul
    ) else (
        echo [!] Библиотека %%L не найдена
    )
)

REM --- Чистим исходники .py, оставляем только бинарники ---
echo [*] Чистим .py исходники
for /r "%DIST_FULL%" %%f in (*.py) do (
    del "%%f" >nul 2>&1
)

REM --- Удаляем __pycache__ ---
echo [*] Удаляем __pycache__
for /d /r "%DIST_FULL%" %%d in (__pycache__) do (
    rd /s /q "%%d" 2>nul
)

echo [*] dist_full готов
endlocal
pause
