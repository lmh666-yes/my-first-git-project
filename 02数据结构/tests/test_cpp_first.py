# -*- coding: utf-8 -*-
"""CppSimulator 首批目标文件: 输出 vs 真实 g++ 对比 + 快照要点"""
import sys, io, os, subprocess, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simcore import is_cpp_code
from cppsim import CppSimulator

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "实例样本")
GXX = r"C:\mingw64\bin\g++.exe"

def real_out(path, stdin_bytes=b""):
    exe = os.path.join(tempfile.gettempdir(), "cppvis_t.exe")
    try:
        subprocess.run([GXX, "-O0", "-o", exe, path], check=True,
                       capture_output=True, timeout=30)
    except subprocess.CalledProcessError as e:
        return f"(编译失败) {e.stderr.decode('utf-8','replace')[-200:]}"
    try:
        r = subprocess.run([exe], capture_output=True, timeout=10, input=stdin_bytes)
        return r.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return "(运行超时)"

def run_cpp(path, inputs=None):
    code = open(path, encoding="utf-8", errors="replace").read()
    assert is_cpp_code(code), f"{os.path.basename(path)} 未识别为 C++"
    sim = CppSimulator(code)
    sim.pending_inputs = list(inputs or [])
    sim.run()
    eng = sim.engine
    out = "".join(eng.outputs) if eng else ""
    err = eng.error if eng else None
    return out, err, eng, sim

def norm(s):
    return s.replace("\r\n", "\n").replace("\r", "\n").strip()

# --- 1. 02cppdemo.cpp: 需要 cin 输入(给 5 6.5) ---
path = os.path.join(BASE, "02cppdemo.cpp")
real = real_out(path, b"5\n6.5\n")
out, err, eng, sim = run_cpp(path, inputs=[5, 6.5])
print("== 02cppdemo.cpp ==")
print("  一致" if norm(real) == norm(out) else "  不一致!")
if norm(real) != norm(out):
    print(f"  [g++] {real!r}")
    print(f"  [cpp] {out!r}")
    print(f"  错误: {err}")
else:
    print(f"  输出: {real[:140]!r}")
# 帧/堆要点
if eng and eng.snapshots:
    last = eng.snapshots[max(eng.snapshots.keys())]
    print(f"  最终帧: {[fr['func'] for fr in last['frames']]} 变量: "
          f"{[v[0] for fr in last['frames'] for v in fr['vars']]}")

# --- 2. 01类定义.cpp ---
path2 = os.path.join(BASE, "01类定义.cpp")
real2 = real_out(path2)
out2, err2, eng2, sim2 = run_cpp(path2)
print("\n== 01类定义.cpp ==")
print("  一致" if norm(real2) == norm(out2) else "  不一致!")
if norm(real2) != norm(out2):
    print(f"  [g++] {real2!r}")
    print(f"  [cpp] {out2!r}")
    print(f"  错误: {err2}")
else:
    print(f"  输出: {real2[:140]!r}")
if eng2 and eng2.snapshots:
    last2 = eng2.snapshots[max(eng2.snapshots.keys())]
    print(f"  最终堆块: " + ", ".join(f"{b['typename']}@{b['addr']:#x}{{{b['fields']}}}" for b in last2["heap"]))
    print(f"  帧: {[fr['func'] for fr in last2['frames']]}")
