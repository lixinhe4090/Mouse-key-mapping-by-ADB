# AutoKeymap  
#Chinese（中文）

> 零配置、游戏级延迟的 Android 键鼠映射工具  
> 基于 Python + ADB + Tkinter + pynput

---

## 功能一览
| 功能 | 状态 |
|---|---|
| 实时键鼠映射 | ✅ |
| 图形化坐标拾取 | ✅ |
| 自定义热键 | ✅ |
| 右键删除绑定 | ✅ |
| 全局清屏 (Ctrl+W+C) | ✅ |
| 自适应缩放截图 | ✅ |
| 游戏级延迟 | ✅ |

---

## 下载与运行
1. **环境准备**
   ```bash
   pip install pillow pynput
   adb --version   # 确保 adb 已加入 PATH
   ```

2. **连接设备**
   ```bash
   adb devices               # USB
   adb tcpip 5555            # WiFi
   adb connect <手机IP>:5555
   ```

3. **启动程序**
   ```bash
   python main.py            # 源码
   # 或
   dist/main.exe             # 打包后单文件
   ```

---

## 快速上手
1. 点击 **刷新屏幕** → 载入手机/模拟器实时画面  
2. 左键单击 **游戏按钮** → 立即按下想要绑定的 **键盘/鼠标键**  
3. 右键点击 **红色十字** 或 **列表条目** → 删除绑定  
4. 按 **Ctrl+W+C** → 弹窗确认 → 一键清空全部配置  
5. 点击 **开始监听** → 最小化窗口 → 进入游戏级映射模式  

---

## 配置文件
自动生成 `config.json`，示例：

```json
{
  "w": {"type": "tap", "x": 500, "y": 1500},
  "space": {"type": "tap", "x": 600, "y": 1600}
}
```

---

## 打包指令
```bash
pyinstaller main.py -F -c --distpath dist --workpath build --specpath build
```

---
