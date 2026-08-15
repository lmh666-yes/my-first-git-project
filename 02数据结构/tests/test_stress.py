# -*- coding: utf-8 -*-
"""02数据结构 程序压力 / 崩溃 / 保护还原 综合测试
A. 压力测试: 大程序/大堆/递归/大数组/死循环/快速连续操作
B. 崩溃测试: 各种非法/边界代码必须“安全失败”(捕获为 SimError 或 engine.error, 不裸崩)
C. 保护还原: 坏代码后加载好代码仍正常; reset 状态干净; 引擎状态隔离"""
import sys, io, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from simcore import Simulator, SimError
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


def safe_run(code):
    """安全执行: 返回 (snaps, err, 是否裸异常)"""
    try:
        sim = Simulator(code)
        if sim.main_name() is None:
            return {}, None, False
        snaps = sim.run()
        err = sim.engine.error if sim.engine else None
        return snaps, err, False
    except SimError as e:
        return {}, e, False
    except RecursionError:
        return {}, None, True     # 裸异常(未捕获), 标记
    except Exception:
        return {}, None, True


# ============================================================
# A. 压力测试
# ============================================================
print("=== A. 压力测试 ===")

# A1. 大程序(3000+ 行)执行
lines = ["#include <stdio.h>", "#include <stdlib.h>",
         "typedef struct Node { int val; struct Node *next; } Node;", ""]
for i in range(100):
    lines.append(f"int sum_{i}(int a[], int n) {{ int s=0; for(int k=0;k<n;k++) s+=a[k]; return s; }}")
    lines.append("")
for i in range(40):
    lines.append(f"Node *mk_{i}(int v) {{ Node *n=malloc(sizeof(Node)); n->val=v; n->next=0; return n; }}")
    lines.append("")
idx = 0
while len(lines) < 3050:
    lines.append(f"    int w{idx} = {idx % 100}; arr[{idx % 50}] += w{idx};")
    idx += 1
lines += ["int main() { int arr[50]; for(int i=0;i<50;i++) arr[i]=i;",
          "Node *head=0; for(int i=0;i<12;i++){ Node *n=malloc(sizeof(Node)); n->val=i*3; n->next=head; head=n; }",
          "int total = sum_0(arr,50)+sum_1(arr,50); Node *p=head; while(p){ total+=p->val; p=p->next; } return 0; }"]
big = "\n".join(lines)
t0 = time.time()
snaps, err, raw = safe_run(big)
t1 = time.time() - t0
report("A1 大程序(3050行)执行", err is None and not raw and len(snaps) > 0,
       f"快照{len(snaps)} 耗时{t1:.2f}s")

# A2. 大堆: 连续 malloc 600 次(超 MAX_BLOCKS=500)
mallocs = "int main() { int *p[600]; for(int i=0;i<600;i++){ p[i]=malloc(sizeof(int)); if(p[i]) *p[i]=i; } int s=0; for(int i=0;i<600;i++) if(p[i]) s+=*p[i]; return s; }"
snaps, err, raw = safe_run(mallocs)
heap_cnt = len(snaps[max(snaps)].get("heap", [])) if snaps and err is None else -1
report("A2 大堆600次malloc(上限500)", err is None and not raw and 0 < heap_cnt <= 500,
       f"实际堆块{heap_cnt}")

# A3. 深层递归
for name, code in [("A3a fact(50)", "int fact(int n){ if(n<=1) return 1; return n*fact(n-1);} int main(){ int r=fact(50); return 0; }"),
                   ("A3b fact(200)", "int fact(int n){ if(n<=1) return 1; return n*fact(n-1);} int main(){ int r=fact(200); return 0; }")]:
    snaps, err, raw = safe_run(code)
    report(name, not raw, f"err={err.msg[:40] if err else '无'}")

# A4. 大数组
arr_code = "int main() { int a[8000]; for(int i=0;i<8000;i++) a[i]=i; int s=0; for(int i=0;i<8000;i++) s+=a[i]; return 0; }"
snaps, err, raw = safe_run(arr_code)
report("A4 大数组8000元素", err is None and not raw, f"err={err.msg[:40] if err else '无'}")

# A5. 死循环检测
for name, code in [("A5a while(1)", "int main() { while(1) { } return 0; }"),
                   ("A5b for(;;)", "int main() { for(;;) { } return 0; }")]:
    snaps, err, raw = safe_run(code)
    report(name, err is not None and not raw, f"err={err.msg[:40] if err else '无'}")

# A6. 快速连续操作(GUI): load→run→step100→reset × 20
t0 = time.time()
crashes = 0
for i in range(20):
    try:
        app.load_example_text('int main() { int a[20]; for(int j=0;j<20;j++) a[j]=j*j; int s=0; for(int j=0;j<20;j++) s+=a[j]; return 0; }')
        root.update()
        app.build_step_list()
        for _ in range(min(100, len(app.step_list))):
            app.step_next()
            root.update()
        app.reset()
        root.update()
    except Exception as e:
        crashes += 1
