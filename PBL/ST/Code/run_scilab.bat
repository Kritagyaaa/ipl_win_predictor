@echo off
setlocal EnableDelayedExpansion

cd /d "%~dp0"

set "SCILAB="
if exist "C:\Program Files\scilab-2026.0.1\bin\WScilex-cli.exe" (
  set "SCILAB=C:\Program Files\scilab-2026.0.1\bin\WScilex-cli.exe"
) else if exist "C:\Program Files\scilab-2025.0.0\bin\WScilex-cli.exe" (
  set "SCILAB=C:\Program Files\scilab-2025.0.0\bin\WScilex-cli.exe"
)

if not defined SCILAB (
  echo [ERROR] Scilab CLI not found at expected location.
  echo Install Scilab to: C:\Program Files\scilab-2026.0.1
  pause
  exit /b 1
)

echo Running Scilab script...
echo.
start "" /wait "!SCILAB!" -nb -f "scilab_code\matrix_solver.sce"
echo.
echo [OK] Scilab script completed.
pause
exit /b 0
