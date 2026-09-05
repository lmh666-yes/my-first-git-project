# -*- coding: utf-8 -*-
"""canvas 卡片交互冒烟: 开卡/关卡/拖卡/多次重绘; 断言无 window item 且画布总有内容"""
import sys, io, os, traceback
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from types import SimpleNamespace
from visualizer import App

ROOTD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = 0
exc_log = []
root = tk.Tk()
def on_cb_exc(exc, val, tb):
    exc_log.append("".join(traceback.format_exception(exc, val, tb)))
root.report_callback_exception = on_cb_exc
app = App(root)
app._popup = False
root.geometry("1100x700+10+10")
root.update()
app.root.deiconify()
root.update()

def fake(px, py):
    return SimpleNamespace(x=px, y=py)

def check_no_window(tag):
    global fails
    ws = [it for it in app.canvas.find_all() if app.canvas.type(it) == "window"]
    if ws:
        fails += 1
        print(f"[FAIL {tag}] 仍有 {len(ws)} 个 window item(旧浮窗残留)")
    if not app.canvas.find_all():
        fails += 1
        print(f"[FAIL {tag}] 画布为空(白屏)")

def drive(path, tag):
    global fails
    code = open(path, encoding="utf-8", errors="replace").read()
    app.load_example_text(code)
    root.update()
    lines = code.splitlines()
    for ln in range(1, len(lines) + 1):
        try:
            app.show_line(ln)
            root.update()
        except Exception:
            pass
    d = app.drawer
    # 逐个内存块点击两次(开→关)
    for addr, (x, y, w, h) in list(d.node_rects.items()):
        px, py = int(x + w / 2), int(y + h / 2)
        try:
            app._cv_press(fake(px, py)); app._cv_release(fake(px, py)); root.update()
            app._cv_press(fake(px, py)); app._cv_release(fake(px, py)); root.update()
            check_no_window(f"{tag} blk toggle")
        except Exception as ex:
            fails += 1
            print(f"[FAIL {tag}] 块点击: {ex}")
            traceback.print_exc()
    # 逐指针绿框: 开(出卡)→拖卡→✕ 关
    for name, (x, y, w, h) in list(d.ptr_boxes.items()):
        px, py = int(x + w / 2), int(y + h / 2)
        try:
            app._cv_press(fake(px, py)); app._cv_release(fake(px, py)); root.update()
            ps = [p for p in d.panels if p["kind"] == "ptr"]
            if not ps:
                fails += 1; print(f"[FAIL {tag}] 点绿框 {name} 未开卡")
            else:
                p = ps[0]
                r = p.get("rect")
                if not r:
                    fails += 1; print(f"[FAIL {tag}] 卡片 {name} 无 rect")
                else:
                    # 拖动卡片
                    mx, my = int(r[0] + r[2] / 2), int(r[1] + r[3] / 2)
                    app._cv_press(fake(mx, my))
                    app._cv_drag(fake(mx + 12, my + 8)); root.update()
                    app._cv_drag(fake(mx + 24, my + 16)); root.update()
                    app._cv_release(fake(mx + 24, my + 16)); root.update()
                    # ✕ 关闭
                    cl = p.get("close")
                    app._cv_press(fake(int(cl[0] + 8), int(cl[1] + 8)))
                    app._cv_release(fake(int(cl[0] + 8), int(cl[1] + 8)))
                    root.update()
                    if d.panels:
                        fails += 1; print(f"[FAIL {tag}] ✕ 未关闭指针卡")
                    check_no_window(f"{tag} ptr")
        except Exception as ex:
            fails += 1
            print(f"[FAIL {tag}] 绿框流程: {ex}")
            traceback.print_exc()
    # 连点 3 块(最多2块: 最旧自动移除) 后 3 次 redraw 稳定
    for addr, (x, y, w, h) in list(d.node_rects.items()):
        px, py = int(x + w / 2), int(y + h / 2)
        try:
            app._cv_press(fake(px, py)); app._cv_release(fake(px, py)); root.update()
        except Exception:
            pass
    for _ in range(3):
        app.redraw(); root.update()
        check_no_window(f"{tag} redraw")
    app.drawer.panels = []
    app.drawer.ptr_links = {}
    app.drawer.wrap_arrows = {}
    app.drawer.wrap_marks = {}
    app.redraw(); root.update()
    print(f"== {tag} 完成(累计失败 {fails}, 回调异常 {len(exc_log)}) ==")

for p, t in [("案例讲解1/01枚举法.c", "01"), ("案例讲解1/03结构体包装.c", "03"),
             ("案例讲解1/04C++中实现.cpp", "04"), ("examples/linked_list_insert.c", "ll")]:
    drive(os.path.join(ROOTD, p), t)
for s in exc_log[:3]:
    print("[CALLBACK]\n" + s)
print(f"\n===== 卡片交互冒烟: 失败 {fails}, 回调异常 {len(exc_log)} =====")
root.destroy()
sys.exit(1 if (fails or exc_log) else 0)
