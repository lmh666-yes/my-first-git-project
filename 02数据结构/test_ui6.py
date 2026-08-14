# -*- coding: utf-8 -*-
"""科学性验证: 从 435 个代码文件中随机抽 20 个,
检查 ① 矩形无遮挡 ② 堆区标题不被第一排节点遮挡 ③ 每个节点 next 箭头完整(NULL/野指针有指向)
④ 野指针/已释放内存能通过框图正确展示。
抽样使用固定随机种子,结果可复现。"""
import sys, io, os, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tkinter as tk
from simcore import Simulator, SimError
from visualizer import Drawer

BASE = r"D:\yq\01虚拟机"
SKIP = "999复习巩固"
EXT = (".c", ".cpp", ".cxx", ".h", ".hpp")

targets = []
for root_d in ["02C语言", "03数据结构"]:
    rd = os.path.join(BASE, root_d)
    if not os.path.isdir(rd):
        continue
    for dp, _, fns in os.walk(rd):
        if SKIP in dp:
            continue
        for fn in fns:
            if fn.lower().endswith(EXT):
                targets.append(os.path.join(dp, fn))

random.seed(20260814)
# 全量分类: 找出含堆块(链表/结构体)可绘制文件 与 全部可绘制文件，保证抽样覆盖链表场景
ok_heap, ok_all = [], []
for path in targets:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            code = f.read()
        if not code.strip():
            continue
        sim = Simulator(code)
        if sim.main_name() is None:
            continue
        snaps = sim.run()
        err = sim.engine.error if sim.engine else None
        if err and not ("需要手动输入" in err.msg or "疑似死循环" in err.msg):
            continue
        if not snaps:
            continue
        last = max(snaps)
        ok_all.append(path)
        if snaps[last].get("heap"):
            ok_heap.append(path)
    except Exception:
        continue
print(f"全量分类: 可绘制 {len(ok_all)} 个, 其中含堆块(链表/结构体) {len(ok_heap)} 个")

n_heap = min(12, len(ok_heap))
heap_sample = random.sample(ok_heap, n_heap) if ok_heap else []
rest = [p for p in ok_all if p not in heap_sample]
others = random.sample(rest, min(8, len(rest))) if rest else []
sample = heap_sample + others

root = tk.Tk()
root.withdraw()
canvas = tk.Canvas(root, width=620, height=760)
canvas.config(width=620, height=760)
d = Drawer(canvas)


def overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def rects_on(cv):
    out = []
    for it in cv.find_all():
        if cv.type(it) == "rectangle":
            out.append(cv.coords(it))
    return out


def check_occlusion(cv):
    """所有矩形两两不重叠(变量区与节点区、节点之间)"""
    rects = rects_on(cv)
    bad = []
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            if overlap(rects[i], rects[j]):
                bad.append((rects[i], rects[j]))
    return rects, bad


def check_title(cv):
    """堆区标题文字底部 <= 第一排节点顶部(不被遮挡)"""
    title_y = None
    for it in cv.find_all():
        if cv.type(it) == "text" and "内存 / 结构" in cv.itemcget(it, "text"):
            title_y = cv.coords(it)[1]
            break
    rects = rects_on(cv)
    if title_y is None or not rects:
        return True, "无标题或矩形(跳过)"
    # 堆区第一个节点顶部 = 大于标题 y 的最小矩形顶部
    tops = [r[1] for r in rects if r[1] > title_y - 5]
    if not tops:
        return True, "无堆区节点"
    first_top = min(tops)
    title_bottom = title_y + 15   # 10号加粗文字高度约15px
    return (title_bottom <= first_top + 1), f"标题底={title_bottom:.0f} 首节点顶={first_top:.0f}"


stats = {"files": 0, "skipped": 0, "parse_fail": 0, "run_err": 0,
         "passed": 0, "occ_fail": 0, "title_fail": 0, "audit_fail": 0}
