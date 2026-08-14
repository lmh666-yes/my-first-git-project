# -*- coding: utf-8 -*-
"""验证: 01单向带头不循环.c 链表构建与移动节点正确性"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simcore import Simulator

p = r"d:\yq\01虚拟机\03数据结构\02单向链表\code\01单向带头不循环.c"
code = open(p, encoding="utf-8", errors="replace").read()
s = Simulator(code)

# 停在 main 最后一次 single_print 之后、destory 之前（行号需找）
# 找 main 中 "single_print(head);" 的最后一次调用行
main_body = s.funcs["main"].body
print_target = None
for st in main_body:
    if st.line > 150:
        print_target = st.line
# main_body 顶层语句; 直接停到 main 最后一个语句前
lines = [st.line for st in main_body]
print("main 顶层行:", lines)
# 停到倒数第 2 个语句(销毁前)所在行
destory_line = None
for st in main_body:
    txt = ""
    try:
        from simcore import ExprStmt
    except Exception:
        pass
    # 顶层语句大多是 expr(call), 找到 destory 调用
    if getattr(st, "kind", "") == "expr" and st.expr[0] == "call":
        callee = st.expr[1]
        if isinstance(callee, tuple) and callee[0] == "var" and callee[1] == "single_list_destory":
            destory_line = st.line
print("destory 行:", destory_line)

# 停到 main 最后一次 single_print 之后、destory 之前
# main 顶层行: 269..274 是移动+打印, 278 是 destory
target = 274   # 最后一次 single_print(head) 之后
s.run_to_line(target)
snaps = s.snapshots
last = max(snaps.keys())
snap = snaps[last]
hb = {b["addr"]: b for b in snap["heap"]}

def chain(addr):
    """沿 next 字段遍历链表, 返回 data 序列"""
    out = []
    seen = set()
    while addr in hb and addr not in seen and len(out) < 30:
        seen.add(addr)
        blk = hb[addr]
        d = blk["fields"].get("data")
        out.append(d[1] if d and d[0] == "int" else "?")
        n = blk["fields"].get("next")
        if n and n[0] == "ptr":
            addr = n[1]
        else:
            break
    return out

# 头节点 head = 0x1000
seq = chain(0x1000)
print("链表序列(带头):", seq)

# 期望(带头): 初始 1..10; 移动 8->3: 1,2,8,3,4,5,6,7,9,10
# 移动 7->1: 7,1,2,8,3,4,5,6,9,10; 移动 2->10: 7,1,8,3,4,5,6,9,2,10
expected = [0, 7, 1, 8, 3, 4, 5, 6, 9, 2, 10]
print("期望:", expected)
print("[%s] 链表移动节点结果正确" % ("PASS" if seq == expected else "FAIL"))
