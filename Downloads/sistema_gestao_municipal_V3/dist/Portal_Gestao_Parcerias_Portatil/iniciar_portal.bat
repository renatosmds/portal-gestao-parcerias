@echo off
cd /d "%~dp0"
PortalPGP.exe
if errorlevel 1 pause
