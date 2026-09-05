# -*- coding: utf-8 -*-
"""GUI 冒烟(批2): 03类继承构造析构 / 12类对象成员 / 01类外堆内存 逐行渲染 + run_all 不崩"""
import sys, io, os, traceback
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

def run_file(fn):
    global fails
    code = open(os.path.join(BASE, fn), encoding="utf-8", errors="replace").read()
    lines = code.splitlines()
    try:
        app.load_example_text(code)
        root.update()
        is_cpp = bool(getattr(app.sim, "cpp_detected", False))
        hit = 0
        errs = 0
        for ln in range(1, len(lines) + 1):
            try:
                app.show_line(ln)
                root.update()
                if app.snapshots:
                    hit += 1
            except Exception:
                errs += 1
                if errs <= 6:
                    traceback.print_exc()
                    print(f"      ^^^ 第 {ln} 行异常")
        app.run_all()
        root.update()
        app.redraw()
        root.update()
        ok = is_cpp and errs == 0 and hit > 0
        print(f"  [{'PASS' if ok else 'FAIL'}] {fn}: cpp={is_cpp} 逐行出图{hit}/{len(lines)} 异常{errs}")
        if not ok:
            fails += 1
    except Exception as ex:
        print(f"  [FAIL] {fn}: 异常 {ex}")
        fails += 1

for f in ["03类继承中的构造和析构.cpp", "12类对象成员.cpp", "01类外堆内存.cpp",
          "01类继承语法.cpp"]:
    run_file(f)

root.destroy()
print(f"\n===== GUI 批2 冒烟: {'全部通过' if fails==0 else str(fails)+' 失败'} =====")
sys.exit(1 if fails else 0)
