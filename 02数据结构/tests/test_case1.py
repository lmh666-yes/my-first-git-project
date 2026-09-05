# -*- coding: utf-8 -*-
"""案例讲解1 四文件: 引擎输出 vs 真实 gcc/g++ 逐字对比(01枚举/02void指针/03结构体/04C++实现)"""
import sys, io, os, subprocess, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simcore import Simulator, is_cpp_code
from cppsim import CppSimulator

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "案例讲解1")
CC = r"C:\mingw64\bin\gcc.exe"
GXX = r"C:\mingw64\bin\g++.exe"
FILES = [("01枚举法.c", False), ("02void指针.c", False),
         ("03结构体包装.c", False), ("04C++中实现.cpp", True)]

def real_out(path, is_cpp):
    exe = os.path.join(tempfile.gettempdir(), "case1_t.exe")
    comp = GXX if is_cpp else CC
    try:
        subprocess.run([comp, "-O0", "-o", exe, path], check=True, capture_output=True, timeout=40)
    except subprocess.CalledProcessError as e:
        return f"(编译失败) {e.stderr.decode('utf-8','replace')[-200:]}"
    try:
        r = subprocess.run([exe], capture_output=True, timeout=10)
        return r.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return "(运行超时)"

def run_sim(path, is_cpp):
    code = open(path, encoding="utf-8", errors="replace").read()
    assert is_cpp_code(code) == is_cpp, "C++ 识别不符"
    if is_cpp:
        sim = CppSimulator(code)
        sim.pending_inputs = []
        sim.run()
        eng = sim.engine
        out = "".join(eng.outputs) if eng else ""
        err = eng.error if eng else None
        return out, err
    sim = Simulator(code)
    sim.pending_inputs = []
    sim.run()
    eng = sim.engine if hasattr(sim, "engine") else None
    out = "".join(getattr(eng, "outputs", []))
    err = getattr(eng, "error", None) if eng else getattr(sim, "error", None)
    return out, err

def norm(s):
    return s.replace("\r\n", "\n").replace("\r", "\n").strip()

fails = 0
for fn, iscpp in FILES:
    path = os.path.join(BASE, fn)
    real = real_out(path, iscpp)
    try:
        out, err = run_sim(path, iscpp)
    except Exception as ex:
        out, err = "", f"异常 {type(ex).__name__}: {ex}"
    ok = norm(real) == norm(out) and err is None
    if not ok:
        fails += 1
    print(f"\n== {fn}  {'一致' if ok else '不一致!'} ==")
    if not ok:
        print(f"  [real] {real[:220]!r}")
        print(f"  [sim ] {out[:220]!r}")
        print(f"  [err ] {err}")
print(f"\n===== 案例讲解1 对比: {'全部通过' if fails==0 else str(fails)+' 失败'} =====")
sys.exit(1 if fails else 0)
