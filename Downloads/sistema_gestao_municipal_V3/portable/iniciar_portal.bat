@echo off
setlocal
cd /d "%~dp0.."
set "ROOT=%CD%"
set "PYTHON=%ROOT%\runtime\Scripts\python.exe"
if not exist "%PYTHON%" (
  echo [ERRO] Runtime portatil nao encontrado.
  echo Execute primeiro portable\preparar_runtime.bat neste computador.
  pause
  exit /b 1
)
if not exist "%ROOT%\dados" mkdir "%ROOT%\dados"
if not exist "%ROOT%\dados\media" mkdir "%ROOT%\dados\media"
if not exist "%ROOT%\logs" mkdir "%ROOT%\logs"
set "PGP_DATA_DIR=%ROOT%\dados"
set "DEBUG=True"
set "ALLOWED_HOSTS=127.0.0.1,localhost"
"%PYTHON%" manage.py migrate --noinput
"%PYTHON%" manage.py collectstatic --noinput --clear
start "" http://127.0.0.1:8000/
"%PYTHON%" manage.py runserver 127.0.0.1:8000
endlocal
