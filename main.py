#!/usr/bin/env python3
# auto_keymap.py
import io, json, os, threading, subprocess, time
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox, ttk
from pynput import keyboard, mouse

CFG_FILE = "config.json"

def save_config():
    with open(CFG_FILE, "w", encoding="utf-8") as f:
        json.dump(MAPPING, f, indent=2, ensure_ascii=False)

ADB = "adb"
CFG_FILE = "config.json"
MAPPING = json.load(open(CFG_FILE)) if os.path.isfile(CFG_FILE) else {}

# ---------- ADB ----------
def adb(cmd):
    return subprocess.check_output([ADB] + cmd).strip()

def get_device():
    lines = subprocess.check_output([ADB, "devices"]).decode().splitlines()
    devices = [l.split()[0] for l in lines[1:] if l.endswith("\tdevice")]
    if not devices:
        raise RuntimeError("未找到已授权的 ADB 设备！")
    return devices[0]

DEVICE = get_device()
def adb_shell(cmd):
    subprocess.call([ADB, "-s", DEVICE, "shell", "input"] + cmd)

# ---------- GUI ----------
class MapperGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Auto Keymap")
        self.geometry("960x720")
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

        self.scale = 1.0  # 缩放系数
        self.img = None
        self.tk_img = None
        self.mark_ids = []  # 保存标记 id，便于删除

        # 顶部
        frm = tk.Frame(self)
        tk.Button(frm, text="刷新屏幕", command=self.refresh_screen).pack(side="left", padx=5)
        tk.Button(frm, text="保存配置", command=self.save_cfg).pack(side="left", padx=5)
        tk.Button(frm, text="开始监听", command=self.start_listening).pack(side="left", padx=5)
        frm.pack(pady=5)

        # 左侧可滚动画布
        cvs_frame = tk.Frame(self)
        self.canvas = tk.Canvas(cvs_frame, bg="black")
        hbar = ttk.Scrollbar(cvs_frame, orient="horizontal", command=self.canvas.xview)
        vbar = ttk.Scrollbar(cvs_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Button-3>", self.on_canvas_right)  # 右键删除
        self.canvas.pack(side="left", fill="both", expand=True)
        hbar.pack(fill="x")
        vbar.pack(side="right", fill="y")
        cvs_frame.pack(fill="both", expand=True, padx=5)

        # 右侧列表
        self.tree = ttk.Treeview(self, columns=("action"), height=8, show="tree")
        self.tree.heading("#0", text="热键")
        self.tree.heading("action", text="动作")
        self.tree.bind("<Button-3>", self.on_tree_right)
        self.tree.pack(fill="x", padx=5, pady=5)

        # 全局键盘钩子：Ctrl+W+C
        keyboard.Listener(on_press=self.global_hotkey, daemon=True).start()

        self.refresh_screen()
        self.update_table()

    # ---------- 屏幕刷新 ----------
    def refresh_screen(self):
        raw = subprocess.check_output([ADB, "-s", DEVICE, "exec-out", "screencap", "-p"])
        self.img = Image.open(io.BytesIO(raw)).convert("RGB")
        # 自适应缩放
        w, h = self.img.size
        max_side = 900
        if max(w, h) > max_side:
            self.scale = max_side / max(w, h)
        else:
            self.scale = 1.0
        scaled = self.img.resize((int(w * self.scale), int(h * self.scale)), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(scaled)
        self.canvas.delete("all")
        self.canvas.config(scrollregion=(0, 0, scaled.width, scaled.height))
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        self.redraw_marks()

    # ---------- 标记绘制 ----------
    def redraw_marks(self):
        for mid in self.mark_ids:
            self.canvas.delete(mid)
        self.mark_ids.clear()
        for k, v in MAPPING.items():
            x, y = int(v["x"] * self.scale), int(v["y"] * self.scale)
            size = 10
            line1 = self.canvas.create_line(x - size, y, x + size, y, fill="red", width=2)
            line2 = self.canvas.create_line(x, y - size, x, y + size, fill="red", width=2)
            self.mark_ids.extend([line1, line2])

    # ---------- 绑定键位 ----------
    def on_canvas_click(self, ev):
        # 还原原始坐标
        raw_x = int(self.canvas.canvasx(ev.x) / self.scale)
        raw_y = int(self.canvas.canvasy(ev.y) / self.scale)
        self.wait_hotkey(raw_x, raw_y)

    def wait_hotkey(self, x, y):
        self.config(cursor="watch")
        self.update()

        def once_key(k):
            try:
                key = k.char
            except AttributeError:
                key = str(k)
            self.bind_key(key, "tap", x, y)
            return False
        def once_click(x2, y2, button, pressed):
            if pressed:
                self.bind_key(str(button), "tap", x, y)
            return False

        k_listener = keyboard.Listener(on_press=once_key)
        m_listener = mouse.Listener(on_click=once_click)
        for l in (k_listener, m_listener):
            l.start()
        while k_listener.is_alive() and m_listener.is_alive():
            self.update()
        k_listener.stop(); m_listener.stop()
        self.config(cursor="")
        self.update_table()
        self.redraw_marks()

    def bind_key(self, key, typ, x, y):
        MAPPING[key] = {"type": typ, "x": x, "y": y}
        print("绑定:", key, MAPPING[key])

    # ---------- 删除 ----------
    def on_canvas_right(self, ev):
        raw_x = int(self.canvas.canvasx(ev.x) / self.scale)
        raw_y = int(self.canvas.canvasy(ev.y) / self.scale)
        to_del = None
        for k, v in MAPPING.items():
            if abs(v["x"] - raw_x) < 30 and abs(v["y"] - raw_y) < 30:
                to_del = k
                break
        if to_del:
            del MAPPING[to_del]
            self.update_table()
            self.redraw_marks()

    def on_tree_right(self, ev):
        item = self.tree.identify_row(ev.y)
        if item:
            key = self.tree.item(item, "text")
            if key in MAPPING:
                del MAPPING[key]
                self.update_table()
                self.redraw_marks()

    # ---------- 表格 ----------
    def update_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for k, v in MAPPING.items():
            self.tree.insert("", "end", text=k, values=(v,))

    # ---------- 全局热键 ----------
    def global_hotkey(self, key):
        # pynput 无法直接捕获组合键，用状态机简单实现
        if str(key) == "Key.ctrl_l" or str(key) == "Key.ctrl_r":
            self.ctrl_pressed = True
        elif str(key) == "'w'" and getattr(self, "ctrl_pressed", False):
            self.w_pressed = True
        elif str(key) == "'c'" and getattr(self, "w_pressed", False):
            self.clear_cfg()

    def clear_cfg(self):
        if messagebox.askyesno("确认清空", "确定要清空所有键位映射吗？此操作不可撤销！"):
            MAPPING.clear()
            self.update_table()
            self.redraw_marks()
            save_config()
            messagebox.showinfo("已清空", "配置文件已重置")
        # 重置状态
        self.ctrl_pressed = self.w_pressed = False

    # ---------- 保存 ----------
    def save_cfg(self):
        save_config()
        messagebox.showinfo("保存", "已写入 config.json")

    # ---------- 监听 ----------
    def start_listening(self):
        save_config()
        self.withdraw()
        start_worker()

    def on_exit(self):
        save_config()
        self.destroy()

# ---------- 后台 ----------
def start_worker():
    def on_key(k):
        try:
            key = k.char
        except AttributeError:
            key = str(k)
        if key in MAPPING:
            v = MAPPING[key]
            if v["type"] == "tap":
                adb_shell(["tap", str(v["x"]), str(v["y"])])
    def on_click(x, y, button, pressed):
        if pressed and str(button) in MAPPING:
            v = MAPPING[str(button)]
            adb_shell(["tap", str(v["x"]), str(v["y"])])
    k = keyboard.Listener(on_press=on_key)
    m = mouse.Listener(on_click=on_click)
    k.start(); m.start()
    print("🎮 实时映射已启动，Ctrl+C 退出")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        k.stop(); m.stop()

# ---------- 主入口 ----------
if __name__ == "__main__":
    MapperGUI().mainloop()