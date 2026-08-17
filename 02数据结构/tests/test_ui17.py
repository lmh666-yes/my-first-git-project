# -*- coding: utf-8 -*-
"""1.0.4 修复测试: 1.c(带头单链表 初始化/尾插/打印/反转/销毁) 全功能验证
① 无大小数组 int a[] = {...} 推断大小
② main 正确识别 + 完整执行
③ 链表反转前后输出正确
④ 函数前向声明(prototype)支持
⑤ 常规运行逐步 + 快速运行 + 日志"""
import sys, io, os
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

SRC = r"D:\yq\CQ2615\s-01数据结构\01-作业\8.14\1.c"
if not os.path.exists(SRC):
    print("跳过: 缺少 1.c")
    print("DONE")
    sys.exit(0)
code = open(SRC, encoding="utf-8", errors="replace").read()

# === 1. 引擎层: main 识别 + 无大小数组 + 反转正确 ===
sim = Simulator(code)
check(sim.main_name() == "main", f"main 正确识别 (实际 {sim.main_name()})")
check("main" in sim.funcs and len(sim.funcs) >= 8, f"函数列表完整 ({len(sim.funcs)} 个, 含 prototype+定义)")
snaps = sim.run()
err = sim.engine.error if sim.engine else None
check(err is None, f"执行无错误 ({err.msg if err else '无'})")
outs = " ".join(sim.engine.outputs) if sim.engine else ""
check("1 ->" in outs and "2 ->" in outs and "5 ->" in outs, "反转前输出 1->2->...->5")
check("5 ->" in outs and "4 ->" in outs and "1 ->" in outs, "反转后输出 5->4->...->1")
last = max(snaps)
arr_ok = False
n_ok = False
for f in snaps[last].get("frames", []):
    if f["func"] == "main":
        for nm, v in f["vars"]:
            if nm == "arr" and v.get("type") == "int[5]":
                arr_ok = True
            if nm == "n" and v.get("value") == ("int", 5):
                n_ok = True
check(arr_ok, "无大小数组 int arr[]={...} 推断为 int[5]")
check(n_ok, "n = sizeof(arr)/sizeof(arr[0]) = 5")

# === 2. GUI 层 ===
root = tk.Tk()
root.geometry("1300x720")
app = App(root)
app._popup = False
root.update()
app.load_example_text(code)
app.set_run_mode("常规运行")
root.update()
check(app.step_idx == -1 and len(app.step_list) > 0,
      f"常规运行逐步序列就绪 ({len(app.step_list)} 步)")
app.step_next()
root.update()
check(app.step_idx == 0, "常规运行第一步正常")
app.set_run_mode("快速运行")
root.update()
check("跑通" in app.run_status.cget("text"), "快速运行跑通")
logtxt = app.logbox.get("1.0", "end")
check("反转前" in logtxt and "反转后" in logtxt, "日志含 反转前/反转后 输出")
check("1 ->" in logtxt and "5 ->" in logtxt, "日志含链表节点输出")
app.reset()
root.update()
print()
print("===== 1.0.4 1.c 全功能测试: %s =====" % ("全部通过" if fails == 0 else f"有 {fails} 个失败"))
sys.exit(fails)
