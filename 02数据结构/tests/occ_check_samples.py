# -*- coding: utf-8 -*-
"""实例样本11个C文件: 图形几何审计(节点遮挡/标题遮挡) 于3个代表快照
(首个有堆 / 堆最多 / 最终)"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from simcore import Simulator
from visualizer import Drawer

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "实例样本")
FILES = ["01cdemo.c", "01单向带头不循环.c", "01双向循环链表.c", "01循环队列.c",
         "01顺序栈.c", "02单向带头循环链表.c", "02链式栈.c", "02链式队列.c",
         "03单向不带头循环链表.c", "案例1.c", "案例2.c"]

root = tk.Tk()
root.withdraw()

def overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

def rects_on(cv):
    return [cv.bbox(it) for it in cv.find_all() if cv.type(it) == "polygon" and cv.bbox(it)]

def var_box(cv):
    for it in cv.find_all():
        if cv.type(it) == "rectangle":
            b = cv.bbox(it)
            if b and b[0] <= 20 and (b[3] - b[1]) > 50:
                return b
    return None

def check(cv):
    boxes = rects_on(cv)
    vb = var_box(cv)
    bad = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if overlap(boxes[i], boxes[j]):
                bad.append((boxes[i], boxes[j]))
    if vb:
        for b in boxes:
            if overlap(vb, b):
                bad.append((vb, b))
    # 标题遮挡
    title_y = None
    for it in cv.find_all():
        if cv.type(it) == "text" and "内存 / 结构" in cv.itemcget(it, "text"):
            title_y = cv.coords(it)[1]
            break
    title_bad = False
    if title_y is not None and boxes:
        tops = [b[1] for b in boxes if b[1] > title_y - 5]
        if tops and (title_y + 15 > min(tops) + 1):
            title_bad = True
    return len(boxes), len(bad), title_bad

fails = 0
for fn in FILES:
    path = os.path.join(BASE, fn)
    code = open(path, encoding="utf-8", errors="replace").read()
    sim = Simulator(code)
    sim.run()
    snaps = sim.engine.snapshots
    if not snaps:
        print(f"  [FAIL] {fn}: 无快照")
        fails += 1
        continue
    # 三个代表快照
    ordered = sorted(snaps.items())
    cand = []
    if ordered:
        cand.append(ordered[-1][1])   # 最终
    withheap = [(ln, s) for ln, s in ordered if s["heap"]]
    if withheap:
        cand.append(withheap[0][1])
        mx = max(withheap, key=lambda x: len(x[1]["heap"]))[1]
        if mx not in cand:
            cand.append(mx)
    res = []
    # 每文件新建画布/绘制器, 排除跨文件复用污染
    canvas = tk.Canvas(root, width=620, height=760)
    d = Drawer(canvas)
    for snap in cand:
        d.clear()
        try:
            d.draw(snap, "audit")
            root.update()
            n, bad, tbad = check(canvas)
            res.append(f"框{n}遮挡{bad}{'标题遮' if tbad else ''}")
        except Exception as ex:
            res.append(f"异常{ex}")
    allok = all("遮挡0" in r and "标题遮" not in r and "异常" not in r for r in res)
    print(f"  [{'PASS' if allok else 'FAIL'}] {fn}: {len(cand)}态 -> {'; '.join(res)}")
    if not allok:
        fails += 1
root.destroy()
print(f"\n===== 实例样本几何审计: {'全部通过' if fails==0 else str(fails)+' 失败'} =====")
sys.exit(1 if fails else 0)
