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
    NODE_H0 = 30          # 标题行高
    FIELD_H = 22          # 每字段行高
    GAP = 36              # 节点间距

    def __init__(self, canvas):
        self.c = canvas
        self.zoom = 1.0
        self.node_rects = {}        # addr -> (x, y, w, h)（缩放后画布坐标）
        self.panels = []            # 信息面板（最多2个：第1红·右上，第2蓝·右下）
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
            self.draw_chains(chain_heads, heap_by_addr, hx0, htop, H)
        else:
            self.draw_heap_blocks(heap_by_addr, hx0, htop, H)
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
        """返回该块第一个指针字段的目标地址(0=无/NULL, 非0=地址)"""
        for fn, fv in blk["fields"].items():
            if fv[0] == "ptr":
                return fv[1]
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
            while cur in heap_by_addr and cur not in visited and steps < 200:
                visited.add(cur)
                if cur in global_visited:
                    # 链在此接入已画节点：断链标注
                    self.c.create_text(x + 2, y - 16 * z, anchor="nw",
                                       text="↑ 接上方已画块", fill="#666666",
                                       font=self.FM(9, True))
                    break
                blk = heap_by_addr[cur]
                # 超出行宽 -> 换行，画向下续接标记（与下一行错开，不遮挡节点）
                if prev is not None and x > x0 + max_w:
                    _paddr, prx, pby = prev
                    self.c.create_line(prx - 4, pby + 2, prx - 4, pby + 20 * z,
                                       fill="#1565c0", width=2, arrow=tk.LAST)
                    self.c.create_text(x0 + 2, pby + max(20, round(22 * z)), anchor="nw",
                                       text="↘ 续接", fill="#1565c0",
                                       font=self.FM(9, True))
                    y = pby + max(30, round(40 * z))
                    x = x0
                    self.last_audit["wraps"] += 1
                rx, by = self.draw_node(x, y, cur, blk, heap_by_addr)
                pos[cur] = (x, y, rx, by)
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
                    prev = (cur, rx, by)
                    cur = tgt
                    x = rx + self.gap
                    steps += 1
                else:
                    # next 为 NULL 或野指针 → 画带箭头的指向标记（与 next 字段行对齐）
                    self._draw_next_target(rx, y, self._next_field_idx(blk), tgt, z)
                    break
            # 画箭头：同一视觉行内连线（跨行由 ↘ 标记连接），高度对准 next 字段行
            for a, (bx, by, rx, _bh) in pos.items():
                blk = heap_by_addr[a]
                tgt = self._next_target(blk)
                if tgt in pos:
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

    def _next_field_idx(self, blk):
        """返回第一个指针(next)字段的序号，用于箭头与该行对齐"""
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

    def draw_heap_blocks(self, heap_by_addr, x0, y0, H):
        z = self.zoom
        x = x0
        y = y0
        vis_w = int(self.c.cget("width")) / z
        for addr in sorted(heap_by_addr.keys()):
            blk = heap_by_addr[addr]
            rx, by = self.draw_node(x, y, addr, blk, heap_by_addr)
            x = rx + self.gap
            if x > x0 + vis_w - 60:
                x = x0
                y = by + max(30, round(40 * z))

    def arrow(self, x1, y1, x2, y2, color="#1565c0"):
        az = max(0.6, self.zoom)
        self.c.create_line(x1, y1, x2, y2, fill=color,
                           width=max(1.5, 2 * self.zoom),
                           arrow=tk.LAST,
                           arrowshape=(max(6, round(12 * az)),
                                       max(8, round(15 * az)),
                                       max(3, round(7 * az))))

    # ---------- 信息面板（点击内存块显示详情）：最多 2 个，可拖动/关闭，节点描边+连线 ----------
    # 第 1 个：右上角·红色连线；第 2 个：右下角·蓝色连线
    def _add_panel(self, addr):
        if any(p["addr"] == addr for p in self.panels):
            return
        if len(self.panels) >= 2:                     # 超过 2 个：移除最旧的
            old = self.panels.pop(0)
            self._remove_panel(old["addr"])
        is_first = len(self.panels) == 0
        color = "#e53935" if is_first else "#1e88e5"
        cw = max(240, self.c.winfo_width())
        ch = max(240, self.c.winfo_height())
        dx = cw - 20
        dy = 20 if is_first else ch - 20
        self.panels.append({"addr": addr, "color": color, "dx": dx, "dy": dy,
                            "anchor": "ne" if is_first else "se",
                            "win_id": None, "line_id": None, "frame": None})

    def _remove_panel(self, addr):
        for p in self.panels:
            if p["addr"] == addr:
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
        # 移除后重新分配：始终第1个=红·右上，第2个=蓝·右下
        cw = max(240, self.c.winfo_width())
        ch = max(240, self.c.winfo_height())
        for i, p in enumerate(self.panels):
            p["color"] = "#e53935" if i == 0 else "#1e88e5"
            p["dx"] = cw - 20
            p["dy"] = 20 if i == 0 else ch - 20
            p["anchor"] = "ne" if i == 0 else "se"

    def _draw_info_panels(self):
        for p in list(self.panels):
            self._draw_panel(p)

    def _draw_panel(self, p):
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

    def _draw_panel_link(self, p):
        """节点中心 → 面板 的细虚线连接线（不显眼）"""
        if p.get("line_id"):
            try:
                self.c.delete(p["line_id"])
            except Exception:
                pass
            p["line_id"] = None
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
        btn("▶ 运行全部", self.run_all).pack(side=tk.LEFT, padx=4, pady=4)
        btn("↺ 重置", self.reset).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Label(bar, text="示例:", bg="#2c3e50", fg="white",
                 font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=(16, 2))
        self.example_var = tk.StringVar()
        ex = ttk.Combobox(bar, textvariable=self.example_var, state="readonly",
                          width=18, values=list(EXAMPLES.keys()))
        ex.pack(side=tk.LEFT, padx=2)
        ex.bind("<<ComboboxSelected>>", self.load_example)
        tk.Label(bar, text="提示：点击代码行查看该行状态 · ←/→ 上一步下一步 · 拖动平移 · Ctrl+滚轮缩放",
                 bg="#2c3e50", fg="#ecf0f1",
                 font=("Microsoft YaHei", 9)).pack(side=tk.RIGHT, padx=10)
        # 键盘快捷键：←/→ 逐步回放
        root.bind("<Left>", lambda e: self.step_prev())
        root.bind("<Right>", lambda e: self.step_next())

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
            sim = Simulator(code)
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
        """单击内存块：已选中→关闭；未选中→添加面板（第1红右上/第2蓝右下）"""
        cx = self.canvas.canvasx(ev.x)
        cy = self.canvas.canvasy(ev.y)
        hit = None
        for addr, (x, y, w, h) in self.drawer.node_rects.items():
            if x <= cx <= x + w and y <= cy <= y + h:
                hit = addr
                break
        if hit is None:
            return
        d = self.drawer
        if any(p["addr"] == hit for p in d.panels):
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
        self.drawer.zoom = 1.0
        self.drawer.selected_addr = None
        self.drawer.panels = []
        self.drawer.node_rects = {}
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
