# Building from Source

This document records the Windows PyInstaller command used to build the project.

Run in **Windows Command Prompt** from the project directory, with Python, PyInstaller, and the required project dependencies installed:

```bat
pyinstaller --onefile --windowed ^
  --name "Wand Patcher" ^
  --icon "icon.ico" ^
  --add-data "music.mp3;." ^
  --collect-all pygame ^
  --hidden-import music_player ^
  app.py
```

The command expects `app.py`, `icon.ico`, `music.mp3`, and the `music_player` module to be available at their existing paths. The generated executable is placed in `dist/` by default.

The precise dependency versions have not been provided. Document the tested Python, pygame, and PyInstaller versions once known.
