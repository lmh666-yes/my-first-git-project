# -*- coding: utf-8 -*-
"""1.0.2 新功能测试:
① 返回调用处(从函数内跳回 main)
② 运行模式菜单: 常规/运行全部/自由测试 + 状态栏绿红显示
③ 自由测试: 输入点暂停弹输入窗(标题含行号) + 输入后可跑通
④ getchar 等输入函数也支持交互输入
"""
import sys, io, os
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
root.geometry("1100x700")
app = App(root)
app._popup = False
root.update()

# === 1. 返回调用处 ===
app.load_example_text(EXAMPLES["递归-阶乘"])
app.build_step_list()
deep_idx = None
for i, (ln, snap) in enumerate(app.step_list):
    if len(snap.get("frames", [])) >= 2:
        deep_idx = i
        break
check(deep_idx is not None, "递归示例存在函数内步骤")
if deep_idx is not None:
    app.step_idx = deep_idx
    app._show_step(deep_idx)
    root.update()
    d_before = len(app.step_list[app.step_idx][1].get("frames", []))
    app.step_back_to_caller()
    root.update()
    d_after = len(app.step_list[app.step_idx][1].get("frames", []))
    check(d_after < d_before, f"返回调用处: 栈深度 {d_before} → {d_after}")

# === 2. 运行模式 + 状态栏 ===
# 常规运行 → 定位 main
app.load_example_text(EXAMPLES["链表-头插法"])
app.set_run_mode("常规运行")
root.update()
check(app.run_status.cget("text") == "● 常规运行", f"常规运行状态栏: '{app.run_status.cget('text')}'")
# 运行全部(跑通) → 绿
app.set_run_mode("运行全部")
root.update()
st = app.run_status.cget("text")
check("跑通" in st, f"运行全部跑通显示: '{st}'")
check(str(app.run_status.cget("fg")).lower() in ("#2ecc71", "#2ECC71"), "跑通为绿色")
# 未跑通(死循环) → 红 + !!!
app.load_example_text("int main() { while(1) {} return 0; }")
app.set_run_mode("运行全部")
root.update()
st = app.run_status.cget("text")
check("未" in st and "!!!" in st, f"未跑通显示红+!!!: '{st}'")
check(str(app.run_status.cget("fg")).lower() in ("#e74c3c", "#E74C3C"), "未跑通为红色")

# === 3. 自由测试 + 输入窗 ===
SCANF_CODE = "int main() { int a; scanf(\"%d\", &a); return 0; }"
app.load_example_text(SCANF_CODE)
app.set_run_mode("自由测试")
root.update()
wins = [w for w in root.winfo_children()
        if isinstance(w, tk.Toplevel) and "模拟输入" in w.title()]
check(len(wins) >= 1, f"自由测试弹出输入窗 ({len(wins)} 个)")
if wins:
    t = wins[0].title()
    check("第" in t and "行" in t, f"输入窗标题含行号: '{t}'")
    # 模拟输入并继续 → 应跑通
    app._pending_inputs.append(5)
    wins[0].destroy()
    app._free_resume()
    root.update()
    st = app.run_status.cget("text")
    check("跑通" in st, f"输入后自由测试跑通: '{st}'")

# === 4. getchar 交互输入 ===
GC = "int main() { int c; c = getchar(); return 0; }"
app.load_example_text(GC)
app.set_run_mode("自由测试")
root.update()
wins = [w for w in root.winfo_children()
        if isinstance(w, tk.Toplevel) and "模拟输入" in w.title()]
check(len(wins) >= 1, "getchar 也弹输入窗")
if wins:
    app._pending_inputs.append(65)   # 'A'
    wins[0].destroy()
    app._free_resume()
    root.update()
    check("跑通" in app.run_status.cget("text"), "getchar 输入后跑通")

# === 5. 多个输入步骤: 两次 scanf 开两个框 ===
MULTI = "int main() { int a,b; scanf(\"%d\",&a); scanf(\"%d\",&b); return 0; }"
app.load_example_text(MULTI)
app.set_run_mode("自由测试")
root.update()
wins = [w for w in root.winfo_children()
        if isinstance(w, tk.Toplevel) and "模拟输入" in w.title()]
check(len(wins) == 1, "第一个输入点弹 1 个框")
if wins:
    app._pending_inputs.append(1)
    wins[0].destroy()
    app._free_resume()
    root.update()
    wins2 = [w for w in root.winfo_children()
             if isinstance(w, tk.Toplevel) and "模拟输入" in w.title()]
    check(len(wins2) == 1, "第二个输入点再弹新框")
    if wins2:
        app._pending_inputs.append(2)
        wins2[0].destroy()
        app._free_resume()
        root.update()
        check("跑通" in app.run_status.cget("text"), "两个输入都输入后跑通")

# === 6. 重置清理 ===
app.reset()
root.update()
wins = [w for w in root.winfo_children()
        if isinstance(w, tk.Toplevel) and "模拟输入" in w.title()]
check(len(wins) == 0, "reset 后无残留输入窗")

root.destroy()
print()
print("===== 1.0.2 新功能测试: %s =====" % ("全部通过" if fails == 0 else f"有 {fails} 个失败"))
sys.exit(fails)
