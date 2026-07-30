@echo off
setlocal
cd /d "%~dp0.."
if not exist backups mkdir backups
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set DATA=%%d-%%b-%%c
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set HORA=%%a%%b
set "DEST=backups\backup_%DATA%_%HORA%"
mkdir "%DEST%"
if exist dados\db.sqlite3 copy /y dados\db.sqlite3 "%DEST%\db.sqlite3" >nul
if exist dados\media xcopy dados\media "%DEST%\media" /E /I /Y >nul
echo Backup criado em %DEST%
pause
