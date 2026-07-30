@echo off
setlocal
cd /d "%~dp0.."
echo [1/5] Instalando ferramentas de empacotamento no computador principal...
python -m pip install --upgrade pip pyinstaller openpyxl
if errorlevel 1 goto erro

echo [2/5] Limpando pacote anterior...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [3/5] Gerando executavel portatil...
cd portable_real
python -m PyInstaller PortalPGP.spec --noconfirm
if errorlevel 1 goto erro

echo [4/5] Montando pasta final...
set DEST=..\dist\Portal_Gestao_Parcerias_Portatil
if exist "%DEST%" rmdir /s /q "%DEST%"
mkdir "%DEST%\sistema"
mkdir "%DEST%\dados\media"
mkdir "%DEST%\logs"
mkdir "%DEST%\backups"
xcopy /e /i /y "dist\PortalPGP\*" "%DEST%\" >nul
xcopy /e /i /y "..\apps" "%DEST%\sistema\apps" >nul
xcopy /e /i /y "..\gestao_rh" "%DEST%\sistema\gestao_rh" >nul
xcopy /e /i /y "..\templates" "%DEST%\sistema\templates" >nul
xcopy /e /i /y "..\static" "%DEST%\sistema\static" >nul
copy /y "..\manage.py" "%DEST%\sistema\manage.py" >nul
if exist "..\db.sqlite3" copy /y "..\db.sqlite3" "%DEST%\dados\db.sqlite3" >nul
if exist "..\media" xcopy /e /i /y "..\media" "%DEST%\dados\media" >nul
copy /y "iniciar_portal.bat" "%DEST%\iniciar_portal.bat" >nul
copy /y "fazer_backup.bat" "%DEST%\fazer_backup.bat" >nul
copy /y "LEIA-ME-PORTATIL.txt" "%DEST%\LEIA-ME-PORTATIL.txt" >nul

echo [5/5] Concluido.
echo Copie a pasta abaixo para o pendrive:
echo %CD%\%DEST%
pause
exit /b 0
:erro
echo [ERRO] Nao foi possivel gerar o pacote portatil.
pause
exit /b 1
