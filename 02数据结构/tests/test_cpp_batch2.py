# -*- coding: utf-8 -*-
"""本批(批2) C++ 目标文件: CppSimulator 输出 vs 真实 g++"""
import sys, io, os, subprocess, tempfile, traceback
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cppsim import CppSimulator

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "实例样本")
GXX = r"C:\mingw64\bin\g++.exe"
# (文件名, g++ 运行 stdin, 模拟器 cin 输入序列)
FILES = [("03类继承中的构造和析构.cpp", b"", []),
         ("12类对象成员.cpp", b"", []),
         ("01类外堆内存.cpp", b"", []),
         ("02cppdemo.cpp", b"5\n6.5\n", [5, 6.5]),
         ("01类定义.cpp", b"", []),
         ("01类继承语法.cpp", b"", [])]

def real_out(path, stdin=b""):
    exe = os.path.join(tempfile.gettempdir(), "cpp2_t.exe")
    try:
        subprocess.run([GXX, "-O0", "-o", exe, path], check=True, capture_output=True, timeout=40)
    except subprocess.CalledProcessError as e:
        return f"(编译失败) {e.stderr.decode('utf-8','replace')[-300:]}"
    try:
        r = subprocess.run([exe], capture_output=True, timeout=10, input=stdin)
        return r.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return "(运行超时)"

def norm(s):
    return s.replace("\r\n", "\n").replace("\r", "\n").strip()

fails = 0
for fn, rstdin, inputs in FILES:
    path = os.path.join(BASE, fn)
    code = open(path, encoding="utf-8", errors="replace").read()
    real = real_out(path, rstdin)
    try:
        sim = CppSimulator(code)
        sim.pending_inputs = list(inputs)
        sim.run()
        eng = sim.engine
        out = "".join(eng.outputs) if eng else ""
        err = eng.error if eng else None
    except Exception as ex:
        traceback.print_exc()
        print(f"[FAIL] {fn}: 异常 {ex}")
        fails += 1
        continue
    ok = norm(real) == norm(out)
    if not ok:
        fails += 1
    print(f"\n== {fn}  {'一致' if ok else '不一致!'} ==")
    if not ok:
        print(f"  [g++] {real[:300]!r}")
        print(f"  [cpp] {out[:300]!r}")
        print(f"  错误: {err}")
print(f"\n===== 批2 对比 {'全部通过' if fails==0 else str(fails)+' 失败'} =====")
sys.exit(1 if fails else 0)
