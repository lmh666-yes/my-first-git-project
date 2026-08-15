# -*- coding: utf-8 -*-
"""GUI 无界面自检：创建窗口、载入每个示例、逐行点击、验证绘图不崩溃"""
import sys, io, os, traceback
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from visualizer import App, EXAMPLES

fails = 0

def check(cond, msg):
    global fails
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        fails += 1

root = tk.Tk()
root.withdraw()  # 不显示
app = App(root)
app._popup = False  # 测试时关闭错误弹窗

for name, code in EXAMPLES.items():
    try:
        app.load_example_text(code)
        lines = code.splitlines()
        hit = 0
        for ln in range(1, len(lines) + 1):
            app.show_line(ln)
            root.update()
            if app.snapshots:
                hit += 1
        check(hit > 0, f"{name}: {len(lines)} 行，{hit} 行成功生成状态快照")
    except Exception as ex:
        traceback.print_exc()
        check(False, f"{name}: 异常 {ex}")

# 运行全部
try:
    app.run_all()
    root.update()
    check(app.snapshots != {}, "运行全部：生成最终快照")
except Exception as ex:
    check(False, f"运行全部异常: {ex}")

# 错误代码应提示不崩溃
err_code = "int main() { int a = ; return 0; }"
try:
    app.load_example_text(err_code)
    app.run_all()
    root.update()
    check(True, "错误代码被捕获，未崩溃")
except Exception as ex:
    check(False, f"错误代码异常: {ex}")

root.destroy()
print()
print("===== GUI 自检结果: %s =====" % ("全部通过" if fails == 0 else f"有 {fails} 个失败"))
sys.exit(fails)
