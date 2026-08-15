# -*- coding: utf-8 -*-
"""用户文件专项: 跨排长链(10节点→多排)的遮挡 + 标题 + 箭头审计 + NULL/野指针指向"""
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


def overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def audit_ok(d):
    au = d.last_audit
    return au["nodes"] == au["arrows"] + au["nulls"] + au["wilds"] + au["wraps"]


def check(ln):
    app.show_line(ln)
    root.update()
    cv = app.canvas
    d = app.drawer
    au = d.last_audit
    # 节点 = 圆角多边形(polygon) 的 bbox
    nodes = []
    for it in cv.find_all():
        if cv.type(it) == "polygon":
            b = cv.bbox(it)
            if b:
                nodes.append(b)
    # 变量区大矩形
    var_rect = None
    for it in cv.find_all():
        if cv.type(it) == "rectangle":
            b = cv.bbox(it)
            if b and b[0] <= 20 and (b[3] - b[1]) > 50:
                var_rect = b
                break
    bad = 0
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if overlap(nodes[i], nodes[j]):
                bad += 1
    if var_rect:
        for b in nodes:
            if overlap(var_rect, b):
                bad += 1
    # 标题遮挡
    title_y = None
    for it in cv.find_all():
        if cv.type(it) == "text" and "内存 / 结构" in cv.itemcget(it, "text"):
            title_y = cv.coords(it)[1]
            break
    title_ok = True
    tinfo = "无标题"
    if title_y is not None and nodes:
        first_top = min(b[1] for b in nodes)
        tinfo = f"标题底~{title_y + 15:.0f} 首节点顶={first_top:.0f}"
        title_ok = title_y + 15 <= first_top + 1
    ok = audit_ok(d) and bad == 0 and title_ok
    print(f"  第{ln}行: 节点{au['nodes']} 箭头{au['arrows']} NULL{au['nulls']} "
          f"野{au['wilds']} 续排{au['wraps']} 块数={len(nodes)} 重叠={bad} {tinfo}")
    return ok, au["wraps"] > 0


# 找到链完整(跨排)的步骤: 遍历多行, 取 wraps>0 的一步重点检查
checked = []
multiline_ok = None
for ln in (126, 127, 128, 130, 135, 140, 150, 160, 200, 230, 250, 269):
    ok, crossed = check(ln)
    checked.append((ln, ok))
    if crossed and multiline_ok is None:
        multiline_ok = ok

all_ok = all(ok for _, ok in checked)
print("----")
print(f"检查 {len(checked)} 个步骤, 全部通过: {all_ok}")
print(f"跨排(wraps>0)步骤存在且通过: {multiline_ok}")
print("[%s] 用户文件多步骤: 无遮挡 + 标题不被压 + 箭头完整" % ("PASS" if all_ok and multiline_ok else "FAIL"))

# 额外: 检查 NULL 箭头(链尾)存在 —— 末节点 next=NULL 应有 NULL 标记
app.show_line(269)
root.update()
au = app.drawer.last_audit
has_null_arrow = au["nulls"] > 0 or au["nodes"] == 0
print(f"最终快照: 节点{au['nodes']} NULL标记{au['nulls']}")
print("[%s] 指向 NULL 的箭头已实现" % ("PASS" if has_null_arrow else "FAIL"))
print("DONE")
