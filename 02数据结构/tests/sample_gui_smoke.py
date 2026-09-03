# -*- coding: utf-8 -*-
"""11个纯C样本 GUI 渲染冒烟: 逐行点击渲染 + run_all + redraw, 全程不崩溃"""
import sys, io, os, traceback
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from visualizer import App

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "实例样本")
FILES = ["01cdemo.c", "01单向带头不循环.c", "01双向循环链表.c", "01循环队列.c",
         "01顺序栈.c", "02单向带头循环链表.c", "02链式栈.c", "02链式队列.c",
         "03单向不带头循环链表.c", "案例1.c", "案例2.c"]

fails = 0
root = tk.Tk()
root.withdraw()
app = App(root)
app._popup = False

for fn in FILES:
    path = os.path.join(BASE, fn)
    code = open(path, encoding="utf-8", errors="replace").read()
    lines = code.splitlines()
    try:
        app.load_example_text(code)
        hit = 0
        for ln in range(1, len(lines) + 1):
            app.show_line(ln)
            root.update()
            if app.snapshots:
                hit += 1
        # run_all + 强制重绘
        app.run_all()
        root.update()
        app.redraw()
        root.update()
        ok = hit > 0
        print(f"  [{'PASS' if ok else 'FAIL'}] {fn}: {len(lines)}行, {hit}行有快照")
        if not ok:
            fails += 1
    except Exception as ex:
        traceback.print_exc()
        print(f"  [FAIL] {fn}: 异常 {ex}")
        fails += 1

root.destroy()
print(f"\n===== 样本GUI渲染冒烟: {'全部通过' if fails==0 else str(fails)+' 失败'} =====")
sys.exit(1 if fails else 0)
