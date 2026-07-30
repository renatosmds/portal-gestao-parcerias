import os
import sys
import threading
import time
import webbrowser
from pathlib import Path


def raiz_execucao():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]

ROOT = raiz_execucao()
SYSTEM_DIR = ROOT / "sistema"
DATA_DIR = ROOT / "dados"
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / "media").mkdir(exist_ok=True)
(ROOT / "logs").mkdir(exist_ok=True)
(ROOT / "backups").mkdir(exist_ok=True)

os.chdir(SYSTEM_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gestao_rh.settings")
os.environ["PGP_DATA_DIR"] = str(DATA_DIR)
os.environ.setdefault("DEBUG", "False")
os.environ.setdefault("ALLOWED_HOSTS", "127.0.0.1,localhost")

from django.core.management import call_command, execute_from_command_line

call_command("migrate", interactive=False, verbosity=1)
call_command("collectstatic", interactive=False, clear=False, verbosity=0)

threading.Thread(target=lambda: (time.sleep(2), webbrowser.open("http://127.0.0.1:8000/")), daemon=True).start()
execute_from_command_line(["manage.py", "runserver", "127.0.0.1:8000", "--noreload"])
