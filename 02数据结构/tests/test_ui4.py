# -*- coding: utf-8 -*-
"""UI 交互验证: 51/68行布局、点击内存块信息面板、缩放、拖拽平移"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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


def rects_excluding_panel(cv):
    out = []
    for it in cv.find_all():
        if cv.type(it) == "window":
            continue
        b = cv.bbox(it)
        if b:
            out.append(b)
    return out


def max_content_w(cv):
    bb = rects_excluding_panel(cv)
    return max(b[2] for b in bb) if bb else 0


def overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


# ---- 1. 51 行: 横向不溢出, 滚动条滑块≈100% ----
app.show_line(51)
root.update()
vis_w = app.canvas.winfo_width()
cw = max_content_w(app.canvas)
xr = app.canvas.xview()
print(f"51行: 内容宽={cw} 可视宽={vis_w} 横向滑块={xr[1]-xr[0]:.1%}")
ok51 = cw <= vis_w + 5 and (xr[1] - xr[0]) >= 0.9
print("[%s] 51行横向不溢出且滑块可拖" % ("PASS" if ok51 else "FAIL"))

# ---- 2. 68 行: 节点矩形互不重叠、不与变量区重叠 ----
app.show_line(68)
root.update()
rects = []
for it in app.canvas.find_all():
    if app.canvas.type(it) == "rectangle":
        rects.append(app.canvas.coords(it))
# 变量区矩形(最左、最大灰底)
var_rect = None
for r in rects:
    x1, y1, x2, y2 = r
    if x1 <= 20 and y2 - y1 > 50:
        var_rect = r
        break
bad = []
for i in range(len(rects)):
    for j in range(i + 1, len(rects)):
        if overlap(rects[i], rects[j]):
            bad.append((rects[i], rects[j]))
# 只报节点之间的重叠(排除变量区与标题)
bad = [b for b in bad if not (b[0] is var_rect or b[1] is var_rect)]
print(f"68行: 矩形数={len(rects)} 相互重叠对数={len(bad)}")
for b in bad[:5]:
    print("  重叠:", b)
ok68 = len(bad) == 0
print("[%s] 68行节点无重叠" % ("PASS" if ok68 else "FAIL"))

# ---- 3. 点击内存块 → 右上角信息面板 ----
app.show_line(68)
root.update()
app.canvas.xview_moveto(0)
app.canvas.yview_moveto(0)
root.update()
d = app.drawer
d.panels = []
assert d.node_rects, "node_rects 为空"
addr, (rx, ry, rw, rh) = list(d.node_rects.items())[0]
ev = Ev()
ev.x = rx + 6
ev.y = ry + 6
app._cv_click(ev)
root.update()
hit_ok = any(p["addr"] == addr and p.get("win_id") for p in d.panels)
win_items = [it for it in app.canvas.find_all() if app.canvas.type(it) == "window"]
print(f"点击块 0x{addr:x}: 面板数={len(d.panels)} 面板窗口数={len(win_items)}")
print("[%s] 点击内存块显示信息面板" % ("PASS" if hit_ok and win_items else "FAIL"))

# ---- 4. 缩放: zoom 变化后重绘且滚动区变化 ----
d.zoom = 1.0
app.show_line(68)
root.update()
bb_before = app.canvas.bbox("all")
ev = Ev(); ev.x = 300; ev.y = 200; ev.delta = 120; ev.state = 4  # Ctrl 按下
app._cv_wheel(ev)
root.update()
zoomed = d.zoom > 1.0
bb_after = app.canvas.bbox("all")
print(f"缩放: zoom={d.zoom:.2f} bbox_before={bb_before[2] if bb_before else 0:.0f} bbox_after={bb_after[2] if bb_after else 0:.0f}")
print("[%s] Ctrl+滚轮缩放生效" % ("PASS" if zoomed else "FAIL"))

# ---- 5. 拖拽平移: scan_dragto 后 view 变化 ----
d.zoom = 1.0
app.show_line(68)
root.update()
app._canvas_mouse_down = True
app._press_x, app._press_y = 200, 200
app._dragging = False
app.canvas.scan_mark(200, 200)
ev2 = Ev(); ev2.x = 250; ev2.y = 220
app._cv_drag(ev2)
root.update()
y0 = app.canvas.canvasy(0)
print(f"拖拽后 canvasy(0)={y0:.1f}")
print("[%s] 拖拽平移生效" % ("PASS" if y0 > 0.5 else "FAIL"))

print("DONE")
