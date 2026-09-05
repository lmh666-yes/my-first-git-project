# -*- coding: utf-8 -*-
"""GUI: 案例讲解1 4 文件逐行渲染; 载入新文件自动清空日志; 清理日志按钮"""
import sys, io, os, traceback
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from visualizer import App

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "案例讲解1")
fails = 0
root = tk.Tk()
root.withdraw()
app = App(root)
app._popup = False

def log_text():
    try:
        return app.logbox.get("1.0", "end")
    except Exception:
        return ""

def run_file(fn, expect_cpp):
    global fails
    code = open(os.path.join(BASE, fn), encoding="utf-8", errors="replace").read()
    lines = code.splitlines()
    # 清空日志(模拟手动清理按钮)
    app.clear_log()
    assert log_text().strip() == "", "clear_log 未清空日志"
    assert app._run_count == 0, "clear_log 未重置计数"
    try:
        app.load_example_text(code)
        root.update()
        is_cpp = bool(getattr(app.sim, "cpp_detected", False))
        # 载入新文件后日志不应包含上一个文件内容, 且从第 1 次执行开始
        lt = log_text()
        fresh = lt.count("第 1 次执行") >= 1 and lt.count("第 2 次执行") == 0
        hit, errs = 0, 0
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
        ok = (is_cpp == expect_cpp) and errs == 0 and hit > 0 and fresh
        print(f"  [{'PASS' if ok else 'FAIL'}] {fn}: cpp={is_cpp} 出图{hit}/{len(lines)} 异常{errs} 日志干净={fresh}")
        if not ok:
            fails += 1
    except Exception as ex:
        print(f"  [FAIL] {fn}: 异常 {ex}")
        fails += 1

run_file("01枚举法.c", False)
run_file("02void指针.c", False)
run_file("03结构体包装.c", False)
run_file("04C++中实现.cpp", True)

root.destroy()
print(f"\n===== GUI 案例讲解1 冒烟: {'全部通过' if fails==0 else str(fails)+' 失败'} =====")
sys.exit(1 if fails else 0)
