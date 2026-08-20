# -*- coding: utf-8 -*-
"""C 语言刷题软件 · 类似软考通
题库来源：题库.json（由 build_bank.py 从 docx 生成）
功能：顺序练习 / 随机练习 / 错题重做 / 模拟考试；判分 + 解析 + 进度统计 + 收藏 + 错题本 + 笔记 + 重置进度。
版本：1.0.7"""
import sys, io, os, json, random, time
import tkinter as tk
from tkinter import ttk, messagebox

HERE = os.path.dirname(os.path.abspath(__file__))
BANK_PATH = os.path.join(HERE, "题库.json")
PROG_PATH = os.path.join(HERE, "progress.json")

COLOR_OK = "#1a7f37"
COLOR_NO = "#c62828"
COLOR_BLUE = "#1a5276"


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


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("C 语言刷题软件")
        self.root.geometry("1180x720")
        self.bank = load_bank()
        if not self.bank:
            messagebox.showerror("题库错误",
                                 "题库为空或损坏，请重新运行 build_bank.py 生成题库。")
        self.progress = load_progress()   # {id: {"ok","fav","wrong_count","notes"}}
        self.mode = "顺序"                 # 顺序/随机/错题/考试
        self.queue = []                    # 当前模式下的题目序列
        self.idx = 0
        self.choice_var = tk.StringVar()
        self.exam_left = 0                 # 考试剩余秒数
        self._exam_timer = None            # 考试倒计时定时器
        self._note_save_job = None         # 笔记防抖写盘定时器
        self._build_ui()
        self.set_mode("顺序")
        self.show_question()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        """关窗：先保存当前笔记与进度"""
        self._save_note()
        self._save_progress()
        self.root.destroy()

    # ---------- UI ----------
    def _build_ui(self):
        # grid 布局：bar(0) pbar(1) body(2,权重1) nav(3)，底部导航始终可见
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
        body.grid_columnconfigure(0, weight=3)   # 左：题目
        body.grid_columnconfigure(1, weight=1)   # 右：笔记

        left = tk.Frame(body, bg="#ffffff")
        left.grid(row=0, column=0, sticky="nsew")
        right = tk.Frame(body, bg="#fdf6e3", bd=1, relief=tk.GROOVE)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        # ---- 左：题干 / 选项 / 反馈 ----
        self.head_label = tk.Label(left, text="", bg="#eaf2f8", fg=COLOR_BLUE,
                                   font=("Microsoft YaHei", 12, "bold"),
                                   anchor="w", padx=12, pady=6)
        self.head_label.pack(fill=tk.X)
        self.stem = tk.Text(left, font=("Consolas", 12), wrap="word",
                            bg="#ffffff", relief=tk.FLAT, padx=14, pady=8,
                            height=7, state=tk.DISABLED)
        self.stem.pack(fill=tk.X, pady=(4, 0))

        # 选项区（单选 / 判断 动态填充）
        self.opt_frame = tk.Frame(left, bg="#ffffff")
        self.opt_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        self.opt_widgets = []

        # 反馈区（答案 / 解析 / 错题次数）
        self.fb = tk.Text(left, font=("Microsoft YaHei", 11), wrap="word",
                          height=7, relief=tk.GROOVE, bd=1, padx=10, pady=6)
        self.fb.pack(fill=tk.X, padx=10, pady=(2, 6))

        # ---- 右：笔记区（可写可改，自动保存） ----
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

        # 底部导航（grid row3，固定可见）
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
        # 切换模式先保存当前题笔记 + 停考试倒计时（避免后台残留定时器覆盖标题/突然弹交卷）
        self._save_note()
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
            self.start_exam()
            return
        self.idx = 0
        self.show_question()

    def start_exam(self):
        self._stop_exam_timer()
        q = [it for it in self.bank if it.get("kind") in ("choice", "judge")]
        n = min(20, len(q))
        random.shuffle(q)
        self.queue = q[:n]
        self.idx = 0
        self.exam_left = n * 60
        self._exam_tick()
        self.show_question()

    def _stop_exam_timer(self):
        """取消考试倒计时定时器（切换模式 / 交卷 / 重新开考时调用）"""
        if self._exam_timer:
            try:
                self.root.after_cancel(self._exam_timer)
            except Exception:
                pass
            self._exam_timer = None

    def _exam_tick(self):
        if self.mode != "考试":            # 已切走：残留定时器直接退出
            self._exam_timer = None
            return
        if self.exam_left <= 0:
            self.finish_exam()
            return
        self.exam_left -= 1
        mm, ss = divmod(self.exam_left, 60)
        self.head_label.config(
            text=f"⏱ 模拟考试 · 剩余 {mm:02d}:{ss:02d} · 共 {len(self.queue)} 题")
        self._exam_timer = self.root.after(1000, self._exam_tick)

    def finish_exam(self):
        self._stop_exam_timer()
        done = [it for it in self.queue
                if self.progress.get(it.get("id", ""), {}).get("ok") is not None]
        ok = [it for it in done
              if self.progress.get(it.get("id", ""), {}).get("ok") is True]
        total = len(done)
        score = round(len(ok) / total * 100) if total else 0
        messagebox.showinfo(
            "交卷", f"已完成 {total} 题，答对 {len(ok)} 题\n得分：{score} 分")
        self.set_mode("顺序")

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
        # 显示该题历史作答状态
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

    def _render_options(self, it):
        # 清空选项区所有动态控件（含标题 Label，避免累积撑高把底部导航挤出窗口）
        for w in self.opt_frame.winfo_children():
            w.destroy()
        self.opt_widgets = []
        self.choice_var.set("")
        kind = it.get("kind", "qa")
        if kind == "choice":
            self._add_btn("请选择答案：", COLOR_BLUE, disabled=False)
            for o in it.get("options", []):
                rb = tk.Radiobutton(
                    self.opt_frame, text=f"{o.get('key', '?')}. {o.get('text', '')}",
                    variable=self.choice_var, value=o.get("key", "?"),
                    font=("Microsoft YaHei", 11), anchor="w", padx=6)
                rb.pack(fill=tk.X, pady=2)
                self.opt_widgets.append(rb)
        elif kind == "judge":
            self._add_btn("请判断对错：", COLOR_BLUE, disabled=False)
            for txt, key in (("✔ 正确", "√"), ("✘ 错误", "×")):
                b = tk.Button(self.opt_frame, text=txt, command=lambda k=key: self.answer_judge(k),
                              width=14, cursor="hand2", font=("Microsoft YaHei", 11),
                              bg="#34495e", fg="white")
                b.pack(side=tk.LEFT, padx=10, pady=8)
                self.opt_widgets.append(b)
        else:  # 兼容旧题库：简答（新题库不再包含）
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
        self.opt_widgets.append(lbl)      # 登记销毁，避免累积

    # ---------- 作答 ----------
    def check(self):
        """单选提交"""
        it = self.queue[self.idx]
        if it.get("kind") != "choice":
            return
        sel = self.choice_var.get()
        if not sel:
            messagebox.showinfo("提示", "请先选择一个答案")
            return
        self.record(it.get("id", ""), sel == str(it.get("answer", "")).upper())
        self._show_result(it, sel)
        self._update_stat()

    def answer_judge(self, key):
        it = self.queue[self.idx]
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
        """记录作答；答错累计错误次数，自动进入错题库（错题模式按 ok=False 收集）"""
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
        """笔记编辑：实时更新内存 + 防抖 0.8s 写盘"""
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
        """把当前笔记写入内存与磁盘（切换题目 / 关窗前调用）"""
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
        """清除当前题作答记录，重新做"""
        it = self.queue[self.idx]
        if it.get("id", "") in self.progress:
            del self.progress[it.get("id", "")]
            self._save_progress()
        self.show_question()

    def reset_progress(self):
        """清除记忆：全部做题记录 / 错题次数 / 笔记 重置"""
        if not messagebox.askyesno(
                "重置进度",
                "确定要清除全部做题记录、错题次数和笔记吗？\n题库不会删除，进度将归零。"):
            return
        if self.mode == "错题":
            self.set_mode("顺序")          # 错题队列已失效，先脱离再清空
        self.progress = {}
        self._save_progress()
        self.note_text.delete("1.0", "end")
        self.fb.config(state=tk.NORMAL)
        self.fb.delete("1.0", "end")
        self.fb.insert(tk.END, "🗑 已清除全部做题记录，重新开始！\n")
        self.fb.config(state=tk.DISABLED)
        self._update_stat()
        self.show_question()

    # ---------- 导航 ----------
    def prev_q(self):
        self._save_note()                  # 先保存当前题笔记
        if self.idx > 0:
            self.idx -= 1
            self.show_question()
        else:
            messagebox.showinfo("提示", "已经是第一题")

    def next_q(self):
        self._save_note()                  # 先保存当前题笔记
        if self.idx < len(self.queue) - 1:
            self.idx += 1
            self.show_question()
        else:
            if self.mode == "考试":
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
