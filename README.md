# 🔋 Battery Monitor

**Smart Windows tray app to alert you on low or full battery — built with Python and Claude AI.**

[![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-blue?logo=windows)](https://www.microsoft.com/windows/) [![Python](https://img.shields.io/badge/Python-3.x-green?logo=python)](https://python.org) [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features
- 📉 Alerts on low (default: 20%) and full battery (default: 90%)
- 🖥️ System tray icon with battery % and status
- ⚙️ Settings: thresholds, alert sounds (WAV), check interval
- 🚀 Auto-start with Windows
- 🎛️ Easy GUI via tray menu and settings window

## 📦 Installation
### 🔹 Download EXE
1. Download from [Releases](../../releases)
2. Run `BatteryMonitor.exe`
3. Optional: Place sound file at `D:\Battery Alarm\siren-alert.wav`

### 🔹 Build from Source
```bash
pip install psutil pystray pillow pyinstaller
git clone https://github.com/talhamansoor786/battery-monitor
cd battery-monitor
pyinstaller --onefile --noconsole battery_monitor.py
```

## 🧠 Usage
- Launch → Tray icon appears
- Right-click → Open settings, toggle startup, pause, exit
- Left-click → Show battery status

## 🔧 Configuration
Settings saved in `battery_config.json`:
```json
{
  "alarm_sound": "D:\\Battery Alarm\\siren-alert.wav",
  "low_threshold": 20,
  "high_threshold": 90,
  "check_interval": 60,
  "auto_startup": false
}
```

## 📁 Project Structure
- `battery_monitor.py`: Main script  
- `build_exe.bat`: Build helper  
- `battery_config.json`: User settings  
- `Battery Alarm/`: Custom sound folder  

## 🛠 Built With
- Python, psutil, pystray, Pillow, tkinter, PyInstaller

## 📃 License
MIT – free for personal and commercial use.
