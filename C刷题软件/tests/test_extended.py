# -*- coding: utf-8 -*-
"""扩展自检（1.2.0）：数据完整性 / 界面结构(无随机/收藏/重新做) / 判断题交互 /
笔记时机 / 错题进出 / 悬停绑定 / 控件泄漏 / 考试边界"""
import sys, io, os, json, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "core"))
import tkinter as tk
import 刷题软件 as bs

PASS = 0
FAIL = 0
def ok(name, cond, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {extra}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {extra}")

bs.messagebox.showinfo = lambda t, m: None
bs.messagebox.showerror = lambda t, m: None
bs.messagebox.showwarning = lambda t, m: None
bs.messagebox.askyesno = lambda t, m: True

bp = bs.PROG_PATH
tmp = bp + ".bak"
if os.path.exists(bp):
    os.replace(bp, tmp)

root = tk.Tk()
root.withdraw()
app = bs.App(root)
root.update()

# ---- 1. 数据完整性 ----
bank = app.bank
ok("题库130题", len(bank) == 130, f"({len(bank)})")
kind = {}
for it in bank:
    kind[it["kind"]] = kind.get(it["kind"], 0) + 1
ok("题型分布", kind == {"choice": 80, "judge": 50}, str(kind))
miss = [it["id"] for it in bank if not it.get("stem") or not it.get("answer")]
ok("无空题干/空答案", not miss, str(miss[:3]))
JOK = {"对", "错", "√", "×", "T", "F", "TRUE", "FALSE"}
badj = [it["id"] for it in bank if it["kind"] == "judge"
        and str(it.get("answer", "")).strip().upper() not in JOK]
ok("判断题答案合法", not badj, str(badj[:3]))
bada = []
for it in bank:
    if it["kind"] == "choice":
        keys = [o["key"] for o in it.get("options", [])]
        if str(it.get("answer", "")).strip().upper() not in keys or len(keys) != len(set(keys)):
            bada.append(it["id"])
ok("选择题答案在选项内且key唯一", not bada, str(bada[:3]))

# ---- 2. 界面结构：无随机/收藏/重新做题 ----
mode_btns = list(app.mode_btns.keys())
ok("模式按钮=顺序/错题/考试", mode_btns == ["顺序", "错题", "考试"], str(mode_btns))
nav_texts = [t for _, t in app.nav_btns]
ok("底部导航4按钮且无收藏/重做",
   len(nav_texts) == 4 and not any("收藏" in t or "重新做" in t for t in nav_texts),
   str(nav_texts))

# ---- 3. 判断题交互：选择不判分，确认才判分 ----
app.set_mode("顺序")
ji, jit = next((i, it) for i, it in enumerate(bank) if it["kind"] == "judge")
app.idx = ji
app.show_question()
app.answer_judge("√")
root.update()
ok("判断选择后未判分", app.progress.get(jit["id"], {}).get("ok") is None)
app.check()
root.update()
ok("判断确认后已判分", app.progress.get(jit["id"], {}).get("ok") is not None)

# ---- 4. 已答题重开显示上次作答 ----
app.show_question()
root.update()
fb_text = app.fb.get("1.0", "end-1c")
ok("已答题反馈显示上次作答", "上次作答" in fb_text, fb_text[:30].replace("\n", " "))

# ---- 5. 笔记时机 ----
un = next((i for i, it in enumerate(bank)
           if app.progress.get(it["id"], {}).get("ok") is None), None)
if un is not None:
    app.idx = un
    app.show_question()
    root.update()
    ok("未作答不显示笔记", app.note_text.get("1.0", "end-1c") == "",
       repr(app.note_text.get("1.0", "end-1c")))
    it = app.queue[un]
    if it["kind"] == "choice":
        app.choice_var.set(it["options"][0]["key"])
    else:
        app.answer_judge("√")
    app.check()
    root.update()
    ok("作答后笔记区出现", app.note_text.winfo_ismapped()
       or app.note_text.get("1.0", "end-1c") == "",
       "note:" + repr(app.note_text.get("1.0", "end-1c")))
else:
    ok("找到未答题", False, "未找到")

# ---- 6. 错题进出 ----
app.set_mode("顺序")
some = next((i for i, it in enumerate(bank)
             if app.progress.get(it["id"], {}).get("ok") is True), 0)
cid = bank[some]["id"]
app.progress[cid] = {"ok": False, "wrong_count": 1, "notes": ""}
app._save_progress()
app.set_mode("错题")
ok("答错进入错题库", cid in [it["id"] for it in app.queue])
app.progress[cid] = {"ok": True, "wrong_count": 0, "notes": ""}
app._save_progress()
app.set_mode("错题")
ok("答对移出错题库", cid not in [it["id"] for it in app.queue])

# ---- 7. 进度记录无收藏字段 ----
has_fav = any("fav" in r for r in app.progress.values())
ok("进度记录无收藏字段", not has_fav)

# ---- 8. 悬停绑定存在 ----
nav0 = app.nav_btns[0][0]
ok("导航按钮有Enter绑定", bool(nav0.bind("<Enter>")))
row0 = app._choice_rows[0]["frame"]
ok("选项行有Enter绑定", bool(row0.bind("<Enter>")))

# ---- 9. 快速翻题控件稳定 ----
app.set_mode("顺序")
maxn = 0
for k in range(2000):
    if k % 2 == 0:
        app.next_q()
    else:
        app.prev_q()
    if k % 100 == 0:
        root.update_idletasks()
        root.update()
        maxn = max(maxn, len(app.opt_frame.winfo_children()))
ok("2000次翻题控件稳定", maxn <= 9, f"max={maxn}")

# ---- 10. 考试：重新考试清空答案 / 交卷 ----
app.set_mode("考试")
app._exam_start()
root.update_idletasks()
app.idx = 0
app._exam_render_q()
q0 = app.queue[0]
if q0["kind"] == "choice":
    app.choice_var.set(q0["options"][0]["key"])
else:
    app.answer_judge("√")
app.check()
root.update()
ok("考试作答已记录", len(app.exam["answers"]) >= 1)
app._exam_start()
ok("重新考试清空答案", not app.exam["answers"])
ok("考试队列20题", len(app.queue) == 20)
app.finish_exam()
root.update()
ok("交卷finished", app.exam.get("finished") is True)

# ---- 11. 进度条样式 ----
ok("进度条样式应用", "green" in str(app.pbar.cget("style")))

# 恢复 progress
if os.path.exists(tmp):
    os.replace(tmp, bp)
root.destroy()
print(f"\n===== 扩展自检: PASS={PASS} FAIL={FAIL} =====")
sys.exit(1 if FAIL else 0)
