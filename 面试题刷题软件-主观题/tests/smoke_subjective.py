# -*- coding: utf-8 -*-
"""主观题版冒烟测试：题库加载 / 首题显示 / 打字作答自动保存 /
查看·收起参考答案 / 切题恢复作答 / 跳题 / 统计 / 重置。

用法：python smoke_subjective.py
"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "core"))
import tkinter as tk
import 主观题软件 as ss

fails = 0
def check(cond, msg, extra=""):
    global fails
    line = ("  [PASS] " if cond else "  [FAIL] ") + msg
    if extra:
        line += " " + str(extra)
    print(line)
    if not cond:
        fails += 1

# 备份用户进度，测试结束恢复
bp = ss.PROG_PATH
tmp = bp + ".bak"
had = os.path.exists(bp)
if had:
    os.replace(bp, tmp)

ss.messagebox.showinfo = lambda t, m: None
ss.messagebox.showerror = lambda t, m: None
ss.messagebox.showwarning = lambda t, m: None
ss.messagebox.askyesno = lambda t, m: True

root = tk.Tk()
root.withdraw()
app = ss.App(root)
root.update()

# 1. 题库
check(len(app.bank) == 399, f"题库 399 题（实际 {len(app.bank)}）")
kinds = {it["kind"] for it in app.bank}
check(kinds == {"subjective"}, f"全部为主观题（{kinds}）")
check(all(it.get("answer") for it in app.bank if it["num"] != 88),
      "每题均有参考答案（第 88 题为同题引用，除外）")

# 2. 首题显示
it = app.queue[0]
check("主观题" in app.head_label.cget("text"), f"题头标注（{app.head_label.cget('text')}）")
check(app.stem.get("1.0", "end").strip().startswith("C 语言中的 volatile"),
      "第 1 题题干正确显示")

# 3. 打字作答 + 自动保存
app.ans_text.insert("1.0", "volatile 防止编译器优化，每次从内存读取。")
app._save_answer()
check(app.progress.get(it["id"], {}).get("wrote", "").startswith("volatile"),
      "作答自动保存到进度")

# 4. 查看 / 收起参考答案
app.toggle_reveal()
root.update()
fb = app.fb.get("1.0", "end")
check("参考答案" in fb and "得分点" in fb, "查看答案显示参考答案+得分点")
check(app.progress[it["id"]]["revealed"] is True, "已看答案被记录")
check("收起" in app.reveal_btn.cget("text"), "按钮切换为收起")
app.toggle_reveal()
root.update()
check("点「查看参考答案」" in app.fb.get("1.0", "end"), "收起后恢复提示")
check(app.revealed is False, "收起状态正确")

# 5. 导航 + 切题恢复作答
app.next_q()
root.update()
check(app.idx == 1, "下一题")
app.ans_text.insert("1.0", "第二题作答")
app.prev_q()
root.update()
check(app.idx == 0, "上一题")
check("volatile" in app.ans_text.get("1.0", "end"), "切题后作答内容恢复")
app.next_q()
root.update()
check("第二题作答" in app.ans_text.get("1.0", "end"), "第二题作答也已保存")

# 6. 跳题
app.jump_var.set("33")
app._jump()
root.update()
check(app.queue[app.idx]["num"] == 33, f"按题号跳转（当前 {app.queue[app.idx]['num']}）")
app.jump_var.set("9999")
app._jump()
check(app.queue[app.idx]["num"] == 33, "无效题号不改变位置")

# 7. 统计
app._update_stat()
root.update()
txt = app.stat_label.cget("text")
check("已看答案" in txt and "已作答" in txt, f"统计显示（{txt}）")

# 8. 模拟考试
app.set_mode("考试")
root.update()
check("考试说明" in app.stem.get("1.0", "end"), "进入考试待开始页")
app._exam_start()
root.update()
check(len(app.queue) == 10, "开考后 10 题", f"({len(app.queue)})")
check(app.exam_left > 39 * 60 - 5, "倒计时约 40 分钟", f"({app.exam_left})")
it0 = app.queue[0]
app.ans_text.insert("1.0", "我的考试作答")
app._save_answer()
check(app.progress.get(it0["id"], {}).get("wrote", "").startswith("我的考试作答"),
      "考试作答已保存", app.progress.get(it0["id"], {}).get("wrote", "")[:20])
app.next_q()
root.update()
check(app.idx == 1, "考试下一题", f"({app.idx})")
app.prev_q()
root.update()
check("我的考试作答" in app.ans_text.get("1.0", "end"), "考试切回后作答恢复")
app._exam_toggle_pause()
root.update()
check(app._exam_paused() and "已暂停" in app.head_label.cget("text"), "暂停成功")
app._exam_toggle_pause()
root.update()
check(app._exam_running(), "继续成功")
n_before = app.progress.get("_exam_count", 0)
app.finish_exam()
root.update()
check(app._exam_finished(), "交卷完成")
check(app.progress.get("_exam_count", 0) == n_before + 1, "交卷计入考试次数")
check("考试结束" in app.head_label.cget("text"), "跳转成绩页")
app._exam_review(it0["id"])
root.update()
fb = app.fb.get("1.0", "end")
check("参考答案" in fb and "得分点" in fb, "回顾显示参考答案+得分点")
check("我的考试作答" in app.ans_text.get("1.0", "end"), "回顾显示我的作答（只读）")
app._exam_restart_to_ready()
root.update()
check("考试说明" in app.stem.get("1.0", "end") and not app._exam_active(), "重新考试回待开始页")

# 9. 计划式抽题：10 次考试覆盖 100 题不重复
seen = set()
for k in range(10):
    app._exam_start()
    seen.update(it["id"] for it in app.queue)
    app.finish_exam()
    root.update()
check(len(seen) == 100, "10 次考试抽题 100 个不重复", f"({len(seen)})")

# 10. 重置
app._confirm_cool_down = lambda seconds=5: True
app.reset_progress()
root.update()
check(app.progress == {}, "重置清空全部记录")
check(app.idx == 0, "重置后回到第 1 题")

root.destroy()

# 恢复用户进度
if had:
    os.replace(tmp, bp)
elif os.path.exists(bp):
    os.remove(bp)

print()
print(f"结果：{'全部通过 ✔' if fails == 0 else f'{fails} 项失败 ✘'}")
sys.exit(1 if fails else 0)
