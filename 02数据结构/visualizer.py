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
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simcore import Simulator, SimError, is_cpp_code
from cppsim import CppSimulator


def make_simulator(code):
    """按代码内容分流：C++ 用 CppSimulator(独立引擎)，纯 C 用原 Simulator(零影响)"""
    if is_cpp_code(code):
        return CppSimulator(code)
    return Simulator(code)

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
# 辅助：自动模拟输入 / 语句行收集
# ---------------------------------------------------------------
def auto_gen_inputs(code, count=None):
    """扫描代码中的 scanf/getchar/gets 等，按格式生成合理随机输入（“模拟输入”）。"""
    import re, random
    inputs = []
    for m in re.finditer(r'scanf\s*\(\s*"([^"]*)"', code):
        fmt = m.group(1)
        for f in re.finditer(r'%([diuoxXfFeEgGcsp])', fmt):
            inputs.append(random.randint(1, 100))
    for m in re.finditer(r'\b(getchar|getch|getc|fgetc|getche)\s*\(', code):
        inputs.append(random.randint(65, 90))          # 字母 A-Z
    for m in re.finditer(r'\b(gets|getline|fgets)\s*\(', code):
        inputs.append(random.randint(1, 100))
    if not inputs:
        return []
    # 循环内 scanf 次数不定：保证足够数量
    while len(inputs) < 20:
        inputs.append(random.randint(1, 100))
    return inputs[:count] if count else inputs


def _stmt_lines(stmts):
    """递归收集语句树中所有语句的行号（用于判断某行属于哪个函数体）"""
    out = set()
    for st in stmts:
        out.add(st.line)
        for attr in ("body", "then_s", "else_s"):
            sub = getattr(st, attr, None)
            if isinstance(sub, list):
                out |= _stmt_lines(sub)
            elif sub is not None and hasattr(sub, "line"):
                out.add(sub.line)
    return out


# ---------------------------------------------------------------
# 绘制器：把快照画到 Canvas
# ---------------------------------------------------------------
def loc_tag(blk):
    """块的位置标签：[栈] / [堆]"""
    return "[栈]" if blk.get("loc") == "栈" else "[堆]"


