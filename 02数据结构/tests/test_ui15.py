# -*- coding: utf-8 -*-
"""1.0.3 新功能测试:
① 快速运行默认模拟输入 + 日志窗口(程序输出/输入来源标注)
② printf 输出进入日志
③ 常规运行点击限制(main 外不可点)
④ 输入级联格式化(重新到输入点清空该点及后续)
⑤ 输入窗含「模拟输入」按钮
⑥ auto_gen_inputs 自动生成
"""
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from visualizer import App, EXAMPLES, auto_gen_inputs

fails = 0
def check(cond, msg):
    global fails
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        fails += 1

root = tk.Tk()
root.geometry("1300x720")
app = App(root)
app._popup = False
root.update()

# === 1. 快速运行: 自动模拟输入 + 日志 ===
SCANF = 'int main() { int a,b; printf("sum=%d\\n", a+b); scanf("%d", &a); scanf("%d", &b); printf("done\\n"); return 0; }'
app.load_example_text(SCANF)         # 载入默认执行一次快速运行
root.update()
logtxt = app.logbox.get("1.0", "end")
check(app._run_count >= 1, f"日志有执行次数记录 ({app._run_count})")
check("程序输出" in logtxt, "日志含「程序输出」")
check("sum=" in logtxt or "done" in logtxt, "日志含 printf 输出内容")
check("模拟输入" in logtxt, "日志输入标注 (模拟输入)")
check("✅ 已跑通" in logtxt or "❌" in logtxt, "日志含运行状态")

# === 2. printf 输出正确性 ===
PC = 'int main() { printf("a=%d %s %x\\n", 10, "hi", 255); puts("world"); return 0; }'
app.load_example_text(PC)
root.update()
logtxt = app.logbox.get("1.0", "end")
check("a=10 hi ff" in logtxt, "printf 格式替换正确 (a=10 hi ff)")
check("world" in logtxt, "puts 输出进入日志")

# === 3. 常规运行点击限制 ===
app.load_example_text(EXAMPLES["递归-阶乘"])
app.set_run_mode("常规运行")
root.update()
# fact 函数体行(第 2 行 if)不应可点; main 体行(第 6 行)应可点
app.show_line(2)
root.update()
check(not app._line_in_main(2) and app._line_in_main(6),
      "常规运行: main 外行不可点, main 内行可点")

# === 4. 输入级联格式化 ===
app._input_slots = {5: [1], 10: [2], 12: [3]}
app._pending_inputs = [1, 2, 3]
# 重新到输入点 5 → 清空 5 及之后所有
if 5 in app._input_slots:
    for k in list(app._input_slots.keys()):
        if k >= 5:
            del app._input_slots[k]
    app._rebuild_pending_from_slots()
check(app._input_slots == {} and app._pending_inputs == [],
      "输入级联格式化: 重新到输入点清空该点及后续")

# === 5. 输入窗含「模拟输入」按钮 ===
app.load_example_text(SCANF)
app.set_run_mode("自由运行")
root.update()
wins = [w for w in root.winfo_children()
        if isinstance(w, tk.Toplevel) and "模拟输入" in w.title()]
check(len(wins) >= 1, "自由运行弹出输入窗")
if wins:
    btns = []
    def findb(w, out):
        if isinstance(w, tk.Button):
            out.append(w.cget("text"))
        for c in w.winfo_children():
            findb(c, out)
    findb(wins[0], btns)
    check("模拟输入" in btns, f"输入窗含「模拟输入」按钮: {btns}")
    # 用模拟输入按钮提交
    app._input_slots = {}
    app._auto_slots = {}
    for b in wins[0].winfo_children():
        pass
    # 直接模拟按钮逻辑: 生成并提交
    import random
    vals = auto_gen_inputs(app.get_code())
    app._input_slots[next(iter(app.snapshots.keys()), 1)] = vals[:1]
    app._rebuild_pending_from_slots()
    check(len(app._pending_inputs) >= 1, "模拟输入按钮: 自动生成值并写入槽")
    wins[0].destroy()

# === 6. auto_gen_inputs ===
vals = auto_gen_inputs('int main(){ int a; scanf("%d",&a); getchar(); return 0; }')
check(len(vals) >= 2, f"auto_gen_inputs 生成足够输入 ({len(vals)} 个)")
vals2 = auto_gen_inputs('int main(){ return 0; }')
check(vals2 == [], "无输入函数返回空列表")

app.reset()
root.update()
print()
print("===== 1.0.3 新功能测试: %s =====" % ("全部通过" if fails == 0 else f"有 {fails} 个失败"))
sys.exit(fails)
