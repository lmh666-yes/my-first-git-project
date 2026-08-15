# -*- coding: utf-8 -*-
"""1.0.1 新功能测试:
① 独立指针变量绿框 + 点击绿色解释面板(指向目标/地址)
② 链表换行「续接」标记 + 点击显示高亮紫色垂直箭头(再点隐藏)
③ 粘贴代码界面右下按钮加大优化
"""
import sys, io, os, types
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

# === 1. 指针绿框 + 绿色解释面板 (08.c 场景) ===
code08 = r"""
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
typedef struct { int x; int y; } po;
int main() {
    po *p;
    p = (po*)malloc(sizeof(po));
    p->x = 10;
    p->y = 20;
    return 0;
}
"""
app.load_example_text(code08)
app.run_all()
root.update()
d = app.drawer
check("p" in d.ptr_boxes, "独立指针变量 p 有绿框")
x = y = w = h = 0
if "p" in d.ptr_boxes:
    x, y, w, h = d.ptr_boxes["p"]
    check(w > 10 and h > 10, f"绿框尺寸正常 ({w:.0f}x{h:.0f})")
# 模拟点击绿框中心 → 绿色面板
app._cv_click(types.SimpleNamespace(x=int(x + w / 2), y=int(y + h / 2)))
root.update()
ptr_panels = [p for p in d.panels if p["kind"] == "ptr"]
check(len(ptr_panels) == 1 and ptr_panels[0]["name"] == "p", "点击绿框出现绿色解释面板")
check(bool(ptr_panels) and ptr_panels[0]["color"] == "#43a047", "指针面板为绿色")
# 面板内容: 含指向地址 与 目标类型
txt = ""
def collect(widget, out):
    try:
        out.append(widget.cget("text"))
    except Exception:
        pass
    for c in widget.winfo_children():
        collect(c, out)
if ptr_panels and ptr_panels[0].get("frame"):
    buf = []
    collect(ptr_panels[0]["frame"], buf)
    txt = " ".join(buf)
check("0x" in txt and "po" in txt, "面板包含指向地址(0x...)与目标类型(po)")
# 再点一次关闭
app._cv_click(types.SimpleNamespace(x=int(x + w / 2), y=int(y + h / 2)))
root.update()
check(not any(p["kind"] == "ptr" for p in d.panels), "再点绿框关闭面板")

# === 2. 续接标记 + 紫箭头 (递归链表求和, 窄画布强制换行) ===
app.load_example_text(EXAMPLES["递归-链表求和"])
app.run_all()
root.update()
for _ in range(3):
    if d.wrap_marks:
        break
    root.geometry("430x700")
    root.update()
    app.redraw()
    root.update()
wrap = bool(d.wrap_marks)
check(wrap, "递归链表求和: 存在可点击「续接」标记")
if wrap:
    mid, info = next(iter(d.wrap_marks.items()))
    x1, y1, x2, y2 = info["rect"]
    check(x2 - x1 >= 60, f"续接标记加大 (宽 {x2-x1:.0f}px)")
    app._cv_click(types.SimpleNamespace(x=int((x1 + x2) / 2), y=int((y1 + y2) / 2)))
    root.update()
    check(mid in d.wrap_arrows, "点击续接 → 出现高亮紫色箭头")
    app._cv_click(types.SimpleNamespace(x=int((x1 + x2) / 2), y=int((y1 + y2) / 2)))
    root.update()
    check(mid not in d.wrap_arrows, "再点续接 → 紫箭头隐藏")

# === 3. 粘贴界面按钮加大 ===
win = None
btns = []
try:
    app.paste_code()
    root.update()
    for w in root.winfo_children():
        if isinstance(w, tk.Toplevel):
            win = w
    if win is None:
        check(False, "粘贴界面未打开")
    else:
        def find_btns(widget, out):
            if isinstance(widget, tk.Button):
                out.append(widget)
            for c in widget.winfo_children():
                find_btns(c, out)
        find_btns(win, btns)
        check(len(btns) >= 2, f"粘贴界面按钮存在 ({len(btns)} 个)")
        ok = True
        for b in btns:
            fstr = str(b.cget("font"))
            try:
                pad = int(b.cget("padx"))
            except Exception:
                pad = 0
            fsz = 0
            for tok in fstr.replace("{", " ").replace("}", " ").split():
                if tok.isdigit():
                    fsz = max(fsz, int(tok))
            if not (fsz >= 11 and pad >= 20):
                ok = False
                print(f"  [信息] 按钮 {b.cget('text')} 字号={fsz} padx={pad}")
        check(ok, "粘贴界面按钮加大加粗(字号≥11, padx≥20)")
        win.destroy()
except Exception as ex:
    check(False, f"粘贴界面异常: {ex}")

root.destroy()
print()
print("===== 1.0.1 新功能测试: %s =====" % ("全部通过" if fails == 0 else f"有 {fails} 个失败"))
sys.exit(fails)
