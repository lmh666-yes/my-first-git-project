# -*- coding: utf-8 -*-
"""C++ 识别与分流测试:
 ① 44 个 .cpp / 伪C++ .c 全部判为 C++(真)
 ② 11 个纯 C 样本 + examples 全部判为 C(假)  —— 不影响 C
 ③ Simulator 对 C++ 给出识别错误而非静默空跑
 ④ 对 C 文件 run 行为不变"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simcore import Simulator, is_cpp_code, SimError

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "实例样本")
EX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")

fails = 0
def ok(cond, msg):
    global fails
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        fails += 1

# ① 44 cpp + 2 伪 c (02cppdemo.c / 04string.c) 应判 C++
all_files = sorted(os.listdir(BASE))
cpp_ok = c_false_pos = 0
checked_cpp = 0
for fn in all_files:
    if not fn.lower().endswith((".c", ".cpp")):
        continue
    code = open(os.path.join(BASE, fn), encoding="utf-8", errors="replace").read()
    if not code.strip():
        continue
    if fn.lower().endswith(".cpp") or fn in ("02cppdemo.c", "04string.c"):
        checked_cpp += 1
        if is_cpp_code(code):
            cpp_ok += 1
        else:
            print(f"  ! 未识别: {fn}")
    else:
        # 纯 C 样本: 不应判 C++
        if is_cpp_code(code):
            c_false_pos += 1
            print(f"  ! C 被误判为 C++: {fn}")
ok(checked_cpp > 0 and cpp_ok == checked_cpp,
   f"识别 {cpp_ok}/{checked_cpp} 个 C++ 文件")
ok(c_false_pos == 0, f"纯 C 样本无误判(0 个)")

# examples 示例也应判 C(假)
for fn in os.listdir(EX):
    code = open(os.path.join(EX, fn), encoding="utf-8", errors="replace").read()
    if code.strip() and is_cpp_code(code):
        print(f"  ! examples 误判: {fn}")
        fails += 1
ok(True, "examples 示例无误判")

# ③ Simulator 对 C++ 识别错误
bad = 0
for fn in ["02cppdemo.cpp", "01类定义.cpp", "09空类不空.cpp", "04string.c", "05引用.cpp", "07auto关键字.cpp"]:
    code = open(os.path.join(BASE, fn), encoding="utf-8", errors="replace").read()
    sim = Simulator(code)
    snaps = sim.run()
    err = sim.engine.error if sim.engine else None
    cppdet = sim.cpp_detected
    good = cppdet and not snaps and err is not None and "C++" in err.msg
    if not good:
        bad += 1
        print(f"  ! {fn}: cpp={cppdet} snaps={len(snaps)} err={err.msg if err else None}")
ok(bad == 0, "Simulator 对 C++ 给识别错误(不空跑、不按 C 解析)")

# ④ C 文件: run 不受影响(以 2 个真实 C 样本为例, 应正常出快照)
c_ok = 0
for fn in ["01cdemo.c", "案例1.c", "01单向带头不循环.c"]:
    code = open(os.path.join(BASE, fn), encoding="utf-8", errors="replace").read()
    sim = Simulator(code)
    snaps = sim.run()
    if snaps and not (sim.engine and sim.engine.error) and not sim.cpp_detected:
        c_ok += 1
ok(c_ok == 3, "纯 C 样本 run 正常(3 个示例均出快照且无识别干扰)")

print(f"\n===== C++ 识别测试: {'全部通过' if fails==0 else str(fails)+' 失败'} =====")
sys.exit(1 if fails else 0)
