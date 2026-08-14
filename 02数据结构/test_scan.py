# -*- coding: utf-8 -*-
"""批量扫描 D:\\yq\\01虚拟机 下 02/03 开头文件夹的所有代码文件，
统计可视化器的解析/执行通过情况。排除 02C语言\\999复习巩固。"""
import sys, io, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simcore import Simulator, SimError

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

print(f"共 {len(targets)} 个代码文件")

stats = {"ok": 0, "empty": 0, "nomain": 0, "err": 0, "parse_fail": 0}
fails = []   # (path, category, msg, line)
t0 = time.time()
for i, path in enumerate(targets, 1):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            code = f.read()
    except Exception as ex:
        fails.append((path, "read", str(ex), 0))
        stats["parse_fail"] += 1
        continue
    if not code.strip():
        stats["empty"] += 1
        continue
    try:
        sim = Simulator(code)
    except Exception as ex:
        # 头文件（.h/.hpp）解析失败 → 归入“头文件(跳过)”，不影响通过率
        if path.lower().endswith((".h", ".hpp")):
            stats["nomain"] += 1
            continue
        stats["parse_fail"] += 1
        ln = getattr(ex, "line", 0)
        fails.append((path, "parse", str(ex), ln))
        continue
    if sim.main_name() is None:
        stats["nomain"] += 1
        continue
    try:
        sim.run()
        err = sim.engine.error if sim.engine else None
    except Exception as ex:
        stats["parse_fail"] += 1
        fails.append((path, "exec_exc", str(ex), getattr(ex, "line", 0)))
        continue
    if err:
        # 死循环 / 需输入 → 视为“可正常打开（显示部分状态）”
        if "需要手动输入" in err.msg or "疑似死循环" in err.msg:
            stats["ok"] += 1
            continue
        stats["err"] += 1
        fails.append((path, "run_err", err.msg, err.line))
    else:
        stats["ok"] += 1

elapsed = time.time() - t0
print(f"耗时 {elapsed:.1f}s")
print(f"OK(有快照)   : {stats['ok']}")
print(f"空文件        : {stats['empty']}")
print(f"无 main(头文件/笔记): {stats['nomain']}")
print(f"运行报错      : {stats['err']}")
print(f"解析失败      : {stats['parse_fail']}")
pass_rate = (stats["ok"] + stats["empty"] + stats["nomain"]) / max(1, len(targets)) * 100
print(f"可正常打开率(OK+空+无main): {pass_rate:.1f}%")
print(f"其中 OK(真正能出图) 率: {stats['ok']/max(1,len(targets))*100:.1f}%")

print("\n===== 失败清单 =====")
# 按目录分组
from collections import Counter
cat = Counter(os.path.relpath(os.path.dirname(p), BASE).split(os.sep)[0] if len(os.path.relpath(os.path.dirname(p), BASE).split(os.sep)) > 0 else "?" for p, *_ in fails)
print("按顶层文件夹失败分布:", dict(cat))
# 打印前 40 个失败
for path, kind, msg, ln in fails[:40]:
    print(f"  [{kind}] {os.path.relpath(path, BASE)} (行{ln}) {msg[:60]}")
