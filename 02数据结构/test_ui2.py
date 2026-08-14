# -*- coding: utf-8 -*-
"""验证三项优化：上下布局 / 点击行内存变更摘要 / 堆栈准确标注"""
import sys, io, os, traceback
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tkinter as tk
from visualizer import App, EXAMPLES
from simcore import Simulator

fails = 0

def check(cond, msg):
    global fails
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        fails += 1

root = tk.Tk()
root.withdraw()
app = App(root)
app._popup = False

# 1. 堆/栈标注（引擎层）
code = r"""
typedef struct Node { int val; struct Node *next; } Node;
int main() {
    Node *head = NULL;
    Node *n = malloc(sizeof(Node));
    n->val = 5;
    n->next = NULL;
    head = n;
    return 0;
}
"""
sim = Simulator(code)
snaps = sim.run()
last = max(snaps)
snap = snaps[last]
blocks = snap["heap"]
malloc_b = [b for b in blocks if b["loc"] == "堆"]
check(len(malloc_b) == 1, f"malloc 的节点标注为「堆」（{len(malloc_b)} 个）")

# 结构体变量应标「栈」
code2 = "typedef struct { int len; } S;\nint main() { S s; s.len = 3; return 0; }\n"
sim2 = Simulator(code2)
snaps2 = sim2.run()
last2 = max(snaps2)
blk2 = [b for b in snaps2[last2]["heap"] if b["typename"] == "S"]
check(blk2 and blk2[0]["loc"] == "栈", "结构体变量 s 标注为「栈」")

# 2. GUI：点击行 → 变更摘要
app.load_example_text(code)
root.update()
# 找 malloc 行（第 5 行附近）
app.show_line(5)   # Node *n = malloc(...)
root.update()
check("分配" in app.status.cget("text"), f"点击 malloc 行显示「分配」→ {app.status.cget('text')[:40]}")
# 找 n->val = 5 行（第 6 行）
app.show_line(6)
root.update()
check("修改" in app.status.cget("text") and "val" in app.status.cget("text"),
      f"点击赋值行显示字段修改 → {app.status.cget('text')[:50]}")
# 宏/typedef 行：第 1 行 typedef
app.show_line(1)
root.update()
check("未修改内存" in app.status.cget("text"), f"点击 typedef 行显示「未修改内存」→ {app.status.cget('text')[:40]}")

# 3. 布局：draw 后 canvas 有标题 + 下方内存区
app.show_line(5)
root.update()
canvas_items = app.canvas.find_all()
check(len(canvas_items) > 5, f"绘制后有 {len(canvas_items)} 个图形元素")

root.destroy()
print()
print("===== 界面优化验证: %s =====" % ("全部通过" if fails == 0 else f"有 {fails} 个失败"))
sys.exit(fails)
