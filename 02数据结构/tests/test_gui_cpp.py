# -*- coding: utf-8 -*-
"""GUI 层: 载入 C++ 文件应显示识别提示(非空白/非崩溃), 载入 C 文件正常"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from visualizer import App

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "实例样本")
fails = 0

root = tk.Tk()
root.withdraw()
app = App(root)
app._popup = False

def check(cond, msg):
    global fails
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        fails += 1

# ① 载入 C++ 文件
code = open(os.path.join(BASE, "01类定义.cpp"), encoding="utf-8", errors="replace").read()
try:
    app.load_example_text(code)
    root.update()
    cpp = getattr(app.sim, "cpp_detected", False)
    check(cpp, "载入 .cpp 识别为 C++")
    check(not app.snapshots, "C++ 不生成误导性快照(不按 C 空跑)")
    check(hasattr(app, "sim") and app.sim.engine and app.sim.engine.error and "C++" in app.sim.engine.error.msg,
          "引擎给出 C++ 识别错误提示")
except Exception as ex:
    check(False, f"载入 .cpp 异常: {ex}")

# ② 载入纯 C 文件仍正常(能出快照/状态)
code2 = open(os.path.join(BASE, "01cdemo.c"), encoding="utf-8", errors="replace").read()
try:
    app.load_example_text(code2)
    root.update()
    check(getattr(app.sim, "cpp_detected", False) is False, "纯 C 不误判为 C++")
    check(bool(app.snapshots), "纯 C 仍能正常生成快照")
except Exception as ex:
    check(False, f"载入 .c 异常: {ex}")

root.destroy()
print(f"\n===== GUI C++ 识别验证: {'全部通过' if fails==0 else str(fails)+' 失败'} =====")
sys.exit(1 if fails else 0)
