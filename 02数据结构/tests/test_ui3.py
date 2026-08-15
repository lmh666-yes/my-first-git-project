# -*- coding: utf-8 -*-
"""UI 验证: 滚动条可见性、行号对齐、变量区与堆块不重叠"""
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

# ---- 1. 滚动条 ----
sc = app.scrolly
print("滚动条宽x高:", sc.winfo_width(), "x", sc.winfo_height())
print("代码可视高:", app.code.winfo_height(), "总行数:", int(app.code.index('end-1c').split('.')[0]))
yv = app.code.yview()
print("yview:", yv, "(滑块比例 < 1.0 说明有滚动需求)")
scroll_ok = sc.winfo_width() >= 12 and sc.winfo_height() > 30 and (yv[1] - yv[0]) < 0.99
print("[%s] 滚动条存在且可滚动" % ("PASS" if scroll_ok else "FAIL"))

# ---- 2. 行号对齐: 取可视区首行和若干行, 比较 line_canvas 行号 y 与 code dlineinfo y ----
ok_align = True
first = int(float(app.code.index("@0,0")))
app._upd_lines()
root.update()
for ln in range(first, first + 8):
    d = app.code.dlineinfo(f"{ln}.0")
    if not d:
        continue
    _x, code_y, _w, lh, _bl = d
    items = app.line_canvas.find_all()
    found = None
    for it in items:
        if app.line_canvas.type(it) == "text" and app.line_canvas.itemcget(it, "text") == str(ln):
            found = app.line_canvas.coords(it)
            break
    if found:
        cy = found[1]
        if abs(cy - (code_y + lh / 2)) > 2:
            ok_align = False
            print(f"行号错位: 第{ln}行 行号y={cy} 代码y={code_y + lh / 2}")
    else:
        ok_align = False
        print(f"第{ln}行行号未找到")
print("[%s] 行号与代码对齐" % ("PASS" if ok_align else "FAIL"))

# ---- 3. 变量区与堆块不重叠: 运行到移动节点(多帧)后检查 ----
app._pending_inputs = []
for _ in range(200):
    app.step_next()
    root.update()
    if app.current_line in (269, 270, 271, 272, 273, 274):
        break
root.update()
# 从 canvas 收集: 变量区矩形(白色)底部 与 第一个堆块顶部
canvas = app.canvas
items = canvas.find_all()
rects = []
texts_y = []
for it in items:
    typ = canvas.type(it)
    if typ == "rectangle":
        rects.append(canvas.coords(it))
    elif typ == "text":
        texts_y.append(canvas.coords(it)[1])
# 找"内存 / 结构"标题的 y(堆区顶部)
heap_title_y = None
for it in items:
    if canvas.type(it) == "text":
        t = canvas.itemcget(it, "text")
        if "内存 / 结构" in t:
            heap_title_y = canvas.coords(it)[1]
            break
# 找变量区矩形底部
var_rect_bottom = None
for r in rects:
    x1, y1, x2, y2 = r
    if var_rect_bottom is None or y2 < var_rect_bottom:
        # 最小的矩形是变量区
        if y2 - y1 < 500:
            var_rect_bottom = y2
print("堆区标题 y:", heap_title_y)
print("变量区矩形底部 y:", var_rect_bottom)
overlap = var_rect_bottom is not None and heap_title_y is not None and heap_title_y < var_rect_bottom - 5
print("[%s] 变量区与堆块不重叠" % ("FAIL" if overlap else "PASS"))

# ---- 4. 右侧水平/垂直滚动条: 尺寸足够大、滑块比例可拖拽 ----
hsb, vsb = app.hsb, app.vsb
print("右 横向滚动条 宽x高:", hsb.winfo_width(), "x", hsb.winfo_height())
print("右 纵向滚动条 宽x高:", vsb.winfo_width(), "x", vsb.winfo_height())
xr = app.canvas.xview()
yr = app.canvas.yview()
sl_w = xr[1] - xr[0]   # 水平滑块比例
sl_h = yr[1] - yr[0]   # 垂直滑块比例
print(f"canvas xview={tuple(round(v,3) for v in xr)} 滑块比例={sl_w:.2%}")
print(f"canvas yview={tuple(round(v,3) for v in yr)} 滑块比例={sl_h:.2%}")
hsb_ok = hsb.winfo_height() >= 18 and sl_w >= 0.10
vsb_ok = vsb.winfo_width() >= 18 and sl_h >= 0.05
print("[%s] 右侧横向滚动条可拖拽(滑块≥10%%)" % ("PASS" if hsb_ok else "FAIL"))
print("[%s] 右侧纵向滚动条可拖拽(滑块≥5%%)" % ("PASS" if vsb_ok else "FAIL"))
print("当前步:", app.step_idx + 1, "/", len(app.step_list), "行:", app.current_line)
print("DONE")
