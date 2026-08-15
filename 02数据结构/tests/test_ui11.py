# -*- coding: utf-8 -*-
"""信息面板(介绍框)验证: ①点击第1块→右上红面板+红描边+红线 ②点击第2块→右下蓝面板+蓝描边+蓝线
③再点已选中→关闭 ④移除后重新分配(红右上/蓝右下) ⑤面板可拖动且连线同步 ⑥关闭叉叉"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from visualizer import App

p = r"d:\yq\01虚拟机\03数据结构\02单向链表\code\01单向带头不循环.c"
code = open(p, encoding="utf-8", errors="replace").read()

root = tk.Tk()
root.geometry("1180x720")
app = App(root)
app._popup = False
app.load_example_text(code)
root.update()
root.update_idletasks()

app.show_line(126)
root.update()
app.canvas.xview_moveto(0)
app.canvas.yview_moveto(0)
root.update()

class Ev:
    pass


def click(addr):
    d = app.drawer
    x, y, w, h = d.node_rects[addr]
    ev = Ev(); ev.x = x + 5; ev.y = y + 5
    app._cv_click(ev)
    root.update()


d = app.drawer
addrs = list(d.node_rects.keys())
cw = app.canvas.winfo_width()
ch = app.canvas.winfo_height()
ok = True

# ---- ① 点击第1个块 → 红色右上 ----
addr1 = addrs[0]
click(addr1)
p1 = d.panels[0] if d.panels else None
ok1 = (len(d.panels) == 1 and p1["color"] == "#e53935"
       and p1["anchor"] == "ne" and p1["dx"] > cw - 60 and p1["dy"] < 60
       and bool(app.canvas.find_withtag(f"hl_{addr1}")) and bool(p1["line_id"]))
print(f"① 第1块: 面板数={len(d.panels)} 色={p1['color'] if p1 else None} "
      f"anchor={p1['anchor'] if p1 else None} 描边={bool(app.canvas.find_withtag(f'hl_{addr1}'))} 线={bool(p1 and p1['line_id'])}")
print("[%s] 第1块: 红色面板在右上角+红描边+红线" % ("PASS" if ok1 else "FAIL"))
ok = ok and ok1

# ---- ② 点击第2个不同块 → 蓝色右下 ----
addr2 = addrs[1] if len(addrs) > 1 else addrs[0]
click(addr2)
p2 = d.panels[1] if len(d.panels) > 1 else None
ok2 = (len(d.panels) == 2 and p2["color"] == "#1e88e5"
       and p2["anchor"] == "se" and p2["dy"] > ch - 60
       and bool(app.canvas.find_withtag(f"hl_{addr2}")) and bool(p2["line_id"]))
print(f"② 第2块: 面板数={len(d.panels)} 色={p2['color'] if p2 else None} "
      f"anchor={p2['anchor'] if p2 else None} dy={p2['dy'] if p2 else None} 描边={bool(app.canvas.find_withtag(f'hl_{addr2}'))}")
print("[%s] 第2块: 蓝色面板在右下角+蓝描边+蓝线" % ("PASS" if ok2 else "FAIL"))
ok = ok and ok2

# ---- ③ 再点已选中的 addr1 → 关闭 ----
click(addr1)
ok3 = len(d.panels) == 1 and d.panels[0]["addr"] == addr2
print(f"③ 再点addr1: 面板数={len(d.panels)} 剩余={[hex(x['addr']) for x in d.panels]}")
print("[%s] 再点已选中→关闭该面板" % ("PASS" if ok3 else "FAIL"))
ok = ok and ok3

# ---- ④ 移除后重新分配: 再点 addr1 → 成为第2个(蓝右下), 原addr2回第1(红右上) ----
click(addr1)
p_a1 = next((p for p in d.panels if p["addr"] == addr1), None)
p_a2 = next((p for p in d.panels if p["addr"] == addr2), None)
ok4 = (len(d.panels) == 2 and p_a2["color"] == "#e53935" and p_a2["anchor"] == "ne"
       and p_a1["color"] == "#1e88e5" and p_a1["anchor"] == "se")
print(f"④ 重分配: addr2(红右上)={p_a2['color']}/{p_a2['anchor']} addr1(蓝右下)={p_a1['color']}/{p_a1['anchor']} 面板数={len(d.panels)}")
print("[%s] 移除后重新分配(第1红右上/第2蓝右下)" % ("PASS" if ok4 else "FAIL"))
ok = ok and ok4

# ---- ⑤ 面板可拖动, 连线同步 ----
frame = d.panels[0]["frame"]
x0 = frame.winfo_rootx()
y0 = frame.winfo_rooty()
dx_before = d.panels[0]["dx"]
dy_before = d.panels[0]["dy"]
try:
    frame.event_generate("<ButtonPress-1>", x=8, y=8, rootx=x0 + 8, rooty=y0 + 8)
    frame.event_generate("<B1-Motion>", x=8, y=8, rootx=x0 + 8 + 40, rooty=y0 + 8 + 25)
    root.update()
    p_ = d.panels[0]
    ok5 = (abs(p_["dx"] - dx_before - 40) < 3 and abs(p_["dy"] - dy_before - 25) < 3
           and p_["line_id"])
    print(f"⑤ 拖动: dx {dx_before}->{p_['dx']} dy {dy_before}->{p_['dy']} 线={bool(p_['line_id'])}")
except Exception as ex:
    ok5 = False
    print("⑤ 拖动模拟异常:", str(ex)[:80])
print("[%s] 面板可拖动且连线同步" % ("PASS" if ok5 else "FAIL"))
ok = ok and ok5

# ---- ⑥ 关闭叉叉 ----
p_before = len(d.panels)
bar_close = None
def find_close(w):
    global bar_close
    for ch in w.winfo_children():
        if isinstance(ch, tk.Label) and ch.cget("text").strip() == "✕":
            bar_close = ch
            return True
        if find_close(ch):
            return True
    return False
fr = d.panels[0]["frame"]
find_close(fr)
if bar_close is not None:
    print("  找到✕, bindings:", bar_close.bind("<Button-1>"))
    bar_close.event_generate("<Button-1>", x=2, y=2)
    root.update()
    root.update_idletasks()
    print("  触发后面板数:", len(d.panels))
ok6 = len(d.panels) == p_before - 1
print(f"⑥ 叉叉: 面板数 {p_before}->{len(d.panels)}")
print("[%s] 关闭叉叉生效" % ("PASS" if ok6 else "FAIL"))
ok = ok and ok6

print("[%s] 信息面板全部功能验证" % ("PASS" if ok else "FAIL"))
print("DONE")
