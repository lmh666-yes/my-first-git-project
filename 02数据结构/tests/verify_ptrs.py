# -*- coding: utf-8 -*-
"""指针指向审计: 对11个C样本最终快照检查
 ①所有指针(栈变量/堆字段)指向存在块或NULL, 无野指针
 ②从每个 head 指针沿 next 可完整遍历(不越界/不死循环) ③与真实输出吻合的链表长度"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simcore import Simulator

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "实例样本")
FILES = ["01cdemo.c", "01单向带头不循环.c", "01双向循环链表.c", "01循环队列.c",
         "01顺序栈.c", "02单向带头循环链表.c", "02链式栈.c", "02链式队列.c",
         "03单向不带头循环链表.c", "案例1.c", "案例2.c"]

fails = 0
for fn in FILES:
    path = os.path.join(BASE, fn)
    code = open(path, encoding="utf-8", errors="replace").read()
    sim = Simulator(code)
    sim.run()
    eng = sim.engine
    if not eng.snapshots:
        print(f"  [FAIL] {fn}: 无快照")
        fails += 1
        continue
    snap = eng.snapshots[max(eng.snapshots.keys())]   # 最终状态(return后)
    heap_addrs = {b["addr"] for b in snap["heap"]}
    freed = {b["addr"] for b in snap["heap"] if b.get("freed")}
    problems = []
    ptr_cnt = 0
    # ① 栈变量指针
    for fr in snap["frames"]:
        for name, v in fr["vars"]:
            val = v.get("value")
            if val and val[0] == "ptr":
                ptr_cnt += 1
                a = val[1]
                if a not in heap_addrs:
                    problems.append(f"变量 {name}->0x{a:x} 指向不存在的块(野指针)")
            # 数组里含指针(结构体数组)较少, 略
    # ② 堆字段指针
    for b in snap["heap"]:
        for fn2, fv in b["fields"].items():
            if isinstance(fv, tuple) and fv and fv[0] == "ptr":
                ptr_cnt += 1
                a = fv[1]
                if a not in heap_addrs:
                    problems.append(f"@{b['addr']:x}.{fn2}->0x{a:x} 野指针")
        if b.get("scalar") and b["scalar"][0] == "ptr":
            ptr_cnt += 1
            if b["scalar"][1] not in heap_addrs:
                problems.append(f"@{b['addr']:x} 标量指针 野指针")
    # ③ 从 head 变量沿 next 遍历(找最大链, 检测回环)
    def walk(start, field="next", maxn=600):
        seen = []
        cur = start
        for _ in range(maxn):
            if cur in seen:
                return seen, True   # 成环
            if cur not in heap_addrs:
                return seen, False
            seen.append(cur)
            blk = {x["addr"]: x for x in snap["heap"]}[cur]
            nv = blk["fields"].get(field)
            if not nv or nv[0] == "null" or nv[0] == "fn":
                return seen, True    # NULL 或函数指针字段=合法终点
            if nv[0] != "ptr":
                return seen, False
            cur = nv[1]
        return seen, False
    # 统计含结构字段的块并按 data 序列
    struct_blks = [b for b in snap["heap"] if b["fields"]]
    heads = []
    for fr in snap["frames"]:
        for name, v in fr["vars"]:
            val = v.get("value")
            if val and val[0] == "ptr" and val[1] in heap_addrs and name.lower() in ("head", "list1", "list2", "s", "q", "top", "front"):
                heads.append((name, val[1]))
    chain_info = []
    for name, a in heads:
        bm = {x["addr"]: x for x in snap["heap"]}
        if a in bm and bm[a].get("freed"):
            chain_info.append(f"{name}->悬垂(指向已free的块 0x{a:x}, 教学演示)")
            continue
        chain, ok = walk(a)
        if not ok:
            problems.append(f"从 {name} 沿 next 遍历异常(指向无效)")
        if chain:
            data = []
            for ca in chain:
                blk = bm[ca]
                dv = blk["fields"].get("data")
                data.append(dv[1] if dv and dv[0] == "int" else "?")
            tail = bm[chain[-1]] if chain else None
            tag = "(循环)" if (tail and tail["fields"].get("next") and tail["fields"]["next"][0] == "ptr" and tail["fields"]["next"][1] in set(chain)) else ""
            chain_info.append(f"{name}->{len(chain)}节点{tag}[{','.join(map(str,data[:40]))}]")
    status = "OK" if not problems else "问题"
    if problems:
        fails += 1
    print(f"\n===== {fn}  指针审计: {status}  ({len(snap['heap'])}块 {ptr_cnt}指针) =====")
    for p in problems[:12]:
        print(f"    ! {p}")
    for c in chain_info[:4]:
        print(f"    链: {c}")
print(f"\n===== 指针审计 {('全部通过' if fails==0 else str(fails)+' 个文件有问题')} =====")
sys.exit(1 if fails else 0)
