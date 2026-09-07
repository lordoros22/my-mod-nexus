# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

# Encontra onde o pacote vosk está instalado no Python para copiar a pasta inteira
import vosk
vosk_path = os.path.dirname(vosk.__file__)

datas = [(vosk_path, 'vosk')] # Força a inclusão da pasta física do vosk em _internal/vosk
binaries = []
hiddenimports = ['vgamepad', 'vosk', 'sounddevice', 'tkinter', 'json']

tmp_ret = collect_all('vgamepad')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

tmp_ret = collect_all('vosk')
datas += tmp_ret[0]; binaries += tmp_ret[1]

a = Analysis(
    ['bot.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='bot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='bot',
)