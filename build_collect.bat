@echo off
setlocal EnableDelayedExpansion

REM ------------------------
REM Параметры
REM ------------------------
set "ROOT=%~dp0"
set "DIST=%ROOT%dist"
set "DIST_FULL=%ROOT%dist_full"
set "PYTHONPATH=C:\Users\danila\AppData\Local\Programs\Python\Python310"

REM ------------------------
REM Очистка dist_full
REM ------------------------
if exist "%DIST_FULL%" rmdir /s /q "%DIST_FULL%"
mkdir "%DIST_FULL%"

REM ------------------------
REM Копируем готовый exe
REM ------------------------
if exist "%DIST%\main.exe" copy "%DIST%\main.exe" "%DIST_FULL%\" >nul

REM ------------------------
REM Копируем ресурсы
REM ------------------------
if exist "%ROOT%resource" (
    xcopy "%ROOT%resource" "%DIST_FULL%\resource" /E /I /Y >nul
)

REM ------------------------
REM Копируем библиотеки
REM ------------------------
set "LIBS=PySide6 docx docxtpl dependency_injector PIL lxml dateutil latex2mathml PyQt6 PyMuPDF pymupdf docx2pdf mathml_to_latex cryptography"

for %%L in (%LIBS%) do (
    if exist "%PYTHONPATH%\Lib\site-packages\%%L" (
        echo [*] Копируем библиотеку %%L
        xcopy "%PYTHONPATH%\Lib\site-packages\%%L" "%DIST_FULL%\%%L" /E /I /Y >nul
    ) else (
        echo [!] Библиотека %%L не найдена
    )
)

REM ------------------------
REM Удаляем исходники .py
REM ------------------------
echo [*] Удаляем все .py файлы
for /r "%DIST_FULL%" %%f in (*.py) do (
    del "%%f" >nul 2>&1
)

REM ------------------------
REM Удаляем __pycache__
REM ------------------------
echo [*] Удаляем __pycache__ директории
for /d /r "%DIST_FULL%" %%d in (__pycache__) do (
    rd /s /q "%%d" 2>nul
)

REM ------------------------
REM dist_full готов
REM ------------------------
echo [*] dist_full готов
endlocal
pause
