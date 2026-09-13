# -*- coding: utf-8 -*-
"""UI 长内容/滚动/缩放专项测试：
1) 超长题干 → 高度封顶 14 行 + 垂直滚动条（内容不丢）
2) 超长选项 → 选项区出现滚动条
3) 标签换行宽度随窗口宽度自适应（缩放后同步）
4) 短题干 → 不显示滚动条
5) 配图渲染
6) 超长解析反馈 → 解析区出现滚动条 + 拖动分隔条可放大解析区
7) 窗口缩放后选项区宽度/换行同步
8) 考试全流程（含长内容渲染）无异常
用法：python test_ui_long.py（窗口会短暂显示）
"""
import sys, os, io, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "core"))
import tkinter as tk
import 刷题软件 as bs

fails = 0
def check(cond, msg):
    global fails
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        fails += 1

bs.messagebox.showinfo = lambda t, m: None
bs.messagebox.showerror = lambda t, m: None
bs.messagebox.showwarning = lambda t, m: None
bs.messagebox.askyesno = lambda t, m: True

bp = bs.PROG_PATH
tmp = bp + ".bak"
had = os.path.exists(bp)
if had:
    os.replace(bp, tmp)

root = tk.Tk()
app = bs.App(root)
root.update()

# ---------- 构造超长内容题 ----------
long_stem = "\n".join(["很长很长的题干内容测试，" * 6] * 30)
fake = {"id": "T-long", "kind": "choice", "kind_name": "单选题", "num": 999,
        "stem": long_stem,
        "options": [{"key": k, "text": "很长的选项内容测试，" * 25} for k in "ABCD"],
        "answer": "A", "explain": "解析内容" * 300, "imgs": []}

app.set_mode("顺序")
app.queue = [fake]
app.idx = 0
app.show_question()
root.update()
root.update_idletasks()

# 1. 长题干
check(int(app.stem.cget("height")) == 14,
      f"超长题干高度封顶 14 行（实际 {app.stem.cget('height')}）")
check(app.stem_sb.winfo_manager() == "grid", "超长题干出现垂直滚动条（内容不丢）")

# 2. 长选项滚动条（等待防抖 60ms 后再检查）
time.sleep(0.25)
root.update()
root.update_idletasks()
check(app.opt_sb.winfo_manager() == "grid", "超长选项区出现垂直滚动条")

# 3. 标签换行宽度自适应
w = app.opt_canvas.winfo_width()
ws = [int(lbl.cget("wraplength")) for lbl in app._wrap_widgets]
check(len(ws) > 0 and all(abs(x - (w - 48)) <= 4 for x in ws),
      f"标签换行宽度自适应（选项区宽 {w}px，标签 {ws[:3]}）")

# 4. 短题干
app.queue = [app._by_id("choice-1")]
app.idx = 0
app.show_question()
root.update()
root.update_idletasks()
check(int(app.stem.cget("height")) < 14,
      f"短题干高度自适应（实际 {app.stem.cget('height')} 行）")
check(app.stem_sb.winfo_manager() != "grid", "短题干不显示滚动条")

# 5. 配图渲染
img_items = [it for it in app.bank if it.get("imgs")]
if img_items:
    app.queue = img_items[:1]
    app.idx = 0
    app.show_question()
    root.update()
    root.update_idletasks()
    imgs_ok = any(getattr(w_, "image", None) for w_ in app.opt_widgets)
    check(imgs_ok, f"配图渲染成功（{img_items[0]['id']}）")
else:
    print("  [SKIP] 题库无配图题")

# 6. 超长解析反馈
fake2 = dict(fake)
fake2["imgs"] = []
app.queue = [fake2]
app.idx = 0
app.show_question()
root.update()
app.reveal_qa()
root.update()
root.update_idletasks()
check(app.fb_sb.winfo_manager() == "grid", "超长解析区出现滚动条（内容不丢）")
h_before = app.fb.winfo_height()
try:
    app.split.sashpos(0, max(150, app.split.winfo_height() - 420))     # ttk 分栏
except Exception:
    try:
        app.split.sash_place(0, 0, max(150, app.split.winfo_height() - 420))
    except Exception:
        pass
root.update()
root.update_idletasks()
h_after = app.fb.winfo_height()
check(h_after > h_before, f"拖动分隔条可放大解析区（{h_before} → {h_after}）")

# 7. 窗口缩放同步
root.geometry("920x640")
root.update()
root.update_idletasks()
w1 = app.opt_canvas.winfo_width()
root.geometry("1180x780")
root.update()
root.update_idletasks()
w2 = app.opt_canvas.winfo_width()
check(w2 > w1, f"窗口缩放后选项区宽度自适应（{w1} → {w2}）")
ws2 = [int(lbl.cget("wraplength")) for lbl in app._wrap_widgets]
check(len(ws2) > 0 and all(abs(x - (w2 - 48)) <= 4 for x in ws2),
      "缩放后标签换行宽度同步更新")

# 8. 考试全流程（真实题库）
app.set_mode("考试")
app._exam_start()
root.update()
total = len(app.queue)
for i in range(total):
    app.idx = i
    it = app.queue[i]
    if it["kind"] in ("choice", "multi"):
        ans = str(app.exam["opts"][it["id"]]["answer"])
    elif it["kind"] == "judge":
        ans = str(it.get("answer", "√"))
    else:
        continue
    app._exam_answer(it, ans)
root.update()
app.finish_exam()
root.update()
check(app.exam.get("finished") is True, "考试全流程（含长内容渲染）无异常")
check(app.opt_frame.winfo_reqheight() > 0, "成绩页渲染正常")

root.destroy()
if had:
    os.replace(tmp, bp)
elif os.path.exists(bp):
    os.remove(bp)

print()
print("结果：" + ("全部通过" if fails == 0 else f"{fails} 项失败"))
sys.exit(1 if fails else 0)
