## pyinstaller no icon 

```
pyinstaller -F -w -i apple.ico futures.py --noconsole
```



## pyinstaller add icon

- ### Change if.py like this

```python
+def resource_path(relative_path):
+    """ Get absolute path to resource, works for dev and for PyInstaller """
+    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
+    return os.path.join(base_path, relative_path)
+
 def main():
     app = wx.App(False)
     frame = wx.Frame(None, 100, '期指合约', size = wx.Size(1400, int(1200*0.618)))
-    icon = wx.Icon('apple.ico', wx.BITMAP_TYPE_ICO)
+    iconPath = 'apple.ico'
+    iconPath= resource_path(iconPath)
+    icon = wx.Icon(iconPath, wx.BITMAP_TYPE_ICO)
     frame.SetIcon(icon)

```

- ### generate spec file

```shell
pyi-makespec -F -w futures.py
```

​	-F to generate only one file

​	-w not show window when running

​	this will generate futures.spec file like this

```python
# -*- mode: python -*-

block_cipher = None

a = Analysis(['futures.py'],
             pathex=['D:\files\pkg'], # file path
             binaries=[],
             datas=[], # where to change
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='futures',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )

```

- ### modify futures.spec

​		change

```python
"datas=[],"
```

​		to

```python
"datas=[('apple.ico','.')],"
```

- ### run pyinstaller

```shell
pyinstaller -F -w -i apple.ico futures.spec --noconsole
```

​	-i  apple.ico : to use apple.ico also as the Taskbar icon



