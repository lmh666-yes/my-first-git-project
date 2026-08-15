# -*- coding: utf-8 -*-
"""准确性验证：验证本轮新增功能的模拟结果是否正确"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simcore import Simulator

fails = 0

def check(cond, msg):
    global fails
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        fails += 1

def final_var(sim, name):
    """取最终快照里 name 变量的值（int 或数组）"""
    if not sim.snapshots:
        return None
    last = max(sim.snapshots.keys())
    snap = sim.snapshots[last]
    for f in snap["frames"]:
        for vn, vv in f["vars"]:
            if vn == name:
                if isinstance(vv, dict) and "value" in vv and isinstance(vv["value"], tuple):
                    return vv["value"][1]
                if isinstance(vv, dict) and "arr" in vv:
                    return [x[1] for x in vv["arr"] if isinstance(x, tuple) and x[0] == "int"]
    return None

# 1. 指针算术：int *p = a+2; p[0] 应为 3
code1 = """
int main() { int a[5]={1,2,3,4,5}; int *p = a + 2; int x = p[0]; int y = *p; return 0; }
"""
s = Simulator(code1); s.run()
check(final_var(s, "x") == 3, f"p=a+2; p[0]=3 (实际 {final_var(s, 'x')})")
check(final_var(s, "y") == 3, f"*p=3 (实际 {final_var(s, 'y')})")

# 2. 宏：#define N 10; x=N → 10
code2 = """
#define N 10
int main() { int x = N; return 0; }
"""
s = Simulator(code2); s.run()
check(final_var(s, "x") == 10, f"宏 N=10 (实际 {final_var(s, 'x')})")

# 3. 内置宏 INT_MAX
code3 = """
int main() { int x = INT_MAX; int y = INT_MIN; return 0; }
"""
s = Simulator(code3); s.run()
check(final_var(s, "x") == 2147483647, f"INT_MAX (实际 {final_var(s, 'x')})")
check(final_var(s, "y") == -2147483648, f"INT_MIN (实际 {final_var(s, 'y')})")

# 4. 字符串字面量 *p → 'h'
code4 = """
int main() { char *p = "hello"; int c = *p; return 0; }
"""
s = Simulator(code4); s.run()
check(final_var(s, "c") == ord('h'), f"*p='h' (实际 {final_var(s, 'c')})")

# 5. 全局变量
code5 = """
int g = 5;
int main() { int x = g + 1; return 0; }
"""
s = Simulator(code5); s.run()
check(final_var(s, "x") == 6, f"全局变量 g=5, x=6 (实际 {final_var(s, 'x')})")

# 6. 带参宏 MAX
code6 = """
int main() { int x = MAX(3, 7); return 0; }
"""
s = Simulator(code6); s.run()
check(final_var(s, "x") == 7, f"MAX(3,7)=7 (实际 {final_var(s, 'x')})")

# 7. int 指针自增步长 4
code7 = """
int main() { int a[5]={10,20,30,40,50}; int *p = a; p++; int x = *p; return 0; }
"""
s = Simulator(code7); s.run()
check(final_var(s, "x") == 20, f"int* p++ 后 *p=20 (实际 {final_var(s, 'x')})")

# 8. char 指针自增步长 1
code8 = """
int main() { char *p = "abc"; p++; p++; int x = *p; return 0; }
"""
s = Simulator(code8); s.run()
check(final_var(s, "x") == ord('c'), f"char* p++两次后 *p='c' (实际 {final_var(s, 'x')})")

# 9. &arr[i] 元素槽：*p 读写
code9 = """
int main() { int a[3]={1,2,3}; int *p = &a[1]; int x = *p; *p = 99; int y = a[1]; return 0; }
"""
s = Simulator(code9); s.run()
check(final_var(s, "x") == 2, f"&a[1] *p=2 (实际 {final_var(s, 'x')})")
check(final_var(s, "y") == 99, f"*p=99 后 a[1]=99 (实际 {final_var(s, 'y')})")

# 10. 结构体嵌套
code10 = """
struct B { int y; };
struct A { int x; struct B b; };
int main() { struct A a; a.x = 5; a.b.y = 7; int z = a.b.y; return 0; }
"""
s = Simulator(code10); s.run()
check(final_var(s, "z") == 7, f"嵌套结构体 a.b.y=7 (实际 {final_var(s, 'z')})")

# 11. malloc 数组 *p++ 写
code11 = """
#include <stdlib.h>
int main() { int *p = (int*)malloc(sizeof(int)*3); *p = 1; *(p+1) = 2; int x = p[1]; return 0; }
"""
s = Simulator(code11); s.run()
check(final_var(s, "x") == 2, f"malloc 数组 p[1]=2 (实际 {final_var(s, 'x')})")

# 12. 三目运算符
code12 = """
int main() { int a = 5; int x = (a > 3) ? 100 : 200; return 0; }
"""
s = Simulator(code12); s.run()
check(final_var(s, "x") == 100, f"三目 (a>3)?100:200=100 (实际 {final_var(s, 'x')})")

# 13. 位运算 | ~
code13 = """
int main() { int a = 5 | 2; int b = ~0 & 0xFF; int c = 1 << 4; return 0; }
"""
s = Simulator(code13); s.run()
check(final_var(s, "a") == 7, f"5|2=7 (实际 {final_var(s, 'a')})")
check(final_var(s, "b") == 255, f"~0 & 0xFF=255 (实际 {final_var(s, 'b')})")
check(final_var(s, "c") == 16, f"1<<4=16 (实际 {final_var(s, 'c')})")

# 14. switch
code14 = """
int main() { int x = 0; switch(2){case 1: x=10; break; case 2: x=20; break; default: x=30;} return 0; }
"""
s = Simulator(code14); s.run()
check(final_var(s, "x") == 20, f"switch case2=20 (实际 {final_var(s, 'x')})")

# 15. 函数调用/递归阶乘
code15 = """
int fact(int n){ if(n<=1) return 1; return n*fact(n-1); }
int main() { int x = fact(5); return 0; }
"""
s = Simulator(code15); s.run()
check(final_var(s, "x") == 120, f"fact(5)=120 (实际 {final_var(s, 'x')})")

# 16. 全局数组 + sizeof
code16 = """
int main() { int a[10]; int n = sizeof(a)/sizeof(a[0]); return 0; }
"""
s = Simulator(code16); s.run()
check(final_var(s, "n") == 10, f"sizeof(a)/sizeof(a[0])=10 (实际 {final_var(s, 'n')})")

# 17. 联合体顶层
code17 = """
union { unsigned i; unsigned char c; }u;
int main() { u.i = 0x1; int x = u.c; return 0; }
"""
s = Simulator(code17); s.run()
check(final_var(s, "x") == 1, f"union u.c 读值 (实际 {final_var(s, 'x')})")

# 18. 数组自动扩展(越界宽容)
code18 = """
int main() { int a[3]={1,2,3}; a[10] = 5; int x = a[10]; return 0; }
"""
s = Simulator(code18); s.run()
check(final_var(s, "x") == 5, f"越界写后读回 (实际 {final_var(s, 'x')})")

print()
print("===== 准确性验证: %s =====" % ("全部通过" if fails == 0 else f"有 {fails} 个失败"))
sys.exit(fails)
