@echo off
setlocal
cd /d "%~dp0"
for /f "tokens=1-4 delims=/ " %%a in ("%date%") do set DT=%%d-%%b-%%c
set TM=%time:~0,2%-%time:~3,2%-%time:~6,2%
set TM=%TM: =0%
set DEST=backups\backup_%DT%_%TM%
mkdir "%DEST%\media"
copy /y "dados\db.sqlite3" "%DEST%\db.sqlite3" >nul
xcopy /e /i /y "dados\media" "%DEST%\media" >nul
echo Backup criado em %DEST%
pause
