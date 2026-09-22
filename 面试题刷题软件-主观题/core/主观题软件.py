# -*- coding: utf-8 -*-
"""面试题刷题软件 · 主观题
题库来源：题库.json（由 build_bank.py 从 题库/02_主观题.md 生成）
功能：顺序浏览 + 打字作答（自动保存）+ 查看参考答案与得分点 + 跳题 +
      收藏题目（收藏区取消收藏，带确认）+ 分区跳转（按试卷分区、确认后跳转）+
      模拟考试（10 题 / 40 分钟，计划式抽题、暂停/退出/恢复、交卷后逐题回顾）+ 重置进度。
特点：不打分、无错题库；考试交卷后对照参考答案与得分点自评。
版本：2.7.0（跳题修复 + 收藏 + 分区跳转）"""
import sys, io, os, json, random, time
import tkinter as tk
from tkinter import ttk, messagebox

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # 上一级 = 软件根目录
BANK_PATH = os.path.join(ROOT, "题库.json")
PROG_PATH = os.path.join(ROOT, "progress.json")

COLOR_BLUE = "#1a5276"
COLOR_OK = "#1a7f37"
COLOR_PURPLE = "#8e44ad"
COLOR_NO = "#c62828"
EXAM_NUM = 10          # 每次考试题数
EXAM_MIN = 40          # 考试时长（分钟）


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
            with open(PROG_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def plan_take(ids, plan, order_key, cursor_key, n):
    """环形连续段抽题（模块级纯函数，便于测试）：
    将 ids 打乱成固定序列存于 plan[order_key]，每场从 plan[cursor_key] 起
    沿环形（到头回绕）连续取 n 个。数学性质：
    · 同一场考试绝不重复（取的是环上一段连续区间，内部元素唯一）；
    · 连续 ⌈len(ids)/n⌉+1 场必覆盖全部题目；
    · 每题出现间隔恒定，不出现长期漏考。"""
    n = max(0, min(int(n), len(ids)))
    if n == 0:
        return []
    order = plan.get(order_key)
    if not isinstance(order, list) or set(order) != set(ids):
        order = ids[:]
        random.shuffle(order)
        plan[cursor_key] = 0
    m = len(order)
    cur = plan.get(cursor_key, 0)
    if not isinstance(cur, int) or cur < 0 or cur >= m:
        cur = 0
    if n >= m:
        plan[order_key], plan[cursor_key] = order, 0
        return order[:]
    end = cur + n
    if end <= m:
        picked = order[cur:end]
    else:
        picked = order[cur:] + order[:end - m]
    plan[order_key], plan[cursor_key] = order, end % m
    return picked


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("面试题刷题软件 · 主观题")
        self._fit_window(760)
        self.bank = load_bank()
        if not self.bank:
            messagebox.showerror("题库错误",
                                 "题库为空或损坏，请重新运行 build_bank.py 生成题库。")
        self.progress = load_progress()
        ex = self.progress.get("exam")
        self.exam = ex if isinstance(ex, dict) else {}
        self.mode = "顺序"
        self.queue = list(self.bank)
        self.idx = 0
        self._seq_saved_idx = None      # 顺序板块本次会话中的位置（切板块返回时用）
        self._resume_notice = False     # 恢复进度时在题头提示一次
        self._cur_qid = None            # 作答框当前对应的题（未渲染时禁止回写）
        self._save_job = None
        self._exam_timer = None
        self._closing = False          # 窗口销毁中：不再挂新的 after 定时器
        self.exam_left = 0
        self.revealed = False              # 当前题是否正在显示答案
        self._build_ui()
        # 有未完成/未结算的考试 → 直接进入考试板块恢复
        if self.exam.get("active"):
            self.set_mode("考试")
        else:
            self.set_mode("顺序")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<Destroy>", self._on_root_destroy, add="+")
        self._bind_keys()

    def _fit_window(self, base_h):
        """窗口自适应屏幕大小并居中（默认给出较大的初始尺寸，之后可自由缩放）"""
        try:
            self.root.update_idletasks()
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            w = max(1020, min(1760, int(sw * 0.9), sw - 40))
            h = max(680, min(base_h + 400, int(sh * 0.9), sh - 60))
            x = max(0, (sw - w) // 2)
            y = max(0, (sh - h) // 2 - 20)
            self.root.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            self.root.geometry(f"1280x{base_h}")
        try:
            self.root.minsize(960, 620)
        except Exception:
            pass

    def _nav_allowed(self):
        """快捷翻题仅在顺序板块或考试进行中生效"""
        return self.mode == "顺序" or self._exam_running()

    # ---------- 进度记忆 ----------
    def _q_done(self, it):
        """该题是否已完成：有作答内容 或 已查看参考答案（两种都算做过）"""
        pr = self.progress.get(it.get("id", ""))
        if not isinstance(pr, dict):
            return False
        return bool(str(pr.get("wrote", "") or "").strip()) or bool(pr.get("revealed"))

    def _resume_index(self):
        """记忆位置 = 连续完成题目的最后一题。
        例：做了 1、2、3、4，跳过 5 又做了 6、7、8 → 回到第 4 题。"""
        last = -1
        for i, it in enumerate(self.queue):
            if self._q_done(it):
                last = i
            else:
                break
        return last if last >= 0 else 0

    def _bind_keys(self):
        """键盘快捷键：← 上一题 / → 下一题（焦点在作答框/输入框时自动让位）"""
        def wrap(fn, guard=None):
            def _h(_e):
                try:
                    w = self.root.focus_get()
                    if isinstance(w, (tk.Text, tk.Entry)):
                        return ""
                except Exception:
                    pass
                if guard is not None and not guard():
                    return ""
                fn()
                return "break"
            return _h
        self.root.bind("<Left>", wrap(self.prev_q, self._nav_allowed))
        self.root.bind("<Right>", wrap(self.next_q, self._nav_allowed))

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
                self.exam["paused"] = False
                self._save_exam()
                self._exam_tick()
                self._exam_render_q()
                return
        self._save_answer()
        self._save_progress()
        self.root.destroy()

    # ---------- UI ----------
    def _bind_hover(self, widget, base, hover):
        def on_enter(_e):
            try:
                widget.config(bg=hover)
            except Exception:
                pass

        def on_leave(_e):
            try:
                widget.config(bg=base)
            except Exception:
                pass
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def _build_ui(self):
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        # 顶部栏
        bar = tk.Frame(self.root, bg="#2c3e50")
        bar.grid(row=0, column=0, sticky="ew")
        tk.Label(bar, text="🎯 面试题刷题（主观题）", bg="#2c3e50", fg="white",
                 font=("Microsoft YaHei", 13, "bold"), padx=12).pack(side=tk.LEFT, pady=6)
        # 板块按钮：顺序 / 收藏 / 考试
        self.mode_btns = {}
        for m in ("顺序", "收藏", "考试"):
            b = tk.Button(bar, text=m, command=lambda mm=m: self.set_mode(mm),
                          relief=tk.FLAT, padx=10, cursor="hand2",
                          font=("Microsoft YaHei", 10))
            b.pack(side=tk.LEFT, padx=3, pady=6)
            self.mode_btns[m] = b
        # 分区跳转
        bsec = tk.Button(bar, text="📂 分区", command=self._open_sections,
                         relief=tk.FLAT, padx=8, cursor="hand2", bg="#34495e", fg="#ecf0f1",
                         font=("Microsoft YaHei", 10))
        bsec.pack(side=tk.LEFT, padx=(10, 0), pady=6)
        # 右上角：考试上下文按钮区（开始/暂停/退出/重新考试）
        self.exam_bar = tk.Frame(bar, bg="#2c3e50")
        self.exam_bar.pack(side=tk.RIGHT, padx=8)
        self.stat_label = tk.Label(bar, text="", bg="#2c3e50", fg="#ecf0f1",
                                   font=("Microsoft YaHei", 10, "bold"))
        self.stat_label.pack(side=tk.RIGHT, padx=12)
        tk.Label(bar, text="跳题号:", bg="#2c3e50", fg="#ecf0f1",
                 font=("Microsoft YaHei", 10)).pack(side=tk.RIGHT, padx=(0, 2))
        self.jump_var = tk.StringVar()
        self.jump_entry = tk.Entry(bar, textvariable=self.jump_var, width=5,
                                   font=("Microsoft YaHei", 10))
        self.jump_entry.pack(side=tk.RIGHT, padx=(0, 8))
        self.jump_entry.bind("<Return>", lambda e: self._jump())

        # 主体
        body = tk.Frame(self.root, bg="#f5f7fa")
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_rowconfigure(3, weight=1)
        body.grid_columnconfigure(0, weight=1)

        self.head_label = tk.Label(body, text="", bg="#eaf2f8", fg=COLOR_BLUE,
                                   font=("Microsoft YaHei", 12, "bold"),
                                   anchor="w", padx=12, pady=6)
        self.head_label.grid(row=0, column=0, sticky="ew")
        # 题干区：高度随内容自适应，超过上限出现滚动条（长题干不丢内容）
        self.stem_frame = tk.Frame(body, bg="#ffffff")
        self.stem_frame.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.stem_frame.grid_columnconfigure(0, weight=1)
        self.stem_sb = tk.Scrollbar(self.stem_frame, orient="vertical")
        self.stem = tk.Text(self.stem_frame, font=("Consolas", 12), wrap="char",
                            bg="#ffffff", relief=tk.FLAT, padx=14, pady=8,
                            height=7, state=tk.DISABLED,
                            yscrollcommand=self.stem_sb.set)
        self.stem_sb.config(command=self.stem.yview)
        self.stem.grid(row=0, column=0, sticky="ew")
        self.img_area = tk.Frame(body, bg="#f5f7fa")
        self.img_area.grid(row=2, column=0, sticky="ew", padx=10)

        # 作答区 + 参考答案区：放进「可上下拖动的分栏」——拖动中间分隔条即可调整两者高度
        self.split = ttk.Panedwindow(body, orient=tk.VERTICAL)
        self.split.grid(row=3, column=0, sticky="nsew")
        self._sash_user = False
        self.split.bind("<Configure>", self._on_split_configure)
        self.split.bind("<B1-Motion>", self._on_sash_drag)

        wrap = tk.Frame(self.split, bg="#f5f7fa")
        self.split.add(wrap, weight=52)
        wrap.grid_rowconfigure(1, weight=1)
        wrap.grid_columnconfigure(0, weight=1)
        self.ans_label = tk.Label(wrap, text="✍️ 我的作答（打字作答，自动保存；不判对错）",
                                  bg="#fdf6e3", fg="#7b5804",
                                  font=("Microsoft YaHei", 10, "bold"),
                                  anchor="w", padx=12, pady=4)
        self.ans_label.grid(row=0, column=0, sticky="ew")
        self.ans_text = tk.Text(wrap, font=("Microsoft YaHei", 11), wrap="word",
                                bg="#fffdf5", relief=tk.GROOVE, bd=1,
                                padx=10, pady=6, height=6)
        self.ans_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(2, 6))
        self.ans_text.bind("<KeyRelease>", lambda e: self._edited())

        # 参考答案区：与作答区同处一个可上下拖动的分栏；超出可视区自动出现滚动条
        self.fb_frame = tk.Frame(self.split, bg="#f5f7fa")
        self.split.add(self.fb_frame, weight=48)
        self.fb_frame.grid_columnconfigure(0, weight=1)
        self.fb_frame.grid_rowconfigure(1, weight=1)
        self.fb_head = tk.Label(
            self.fb_frame,
            text="👀 参考答案 / 得分点（拖动上方分隔条可放大此区域，内容可滚动）",
            bg="#f4ecf7", fg=COLOR_PURPLE, font=("Microsoft YaHei", 9, "bold"),
            anchor="w", padx=8, pady=3)
        self.fb_head.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.fb_sb = tk.Scrollbar(self.fb_frame, orient="vertical")
        self.fb = tk.Text(self.fb_frame, font=("Microsoft YaHei", 11), wrap="char",
                          height=6, relief=tk.GROOVE, bd=1, padx=10, pady=6,
                          state=tk.DISABLED, yscrollcommand=self._fb_on_scroll)
        self.fb_sb.config(command=self.fb.yview)
        self.fb.grid(row=1, column=0, sticky="nsew", padx=(6, 0), pady=(0, 6))
        self.fb.tag_configure("h_ans", foreground=COLOR_OK,
                              font=("Microsoft YaHei", 11, "bold"))
        self.fb.tag_configure("h_exp", foreground=COLOR_PURPLE,
                              font=("Microsoft YaHei", 11, "bold"))
        self._clear_fb()

        # 底部导航（按钮动态重建）
        self.nav = tk.Frame(self.root, bg="#f0f0f0")
        self.nav.grid(row=2, column=0, sticky="ew")
        self.reveal_btn = None

    def _set_nav(self, btns):
        """重建底部导航按钮：btns = [(文字, 命令, 颜色), ...]"""
        for w in self.nav.winfo_children():
            w.destroy()
        hover_map = {COLOR_BLUE: "#2471a3", COLOR_PURPLE: "#a569bd",
                     COLOR_OK: "#27ae60", COLOR_NO: "#e74c3c"}
        self.reveal_btn = None
        for txt, fn, color in btns:
            b = tk.Button(self.nav, text=txt, command=fn, bg=color, fg="white",
                          cursor="hand2", padx=12, pady=5,
                          font=("Microsoft YaHei", 10))
            b.pack(side=tk.LEFT, padx=4, pady=6)
            self._bind_hover(b, color, hover_map.get(color, color))
            if "查看参考答案" in txt:
                self.reveal_btn = b

    # ---------- 模式 ----------
    def set_mode(self, mode):
        self._save_answer()
        # 考试中禁止切换其他板块
        if (self.mode == "考试" and mode != "考试"
                and self._exam_active() and not self._exam_finished()):
            messagebox.showwarning("考试中", "考试进行中，不能切换到其他板块！\n请先交卷或退出考试。")
            return
        if mode == "收藏":
            favs = set(self._favs())
            if not any(it.get("id") in favs for it in self.bank):
                messagebox.showinfo("收藏", "还没有收藏题目。\n在「顺序」板块做题时点「⭐ 收藏」即可收藏。")
                return
        self._stop_exam_timer()
        if self.mode == "顺序" and mode != "顺序":
            self._seq_saved_idx = self.idx      # 记住本次浏览位置，回到顺序板块时恢复
        self.mode = mode
        for m, b in self.mode_btns.items():
            b.config(bg="#34495e", fg="white")
        self.mode_btns[mode].config(bg="#1a5276", fg="white")
        self.jump_entry.config(state=tk.DISABLED if mode == "考试" else tk.NORMAL)
        if mode == "顺序":
            for w in self.exam_bar.winfo_children():
                w.destroy()
            self.queue = list(self.bank)
            # 首次进入（打开软件）：跳到"连续完成题目的最后一题"；之后回到上次浏览位置
            self.idx = self._resume_index() if self._seq_saved_idx is None \
                else self._seq_saved_idx
            if self.queue:
                self.idx = max(0, min(self.idx, len(self.queue) - 1))
            self._resume_notice = bool(self.idx > 0 and self._seq_saved_idx is None)
            self.show_question()
        elif mode == "收藏":
            for w in self.exam_bar.winfo_children():
                w.destroy()
            favs = set(self._favs())
            self.queue = [it for it in self.bank if it.get("id") in favs]
            self.idx = 0
            self.show_question()
        else:
            self._enter_exam_board()

    # ---------- 考试 ----------
    def _stop_exam_timer(self):
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
            b = tk.Button(self.exam_bar, text="🔄 重新考试", command=self._exam_restart_to_ready,
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
        cnt = self.progress.get("_exam_count", 0)
        rounds = max(1, -(-len(self.bank) // EXAM_NUM))
        self.head_label.config(text=f"📝 模拟考试 · 第 {cnt + 1} 次考试")
        self._set_readonly(self.stem,
            "考试说明：\n\n"
            f"· 共 {EXAM_NUM} 题（从 {len(self.bank)} 题主观题库中环形抽取，同一场不重复），限时 {EXAM_MIN} 分钟\n"
            "· 打字作答，自动保存；考试中可随时修改\n"
            "· 主观题不打分：交卷后逐题对照参考答案与得分点自评\n"
            f"· 当前第 {cnt + 1} 次考试 · 已累计完成 {cnt} 次 · 连续 {rounds} 场必覆盖全部题目\n"
            "· 考试中可暂停 / 退出；强制关闭程序会自动保存，下次打开继续\n"
            "· 考试中不能切换到其他板块\n\n"
            "点击右上角「▶ 开始考试」按钮开始。", 4, 16)
        self._render_images({})
        self._clear_fb()
        self.ans_text.delete("1.0", "end")
        self._set_ans_enabled(False)
        self._cur_qid = None
        self._set_nav([])
        self._update_stat()

    def _exam_pick_ids(self):
        """环形连续段抽题：从打乱序列环形取 10 个，连续 41 场必覆盖全部题目"""
        ids = [it["id"] for it in self.bank]
        if not ids:
            return []
        sig = f"{len(self.bank)}:{self.bank[0].get('id')}:{self.bank[-1].get('id')}"
        plan = self.progress.get("_exam_plan")
        if not isinstance(plan, dict) or plan.get("sig") != sig:
            plan = {"sig": sig}
        picked = plan_take(ids, plan, "sub", "cur", EXAM_NUM)
        self.progress["_exam_plan"] = plan
        return picked

    def _exam_start(self):
        """开始考试：计划式抽 10 题（完成交卷才计入考试次数）"""
        self._stop_exam_timer()
        self.mode = "考试"
        ids = self._exam_pick_ids()
        self.exam = {"active": True, "finished": False, "paused": False,
                     "ids": ids, "idx": 0, "left": EXAM_MIN * 60}
        self.queue = [it for it in self.bank if it.get("id") in set(ids)]
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
        if 0 <= self.idx < len(self.queue):
            mm, ss = divmod(self.exam_left, 60)
            self.head_label.config(
                text=f"⏱ 模拟考试 · 剩余 {mm:02d}:{ss:02d} · 第 {self.idx + 1}/{len(self.queue)} 题")
        self._exam_timer = self.root.after(1000, self._exam_tick)

    def _exam_render_q(self):
        """考试模式显示当前题（含已保存的作答）"""
        if not self.queue or not (0 <= self.idx < len(self.queue)):
            return
        it = self.queue[self.idx]
        self.exam["idx"] = self.idx
        mm, ss = divmod(self.exam_left, 60)
        self.head_label.config(
            text=f"⏱ 模拟考试 · 剩余 {mm:02d}:{ss:02d} · 第 {self.idx + 1}/{len(self.queue)} 题")
        self._cur_qid = it.get("id", "")
        self._set_readonly(self.stem, str(it.get("stem", "")), 4, 14)
        self._render_images(it)
        rec = self.progress.get(it.get("id", ""), {})
        self._set_ans_enabled(True)
        self.ans_text.delete("1.0", "end")
        self.ans_text.insert("1.0", rec.get("wrote", ""))
        self._clear_fb()
        self._set_nav([("◀ 上一题", self.prev_q, COLOR_BLUE),
                       ("📮 交卷", self._exam_ask_finish, COLOR_OK),
                       ("下一题 ▶", self.next_q, COLOR_BLUE)])
        self.revealed = False
        self._update_stat()

    def _exam_render_paused(self):
        """暂停页"""
        self._cur_qid = None                    # 只读页：禁止回写作答
        self._exam_update_topbar()
        mm, ss = divmod(self.exam_left, 60)
        self.head_label.config(text="⏸ 考试已暂停")
        done = sum(1 for it in self._exam_qlist()
                   if str(self.progress.get(it.get("id", ""), {}).get("wrote", "")).strip())
        self._set_readonly(self.stem,
            f"考试已暂停。\n\n剩余时间：{mm:02d}:{ss:02d}\n"
            f"已作答 {done}/{len(self._exam_qlist())} 题\n\n"
            "点击顶部「▶ 继续考试」恢复答题。", 4, 14)
        self._render_images({})
        self._clear_fb()
        self.ans_text.delete("1.0", "end")
        self._set_ans_enabled(False)
        self._set_nav([])
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

    def _exam_restart_to_ready(self):
        """重新考试：先回到考试待开始页，点「开始考试」才正式开考"""
        self._stop_exam_timer()
        self.exam = {}
        self.progress.pop("exam", None)
        self._save_progress()
        self.mode = "考试"
        self._exam_show_ready()

    def _exam_ask_finish(self):
        """手动交卷确认"""
        if not self._exam_active() or self._exam_finished():
            return
        done = sum(1 for it in self._exam_qlist()
                   if str(self.progress.get(it.get("id", ""), {}).get("wrote", "")).strip())
        if messagebox.askyesno("交卷", f"确定交卷吗？\n（已作答 {done}/{len(self._exam_qlist())} 题）"):
            self.finish_exam()

    def finish_exam(self):
        """交卷：完成交卷才计入考试次数"""
        self._stop_exam_timer()
        if not self._exam_active() or self.exam.get("finished"):
            return
        self._save_answer()
        self.exam["finished"] = True
        self.exam["paused"] = False
        self.exam["left"] = self.exam_left
        self.progress["_exam_count"] = self.progress.get("_exam_count", 0) + 1
        self._save_exam()
        self._exam_show_result_page()

    def _exam_show_result_page(self):
        """成绩页：完成情况 + 题号按钮（点击逐题回顾）"""
        self._cur_qid = None
        self._stop_exam_timer()
        self._exam_update_topbar()
        qs = self._exam_qlist()
        total = len(qs)
        answered = [it for it in qs
                    if str(self.progress.get(it.get("id", ""), {}).get("wrote", "")).strip()]
        un = total - len(answered)
        self.head_label.config(text="🏁 考试结束")
        self._set_readonly(self.stem,
            f"📋 考试完成：已作答 {len(answered)}/{total} 题 · 未作答 {un} 题\n\n"
            "主观题不打分——点击下方题号逐题回顾：\n"
            "对照参考答案与得分点，自我评估掌握程度。", 4, 16)
        self._render_images({})
        self._clear_fb()
        self._set_ans_enabled(False)
        self.ans_text.delete("1.0", "end")
        # 题号按钮（每行 6 个自动换行）放到作答区（用 ans_text 所在区域顶部？）
        # 简化：题号按钮放反馈区上方——用 fb 文本呈现题号不好点，改为在 ans_text 区域上方插入按钮行
        self._show_review_buttons(qs)
        self._set_nav([("🔄 重新考试", self._exam_restart_to_ready, "#b9770e"),
                       ("⬅ 返回顺序", lambda: self.set_mode("顺序"), COLOR_BLUE)])
        self._update_stat()

    def _show_review_buttons(self, qs):
        """在题目区下方生成可点击的题号按钮（回顾）"""
        for w in self.img_area.winfo_children():
            w.destroy()
        row = None
        for k, it in enumerate(qs):
            if k % 6 == 0:
                row = tk.Frame(self.img_area, bg="#f5f7fa")
                row.pack(fill=tk.X, pady=2)
            wrote = str(self.progress.get(it.get("id", ""), {}).get("wrote", "")).strip()
            color = COLOR_OK if wrote else "#95a5a6"
            b = tk.Button(row, text=f"第 {it.get('num')} 题", width=10,
                          command=lambda q=it.get("id"): self._exam_review(q),
                          bg=color, fg="white", cursor="hand2",
                          font=("Microsoft YaHei", 10))
            b.pack(side=tk.LEFT, padx=4)

    def _exam_review(self, qid):
        """回顾：题干 + 我的作答 + 参考答案 + 得分点"""
        it = self._by_id(qid)
        if not it:
            return
        self._cur_qid = None
        self._set_readonly(self.stem, str(it.get("stem", "")), 4, 14)
        self._render_images(it)
        self.head_label.config(text=f"📖 第 {it.get('num')} 题 · 回顾")
        self._set_ans_enabled(False)
        self.ans_text.delete("1.0", "end")
        wrote = self.progress.get(qid, {}).get("wrote", "")
        self.ans_text.insert("1.0", wrote or "（本题未作答）")
        ans = it.get("answer") or "（无）"
        exp = it.get("explain") or "（无）"
        self.fb.config(state=tk.NORMAL)
        self.fb.delete("1.0", "end")
        self.fb.insert(tk.END, "✅ 参考答案\n", ("h_ans",))
        self.fb.insert(tk.END, ans + "\n\n")
        self.fb.insert(tk.END, "🎯 得分点\n", ("h_exp",))
        self.fb.insert(tk.END, exp)
        self.fb.config(state=tk.DISABLED)
        try:
            self.fb.yview_moveto(0)
        except Exception:
            pass
        self._fit_fb_view()
        self._set_nav([("⬅ 返回成绩", self._exam_show_result_page, COLOR_BLUE)])

    # ---------- 顺序模式 ----------
    def show_question(self):
        if not self.queue:
            return
        self.idx = max(0, min(self.idx, len(self.queue) - 1))
        it = self.queue[self.idx]
        self.revealed = False
        head = (f"[{it.get('kind_name', '主观题')} "
                f"{it.get('num', '')}]  {self.idx + 1}/{len(self.queue)}")
        if self._resume_notice:
            head += "　↩ 已回到上次进度"
            self._resume_notice = False
        self.head_label.config(text=head)
        self._set_readonly(self.stem, str(it.get("stem", "")), 4, 14)
        self._render_images(it)
        rec = self.progress.get(it.get("id", ""), {})
        self._set_ans_enabled(True)
        self.ans_text.delete("1.0", "end")
        self.ans_text.insert("1.0", rec.get("wrote", ""))
        self._clear_fb()
        if self.mode == "收藏":
            self._set_nav([("◀ 上一题", self.prev_q, COLOR_BLUE),
                           ("💔 取消收藏", self.unfav_cur, COLOR_NO),
                           ("下一题 ▶", self.next_q, COLOR_BLUE),
                           ("🗑 重置进度", self.reset_progress, COLOR_NO)])
        else:
            fav_txt = "⭐ 已收藏" if self._is_fav(it.get("id", "")) else "⭐ 收藏"
            self._set_nav([("◀ 上一题", self.prev_q, COLOR_BLUE),
                           (fav_txt, self.fav_add, "#b9770e"),
                           ("👀 查看参考答案", self.toggle_reveal, COLOR_PURPLE),
                           ("下一题 ▶", self.next_q, COLOR_BLUE),
                           ("🗑 重置进度", self.reset_progress, COLOR_NO)])
        self._cur_qid = it.get("id", "")        # 作答框现在对应本题，允许自动保存
        self._update_stat()

    def _set_ans_enabled(self, enabled):
        self.ans_text.config(state=tk.NORMAL if enabled else tk.DISABLED,
                             bg="#fffdf5" if enabled else "#f4f6f7")
        self.ans_label.config(
            text="✍️ 我的作答（打字作答，自动保存；不判对错）" if enabled
            else "📖 我的作答（只读）")

    def _set_readonly(self, widget, text, min_h=4, max_h=14):
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", "end")
        widget.insert("1.0", str(text))
        try:
            widget.update_idletasks()
            raw = int(widget.count("1.0", "end-1c", "displaylines")[0])
        except Exception:
            raw = str(text).count("\n") + 1
        if not isinstance(raw, int) or raw <= 0:
            raw = 1
        lines = max(min_h, min(max_h, raw))
        widget.config(height=lines)
        widget.config(state=tk.DISABLED)
        # 题干内容超出显示上限时，露出垂直滚动条（内容不丢）
        try:
            if widget is getattr(self, "stem", None):
                if raw > lines and not self.stem_sb.winfo_ismapped():
                    self.stem_sb.grid(row=0, column=1, sticky="ns")
                elif raw <= lines and self.stem_sb.winfo_ismapped():
                    self.stem_sb.grid_remove()
        except Exception:
            pass

    def _on_root_destroy(self, e):
        """窗口销毁时取消所有挂起的 after 定时器（避免 Tcl 'invalid command name' 报错）"""
        try:
            if e.widget is not self.root:
                return
        except Exception:
            return
        self._closing = True
        for attr in ("_fb_after", "_save_job", "_exam_timer"):
            job = getattr(self, attr, None)
            if job:
                try:
                    self.root.after_cancel(job)
                except Exception:
                    pass
                setattr(self, attr, None)

    def _on_split_configure(self, e):
        """分栏默认按 52% / 48% 分配（作答区 / 参考答案区）；用户拖动过分隔条后不再自动改比例"""
        if getattr(self, "_sash_user", False) or e.height < 160:
            return
        try:
            self.split.sashpos(0, max(150, int(e.height * 0.52)))
        except Exception:
            pass

    def _on_sash_drag(self, _e):
        """拖动分隔条 → 记住用户已手动调整比例（此后不再自动重置）"""
        self._sash_user = True

    def _fb_on_scroll(self, first, last):
        """文本可见比例变化（内容增减 / 滚动 / 拖动分隔条）→ 更新滚动条并稍后复核"""
        try:
            self.fb_sb.set(first, last)
        except Exception:
            pass
        self._fit_fb_soon(60)

    def _fit_fb_soon(self, delay=60):
        """稍后再判定滚动条（等文本重新布局完成，避免时序抖动）"""
        if getattr(self, "_closing", False):
            return
        if getattr(self, "_fb_after", None):
            try:
                self.root.after_cancel(self._fb_after)
            except Exception:
                pass
        self._fb_after = self.root.after(delay, self._fit_fb_view)

    def _fb_set_sb(self, need):
        try:
            if need and not self.fb_sb.winfo_ismapped():
                self.fb_sb.grid(row=1, column=1, sticky="ns")
            elif not need and self.fb_sb.winfo_ismapped():
                self.fb_sb.grid_remove()
        except Exception:
            pass

    def _fit_fb_view(self):
        """参考答案区滚动条判定：按“内容显示行数 vs 可视行数”（高度由可拖动分栏决定，不封顶行数）"""
        try:
            self._fb_after = None
        except Exception:
            pass
        try:
            raw = int(self.fb.count("1.0", "end-1c", "displaylines")[0])
        except Exception:
            raw = str(self.fb.get("1.0", "end-1c")).count("\n") + 1
        if not isinstance(raw, int) or raw <= 0:
            raw = 1
        line_h = 0
        try:
            info = self.fb.dlineinfo("1.0")   # (x, y, w, h, baseline)
            if info:
                line_h = int(info[3])
        except Exception:
            line_h = 0
        if line_h <= 0:
            try:
                from tkinter import font as tkfont
                line_h = max(12, tkfont.Font(
                    font=self.fb.cget("font")).metrics("linespace"))
            except Exception:
                line_h = 20
        try:
            visible = max(1, (self.fb.winfo_height() - 12) // line_h)
        except Exception:
            visible = 1
        self._fb_set_sb(raw > visible)

    def _render_images(self, it):
        """显示题目配图（imgs 文件名列表 → 软件根 imgs/ 目录）"""
        for w in self.img_area.winfo_children():
            w.destroy()
        for name in (it.get("imgs") or []):
            img = self._load_image(os.path.join(ROOT, "imgs", name), max_w=640)
            if img is None:
                continue
            lbl = tk.Label(self.img_area, image=img, bg="#f5f7fa",
                           bd=1, relief=tk.GROOVE)
            lbl.pack(pady=4)
            lbl.image = img

    @staticmethod
    def _load_image(path, max_w=640):
        """加载 PNG 并按最大宽度缩放；优先用 PIL（平滑缩放），否则 tk 原生"""
        if not path or not os.path.exists(path):
            return None
        try:
            from PIL import Image, ImageTk
            im = Image.open(path)
            if im.width > max_w:
                im = im.resize((max_w, max(1, round(im.height * max_w / im.width))),
                               Image.LANCZOS)
            return ImageTk.PhotoImage(im)
        except Exception:
            pass
        try:
            img = tk.PhotoImage(file=path)
            if img.width() > max_w:
                f = (img.width() + max_w - 1) // max_w
                img = img.subsample(f, f)
            return img
        except Exception:
            return None

    def _clear_fb(self, placeholder=True):
        self.fb.config(state=tk.NORMAL)
        self.fb.delete("1.0", "end")
        if placeholder:
            self.fb.insert(tk.END, "（点「查看参考答案」显示答案与得分点）")
        self.fb.config(state=tk.DISABLED)
        try:
            self.fb.yview_moveto(0)
        except Exception:
            pass
        self._fit_fb_view()

    def _cur(self):
        if self.queue and 0 <= self.idx < len(self.queue):
            return self.queue[self.idx]
        return None

    # ---------- 查看答案（顺序模式） ----------
    def toggle_reveal(self):
        it = self._cur()
        if it is None or self.mode == "考试":
            return
        if self.revealed:
            self._clear_fb()
            self.revealed = False
            if self.reveal_btn:
                self.reveal_btn.config(text="👀 查看参考答案")
            return
        self._save_answer()
        ans = it.get("answer") or "（无）"
        exp = it.get("explain") or "（无）"
        self.fb.config(state=tk.NORMAL)
        self.fb.delete("1.0", "end")
        self.fb.insert(tk.END, "✅ 参考答案\n", ("h_ans",))
        self.fb.insert(tk.END, ans + "\n\n")
        self.fb.insert(tk.END, "🎯 得分点\n", ("h_exp",))
        self.fb.insert(tk.END, exp)
        self.fb.config(state=tk.DISABLED)
        try:
            self.fb.yview_moveto(0)          # 新答案从顶部开始看
        except Exception:
            pass
        self._fit_fb_view()
        rec = self.progress.setdefault(it.get("id", ""), 
                                       {"wrote": "", "revealed": False})
        rec["revealed"] = True
        self._save_progress()
        self.revealed = True
        if self.reveal_btn:
            self.reveal_btn.config(text="🙈 收起参考答案")
        self._update_stat()

    # ---------- 作答自动保存 ----------
    def _edited(self):
        if self._save_job:
            try:
                self.root.after_cancel(self._save_job)
            except Exception:
                pass
        self._save_job = self.root.after(800, self._auto_save)

    def _auto_save(self):
        self._save_job = None
        self._save_answer()
        self._update_stat()

    def _save_answer(self):
        if self._save_job:
            try:
                self.root.after_cancel(self._save_job)
            except Exception:
                pass
            self._save_job = None
        it = self._cur()
        if it is None:
            return
        if str(self.ans_text.cget("state")) == tk.DISABLED:
            return                          # 只读页面（待开始/成绩/回顾）不回写
        if self._cur_qid != it.get("id", ""):
            return                          # 作答框还没渲染过本题（如刚启动）→ 不回写，避免清空已存答案
        qid = it.get("id", "")
        rec = self.progress.setdefault(qid, {"wrote": "", "revealed": False})
        rec["wrote"] = self.ans_text.get("1.0", "end-1c")
        self._save_progress()

    # ---------- 导航 ----------
    def prev_q(self):
        self._save_answer()
        if self.idx > 0:
            self.idx -= 1
            self._render_cur()
        else:
            messagebox.showinfo("提示", "已经是第一题")

    def next_q(self):
        self._save_answer()
        if self.idx < len(self.queue) - 1:
            self.idx += 1
            self._render_cur()
        else:
            if self.mode == "考试" and self._exam_running():
                if messagebox.askyesno("交卷", "已到最后一题，确定交卷吗？"):
                    self.finish_exam()
            else:
                messagebox.showinfo("提示", "已经是最后一题")

    def _render_cur(self):
        if self.mode == "考试":
            self.exam["idx"] = self.idx
            self.exam["left"] = self.exam_left
            self._save_exam()
            self._exam_render_q()
        else:
            self.show_question()

    def _jump(self):
        """跳题：先按题号精确查找；找不到再按“第 n 题”（顺序位置）兑底；
        题库编号有空档（迁出/合并留空），提示中给出真实范围"""
        if self.mode == "考试":
            return
        s = self.jump_var.get().strip()
        self.jump_var.set("")
        if not s.isdigit():
            return
        n = int(s)
        pos = next((i for i, it in enumerate(self.queue) if it.get("num") == n), None)
        if pos is None and 1 <= n <= len(self.queue):
            pos = n - 1          # 兑底：按“第几题”（顺序位置）跳
        if pos is None:
            nums = [it.get("num") for it in self.queue if isinstance(it.get("num"), int)]
            messagebox.showinfo(
                "未找到",
                f"未找到题号 {n}。\n\n· 题号范围 1~{max(nums) if nums else '?'}"
                "（中间空号为迁出/合并留下的空档）\n"
                f"· 也可输入 1~{len(self.queue)} 表示第几题（按顺序位置）")
            return
        self._save_answer()
        self.idx = pos
        self.show_question()

    # ---------- 收藏 ----------
    def _favs(self):
        f = self.progress.get("_favs")
        return f if isinstance(f, list) else []

    def _is_fav(self, qid):
        return qid in self._favs()

    def fav_add(self):
        """题目页：收藏本题（取消收藏需到收藏板块）"""
        it = self._cur()
        if it is None or self.mode == "考试":
            return
        qid = it.get("id", "")
        if self._is_fav(qid):
            messagebox.showinfo("收藏", "本题已在收藏中。\n如需取消，请到「收藏」板块点「💔 取消收藏」。")
            return
        favs = self._favs()
        favs.append(qid)
        self.progress["_favs"] = favs
        self._save_progress()
        self.show_question()
        messagebox.showinfo("收藏", f"⭐ 已收藏第 {it.get('num')} 题（在「收藏」板块查看）")

    def unfav_cur(self):
        """收藏板块：取消收藏（弹窗确认）"""
        it = self._cur()
        if it is None:
            return
        qid = it.get("id", "")
        if not self._is_fav(qid):
            return
        if not messagebox.askyesno("取消收藏",
                                   f"确定取消收藏第 {it.get('num')} 题吗？"):
            return
        favs = [x for x in self._favs() if x != qid]
        self.progress["_favs"] = favs
        self._save_progress()
        # 从收藏队列中移除后刷新
        self.queue = [x for x in self.queue if x.get("id") != qid]
        if not self.queue:
            messagebox.showinfo("收藏", "收藏已清空。")
            self.set_mode("顺序")
            return
        self.idx = max(0, min(self.idx, len(self.queue) - 1))
        self.show_question()

    # ---------- 分区跳转 ----------
    def _open_sections(self):
        """分区目录窗口：左侧按大区（年份/附加）分组的分区树，右侧分区内题目清单，双击/按钮跳转"""
        if self.mode == "考试" and self._exam_active() and not self._exam_finished():
            messagebox.showwarning("考试中", "考试进行中，不能跳题！\n请先交卷或退出考试。")
            return
        sections, seen = [], set()
        for it in self.bank:
            g = it.get("sec_group") or "未分类"
            s = it.get("sec") or g
            if (g, s) not in seen:
                seen.add((g, s))
                sections.append((g, s))
        if not sections:
            messagebox.showinfo("分区跳转", "当前题库没有分区信息（请重新运行 build_bank.py 生成题库）。")
            return
        win = tk.Toplevel(self.root)
        win.title("📂 分区跳转")
        win.transient(self.root)
        try:
            sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
            w, h = max(760, min(980, int(sw * 0.62))), max(520, min(820, int(sh * 0.72)))
            win.geometry(f"{w}x{h}+{max(0, (sw - w) // 2)}+{max(0, (sh - h) // 2 - 30)}")
        except Exception:
            pass
        main = tk.Frame(win, bg="#f5f7fa")
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        tk.Label(main, text="① 选择分区（左侧） → ② 点选题目（右侧） → 确认后跳转",
                 bg="#f5f7fa", fg=COLOR_BLUE, font=("Microsoft YaHei", 10, "bold"),
                 anchor="w").pack(fill=tk.X, pady=(0, 6))
        body = tk.Frame(main, bg="#f5f7fa")
        body.pack(fill=tk.BOTH, expand=True)
        lf = tk.Frame(body, bg="#f5f7fa")
        lf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rf = tk.Frame(body, bg="#f5f7fa")
        rf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))
        tk.Label(lf, text="分区目录", bg="#eaf2f8", fg=COLOR_BLUE,
                 font=("Microsoft YaHei", 10, "bold")).pack(fill=tk.X)
        tk.Label(rf, text="题目清单", bg="#eaf2f8", fg=COLOR_BLUE,
                 font=("Microsoft YaHei", 10, "bold")).pack(fill=tk.X)
        tv = ttk.Treeview(lf, show="tree", selectmode="browse")
        tv.pack(fill=tk.BOTH, expand=True)
        lb = tk.Listbox(rf, font=("Microsoft YaHei", 10), activestyle="dotbox")
        lb.pack(fill=tk.BOTH, expand=True)
        # 建树：大区 → 分区
        groups = {}
        for g, s in sections:
            groups.setdefault(g, []).append(s)
        for g, ss in groups.items():
            gid = "g|" + g
            tv.insert("", "end", iid=gid, text=f"📁 {g}（{len(ss)} 个分区）")
            for s in ss:
                sid = "s|" + g + "|" + s
                cnt = sum(1 for it in self.bank
                          if (it.get("sec_group") or "未分类") == g and (it.get("sec") or g) == s)
                label = s if s != g else f"（{g}）未细分"
                tv.insert(gid, "end", iid=sid, text=f"　📄 {label}（{cnt} 题）")

        def fill_list(items):
            lb.delete(0, tk.END)
            for it in items:
                stem = str(it.get("stem", "")).replace("\n", " ")
                lb.insert(tk.END, f"{it.get('num')}. {stem[:44]}")
            lb._items = items

        def on_tree(_e=None):
            sel = tv.selection()
            if not sel:
                return
            sid = sel[0]
            if sid.startswith("g|"):
                g = sid[2:]
                items = [it for it in self.bank
                         if (it.get("sec_group") or "未分类") == g]
            else:
                _, g, s = sid.split("|", 2)
                items = [it for it in self.bank
                         if (it.get("sec_group") or "未分类") == g and (it.get("sec") or g) == s]
            fill_list(items)

        def do_jump(_e=None):
            sel = lb.curselection()
            items = getattr(lb, "_items", [])
            if not sel or not items:
                messagebox.showinfo("提示", "请先在右侧选择题号")
                return
            it = items[sel[0]]
            if messagebox.askyesno("跳转确认",
                                   f"确定跳转到第 {it.get('num')} 题吗？\n\n{str(it.get('stem', ''))[:60]}"):
                self._jump_to_qid(it.get("id", ""))
                win.destroy()

        tv.bind("<<TreeviewSelect>>", on_tree)
        lb.bind("<Double-Button-1>", do_jump)
        btns = tk.Frame(main, bg="#f5f7fa")
        btns.pack(fill=tk.X, pady=(8, 0))
        tk.Button(btns, text="➡ 跳转到选中题目", command=do_jump, bg=COLOR_BLUE,
                  fg="white", cursor="hand2", padx=14, pady=5,
                  font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)
        tk.Button(btns, text="关闭", command=win.destroy, padx=14, pady=5,
                  font=("Microsoft YaHei", 10)).pack(side=tk.RIGHT)
        # 默认展开第一个大区
        first = tv.get_children()
        if first:
            tv.item(first[0], open=True)
            tv.selection_set(first[0])
            on_tree()

    def _jump_to_qid(self, qid):
        """跳转到指定 id 的题（自动切到顺序板块）"""
        if self.mode != "顺序":
            self.set_mode("顺序")
        idx = next((i for i, it in enumerate(self.queue) if it.get("id") == qid), None)
        if idx is None:
            return
        self._save_answer()
        self.idx = idx
        self.show_question()

    # ---------- 重置 ----------
    def reset_progress(self):
        """清除记忆：3 次确认 + 5 秒冷静期"""
        if not messagebox.askyesno("重置进度（1/3）",
                                   "确定要清除全部作答记录与看答案记录吗？\n（收藏会保留，此操作不可恢复！）"):
            return
        if not messagebox.askyesno("重置进度（2/3）",
                                   "再次确认：将清空所有作答内容与看答案记录！（收藏保留）"):
            return
        if not self._confirm_cool_down():
            return
        self._stop_exam_timer()
        favs = self._favs()               # 收藏不随重置清除
        self.exam = {}
        self.progress = {}
        if favs:
            self.progress["_favs"] = favs
        self.queue = []
        self.idx = 0
        self.mode = "顺序"
        self._seq_saved_idx = 0
        self._resume_notice = False
        self._save_progress()
        self.ans_text.delete("1.0", "end")
        self.idx = 0
        self.set_mode("顺序")
        self.show_question()
        self._update_stat()

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
        result = [False]
        left = [seconds]

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

    # ---------- 统计 / 保存 ----------
    def _update_stat(self):
        total = len(self.bank)
        done = sum(1 for it in self.bank
                   if str(self.progress.get(it.get("id", ""), {}).get("wrote", "")).strip())
        revealed = sum(1 for it in self.bank
                       if self.progress.get(it.get("id", ""), {}).get("revealed"))
        fav_n = len(self._favs())
        self.stat_label.config(
            text=f"已看答案 {revealed}/{total} · 已作答 {done}/{total} · ⭐收藏 {fav_n}")

    def _save_progress(self):
        try:
            with open(PROG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.progress, f, ensure_ascii=False, indent=1)
        except Exception:
            pass


def _enable_dpi_awareness():
    """Windows 下启用 DPI 感知：高分屏下窗口与文字更清晰（其他系统自动忽略）"""
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)    # Win 8.1+
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()         # 旧系统
    except Exception:
        pass


def main():
    if not os.path.exists(BANK_PATH):
        messagebox.showerror("缺少题库",
                             "未找到 题库.json，请运行 build_bank.py 生成题库。")
        return
    _enable_dpi_awareness()
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
