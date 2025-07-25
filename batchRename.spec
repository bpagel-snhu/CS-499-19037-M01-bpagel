# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.building.build_main import Analysis
from PyInstaller.building.api import PYZ, EXE
from PyInstaller.utils.hooks import collect_all
import os
import sys

# Cross-platform icon selection
if sys.platform == "win32":
    icon_file = os.path.join('batch_renamer', 'ui', 'assets', 'batchRename.ico')
elif sys.platform == "darwin":
    icon_file = os.path.join('batch_renamer', 'ui', 'assets', 'batchRename.icns')
else:
    icon_file = None  # No icon for other platforms

datas = []
binaries = []
hiddenimports = []
tmp_ret = collect_all('batch_renamer')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
# Explicitly add UI asset files
assets_dir = os.path.join('batch_renamer', 'ui', 'assets')
datas += [
    (os.path.join(assets_dir, 'batchRename.ico'), assets_dir),
    (os.path.join(assets_dir, 'batchRename.icns'), assets_dir),
    (os.path.join(assets_dir, 'RB Barron Pagel - No BG.png'), assets_dir),
]


a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BP File Utilities',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,  # Use the platform-specific icon
)
