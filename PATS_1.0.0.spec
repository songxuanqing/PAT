# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['–key=novarandnovarand', 'main.py'],
    pathex=[],
    binaries=[('OpenAPISetup.exe', '.')],
    datas=[('star-yellow.png', '.'), ('star-blank.png', '.'), ('pigicon.ico', '.'), ('main.ui', '.'), ('register_ai_condition.ui', '.'), ('register_dao_condition.ui', '.'), ('register_kiwoom_condition.ui', '.'), ('main.ui', '.'), ('searchCode.ui', '.'), ('setting_piggle_dao_most_voted.ui', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PATS_1.0.0',
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
    icon=['pigicon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PATS_1.0.0',
)
