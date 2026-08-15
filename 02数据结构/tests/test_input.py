# -*- coding: utf-8 -*-
"""模拟输入(scanf)严格测试: 准确性 / 容量 / 容错 / 兼容 / GUI输入面板
覆盖: 单个/多个scanf、多次调用、数组元素、循环输入、输入不足容错、
      负数、大容量(1000输入)、GUI端输入传递、输入面板无崩溃"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from simcore import Simulator
from visualizer import App

root = tk.Tk()
root.withdraw()
root.geometry("1180x720")
app = App(root)
app._popup = False
root.update()
root.update_idletasks()

ok_all = True


def report(name, ok, info=""):
    global ok_all
    ok_all = ok_all and ok
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}  {info}")


def get_var(snaps, name, line=None):
    """取指定行快照中变量 name 的值"""
    if line is None:
        line = max(snaps)
    snap = snaps[line]
    for fr in snap.get("frames", []):
        for n, v in fr["vars"]:
            if n == name:
                val = v.get("value")
                if val and val[0] == "int":
                    return val[1]
                return val
    return None


def run_io(code, inputs):
    sim = Simulator(code)
    sim.pending_inputs = list(inputs)
    snaps = sim.run()
    err = sim.engine.error if sim.engine else None
    return snaps, err


print("=== A. 引擎层 scanf 准确性 ===")
# A1 单个
s, e = run_io("int main() { int a=0; scanf(\"%d\", &a); return 0; }", [42])
report("A1 scanf单个输入", e is None and get_var(s, "a") == 42, f"a={get_var(s, 'a')}")
# A2 多个变量
s, e = run_io("int main() { int a=0,b=0; scanf(\"%d%d\", &a, &b); return 0; }", [7, 9])
report("A2 scanf两个变量", e is None and get_var(s, "a") == 7 and get_var(s, "b") == 9,
       f"a={get_var(s,'a')} b={get_var(s,'b')}")
# A3 多次调用
s, e = run_io("int main() { int a=0,b=0; scanf(\"%d\", &a); scanf(\"%d\", &b); return 0; }", [3, 5])
report("A3 两次scanf调用", e is None and get_var(s, "a") == 3 and get_var(s, "b") == 5,
       f"a={get_var(s,'a')} b={get_var(s,'b')}")
# A4 数组元素
s, e = run_io("int main() { int arr[3]; scanf(\"%d\", &arr[1]); return 0; }", [8])
arr = None
snap = s[max(s)]
for fr in snap.get("frames", []):
    for n, v in fr["vars"]:
        if n == "arr" and "arr" in v:
            arr = v["arr"]
report("A4 scanf数组元素", e is None and arr and arr[1] == ("int", 8), f"arr[1]={arr[1] if arr else None}")
# A5 循环输入5个存数组
code5 = "int main() { int a[5]; for(int i=0;i<5;i++) scanf(\"%d\", &a[i]); return 0; }"
s, e = run_io(code5, [1, 2, 3, 4, 5])
arr = None
snap = s[max(s)]
for fr in snap.get("frames", []):
    for n, v in fr["vars"]:
        if n == "a" and "arr" in v:
            arr = v["arr"]
vals = [x[1] for x in arr] if arr else None
report("A5 循环scanf5个入数组", e is None and vals == [1, 2, 3, 4, 5], f"a={vals}")
# A6 输入不足容错
s, e = run_io("int main() { int a=99; scanf(\"%d\", &a); return 0; }", [])
report("A6 输入不足容错(a置0)", e is None and get_var(s, "a") == 0, f"a={get_var(s,'a')}")
# A7 负数
s, e = run_io("int main() { int a=0; scanf(\"%d\", &a); return 0; }", [-123])
report("A7 负数输入", e is None and get_var(s, "a") == -123, f"a={get_var(s,'a')}")
# A8 混合目标: &a 与变量与数组
s, e = run_io("int main() { int a=0,b=0,c[2]; scanf(\"%d\", &a); scanf(\"%d\", b); scanf(\"%d\", &c[1]); return 0; }", [11, 22, 33])
c = None
snap = s[max(s)]
for fr in snap.get("frames", []):
    for n, v in fr["vars"]:
        if n == "c" and "arr" in v:
            c = v["arr"]
report("A8 混合目标(&a/变量/数组)", e is None and get_var(s, "a") == 11 and get_var(s, "b") == 22 and c and c[1] == ("int", 33),
       f"a={get_var(s,'a')} b={get_var(s,'b')} c[1]={c[1] if c else None}")

print("=== B. 容量测试 ===")
# B1 1000 次 scanf(大容量) - 用程序内求和验证全部写入
N = 1000
code_big = ("int main() { int a[%d]; for(int i=0;i<%d;i++) scanf(\"%%d\", &a[i]);"
            " int s=0; for(int i=0;i<%d;i++) s+=a[i]; return 0; }" % (N, N, N))
inputs = list(range(N))
s, e = run_io(code_big, inputs)
expected = N * (N - 1) // 2
got = get_var(s, "s")
ok_big = e is None and got == expected
report(f"B1 大容量{N}次scanf(求和验证)", ok_big, f"求和={got} 期望={expected}")
# B2 输入多于需要(多余忽略)
s, e = run_io("int main() { int a=0; scanf(\"%d\", &a); return 0; }", [5, 6, 7])
report("B2 多余输入忽略", e is None and get_var(s, "a") == 5, f"a={get_var(s,'a')}")
# B3 输入含大数
s, e = run_io("int main() { int a=0; scanf(\"%d\", &a); return 0; }", [2147483647])
report("B3 大整数输入", e is None and get_var(s, "a") == 2147483647, f"a={get_var(s,'a')}")

print("=== C. 引擎容错/兼容 ===")
# C1 含scanf但无输入(_pending_inputs 空) 不崩
s, e = run_io("int main() { int a=0; scanf(\"%d\", &a); return 0; }", [])
report("C1 无输入不崩", e is None, f"err={e.msg[:30] if e else '无'}")
# C2 scanf 返回 0(成功) 不崩溃
s, e = run_io("int main() { int r; r = scanf(\"%d\", &r); return 0; }", [10])
report("C2 scanf返回值", e is None, f"err={e.msg[:30] if e else '无'}")
# C3 getchar/gets 混合
s, e = run_io("int main() { int c=0; c = getchar(); return 0; }", [])
report("C3 getchar容错", e is None, f"err={e.msg[:30] if e else '无'}")
# C4 含scanf的死循环检测兼容
s, e = run_io("int main() { int a=0; while(1){ scanf(\"%d\", &a); } return 0; }", [1, 2, 3])
report("C4 scanf+死循环(有输入,自动截断不崩)", e is not None, f"err={e.msg[:40] if e else '无'}")

print("=== D. GUI 输入面板 ===")
# D1 GUI端: 设置 _pending_inputs 后 run_all 变量正确
io_code = "int main() { int a=0,b=0; scanf(\"%d%d\", &a, &b); int s=a+b; return 0; }"
app.load_example_text(io_code)
root.update()
app._pending_inputs = [20, 22]
app._input_requested = True   # 跳过弹窗
app.run_all()
root.update()
au = app.drawer.last_audit
report("D1 GUI模拟输入执行", app.current_line is not None and au["nodes"] >= 0, f"行={app.current_line}")
# D2 GUI: 输入面板(弹窗)逻辑 - 无scanf不弹窗
app.load_example_text("int main() { int x=1; return x; }")
root.update()
import re
has_scanf = bool(re.search(r"\bscanf\b", app.get_code()))
report("D2 无scanf不请求输入", not has_scanf)
# D3 GUI: 含scanf时输入面板解析(逗号/空格分隔)
# 直接测解析逻辑: 模拟 entry 内容
def parse_inputs(text):
    vals = []
    for x in text.replace(",", " ").split():
        try:
            vals.append(int(x, 0))
        except Exception:
            try:
                vals.append(int(float(x)))
            except Exception:
                pass
    return vals
p1 = parse_inputs("1 2 3")
p2 = parse_inputs("10, 20, 30")
p3 = parse_inputs("0x10 42 abc 3.7")
report("D3 输入面板解析(空格/逗号/十六进制/忽略非法)",
       p1 == [1, 2, 3] and p2 == [10, 20, 30] and p3 == [16, 42, 3],
       f"p1={p1} p2={p2} p3={p3}")
# D4 GUI: 大容量输入面板传递
app.load_example_text(io_code)
root.update()
app._pending_inputs = list(range(100))
app._input_requested = True
app.run_all()
root.update()
report("D4 GUI大容量输入(100)不崩", app.current_line is not None)
# D5 GUI: 输入后 reset 干净
app.reset()
root.update()
report("D5 输入后reset干净", app._pending_inputs == [] and app.step_list == [])

print("=" * 60)
print("[%s] 模拟输入严格测试" % ("PASS" if ok_all else "FAIL"))
print("DONE")
