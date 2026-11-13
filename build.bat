@echo off
pyinstaller --onefile --windowed ^
  --name "Wand Patcher" ^
  --icon "icon.ico" ^
  --add-data "music.mp3;." ^
  --collect-all pygame ^
  --hidden-import music_player ^
  app.py
