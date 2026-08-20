# -*- coding: utf-8 -*-
"""刷题软件自检：题库加载 / 模式切换(含考试定时器修复) / 单选判断判分 / 错题次数 /
笔记 / 重置进度 / 统计 / 进度保存"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tkinter as tk
import 刷题软件 as bs

fails = 0
def check(cond, msg):
    global fails
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        fails += 1

# 备份进度
bp = bs.PROG_PATH
tmp = bp + ".bak"
if os.path.exists(bp):
    os.replace(bp, tmp)

# 屏蔽弹窗
bs.messagebox.showinfo = lambda t, m: None
bs.messagebox.showerror = lambda t, m: None
bs.messagebox.askyesno = lambda t, m: True

root = tk.Tk()
root.withdraw()
app = bs.App(root)
root.update()

# 1. 题库（只含选择+判断）
check(len(app.bank) == 130, f"题库 130 题 (实际 {len(app.bank)})")
kinds = {}
for it in app.bank:
    kinds[it["kind"]] = kinds.get(it["kind"], 0) + 1
check(kinds == {"choice": 80, "judge": 50}, f"题型分布 {kinds}")
check(all(it["answer"] for it in app.bank), "全部有答案")
check(all(it["stem"] for it in app.bank), "全部有题干")

# 2. 顺序模式 + 单选判分
app.set_mode("顺序")
root.update()
check(app.mode == "顺序" and len(app.queue) == 130, "顺序模式 130 题")
it = app.queue[0]
check(it["id"] == "choice-1" and it["kind"] == "choice", "第1题为单选")
ans = it["answer"]
app.choice_var.set(ans)
app.check()
root.update()
rec = app.progress.get(it["id"])
check(rec and rec["ok"] is True, f"单选答对记录 ({ans})")
# 答错两次 → 错误次数 = 2
it2 = app.queue[1]
app.idx = 1
app.show_question()
root.update()
wrong = "A" if it2["answer"] != "A" else "B"
for _ in range(2):
    app.choice_var.set(wrong)
    app.check()
    root.update()
rec2 = app.progress[it2["id"]]
check(rec2["ok"] is False and rec2["wrong_count"] == 2,
      f"单选答错+错误次数 (ans={it2['answer']})")
fb = app.fb.get("1.0", "end")
check("累计错误" in fb and "2 次" in fb, "反馈框显示错误次数")

# 3. 判断判分
app.idx = 80   # 判断题第1题
app.show_question()
root.update()
jit = app.queue[80]
check(jit["kind"] == "judge", "第81题(队列中)为判断题")
app.answer_judge(jit["answer"])
root.update()
check(app.progress[jit["id"]]["ok"] is True, f"判断答对记录 ({jit['answer']})")

# 4. 笔记功能（写入/跨题保存/回显）
note_text = "这是我的自定义笔记-测试"
app.idx = 0
app.show_question()
root.update()
app.note_text.delete("1.0", "end")
app.note_text.insert("1.0", note_text)
app._note_edited()
root.update()
app.next_q()
root.update()
check(app.progress.get(it["id"], {}).get("notes") == note_text, "笔记保存到原题")
check(app.note_text.get("1.0", "end-1c") == "", "切换后新题笔记为空")
app.prev_q()
root.update()
check(app.note_text.get("1.0", "end-1c") == note_text, "再次打开笔记回显")

# 5. 模式切换 + 考试定时器不残留（修复切换 bug）
app.set_mode("考试")
root.update()
check(app._exam_timer is not None, "考试模式开启倒计时")
app.set_mode("随机")
root.update()
check(app._exam_timer is None, "切走后倒计时已停止(修复切换bug)")
check(app.mode == "随机" and len(app.queue) == 130, "随机模式 130 题")
app.set_mode("错题")
root.update()
check(app.mode == "错题" and len(app.queue) >= 1,
      f"错题模式收集错题 ({len(app.queue)} 题)")
app.set_mode("顺序")
root.update()

# 6. 重置进度（清除记忆）
app.reset_progress()
root.update()
check(app.progress == {}, "重置后进度清空")
check(app.progress.get(it["id"]) is None, "重置后笔记也清除")

# 7. 统计归零
app._update_stat()
root.update()
done = [i for i in app.bank if app.progress.get(i["id"], {}).get("ok") is not None]
check(len(done) == 0, f"重置后统计归零 (已做 {len(done)})")

# 8. 进度保存/恢复
app.choice_var.set("A" if app.queue[0]["answer"] != "A" else "B")
app.check()
root.update()
app._save_progress()
check(os.path.exists(bp), "进度已保存 progress.json")
app2 = bs.App(root)
root.update()
check(len(app2.progress) == 1, "重新加载进度恢复")

# 清理测试进度
root.destroy()
os.remove(bp) if os.path.exists(bp) else None
if os.path.exists(tmp):
    os.replace(tmp, bp)
print()
print("===== 刷题软件自检: %s =====" % ("全部通过" if fails == 0 else f"有 {fails} 个失败"))
sys.exit(fails)
