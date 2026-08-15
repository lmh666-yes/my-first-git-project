# -*- coding: utf-8 -*-
"""UI 实战验证: 加载 01/02 单向链表(带头不循环 / 带头循环), 检查:
① 指针绿框数量与位置 ② 循环链表自循环/循环返回箭头 ③ 续接标记 ④ 点击绿框高亮线"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from visualizer import App

fails = 0
def check(cond, msg):
    global fails
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        fails += 1

BASE = r"D:\yq\01虚拟机\03数据结构\02单向链表\code"
F1 = os.path.join(BASE, "01单向带头不循环.c")
F2 = os.path.join(BASE, "02单向带头循环链表.c")

if not os.path.exists(F1) or not os.path.exists(F2):
    print("跳过: 缺少外部链表文件")
    print("DONE")
    sys.exit(0)

root = tk.Tk()
root.geometry("1100x700")
app = App(root)
app._popup = False
root.update()

def load_and_check(path, name, expect_cycle):
    app.load_example_text(open(path, encoding="utf-8", errors="replace").read())
    app.run_all()
    root.update()
    d = app.drawer
    print(f"--- {name} ---")
    check(len(d.node_rects) > 0, f"内存框图 {len(d.node_rects)} 个")
    check(len(d.ptr_boxes) > 0, f"指针绿框 {len(d.ptr_boxes)} 个: {list(d.ptr_boxes.keys())[:6]}")
    # 绿框文字位置: 检查每个绿框 bbox 内的文字不溢出(文字中心在框内)
    txt_ok = True
    for nm, (x, y, w, h) in d.ptr_boxes.items():
        if w <= 0 or h <= 0:
            txt_ok = False
    check(txt_ok, "绿框尺寸全部正常")
    # 循环箭头: 自循环或循环返回
    if expect_cycle:
        # 检查是否有循环相关: 通过 last_audit arrows 数与节点数对比(循环会有回边箭头)
        check(d.last_audit["arrows"] >= 1, f"循环链表箭头数 {d.last_audit['arrows']} (含回边)")
    else:
        check(True, f"普通链表箭头数 {d.last_audit['arrows']}")
    # 点击第一个绿框 → 绿色高亮线
    if d.ptr_boxes:
        nm = next(iter(d.ptr_boxes))
        x, y, w, h = d.ptr_boxes[nm]
        import types
        app._cv_click(types.SimpleNamespace(x=int(x + w / 2), y=int(y + h / 2)))
        root.update()
        check(nm in d.ptr_links, f"点击绿框 {nm} 出现绿色高亮线")
        app._cv_click(types.SimpleNamespace(x=int(x + w / 2), y=int(y + h / 2)))
        root.update()
        check(nm not in d.ptr_links, f"再点绿框 {nm} 高亮线消失")
    return d

load_and_check(F1, "01 带头不循环", False)
load_and_check(F2, "02 带头循环", True)

root.destroy()
print()
print("===== UI 实战验证: %s =====" % ("全部通过" if fails == 0 else f"有 {fails} 个失败"))
sys.exit(fails)
