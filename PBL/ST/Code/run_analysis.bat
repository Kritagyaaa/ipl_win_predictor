@echo off
setlocal

cd /d "%~dp0"

set "RSCRIPT="
where Rscript >nul 2>&1
if %errorlevel%==0 set "RSCRIPT=Rscript"

if not defined RSCRIPT if exist "C:\Program Files\R\R-4.5.3\bin\Rscript.exe" set "RSCRIPT=C:\Program Files\R\R-4.5.3\bin\Rscript.exe"
if not defined RSCRIPT if exist "C:\Program Files\R\R-4.5.3\bin\x64\Rscript.exe" set "RSCRIPT=C:\Program Files\R\R-4.5.3\bin\x64\Rscript.exe"

if not defined RSCRIPT (
  echo [ERROR] Rscript not found.
  echo Install R or add Rscript to PATH.
  exit /b 1
)

echo Running R analysis...
"%RSCRIPT%" "r_code\analysis.r"
if errorlevel 1 (
  echo [ERROR] R analysis failed.
  exit /b %errorlevel%
)

echo [OK] R analysis completed.
echo Outputs: r_code\scatter_plot.png and r_code\residual_plot.png
pause
exit /b 0
