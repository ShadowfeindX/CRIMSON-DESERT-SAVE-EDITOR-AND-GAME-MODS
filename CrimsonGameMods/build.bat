@echo off
cd /d "%~dp0"
echo Clearing caches...
for /d /r %%i in (__pycache__) do @if exist "%%i" rd /s /q "%%i"
if exist build rd /s /q build
if exist dist\CrimsonGameMods.exe del /f dist\CrimsonGameMods.exe
echo Building...
python -m PyInstaller CrimsonGameMods.spec --noconfirm
echo.
echo Done. Output: dist\CrimsonGameMods.exe
pause
