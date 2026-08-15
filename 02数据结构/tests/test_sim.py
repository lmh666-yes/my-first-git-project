# -*- coding: utf-8 -*-
"""test_sim.py — 验证 simcore 模拟引擎的准确性"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simcore import Simulator, SimError

fails = 0

def check(cond, msg):
    global fails
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        fails += 1

def run_code(code, stop_line=None):
    sim = Simulator(code)
    if stop_line is not None:
        snaps = sim.run_to_line(stop_line)
    else:
        snaps = sim.run()
    if sim.engine and sim.engine.error:
        raise sim.engine.error
    return sim, snaps

# ---------- 1. 链表头插 ----------
LINK_INSERT = r"""
#include <stdio.h>
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
    return 0;
}
"""

print("== 测试1: 链表头插 ==")
sim, snaps = run_code(LINK_INSERT)
# 找 head 声明行之后的快照
lines = [ln for ln in snaps if ln > 0]
last = max(lines)
snap = snaps[last]
# 检查堆上有 2 个块，head 指向 val=2 的块
heap = snap["heap"]
check(len(heap) == 2, f"堆上有 2 个节点(实际 {len(heap)})")
head_var = None
for fr in snap["frames"]:
    for n, v in fr["vars"]:
        if n == "head":
            head_var = v
check(head_var is not None, "存在 head 变量")
if head_var:
    hv = head_var["value"]
    check(hv[0] == "ptr", f"head 是指针(实际 {hv})")
    if hv[0] == "ptr":
        addr = hv[1]
        blk = next((b for b in heap if b["addr"] == addr), None)
        check(blk is not None and blk["fields"]["val"][1] == 2,
              f"head 指向 val=2 的节点(实际 {blk['fields']['val'] if blk else '无'})")
        if blk:
            nxt = blk["fields"]["next"]
            check(nxt[0] == "ptr", f"head 的 next 是指针")
            if nxt[0] == "ptr":
                blk2 = next((b for b in heap if b["addr"] == nxt[1]), None)
                check(blk2 is not None and blk2["fields"]["val"][1] == 1,
                      f"第二个节点 val=1(实际 {blk2['fields']['val'] if blk2 else '无'})")
                if blk2:
                    check(blk2["fields"]["next"][0] == "null", "第二个节点 next=NULL")

# ---------- 2. 链表遍历求和 ----------
LINK_SUM = r"""
typedef struct Node { int val; struct Node *next; } Node;
int main() {
    Node *a = malloc(sizeof(Node));
    a->val = 10; a->next = NULL;
    Node *b = malloc(sizeof(Node));
    b->val = 20; b->next = NULL;
    a->next = b;
    int sum = 0;
    Node *p = a;
    while (p) {
        sum = sum + p->val;
        p = p->next;
    }
    return 0;
}
"""
print("== 测试2: 链表遍历求和 ==")
sim, snaps = run_code(LINK_SUM)
last = max(snaps)
snap = snaps[last]
# 最终 sum=30, p=NULL
sumv = None
for fr in snap["frames"]:
    for n, v in fr["vars"]:
        if n == "sum":
            sumv = v
check(sumv is not None and sumv["value"] == ("int", 30), f"sum=30(实际 {sumv})")

# ---------- 3. 链表反转 ----------
LINK_REVERSE = r"""
typedef struct Node { int val; struct Node *next; } Node;
int main() {
    Node *head = NULL;
    Node *a = malloc(sizeof(Node)); a->val = 1; a->next = NULL;
    Node *b = malloc(sizeof(Node)); b->val = 2; b->next = NULL;
    Node *c = malloc(sizeof(Node)); c->val = 3; c->next = NULL;
    head = a; a->next = b; b->next = c;
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
"""
print("== 测试3: 链表反转 ==")
sim, snaps = run_code(LINK_REVERSE)
last = max(snaps)
snap = snaps[last]
heap = snap["heap"]
headv = None
for fr in snap["frames"]:
    for n, v in fr["vars"]:
        if n == "head":
            headv = v
# head 应指向 val=3
vals = []
addr = headv["value"][1] if headv and headv["value"][0] == "ptr" else None
seen = set()
while addr and addr not in seen:
    seen.add(addr)
    blk = next((b for b in heap if b["addr"] == addr), None)
    if not blk:
        break
    vals.append(blk["fields"]["val"][1])
    nx = blk["fields"]["next"]
    addr = nx[1] if nx[0] == "ptr" else None
check(vals == [3, 2, 1], f"反转后顺序 3,2,1(实际 {vals})")

# ---------- 4. 递归：链表求和（递归调用栈） ----------
LINK_REC = r"""
typedef struct Node { int val; struct Node *next; } Node;
int sum_list(Node *head) {
    if (!head) return 0;
    return head->val + sum_list(head->next);
}
int main() {
    Node *a = malloc(sizeof(Node)); a->val = 5; a->next = NULL;
    Node *b = malloc(sizeof(Node)); b->val = 7; b->next = NULL;
    a->next = b;
    int total = sum_list(a);
    return 0;
}
"""
print("== 测试4: 递归求和 ==")
sim, snaps = run_code(LINK_REC)
last = max(snaps)
snap = snaps[last]
total = None
for fr in snap["frames"]:
    for n, v in fr["vars"]:
        if n == "total":
            total = v
check(total is not None and total["value"] == ("int", 12), f"total=12(实际 {total})")

# ---------- 5. NULL 解引用应报错 ----------
NULL_ERR = r"""
typedef struct Node { int val; struct Node *next; } Node;
int main() {
    Node *p = NULL;
    p->val = 1;
    return 0;
}
"""
print("== 测试5: NULL 解引用报错 ==")
try:
    run_code(NULL_ERR)
    check(False, "应当报 NULL 解引用错误")
except SimError as ex:
    check("NULL" in ex.msg, f"报错信息含 NULL({ex.msg})")

# ---------- 6. 数组 ----------
ARR = r"""
int main() {
    int arr[4];
    arr[0] = 10;
    arr[1] = 20;
    arr[2] = arr[0] + arr[1];
    return 0;
}
"""
print("== 测试6: 数组 ==")
sim, snaps = run_code(ARR)
last = max(snaps)
snap = snaps[last]
arrv = None
for fr in snap["frames"]:
    for n, v in fr["vars"]:
        if n == "arr":
            arrv = v
check(arrv is not None and arrv["arr"] == [("int", 10), ("int", 20), ("int", 30), ("int", 0)],
      f"arr=[10,20,30,0](实际 {arrv['arr'] if arrv else '无'})")

# ---------- 7. for 循环 ----------
FORL = r"""
int main() {
    int sum = 0;
    int i;
    for (i = 0; i < 5; i = i + 1) {
        sum = sum + i;
    }
    return 0;
}
"""
print("== 测试7: for 循环 ==")
sim, snaps = run_code(FORL)
last = max(snaps)
snap = snaps[last]
sumv = None
for fr in snap["frames"]:
    for n, v in fr["vars"]:
        if n == "sum":
            sumv = v
check(sumv is not None and sumv["value"] == ("int", 10), f"sum=10(实际 {sumv})")

# ---------- 8. 点击任意行 -> 对应快照 ----------
print("== 测试8: 逐行快照（点击行功能核心） ==")
sim, snaps = run_code(LINK_INSERT)
lines = sorted(snaps.keys())
check(len(lines) >= 8, f"记录了 {len(lines)} 行快照")
# 检查执行到"n1->val = 1"之后，堆上已有 n1 且 val=1
for ln in lines:
    snap = snaps[ln]
    blks = snap["heap"]
    if len(blks) == 1:
        b = blks[0]
        if b["fields"]["val"] == ("int", 1):
            check(True, f"第 {ln} 行后快照: 1 个节点 val=1 ✓")
            break
else:
    check(False, "未找到单节点 val=1 的快照")

print()
print("===== 结果: %s =====" % ("全部通过" if fails == 0 else f"有 {fails} 个失败"))
sys.exit(fails)
