# AutoKeymap  

> Zero-config, game-grade latency Android key/mouse remapper  
> Powered by Python + ADB + Tkinter + pynput

---

## Features
| Feature | Status |
|---|---|
| Real-time key/mouse mapping | ✅ |
| GUI coordinate picker | ✅ |
| Custom hotkeys | ✅ |
| Right-click to unbind | ✅ |
| Global clear (Ctrl+W+C) | ✅ |
| Auto-scaled screenshots | ✅ |
| Game-grade latency | ✅ |

---

## Download & Run
1. **Prerequisites**
   ```bash
   pip install pillow pynput
   adb --version   # ensure adb is in PATH
   ```

2. **Connect Device**
   ```bash
   adb devices               # USB
   adb tcpip 5555            # Wi-Fi
   adb connect <phone-ip>:5555
   ```

3. **Launch**
   ```bash
   python main.py            # source
   # OR
   dist/main.exe             # single-file binary
   ```

---

## Quick Start
1. Click **Refresh Screen** → load live phone/emulator view  
2. Left-click **any on-screen button** → press the key/mouse button you want to bind  
3. Right-click **red cross** or **list item** → remove binding  
4. Press **Ctrl+W+C** → confirm → wipe all mappings  
5. Click **Start Listening** → minimize window → enjoy game-grade latency  

---

## Config File
Auto-generated `config.json` example:

```json
{
  "w": {"type": "tap", "x": 500, "y": 1500},
  "space": {"type": "tap", "x": 600, "y": 1600}
}
```

---

## Build Command
```bash
pyinstaller main.py -F -c --distpath dist --workpath build --specpath build
```

---
