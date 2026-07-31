#!/bin/bash

source venv/bin/activate
cd /home/ubuntu/sistema-gestao-municipal
git pull
pip install -r requirements.txt
python manage.py migrate
sudo systemctl restart gestao_rh.service

