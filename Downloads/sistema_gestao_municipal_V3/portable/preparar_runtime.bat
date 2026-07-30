@echo off
setlocal
cd /d "%~dp0.."
where py >nul 2>nul
if errorlevel 1 (
  echo [ERRO] O Python Launcher nao foi encontrado neste computador.
  echo Instale Python 3.13 ou 3.14 apenas para preparar o runtime uma vez.
  pause
  exit /b 1
)
if exist runtime rmdir /s /q runtime
py -3 -m venv runtime
if errorlevel 1 goto erro
runtime\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
runtime\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto erro
runtime\Scripts\python.exe manage.py collectstatic --noinput --clear
if errorlevel 1 goto erro
if not exist dados mkdir dados
if not exist dados\media mkdir dados\media
if exist db.sqlite3 if not exist dados\db.sqlite3 copy /y db.sqlite3 dados\db.sqlite3 >nul
if exist media xcopy media dados\media /E /I /Y >nul
copy /y .env.example .env.portatil >nul

echo.
echo Runtime preparado. Copie esta pasta para o pendrive e use portable\iniciar_portal.bat.
pause
exit /b 0
:erro
echo [ERRO] Nao foi possivel preparar o runtime portatil.
pause
exit /b 1
