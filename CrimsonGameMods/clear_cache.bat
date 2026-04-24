@echo off
cd /d "%~dp0"
echo Clearing __pycache__...
for /d /r %%i in (__pycache__) do @if exist "%%i" rd /s /q "%%i"
echo Done.
pause
