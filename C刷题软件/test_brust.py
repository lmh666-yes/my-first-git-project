# -*- coding: utf-8 -*-
"""刷题软件自检：题库加载 / 四种模式 / 单选判断简答判分 / 统计 / 进度保存"""
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

root = tk.Tk()
root.withdraw()
app = bs.App(root)
root.update()

# 1. 题库
check(len(app.bank) == 141, f"题库 141 题 (实际 {len(app.bank)})")
kinds = {}
for it in app.bank:
    kinds[it["kind"]] = kinds.get(it["kind"], 0) + 1
check(kinds == {"choice": 80, "judge": 50, "qa": 11}, f"题型分布 {kinds}")
check(all(it["answer"] for it in app.bank if it["kind"] != "qa"), "单选/判断全部有答案")
check(all(it["stem"] for it in app.bank), "全部有题干")

# 2. 顺序模式 + 单选判分
app.set_mode("顺序")
root.update()
check(app.mode == "顺序" and len(app.queue) == 141, "顺序模式 141 题")
it = app.queue[0]
check(it["id"] == "choice-1" and it["kind"] == "choice", "第1题为单选")
# 选正确选项
ans = it["answer"]
app.choice_var.set(ans)
app.check()
root.update()
rec = app.progress.get(it["id"])
check(rec and rec["ok"] is True, f"单选答对记录 ({ans})")
# 选错误
app.idx = 1
app.show_question()
root.update()
it2 = app.queue[1]
wrong = "A" if it2["answer"] != "A" else "B"
app.choice_var.set(wrong)
app.check()
root.update()
check(app.progress[it2["id"]]["ok"] is False, f"单选答错记录 ({it2['answer']} vs {wrong})")

# 3. 判断判分
app.idx = 80   # 判断题第1题
app.show_question()
root.update()
jit = app.queue[80]
check(jit["kind"] == "judge", "第81题(队列中)为判断题")
app.answer_judge(jit["answer"])
root.update()
check(app.progress[jit["id"]]["ok"] is True, f"判断答对记录 ({jit['answer']})")

# 4. 简答
app.idx = 130   # 简答第1题
app.show_question()
root.update()
qit = app.queue[130]
check(qit["kind"] == "qa", "第131题(队列中)为简答题")
app.reveal_qa()
root.update()
fb = app.fb.get("1.0", "end")
check("参考答案" in fb or "未提供" in fb, "简答显示参考答案")
app.mark_qa(True)
root.update()
check(app.progress[qit["id"]]["ok"] is True, "简答标记已掌握")

# 5. 模式切换
app.set_mode("随机")
root.update()
check(app.mode == "随机" and len(app.queue) == 141, "随机模式 141 题")
app.set_mode("错题")
root.update()
check(app.mode == "错题" and len(app.queue) >= 1, f"错题模式收集错题 ({len(app.queue)} 题)")

# 6. 统计
app._update_stat()
root.update()
done = [i for i in app.bank if app.progress.get(i["id"], {}).get("ok") is not None]
check(len(done) >= 4, f"进度统计已做 {len(done)} 题")

# 7. 进度保存
app._save_progress()
check(os.path.exists(bp), "进度已保存 progress.json")
app2 = bs.App(root)
root.update()
check(len(app2.progress) >= 4, "重新加载进度恢复")

# 清理测试进度
root.destroy()
os.remove(bp) if os.path.exists(bp) else None
if os.path.exists(tmp):
    os.replace(tmp, bp)
print()
print("===== 刷题软件自检: %s =====" % ("全部通过" if fails == 0 else f"有 {fails} 个失败"))
sys.exit(fails)
