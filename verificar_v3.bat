@echo off
cd /d %~dp0
python manage.py check
python -m compileall apps gestao_rh home
pause