report("A6 快速连续操作20轮(load/step/reset)", crashes == 0,
       f"崩溃{crashes} 耗时{time.time()-t0:.2f}s")

# ============================================================
# B. 崩溃测试(非法/边界代码必须安全失败)
# ============================================================
print("=== B. 崩溃测试 ===")
BAD_CODES = [
    "int main() { int x = ; }",                 # 语法错误
    "int main( { return 0; }",                  # 语法错误
    "int main() { int *p = 0; *p = 1; }",       # NULL 解引用
    "int main() { int *p; *p = 1; }",           # 野指针写
    "int main() { int a[3]; a[100] = 1; }",     # 越界
    "int main() { int x = 1 / 0; }",            # 除零
    "int main() { while(1) {} }",               # 死循环
    "int main() { return 0;",                   # 缺括号
    "void no_main() {}",                        # 无 main
    "",                                          # 空文件
    "// 只有注释",                               # 注释
    "int main() { undefined_func(); }",         # 未定义函数
    "int main() { int *p=malloc(4); free(p); *p=1; }",  # use-after-free
    "int main() { char *s=malloc(99999); s[0]='a'; }",  # 大分配
    "int main() { struct Foo x; }",             # 未定义结构体
    "int main() { return \"str\"; }",           # 类型混乱
]
bad_crash = 0
bad_safe = 0
for code in BAD_CODES:
    snaps, err, raw = safe_run(code)
    if raw:
        bad_crash += 1
    else:
        bad_safe += 1
report("B1 引擎16种非法代码全部安全失败", bad_crash == 0, f"安全{bad_safe} 裸崩{bad_crash}")

# GUI 层面: 逐个加载非法代码, 不崩
gui_crash = 0
for code in BAD_CODES:
    try:
        app.load_example_text(code)
        root.update()
        app.reset()
        root.update()
    except Exception:
        gui_crash += 1
report("B2 GUI加载16种非法代码不崩", gui_crash == 0, f"崩溃{gui_crash}")

# ============================================================
# C. 保护还原测试
# ============================================================
print("=== C. 保护还原测试 ===")

# C1. 坏代码后加载好代码, 仍正常
app.load_example_text("int main() { int x = ; }")   # 坏
root.update()
app.load_example_text('int main() { int s=0; for(int i=0;i<10;i++) s+=i; return 0; }')  # 好
root.update()
app.build_step_list()
ok_c1 = len(app.step_list) > 0 and app.current_line is not None
report("C1 坏代码后加载好代码仍可执行", ok_c1, f"步数{len(app.step_list)}")

# C2. 好→坏→好→空→好 连续切换
seq_ok = True
for code in ['int main() { int x=1; return x; }',
             "int main() { while(1) {} }",
             'int main() { int a=2,b=3; return a+b; }',
             "",
             'int main() { char *p="hi"; return 0; }']:
    try:
        app.load_example_text(code)
        root.update()
        app.run_all()
        root.update()
    except Exception:
        seq_ok = False
report("C2 好/坏/空交替加载5次不崩", seq_ok)

# C3. reset 后状态干净
app.load_example_text('int main() { int s=0; for(int i=0;i<10;i++) s+=i; return 0; }')
root.update()
app.build_step_list()
app.reset()
root.update()
clean = (app.step_list == [] and app.snapshots == {} and app.step_idx == -1
         and len(app.drawer.panels) == 0 and app.current_line is None)
report("C3 reset 后状态完全还原", clean)

# C4. 引擎状态隔离: 坏代码后执行好代码正常
safe_run("int main() { int *p=0; *p=1; }")   # 先跑坏的
snaps, err, raw = safe_run('int main() { int s=0; for(int i=0;i<10;i++) s+=i; return 0; }')
report("C4 引擎坏代码后好代码正常", err is None and not raw and len(snaps) > 0,
       f"快照{len(snaps)}")

# C5. GUI 逐步回放出错后再运行(还原)
app.load_example_text('int main() { int a=5; while(a>0) a=a-1; return 0; }')
root.update()
app.build_step_list()
n_before = len(app.step_list)
# 快速步进到最后, 再 reset, 再逐步
for _ in range(n_before):
    app.step_next()
    root.update()
app.reset()
root.update()
app.step_next()
root.update()
ok_c5 = app.step_idx == 0 and len(app.step_list) > 0
report("C5 逐步到终点→reset→重跑还原", ok_c5)

print("=" * 60)
print("[%s] 压力 / 崩溃 / 保护还原 综合测试" % ("PASS" if ok_all else "FAIL"))
print("DONE")
