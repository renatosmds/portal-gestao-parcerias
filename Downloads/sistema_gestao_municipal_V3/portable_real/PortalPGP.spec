# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = [], [], []
for pacote in ["django", "rest_framework", "whitenoise", "allauth", "grappelli", "bootstrapform", "openpyxl"]:
    d, b, h = collect_all(pacote)
    datas += d; binaries += b; hiddenimports += h

a = Analysis(["portal_launcher.py"], pathex=[], binaries=binaries, datas=datas, hiddenimports=hiddenimports,
             hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="PortalPGP", debug=False, bootloader_ignore_signals=False,
          strip=False, upx=True, console=True, disable_windowed_traceback=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=True, upx_exclude=[], name="PortalPGP")
