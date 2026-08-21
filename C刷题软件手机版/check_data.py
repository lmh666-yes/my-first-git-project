# -*- coding: utf-8 -*-
"""数据准确性校验: 桌面版题库.json vs 手机版 index.html 内嵌 BANK 逐题一致"""
import sys, io, os, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

ROOT = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(ROOT, "..", "C刷题软件", "题库.json")
HTML = os.path.join(ROOT, "www", "index.html")

def main():
    # 1. 加载桌面版题库
    bank = json.load(open(BANK, encoding="utf-8"))
    print(f"题库.json: {len(bank)} 题")

    # 2. 从 index.html 提取 BANK
    html = open(HTML, encoding="utf-8").read()
    m = re.search(r"const BANK=(.*?);\nconst EXAM_MIN", html, re.S)
    assert m, "未找到 BANK"
    mob = json.loads(m.group(1))
    print(f"index.html: {len(mob)} 题")

    # 3. 数量与题型
    def kinds(b):
        c = {}
        for it in b:
            c[it.get("kind")] = c.get(it.get("kind"), 0) + 1
        return c
    print("题库.json 题型:", kinds(bank))
    print("index.html 题型:", kinds(mob))
    assert len(bank) == len(mob) == 130, "题数不一致!"
    assert kinds(bank) == kinds(mob) == {"choice": 80, "judge": 50}, "题型分布不一致!"

    # 4. 逐题字段一致
    fields = ["id", "kind", "kind_name", "num", "stem", "answer", "explain"]
    diffs = []
    for a, b in zip(bank, mob):
        for f in fields:
            if a.get(f) != b.get(f):
                diffs.append((a.get("id"), f, a.get(f), b.get(f)))
        if a.get("options") != b.get("options"):
            diffs.append((a.get("id"), "options", a.get("options"), b.get("options")))
    print("字段不一致数:", len(diffs))
    for d in diffs[:10]:
        print("  DIFF:", d)

    # 5. 字段完整性
    missing = []
    for it in bank:
        for f in ("id", "kind", "stem", "answer"):
            if not it.get(f):
                missing.append((it.get("id"), f))
    print("缺关键字段数:", len(missing))

    # 6. 选项完整性
    bad_opt = []
    for it in bank:
        if it.get("kind") == "choice":
            for o in it.get("options", []):
                if not o.get("key") or not o.get("text"):
                    bad_opt.append(it.get("id"))
            keys = [o.get("key") for o in it.get("options", [])]
            if len(keys) != len(set(keys)):
                bad_opt.append(it.get("id") + ": 选项key重复")
    print("选项异常数:", len(bad_opt))

    # 7. 判断题答案格式
    JOK = {"对", "错", "√", "×", "T", "F", "TRUE", "FALSE"}
    bad_j = []
    for it in bank:
        if it.get("kind") == "judge":
            a = str(it.get("answer", "")).strip().upper()
            if a not in {"对", "错", "√", "×", "T", "F", "TRUE", "FALSE"}:
                bad_j.append((it.get("id"), it.get("answer")))
    print("判断题答案异常数:", len(bad_j), bad_j[:5])

    # 8. 选择题答案是否在选项内
    bad_a = []
    for it in bank:
        if it.get("kind") == "choice":
            ans = str(it.get("answer", "")).strip().upper()
            keys = [o.get("key") for o in it.get("options", [])]
            if ans not in keys:
                bad_a.append((it.get("id"), it.get("answer"), keys))
    print("选择题答案不在选项内:", len(bad_a), bad_a[:5])

    ok = (len(diffs) == 0 and len(missing) == 0 and len(bad_opt) == 0
          and len(bad_j) == 0 and len(bad_a) == 0)
    print("\n===== 数据校验:", "全部通过 ✓" if ok else "存在异常 ✗", "=====")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
