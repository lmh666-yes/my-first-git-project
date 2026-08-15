# -*- coding: utf-8 -*-
"""GUI 验证 06.c: 逐步执行并截图, 检查 scalar 值与 freed 状态显示"""
import sys, io, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from visualizer import App
from PIL import ImageGrab

p = r"d:\yq\CQ2615\c-06-复习\06.c"
code = open(p, encoding="utf-8", errors="replace").read()

root = tk.Tk()
root.geometry("1180x720")
root.attributes("-topmost", True)
app = App(root)
app._popup = False
app.load_example_text(code)
root.deiconify()
root.lift()
root.update()
root.update_idletasks()
time.sleep(0.8)

# 逐步执行到 free(p) 之后
app.build_step_list()
for _ in range(6):
    app.step_next()
    root.update()
    d = app.drawer
    au = d.last_audit
    print(f"步{app.step_idx+1}: 行{app.current_line} 节点{au['nodes']} 块显示:")
    for addr, (x, y, w, h) in d.node_rects.items():
        blk = d.heap_by_addr.get(addr)
        if blk:
            print(f"   0x{addr:x}: {blk['typename']} loc={blk.get('loc')} "
                  f"scalar={blk.get('scalar')} freed={blk.get('freed')} rect=({x:.0f},{y:.0f},{w:.0f},{h:.0f})")
root.update()
time.sleep(0.5)
x0, y0 = root.winfo_rootx(), root.winfo_rooty()
w, h = root.winfo_width(), root.winfo_height()
ImageGrab.grab().crop((x0, y0, x0 + w, y0 + h)).save(r"d:\github\02数据结构\shot_06c.png")
print("截图已保存 shot_06c.png")
print("DONE")
