# -*- coding: utf-8 -*-
"""11个纯C样本: 引擎输出 vs 真实gcc编译输出 对比 + 最终快照要点(用于图形验证)"""
import sys, io, os, subprocess, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simcore import Simulator

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "实例样本")
GCC = r"C:\mingw64\bin\gcc.exe"

C_FILES = ["01cdemo.c", "01单向带头不循环.c", "01双向循环链表.c", "01循环队列.c",
           "01顺序栈.c", "02单向带头循环链表.c", "02链式栈.c", "02链式队列.c",
           "03单向不带头循环链表.c", "案例1.c", "案例2.c"]

def real_out(path):
    """真实 gcc 编译运行输出(带默认输入)"""
    exe = os.path.join(tempfile.gettempdir(), "cvis_t.exe")
    try:
        subprocess.run([GCC, "-O0", "-o", exe, path], check=True,
                       capture_output=True, timeout=30)
    except subprocess.CalledProcessError as e:
        return f"(编译失败) {e.stderr.decode('utf-8', 'replace')[-200:]}"
    try:
        r = subprocess.run([exe], capture_output=True, timeout=10,
                           input=b"5\n3\n8\n1\n9\n0\n10\n6\n7\n4\n2\n")
        return r.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return "(运行超时)"

def snap_brief(path):
    """引擎跑到最后: 返回输出 + 快照要点"""
    code = open(path, encoding="utf-8", errors="replace").read()
    sim = Simulator(code)
    sim.run()
    eng = sim.engine
    info = []
    out_txt = "".join(getattr(eng, "outputs", []))
    if eng.error:
        info.append(f"ERR: {eng.error.msg}")
    # 堆块列表
    lines = []
    for blk in sorted(eng.heap.values(), key=lambda b: b.addr):
        tag = "栈" if blk.is_stack else "堆"
        fields = {k: (v.val if hasattr(v, "val") else str(v))
                  for k, v in blk.fields.items()}
        lines.append(f"{tag}@{blk.addr:x} {blk.typename}{{{fields}}}")
    return out_txt, lines

total_ok = 0
def norm(s):
    return s.replace("\r\n", "\n").replace("\r", "\n").strip()

for fn in C_FILES:
    path = os.path.join(BASE, fn)
    rout = real_out(path)
    try:
        sout, slines = snap_brief(path)
    except Exception as e:
        sout, slines = f"(引擎异常 {e})", []
    match = norm(rout) == norm(sout)
    total_ok += 1 if match else 0
    print(f"\n===== {fn}  引擎输出与真实 {'一致' if match else '不一致!'} =====")
    if not match:
        print(f"  [真实] {rout!r}")
        print(f"  [引擎] {sout!r}")
    else:
        print(f"  输出: {rout[:130]!r}")
    # 快照要点(每文件最多10块)
    for ln in slines[:10]:
        print(f"    {ln}")
print(f"\n===== 输出一致 {total_ok}/{len(C_FILES)} =====")
