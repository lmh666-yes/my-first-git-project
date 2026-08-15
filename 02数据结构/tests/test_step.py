# -*- coding: utf-8 -*-
"""临时验证: scanf 输入模拟 + 函数 return 后 main 继续"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from visualizer import App

root = tk.Tk()
root.withdraw()
app = App(root)
app._popup = False

# 测试1: scanf 输入模拟
code1 = 'int main() { int a, b; scanf("%d %d", &a, &b); int s = a + b; return 0; }'
app.load_example_text(code1)
app._pending_inputs = [3, 4]
app.run_all()
root.update()
last = app.snapshots[max(app.snapshots.keys())]
vals = {}
for fr in last["frames"]:
    for n, v in fr["vars"]:
        vals[n] = v.get("value")
print("scanf测试:", vals)
ok1 = vals.get("a") == ("int", 3) and vals.get("b") == ("int", 4) and vals.get("s") == ("int", 7)
print("  [%s] scanf 输入 a=3 b=4 s=7" % ("PASS" if ok1 else "FAIL"))

# 测试2: 函数 return 后 main 继续
code2 = 'int add(int x) { return x + 1; }\nint main() { int a = add(5); int b = add(10); return 0; }'
app.load_example_text(code2)
app._pending_inputs = []
lines = []
for _ in range(30):
    app.step_next()
    root.update()
    lines.append(app.current_line)
print("逐步行序列:", lines)
last2 = app.snapshots[max(app.snapshots.keys())] if app.snapshots else {}
vals2 = {}
for fr in last2.get("frames", []):
    for n, v in fr["vars"]:
        vals2[n] = v.get("value")
print("最终:", vals2, "总步数", len(app.step_list))
# add 内 return 后 main 应继续, 最终 a=6 b=11
ok2 = vals2.get("a") == ("int", 6) and vals2.get("b") == ("int", 11)
print("  [%s] 函数返回后 main 继续 a=6 b=11" % ("PASS" if ok2 else "FAIL"))

print("DONE")
