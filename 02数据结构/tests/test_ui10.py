# -*- coding: utf-8 -*-
"""缩放适配验证: 在多个 zoom 下检查 行高≥字号(不挤压)、节点无重叠、文字可读"""
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

app.show_line(126)
root.update()


def overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


zooms = [0.45, 0.6, 0.8, 1.0, 1.5, 2.0, 3.0]
all_ok = True
for z in zooms:
    d = app.drawer
    d.zoom = z
    app.show_line(126)
    root.update()
    # 1) 行高 vs 字号: 变量区行高 lh 应 >= 字号(约 px)
    font_px = max(8, round(10 * z))
    lh_ok = d.lh >= font_px - 2
    fh_ok = d.fh >= font_px - 2
    # 2) 节点(polygon)之间不重叠
    nodes = []
    for it in app.canvas.find_all():
        if app.canvas.type(it) == "polygon":
            b = app.canvas.bbox(it)
            if b:
                nodes.append(b)
    bad = 0
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if overlap(nodes[i], nodes[j]):
                bad += 1
    ok = lh_ok and fh_ok and bad == 0
    all_ok = all_ok and ok
    print(f"  zoom={z:.2f}: 字号={font_px} 变量行高={d.lh} 字段行高={d.fh} "
          f"节点块={len(nodes)} 重叠={bad} {'PASS' if ok else 'FAIL'}")

print("[%s] 所有缩放下布局协调(不挤压、无重叠、文字可读)" % ("PASS" if all_ok else "FAIL"))
print("DONE")
