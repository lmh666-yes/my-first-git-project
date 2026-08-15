# -*- coding: utf-8 -*-
"""精确验证: 节点矩形宽度是否足够容纳所有文字(防越界) + 信息面板存在"""
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

# 运行到若干关键行, 检查每个节点矩形宽是否 >= 标题/字段文字宽+边距
issues = 0
for ln in (51, 68, 90, 100, 269):
    app.show_line(ln)
    root.update()
    d = app.drawer
    tf = d.F(10, True)
    ff = d.F(10)
    for addr, (x, y, w, h) in d.node_rects.items():
        blk = d.heap_by_addr.get(addr)
        if blk is None:
            continue
        loc = "栈" if blk.get("loc") == "栈" else "堆"
        title = f"{blk['typename']} @0x{addr:x} [{loc}]"
        tw = d.mw(title, tf)
        need = 0
        for fn, disp, tgt in d.field_rows(blk):
            t = f"{fn} -> {disp}" if tgt is not None else f"{fn} = {disp}"
            need = max(need, d.mw(t, ff))
        maxneed = max(tw, need) + 14 * d.zoom
        if w < maxneed - 1:
            issues += 1
            print(f"  第{ln}行 块0x{addr:x} 宽={w:.0f} 需要={maxneed:.0f} 越界!")
print("[%s] 所有节点文字均在矩形内(不越界)" % ("PASS" if issues == 0 else f"FAIL({issues})"))

# 信息面板 + 缩放 + 拖拽 + 点击 综合
app.show_line(68)
root.update()
d = app.drawer
addr, (rx, ry, rw, rh) = list(d.node_rects.items())[2]
class Ev: pass
ev = Ev(); ev.x = rx + 6; ev.y = ry + 6
app._cv_click(ev)
root.update()
win_items = [it for it in app.canvas.find_all() if app.canvas.type(it) == "window"]
print("选中块:", hex(d.selected_addr) if d.selected_addr else None, "面板窗口数:", len(win_items))
print("[%s] 点击内存块 → 右上角信息面板" % ("PASS" if d.selected_addr is not None and win_items else "FAIL"))

# 缩放
z0 = d.zoom
ev = Ev(); ev.x = 300; ev.y = 200; ev.delta = 120; ev.state = 4
app._cv_wheel(ev)
root.update()
print(f"缩放: {z0:.2f} -> {d.zoom:.2f}")
print("[%s] Ctrl+滚轮缩放" % ("PASS" if d.zoom > z0 else "FAIL"))

# 左键+滚轮缩放(左键按住模拟)
d.zoom = 1.0
app.show_line(68); root.update()
z0 = d.zoom
app._canvas_mouse_down = True
ev = Ev(); ev.x = 300; ev.y = 200; ev.delta = -120; ev.state = 0
app._cv_wheel(ev)
root.update()
app._canvas_mouse_down = False
print(f"左键+滚轮: {z0:.2f} -> {d.zoom:.2f}")
print("[%s] 左键+滚轮缩放" % ("PASS" if d.zoom < z0 else "FAIL"))

print("DONE")
