# -*- coding: utf-8 -*-
"""
visualizer.py — C/C++ 数据结构可视化器（GUI）

功能：
  · 打开 / 粘贴 C 代码片段（结构体、链表、树、数组、递归等）
  · 左侧显示代码，右侧显示内存/结构图
  · 点击代码某一行 → 从头执行到该行，右侧显示该行执行后的
    内存（堆块、指针箭头）与链表结构图
  · 内置多个示例，一键载入
  · 底部状态栏显示当前行 / 执行信息 / 错误

运行： python visualizer.py
依赖： 仅 Python 标准库（tkinter）
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simcore import Simulator, SimError

EXAMPLES = {
    "链表-头插法": r"""#include <stdio.h>
#include <stdlib.h>
typedef struct Node { int val; struct Node *next; } Node;
int main() {
    Node *head = NULL;
    Node *n1 = malloc(sizeof(Node));
    n1->val = 1;
    n1->next = NULL;
    head = n1;
    Node *n2 = malloc(sizeof(Node));
    n2->val = 2;
    n2->next = head;
    head = n2;
    Node *n3 = malloc(sizeof(Node));
    n3->val = 3;
    n3->next = head;
    head = n3;
    return 0;
}
""",
    "链表-反转": r"""typedef struct Node { int val; struct Node *next; } Node;
int main() {
    Node *head = NULL;
    Node *a = malloc(sizeof(Node)); a->val = 1; a->next = NULL;
    Node *b = malloc(sizeof(Node)); b->val = 2; b->next = NULL;
    Node *c = malloc(sizeof(Node)); c->val = 3; c->next = NULL;
    head = a;
    a->next = b;
    b->next = c;
    Node *prev = NULL;
    Node *cur = head;
    while (cur) {
        Node *nxt = cur->next;
        cur->next = prev;
        prev = cur;
        cur = nxt;
    }
    head = prev;
    return 0;
}
""",
    "链表-遍历求和": r"""typedef struct Node { int val; struct Node *next; } Node;
int main() {
    Node *a = malloc(sizeof(Node));
    a->val = 10; a->next = NULL;
    Node *b = malloc(sizeof(Node));
    b->val = 20; b->next = NULL;
    Node *c = malloc(sizeof(Node));
    c->val = 30; c->next = NULL;
    a->next = b;
    b->next = c;
    int sum = 0;
    Node *p = a;
    while (p) {
        sum = sum + p->val;
        p = p->next;
    }
    return 0;
}
""",
    "递归-阶乘": r"""int fact(int n) {
    if (n <= 1) return 1;
    return n * fact(n - 1);
}
int main() {
    int r = fact(4);
    return 0;
}
""",
    "递归-链表求和": r"""typedef struct Node { int val; struct Node *next; } Node;
