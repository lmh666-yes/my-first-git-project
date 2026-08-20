# -*- coding: utf-8 -*-
"""C刷题软件 · 压力测试
覆盖：快速翻题 / 全题库作答 / 模式切换 / 收藏切换 / 随机混合操作 / 控件泄漏检测
用法：python test_stress.py
"""
import sys, io, os, random, faulthandler, tkinter as tk
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
faulthandler.dump_traceback_later(120, exit=True)

import importlib.util
spec = importlib.util.spec_from_file_location("bs", os.path.join(os.path.dirname(os.path.abspath(__file__)), "刷题软件.py"))
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)

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

# 屏蔽 messagebox，避免边界提示阻塞测试
_msgs = []
bs.messagebox.showinfo = lambda t, m: _msgs.append((t, m))
bs.messagebox.showerror = lambda t, m: _msgs.append((t, m))
bs.messagebox.showwarning = lambda t, m: _msgs.append((t, m))

def main():
    root = tk.Tk()
    root.geometry("980x700")
    app = bs.App(root)
    root.update()
    N = len(app.bank)
    ok("题库加载", N == 141, f"({N})")

    # ---- 1. 快速翻题 5000 次 ----
    max_n, nav_lost = 0, 0
    for k in range(5000):
        if k % 2 == 0:
            app.next_q()
        else:
            app.prev_q()
        if k % 50 == 0:
            root.update_idletasks()
            root.update()
            max_n = max(max_n, len(app.opt_frame.winfo_children()))
            for b, _ in app.nav_btns:
                if not b.winfo_ismapped():
                    nav_lost += 1
                    break
    ok("5000次快速翻题无异常", True)
    ok("选项区控件数量稳定(<=9)", max_n <= 9, f"max={max_n}")
    ok("底部导航全程可见(刷新后)", nav_lost == 0, f"lost={nav_lost}")

    # ---- 2. 全题库每题作答 ----
    err = 0
    app.set_mode("顺序")
    for i in range(N):
        app.idx = i
        app.show_question()
        it = app.queue[i]
        try:
            if it["kind"] == "choice":
                app.choice_var.set(it["options"][0]["key"])
                app.check()
            elif it["kind"] == "judge":
                app.answer_judge("√")
            else:
                app.reveal_qa()
                app.mark_qa(True)
        except Exception as e:
            err += 1
            if err <= 3:
                print("    ERR@", i, e)
    ok("全题库作答无异常", err == 0, f"err={err}")

    # ---- 3. 500 次模式切换 ----
    modes = ["顺序", "随机", "错题", "考试", "随机", "顺序"]
    err = 0
    for _ in range(500):
        try:
            app.set_mode(random.choice(modes))
            root.update_idletasks()
        except Exception as e:
            err += 1
            if err <= 3:
                print("    ERR mode:", e)
    ok("500次模式切换无异常", err == 0, f"err={err}")

    # ---- 4. 全题收藏切换 ----
    app.set_mode("顺序")
    err = 0
    for i in range(N):
        try:
            app.idx = i
            app.show_question()
            app.toggle_fav()
        except Exception as e:
            err += 1
    ok("全题收藏切换无异常", err == 0, f"err={err}")

    # ---- 5. 随机混合操作 3000 次 ----
    ops = ["next", "prev", "check", "judge", "reveal", "mark", "fav", "redo"]
    err = 0
    for _ in range(3000):
        op = random.choice(ops)
        try:
            if op == "next":
                app.next_q()
            elif op == "prev":
                app.prev_q()
            elif op == "check":
                app.choice_var.set(random.choice(["A", "B", "C", "D"]))
                app.check()
            elif op == "judge":
                app.answer_judge(random.choice(["√", "×"]))
            elif op == "reveal":
                app.reveal_qa()
            elif op == "mark":
                app.mark_qa(random.choice([True, False]))
            elif op == "fav":
                app.toggle_fav()
            else:
                app.redo_q()
        except Exception as e:
            err += 1
            if err <= 5:
                print("    ERR op:", op, e)
        if random.random() < 0.02:
            root.update_idletasks()
    ok("3000次随机混合操作无异常", err == 0, f"err={err}")

    # ---- 6. 最终状态检查（先刷新布局） ----
    root.update_idletasks()
    root.update()
    mapped = [b.winfo_ismapped() for b, _ in app.nav_btns]
    ok("最终选项区控件数量正常", len(app.opt_frame.winfo_children()) <= 9,
       f"n={len(app.opt_frame.winfo_children())}")
    ok("最终导航栏全部可见", all(mapped), f"{mapped}")
    try:
        app._update_stat()
        ok("统计更新正常", True)
    except Exception as e:
        ok("统计更新正常", False, str(e))
    try:
        app._save_progress()
        ok("进度保存正常", True)
    except Exception as e:
        ok("进度保存正常", False, str(e))

    root.destroy()
    print(f"\n===== 压力测试结果: PASS={PASS} FAIL={FAIL} =====")
    sys.exit(1 if FAIL else 0)

if __name__ == "__main__":
    main()
