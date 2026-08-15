# -*- coding: utf-8 -*-
"""检查 06.c: malloc/*p赋值/free 的执行与指向"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simcore import Simulator

p = r"d:\yq\CQ2615\c-06-复习\06.c"
code = open(p, encoding="utf-8", errors="replace").read()
print("=== 06.c 源码 ===")
print(code)

print("=== 逐步执行 ===")
sim = Simulator(code)
snaps = sim.run()
err = sim.engine.error if sim.engine else None
steps = list(sim.engine.step_snapshots) if sim.engine else []
print("运行错误:", err.msg if err else "无")
print("快照数:", len(snaps), " 步数:", len(steps))

for i, (ln, snap) in enumerate(steps):
    frames = snap.get("frames", [])
    heap = snap.get("heap", [])
    vars_str = "; ".join(f"{n}={v['value']}" for fr in frames for n, v in fr["vars"])
    heap_str = "; ".join(
        f"{hex(b['addr'])}:{b['typename']}[{b.get('loc')}]"
        + (f"scalar={b['scalar']}" if b.get('scalar') is not None else "")
        + (f" freed={b['freed']}" if b.get('freed') else "")
        + (f" fields={{{ {k:v for k,v in b['fields'].items()} }}}" if b["fields"] else "")
        for b in heap)
    print(f"  步{i+1} 行{ln}: vars=[{vars_str}]  heap=[{heap_str}]")

# 最后状态: free(p) 后 p 应指向已释放地址(悬垂指针)
last = snaps[max(snaps)]
for fr in last.get("frames", []):
    for n, v in fr["vars"]:
        val = v.get("value")
        if val and val[0] == "ptr":
            addr = val[1]
            in_heap = addr in {b["addr"] for b in last.get("heap", [])}
            freed = any(b["addr"] == addr and b.get("freed") for b in last.get("heap", []))
            print(f"  最后: {n} -> 0x{addr:x} 在堆中={in_heap} 已释放={freed} "
                  f"({'悬垂指针(已释放)' if freed else ('正常' if in_heap else '野指针!')})")
print("=== 检查完成 ===")
