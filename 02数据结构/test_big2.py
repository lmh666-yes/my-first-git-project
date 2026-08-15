# -*- coding: utf-8 -*-
"""几千行可执行 C 项目测试: 生成 3000+ 行 C 程序(100个函数+链表+数组+main),
加载执行, 验证绘制准确性(节点/审计/无重叠) 与内容准确。"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tkinter as tk
from visualizer import App
from simcore import Simulator

# ---- 生成 3000+ 行 C 程序 ----
lines = []
lines.append("#include <stdio.h>")
lines.append("#include <stdlib.h>")
lines.append("typedef struct Node { int val; struct Node *next; } Node;")
lines.append("")
# 100 个函数(每个 ~3 行) => ~300 行
for i in range(100):
    lines.append(f"int sum_{i}(int a[], int n) {{")
    lines.append(f"    int s = 0;")
    lines.append(f"    for (int k = 0; k < n; k++) s = s + a[k];")
    lines.append(f"    return s;")
    lines.append(f"}}")
    lines.append("")
# 40 个链表函数(每个 ~4 行) => ~160 行
for i in range(40):
    lines.append(f"Node *mk_{i}(int v) {{")
    lines.append(f"    Node *n = malloc(sizeof(Node));")
    lines.append(f"    n->val = v;")
    lines.append(f"    n->next = 0;")
    lines.append(f"    return n;")
    lines.append(f"}}")
    lines.append("")
# 大量数组/赋值语句填充到 3000+ 行
idx = 0
while len(lines) < 3050:
    lines.append(f"    int w{idx} = {idx % 100};")
    lines.append(f"    arr[{idx % 50}] = arr[{idx % 50}] + w{idx};")
    idx += 1
# main
lines.append("int main() {")
lines.append("    int arr[50];")
lines.append("    for (int i = 0; i < 50; i++) arr[i] = i;")
lines.append("    Node *head = 0;")
lines.append("    for (int i = 0; i < 12; i++) {")
lines.append("        Node *n = malloc(sizeof(Node));")
lines.append("        n->val = i * 3;")
lines.append("        n->next = head;")
lines.append("        head = n;")
lines.append("    }")
lines.append("    int total = 0;")
lines.append("    total = sum_0(arr, 50) + sum_1(arr, 50);")
lines.append("    Node *p = head;")
lines.append("    while (p) { total = total + p->val; p = p->next; }")
lines.append("    return 0;")
lines.append("}")

code = "\n".join(lines)
print(f"生成程序行数: {len(lines)}")

# ---- 1. 引擎执行准确性 ----
sim = Simulator(code)
snaps = sim.run()
err = sim.engine.error if sim.engine else None
steps = list(sim.engine.step_snapshots) if sim.engine else []
print(f"引擎: 快照数={len(snaps)} 步数={len(steps)} 运行错误={err.msg if err else '无'}")
ok_engine = err is None and len(snaps) > 0

# ---- 2. GUI 绘制准确性 ----
root = tk.Tk()
root.geometry("1180x720")
app = App(root)
app._popup = False
app.load_example_text(code)
root.update()
app.run_all()
root.update()
d = app.drawer
au = d.last_audit
print(f"绘制: 链数={au['chains']} 节点={au['nodes']} 箭头={au['arrows']} "
      f"NULL={au['nulls']} 野={au['wilds']} 续排={au['wraps']}")
audit_ok = au["nodes"] == au["arrows"] + au["nulls"] + au["wilds"] + au["wraps"]
# 节点无重叠
def overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])
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
print(f"节点块数={len(nodes)} 重叠={bad}")
ok_gui = audit_ok and bad == 0 and au["nodes"] >= 12   # 12 个链表节点

# ---- 3. 逐步回放 20 步无崩溃 ----
app.build_step_list()
n_steps = min(20, len(app.step_list))
for _ in range(n_steps):
    app.step_next()
    root.update()
print(f"逐步回放 {n_steps} 步无崩溃 (总步数 {len(app.step_list)})")
ok_step = n_steps == 20

print("[%s] 几千行(3000+)可执行项目: 引擎准确 + 绘制准确 + 逐步回放无崩溃"
      % ("PASS" if ok_engine and ok_gui and ok_step else "FAIL"))
print("DONE")
