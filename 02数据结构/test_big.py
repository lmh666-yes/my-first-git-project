# -*- coding: utf-8 -*-
"""大项目测试: 加载 6105 行 utils_gen.c, 检查大文件下 UI(加载性能/行号/滚动/高亮/不崩溃);
再加载 test_lib.c 逐步执行, 验证内容准确性。"""
import sys, io, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tkinter as tk
from visualizer import App

root = tk.Tk()
root.geometry("1180x720")
app = App(root)
app._popup = False
root.update()

BIG = r"D:\github\01函数库\library\utils_gen.c"
code_big = open(BIG, encoding="utf-8", errors="replace").read()
total_lines = len(code_big.splitlines())
print(f"大文件行数: {total_lines}")

# ---- 1. 大文件加载性能与 UI ----
t0 = time.time()
app.load_example_text(code_big)
dt = time.time() - t0
root.update()
code_lines = int(app.code.index("end-1c").split(".")[0])
print(f"加载耗时: {dt:.2f}s  代码区行数: {code_lines}")
ok_load = code_lines >= total_lines - 2 and dt < 60

# 行号: 滚动后检查 line_canvas 行号数量
app.code.yview_moveto(0.5)
root.update()
app._upd_lines()
root.update()
ln_items = len(app.line_canvas.find_all())
print(f"滚动到中部后行号元素数: {ln_items} (>0 说明行号正常)")
ok_ln = ln_items > 0

# 滚动条可用
yv = app.code.yview()
print(f"代码 yview: {tuple(round(v,3) for v in yv)}  纵向滑块比例={(yv[1]-yv[0]):.2%}")
ok_scroll = (yv[1] - yv[0]) < 0.99

# 高亮: 检查有 keyword/comment tag 覆盖
hl_ok = bool(app.code.tag_ranges("kw")) and bool(app.code.tag_ranges("cm"))
print(f"语法高亮: 关键字={bool(app.code.tag_ranges('kw'))} 注释={bool(app.code.tag_ranges('cm'))}")

print("[%s] 大文件(6105行)加载/行号/滚动/高亮均正常" % ("PASS" if ok_load and ok_ln and ok_scroll and hl_ok else "FAIL"))

# ---- 2. test_lib.c 内容准确性 ----
LIB = r"D:\github\01函数库\tests\test_lib.c"
code_lib = open(LIB, encoding="utf-8", errors="replace").read()
app.load_example_text(code_lib)
root.update()
try:
    sim = __import__("simcore").Simulator(code_lib)
    snaps = sim.run()
    err = sim.engine.error if sim.engine else None
    print(f"test_lib.c: 快照数={len(snaps)} 运行错误={err.msg if err else '无'}")
    acc_ok = err is None and len(snaps) > 0
    # 逐步执行若干步检查绘制不崩溃
    app.build_step_list()
    for _ in range(min(10, len(app.step_list))):
        app.step_next()
        root.update()
    print(f"test_lib.c 逐步执行 {min(10, len(app.step_list))} 步无崩溃")
except Exception as ex:
    acc_ok = False
    print("test_lib.c 异常:", str(ex)[:80])
print("[%s] test_lib.c 内容准确性(执行无错+逐步绘制无崩溃)" % ("PASS" if acc_ok else "FAIL"))
print("DONE")
