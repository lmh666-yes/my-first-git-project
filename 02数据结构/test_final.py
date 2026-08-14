# -*- coding: utf-8 -*-
"""综合复查：examples 外部文件 + 全部内置示例逐行点击 + 运行全部"""
import sys, io, os, traceback
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tkinter as tk
from visualizer import App, EXAMPLES

fails = 0

def check(cond, msg):
    global fails
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        fails += 1

root = tk.Tk()
root.withdraw()
app = App(root)

# 1. 外部 examples 文件
ex_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples")
for fn in sorted(os.listdir(ex_dir)):
    if fn.endswith(".c"):
        path = os.path.join(ex_dir, fn)
        with open(path, encoding="utf-8") as f:
            code = f.read()
        try:
            app.load_example_text(code)
            lines = code.splitlines()
            hit = 0
            for ln in range(1, len(lines) + 1):
                app.show_line(ln)
                root.update()
                if app.snapshots:
                    hit += 1
            check(hit == len(lines), f"{fn}: {len(lines)} 行全部可点击生成快照（{hit}）")
        except Exception as ex:
            traceback.print_exc()
            check(False, f"{fn}: 异常 {ex}")

# 2. 内置示例 run_all
for name in EXAMPLES:
    try:
        app.load_example_text(EXAMPLES[name])
        app.run_all()
        root.update()
        check(bool(app.snapshots), f"run_all: {name}")
    except Exception as ex:
        traceback.print_exc()
        check(False, f"run_all {name}: 异常 {ex}")

root.destroy()
print()
print("===== 综合复查: %s =====" % ("全部通过" if fails == 0 else f"有 {fails} 个失败"))
sys.exit(fails)
