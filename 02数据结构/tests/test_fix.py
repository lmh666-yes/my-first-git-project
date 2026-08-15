# -*- coding: utf-8 -*-
"""针对性验证：无main片段 / C++提示 / 多节点超出界面时的滚动区域"""
import sys, io, os, traceback
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from visualizer import App
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

# 1. 无 main 的函数片段（入口参数默认值）
FRAG = r"""
typedef struct Node { int val; struct Node *next; } Node;
Node* create_node(int v) {
    Node *n = malloc(sizeof(Node));
    n->val = v;
    n->next = NULL;
    return n;
}
"""
try:
    app.load_example_text(FRAG)
    root.update()
    check(bool(app.snapshots), f"无main片段自动执行成功（快照 {len(app.snapshots)} 个）")
except Exception as ex:
    traceback.print_exc()
    check(False, f"无main片段异常: {ex}")

# 2. C++ 特性代码 → 不崩溃且有提示
CPP = r"""
#include <iostream>
using namespace std;
struct Node { int val; Node* next; };
int main() {
    Node* head = new Node();
    head->val = 1;
    head->next = NULL;
    cout << head->val << endl;
    return 0;
}
"""
try:
    app.load_example_text(CPP)
    root.update()
    hint = app.detect_cpp_hint(CPP)
    check(hint is not None, f"C++ 检测提示命中: '{hint}'")
    check(True, "C++ 代码加载未崩溃")
except Exception as ex:
    traceback.print_exc()
    check(False, f"C++ 代码异常: {ex}")

# 3. 多节点超界：30 个节点链表，验证滚动区域包含全部内容
BIG = "typedef struct Node { int val; struct Node *next; } Node;\nint main() {\n    Node *head = NULL;\n"
for i in range(1, 31):
    BIG += f"    Node *n{i} = malloc(sizeof(Node)); n{i}->val = {i}; n{i}->next = head; head = n{i};\n"
BIG += "    return 0;\n}\n"
try:
    app.load_example_text(BIG)
    root.update()
    # 模拟点击最后一行（执行完所有）
    last = max(app.snapshots.keys())
    app.show_line(last)
    root.update()
    bb = app.canvas.bbox("all")
    sr = app.canvas.cget("scrollregion")
    check(bb is not None, "画布内容存在")
    if bb:
        w = bb[2] - bb[0]
        cw = app.canvas.winfo_width()
        check(w > cw, f"30节点内容宽度 {w} > 可视宽度 {cw}，需要水平滚动（fit 生效）")
        # 验证滚动区域 >= 内容
        vals = [int(x) for x in sr.split()]
        check(vals[2] >= bb[2], f"滚动区域右边界 {vals[2]} >= 内容右边界 {bb[2]}")
except Exception as ex:
    traceback.print_exc()
    check(False, f"多节点超界测试异常: {ex}")

# 4. 多孤立堆块（非链表）：验证换行不超出
BIG2 = "int main() {\n"
for i in range(1, 16):
    BIG2 += f"    int *p{i} = malloc(4);\n"
BIG2 += "    return 0;\n}\n"
try:
    app.load_example_text(BIG2)
    root.update()
    last = max(app.snapshots.keys())
    app.show_line(last)
    root.update()
    bb = app.canvas.bbox("all")
    check(bb is not None and (bb[3] - bb[1]) > 100, "多孤立堆块自动换行、高度合理（可滚动）")
except Exception as ex:
    traceback.print_exc()
    check(False, f"多孤立堆块异常: {ex}")

root.destroy()
print()
print("===== 针对性验证: %s =====" % ("全部通过" if fails == 0 else f"有 {fails} 个失败"))
sys.exit(fails)
