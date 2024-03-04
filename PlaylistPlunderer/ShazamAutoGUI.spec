# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ShazamAutoGUI.py'],
    pathex=[],
    binaries=[],
    datas=[('resources', 'resources'), ('shazam_automation.py', '.')],
    hiddenimports=['webdriver_manager'],
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
    a.binaries,
    a.datas,
    [],
    name='ShazamAutoGUI',
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
    icon=['appicondesk.icns'],
)
app = BUNDLE(
    exe,
    name='ShazamAutoGUI.app',
    icon='appicondesk.icns',
    bundle_identifier=None,
)
