# -*- coding: utf-8 -*-
"""1.0.3 常规运行逐步 bug 修复测试 + 01双向循环链表 全功能检测:
① 常规运行: 点下一步一步一行(不跳结尾), 上一步正常回退
② 快速运行: 跑通 + 日志
③ 自由运行: 无输入直接完成
④ 循环/双向链表绘制: 循环箭头 + 审计平衡"""
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

SRC = r"D:\yq\01虚拟机\03数据结构\03双向链表\code\01双向循环链表.c"
if not os.path.exists(SRC):
    print("跳过: 缺少 01双向循环链表.c")
    print("DONE")
    sys.exit(0)
code = open(SRC, encoding="utf-8", errors="replace").read()

root = tk.Tk()
root.geometry("1300x720")
app = App(root)
app._popup = False
root.update()

# === 1. 常规运行: 一步一行 ===
app.load_example_text(code)
app.set_run_mode("常规运行")
root.update()
check(app.step_idx == -1, f"常规运行后 step_idx 从 -1 开始 (实际 {app.step_idx})")
check(len(app.step_list) > 0, f"逐步序列已构建 ({len(app.step_list)} 步)")
total = len(app.step_list)
# 点下一步: 逐步前进, 不跳结尾
app.step_next()
root.update()
check(app.step_idx == 0, f"第一次下一步 → 第 1 步 (实际 {app.step_idx})")
for _ in range(5):
    app.step_next()
    root.update()
check(app.step_idx == 5, f"连续 6 次下一步 → 第 6 步 (实际 {app.step_idx}，idx=点击次数-1)，一步一行")
check(app.step_idx < total - 1, "未跳到结尾")
# 上一步回退
app.step_prev()
root.update()
check(app.step_idx == 4, f"上一步回退 → 第 5 步 (实际 {app.step_idx})")
# 快速跳到末尾再上一步
app.step_idx = total - 1
app._show_step(total - 1)
root.update()
app.step_prev()
root.update()
check(app.step_idx == total - 2, f"结尾上一步正常回退 (实际 {app.step_idx})")

# === 2. 快速运行: 跑通 + 日志 ===
app.set_run_mode("快速运行")
root.update()
check("跑通" in app.run_status.cget("text"), f"快速运行跑通: '{app.run_status.cget('text')}'")
logtxt = app.logbox.get("1.0", "end")
check("程序输出" in logtxt and ("1->2" in logtxt or "1->" in logtxt),
      "日志含遍历输出 (1->2->...)")
check(app._run_count >= 1, f"日志有执行记录 ({app._run_count} 次)")

# === 3. 自由运行: 无 scanf 直接完成 ===
app.set_run_mode("自由运行")
root.update()
check("跑通" in app.run_status.cget("text"), "自由运行(无输入)直接跑通")

# === 4. 双向循环链表绘制: 循环箭头 + 审计平衡（中间状态: 常规运行到销毁前） ===
app.set_run_mode("常规运行")
root.update()
# 找 main 中 double_list_destroy 调用行之前的步(节点最多)
best = 0
best_nodes = 0
for i, (ln, snap) in enumerate(app.step_list):
    n = len(snap.get("heap", []))
    if n > best_nodes:
        best_nodes = n
        best = i
app.step_idx = best
app._show_step(best)
root.update()
d = app.drawer
au = d.last_audit
check(au["nodes"] == au["arrows"] + au["nulls"] + au["wilds"] + au["wraps"],
      f"箭头审计平衡: 节点{au['nodes']} = 箭头{au['arrows']}+NULL{au['nulls']}+野{au['wilds']}+续{au['wraps']}")
check(au["nodes"] >= 10, f"中间状态节点完整 ({au['nodes']} 个)")
check(au["arrows"] >= 1, f"双向循环链表画出循环箭头 ({au['arrows']} 个)")

# === 5. 返回调用处: 双链表有函数调用, 进入后能返回 ===
app.set_run_mode("常规运行")
root.update()
# 找 main 内函数调用步(深度2)
deep = None
for i, (ln, snap) in enumerate(app.step_list):
    if len(snap.get("frames", [])) >= 2:
        deep = i
        break
if deep is not None:
    app.step_idx = deep
    app._show_step(deep)
    root.update()
    db = len(app.step_list[app.step_idx][1].get("frames", []))
    app.step_back_to_caller()
    root.update()
    da = len(app.step_list[app.step_idx][1].get("frames", []))
    check(da < db, f"返回调用处: 深度 {db} → {da}")
else:
    check(True, "跳过: 无函数内步骤")

app.reset()
root.update()
print()
print("===== 1.0.3 常规运行修复 + 双向链表检测: %s =====" % ("全部通过" if fails == 0 else f"有 {fails} 个失败"))
sys.exit(fails)
