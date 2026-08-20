# -*- coding: utf-8 -*-
"""C 语言刷题软件 · 类似软考通
题库来源：题库.json（由 build_bank.py 从 docx 生成）
功能：顺序/随机/错题/考试；判分+解析+统计+收藏+错题本+笔记+重置进度。
考试：20 分钟 / 20 题 / 每题 5 分；右上角开始考试；可暂停/退出；中断自动保存、下次打开恢复；
      出成绩后可点击错题号回顾；考试中禁止切换板块；关闭程序有提醒。
版本：1.0.8"""
import sys, io, os, json, random, time
import tkinter as tk
from tkinter import ttk, messagebox

HERE = os.path.dirname(os.path.abspath(__file__))
BANK_PATH = os.path.join(HERE, "题库.json")
PROG_PATH = os.path.join(HERE, "progress.json")

COLOR_OK = "#1a7f37"
COLOR_NO = "#c62828"
COLOR_BLUE = "#1a5276"
EXAM_MIN = 20          # 考试时长（分钟）
EXAM_NUM = 20          # 考试题数
EXAM_SCORE = 5         # 每题分值


def load_bank():
    """加载题库；损坏/空/缺失时返回 []（由调用方提示），不崩溃"""
    if not os.path.exists(BANK_PATH):
        return []
    try:
        with open(BANK_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def load_progress():
    if os.path.exists(PROG_PATH):
        try:
            with open(PG_PATH := PROG_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("C 语言刷题软件")
        self.root.geometry("1180x720")
        self.bank = load_bank()
        if not self.bank:
            messagebox.showerror("题库错误",
                                 "题库为空或损坏，请重新运行 build_bank.py 生成题库。")
        self.progress = load_progress()
        # 考试会话（持久化在 progress["exam"]，强制关闭后可恢复）
        ex = self.progress.get("exam")
        self.exam = ex if isinstance(ex, dict) else {}
        self.mode = "顺序"
        self.queue = []
        self.idx = 0
        self.choice_var = tk.StringVar()
        self.exam_left = 0
        self._exam_timer = None
        self._note_save_job = None
        self._build_ui()
        # 有未完成/未结算的考试 → 直接进入考试板块恢复
        if self.exam.get("active"):
            self.set_mode("考试")
        else:
            self.set_mode("顺序")
        self.show_question()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        """关闭程序：考试中先提醒；是则保存退出，否则继续"""
        if self.mode == "考试" and self._exam_active() and not self._exam_finished():
            self._stop_exam_timer()
            self.exam["paused"] = True
            self.exam["left"] = self.exam_left
            self._save_exam()
            if not messagebox.askyesno(
                    "退出程序",
                    "当前正在考试，确定要退出吗？\n（考试已自动保存为暂停，下次打开会直接回到考试）"):
                # 点“否”：恢复考试继续
                self.exam["paused"] = False
                self._save_exam()
                self._exam_tick()
                self._exam_render_q()
                return
        self._save_note()
        self._save_progress()
        self.root.destroy()

    # ---------- UI ----------
    def _build_ui(self):
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        # 顶部栏
        bar = tk.Frame(self.root, bg="#2c3e50")
        bar.grid(row=0, column=0, sticky="ew")
        tk.Label(bar, text="🎯 C 语言刷题", bg="#2c3e50", fg="white",
                 font=("Microsoft YaHei", 13, "bold"), padx=12).pack(side=tk.LEFT, pady=6)
        self.mode_btns = {}
        for m in ("顺序", "随机", "错题", "考试"):
            b = tk.Button(bar, text=m, command=lambda mm=m: self.set_mode(mm),
                          relief=tk.FLAT, padx=10, cursor="hand2",
                          font=("Microsoft YaHei", 10))
            b.pack(side=tk.LEFT, padx=3, pady=6)
            self.mode_btns[m] = b
        # 右上角：考试上下文按钮区（开始/暂停/退出/重新考试）
        self.exam_bar = tk.Frame(bar, bg="#2c3e50")
        self.exam_bar.pack(side=tk.RIGHT, padx=8)
        self.stat_label = tk.Label(bar, text="", bg="#2c3e50", fg="#ecf0f1",
                                   font=("Microsoft YaHei", 10, "bold"))
        self.stat_label.pack(side=tk.RIGHT, padx=12)

        # 进度条
        self.pbar = ttk.Progressbar(self.root, maximum=100, value=0)
        self.pbar.grid(row=1, column=0, sticky="ew")

        # 主体：左=题目区，右=笔记区
        body = tk.Frame(self.root, bg="#ffffff")
        body.grid(row=2, column=0, sticky="nsew")
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=1)

        left = tk.Frame(body, bg="#ffffff")
        left.grid(row=0, column=0, sticky="nsew")
        right = tk.Frame(body, bg="#fdf6e3", bd=1, relief=tk.GROOVE)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self.head_label = tk.Label(left, text="", bg="#eaf2f8", fg=COLOR_BLUE,
                                   font=("Microsoft YaHei", 12, "bold"),
                                   anchor="w", padx=12, pady=6)
        self.head_label.pack(fill=tk.X)
        self.stem = tk.Text(left, font=("Consolas", 12), wrap="word",
                            bg="#ffffff", relief=tk.FLAT, padx=14, pady=8,
                            height=7, state=tk.DISABLED)
        self.stem.pack(fill=tk.X, pady=(4, 0))

        self.opt_frame = tk.Frame(left, bg="#ffffff")
        self.opt_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        self.opt_widgets = []

        self.fb = tk.Text(left, font=("Microsoft YaHei", 11), wrap="word",
                          height=7, relief=tk.GROOVE, bd=1, padx=10, pady=6)
        self.fb.pack(fill=tk.X, padx=10, pady=(2, 6))

        # 右：笔记区
        tk.Label(right, text="📝 我的笔记", bg="#fdf6e3", fg="#7b5804",
                 font=("Microsoft YaHei", 11, "bold"), anchor="w",
                 padx=8, pady=6).pack(fill=tk.X)
        self.note_text = tk.Text(right, font=("Microsoft YaHei", 10), wrap="word",
                                 bg="#fffdf5", relief=tk.FLAT, padx=8, pady=6)
        self.note_text.pack(fill=tk.BOTH, expand=True)
        self.note_text.bind("<KeyRelease>", lambda e: self._note_edited())
        tk.Label(right, text="笔记自动保存，下次做到这题自动显示",
                 bg="#fdf6e3", fg="#a08030", font=("Microsoft YaHei", 8),
                 anchor="w", padx=8, pady=4).pack(fill=tk.X)

        # 底部导航
        nav = tk.Frame(self.root, bg="#f0f0f0")
        nav.grid(row=3, column=0, sticky="ew")
        self.nav_btns = []
        for txt, fn, color in (("◀ 上一题", self.prev_q, COLOR_BLUE),
                               ("确认答案", self.check, COLOR_BLUE),
                               ("下一题 ▶", self.next_q, COLOR_BLUE),
                               ("⭐ 收藏", self.toggle_fav, "#8e44ad"),
                               ("重新做题", self.redo_q, "#b9770e"),
                               ("🗑 重置进度", self.reset_progress, COLOR_NO)):
            b = tk.Button(nav, text=txt, command=fn, bg=color, fg="white",
                          cursor="hand2", padx=12, pady=5,
                          font=("Microsoft YaHei", 10))
            b.pack(side=tk.LEFT, padx=4, pady=6)
            self.nav_btns.append((b, txt))

    # ---------- 模式 ----------
    def set_mode(self, mode):
        self._save_note()
        # 考试中禁止切换其他板块
        if (self.mode == "考试" and mode != "考试"
                and self._exam_active() and not self._exam_finished()):
            messagebox.showwarning("考试中", "考试进行中，不能切换到其他板块！\n请先交卷或退出考试。")
            return
        self._stop_exam_timer()
        self.mode = mode
        for m, b in self.mode_btns.items():
            b.config(bg="#34495e", fg="white")
        self.mode_btns[mode].config(bg="#1a5276", fg="white")
        if mode == "顺序":
            self.queue = list(self.bank)
        elif mode == "随机":
            q = list(self.bank)
            random.shuffle(q)
            self.queue = q
        elif mode == "错题":
            wrong = [it for it in self.bank
                     if self.progress.get(it.get("id", ""), {}).get("ok") is False]
            self.queue = wrong
            if not wrong:
                messagebox.showinfo("错题本", "太棒了，当前没有错题！")
        elif mode == "考试":
            self._enter_exam_board()
            return
        # 非考试板块：清空右上角考试按钮
        for w in self.exam_bar.winfo_children():
            w.destroy()
        self.idx = 0
        self.show_question()

    # ---------- 考试 ----------
    def _stop_exam_timer(self):
        """取消考试倒计时定时器"""
        if self._exam_timer:
            try:
                self.root.after_cancel(self._exam_timer)
            except Exception:
                pass
            self._exam_timer = None

    def _exam_active(self):
        return bool(self.exam.get("active"))

    def _exam_finished(self):
        return self._exam_active() and bool(self.exam.get("finished"))

    def _exam_running(self):
        return self._exam_active() and not self.exam.get("finished") and not self.exam.get("paused")

    def _exam_paused(self):
        return self._exam_active() and not self.exam.get("finished") and bool(self.exam.get("paused"))

    def _exam_qlist(self):
        ids = set(self.exam.get("ids", []))
        return [it for it in self.bank if it.get("id") in ids]

    def _by_id(self, qid):
        for it in self.bank:
            if it.get("id") == qid:
                return it
        return None

    def _save_exam(self):
        self.progress["exam"] = self.exam
        self._save_progress()

    def _enter_exam_board(self):
        """进入考试板块：按会话状态显示 待开始/继续/成绩"""
        if not self._exam_active():
            self._exam_show_ready()
        elif self._exam_finished():
            self._exam_show_result_page()
        else:
            self.queue = self._exam_qlist()
            self.idx = self.exam.get("idx", 0)
            if self.idx >= len(self.queue):
                self.idx = len(self.queue) - 1
            self.exam_left = self.exam.get("left", EXAM_MIN * 60)
            if self._exam_paused():
                self._exam_render_paused()
            else:
                self._exam_tick()
                self._exam_render_q()

    def _exam_update_topbar(self):
        """刷新右上角考试按钮（只在考试板块显示）"""
        for w in self.exam_bar.winfo_children():
            w.destroy()
        if self.mode != "考试":
            return
        if not self._exam_active():
            b = tk.Button(self.exam_bar, text="▶ 开始考试", command=self._exam_start,
                          bg="#1a5276", fg="white", cursor="hand2", padx=12,
                          font=("Microsoft YaHei", 10))
            b.pack(side=tk.LEFT, padx=3)
        elif self._exam_finished():
            b = tk.Button(self.exam_bar, text="🔄 重新考试", command=self._exam_start,
                          bg="#b9770e", fg="white", cursor="hand2", padx=12,
                          font=("Microsoft YaHei", 10))
            b.pack(side=tk.LEFT, padx=3)
        else:
            if self._exam_paused():
                b1 = tk.Button(self.exam_bar, text="▶ 继续考试", command=self._exam_toggle_pause,
                               bg="#1a5276", fg="white", cursor="hand2", padx=12,
                               font=("Microsoft YaHei", 10))
            else:
                b1 = tk.Button(self.exam_bar, text="⏸ 暂停考试", command=self._exam_toggle_pause,
                               bg="#b9770e", fg="white", cursor="hand2", padx=12,
                               font=("Microsoft YaHei", 10))
            b1.pack(side=tk.LEFT, padx=3)
            b2 = tk.Button(self.exam_bar, text="🚪 退出考试", command=self._exam_quit,
                           bg=COLOR_NO, fg="white", cursor="hand2", padx=12,
                           font=("Microsoft YaHei", 10))
            b2.pack(side=tk.LEFT, padx=3)

    def _exam_show_ready(self):
        """待开始页"""
        self._exam_update_topbar()
        for w in self.opt_frame.winfo_children():
            w.destroy()
        self.opt_widgets = []
        self.choice_var.set("")
        self.head_label.config(text="📝 模拟考试")
        self._set_stem(
            "考试说明：\n\n"
            f"· 共 {EXAM_NUM} 题（单选+判断），限时 {EXAM_MIN} 分钟\n"
            f"· 每题 {EXAM_SCORE} 分，满分 {EXAM_NUM * EXAM_SCORE} 分\n"
            "· 每题只能作答一次，答错会自动进入错题库\n"
            "· 考试中可暂停 / 退出；强制关闭程序会自动保存，下次打开继续\n"
            "· 考试中不能切换到其他板块\n\n"
            "点击右上角「▶ 开始考试」按钮开始。")
        self.fb.config(state=tk.NORMAL)
        self.fb.delete("1.0", "end")
        self.fb.config(state=tk.DISABLED)
        self._add_btn("点击右上角「▶ 开始考试」按钮开始考试。", COLOR_BLUE, False)
        self._update_stat()

    def _exam_start(self):
        """开始 / 重新开始考试"""
        self._stop_exam_timer()
        self.mode = "考试"
        q = [it for it in self.bank if it.get("kind") in ("choice", "judge")]
        n = min(EXAM_NUM, len(q))
        random.shuffle(q)
        ids = [it["id"] for it in q[:n]]
        self.exam = {"active": True, "finished": False, "paused": False,
                     "ids": ids, "idx": 0, "left": EXAM_MIN * 60, "answers": {}}
        self.queue = [it for it in self.bank if it.get("id") in ids]
        self.idx = 0
        self.exam_left = EXAM_MIN * 60
        self._save_exam()
        self._exam_update_topbar()
        self._exam_tick()
        self._exam_render_q()

    def _exam_tick(self):
        if self.mode != "考试" or not self._exam_running():
            self._exam_timer = None
            return
        if self.exam_left <= 0:
            self.finish_exam()
            return
        self.exam_left -= 1
        self.exam["left"] = self.exam_left
        mm, ss = divmod(self.exam_left, 60)
        self.head_label.config(
            text=f"⏱ 模拟考试 · 剩余 {mm:02d}:{ss:02d} · 第 {self.idx + 1}/{len(self.queue)} 题")
        self._exam_timer = self.root.after(1000, self._exam_tick)

    def _exam_render_q(self):
        """考试模式显示当前题（含已作答态）"""
        if not self.queue or not (0 <= self.idx < len(self.queue)):
            return
        it = self.queue[self.idx]
        self.exam["idx"] = self.idx
        mm, ss = divmod(self.exam_left, 60)
        self.head_label.config(
            text=f"⏱ 模拟考试 · 剩余 {mm:02d}:{ss:02d} · 第 {self.idx + 1}/{len(self.queue)} 题")
        self._set_stem(str(it.get("stem", "")))
        self.fb.config(state=tk.NORMAL)
        self.fb.delete("1.0", "end")
        answers = self.exam.get("answers", {})
        sel = answers.get(it.get("id"))
        if sel is not None:
            ok = self._is_ok(it, sel)
            tag = "✅ 正确" if ok else "❌ 错误"
            self.fb.insert(tk.END, f"已作答：{sel} · {tag}（此题不可更改）\n")
        else:
            self.fb.insert(tk.END, "请作答（每题只能答一次）\n")
        self.fb.config(state=tk.DISABLED)
        self._render_options(it, exam_answered=sel)
        self._update_stat()

    def _exam_render_paused(self):
        """暂停页"""
        self._exam_update_topbar()
        for w in self.opt_frame.winfo_children():
            w.destroy()
        self.opt_widgets = []
        self.choice_var.set("")
        mm, ss = divmod(self.exam_left, 60)
        self.head_label.config(text="⏸ 考试已暂停")
        done = len(self.exam.get("answers", {}))
        self._set_stem(
            f"考试已暂停。\n\n剩余时间：{mm:02d}:{ss:02d}\n"
            f"已完成 {done}/{len(self._exam_qlist())} 题\n\n"
            "点击顶部「▶ 继续考试」恢复答题。")
        self.fb.config(state=tk.NORMAL)
        self.fb.delete("1.0", "end")
        self.fb.config(state=tk.DISABLED)
        self._update_stat()

    def _exam_toggle_pause(self):
        if self._exam_paused():
            self.exam["paused"] = False
            self._save_exam()
            self._exam_tick()
            self._exam_render_q()
        else:
            self._stop_exam_timer()
            self.exam["paused"] = True
            self.exam["left"] = self.exam_left
            self._save_exam()
            self._exam_render_paused()
        self._exam_update_topbar()

    def _exam_quit(self):
        """退出考试（作废）"""
        if not messagebox.askyesno("退出考试", "确定要退出考试吗？本次考试将作废。"):
            return
        self._stop_exam_timer()
        self.exam = {}
        self.progress.pop("exam", None)
        self._save_progress()
        self.set_mode("顺序")

    def _exam_answer(self, it, sel):
        """考试中作答（每题一次，答错自动进错题库）"""
        answers = self.exam.setdefault("answers", {})
        qid = it.get("id", "")
        if qid in answers:
            messagebox.showinfo("提示", "本题已作答，不能更改")
            return
        ok = self._is_ok(it, sel)
        answers[qid] = sel
        self.exam["left"] = self.exam_left
        self._save_exam()
        self.record(qid, ok)
        self._exam_render_q()

    def _is_ok(self, it, sel):
        ans = str(it.get("answer", "")).upper().strip()
        sel = str(sel).strip()
        return (sel == ans) or \
               (sel == "√" and ans in ("对", "T", "TRUE", "√")) or \
               (sel == "×" and ans in ("错", "F", "FALSE", "×"))

    def finish_exam(self):
        """交卷计分：每题 EXAM_SCORE 分"""
        self._stop_exam_timer()
        if not self._exam_active() or self.exam.get("finished"):
            return
        self.exam["finished"] = True
        self.exam["paused"] = False
        self.exam["left"] = self.exam_left
        self._save_exam()
        self._exam_show_result_page()

    def _exam_show_result_page(self):
        """成绩页：分数 + 错题号按钮（点击回顾）"""
        self._stop_exam_timer()
        self._exam_update_topbar()
        for w in self.opt_frame.winfo_children():
            w.destroy()
        self.opt_widgets = []
        self.choice_var.set("")
        answers = self.exam.get("answers", {})
        qs = self._exam_qlist()
        total = len(qs)
        correct = sum(1 for it in qs if self._is_ok(it, answers.get(it.get("id"))))
        wrong = [it for it in qs
                 if it.get("id") in answers and not self._is_ok(it, answers.get(it.get("id")))]
        unanswered = [it for it in qs if it.get("id") not in answers]
        score = correct * EXAM_SCORE
        self.head_label.config(text="🏁 考试结束")
        self._set_stem(f"🏆 考试成绩：{score} 分 / 满分 {total * EXAM_SCORE} 分\n\n"
                       f"✅ 答对 {correct} 题 · ❌ 答错 {len(wrong)} 题 · ⭕ 未答 {len(unanswered)} 题")
        self.fb.config(state=tk.NORMAL)
        self.fb.delete("1.0", "end")
        self.fb.insert(tk.END,
                       f"得分：{score} 分（每题 {EXAM_SCORE} 分）　"
                       f"答题进度：{len(answers)}/{total}\n\n"
                       "错题已自动进入「错题」板块，可随时重做。")
        self.fb.config(state=tk.DISABLED)
        self._add_btn(f"🏆 成绩：{score} 分（答对 {correct}/{total}）",
                      COLOR_OK if score >= total * EXAM_SCORE * 0.6 else COLOR_NO, False)
        if wrong:
            self._add_btn("📌 点击错题号回顾题目与答案：", COLOR_NO, False)
            # 用 grid 每行 6 个按钮自动换行，避免错题多时挤在一起
            cols = 6
            for k, it in enumerate(wrong):
                if k % cols == 0:
                    row = tk.Frame(self.opt_frame, bg="#ffffff")
                    row.pack(fill=tk.X, pady=2)
                    self.opt_widgets.append(row)
                b = tk.Button(row, text=f"错题 {it.get('num', '?')}", width=9,
                              command=lambda q=it.get("id"): self._exam_review(q),
                              bg=COLOR_NO, fg="white", cursor="hand2",
                              font=("Microsoft YaHei", 10))
                b.grid(row=0, column=k % cols, padx=4, pady=3)
                self.opt_widgets.append(b)
        else:
            self._add_btn("🎉 全部答对，太棒了！", COLOR_OK, False)
        self._update_stat()

    def _exam_review(self, qid):
        """回顾错题：显示题干/选项/正确答案/你的答案 + 返回成绩"""
        it = self._by_id(qid)
        if not it:
            return
        for w in self.opt_frame.winfo_children():
            w.destroy()
        self.opt_widgets = []
        self.choice_var.set("")
        self.head_label.config(text=f"📖 错题回顾 · 第 {it.get('num', '?')} 题")
        self._set_stem(str(it.get("stem", "")))
        ans = str(it.get("answer", "")).upper().strip()
        your = self.exam.get("answers", {}).get(qid, "")
        if it.get("kind") == "choice":
            for o in it.get("options", []):
                k = o.get("key", "?")
                mark, color = "", "#000000"
                if k == ans:
                    mark, color = "  ← 正确答案", COLOR_OK
                elif str(k) == str(your):
                    mark, color = "  ← 你的答案", COLOR_NO
                self._add_btn(f"{k}. {o.get('text', '')}{mark}", color, False)
        else:
            self._add_btn(f"正确答案：{ans}", COLOR_OK, False)
            if your:
                self._add_btn(f"你的答案：{your}", COLOR_NO if your != ans else COLOR_OK, False)
        if it.get("explain"):
            self._add_btn("解析：" + it.get("explain", ""), COLOR_BLUE, False)
        b = tk.Button(self.opt_frame, text="⬅ 返回成绩", command=self._exam_show_result_page,
                      bg=COLOR_BLUE, fg="white", cursor="hand2", padx=16, pady=6,
                      font=("Microsoft YaHei", 10))
        b.pack(pady=8)
        self.opt_widgets.append(b)
        self.fb.config(state=tk.NORMAL)
        self.fb.delete("1.0", "end")
        self.fb.insert(tk.END, f"你的答案：{your or '未作答'}　正确答案：{ans}")
        self.fb.config(state=tk.DISABLED)
        self._update_stat()

    # ---------- 题目显示 ----------
    def show_question(self):
        if not self.queue:
            return
        if self.idx >= len(self.queue):
            self.idx = len(self.queue) - 1
        if self.idx < 0:
            self.idx = 0
        it = self.queue[self.idx]
        if self.mode != "考试":
            self.head_label.config(text=f"[{it.get('kind_name', it.get('kind', '?'))} "
                                        f"{it.get('num', '')}]  "
                                        f"{self.idx + 1}/{len(self.queue)}")
        self._set_stem(str(it.get("stem", "")))
        self.fb.config(state=tk.NORMAL)
        self.fb.delete("1.0", "end")
        rec = self.progress.get(it.get("id", ""), {})
        if rec.get("ok") is True:
            self.fb.insert(tk.END, "✅ 上次作答：正确\n")
        elif rec.get("ok") is False:
            self.fb.insert(tk.END, "❌ 上次作答：错误\n")
        else:
            self.fb.insert(tk.END, "未作答\n")
        wc = rec.get("wrong_count", 0)
        if wc:
            self.fb.insert(tk.END, f"🔁 本题累计错误：{wc} 次\n")
        if rec.get("fav"):
            self.fb.insert(tk.END, "⭐ 已收藏\n")
        self.fb.config(state=tk.DISABLED)
        self._render_options(it)
        self._load_note(it.get("id", ""))
        self._update_stat()

    def _set_stem(self, text):
        self.stem.config(state=tk.NORMAL)
        self.stem.delete("1.0", "end")
        self.stem.insert("1.0", text)
        self.stem.config(state=tk.DISABLED)

    def _render_options(self, it, exam_answered=None):
        for w in self.opt_frame.winfo_children():
            w.destroy()
        self.opt_widgets = []
        self.choice_var.set("")
        kind = it.get("kind", "qa")
        if kind == "choice":
            if exam_answered is not None:
                ans = str(it.get("answer", "")).upper().strip()
                self._add_btn("本题已作答：", COLOR_BLUE, False)
                for o in it.get("options", []):
                    k = o.get("key", "?")
                    mark, color = "", "#000000"
                    if str(k) == ans:
                        mark, color = "  ← 正确答案", COLOR_OK
                    elif str(k) == str(exam_answered):
                        mark, color = "  ← 你的答案", COLOR_NO
                    self._add_btn(f"{k}. {o.get('text', '')}{mark}", color, False)
            else:
                self._add_btn("请选择答案：", COLOR_BLUE, False)
                for o in it.get("options", []):
                    rb = tk.Radiobutton(
                        self.opt_frame, text=f"{o.get('key', '?')}. {o.get('text', '')}",
                        variable=self.choice_var, value=o.get("key", "?"),
                        font=("Microsoft YaHei", 11), anchor="w", padx=6)
                    rb.pack(fill=tk.X, pady=2)
                    self.opt_widgets.append(rb)
        elif kind == "judge":
            if exam_answered is not None:
                ans = str(it.get("answer", "")).upper().strip()
                self._add_btn("本题已作答：", COLOR_BLUE, False)
                self._add_btn(f"正确答案：{ans}", COLOR_OK, False)
                self._add_btn(f"你的答案：{exam_answered}",
                              COLOR_NO if str(exam_answered) != ans else COLOR_OK, False)
            else:
                self._add_btn("请判断对错：", COLOR_BLUE, False)
                for txt, key in (("✔ 正确", "√"), ("✘ 错误", "×")):
                    b = tk.Button(self.opt_frame, text=txt, command=lambda k=key: self.answer_judge(k),
                                  width=14, cursor="hand2", font=("Microsoft YaHei", 11),
                                  bg="#34495e", fg="white")
                    b.pack(side=tk.LEFT, padx=10, pady=8)
                    self.opt_widgets.append(b)
        else:
            self._add_btn("简答/编程题：先自行作答，再点「查看答案」对照。",
                          "#8e44ad", disabled=False)
            b = tk.Button(self.opt_frame, text="查看答案", command=self.reveal_qa,
                          cursor="hand2", font=("Microsoft YaHei", 11),
                          bg="#8e44ad", fg="white", padx=16, pady=6)
            b.pack(pady=8)
            self.opt_widgets.append(b)
            b2 = tk.Button(self.opt_frame, text="已掌握 ✔", command=lambda: self.mark_qa(True),
                           cursor="hand2", font=("Microsoft YaHei", 11),
                           bg=COLOR_OK, fg="white", padx=12, pady=6)
            b2.pack(side=tk.LEFT, padx=8)
            b3 = tk.Button(self.opt_frame, text="还需复习 ✘", command=lambda: self.mark_qa(False),
                           cursor="hand2", font=("Microsoft YaHei", 11),
                           bg=COLOR_NO, fg="white", padx=12, pady=6)
            b3.pack(side=tk.LEFT, padx=8)
            self.opt_widgets += [b2, b3]

    def _add_btn(self, text, color, disabled):
        lbl = tk.Label(self.opt_frame, text=text, font=("Microsoft YaHei", 11, "bold"),
                       fg=color, anchor="w")
        lbl.pack(fill=tk.X, pady=(6, 2))
        self.opt_widgets.append(lbl)

    # ---------- 作答 ----------
    def check(self):
        it = self.queue[self.idx]
        if it.get("kind") != "choice":
            return
        sel = self.choice_var.get()
        if not sel:
            messagebox.showinfo("提示", "请先选择一个答案")
            return
        if self.mode == "考试":
            self._exam_answer(it, sel)
            return
        self.record(it.get("id", ""), sel == str(it.get("answer", "")).upper())
        self._show_result(it, sel)
        self._update_stat()

    def answer_judge(self, key):
        it = self.queue[self.idx]
        if self.mode == "考试":
            self._exam_answer(it, key)
            return
        ans = str(it.get("answer", "")).strip()
        ok = (key == ans) or (key == "√" and ans in ("对", "T", "true", "√")) \
             or (key == "×" and ans in ("错", "F", "false", "×"))
        self.record(it.get("id", ""), ok)
        rec = self.progress.get(it.get("id", ""), {})
        wc = rec.get("wrong_count", 0)
        self.fb.config(state=tk.NORMAL)
        self.fb.delete("1.0", "end")
        tag = "✅ 回答正确" if ok else "❌ 回答错误"
        self.fb.insert(tk.END, tag + f"（你的答案：{key}，正确答案：{ans}）\n")
        if wc:
            self.fb.insert(tk.END, f"🔁 本题累计错误：{wc} 次\n")
        if it.get("explain"):
            self.fb.insert(tk.END, "\n解析：\n" + it.get("explain", ""))
        self.fb.config(state=tk.DISABLED)
        self._update_stat()

    def reveal_qa(self):
        it = self.queue[self.idx]
        self.fb.config(state=tk.NORMAL)
        self.fb.delete("1.0", "end")
        if it.get("answer") or it.get("explain"):
            self.fb.insert(tk.END, "参考答案：\n" + (it.get("answer") or it.get("explain", "")))
        else:
            self.fb.insert(tk.END, "（原文档未提供答案）")
        self.fb.config(state=tk.DISABLED)

    def mark_qa(self, ok):
        it = self.queue[self.idx]
        self.record(it.get("id", ""), ok)
        self.fb.config(state=tk.NORMAL)
        self.fb.delete("1.0", "end")
        self.fb.insert(tk.END, "✅ 已标记为掌握" if ok else "❌ 已标记为需复习")
        self.fb.config(state=tk.DISABLED)
        self._update_stat()

    def record(self, qid, ok):
        rec = self.progress.setdefault(qid, {"ok": None, "fav": False,
                                             "wrong_count": 0, "notes": ""})
        rec["ok"] = ok
        if not ok:
            rec["wrong_count"] = rec.get("wrong_count", 0) + 1
        self._save_progress()

    def _show_result(self, it, sel):
        ans = str(it.get("answer", "")).upper()
        rec = self.progress.get(it.get("id", ""), {})
        wc = rec.get("wrong_count", 0)
        self.fb.config(state=tk.NORMAL)
        self.fb.delete("1.0", "end")
        if sel == ans:
            self.fb.insert(tk.END, "✅ 回答正确！\n", ("ok",))
        else:
            self.fb.insert(tk.END, f"❌ 回答错误。正确答案：{ans}（你选了 {sel}）\n", ("no",))
        if wc:
            self.fb.insert(tk.END, f"🔁 本题累计错误：{wc} 次\n")
        self.fb.tag_configure("ok", foreground=COLOR_OK)
        self.fb.tag_configure("no", foreground=COLOR_NO)
        if it.get("explain"):
            self.fb.insert(tk.END, "\n解析：\n" + it.get("explain", ""))
        self.fb.config(state=tk.DISABLED)

    # ---------- 笔记 ----------
    def _note_edited(self):
        it = self._cur_item()
        if it is None:
            return
        qid = it.get("id", "")
        rec = self.progress.setdefault(qid, {"ok": None, "fav": False,
                                             "wrong_count": 0, "notes": ""})
        rec["notes"] = self.note_text.get("1.0", "end-1c")
        if self._note_save_job:
            try:
                self.root.after_cancel(self._note_save_job)
            except Exception:
                pass
        self._note_save_job = self.root.after(800, self._save_progress)

    def _cur_item(self):
        if self.queue and 0 <= self.idx < len(self.queue):
            return self.queue[self.idx]
        return None

    def _load_note(self, qid):
        if self._note_save_job:
            try:
                self.root.after_cancel(self._note_save_job)
            except Exception:
                pass
            self._note_save_job = None
        self.note_text.delete("1.0", "end")
        rec = self.progress.get(qid, {})
        self.note_text.insert("1.0", rec.get("notes", ""))

    def _save_note(self):
        it = self._cur_item()
        if it is None:
            return
        qid = it.get("id", "")
        rec = self.progress.setdefault(qid, {"ok": None, "fav": False,
                                             "wrong_count": 0, "notes": ""})
        rec["notes"] = self.note_text.get("1.0", "end-1c")
        self._save_progress()

    # ---------- 收藏 / 重做 / 重置 ----------
    def toggle_fav(self):
        it = self.queue[self.idx]
        rec = self.progress.setdefault(it.get("id", ""), {"ok": None, "fav": False,
                                                          "wrong_count": 0, "notes": ""})
        rec["fav"] = not rec.get("fav", False)
        self._save_progress()
        self.fb.config(state=tk.NORMAL)
        self.fb.delete("1.0", "end")
        self.fb.insert(tk.END, "⭐ 已收藏，可在错题/收藏中回顾" if rec["fav"] else "已取消收藏")
        self.fb.config(state=tk.DISABLED)

    def redo_q(self):
        if self.mode == "考试":
            messagebox.showinfo("提示", "考试中不能重新做题")
            return
        it = self.queue[self.idx]
        if it.get("id", "") in self.progress:
            del self.progress[it.get("id", "")]
            self._save_progress()
        self.show_question()

    def reset_progress(self):
        """清除记忆：3 次确认 + 5 秒冷静期"""
        if not messagebox.askyesno("重置进度（1/3）",
                                   "确定要清除全部做题记录吗？\n（此操作不可恢复！）"):
            return
        if not messagebox.askyesno("重置进度（2/3）",
                                   "再次确认：将清空做题记录、错题次数、笔记和考试记录！"):
            return
        if not self._confirm_cool_down():
            return
        # 执行重置（先清队列与状态，避免 set_mode 内部 _save_note 回写）
        self._stop_exam_timer()
        self.exam = {}
        self.progress = {}
        self.queue = []
        self.idx = 0
        self.mode = "顺序"
        self._save_progress()
        self.note_text.delete("1.0", "end")
        for w in self.exam_bar.winfo_children():
            w.destroy()
        self.fb.config(state=tk.NORMAL)
        self.fb.delete("1.0", "end")
        self.fb.insert(tk.END, "🗑 已清除全部做题记录，重新开始！\n")
        self.fb.config(state=tk.DISABLED)
        self.set_mode("顺序")
        self._update_stat()
        self.show_question()

    def _confirm_cool_down(self, seconds=5):
        """最后一次确认：5 秒冷静期后才能点确定"""
        tl = tk.Toplevel(self.root)
        tl.title("重置确认（3/3）")
        tl.geometry("380x190")
        tl.transient(self.root)
        tl.grab_set()
        tl.resizable(False, False)
        var = tk.StringVar(value=f"最后一次确认（3/3）\n\n请等待 {seconds} 秒后才能点击确定…")
        tk.Label(tl, textvariable=var, font=("Microsoft YaHei", 11),
                 justify="center", pady=18).pack()
        btn = tk.Button(tl, text="确 定", state=tk.DISABLED, width=12,
                        font=("Microsoft YaHei", 10))
        btn.pack(pady=4)
        tk.Button(tl, text="取 消", command=tl.destroy, width=12,
                  font=("Microsoft YaHei", 10)).pack(pady=2)
        left = [seconds]
        result = [False]

        def tick():
            if left[0] <= 0:
                var.set("最后一次确认（3/3）\n\n现在可以点击确定进行重置。")
                btn.config(state=tk.NORMAL)
                return
            var.set(f"最后一次确认（3/3）\n\n请等待 {left[0]} 秒后才能点击确定…")
            left[0] -= 1
            tl.after(1000, tick)

        def do_ok():
            result[0] = True
            tl.destroy()

        btn.config(command=do_ok)
        tick()
        tl.wait_window()
        return result[0]

    # ---------- 导航 ----------
    def prev_q(self):
        self._save_note()
        if self.idx > 0:
            self.idx -= 1
            if self.mode == "考试":
                self.exam["idx"] = self.idx
                self.exam["left"] = self.exam_left
                self._save_exam()
                self._exam_render_q()
            else:
                self.show_question()
        else:
            messagebox.showinfo("提示", "已经是第一题")

    def next_q(self):
        self._save_note()
        if self.idx < len(self.queue) - 1:
            self.idx += 1
            if self.mode == "考试":
                self.exam["idx"] = self.idx
                self.exam["left"] = self.exam_left
                self._save_exam()
                self._exam_render_q()
            else:
                self.show_question()
        else:
            if self.mode == "考试":
                if messagebox.askyesno("交卷", "已到最后一题，确定交卷吗？"):
                    self.finish_exam()
            else:
                messagebox.showinfo("提示", "已经是最后一题")

    # ---------- 统计 ----------
    def _update_stat(self):
        done = [it for it in self.bank
                if self.progress.get(it.get("id", ""), {}).get("ok") is not None]
        ok = [it for it in done
              if self.progress.get(it.get("id", ""), {}).get("ok") is True]
        wrong = sum(1 for it in self.bank
                    if self.progress.get(it.get("id", ""), {}).get("ok") is False)
        rate = round(len(ok) / len(done) * 100) if done else 0
        self.stat_label.config(
            text=f"已做 {len(done)}/{len(self.bank)} · 正确率 {rate}% · 错题 {wrong}")
        self.pbar["value"] = rate

    def _save_progress(self):
        try:
            with open(PROG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.progress, f, ensure_ascii=False, indent=1)
        except Exception:
            pass


def main():
    if not os.path.exists(BANK_PATH):
        messagebox.showerror("缺少题库", "未找到 题库.json，请先运行 build_bank.py 生成题库。")
        return
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
