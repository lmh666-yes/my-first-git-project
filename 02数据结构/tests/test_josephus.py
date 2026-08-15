# -*- coding: utf-8 -*-
"""约瑟夫环实战测试: 加载 05约瑟夫环.c(scanf 输入 + 循环链表 + VLA + free),
验证模拟器能否解析执行, 模拟输入是否正确工作。"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simcore import Simulator, SimError

SRC = r"D:\qq缓存\文件\05约瑟夫环.c"
if not os.path.exists(SRC):
    print("跳过: 找不到 05约瑟夫环.c")
    print("DONE")
    sys.exit(0)

code = open(SRC, encoding="utf-8", errors="replace").read()
print(f"文件行数: {len(code.splitlines())}")

# 1. 解析
try:
    sim = Simulator(code)
    print("[PASS] 解析成功  main=" + str(sim.main_name()))
except Exception as ex:
    print(f"[FAIL] 解析失败: {ex}")
    sys.exit(1)

# 2. 模拟输入 n=6 执行
try:
    sim.pending_inputs = [6]
    snaps = sim.run()
    err = sim.engine.error if sim.engine else None
    print(f"快照数: {len(snaps)}")
    if err:
        print(f"[FAIL] 执行报错: {err.msg}")
    else:
        print("[PASS] n=6 执行完成, 无错误")
except Exception as ex:
    print(f"[FAIL] 执行异常: {ex}")

print("DONE")
