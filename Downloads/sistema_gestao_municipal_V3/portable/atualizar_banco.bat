@echo off
setlocal
cd /d "%~dp0.."
set "PYTHON=%CD%\runtime\Scripts\python.exe"
if not exist "%PYTHON%" (
 echo Runtime nao encontrado.
 pause
 exit /b 1
)
set "PGP_DATA_DIR=%CD%\dados"
"%PYTHON%" manage.py check
if errorlevel 1 pause & exit /b 1
"%PYTHON%" manage.py migrate
pause