class Drawer:
    NODE_W = 132
    NODE_H0 = 30          # 标题行高
    FIELD_H = 22          # 每字段行高
    GAP = 36              # 节点间距

    def __init__(self, canvas):
        self.c = canvas
        self.zoom = 1.0
        self.node_rects = {}        # addr -> (x, y, w, h)（缩放后画布坐标）
        self.panels = []            # 信息面板（块: 红/蓝 各1；指针: 绿1）
        self.ptr_boxes = {}         # 独立指针变量名 -> (x, y, w, h) 绿框
        self.ptr_vars = {}          # 指针变量名 -> 变量描述 v
        self.wrap_marks = {}        # 续接标记 canvas id -> 信息dict
        self.wrap_arrows = {}       # 续接标记 id -> 紫箭头 item id 列表
        self.ptr_links = {}         # 指针变量名 -> 目标块addr(点击绿框的高亮绿线)
        self.frames = []
        self.heap_by_addr = {}
        self._font_cache = {}
        self._fo_cache = {}
        # 缩放布局尺寸（draw 时按 zoom 计算；带下限，保证缩小后文字不挤压、清晰）
        self.lh = 20      # 变量区行高
        self.fh = 22      # 字段行高
        self.h0 = 30      # 节点标题高
        self.gap = 36     # 节点间距
        self.tlh = 19     # 帧标题行高
        self.last_audit = {"chains": 0, "nodes": 0, "arrows": 0,
                           "nulls": 0, "wilds": 0, "wraps": 0}

    # ---------- 字体（随缩放缩放；Tk 字号须为整数，下限 8 保证缩小后仍清晰） ----------
    def F(self, size, bold=False, fam="Consolas"):
        px = max(8, round(size * self.zoom))
        key = (fam, px, bold)
        if key not in self._font_cache:
            self._font_cache[key] = (fam, px, "bold" if bold else "normal")
        return self._font_cache[key]

    def FM(self, size, bold=False):
        return self.F(size, bold, "Microsoft YaHei")

    def fo(self, font):
        """缓存 Font 对象用于测量文字宽度"""
        if font not in self._fo_cache:
            try:
                self._fo_cache[font] = tkfont.Font(font=font)
            except Exception:
                self._fo_cache[font] = None
        return self._fo_cache[font]

    def mw(self, text, font):
        """测量文本宽度（像素）"""
        f = self.fo(font)
        if f is None:
            return len(text) * round(9 * self.zoom)
        return f.measure(text)

    def clear(self):
        self.c.delete("all")
        for p in self.panels:
            p["win_id"] = None
            p["line_id"] = None
        self.ptr_boxes = {}
        self.ptr_vars = {}
        self.wrap_marks = {}
        self.wrap_arrows = {}

    def draw(self, snap, msg="", diff_text=None, changed_vars=None):
        """布局：上方「调用栈/变量」，下方「内存/链表结构」；支持缩放 zoom。
        changed_vars: 本步发生变化的变量名集合（高亮显示）"""
        self.clear()
        z = self.zoom
        W = int(self.c.cget("width"))
        H = int(self.c.cget("height"))
        if W < 50 or H < 50:
            self.fit()
            return
        self.frames = snap.get("frames", [])
        heap = snap.get("heap", [])
        self.heap_by_addr = {b["addr"]: b for b in heap}
        frames = self.frames
        heap_by_addr = self.heap_by_addr
        self.last_audit = {"chains": 0, "nodes": 0, "arrows": 0,
                           "nulls": 0, "wilds": 0, "wraps": 0}
        changed_vars = changed_vars or set()
        # 布局尺寸（带下限）：缩小后文字可读、不挤压；放大后等比放大
        self.lh = max(18, round(20 * z))
        self.fh = max(18, round(self.FIELD_H * z))
        self.h0 = max(24, round(self.NODE_H0 * z))
        self.gap = max(16, round(self.GAP * z))
        self.tlh = max(18, round(19 * z))
        # 标题（含变更摘要）
        self.c.create_text(10 * z, 8 * z, anchor="nw", text=msg,
                           fill="#1a5276", font=self.FM(12, True))
        ty = 32 * z
        if diff_text:
            color = "#1a7f37" if "未修改" in diff_text else "#b35900"
            self.c.create_text(10 * z, ty, anchor="nw", text=diff_text,
                               fill=color, font=self.FM(10, True))
            ty += 20 * z

        # ---- 上方：调用栈 / 变量面板（高度完全自适应，不截断） ----
        vx = 10 * z
        vy = ty + 6 * z
        vw = W - 20 * z
        need_h = max(20, round(26 * z))
        for fr in frames:
            need_h += self.tlh + len(fr["vars"]) * self.lh + max(4, round(6 * z))
        ph = max(need_h + max(8, round(10 * z)), 44)
        self.c.create_rectangle(vx, vy, vx + vw, vy + ph, outline="#bbbbbb",
                                fill="#f4f6f8", width=1)
        self.c.create_text(vx + 8 * z, vy + 4 * z, anchor="nw",
                           text="调用栈 / 变量（栈上）",
                           fill="#555555", font=self.FM(11, True))
        yy = vy + max(18, round(24 * z))
        for fr in frames:
            # 帧标题底色条
            self.c.create_rectangle(vx + 2 * z, yy, vx + vw - 2 * z, yy + self.tlh,
                                    outline="", fill="#e8eaf6")
            self.c.create_text(vx + 8 * z, yy + 1, anchor="nw",
                               text="[ " + fr["func"] + " ]",
                               fill="#283593", font=self.FM(11, True))
            yy += self.tlh
            for name, v in fr["vars"]:
                line = self.fmt_var(name, v)
                warn = self._dangling_warn(v, heap_by_addr)
                if name in changed_vars:
                    # 本步变化的变量：浅黄高亮
                    self.c.create_rectangle(vx + 2 * z, yy - 1,
                                            vx + vw - 2 * z, yy + self.lh - 1,
                                            outline="", fill="#fff9c4")
                self.c.create_text(vx + 16 * z, yy, anchor="nw", text=line,
                                   fill="#c62828" if warn else "#333333",
                                   font=self.F(10))
                if warn:
                    _addr = v["value"][1] if v.get("value") and v["value"][0] == "ptr" else 0
                    _blk = heap_by_addr.get(_addr)
                    _tag = ("⚠指向已释放内存(悬垂指针)" if (_blk and _blk.get("freed"))
                            else "⚠指向未分配内存(野指针)")
                    self.c.create_text(vx + 16 * z + self.mw(line, self.F(10)) + 14 * z,
                                       yy, anchor="nw",
                                       text=_tag,
                                       fill="#c62828", font=self.FM(9, True))
                yy += self.lh
            yy += max(4, round(5 * z))
        # 提示
        self.c.create_text(vx + 8 * z, yy + 2 * z, anchor="nw",
                           text="▼ 下方为内存/结构图：拖动平移 · Ctrl+滚轮缩放 · 双击复位 · 点击内存块看详情",
                           fill="#888888", font=self.FM(9))

        # ---- 下方：堆 / 链表结构（起点在标题之下，标题不被第一排节点遮挡） ----
        hx0 = vx
        htop = vy + ph + max(24, round(34 * z))
        self.c.create_text(hx0, htop - max(14, round(16 * z)), anchor="nw",
                           text="内存 / 结构（■堆 ■栈）",
                           fill="#555555", font=self.FM(10, True))
        chain_heads = self.find_chains(frames, heap_by_addr)
        if chain_heads:
            bottom = self.draw_chains(chain_heads, heap_by_addr, hx0, htop, H)
        else:
            bottom = self.draw_heap_blocks(heap_by_addr, hx0, htop, H)
        self._draw_ptr_boxes(frames, heap_by_addr, hx0, bottom, H)
        self._draw_ptr_links()
        self._draw_info_panels()
        self.fit()

    def fit(self):
        """根据 Canvas 上所有元素自动设置滚动范围（排除右上角信息面板 window；
        scrollregion 始终从 (0,0) 开始，保证 canvasx/canvasy 与内容坐标一致，点击命中准确）"""
        try:
            coords = []
            for it in self.c.find_all():
                if self.c.type(it) == "window":
                    continue
                b = self.c.bbox(it)
                if b:
                    coords.append(b)
            if coords:
                x2 = max(c[2] for c in coords)
                y2 = max(c[3] for c in coords)
                self.c.configure(scrollregion=(0, 0, x2 + 40, y2 + 40))
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
                    blk = heap_by_addr[val[1]]
                    # 只有带字段的结构块才按“链”绘制；标量/数组块走普通网格
                    if blk["fields"]:
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
        # 标量堆块（malloc(sizeof(T)) 后 *p = x）：显示其值
        if not blk["fields"] and blk.get("scalar") is not None:
            sv = blk["scalar"]
            if sv[0] == "int":
                rows.append(("值", str(sv[1]), None))
            elif sv[0] == "ptr":
                rows.append(("值", f"0x{sv[1]:x}", sv[1]))
            else:
                rows.append(("值", "NULL", None))
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
        n = len(self.field_rows(blk))
        return self.h0 + max(1, n) * self.fh + 8

    def draw_node(self, x, y, addr, blk, heap_by_addr):
        """画一个内存块矩形（堆/栈分色，宽度按内容自适应，文字永不越界）
        返回 (右边缘x, 底部y)"""
        z = self.zoom
        h = self.node_height(blk)
        loc = blk.get("loc", "堆")
        freed = blk.get("freed", False)
        if loc == "栈":
            outline, fill = "#2e7d32", "#e8f5e9"   # 绿 = 栈上结构体变量
            loc_txt = "栈"
        elif freed:
            outline, fill = "#c62828", "#fdecea"   # 红 = 已释放(free)
            loc_txt = "堆·已释放"
        else:
            outline, fill = "#b8860b", "#fff8dc"   # 黄 = 堆(malloc)
            loc_txt = "堆"
        title = f"{blk['typename']} @0x{addr:x} [{loc_txt}]"
        tf = self.F(10, True)
        ff = self.F(10)
        title_w = self.mw(title, tf)
        field_lines = []
        for fn, disp, tgt in self.field_rows(blk):
            field_lines.append(f"{fn} -> {disp}" if tgt is not None else f"{fn} = {disp}")
        max_fw = max((self.mw(t, ff) for t in field_lines), default=0)
        w = max(self.NODE_W * z, title_w + 14 * z, max_fw + 14 * z)
        # 标题超宽则截断
        while self.mw(title + "…", tf) > w - 8 * z and len(title) > 1:
            title = title[:-1]
        title += "…"
        # 圆角矩形 + 标题底色条
        r = max(4, round(8 * z))
        self.round_rect(x, y, x + w, y + h, r, outline=outline, fill=fill, width=2)
        if loc == "栈":
            title_bg, title_fg = "#c8e6c9", "#1b5e20"
        elif freed:
            title_bg, title_fg = "#ffcdd2", "#b71c1c"
        else:
            title_bg, title_fg = "#ffe082", "#5d4037"
        self.c.create_rectangle(x + 2 * z, y + 2 * z, x + w - 2 * z,
                                y + self.h0 - 2 * z,
                                outline="", fill=title_bg)
        self.c.create_text(x + 6 * z, y + 4 * z, anchor="nw", text=title,
                           fill=title_fg, font=tf)
        yy = y + self.h0
        for txt in field_lines:
            # 字段超宽则截断
            while self.mw(txt + "…", ff) > w - 8 * z and len(txt) > 1:
                txt = txt[:-1]
            txt += "…"
            if "->" in txt:
                fill_c = "#1565c0"
            elif freed:
                fill_c = "#9e9e9e"
            elif txt.startswith("值 =") or " = " in txt:
                fill_c = "#2e7d32"
            else:
                fill_c = "#333333"
            self.c.create_text(x + 6 * z, yy, anchor="nw", text=txt,
                               fill=fill_c, font=ff)
            yy += self.fh
        if freed:
            # 已释放：底部画删除线
            self.c.create_line(x + 4 * z, y + h - 3 * z, x + w - 4 * z, y + h - 3 * z,
                               fill="#c62828", width=2, dash=(4, 3))
        self.node_rects[addr] = (x, y, w, h)
        return x + w, y + h

    def round_rect(self, x1, y1, x2, y2, r, **kw):
        """圆角矩形（用平滑多边形近似），比直角更精致"""
        pts = (x1 + r, y1, x2 - r, y1,
               x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
               x2 - r, y2, x1 + r, y2,
               x1, y2, x1, y2 - r, x1, y1 + r, x1, y1)
        return self.c.create_polygon(pts, smooth=True, **kw)

    def _dangling_warn(self, v, heap_by_addr):
        """指针变量指向堆外或已释放块且非 NULL → 野指针/悬垂指针警告"""
        val = v.get("value")
        if not val or val[0] != "ptr":
            return False
        addr = val[1]
        if addr == 0:
            return False
        blk = heap_by_addr.get(addr)
        if blk is None:
            return True      # 指向堆外（野指针）
        if blk.get("freed"):
            return True      # 指向已释放块（悬垂指针）
        return False

    def _next_target(self, blk):
        """返回该块 next 字段的目标地址(优先名为 next 的字段，适配双向链表；
        0=无/NULL, 非0=地址, None=函数指针等非指针目标(链结束,不画箭头))"""
        if "next" in blk["fields"]:
            fv = blk["fields"]["next"]
            if fv[0] == "ptr":
                return fv[1]
            if fv[0] == "null":
                return 0
            if fv[0] == "fn":
                return None   # 函数指针成员：以文本显示函数名，不画指向箭头
        for fn, fv in blk["fields"].items():
            if fv[0] == "ptr":
                return fv[1]
            if fv[0] == "fn":
                return None
        return 0

    def draw_chains(self, heads, heap_by_addr, x0, y0, H):
        """画链表：只画主链(优先级最高的 head)，其他指向同一链节点的变量作引用标注，
        避免同一堆块被重复绘制导致箭头错乱；独立链单独绘制，接入已画节点时断链标注。
        宽度适配可视区自动换行。"""
        z = self.zoom
        vis_w = int(self.c.cget("width")) / z          # 可视宽度（内容坐标）
        max_w = max(260, vis_w - 60)                    # 每行宽度上限
        self.last_audit["chains"] = len(heads)
        if not heads:
            return
        # 引用映射: addr -> [变量名]（除主链 label 外的所有指向）
        main_addr, main_label = heads[0]
        refs = {}
        for haddr, hlabel in heads:
            if haddr != main_addr or hlabel != main_label:
                refs.setdefault(haddr, []).append(hlabel)
        global_visited = set()
        for head_addr, head_label in heads:
            if head_addr in global_visited:
                continue
            x = x0
            y = y0
            visited = set()
            pos = {}
            cur = head_addr
            steps = 0
            prev = None                # (addr, rx, by) 上一节点，用于换行续接标记
            chain_bottom = y
            cycle_edges = set()        # 已画循环箭头的边 (from, to)
            while cur in heap_by_addr and cur not in visited and steps < 200:
                visited.add(cur)
                if cur in global_visited:
                    # 链在此接入已画节点：断链标注
                    self.c.create_text(x + 2, y - 16 * z, anchor="nw",
                                       text="↑ 接上方已画块", fill="#666666",
                                       font=self.FM(9, True))
                    break
                blk = heap_by_addr[cur]
                # 超出行宽 -> 换行：画大号可点击「续接」标记（不做误导性垂直短线+左侧转接）
                if prev is not None and x > x0 + max_w:
                    _paddr, prx, pby = prev
                    self._draw_wrap_mark(heap_by_addr, _paddr, prx, pby, cur, z)
                    y = pby + max(44, round(58 * z))
                    x = x0
                    self.last_audit["wraps"] += 1
                rx, by = self.draw_node(x, y, cur, blk, heap_by_addr)
                pos[cur] = (x, y, rx, by)
                # 续接标记的 to_rect 在此节点画完后回填（供紫箭头定位）
                for m in self.wrap_marks.values():
                    if m["to_addr"] == cur and m.get("to_rect") is None:
                        m["to_rect"] = (x, y, rx, by)
                chain_bottom = max(chain_bottom, by)
                self.last_audit["nodes"] += 1
                # 引用标注：其他变量也指向该块（只标注一次，不重复画链）
                if cur in refs:
                    tag = "← " + ", ".join(refs[cur])
                    self.c.create_text(x - 6 * z, y + self.h0,
                                       anchor="se", text=tag, fill="#666666",
                                       font=self.FM(9, True))
                # next 字段目标
                tgt = self._next_target(blk)
                if tgt in heap_by_addr:
                    if tgt in visited:
                        # 循环回边（尾节点→头 / head→head 自循环）：画清晰的循环箭头
                        self._draw_cycle_arrow(cur, pos[cur], blk, tgt, pos, z)
                        self.last_audit["arrows"] += 1
                        cycle_edges.add((cur, tgt))
                        break
                    prev = (cur, rx, by)
                    cur = tgt
                    x = rx + self.gap
                    steps += 1
                elif tgt is None:
                    # 函数指针等非指针目标：链结束，字段行已显示函数名，不画箭头
                    break
                else:
                    # next 为 NULL 或野指针 → 画带箭头的指向标记（与 next 字段行对齐）
                    self._draw_next_target(rx, y, self._next_field_idx(blk), tgt, z)
                    break
            # 画箭头：同一视觉行内连线（跨行由 ↘ 标记连接），高度对准 next 字段行
            # 循环回边已由 _draw_cycle_arrow 绘制，这里跳过避免重复
            for a, (bx, by, rx, _bh) in pos.items():
                blk = heap_by_addr[a]
                tgt = self._next_target(blk)
                if tgt in pos and (a, tgt) not in cycle_edges:
                    tx, ty, trx, _ = pos[tgt]
                    if abs(ty - by) < 2:
                        idx = self._next_field_idx(blk)
                        y1 = self._field_line_y(by, idx, z)
                        y2 = self._field_line_y(ty, idx, z)
                        self.arrow(rx + 1, y1, tx + 6, y2)
                        self.last_audit["arrows"] += 1
            self.c.create_text(x0, chain_bottom + 8 * z, anchor="nw",
                               text=f"← {head_label}",
                               fill="#666666", font=self.FM(10, True))
            y0 = chain_bottom + max(30, round(44 * z))   # 下一条链从本链底部下方开始
            global_visited.update(visited)
        return y0

    def _next_field_idx(self, blk):
        """返回 next 字段的序号(优先名为 next，适配双向链表)，用于箭头与该行对齐"""
        if "next" in blk["fields"]:
            for i, fn in enumerate(blk["fields"]):
                if fn == "next":
                    return i
        for i, fn in enumerate(blk["fields"]):
            if blk["fields"][fn][0] == "ptr":
                return i
        return 0

    def _field_line_y(self, y_top, idx, z):
        """节点内第 idx 个字段行的中心 y（绝对坐标，用带下限行高）"""
        return y_top + self.h0 + idx * self.fh + self.fh / 2

    def _draw_next_target(self, rx, y_top, idx, tgt, z):
        """画 next 指向 NULL 或野指针的标记：箭头从 next 字段行水平引出，与 NULL 对齐"""
        yline = self._field_line_y(y_top, idx, z)
        nx = rx + 8 * z
        off = max(4, round(7 * z))
        if tgt == 0:
            self.c.create_text(nx + 6, yline - off, anchor="nw",
                               text="NULL", fill="#8a8a8a",
                               font=self.F(9, True))
            self.arrow(rx + 1, yline, nx + 4, yline, color="#8a8a8a")
            self.last_audit["nulls"] += 1
        else:
            self.c.create_text(nx + 6, yline - off, anchor="nw",
                               text=f"⚠野指针 0x{tgt:x}", fill="#c62828",
                               font=self.F(9, True))
            self.arrow(rx + 1, yline, nx + 4, yline, color="#c62828")
            self.last_audit["wilds"] += 1

    def _draw_cycle_arrow(self, cur_addr, from_rect, blk, to_addr, pos, z):
        """画循环链表的回边箭头：尾节点→头节点 / 头节点自循环。
        橙色折线从 next 字段行绕行到目标节点 next 字段行，标注 ↺，一眼看清谁指向谁。"""
        bx, by, rx, _bh = from_rect
        idx = self._next_field_idx(blk)
        y1 = self._field_line_y(by, idx, z)
        if to_addr == cur_addr:
            # 自循环：节点右侧画小回环（head->next = head）
            arc_x = rx + max(10, round(14 * z))
            arc_y = y1 - max(10, round(14 * z))
            self.c.create_oval(arc_x, arc_y, arc_x + max(18, round(22 * z)),
                               arc_y + max(18, round(22 * z)),
                               outline="#e65100", width=2)
            self.c.create_line(rx + 1, y1, arc_x, y1, fill="#e65100", width=2)
            self.c.create_line(arc_x + max(18, round(22 * z)), y1,
                               arc_x + max(22, round(26 * z)), y1,
                               fill="#e65100", width=2, arrow=tk.LAST,
                               arrowshape=(7, 10, 4))
            self.c.create_text(arc_x, y1 + max(16, round(20 * z)), anchor="nw",
                               text="↺ 自循环", fill="#e65100",
                               font=self.FM(8, True))
            return
        if to_addr not in pos:
            return
        tx, ty, trx, _ = pos[to_addr]
        to_idx = self._next_field_idx(self.heap_by_addr.get(to_addr) or {})
        y2 = self._field_line_y(ty, to_idx, z)
        # 折线：从本节点 next 字段行 → 向下 → 水平到目标右侧 → 箭头向上指向目标 next 行
        mid_y = max(y1, y2) + max(16, round(22 * z))
        self.c.create_line(rx + 1, y1, rx + 1, mid_y, fill="#e65100", width=2)
        self.c.create_line(rx + 1, mid_y, trx + 6, mid_y, fill="#e65100", width=2)
        self.c.create_line(trx + 6, mid_y, trx + 6, y2, fill="#e65100", width=2,
                           arrow=tk.LAST, arrowshape=(8, 11, 5))
        self.c.create_text((rx + 1 + trx + 6) / 2, mid_y + max(4, round(6 * z)),
                           anchor="n", text="↺ 循环返回", fill="#e65100",
                           font=self.FM(8, True))

    def draw_heap_blocks(self, heap_by_addr, x0, y0, H):
        z = self.zoom
        x = x0
        y = y0
        row_bottom = y0          # 当前行所有块的最大底部(避免高低块混排换行后重叠)
        vis_w = int(self.c.cget("width")) / z
        for addr in sorted(heap_by_addr.keys()):
            blk = heap_by_addr[addr]
            rx, by = self.draw_node(x, y, addr, blk, heap_by_addr)
            row_bottom = max(row_bottom, by)
            x = rx + self.gap
            if x > x0 + vis_w - 60:
                x = x0
                y = row_bottom + max(30, round(40 * z))
                row_bottom = y
        return row_bottom + max(30, round(40 * z))

    def _draw_ptr_boxes(self, frames, heap_by_addr, x0, top, H):
        """为独立定义的指针变量（结构体/联合体字段指针除外）画淡绿色小框。
        文字居中不溢出，每框独立；点击绿框→绿色面板 + 绿色高亮线连到内存框图。"""
        z = self.zoom
        ptrs = []
        for fr in frames:
            for name, v in fr["vars"]:
                val = v.get("value")
                if val and val[0] in ("ptr", "null"):
                    ptrs.append((name, v))
        if not ptrs:
            return top
        vis_w = int(self.c.cget("width")) / z
        x = x0
        y = top + max(14, round(20 * z))
        self.c.create_text(x0, y - 8 * z, anchor="nw",
                           text="■ 指针变量（点击绿框查看指向详情）",
                           fill="#2e7d32", font=self.FM(9, True))
        y += max(8, round(12 * z))
        bh = max(24, round(28 * z))
        nf = self.F(9, True)
        for name, v in ptrs:
            val = v["value"]
            if val[0] == "ptr":
                txt = f"{name} → 0x{val[1]:x}"
            else:
                txt = f"{name} → NULL"
            # 文字过宽则截断（保证不溢出框）
            bw = self.mw(txt, nf) + 20 * z
            while self.mw(txt + "…", nf) > bw - 8 * z and len(txt) > 3:
                txt = txt[:-1]
            if self.mw(txt, nf) > bw - 8 * z:
                txt = txt + "…"
            if x > x0 and x + bw > x0 + vis_w - 40:
                x = x0
                y += bh + 8 * z
            # 淡绿圆角框，文字居中（anchor=center 保证文本在框内）
            self.round_rect(x, y, x + bw, y + bh, max(4, round(7 * z)),
                            outline="#43a047", fill="#e8f5e9", width=1)
            self.c.create_text(x + bw / 2, y + bh / 2, text=txt, fill="#1b5e20",
                               font=nf)
            self.ptr_boxes[name] = (x, y, bw, bh)
            self.ptr_vars[name] = v
            x += bw + 8 * z
        return y + bh + max(10, round(16 * z))

    def _toggle_ptr_link(self, name):
        """点击指针绿框：切换绿色高亮线（连到该指针指向的内存框图）"""
        v = self.ptr_vars.get(name)
        val = v.get("value") if v else None
        target = val[1] if val and val[0] == "ptr" else None
        if name in self.ptr_links:
            del self.ptr_links[name]
        elif target is not None:
            self.ptr_links[name] = target
        else:
            self.ptr_links[name] = None      # NULL 指针：画到绿框下方的 NULL 标记

    def _draw_ptr_links(self):
        """重画指针高亮绿线：从绿框中心连到指向的内存框图（粗亮绿线）"""
        z = self.zoom
        for name, target in list(self.ptr_links.items()):
            box = self.ptr_boxes.get(name)
            if not box:
                continue
            bx, by, bw, bh = box
            sx, sy = bx + bw / 2, by + bh / 2
            if target is None:
                # NULL：向下画一小段带箭头的绿线 + NULL 标注
                ex, ey = sx, sy + max(16, round(20 * z))
                self.c.create_line(sx, sy, ex, ey, fill="#00c853", width=3,
                                   arrow=tk.LAST, arrowshape=(8, 11, 5))
                self.c.create_text(ex + 6, ey, anchor="nw", text="NULL",
                                   fill="#2e7d32", font=self.F(9, True))
                continue
            rect = self.node_rects.get(target)
            if not rect:
                continue
            tx, ty, tw, th = rect
            ex, ey = tx + tw / 2, ty - 2            # 指向目标框图顶部中心
            self.c.create_line(sx, sy, ex, ey, fill="#00c853", width=3,
                               arrow=tk.LAST, arrowshape=(8, 11, 5))
            # 起点小圆点强调
            self.c.create_oval(sx - 4, sy - 4, sx + 4, sy + 4,
                               fill="#00c853", outline="")

    def _draw_wrap_mark(self, heap_by_addr, from_addr, prx, pby, to_addr, z):
        """画大号可点击「续接」标记：位于上一节点右侧/下方，点击后从发出起点
        显示高亮紫色垂直箭头指向下一排节点。返回标记 id。"""
        mk_w = max(60, round(74 * z))
        mk_h = max(24, round(30 * z))
        mkx = prx - mk_w - 8 * z
        mky = pby + max(8, round(12 * z))
        mid = self.round_rect(mkx, mky, mkx + mk_w, mky + mk_h,
                              max(5, round(9 * z)),
                              outline="#1565c0", fill="#e3f2fd", width=2)
        self.c.create_text(mkx + mk_w / 2, mky + mk_h / 2,
                           text="↘ 续接", fill="#0d47a1", font=self.FM(9, True))
        # 上一节点底部 → 续接标记 的短引线（表示从此处向下续接）
        self.c.create_line(prx - mk_w / 2, pby + 2, prx - mk_w / 2, mky,
                           fill="#1565c0", width=2, dash=(3, 2))
        self.wrap_marks[mid] = {"rect": (mkx, mky, mkx + mk_w, mky + mk_h),
                                "from_addr": from_addr,
                                "from_idx": self._next_field_idx(
                                    heap_by_addr.get(from_addr) or {}),
                                "to_addr": to_addr, "to_rect": None}
        return mid

    def _toggle_wrap_arrow(self, mid):
        """点击续接标记：从发出起点(上一节点 next 字段行)出现高亮紫色垂直箭头，
        垂直向下指向下一排节点框图；再点一次隐藏。"""
        info = self.wrap_marks.get(mid)
        if not info:
            return
        if mid in self.wrap_arrows:
            for it in self.wrap_arrows[mid]:
                try:
                    self.c.delete(it)
                except Exception:
                    pass
            del self.wrap_arrows[mid]
            return
        frect = self.node_rects.get(info["from_addr"])
        to_rect = info.get("to_rect")
        if not frect or not to_rect:
            return
        z = self.zoom
        fx, fy, fw, fh = frect
        tx, ty, tw, th = to_rect
        y1 = fy + self.h0 + info["from_idx"] * self.fh + self.fh / 2
        x_start = fx + fw + 2          # 发出起点：节点右边缘 next 字段行
        y_end = ty + 2                 # 指向下一排节点顶部
        x_end = tx + tw / 2            # 下一排节点中心
        items = []
        if abs(x_end - x_start) > 4:
            # 主体垂直向下，末尾水平对准目标节点中心
            items.append(self.c.create_line(x_start, y1, x_start, y_end,
                                            fill="#9c27b0", width=3))
            items.append(self.c.create_line(x_start, y_end, x_end, y_end,
                                            fill="#9c27b0", width=3,
                                            arrow=tk.LAST,
                                            arrowshape=(10, 14, 6)))
        else:
            items.append(self.c.create_line(x_start, y1, x_end, y_end,
                                            fill="#9c27b0", width=3,
                                            arrow=tk.LAST,
                                            arrowshape=(10, 14, 6)))
        # 起点高亮圆点 + 说明
        items.append(self.c.create_oval(x_start - 4, y1 - 4, x_start + 4, y1 + 4,
                                        fill="#9c27b0", outline=""))
        items.append(self.c.create_text(x_start + 6, y1 - 12, anchor="nw",
                                        text="↑ 指向起点", fill="#9c27b0",
                                        font=self.FM(9, True)))
        self.wrap_arrows[mid] = items

    def arrow(self, x1, y1, x2, y2, color="#1565c0"):
        az = max(0.6, self.zoom)
        self.c.create_line(x1, y1, x2, y2, fill=color,
                           width=max(1.5, 2 * self.zoom),
                           arrow=tk.LAST,
                           arrowshape=(max(6, round(12 * az)),
                                       max(8, round(15 * az)),
                                       max(3, round(7 * az))))

    # ---------- 信息面板（点击内存块/指针框显示详情）：块红/蓝各1 + 指针绿1，可拖动/关闭 ----------
    # 第 1 个：右上角·红色连线；第 2 个：右下角·蓝色连线；指针：绿色·可拖动
    def _add_panel(self, addr):
        if any(p["kind"] == "blk" and p["addr"] == addr for p in self.panels):
            return
        blks = [p for p in self.panels if p["kind"] == "blk"]
        if len(blks) >= 2:                            # 块面板超过 2 个：移除最旧的
            self._remove_panel(blks[0]["addr"])
        is_first = len([p for p in self.panels if p["kind"] == "blk"]) == 0
        color = "#e53935" if is_first else "#1e88e5"
        cw = max(240, self.c.winfo_width())
        ch = max(240, self.c.winfo_height())
        dx = cw - 20
        dy = 20 if is_first else ch - 20
        self.panels.append({"kind": "blk", "addr": addr, "color": color,
                            "dx": dx, "dy": dy,
                            "anchor": "ne" if is_first else "se",
                            "win_id": None, "line_id": None, "frame": None})

    def _remove_panel(self, addr):
        for p in self.panels:
            if p["kind"] == "blk" and p["addr"] == addr:
                if p.get("win_id"):
                    try:
                        self.c.delete(p["win_id"])
                    except Exception:
                        pass
                if p.get("line_id"):
                    try:
                        self.c.delete(p["line_id"])
                    except Exception:
                        pass
                self.c.delete(f"hl_{addr}")
                self.panels.remove(p)
                break
        # 移除后重新分配：始终第1个=红·右上，第2个=蓝·右下（只影响块面板）
        cw = max(240, self.c.winfo_width())
        ch = max(240, self.c.winfo_height())
        blks = [p for p in self.panels if p["kind"] == "blk"]
        for i, p in enumerate(blks):
            p["color"] = "#e53935" if i == 0 else "#1e88e5"
            p["dx"] = cw - 20
            p["dy"] = 20 if i == 0 else ch - 20
            p["anchor"] = "ne" if i == 0 else "se"

    def _add_ptr_panel(self, name):
        """指针绿框 → 绿色解释面板（最多 1 个）"""
        if any(p["kind"] == "ptr" and p["name"] == name for p in self.panels):
            return
        for p in [p for p in self.panels if p["kind"] == "ptr"]:
            self._remove_ptr_panel(p["name"])
        cw = max(240, self.c.winfo_width())
        ch = max(240, self.c.winfo_height())
        self.panels.append({"kind": "ptr", "name": name, "addr": None,
                            "color": "#43a047", "dx": cw - 340, "dy": 20,
                            "anchor": "nw", "win_id": None, "line_id": None,
                            "frame": None})

    def _remove_ptr_panel(self, name):
        for p in self.panels:
            if p["kind"] == "ptr" and p["name"] == name:
                if p.get("win_id"):
                    try:
                        self.c.delete(p["win_id"])
                    except Exception:
                        pass
                if p.get("line_id"):
                    try:
                        self.c.delete(p["line_id"])
                    except Exception:
                        pass
                self.c.delete(f"hp_{name}")
                self.panels.remove(p)
                break

    def _draw_info_panels(self):
        for p in list(self.panels):
            self._draw_panel(p)

    def _draw_panel(self, p):
        if p["kind"] == "ptr":
            self._draw_ptr_panel(p)
            return
        addr = p["addr"]
        blk = self.heap_by_addr.get(addr)
        if blk is None:
            return
        # 选中节点描边（红/蓝，外扩 3px）
        rect = self.node_rects.get(addr)
        if rect:
            x, y, w, h = rect
            self.c.delete(f"hl_{addr}")
            self.round_rect(x - 3, y - 3, x + w + 3, y + h + 3,
                            max(5, round(8 * self.zoom)),
                            outline=p["color"], fill="", width=3,
                            tags=(f"hl_{addr}",))
        # 面板
        frame = self._make_panel_frame(blk, addr, p["color"])
        p["frame"] = frame
        x0 = self.c.canvasx(0) + p["dx"]
        y0 = self.c.canvasy(0) + p["dy"]
        p["win_id"] = self.c.create_window(x0, y0, anchor=p["anchor"], window=frame)
        self._bind_panel_drag(frame, p)
        self._draw_panel_link(p)

    def _make_panel_frame(self, blk, addr, color):
        frame = tk.Frame(self.c, bg="#ffffff", highlightbackground=color,
                         highlightthickness=2)
        # 标题栏（含关闭叉叉）
        bar = tk.Frame(frame, bg=color)
        bar.pack(fill=tk.X)
        loc = blk.get("loc", "堆")
        loc_cn = "栈(结构体变量)" if loc == "栈" else "堆(malloc)"
        if blk.get("freed"):
            loc_cn += " · 已释放"
        tk.Label(bar, text=f"◆ {blk['typename']} @0x{addr:x}  [{loc_cn}]",
                 bg=color, fg="white", font=("Microsoft YaHei", 11, "bold"),
                 anchor="w", padx=8, pady=3).pack(side=tk.LEFT, fill=tk.X, expand=True)
        close = tk.Label(bar, text="✕", bg=color, fg="white", cursor="hand2",
                         font=("Microsoft YaHei", 13, "bold"), padx=7, pady=3)
        close.pack(side=tk.RIGHT)
        close.bind("<Button-1>",
                   lambda e: (self._remove_panel(addr), "break")[1])
        # 被哪些变量引用
        owners = []
        for fr in self.frames:
            for name, v in fr["vars"]:
                val = v.get("value")
                if val and val[0] == "ptr" and val[1] == addr:
                    owners.append(name)
        owner_txt = "被变量引用: " + ", ".join(owners) if owners else "未被任何变量直接引用"
        tk.Label(frame, text=owner_txt, bg="#ffffff", fg=color,
                 font=("Microsoft YaHei", 10, "bold"), anchor="w",
                 padx=8).pack(fill=tk.X)
        # 标量值（malloc 标量块）
        if not blk.get("fields") and blk.get("scalar") is not None:
            sv = blk["scalar"]
            val_s = (str(sv[1]) if sv[0] == "int"
                     else (f"0x{sv[1]:x}" if sv[0] == "ptr" else "NULL"))
            tk.Label(frame, text=f"  值 = {val_s}", bg="#ffffff", fg="#2e7d32",
                     font=("Consolas", 10), anchor="w", padx=8).pack(fill=tk.X)
        # 字段详情
        rows = self.field_rows(blk)
        extra = 0
        if len(rows) > 12:
            rows, extra = rows[:12], len(rows) - 12
        for fn, disp, tgt in rows:
            if tgt is not None:
                line = f"  {fn}  →  0x{tgt:x}"
            else:
                line = f"  {fn}  =  {disp}"
            tk.Label(frame, text=line, bg="#ffffff", fg="#333333",
                     font=("Consolas", 10), anchor="w", padx=8).pack(fill=tk.X)
        if extra:
            tk.Label(frame, text=f"  … 等 {extra} 个字段", bg="#ffffff",
                     fg="#888888", font=("Microsoft YaHei", 9),
                     anchor="w", padx=8).pack(fill=tk.X)
        # 底部状态条
        st = f"  状态: {'已释放(free)' if blk.get('freed') else '有效内存'} · 类型位置: {loc_cn}"
        tk.Label(frame, text=st, bg="#f5f5f5", fg="#666666",
                 font=("Microsoft YaHei", 9), anchor="w",
                 padx=8, pady=2).pack(fill=tk.X)
        return frame

    def _draw_ptr_panel(self, p):
        """指针绿框 → 绿色解释面板"""
        name = p["name"]
        v = self.ptr_vars.get(name)
        if v is None:
            return
        rect = self.ptr_boxes.get(name)
        if rect:
            x, y, w, h = rect
            self.c.delete(f"hp_{name}")
            self.round_rect(x - 3, y - 3, x + w + 3, y + h + 3,
                            max(5, round(8 * self.zoom)),
                            outline=p["color"], fill="", width=3,
                            tags=(f"hp_{name}",))
        frame = self._make_ptr_panel_frame(name, v, p["color"])
        p["frame"] = frame
        x0 = self.c.canvasx(0) + p["dx"]
        y0 = self.c.canvasy(0) + p["dy"]
        p["win_id"] = self.c.create_window(x0, y0, anchor=p["anchor"], window=frame)
        self._bind_panel_drag(frame, p)
        self._draw_panel_link(p)

    def _make_ptr_panel_frame(self, name, v, color):
        """绿色解释面板：说明指针指向的目标、地址是什么"""
        frame = tk.Frame(self.c, bg="#ffffff", highlightbackground=color,
                         highlightthickness=2)
        bar = tk.Frame(frame, bg=color)
        bar.pack(fill=tk.X)
        tk.Label(bar, text=f"◆ 指针变量 {name}", bg=color, fg="white",
                 font=("Microsoft YaHei", 11, "bold"), anchor="w",
                 padx=8, pady=3).pack(side=tk.LEFT, fill=tk.X, expand=True)
        close = tk.Label(bar, text="✕", bg=color, fg="white", cursor="hand2",
                         font=("Microsoft YaHei", 13, "bold"), padx=7, pady=3)
        close.pack(side=tk.RIGHT)
        close.bind("<Button-1>",
                   lambda e: (self._remove_ptr_panel(name), "break")[1])
        t = v.get("type", "指针")
        val = v.get("value")
        tk.Label(frame, text=f"  类型: {t}", bg="#ffffff", fg="#333333",
                 font=("Consolas", 10), anchor="w", padx=8).pack(fill=tk.X)
        if val and val[0] == "ptr":
            addr = val[1]
            tk.Label(frame, text=f"  指向地址: 0x{addr:x}", bg="#ffffff", fg=color,
                     font=("Consolas", 10, "bold"), anchor="w", padx=8).pack(fill=tk.X)
            blk = self.heap_by_addr.get(addr)
            if blk is None:
                tk.Label(frame, text="  目标: ⚠ 指向未分配内存（野指针）",
                         bg="#ffffff", fg="#c62828",
                         font=("Microsoft YaHei", 10), anchor="w",
                         padx=8).pack(fill=tk.X)
            elif blk.get("freed"):
                tk.Label(frame, text=f"  目标: ⚠ 指向已释放内存 @0x{addr:x}",
                         bg="#ffffff", fg="#c62828",
                         font=("Microsoft YaHei", 10), anchor="w",
                         padx=8).pack(fill=tk.X)
            else:
                loc_cn = "栈(结构体变量)" if blk.get("loc") == "栈" else "堆(malloc)"
                tk.Label(frame,
                         text=f"  目标: {blk['typename']} @0x{addr:x} [{loc_cn}]",
                         bg="#ffffff", fg="#2e7d32",
                         font=("Microsoft YaHei", 10, "bold"), anchor="w",
                         padx=8).pack(fill=tk.X)
                if not blk.get("fields") and blk.get("scalar") is not None:
                    sv = blk["scalar"]
                    vs = (str(sv[1]) if sv[0] == "int"
                          else (f"0x{sv[1]:x}" if sv[0] == "ptr" else "NULL"))
                    tk.Label(frame, text=f"  内容: 值 = {vs}", bg="#ffffff",
                             fg="#333333", font=("Consolas", 10), anchor="w",
                             padx=8).pack(fill=tk.X)
                else:
                    for fn, fv in list(blk.get("fields", {}).items())[:3]:
                        if fv[0] == "ptr":
                            disp = f"0x{fv[1]:x}"
                        elif fv[0] == "null":
                            disp = "NULL"
                        else:
                            disp = str(fv[1])
                        tk.Label(frame, text=f"  内容: {fn} = {disp}",
                                 bg="#ffffff", fg="#333333",
                                 font=("Consolas", 10), anchor="w",
                                 padx=8).pack(fill=tk.X)
        elif val and val[0] == "null":
            tk.Label(frame, text="  指向: NULL（未指向任何内存）", bg="#ffffff",
                     fg="#8a8a8a", font=("Microsoft YaHei", 10), anchor="w",
                     padx=8).pack(fill=tk.X)
        tk.Label(frame, text="  状态: 独立指针变量（不含结构体/联合体内部指针）",
                 bg="#f5f5f5", fg="#666666", font=("Microsoft YaHei", 9),
                 anchor="w", padx=8, pady=2).pack(fill=tk.X)
        return frame

    def _draw_panel_link(self, p):
        """节点中心/指针框中心 → 面板 的细虚线连接线（不显眼）"""
        if p.get("line_id"):
            try:
                self.c.delete(p["line_id"])
            except Exception:
                pass
            p["line_id"] = None
        if p["kind"] == "ptr":
            rect = self.ptr_boxes.get(p["name"])
        else:
            rect = self.node_rects.get(p["addr"])
        if not rect or not p.get("win_id"):
            return
        x, y, w, h = rect
        nx, ny = x + w / 2, y + h / 2
        try:
            wx, wy = self.c.coords(p["win_id"])
        except Exception:
            return
        p["line_id"] = self.c.create_line(nx, ny, wx, wy, fill=p["color"],
                                          width=1, dash=(4, 3))

    def _bind_panel_drag(self, frame, p):
        """面板可拖动（递归绑定子控件），拖动时同步连线"""
        def start(ev):
            p["_ds"] = (ev.x_root, ev.y_root, p["dx"], p["dy"])
        def move(ev):
            ds = p.get("_ds")
            if not ds:
                return
            sx, sy, dx0, dy0 = ds
            p["dx"] = dx0 + (ev.x_root - sx)
            p["dy"] = dy0 + (ev.y_root - sy)
            try:
                x0 = self.c.canvasx(0)
                y0 = self.c.canvasy(0)
                self.c.coords(p["win_id"], x0 + p["dx"], y0 + p["dy"])
                self._draw_panel_link(p)
            except Exception:
                pass
        def rec(w):
            w.bind("<ButtonPress-1>", start, add="+")
            w.bind("<B1-Motion>", move, add="+")
            for ch in w.winfo_children():
                rec(ch)
        rec(frame)


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
        self._free_active = False     # 自由测试模式是否激活
        self._run_count = 0           # 运行日志计数
        self._input_slots = {}        # 输入点行号 -> [已输入值]（级联格式化用）
        self._auto_slots = {}         # 输入点行号 -> 是否模拟输入

        # ---- 顶部工具栏 ----
        bar = tk.Frame(root, bg="#2c3e50")
        bar.pack(side=tk.TOP, fill=tk.X)
        def btn(t, fn):
            b = tk.Button(bar, text=t, command=fn, bg="#34495e", fg="white",
                          relief=tk.FLAT, padx=10, cursor="hand2",
                          activebackground="#5d6d7e", activeforeground="white",
                          font=("Microsoft YaHei", 10))
            b.bind("<Enter>", lambda e: b.config(bg="#3e5c76"))
            b.bind("<Leave>", lambda e: b.config(bg="#34495e"))
            return b
        btn("📂 打开文件", self.open_file).pack(side=tk.LEFT, padx=4, pady=4)
        btn("📋 粘贴代码", self.paste_code).pack(side=tk.LEFT, padx=4, pady=4)
        btn("◀ 上一步", self.step_prev).pack(side=tk.LEFT, padx=4, pady=4)
        btn("下一步 ▶", self.step_next).pack(side=tk.LEFT, padx=4, pady=4)
        btn("↩ 返回调用处", self.step_back_to_caller).pack(side=tk.LEFT, padx=4, pady=4)
        # ---- 运行模式：主按钮(当前模式) + ⋯ 下拉(展开其他模式) ----
        self.run_mode = "常规运行"
        self.mode_btn = btn(self.run_mode, self.run_current_mode)
        self.mode_btn.pack(side=tk.LEFT, padx=(4, 2), pady=4)
        self.mode_menu = tk.Menu(bar, tearoff=0)
        self.mode_menu.add_command(label="常规运行", command=lambda: self.set_run_mode("常规运行"))
        self.mode_menu.add_command(label="快速运行", command=lambda: self.set_run_mode("快速运行"))
        self.mode_menu.add_command(label="自由运行", command=lambda: self.set_run_mode("自由运行"))
        btn_dots = tk.Button(bar, text="⋯", command=self._popup_mode_menu,
                             bg="#34495e", fg="white", relief=tk.FLAT,
                             font=("Microsoft YaHei", 13, "bold"),
                             padx=6, pady=1, cursor="hand2",
                             activebackground="#5d6d7e", activeforeground="white")
        btn_dots.bind("<Enter>", lambda e: btn_dots.config(bg="#3e5c76"))
        btn_dots.bind("<Leave>", lambda e: btn_dots.config(bg="#34495e"))
        btn_dots.pack(side=tk.LEFT, padx=(0, 4), pady=4)
        btn("↺ 重置", self.reset).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Label(bar, text="示例:", bg="#2c3e50", fg="white",
                 font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=(16, 2))
        self.example_var = tk.StringVar()
        ex = ttk.Combobox(bar, textvariable=self.example_var, state="readonly",
                          width=18, values=list(EXAMPLES.keys()))
        ex.pack(side=tk.LEFT, padx=2)
        ex.bind("<<ComboboxSelected>>", self.load_example)
        # 右上角：运行状态栏（跑通=绿，未跑通=红+!!!；操作提示已移入 README）
        self.run_status = tk.Label(bar, text="● 就绪", bg="#2c3e50", fg="#bdc3c7",
                                   font=("Microsoft YaHei", 10, "bold"))
        self.run_status.pack(side=tk.RIGHT, padx=12)
        # 键盘快捷键：←/→ 逐步回放
        root.bind("<Left>", lambda e: self.step_prev())
        root.bind("<Right>", lambda e: self.step_next())

        # ---- 主区域：左日志 | 左代码 | 右图 ----
        outer = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashwidth=6)
        outer.pack(fill=tk.BOTH, expand=True)

        # 日志面板（代码区左侧，终端样式）
        logf = tk.Frame(outer, bg="#0c0c0c")
        outer.add(logf, minsize=200, width=250)
        loghdr = tk.Frame(logf, bg="#0c0c0c")
        loghdr.pack(fill=tk.X)
        tk.Label(loghdr, text="📜 运行日志", bg="#0c0c0c", fg="#cccccc",
                 font=("Microsoft YaHei", 10, "bold"), anchor="w",
                 padx=6, pady=3).pack(side=tk.LEFT, fill=tk.X, expand=True)
        clr = tk.Button(loghdr, text="🧹 清理日志", command=self.clear_log,
                        bg="#2b2b2b", fg="#b0b0b0", relief=tk.FLAT,
                        cursor="hand2", activebackground="#3e3e3e",
                        activeforeground="white",
                        font=("Microsoft YaHei", 8))
        clr.bind("<Enter>", lambda e: clr.config(bg="#3e5c76", fg="white"))
        clr.bind("<Leave>", lambda e: clr.config(bg="#2b2b2b", fg="#b0b0b0"))
        clr.pack(side=tk.RIGHT, padx=6, pady=2)
        self.logbox = tk.Text(logf, bg="#0c0c0c", fg="#e0e0e0", wrap="word",
                              font=("Consolas", 10), relief=tk.FLAT,
                              padx=6, pady=4, state=tk.DISABLED)
        self.logbox.pack(fill=tk.BOTH, expand=True)
        logsb = tk.Scrollbar(logf, command=self.logbox.yview, width=14,
                             bg="#555555", troughcolor="#0c0c0c",
                             activebackground="#777777")
        logsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.logbox.config(yscrollcommand=logsb.set)

        main = tk.PanedWindow(outer, orient=tk.HORIZONTAL, sashwidth=6)
        outer.add(main, minsize=700, width=880)

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
                            insertbackground="#d4d4d4", font=("Consolas", 13),
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
        self.canvas = tk.Canvas(right, bg="#ffffff", highlightthickness=0,
                                cursor="hand2")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb = tk.Scrollbar(right, orient=tk.VERTICAL, command=self._cv_yview,
                           width=20, bg="#569cd6", troughcolor="#e0e0e0",
                           activebackground="#4a90c2")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb = tk.Scrollbar(right, orient=tk.HORIZONTAL, command=self._cv_xview,
                           width=20, bg="#569cd6", troughcolor="#e0e0e0",
                           activebackground="#4a90c2")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.vsb, self.hsb = vsb, hsb
        self.canvas.config(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.canvas.bind("<Configure>", lambda e: self.redraw())
        # 交互：滚轮(点哪滚哪)、Ctrl+滚轮缩放、拖拽平移、单击看详情、双击复位缩放
        self.canvas.bind("<MouseWheel>", self._cv_wheel)
        self.canvas.bind("<Button-4>", self._cv_wheel_lin)
        self.canvas.bind("<Button-5>", self._cv_wheel_lin)
        self.canvas.bind("<ButtonPress-1>", self._cv_press)
        self.canvas.bind("<B1-Motion>", self._cv_drag)
        self.canvas.bind("<ButtonRelease-1>", self._cv_release)
        self.canvas.bind("<Double-Button-1>", self._zoom_reset)
        self.drawer = Drawer(self.canvas)
        self._canvas_mouse_down = False
        self._dragging = False
        self._press_x = self._press_y = 0

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
                                             font=("Consolas", 12))

    def get_code(self):
        return self.code.get("1.0", "end-1c")

    def on_code_click(self, event):
        idx = self.code.index(f"@{event.x},{event.y}")
        line = int(float(idx.split(".")[0]))
        self.show_line(line)
        # 点到输入步骤 → 触发输入窗（常规运行 main 内/自由运行均可）
        if self._is_input_line(line):
            self._open_input_window(line)

    def show_line(self, line):
        """点击某行：执行到该行，右侧显示状态。
        常规运行模式下仅允许点击 main 函数体；进入调用函数请用“下一步”。"""
        if self.run_mode == "常规运行" and not self._line_in_main(line):
            self.set_status(f"常规运行：第 {line} 行不在 main() 内，进入函数请用“下一步/上一步”", True)
            self.lineinfo.config(text=f"第 {line} 行")
            return
        self.current_line = line
        self.code.tag_remove("hl", "1.0", "end")
        self.code.tag_remove("er", "1.0", "end")
        self.code.tag_add("hl", f"{line}.0", f"{line}.end")
        self.code.see(f"{line}.0")
        code = self.get_code()
        if not code.strip():
            return
        try:
            sim = make_simulator(code)
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
        changed = self._changed_var_names(diff)
        self.drawer.draw(snap, f"执行到第 {line} 行（该行执行后）", diff_text, changed)
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
            # 标量堆块值变化（*p = x）
            if bb.get("scalar") != ab.get("scalar") and ab.get("scalar") is not None:
                changes.append(f"{ab['typename']}@0x{addr:x} 值={self.fmt_diff_val(ab['scalar'])}")
            # 释放
            if not bb.get("freed") and ab.get("freed"):
                changes.append(f"free: {ab['typename']}@0x{addr:x} 已释放")
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
            sim = make_simulator(code)
            sim.pending_inputs = list(self._pending_inputs)
            snaps = sim.run()
            err = sim.engine.error if sim.engine else None
            steps = list(sim.engine.step_snapshots) if sim.engine else []
            self.sim = sim
            return snaps, err, steps
        except SimError as ex:
            return {}, ex, []

    def _changed_var_names(self, diff):
        """从 diff 列表中提取本步发生变化的变量名（用于高亮）"""
        changed = set()
        for d in diff:
            if d.startswith("声明变量 "):
                changed.add(d[len("声明变量 "):].strip())
            elif "=" in d and "->" not in d and "@" not in d \
                    and "分配" not in d and "释放" not in d:
                nm = d.split("=", 1)[0].strip()
                if nm and all(c.isalnum() or c == "_" for c in nm):
                    changed.add(nm)
        return changed

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
        changed = self._changed_var_names(diff)
        if diff:
            diff_text = "本步修改内存：" + "；".join(diff[:8])
            if len(diff) > 8:
                diff_text += f" 等{len(diff)}处"
        else:
            diff_text = "本步未修改内存（声明 / 判断 / 函数调用等）"
        self.drawer.draw(snap, f"第 {idx + 1} / {len(self.step_list)} 步 · 第 {line} 行执行后",
                         diff_text, changed)
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
        # 到达输入步骤 → 触发输入窗（可模拟输入/用户输入，重新到该输入点=格式化重输）
        if self.step_list:
            line = self.step_list[self.step_idx][0]
            if self._is_input_line(line):
                self._open_input_window(line)

    def step_prev(self):
        if not self.step_list:
            self.set_status("请先点“下一步”或“运行全部”", False)
            return
        if self.step_idx <= 0:
            self.set_status("已在第一步", False)
            return
        self.step_idx -= 1
        self._show_step(self.step_idx)

    def step_back_to_caller(self):
        """从函数内部一步返回到调用处（如回到 main）：
        向前找第一个“调用栈变浅”的步（函数返回后的状态）并跳到那里"""
        if not self.step_list:
            self.set_status("请先点“下一步”或“运行全部”", False)
            return
        if self.step_idx < 0:
            self.step_idx = 0
        cur = self.step_list[self.step_idx][1]
        cur_depth = len(cur.get("frames", []))
        if cur_depth > 1:
            # 函数内部步在调用行快照之前，先向后找最近的最外层(main)步
            for i in range(self.step_idx + 1, len(self.step_list)):
                if len(self.step_list[i][1].get("frames", [])) == 1:
                    self.step_idx = i
                    self._show_step(i)
                    return
            # 再向前找最外层
            for i in range(self.step_idx - 1, -1, -1):
                if len(self.step_list[i][1].get("frames", [])) == 1:
                    self.step_idx = i
                    self._show_step(i)
                    return
        # 找不到最外层 → 回退到最近一次调用栈变浅的位置
        for i in range(self.step_idx - 1, -1, -1):
            d = len(self.step_list[i][1].get("frames", []))
            if d < cur_depth:
                self.step_idx = i
                self._show_step(i)
                return
        # 已在最外层（main 内）→ 普通回退一步
        if self.step_idx > 0:
            self.step_idx -= 1
            self._show_step(self.step_idx)
        else:
            self.set_status("已在最外层调用处", False)

    def quick_run(self):
        """快速运行：默认“模拟输入”（程序自动按函数意思生成输入），执行并写日志"""
        code = self.get_code()
        if not code.strip():
            return
        auto = auto_gen_inputs(code)
        if auto:
            self._pending_inputs = list(auto)
        self._input_requested = True      # 快速运行自带输入，不再弹旧输入窗
        snaps, err, steps = self._exec_code()
        outputs = []
        if self.sim is not None and self.sim.engine is not None:
            outputs = list(self.sim.engine.outputs)
        self._log_run("快速运行", auto, outputs, err, auto_inputs=auto)
        if err:
            self._set_run_status("❌ 程序未能正常跑通!!!", "red")
            self.set_status(f"快速运行（未跑通）：{err.msg}", True)
            self.highlight_error(err.line)
            self.draw_empty()
            return
        self.snapshots = snaps
        self.step_list = steps
        if not snaps:
            self._set_run_status("❌ 程序未能正常跑通!!!", "red")
            self.set_status("未发现可执行函数（需要 int main() 或函数定义）", True)
            return
        self.step_idx = len(steps) - 1 if steps else -1
        last = max(snaps.keys())
        self.current_line = last      # 记住最终状态行，重绘/点击面板时保持正确状态
        self.drawer.draw(snaps[last], "运行结束（最终状态）")
        self.code.tag_remove("hl", "1.0", "end")
        self.code.tag_add("hl", f"{last}.0", f"{last}.end")
        self.code.see(f"{last}.0")
        self._set_run_status("✅ 程序已跑通", "green")
        self.set_status(f"快速运行完成：自动模拟输入 {len(auto)} 个，共 {len(snaps)} 个状态；可逐步回放", False)

    def run_all(self):
        """运行全部（旧接口）：用当前 _pending_inputs 执行，不自动生成输入"""
        code = self.get_code()
        if not code.strip():
            return
        self._input_requested = True
        snaps, err, steps = self._exec_code()
        outputs = []
        if self.sim is not None and self.sim.engine is not None:
            outputs = list(self.sim.engine.outputs)
        self._log_run("运行全部", list(self._pending_inputs), outputs, err)
        if err:
            self._set_run_status("❌ 程序未能正常跑通!!!", "red")
            self.set_status(f"运行错误：{err.msg}", True)
            self.highlight_error(err.line)
            self.draw_empty()
            return
        self.snapshots = snaps
        self.step_list = steps
        if not snaps:
            self._set_run_status("❌ 程序未能正常跑通!!!", "red")
            self.set_status("未发现可执行函数（需要 int main() 或函数定义）", True)
            return
        self.step_idx = len(steps) - 1 if steps else -1
        last = max(snaps.keys())
        self.current_line = last      # 记住最终状态行，重绘/点击面板时保持正确状态
        self.drawer.draw(snaps[last], "运行结束（最终状态）")
        self.code.tag_remove("hl", "1.0", "end")
        self.code.tag_add("hl", f"{last}.0", f"{last}.end")
        self.code.see(f"{last}.0")
        self._set_run_status("✅ 程序已跑通", "green")
        self.set_status(f"运行完成，共 {len(snaps)} 个状态；可用“上一步/下一步”逐步回放（共 {len(steps)} 步）", False)

    # ---------- 运行模式：常规 / 全部 / 自由测试 ----------
    def _set_run_status(self, text, color="gray"):
        colors = {"green": "#2ecc71", "red": "#e74c3c",
                  "gray": "#bdc3c7", "blue": "#5dade2"}
        self.run_status.config(text=text, fg=colors.get(color, "#bdc3c7"))

    def _popup_mode_menu(self):
        try:
            self.mode_menu.tk_popup(self.mode_btn.winfo_rootx(),
                                    self.mode_btn.winfo_rooty() +
                                    self.mode_btn.winfo_height())
        finally:
            self.mode_menu.grab_release()

    def set_run_mode(self, mode):
        # 兼容旧模式名：运行全部→快速运行，自由测试→自由运行
        if mode == "运行全部":
            mode = "快速运行"
        elif mode == "自由测试":
            mode = "自由运行"
        self.run_mode = mode
        self.mode_btn.config(text=mode)
        self.run_current_mode()

    def run_current_mode(self):
        m = self.run_mode
        if m == "常规运行":
            self.normal_run()
        elif m in ("快速运行", "运行全部"):
            self.quick_run()
        elif m in ("自由运行", "自由测试"):
            self.free_test_start()

    # ---------- 运行日志（代码区左侧，终端样式） ----------
    def clear_log(self):
        """清空运行日志并重置执行计数"""
        try:
            self.logbox.config(state=tk.NORMAL)
            self.logbox.delete("1.0", "end")
            self.logbox.config(state=tk.DISABLED)
        except Exception:
            pass
        self._run_count = 0

    def log(self, text=""):
        try:
            self.logbox.config(state=tk.NORMAL)
            self.logbox.insert(tk.END, text + "\n")
            self.logbox.config(state=tk.DISABLED)
            self.logbox.see(tk.END)
        except Exception:
            pass

    def _log_run(self, mode, inputs, outputs, err, auto_inputs=None, auto_marks=None):
        self._run_count += 1
        self.log(f"═══ 第 {self._run_count} 次执行 ═══ [{mode}]")
        if outputs:
            self.log("程序输出:")
            for o in outputs:
                # 引擎已把 \n 解码为真实换行；每个 printf 一行，内嵌换行原样显示
                self.log("  " + o)
        if inputs:
            parts = []
            for i, v in enumerate(inputs):
                if auto_marks is not None:
                    tag = "模拟输入" if (i < len(auto_marks) and auto_marks[i]) else "用户输入"
                elif auto_inputs is not None:
                    tag = "模拟输入"
                else:
                    tag = "用户输入"
                parts.append(f"{v} ({tag})")
            self.log("输入: " + " | ".join(parts))
        if err:
            self.log(f"状态: ❌ {err.msg}")
        else:
            self.log("状态: ✅ 已跑通")
        self.log("─" * 28)

    def _line_in_main(self, line):
        """判断某行是否属于 main 函数体（常规运行点击限制用）"""
        try:
            if not self.sim:
                return True
            fd = self.sim.funcs.get("main")
            if fd is None:
                return True
            return line in _stmt_lines(fd.body)
        except Exception:
            return True

    def _is_input_line(self, line):
        """判断某行代码是否含输入语句（scanf/getchar/gets 等）"""
        try:
            txt = self.code.get(f"{line}.0", f"{line}.end")
        except Exception:
            return False
        return any(k in txt for k in ("scanf", "getchar", "gets", "getch",
                                      "fgetc", "getline", "fgets"))

    def normal_run(self):
        """常规运行：重新构建逐步序列并从头开始（一步一行），
        第一步定位到 main 函数起始行，不会跳到结尾。"""
        code = self.get_code()
        if not code.strip():
            return
        m = None
        first = None
        try:
            sim = make_simulator(code)
            m = sim.main_name()
            if m is None:
                self._set_run_status("❌ 未找到 main", "red")
                self.set_status("未找到可执行函数", True)
                return
            self.sim = sim
            fd = sim.funcs[m]
            # C++ 引擎 funcs 存 (rtype, ptr, params, body)；C 引擎存 FuncDef
            body = fd[3] if isinstance(fd, tuple) else fd.body
            first = body[0].line if body else None
        except Exception:
            pass
        # 重新构建逐步序列，从第一步开始（关键：不能被载入时的快速运行状态污染）
        self.step_list = []
        self.step_idx = -1
        self._input_requested = True
        if not self.build_step_list():
            return
        if not self.step_list:
            self.run_all()
            return
        # 定位到 main 起始行（显示起点状态，但不跳到结尾）
        if first is not None:
            self.show_line(first)
        self._set_run_status("● 常规运行", "gray")
        self.set_status(f"常规运行：已定位到 {m}() 起始行，可点“下一步”逐步执行", False)

    # ---------- 自由测试：交互式输入，到输入点暂停弹输入窗 ----------
    def free_test_start(self):
        """自由运行：从 main 开头开始，可随便点击，到需要输入处暂停并弹输入窗，可重复输入"""
        self._free_active = True
        self._pending_inputs = []
        self._input_slots = {}
        self._auto_slots = {}
        self._input_requested = True     # 自由运行自己处理输入，不再走旧弹窗
        self._free_resume()

    def _rebuild_pending_from_slots(self):
        """按输入槽重建输入队列（级联格式化后调用）"""
        vals = []
        for k in sorted(self._input_slots.keys()):
            vals.extend(self._input_slots[k])
        self._pending_inputs = vals

    def _free_resume(self):
        """恢复自由运行执行：重新从头执行，到下一个输入点暂停或执行结束"""
        code = self.get_code()
        if not code.strip():
            return
        try:
            sim = make_simulator(code)
        except Exception:
            self._set_run_status("❌ 程序未能正常跑通!!!", "red")
            return
        sim.pending_inputs = list(self._pending_inputs)
        try:
            snaps, need_line, err = sim.run_pause_at_input()
        except Exception:
            self._set_run_status("❌ 程序未能正常跑通!!!", "red")
            return
        self.sim = sim
        self.snapshots = snaps
        self.step_list = list(sim.engine.step_snapshots) if sim.engine else []
        self.step_idx = len(self.step_list) - 1 if self.step_list else -1
        if need_line is not None:
            # 输入级联格式化：重新进入某输入点 → 清空该输入点及之后的所有输入
            pass
            if need_line in self._input_slots:
                for k in list(self._input_slots.keys()):
                    if k >= need_line:
                        del self._input_slots[k]
                self._rebuild_pending_from_slots()
            self._show_free_pause(need_line, snaps)
            self._open_input_window(need_line)
            return
        # 执行结束：写日志
        self._free_active = False
        outputs = list(sim.engine.outputs) if sim.engine else []
        auto_marks = []
        for k in sorted(self._input_slots.keys()):
            for _ in self._input_slots[k]:
                auto_marks.append(bool(self._auto_slots.get(k)))
        self._log_run("自由运行", list(self._pending_inputs), outputs, err,
                      auto_marks=auto_marks)
        if err:
            self._set_run_status("❌ 程序未能正常跑通!!!", "red")
            self.set_status(f"自由运行结束（未跑通）：{err.msg}", True)
            if err.line:
                self.highlight_error(err.line)
            if snaps:
                last = max(snaps.keys())
                self.current_line = last
                self.drawer.draw(snaps[last], "自由运行（遇到问题）")
        else:
            self._set_run_status("✅ 程序已跑通", "green")
            if snaps:
                last = max(snaps.keys())
                self.current_line = last
                self.drawer.draw(snaps[last], "自由运行完成（最终状态）")
                self.code.tag_remove("hl", "1.0", "end")
                self.code.tag_add("hl", f"{last}.0", f"{last}.end")
                self.code.see(f"{last}.0")
            self.set_status("自由运行完成：程序已跑通", False)

    def _show_free_pause(self, line, snaps):
        """显示自由测试暂停在输入行时的状态（该行执行前/最近的快照）"""
        snap = None
        keys = sorted(snaps.keys())
        for k in keys:
            if k <= line:
                snap = snaps[k]
            else:
                break
        if snap is None and keys:
            snap = snaps[keys[0]]
        self.current_line = line
        self.code.tag_remove("hl", "1.0", "end")
        self.code.tag_remove("er", "1.0", "end")
        self.code.tag_add("hl", f"{line}.0", f"{line}.end")
        self.code.see(f"{line}.0")
        if snap:
            self.drawer.draw(snap, f"自由测试：第 {line} 行需要输入")
        self._set_run_status("⏸ 等待输入…", "blue")
        self.set_status(f"自由测试：第 {line} 行需要输入，请在输入窗中填写", False)

    def _open_input_window(self, line):
        """可拖动的模拟输入窗：上=输入框(可缩放)，下=模拟输入/载入输入结果/重新输入"""
        import random
        win = tk.Toplevel(self.root)
        win.title(f"模拟输入 - 第 {line} 行")
        win.geometry("440x240")
        win.transient(self.root)
        tk.Label(win, text=f"第 {line} 行需要输入（scanf/getchar 等）。"
                           "多个值用空格/逗号分隔，Ctrl+Enter 提交：",
                 font=("Microsoft YaHei", 9), fg="#333333", anchor="w",
                 padx=10).pack(fill=tk.X, pady=(10, 2))
        txt = tk.Text(win, font=("Consolas", 12), height=4,
                      bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
                      padx=8, pady=6, relief=tk.SUNKEN, bd=1)
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)
        txt.focus_set()
        btns = tk.Frame(win)
        btns.pack(fill=tk.X, padx=10, pady=(2, 10))

        def parse():
            vals = []
            for x in txt.get("1.0", "end-1c").replace(",", " ").split():
                try:
                    vals.append(int(x, 0))
                except Exception:
                    try:
                        vals.append(int(float(x)))
                    except Exception:
                        pass
            return vals

        def commit(vals, as_auto=False):
            """把输入写入当前输入点槽（级联格式化后），恢复执行"""
            self._input_slots[line] = vals
            if as_auto:
                self._auto_slots[line] = True
            self._rebuild_pending_from_slots()
            win.destroy()
            self._free_resume()

        def load_input():
            commit(parse(), as_auto=False)

        def auto_input():
            # 程序自动模拟输入：按函数意思生成
            vals = auto_gen_inputs(self.get_code())
            vals = vals[:1] if vals else [random.randint(1, 100)]
            commit(vals, as_auto=True)

        def reinput():
            txt.delete("1.0", "end")
            txt.focus_set()

        tk.Button(btns, text="模拟输入", command=auto_input,
                  bg="#2e7d32", fg="white", cursor="hand2",
                  activebackground="#1b5e20", activeforeground="white",
                  font=("Microsoft YaHei", 11, "bold"),
                  padx=16, pady=6, relief=tk.RAISED, bd=1).pack(side=tk.LEFT)
        tk.Button(btns, text="载入输入结果", command=load_input,
                  bg="#1a5276", fg="white", cursor="hand2",
                  activebackground="#154360", activeforeground="white",
                  font=("Microsoft YaHei", 11, "bold"),
                  padx=16, pady=6, relief=tk.RAISED, bd=1).pack(side=tk.LEFT, padx=(8, 0), expand=True)
        tk.Button(btns, text="重新输入", command=reinput,
                  bg="#8e44ad", fg="white", cursor="hand2",
                  activebackground="#6c3483", activeforeground="white",
                  font=("Microsoft YaHei", 11),
                  padx=16, pady=6, relief=tk.RAISED, bd=1).pack(side=tk.RIGHT, padx=(8, 0))
        txt.bind("<Control-Return>", lambda e: load_input())
        txt.bind("<Return>", lambda e: load_input())

    def reset(self):
        self.current_line = None
        self.code.tag_remove("hl", "1.0", "end")
        self.code.tag_remove("er", "1.0", "end")
        self.snapshots = {}
        self.step_list = []
        self.step_idx = -1
        self._input_requested = False
        self._pending_inputs = []
        self._input_slots = {}
        self._auto_slots = {}
        self._free_active = False
        self._set_run_status("● 就绪", "gray")
        # 关闭自由测试遗留的输入窗
        try:
            for w in self.root.winfo_children():
                if isinstance(w, tk.Toplevel) and w.title().startswith("模拟输入"):
                    w.destroy()
        except Exception:
            pass
        self.draw_empty()
        self.set_status("已重置。点击代码行 / “下一步”逐步运行 / “运行全部”查看最终状态", False)

    def draw_empty(self):
        self.drawer.selected_addr = None
        self.drawer.panels = []
        self.drawer.node_rects = {}
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

    # ---------- 右侧画布交互：滚轮(点哪滚哪) / 拖拽平移 / 缩放 / 点击看详情 ----------
    def _cv_yview(self, *a):
        self.canvas.yview(*a)
        self._keep_panel()

    def _cv_xview(self, *a):
        self.canvas.xview(*a)
        self._keep_panel()

    def _keep_panel(self):
        """滚动/拖动画布时，让所有信息面板跟随可视区并同步连线"""
        d = self.drawer
        for p in d.panels:
            if p.get("win_id"):
                try:
                    x0 = self.canvas.canvasx(0)
                    y0 = self.canvas.canvasy(0)
                    self.canvas.coords(p["win_id"], x0 + p["dx"], y0 + p["dy"])
                    d._draw_panel_link(p)
                except Exception:
                    pass

    def _cv_wheel(self, ev):
        """画布滚轮：Ctrl → 缩放；Shift → 水平滚；否则垂直滚"""
        if ev.state & 0x0004:
            factor = 1.12 if ev.delta > 0 else 1 / 1.12
            self._zoom_at(factor, ev.x, ev.y)
        elif ev.state & 0x0001:
            self.canvas.xview_scroll(int(-ev.delta / 120), "units")
            self._keep_panel()
        else:
            self.canvas.yview_scroll(int(-ev.delta / 120), "units")
            self._keep_panel()
        return "break"

    def _cv_wheel_lin(self, ev):
        """Linux 滚轮 Button-4/5：Ctrl 缩放，否则垂直滚"""
        if ev.state & 0x0004:
            factor = 1.12 if ev.num == 4 else 1 / 1.12
            self._zoom_at(factor, ev.x, ev.y)
        else:
            self.canvas.yview_scroll(-1 if ev.num == 4 else 1, "units")
            self._keep_panel()
        return "break"

    def _zoom_at(self, factor, mx, my):
        """以鼠标位置为中心缩放画布"""
        d = self.drawer
        old = d.zoom
        new = min(4.0, max(0.45, old * factor))
        if abs(new - old) < 1e-6:
            return
        cx = self.canvas.canvasx(mx)
        cy = self.canvas.canvasy(my)
        ratio = new / old
        d.zoom = new
        self.redraw()
        self.canvas.update_idletasks()
        bb = self.canvas.bbox("all")
        if bb:
            reg_w, reg_h = bb[2], bb[3]
            if reg_w > 0:
                self.canvas.xview_moveto(max(0.0, (cx * ratio - mx) / reg_w))
            if reg_h > 0:
                self.canvas.yview_moveto(max(0.0, (cy * ratio - my) / reg_h))
        self._keep_panel()
        try:
            self.set_status(f"缩放 {round(d.zoom * 100)}%  （双击画布恢复 100%）", False)
        except Exception:
            pass

    def _zoom_reset(self, ev=None):
        """双击画布：恢复 100% 缩放并回到左上角"""
        d = self.drawer
        if abs(d.zoom - 1.0) < 0.01:
            return
        d.zoom = 1.0
        self.redraw()
        self.canvas.update_idletasks()
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self._keep_panel()
        try:
            self.set_status("已恢复 100% 缩放", False)
        except Exception:
            pass

    def _cv_press(self, ev):
        self._canvas_mouse_down = True
        self._press_x, self._press_y = ev.x, ev.y
        self._dragging = False
        self.canvas.scan_mark(ev.x, ev.y)
        self.canvas.config(cursor="fleur")

    def _cv_drag(self, ev):
        """按住左键拖动画布平移（像查看图片）"""
        if abs(ev.x - self._press_x) > 4 or abs(ev.y - self._press_y) > 4:
            self._dragging = True
        if self._dragging:
            self.canvas.scan_dragto(ev.x, ev.y, gain=1)
            self._keep_panel()
        return "break"

    def _cv_release(self, ev):
        self._canvas_mouse_down = False
        self.canvas.config(cursor="hand2")
        if not self._dragging:
            self._cv_click(ev)
        self._dragging = False

    def _cv_click(self, ev):
        """单击：续接标记→紫箭头；指针绿框→绿色面板；内存块→红/蓝面板"""
        cx = self.canvas.canvasx(ev.x)
        cy = self.canvas.canvasy(ev.y)
        d = self.drawer
        # 1. 续接标记 → 显示/隐藏紫色垂直箭头
        for mid, info in list(d.wrap_marks.items()):
            x1, y1, x2, y2 = info["rect"]
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                d._toggle_wrap_arrow(mid)
                return "break"
        # 2. 指针绿框 → 绿色解释面板 + 绿色高亮线连到内存框图（再点一次关闭）
        for name, (x, y, w, h) in d.ptr_boxes.items():
            if x <= cx <= x + w and y <= cy <= y + h:
                if any(p["kind"] == "ptr" and p["name"] == name
                       for p in d.panels):
                    d._remove_ptr_panel(name)
                    d._toggle_ptr_link(name)
                else:
                    d._add_ptr_panel(name)
                    d._toggle_ptr_link(name)
                self.redraw()
                return "break"
        # 3. 内存块 → 红/蓝面板
        hit = None
        for addr, (x, y, w, h) in self.drawer.node_rects.items():
            if x <= cx <= x + w and y <= cy <= y + h:
                hit = addr
                break
        if hit is None:
            return
        d = self.drawer
        if any(p["addr"] == hit and p["kind"] == "blk" for p in d.panels):
            d._remove_panel(hit)      # 再点一次 → 关闭该介绍框
        else:
            d._add_panel(hit)         # 新增介绍框（最多 2 个）
        self.redraw()

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
        win.geometry("760x520")
        win.transient(self.root)
        txt = tk.Text(win, font=("Consolas", 11), wrap="none",
                      bg="#fbfbfb", padx=8, pady=8)
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        btns = tk.Frame(win, bg="#f0f0f0", highlightbackground="#dddddd",
                        highlightthickness=1)
        btns.pack(fill=tk.X, side=tk.BOTTOM)
        hint = tk.Label(btns, text="支持 .c / .cpp 片段 · 粘贴后点「载入并分析」",
                        bg="#f0f0f0", fg="#777777",
                        font=("Microsoft YaHei", 9))
        hint.pack(side=tk.LEFT, padx=12, pady=10)

        def ok():
            self.load_example_text(txt.get("1.0", "end-1c"))
            win.destroy()
            self.set_status("已粘贴代码", False)

        btn_ok = tk.Button(btns, text="✔ 载入并分析", command=ok,
                           bg="#1a5276", fg="white", activebackground="#154360",
                           activeforeground="white", cursor="hand2",
                           font=("Microsoft YaHei", 12, "bold"),
                           padx=28, pady=10, relief=tk.RAISED, bd=1)
        btn_ok.pack(side=tk.RIGHT, padx=(0, 12), pady=10)
        btn_cancel = tk.Button(btns, text="取消", command=win.destroy,
                               bg="#9e9e9e", fg="white", cursor="hand2",
                               activebackground="#757575",
                               activeforeground="white",
                               font=("Microsoft YaHei", 11),
                               padx=20, pady=10, relief=tk.RAISED, bd=1)
        btn_cancel.pack(side=tk.RIGHT, padx=8, pady=10)
        txt.focus_set()

    def load_example(self, event=None):
        name = self.example_var.get()
        if name in EXAMPLES:
            self.load_example_text(EXAMPLES[name])

    def load_example_text(self, text):
        # 载入新代码：日志从头开始（干净）
        self.clear_log()
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
        self.drawer.zoom = 1.0
        self.drawer.selected_addr = None
        self.drawer.panels = []
        self.drawer.node_rects = {}
        self.code.tag_remove("hl", "1.0", "end")
        self.code.tag_remove("er", "1.0", "end")
        self.highlight_syntax()
        self._upd_lines()
        # 载入后默认“快速运行”一次：自动模拟输入 + 写日志（进来就执行一次）
        # 但结束后恢复 _pending_inputs，不污染用户后续手动设置的输入
        self._input_requested = False
        self._pending_inputs = []
        self._input_slots = {}
        self._auto_slots = {}
        code_now = self.get_code()
        auto = auto_gen_inputs(code_now)
        if auto:
            self._pending_inputs = list(auto)
        self._input_requested = True
        snaps, err, steps = self._exec_code()
        outputs = list(self.sim.engine.outputs) if self.sim and self.sim.engine else []
        self._log_run("快速运行", auto, outputs, err, auto_inputs=auto)
        self._pending_inputs = []      # 恢复：用户可自行设置输入
        self._input_requested = False
        if err or not snaps:
            # C++ 文件识别：给出明确提示(不影响纯 C 的正常流程)
            if getattr(self, "sim", None) is not None and getattr(self.sim, "cpp_detected", False):
                hl, hln = (self.sim.cpp_hint or ("C++", 1))
                self.highlight_error(hln if isinstance(hln, int) else 1)
                self._set_run_status("📌 已识别为 C++ 文件", "red")
                self.set_status(f"已识别为 C++ 代码（第 {hln} 行含特征 '{str(hl).strip()}'）。"
                                "本工具当前主支持 C 语言子集，C++ 解析支持开发中；"
                                "纯 C 文件不受影响，可正常逐步运行。", True)
                self.log(f"已识别为 C++ 代码（特征 '{str(hl).strip()}'），不按 C 解析（避免误报）。")
                return
            self._set_run_status("❌ 程序未能正常跑通!!!" if err else "● 就绪",
                                 "red" if err else "gray")
            if not snaps:
                self._auto_first()
        else:
            self.snapshots = snaps
            self.step_list = steps
            self.step_idx = len(steps) - 1 if steps else -1
            last = max(snaps.keys())
            self.current_line = last
            self.drawer.draw(snaps[last], "运行结束（最终状态）")
            self._set_run_status("✅ 程序已跑通", "green")
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
            sim = make_simulator(code)
            if sim.main_name() is None:
                self.draw_empty()
                msg = "没有找到 int main() 或任何函数定义，无法执行。\n请粘贴包含函数定义的完整代码片段。"
                self.set_status("未找到可执行函数", True)
                if self._popup:
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
