@echo off
cd /d %~dp0
python manage.py check
if errorlevel 1 pause & exit /b 1
python manage.py runserver