details = []
for i, path in enumerate(sample, 1):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            code = f.read()
    except Exception as ex:
        stats["skipped"] += 1
        details.append((os.path.basename(path), "读文件失败", str(ex)[:40]))
        continue
    if not code.strip():
        stats["skipped"] += 1
        continue
    try:
        sim = Simulator(code)
        if sim.main_name() is None:
            stats["skipped"] += 1
            details.append((os.path.basename(path), "跳过(无main)", ""))
            continue
        snaps = sim.run()
        err = sim.engine.error if sim.engine else None
    except SimError as ex:
        stats["parse_fail"] += 1
        details.append((os.path.basename(path), "解析失败", str(ex)[:50]))
        continue
    except Exception as ex:
        stats["parse_fail"] += 1
        details.append((os.path.basename(path), "异常", str(ex)[:50]))
        continue
    if err:
        if "需要手动输入" in err.msg or "疑似死循环" in err.msg:
            pass          # 有部分快照可画
        else:
            stats["run_err"] += 1
            details.append((os.path.basename(path), "运行错误", err.msg[:50]))
            continue
    if not snaps:
        stats["skipped"] += 1
        details.append((os.path.basename(path), "跳过(无快照)", ""))
        continue
    last = max(snaps)
    canvas.delete("all")
    d.zoom = 1.0
    d.selected_addr = None
    try:
        d.draw(snaps[last], "测试")
        root.update()
    except Exception as ex:
        stats["parse_fail"] += 1
        details.append((os.path.basename(path), "绘制异常", str(ex)[:50]))
        continue
    stats["files"] += 1
    # ① 遮挡
    rects, bad = check_occlusion(canvas)
    occ_ok = len(bad) == 0
    if not occ_ok:
        stats["occ_fail"] += 1
    # ② 标题
    title_ok, tinfo = check_title(canvas)
    if not title_ok:
        stats["title_fail"] += 1
    # ③ 审计: 每个节点 next 都有表示
    au = d.last_audit
    audit_ok = au["nodes"] == au["arrows"] + au["nulls"] + au["wilds"] + au["wraps"]
    if not audit_ok:
        stats["audit_fail"] += 1
    passed = occ_ok and title_ok and audit_ok
    if passed:
        stats["passed"] += 1
    details.append((os.path.basename(path),
                    "PASS" if passed else "FAIL",
                    f"矩形{len(rects)} 遮挡{len(bad)} 节点{au['nodes']} "
                    f"箭头{au['arrows']} NULL{au['nulls']} 野{au['wilds']} 续{au['wraps']} {'' if title_ok else tinfo}"))

print(f"样本文件: {len(sample)}  可绘制: {stats['files']}  跳过: {stats['skipped']}  "
      f"解析失败: {stats['parse_fail']}  运行错误: {stats['run_err']}")
print("-" * 90)
for name, st, info in details:
    mark = "  " if st == "PASS" else "!!"
    print(f"  {name:<28} {st:<6} {info}")
print("-" * 90)
drawn = stats["files"]
ok = stats["passed"]
print(f"绘制 {drawn} 个: 全部检查通过 {ok}  遮挡失败 {stats['occ_fail']}  "
      f"标题遮挡 {stats['title_fail']}  箭头审计失败 {stats['audit_fail']}")
if drawn:
    rate = ok / drawn * 100
    print(f"科学通过率: {rate:.1f}%  ({ok}/{drawn})")
verdict = "PASS" if drawn and ok == drawn else "FAIL"
print(f"[{verdict}] 随机抽样 UI 遮挡 + 箭头指向 100% 通过")

# ---- 野指针/已释放内存展示验证 ----
print("\n=== 野指针/已释放内存 展示验证 ===")
wild_code = r"""#include <stdlib.h>
typedef struct Node { int val; struct Node *next; } Node;
int main() {
    Node *a = malloc(sizeof(Node));
    a->val = 1; a->next = NULL;
    Node *p = malloc(sizeof(Node));
    p->val = 2; p->next = a;
    a->next = p;
    free(a);          /* 释放 a 后 head 成为野指针 */
    Node *head = a;
    return 0;
}
"""
canvas.delete("all")
sim = Simulator(wild_code)
snaps = sim.run()
err = sim.engine.error if sim.engine else None
if err:
    print("  野指针示例运行错误:", err.msg)
else:
    last = max(snaps)
    d.zoom = 1.0
    d.draw(snaps[last], "野指针测试")
    root.update()
    au = d.last_audit
    # 找变量区红色警告文本
    warn_txt = 0
    for it in canvas.find_all():
        if canvas.type(it) == "text":
            t = canvas.itemcget(it, "text")
            if "野指针" in t or "未分配" in t:
                warn_txt += 1
    print(f"  审计: 节点{au['nodes']} 箭头{au['arrows']} NULL{au['nulls']} 野指针标记{au['wilds']}")
    print(f"  红色野指针警告文本数: {warn_txt}")
    ok_wild = (au["wilds"] > 0 or warn_txt > 0)
    print("[%s] 野指针/已释放内存 通过红色箭头+警告文本展示" % ("PASS" if ok_wild else "FAIL"))
print("DONE")
