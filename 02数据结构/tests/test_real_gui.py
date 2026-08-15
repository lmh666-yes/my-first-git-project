# -*- coding: utf-8 -*-
"""真实代码 GUI 测试：加载 D:\yq 下用户写的 C 文件，逐行点击，验证不崩溃、能出图。
仅在 D:\yq\CQ2615 存在时运行，否则跳过。"""
import sys, io, os, traceback
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

BASE = r"D:\yq\CQ2615"
if not os.path.isdir(BASE):
    print("未找到 D:\\yq\\CQ2615，跳过真实文件测试")
    sys.exit(0)

# 收集所有 c- / s- 开头的 .c 文件
targets = []
for d in os.listdir(BASE):
    dp = os.path.join(BASE, d)
    if os.path.isdir(dp) and (d.startswith("c-") or d.startswith("s-")):
        for f in os.listdir(dp):
            if f.lower().endswith(".c") and os.path.getsize(os.path.join(dp, f)) > 0:
                targets.append(os.path.join(dp, f))

print(f"共 {len(targets)} 个非空 .c 文件")

root = tk.Tk()
root.withdraw()
app = App(root)
app._popup = False

ok = fail = 0
for idx, path in enumerate(targets, 1):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            code = f.read()
        app.load_example_text(code)
        lines = code.splitlines()
        hit = 0
        for ln in range(1, len(lines) + 1):
            app.show_line(ln)
            root.update()
            if app.snapshots:
                hit += 1
        name = os.path.basename(path)
        if hit > 0:
            ok += 1
            print(f"  [OK]   [{idx}/{len(targets)}] {name}: {hit}/{len(lines)} 行可生成快照")
        else:
            fail += 1
            print(f"  [NO]   [{idx}/{len(targets)}] {name}: 无快照（空文件或无 main）")
    except Exception as ex:
        fail += 1
        print(f"  [FAIL] [{idx}/{len(targets)}] {os.path.basename(path)}: {ex}")

root.destroy()
print()
print(f"===== 真实代码 GUI 测试: {ok} 成功 / {fail} 失败 =====")
sys.exit(1 if fail else 0)