int sum_list(Node *head) {
    if (!head) return 0;
    return head->val + sum_list(head->next);
}
int main() {
    Node *a = malloc(sizeof(Node)); a->val = 5; a->next = NULL;
    Node *b = malloc(sizeof(Node)); b->val = 7; b->next = NULL;
    Node *c = malloc(sizeof(Node)); c->val = 9; c->next = NULL;
    a->next = b;
    b->next = c;
    int total = sum_list(a);
    return 0;
}
""",
    "数组-简单操作": r"""int main() {
    int arr[5];
    int i;
    arr[0] = 3;
    arr[1] = 7;
    for (i = 2; i < 5; i = i + 1) {
        arr[i] = arr[i-1] + arr[i-2];
    }
    return 0;
}
""",
    "二叉树-插入": r"""typedef struct TNode {
    int val;
    struct TNode *left;
    struct TNode *right;
} TNode;
int main() {
    TNode *root = malloc(sizeof(TNode));
    root->val = 5;
    root->left = NULL;
    root->right = NULL;
    TNode *l = malloc(sizeof(TNode));
    l->val = 3; l->left = NULL; l->right = NULL;
    TNode *r = malloc(sizeof(TNode));
    r->val = 8; r->left = NULL; r->right = NULL;
    root->left = l;
    root->right = r;
    return 0;
}
""",
}


# ---------------------------------------------------------------
# 绘制器：把快照画到 Canvas
# ---------------------------------------------------------------
def loc_tag(blk):
    """块的位置标签：[栈] / [堆]"""
    return "[栈]" if blk.get("loc") == "栈" else "[堆]"


class Drawer:
    NODE_W = 132
    NODE_H0 = 26          # 标题行高
    FIELD_H = 20          # 每字段行高
    GAP = 30              # 节点间距

    def __init__(self, canvas):
        self.c = canvas

    def clear(self):
        self.c.delete("all")

    def draw(self, snap, msg="", diff_text=None):
        """布局：上方「调用栈/变量」，下方「内存/链表结构」（横向空间更大）"""
        self.clear()
        W = int(self.c.cget("width"))
        H = int(self.c.cget("height"))
        if W < 50 or H < 50:
            self.fit()
            return
        # 标题（含变更摘要）
        self.c.create_text(10, 8, anchor="nw", text=msg, fill="#333333",
                           font=("Microsoft YaHei", 11, "bold"))
        ty = 30
        if diff_text:
            color = "#1a7f37" if "未修改" in diff_text else "#b35900"
            self.c.create_text(10, ty, anchor="nw", text=diff_text, fill=color,
                               font=("Microsoft YaHei", 9, "bold"))
            ty += 18
        frames = snap.get("frames", [])
        heap = snap.get("heap", [])
        heap_by_addr = {b["addr"]: b for b in heap}

        # ---- 上方：调用栈 / 变量面板（整行宽度，高度完全自适应，不截断） ----
        vx = 10
        vy = ty + 6
        vw = W - 20
        need_h = 26
        for fr in frames:
            need_h += 20 + len(fr["vars"]) * 17 + 6
        ph = max(need_h + 10, 44)
        self.c.create_rectangle(vx, vy, vx + vw, vy + ph, outline="#bbbbbb",
                                fill="#f4f6f8", width=1)
        self.c.create_text(vx + 8, vy + 4, anchor="nw", text="调用栈 / 变量（栈上）",
                           fill="#555555", font=("Microsoft YaHei", 10, "bold"))
        yy = vy + 24
        for fr in frames:
            self.c.create_text(vx + 8, yy, anchor="nw", text="[ " + fr["func"] + " ]",
                               fill="#1a5276", font=("Microsoft YaHei", 10, "bold"))
            yy += 19
            for name, v in fr["vars"]:
                line = self.fmt_var(name, v)
                self.c.create_text(vx + 16, yy, anchor="nw", text=line,
                                   fill="#333333", font=("Consolas", 9))
                yy += 17
            yy += 5
        # 提示：堆/栈图在下方（紧跟内容，避免与堆块重叠）
        self.c.create_text(vx + 8, yy + 2, anchor="nw",
                           text="▼ 下方为内存/结构图（可上下滚动查看）",
                           fill="#888888", font=("Microsoft YaHei", 9))

        # ---- 下方：堆 / 链表结构（整行宽度横向铺开，起点基于变量区矩形底部，任意帧数都不重叠） ----
        hx0 = vx
        htop = vy + ph + 16
        self.c.create_text(hx0, htop - 14, anchor="nw",
                           text="内存 / 结构（■堆 ■栈）",
                           fill="#555555", font=("Microsoft YaHei", 9, "bold"))
        chain_heads = self.find_chains(frames, heap_by_addr)
        if chain_heads:
            self.draw_chains(chain_heads, heap_by_addr, hx0, htop, H)
        else:
            self.draw_heap_blocks(heap_by_addr, hx0, htop, H)
        self.fit()

    def fit(self):
        """根据 Canvas 上所有元素自动设置滚动范围"""
        try:
            bb = self.c.bbox("all")
            if bb:
                self.c.configure(scrollregion=(0, 0, bb[2] + 40, bb[3] + 40))
            else:
                self.c.configure(scrollregion="0 0 300 200")
        except Exception:
            self.c.configure(scrollregion="0 0 300 200")

    def fmt_var(self, name, v):
        t = v.get("type", "")
        val = v.get("value")
        loc = v.get("loc", "栈")
        locs = "[栈] " if loc == "栈" else "[堆] "
        if val[0] == "ptr":
            s = f"{locs}{name} : {t} -> 0x{val[1]:x}"
        elif val[0] == "null":
            s = f"{locs}{name} : {t} -> NULL"
        else:
            s = f"{locs}{name} : {t} = {val[1]}"
        if "arr" in v:
            arr = v["arr"]
            s += "  [" + ", ".join(str(x[1]) if x[0] == "int" else "?" for x in arr) + "]"
        return s

    def find_chains(self, frames, heap_by_addr):
        """找出可作为链表/结构链起点的指针变量。返回 [(addr, label)]"""
        heads = []
        # 优先名为 head/root/cur 的指针
        pref = ("head", "root", "p", "cur", "first", "top", "list")
        seen = set()
        for fr in frames:
            for name, v in fr["vars"]:
                val = v.get("value")
                if val and val[0] == "ptr" and val[1] in heap_by_addr:
                    heads.append((val[1], name))
        # 按名称优先级排序，去重地址
        def rank(item):
            n = item[1].lower()
            for i, p in enumerate(pref):
                if n.startswith(p):
                    return i
            return len(pref)
        heads.sort(key=rank)
        out = []
        seen_addr = set()
        for addr, name in heads:
            if addr not in seen_addr:
                seen_addr.add(addr)
                out.append((addr, name))
        return out

    def field_rows(self, blk):
        """返回 [(fieldname, value_display, target_addr_or_None)]"""
        rows = []
        for fn, fv in blk["fields"].items():
            if fv[0] == "ptr":
                rows.append((fn, f"0x{fv[1]:x}", fv[1]))
            elif fv[0] == "null":
                rows.append((fn, "NULL", None))
            elif fv[0] == "arr":
                # 数组字段：date[0]=3, date[1]=7, ...
                vals = fv[1]
                shown = []
                for x in vals:
                    if x[0] == "int":
                        shown.append(str(x[1]))
                    elif x[0] == "ptr":
                        shown.append(f"0x{x[1]:x}")
                    else:
                        shown.append("NULL")
                # 只显示前 12 个，避免字段过长
                disp = ", ".join(shown[:12])
                if len(shown) > 12:
                    disp += f", ...({len(shown)}项)"
                rows.append((fn, f"[{disp}]", None))
            else:
                rows.append((fn, str(fv[1]), None))
        return rows

    def node_height(self, blk):
        n = len(blk["fields"])
        return self.NODE_H0 + max(1, n) * self.FIELD_H + 8

    def draw_node(self, x, y, addr, blk, heap_by_addr):
        """画一个内存块矩形（按堆/栈区分颜色），返回 (右边缘x, 底部y)"""
        h = self.node_height(blk)
        loc = blk.get("loc", "堆")
        if loc == "栈":
            outline, fill = "#2e7d32", "#e8f5e9"   # 绿 = 栈上结构体变量
            loc_txt = "栈"
        else:
            outline, fill = "#b8860b", "#fff8dc"   # 黄 = 堆(malloc)
            loc_txt = "堆"
        self.c.create_rectangle(x, y, x + self.NODE_W, y + h,
                                outline=outline, fill=fill, width=2)
        self.c.create_text(x + 6, y + 5, anchor="nw",
                           text=f"{blk['typename']} @0x{addr:x} [{loc_txt}]",
                               fill="#5d4037" if loc == "栈" else "#8b4513",
                               font=("Consolas", 9, "bold"))
        yy = y + self.NODE_H0
        for fn, disp, tgt in self.field_rows(blk):
            if tgt is not None:
                self.c.create_text(x + 6, yy, anchor="nw",
                                   text=f"{fn} -> {disp}",
                                   fill="#1a5276", font=("Consolas", 9))
            else:
                self.c.create_text(x + 6, yy, anchor="nw",
                                   text=f"{fn} = {disp}",
                                   fill="#333333", font=("Consolas", 9))
            yy += self.FIELD_H
        return x + self.NODE_W, y + h

    def draw_chains(self, heads, heap_by_addr, x0, y0, H):
        """画链表：超宽自动换行，横向宽度控制在约一屏，保证水平滚动条滑块大小合理可拖拽"""
        cw = int(self.c.cget("width"))
        max_w = max(680, cw - 60)      # 每行宽度上限
        for addr, label in heads:
            x = x0
            y = y0
            visited = set()
            pos = {}
            cur = addr
            steps = 0
            prev = None                # (addr, rx, by) 上一节点，用于换行续接标记
            chain_bottom = y
            while cur in heap_by_addr and cur not in visited and steps < 200:
                visited.add(cur)
                blk = heap_by_addr[cur]
                # 超出行宽 -> 换行，画向下续接标记
                if prev is not None and x > x0 + max_w:
                    _paddr, prx, pby = prev
                    self.c.create_line(prx - 4, pby + 2, prx - 4, pby + 26,
                                       fill="#1a5276", width=2, arrow=tk.LAST)
                    self.c.create_text(x0 + 2, pby + 28, anchor="nw",
                                       text="↘ 续接", fill="#1a5276",
                                       font=("Microsoft YaHei", 9, "bold"))
                    y = pby + 26 + 10
                    x = x0
                rx, by = self.draw_node(x, y, cur, blk, heap_by_addr)
                pos[cur] = (x, y, rx, by)
                chain_bottom = max(chain_bottom, by)
                # next 字段目标
                tgt = None
                for fn, fv in blk["fields"].items():
                    if fv[0] == "ptr":
                        tgt = fv[1]
                        break
                if tgt in heap_by_addr:
                    prev = (cur, rx, by)
                    cur = tgt
                    x = rx + self.GAP
                    steps += 1
                else:
                    # 画 NULL 尾
                    self.c.create_text(x + self.NODE_W + 10, y + 14,
                                       anchor="nw", text="NULL",
                                       fill="#999999", font=("Consolas", 9))
                    break
            # 画箭头：仅同一视觉行内连线（跨行由 ↘ 标记连接）
            for a, (bx, by, rx, _bh) in pos.items():
                blk = heap_by_addr[a]
                tgt = None
                for fn, fv in blk["fields"].items():
                    if fv[0] == "ptr":
                        tgt = fv[1]
                        break
                if tgt in pos:
                    tx, ty, trx, _ = pos[tgt]
                    if abs(ty - by) < 2:
                        self.arrow(rx - 4, by + self.NODE_H0 + 6,
                                   tx + 6, ty + self.NODE_H0 + 6)
            self.c.create_text(x0, chain_bottom + 8, anchor="nw",
                               text=f"← {label}",
                               fill="#666666", font=("Microsoft YaHei", 9))
            y0 = chain_bottom + 44     # 下一条链从本链底部下方开始

    def draw_heap_blocks(self, heap_by_addr, x0, y0, H):
        x = x0
        y = y0
        for addr in sorted(heap_by_addr.keys()):
            blk = heap_by_addr[addr]
            rx, by = self.draw_node(x, y, addr, blk, heap_by_addr)
            x = rx + self.GAP
            if x > int(self.c.cget("width")) - 160:
                x = x0
                y = by + 40

    def arrow(self, x1, y1, x2, y2):
        self.c.create_line(x1, y1, x2, y2, fill="#1a5276", width=2,
                           arrow=tk.LAST, arrowshape=(9, 11, 5))


# ---------------------------------------------------------------
# 主窗口
# ---------------------------------------------------------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("C/C++ 数据结构可视化器")
        self.root.geometry("1180x720")
        self.snapshots = {}
        self.current_line = None
        self.code_lines = []
        self.sim = None
        self._popup = True   # 错误弹窗开关（测试时可关闭）
        # 逐步回放（pythontutor 式）
        self.step_list = []      # [(line, snapshot), ...]
        self.step_idx = -1
        self._pending_inputs = []     # scanf 模拟输入
        self._input_requested = False

        # ---- 顶部工具栏 ----
        bar = tk.Frame(root, bg="#2c3e50")
        bar.pack(side=tk.TOP, fill=tk.X)
        btn = lambda t, fn: tk.Button(bar, text=t, command=fn, bg="#34495e",
                                      fg="white", relief=tk.FLAT, padx=10,
                                      font=("Microsoft YaHei", 10))
        btn("打开文件", self.open_file).pack(side=tk.LEFT, padx=4, pady=4)
        btn("粘贴代码", self.paste_code).pack(side=tk.LEFT, padx=4, pady=4)
        btn("上一步", self.step_prev).pack(side=tk.LEFT, padx=4, pady=4)
        btn("下一步", self.step_next).pack(side=tk.LEFT, padx=4, pady=4)
        btn("运行全部", self.run_all).pack(side=tk.LEFT, padx=4, pady=4)
        btn("重置", self.reset).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Label(bar, text="示例:", bg="#2c3e50", fg="white",
                 font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=(16, 2))
        self.example_var = tk.StringVar()
        ex = ttk.Combobox(bar, textvariable=self.example_var, state="readonly",
                          width=18, values=list(EXAMPLES.keys()))
        ex.pack(side=tk.LEFT, padx=2)
        ex.bind("<<ComboboxSelected>>", self.load_example)
        tk.Label(bar, text="提示：点击左侧代码行 / 用“上一步、下一步”逐步运行 / “运行全部”看最终状态",
                 bg="#2c3e50", fg="#ecf0f1",
                 font=("Microsoft YaHei", 9)).pack(side=tk.RIGHT, padx=10)

        # ---- 主区域：左代码 | 右图 ----
        main = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashwidth=6)
        main.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(main, bg="#1e1e1e")
        right = tk.Frame(main, bg="#ffffff")
        main.add(left, minsize=430, width=560)
        main.add(right, minsize=380, width=580)

        # 行号 + 代码（先 pack 滚动条，避免被 expand 的代码区挤成 1px）
        self.scrolly = tk.Scrollbar(left, command=self.sync_scroll, width=18,
                                    bg="#569cd6", troughcolor="#1e1e1e",
                                    activebackground="#4a90c2")
        self.scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        self.line_canvas = tk.Canvas(left, width=40, bg="#1e1e1e",
                                     highlightthickness=0)
        self.line_canvas.pack(side=tk.LEFT, fill=tk.Y)
        self.code = tk.Text(left, wrap="none", bg="#1e1e1e", fg="#d4d4d4",
                            insertbackground="#d4d4d4", font=("Consolas", 12),
                            relief=tk.FLAT, padx=6, pady=4, undo=True)
        self.code.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.code.config(yscrollcommand=lambda *a: (self._upd_lines(), self.scrolly.set(*a)))
        # 鼠标滚轮滚动代码区（快速上下查看）
        def _wheel(ev):
            self.code.yview_scroll(int(-ev.delta / 120), "units")
            self._upd_lines()
        self.code.bind("<MouseWheel>", _wheel)
        self.code.bind("<Button-4>", lambda ev: self.code.yview_scroll(-1, "units"))
        self.code.bind("<Button-5>", lambda ev: self.code.yview_scroll(1, "units"))
        self.line_canvas.bind("<MouseWheel>", _wheel)
        self.line_canvas.bind("<Button-4>", lambda ev: self.code.yview_scroll(-1, "units"))
        self.line_canvas.bind("<Button-5>", lambda ev: self.code.yview_scroll(1, "units"))
        self.code.tag_configure("hl", background="#264f78", foreground="#ffffff")
        self.code.tag_configure("kw", foreground="#569cd6")
        self.code.tag_configure("cm", foreground="#6a9955")
        self.code.tag_configure("ty", foreground="#4ec9b0")
        self.code.tag_configure("er", background="#5a1d1d")
        self.code.bind("<Button-1>", self.on_code_click)
        self.code.bind("<KeyRelease>", lambda e: self._upd_lines())

        # 右侧画布（带水平/垂直滚动条，内容超出时可滚动查看）
        self.canvas = tk.Canvas(right, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb = tk.Scrollbar(right, orient=tk.VERTICAL, command=self.canvas.yview,
                           width=20, bg="#569cd6", troughcolor="#e0e0e0",
                           activebackground="#4a90c2")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb = tk.Scrollbar(right, orient=tk.HORIZONTAL, command=self.canvas.xview,
                           width=20, bg="#569cd6", troughcolor="#e0e0e0",
                           activebackground="#4a90c2")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.vsb, self.hsb = vsb, hsb
        self.canvas.config(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.canvas.bind("<Configure>", lambda e: self.redraw())
        self.drawer = Drawer(self.canvas)

        # ---- 底部状态栏 ----
        status = tk.Frame(root, bg="#f0f0f0")
        status.pack(side=tk.BOTTOM, fill=tk.X)
        self.status = tk.Label(status, text="就绪：粘贴或打开 C 代码，或选择示例",
                               anchor="w", bg="#f0f0f0", fg="#333333",
                               font=("Microsoft YaHei", 9), padx=8)
        self.status.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.lineinfo = tk.Label(status, text="", anchor="e", bg="#f0f0f0",
                                 fg="#555555", font=("Consolas", 9), padx=8)
        self.lineinfo.pack(side=tk.RIGHT)

        # 载入默认示例
        self.load_example_text(EXAMPLES["链表-头插法"])

    # ---------- 代码与行号 ----------
    def sync_scroll(self, *a):
        self.code.yview(*a)
        self._upd_lines()

    def _upd_lines(self):
        """按代码 Text 每行的实际像素位置绘制行号，保证严格对齐"""
        self.line_canvas.delete("all")
        try:
            first = int(float(self.code.index("@0,0")))
            h = self.code.winfo_height()
            last = int(float(self.code.index(f"@0,{h + 1}"))) + 1
        except Exception:
            first, last = 1, 30
        for ln in range(max(1, first), max(1, last) + 1):
            d = self.code.dlineinfo(f"{ln}.0")
            if d:
                _x, y, _w, lh, _bl = d
                self.line_canvas.create_text(20, y + lh // 2, anchor="e",
                                             text=str(ln), fill="#858585",
                                             font=("Consolas", 11))

    def get_code(self):
        return self.code.get("1.0", "end-1c")

    def on_code_click(self, event):
        idx = self.code.index(f"@{event.x},{event.y}")
        line = int(float(idx.split(".")[0]))
        self.show_line(line)

    def show_line(self, line):
        """点击某行：执行到该行，右侧显示状态"""
        self.current_line = line
        self.code.tag_remove("hl", "1.0", "end")
        self.code.tag_remove("er", "1.0", "end")
        self.code.tag_add("hl", f"{line}.0", f"{line}.end")
        self.code.see(f"{line}.0")
        code = self.get_code()
        if not code.strip():
            return
        try:
            sim = Simulator(code)
            snaps = sim.run_to_line(line)
            self.snapshots = snaps
            err = sim.engine.error if sim.engine else None
        except SimError as ex:
            self.set_status(f"语法错误：{ex}", True)
            self.highlight_error(ex.line)
            self.lineinfo.config(text=f"第 {line} 行")
            return
        if err:
            self.set_status(f"运行错误：{err.msg}", True)
            self.highlight_error(err.line)
            self.lineinfo.config(text=f"第 {line} 行")
            self.draw_empty()
            return
        snap = snaps.get(line)
        if snap is None:
            # 该行不是语句行（如宏定义/注释/typedef 等），不修改内存
            snap = self.nearest_snap(snaps, line)
            if snap:
                self.drawer.draw(snap, f"点击第 {line} 行（无执行效果）",
                                 "本行未修改内存（宏定义 / 注释 / typedef / 空行等）")
                self.set_status(f"第 {line} 行未修改内存（宏/注释/声明等）", False)
                self.lineinfo.config(text=f"第 {line} 行")
            else:
                self.draw_empty()
                self.set_status("该行无可展示状态（代码为空或该行无执行效果）", False)
            return
        # 语句行：对比上一快照，判断本行是否修改了内存
        prev = self.prev_snap(snaps, line)
        diff = self.diff_snapshots(prev, snap) if prev is not None else []
        if diff:
            diff_text = "本行修改内存：" + "；".join(diff[:8])
            if len(diff) > 8:
                diff_text += f" 等{len(diff)}处"
        else:
            diff_text = "本行未修改内存（声明 / 判断 / 函数调用等）"
        self.drawer.draw(snap, f"执行到第 {line} 行（该行执行后）", diff_text)
        self.set_status(f"第 {line} 行：{diff_text}", False)
        self.lineinfo.config(text=f"第 {line} 行")

    def get_line_text(self, line):
        try:
            return self.code.get(f"{line}.0", f"{line}.end").strip()
        except Exception:
            return ""

    def prev_snap(self, snaps, line):
        """比 line 小的最大快照行（line 执行前的状态）"""
        keys = sorted(snaps.keys())
        best = None
        for k in keys:
            if k < line:
                best = k
            else:
                break
        return snaps.get(best) if best is not None else None

    def fmt_diff_val(self, dv):
        if dv[0] == "int":
            return str(dv[1])
        if dv[0] == "ptr":
            return f"0x{dv[1]:x}"
        if dv[0] == "arr":
            return "[" + ", ".join(self.fmt_diff_val(x) for x in dv[1][:10]) + ("]" if len(dv[1]) <= 10 else "...]")
        return "NULL"

    def diff_snapshots(self, before, after):
        """对比两个快照，返回本行对内存/变量的变更描述列表"""
        if before is None or after is None:
            return []
        changes = []
        b_h = {b["addr"]: b for b in before["heap"]}
        a_h = {a["addr"]: a for a in after["heap"]}
        for addr in a_h:
            if addr not in b_h:
                changes.append(f"分配{loc_tag(a_h[addr])} {a_h[addr]['typename']}@0x{addr:x}")
        for addr in b_h:
            if addr not in a_h:
                changes.append(f"释放 0x{addr:x}")
        for addr in b_h.keys() & a_h.keys():
            bb, ab = b_h[addr], a_h[addr]
            for fn in set(bb["fields"].keys()) | set(ab["fields"].keys()):
                bv = bb["fields"].get(fn)
                av = ab["fields"].get(fn)
                if bv != av:
                    changes.append(f"{ab['typename']}@0x{addr:x}.{fn}={self.fmt_diff_val(av)}")
        # 变量变化
        def var_map(snap):
            m = {}
            for fr in snap["frames"]:
                for n, v in fr["vars"]:
                    m[n] = v
            return m
        b_vars, a_vars = var_map(before), var_map(after)
        for n in a_vars:
            if n not in b_vars:
                changes.append(f"声明变量 {n}")
            elif a_vars[n]["value"] != b_vars[n]["value"]:
                changes.append(f"{n}={self.fmt_diff_val(a_vars[n]['value'])}")
        return changes

    def nearest_snap(self, snaps, line):
        if not snaps:
            return None
        keys = sorted(snaps.keys())
        best = None
        for k in keys:
            if k <= line:
                best = k
            else:
                break
        if best is None and keys:
            best = keys[0]
        return snaps.get(best)

    def _request_inputs(self):
        """程序含 scanf 时弹出输入框（模拟输入）"""
        import re
        code = self.get_code()
        if not re.search(r"\bscanf\b", code):
            return
        if not self._popup:
            return
        win = tk.Toplevel(self.root)
        win.title("模拟输入 (scanf)")
        win.geometry("440x160")
        win.transient(self.root)
        win.grab_set()
        tk.Label(win, text="程序含 scanf 输入。请输入值（多个值用空格分隔）：",
                 font=("Microsoft YaHei", 10)).pack(pady=(14, 6))
        entry = tk.Entry(win, font=("Consolas", 12), width=44)
        entry.pack(pady=4)
        entry.focus_set()

        def ok():
            vals = []
            for x in entry.get().replace(",", " ").split():
                try:
                    vals.append(int(x, 0))
                except Exception:
                    try:
                        vals.append(int(float(x)))
                    except Exception:
                        pass
            self._pending_inputs = vals
            win.destroy()

        tk.Button(win, text="确定", command=ok, width=12,
                  font=("Microsoft YaHei", 10)).pack(pady=8)
        entry.bind("<Return>", lambda e: ok())

    def _exec_code(self):
        """执行当前代码；返回 (snaps, err, steps)。含 scanf 时请求输入。"""
        code = self.get_code()
        if not code.strip():
            return {}, None, []
        if not self._input_requested:
            self._request_inputs()
            self._input_requested = True
        try:
            sim = Simulator(code)
            sim.pending_inputs = list(self._pending_inputs)
            snaps = sim.run()
            err = sim.engine.error if sim.engine else None
            steps = list(sim.engine.step_snapshots) if sim.engine else []
            self.sim = sim
            return snaps, err, steps
        except SimError as ex:
            return {}, ex, []

    def _show_step(self, idx):
        line, snap = self.step_list[idx]
        self.current_line = line
        self.code.tag_remove("hl", "1.0", "end")
        self.code.tag_remove("er", "1.0", "end")
        self.code.tag_add("hl", f"{line}.0", f"{line}.end")
        self.code.see(f"{line}.0")
        if idx > 0:
            diff = self.diff_snapshots(self.step_list[idx - 1][1], snap)
        else:
            diff = []
        if diff:
            diff_text = "本步修改内存：" + "；".join(diff[:8])
            if len(diff) > 8:
                diff_text += f" 等{len(diff)}处"
        else:
            diff_text = "本步未修改内存（声明 / 判断 / 函数调用等）"
        self.drawer.draw(snap, f"第 {idx + 1} / {len(self.step_list)} 步 · 第 {line} 行执行后", diff_text)
        self.set_status(f"第 {idx + 1}/{len(self.step_list)} 步：{diff_text}", False)
        self.lineinfo.config(text=f"第 {line} 行")

    def build_step_list(self):
        """预先执行并记录每一步（供逐步回放）"""
        snaps, err, steps = self._exec_code()
        self.snapshots = snaps
        self.step_list = steps
        self.step_idx = -1
        if err and not steps:
            self.set_status(f"运行错误：{err.msg}", True)
            self.highlight_error(err.line)
            self.draw_empty()
            return False
        return True

    def step_next(self):
        """下一步：像 pythontutor 一样逐步运行（会进入函数内部）"""
        if not self.step_list:
            if not self.build_step_list():
                return
        if not self.step_list:
            self.set_status("程序无执行步骤（可能没有 main / 函数）", True)
            return
        if self.step_idx >= len(self.step_list) - 1:
            self.set_status("已到最后一步；点“重置”可重新开始", False)
            return
        self.step_idx += 1
        self._show_step(self.step_idx)

    def step_prev(self):
        if not self.step_list:
            self.set_status("请先点“下一步”或“运行全部”", False)
            return
        if self.step_idx <= 0:
            self.set_status("已在第一步", False)
            return
        self.step_idx -= 1
        self._show_step(self.step_idx)

    def run_all(self):
        snaps, err, steps = self._exec_code()
        if err:
            self.set_status(f"运行错误：{err.msg}", True)
            self.highlight_error(err.line)
            self.draw_empty()
            return
        self.snapshots = snaps
        self.step_list = steps
        if not snaps:
            self.set_status("未发现可执行函数（需要 int main() 或函数定义）", True)
            return
        self.step_idx = len(steps) - 1 if steps else -1
        last = max(snaps.keys())
        self.drawer.draw(snaps[last], "运行结束（最终状态）")
        self.code.tag_remove("hl", "1.0", "end")
        self.code.tag_add("hl", f"{last}.0", f"{last}.end")
        self.code.see(f"{last}.0")
        self.set_status(f"运行完成，共 {len(snaps)} 个状态；可用“上一步/下一步”逐步回放（共 {len(steps)} 步）", False)

    def reset(self):
        self.current_line = None
        self.code.tag_remove("hl", "1.0", "end")
        self.code.tag_remove("er", "1.0", "end")
        self.snapshots = {}
        self.step_list = []
        self.step_idx = -1
        self._input_requested = False
        self._pending_inputs = []
        self.draw_empty()
        self.set_status("已重置。点击代码行 / “下一步”逐步运行 / “运行全部”查看最终状态", False)

    def draw_empty(self):
        self.canvas.delete("all")
        self.canvas.create_text(20, 40, anchor="nw",
                                text="（暂无图形。点击左侧代码行，或点击“运行全部”）",
                                fill="#999999", font=("Microsoft YaHei", 12))
        self.drawer.fit()

    def redraw(self):
        if self.current_line and self.snapshots:
            snap = self.snapshots.get(self.current_line) or self.nearest_snap(
                self.snapshots, self.current_line)
            if snap:
                self.drawer.draw(snap, f"执行到第 {self.current_line} 行（该行执行后）")

    # ---------- 文件 / 粘贴 / 示例 ----------
    def open_file(self):
        path = filedialog.askopenfilename(
            title="选择 C/C++ 文件",
            filetypes=[("C/C++ 源文件", "*.c *.cpp *.cxx *.h *.txt"), ("所有文件", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except Exception as ex:
            messagebox.showerror("打开失败", str(ex))
            return
        self.load_example_text(text)
        self.set_status(f"已打开：{os.path.basename(path)}", False)

    def paste_code(self):
        win = tk.Toplevel(self.root)
        win.title("粘贴代码")
        win.geometry("700x460")
        txt = tk.Text(win, font=("Consolas", 11), wrap="none")
        txt.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        btns = tk.Frame(win)
        btns.pack(fill=tk.X, padx=6, pady=4)

        def ok():
            self.load_example_text(txt.get("1.0", "end-1c"))
            win.destroy()
            self.set_status("已粘贴代码", False)

        tk.Button(btns, text="载入并分析", command=ok,
                  bg="#1a5276", fg="white", padx=12).pack(side=tk.RIGHT)
        tk.Button(btns, text="取消", command=win.destroy,
                  bg="#888888", fg="white", padx=12).pack(side=tk.RIGHT, padx=8)

    def load_example(self, event=None):
        name = self.example_var.get()
        if name in EXAMPLES:
            self.load_example_text(EXAMPLES[name])

    def load_example_text(self, text):
        self.code.delete("1.0", "end")
        self.code.insert("1.0", text)
        self.code.edit_reset()
        self.snapshots = {}
        self.step_list = []
        self.step_idx = -1
        self._input_requested = False
        self._pending_inputs = []
        self.current_line = None
        self.snapshots = {}
        self.code.tag_remove("hl", "1.0", "end")
        self.code.tag_remove("er", "1.0", "end")
        self.highlight_syntax()
        self._upd_lines()
        # 载入后自动执行到第一条语句并立即显示，避免“没反应”
        self._auto_first()
        self.set_status(f"已载入代码（{len(text.splitlines())} 行）。点击代码行查看每一步状态", False)

    # 检测常见 C++ 特性，给出友好提示（本工具仅支持 C 子集）
    CPP_HINTS = ["cout", "cin", "endl", "::", "new ", "delete ",
                 "class ", "namespace", "template", "vector<",
                 "std::", "using namespace", "public:", "private:",
                 ".push_back", "->push_back", "#include <iostream>",
                 "#include <string>"]

    def detect_cpp_hint(self, code):
        for h in self.CPP_HINTS:
            if h in code:
                return h
        return None

    def _auto_first(self):
        """载入代码后自动执行第一行并显示；失败时给出明确提示（弹窗 + 标红）"""
        code = self.get_code()
        if not code.strip():
            self.draw_empty()
            return
        # C++ 特性提示
        hint = self.detect_cpp_hint(code)
        try:
            sim = Simulator(code)
            if sim.main_name() is None:
                self.draw_empty()
                msg = "没有找到 int main() 或任何函数定义，无法执行。\n请粘贴包含函数定义的完整代码片段。"
                self.set_status("未找到可执行函数", True)
                messagebox.showwarning("无法分析", msg)
                return
            snaps = sim.run()
            err = sim.engine.error if sim.engine else None
        except SimError as ex:
            self._show_load_error(ex, hint)
            return
        if err:
            self._show_load_error(SimError(err.line, err.msg), hint)
            return
        if not snaps:
            self.draw_empty()
            self.set_status("代码中没有可执行的语句", True)
            return
        first = min(snaps.keys())
        self.snapshots = snaps
        self.current_line = first
        self.code.tag_remove("hl", "1.0", "end")
        self.code.tag_add("hl", f"{first}.0", f"{first}.end")
        self.code.see(f"{first}.0")
        self.drawer.draw(snaps[first], f"执行到第 {first} 行（该行执行后）")
        if hint:
            self.set_status(f"提示：检测到 C++ 写法 '{hint}'，本工具主要支持 C 子集，部分内容可能无法模拟", True)
        else:
            self.set_status(f"已自动执行到第 {first} 行；点击任意代码行查看对应状态", False)

    def _show_load_error(self, ex, hint):
        self.draw_empty()
        self.highlight_error(ex.line)
        msg = f"无法分析该代码：\n{ex.msg}\n\n"
        if hint:
            msg += f"检测到 C++ 写法 '{hint}'，本工具目前支持 C 子集\n（结构体/指针/malloc/if/while/for/递归/数组）。\n"
        msg += "可参考内置示例的写法。"
        self.set_status(f"错误：{ex.msg}", True)
        if self._popup:
            messagebox.showwarning("无法分析该代码", msg)

    # ---------- 语法高亮（简单） ----------
    KEYWORDS = {"int", "char", "void", "struct", "typedef", "if", "else",
                "while", "for", "return", "break", "malloc", "calloc",
                "sizeof", "NULL", "main"}

    def highlight_syntax(self):
        self.code.tag_remove("kw", "1.0", "end")
        self.code.tag_remove("cm", "1.0", "end")
        self.code.tag_remove("ty", "1.0", "end")
        content = self.get_code()
        for i, line in enumerate(content.splitlines(), 1):
            self._hl_line(i, line)

    def _hl_line(self, ln, line):
        # 注释
        cm = line.find("//")
        if cm >= 0:
            self.code.tag_add("cm", f"{ln}.{cm}", f"{ln}.end")
            line = line[:cm]
        # 关键字 / 类型
        import re
        for m in re.finditer(r"[A-Za-z_]\w*", line):
            w = m.group()
            if w in self.KEYWORDS:
                self.code.tag_add("kw", f"{ln}.{m.start()}", f"{ln}.{m.end()}")
            elif w in ("Node", "TNode", "ListNode"):
                self.code.tag_add("ty", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

    def highlight_error(self, line):
        self.code.tag_add("er", f"{line}.0", f"{line}.end")
        self.code.see(f"{line}.0")

    def set_status(self, text, is_err=False):
        self.status.config(text=text,
                           fg="#c0392b" if is_err else "#333333")


def main():
    root = tk.Tk()
    try:
        style = ttk.Style()
        style.theme_use("vista")
    except Exception:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
