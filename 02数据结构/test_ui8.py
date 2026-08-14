# -*- coding: utf-8 -*-
"""验证: ① NULL箭头与next字段行对齐 ② 堆内箭头高度=next字段行 ③ 仅Ctrl+滚轮缩放 ④ 双击复位"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tkinter as tk
from visualizer import App

p = r"d:\yq\01虚拟机\03数据结构\02单向链表\code\01单向带头不循环.c"
code = open(p, encoding="utf-8", errors="replace").read()

root = tk.Tk()
root.geometry("1180x720")
app = App(root)
app._popup = False
app.load_example_text(code)
root.update()
root.update_idletasks()

class Ev:
    pass


# ---- 1. NULL 箭头与 next 字段行对齐 ----
app.show_line(126)   # 链完整(10节点+head), 有 NULL 尾
root.update()
cv = app.canvas
z = app.drawer.zoom
# NULL 文本中心
nulls = []
for it in cv.find_all():
    if cv.type(it) == "text":
        t = cv.itemcget(it, "text").strip()
        if t == "NULL":
            x, y = cv.coords(it)
            nulls.append((x, y + 7 * z))
# 水平箭头(不含续接竖直箭头)
harrows = []
for it in cv.find_all():
    if cv.type(it) == "line":
        c = cv.coords(it)
        if len(c) == 4 and abs(c[1] - c[3]) < 0.5:
            harrows.append(c)
# 每个 NULL 找最近的水平箭头, 检查 y 对齐
mis_null = 0
for nx, ny in nulls:
    best = min(harrows, key=lambda a: abs(a[1] - ny), default=None)
    if best is None:
        mis_null += 1
        print(f"  NULL({nx:.0f},{ny:.0f}) 无箭头!")
    elif abs(best[1] - ny) > 2:
        mis_null += 1
        print(f"  NULL({nx:.0f},{ny:.0f}) 箭头y={best[1]:.0f} 错位")
print(f"NULL 标记数={len(nulls)} 水平箭头数={len(harrows)} 错位={mis_null}")
print("[%s] NULL 箭头与文本对齐" % ("PASS" if mis_null == 0 and nulls else "FAIL"))

# ---- 2. 堆内节点箭头高度 = next 字段行 ----
d = app.drawer
# 计算每个节点的 next 字段行 y
next_lines = set()
for addr, (x, y, w, h) in d.node_rects.items():
    blk = d.heap_by_addr.get(addr)
    if blk is None:
        continue
    idx = d._next_field_idx(blk)
    next_lines.add(round(d._field_line_y(y, idx, z)))
mis_arrow = 0
bad_ys = []
for c in harrows:
    if round(c[1]) not in next_lines:
        mis_arrow += 1
        bad_ys.append((round(c[0]), round(c[1]), round(c[2])))
print(f"节点 next 字段行数={len(next_lines)} 水平箭头不匹配={mis_arrow}")
if bad_ys:
    print("  不匹配箭头(起点x, y, 终点x):", bad_ys[:10])
    print("  next 字段行 y 集合:", sorted(next_lines))
print("[%s] 堆内箭头高度=next字段行" % ("PASS" if mis_arrow == 0 else "FAIL"))

# ---- 3. 仅 Ctrl+滚轮缩放; 普通滚轮不缩放 ----
# 普通滚轮(无 Ctrl, 无左键) → 垂直滚动, 不缩放
app.canvas.yview_moveto(0.3)   # 先滚到中部, 保证可滚动
root.update()
z1 = d.zoom
y_before = app.canvas.yview()[0]
ev = Ev(); ev.x = 300; ev.y = 200; ev.delta = 120; ev.state = 0
app._cv_wheel(ev)
root.update()
nozoom_ok = abs(d.zoom - z1) < 1e-9
y_after = app.canvas.yview()[0]
scrolled = abs(y_after - y_before) > 1e-6
# Ctrl 缩放
z2 = d.zoom
ev = Ev(); ev.x = 300; ev.y = 200; ev.delta = 120; ev.state = 4  # Ctrl
app._cv_wheel(ev)
root.update()
ctrl_ok = d.zoom > z2
print(f"普通滚轮: zoom不变={nozoom_ok} 滚动={scrolled}   Ctrl缩放: {z2:.2f}->{d.zoom:.2f}")
print("[%s] 仅 Ctrl+滚轮缩放, 普通滚轮只滚动" % ("PASS" if ctrl_ok and nozoom_ok and scrolled else "FAIL"))

# ---- 4. 双击复位 ----
app._zoom_reset()
root.update()
print(f"双击复位后 zoom={d.zoom:.2f}")
verdict = "PASS" if abs(d.zoom - 1.0) < 0.01 else "FAIL"
print(f"[{verdict}] 双击恢复 100%")
print("DONE")
