# -*- coding: utf-8 -*-
"""题库构建器 v2：从单个 Word 文档（题目自带答案）解析生成 题库.json。
输入：嵌入式软件开发（中级）题库（含答案）.docx
题型：一、单选题(80) + 二、判断题(50)。
特点：题干可含多行代码（完整保留）；判断题 5 题一组共享一个答案串；选项兼容带/不带 A-D 前缀。"""
import sys, io, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
import docx

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "嵌入式软件开发（中级）题库（含答案） -划重点(1) (1).docx")
OUT = os.path.join(HERE, "题库.json")

# 已知原文档笔误修正（不影响其他题）：第24题“interface”重复，答案D指向 ifconfig
FIXES = {
    "查看服务器网口配置的命令是什么": {
        "options": ["ipconfig", "show", "interface", "ifconfig"],
        "answer": "D",
    },
}


def load_paras():
    if not os.path.exists(SRC):
        sys.exit("[错误] 未找到题库 Word 文档: " + SRC)
    doc = docx.Document(SRC)
    return [p.text.strip() for p in doc.paragraphs if p.text.strip()]


# ---------- 单选题 ----------
def split_choice_blocks(paras):
    """按“答案：X”把单选题区切块，返回 [(题干+选项行, 答案行)]"""
    start = paras.index("一、单选题：") + 1
    end = next(i for i, t in enumerate(paras) if t.startswith("二、判断题"))
    blocks, cur = [], []
    for t in paras[start:end]:
        if t.startswith("答案"):
            if cur:
                blocks.append((cur, t))
            cur = []
        else:
            cur.append(t)
    return blocks


def parse_choice_block(lines, ans_line):
    """返回 (stem, opts, problem)。opts=[{'key','text'}]"""
    problem = ""
    m = re.search(r"答案[:：]\s*([A-Da-d])", ans_line)
    answer = m.group(1).upper() if m else "?"
    # 定位带 A-D 前缀的选项行
    pre_idx = [i for i, ln in enumerate(lines) if re.match(r"^[A-Da-d][\.、．]", ln)]
    if len(pre_idx) >= 4:
        stem_lines = lines[:pre_idx[0]]
        opt_lines = lines[pre_idx[0]:]
        opts = []
        for ln in opt_lines:
            m2 = re.match(r"^([A-Da-d])[\.、．]\s*(.*)$", ln)
            if m2:
                opts.append({"key": m2.group(1).upper(), "text": m2.group(2).strip()})
    else:
        # 无前缀：最后 4 行是选项，其余（含代码）是题干
        if len(lines) > 4:
            stem_lines, opt_lines = lines[:-4], lines[-4:]
        else:
            stem_lines, opt_lines = lines[:1], lines[1:]
        opts = [{"key": "ABCD"[i] if i < 4 else "?", "text": ln} for i, ln in enumerate(opt_lines)]
        # 一行内包含多个选项（用 2+ 空格 或 制表符 分隔，如“-3\t9\t-12\t6”）
        if len(opts) == 1 and re.search(r"\t|\s{2,}", opts[0]["text"]):
            parts = re.split(r"\t|\s{2,}", opts[0]["text"].strip())
            opts = [{"key": "ABCD"[i], "text": p} for i, p in enumerate(parts)]
    stem = "\n".join(stem_lines)
    # 已知笔误修正
    for kw, fix in FIXES.items():
        if kw in stem:
            opts = [{"key": "ABCD"[i], "text": t} for i, t in enumerate(fix["options"])]
            answer = fix["answer"]
            stem = stem.split("\n")[0]   # 题干只保留首行，去除误并入的选项行
            problem = "已按笔误修正（原文档选项重复 interface）"
            break
    # 选项数检查
    if len(opts) != 4:
        problem = f"选项数={len(opts)}"
    return stem, opts, answer, problem


# ---------- 判断题 ----------
def split_judge_blocks(paras):
    """按“答案：×××…”把判断题区切块"""
    jstart = next(i for i, t in enumerate(paras) if t.startswith("二、判断题")) + 1
    blocks, cur = [], []
    for t in paras[jstart:]:
        if t.startswith("答案"):
            if cur:
                blocks.append((cur, t))
            cur = []
        else:
            cur.append(t)
    return blocks


def parse_judge_block(lines, ans_line):
    """判断题 5 题一组共享答案串；若行数多于答案数，末题带代码（多行合并）"""
    items = []          # [(stem, answer, problem)]
    m = re.search(r"答案[:：]\s*([√×对错TF]+)", ans_line)
    if not m:
        return [(ln, "?", "答案格式异常") for ln in lines]
    s = m.group(1)
    N, M = len(s), len(lines)
    norm = lambda c: "√" if c in ("√", "对", "T") else "×"
    if M == N:
        for j in range(N):
            items.append((lines[j], norm(s[j]), ""))
    elif M > N:
        # 前 N-1 行各一题，第 N 题 = 剩余行（含代码）
        for j in range(N - 1):
            items.append((lines[j], norm(s[j]), ""))
        last_stem = "\n".join(lines[N - 1:])
        items.append((last_stem, norm(s[N - 1]), "末题含多行代码已合并"))
    else:
        for j in range(M):
            items.append((lines[j], norm(s[j]) if j < N else "?", "答案数多于题数"))
    return items


def build():
    paras = load_paras()
    bank = []

    # ---- 单选 ----
    problems = []
    for idx, (lines, ans) in enumerate(split_choice_blocks(paras), 1):
        stem, opts, answer, problem = parse_choice_block(lines, ans)
        if problem:
            problems.append(f"单选#{idx} {problem} | {stem[:40]}")
        bank.append({
            "id": f"choice-{idx}", "kind": "choice", "kind_name": "单选题",
            "num": idx, "stem": stem, "options": opts,
            "answer": answer, "explain": "",
        })

    # ---- 判断 ----
    jnum = 0
    for bi, (lines, ans) in enumerate(split_judge_blocks(paras), 1):
        for stem, answer, problem in parse_judge_block(lines, ans):
            jnum += 1
            if problem:
                problems.append(f"判断#{jnum} {problem} | {stem[:40]}")
            bank.append({
                "id": f"judge-{jnum}", "kind": "judge", "kind_name": "判断题",
                "num": jnum, "stem": stem, "options": [],
                "answer": answer, "explain": "",
            })

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(bank, f, ensure_ascii=False, indent=1)

    cnt = {}
    for it in bank:
        cnt[it["kind"]] = cnt.get(it["kind"], 0) + 1
    print("已生成:", OUT)
    print("题数统计:", cnt, "共", len(bank), "题")
    if problems:
        print("\n[!] 解析告警:")
        for pr in problems:
            print("   ", pr)
    else:
        print("解析告警: 无")
    # 抽查
    for it in bank[:3] + bank[80:83]:
        print(f"  [{it['kind_name']} {it['num']}] 答案={it['answer']!r} 题干={it['stem'][:40]!r}")
        if it["options"]:
            print("     选项:", ", ".join(f"{o['key']}.{o['text'][:18]}" for o in it["options"]))
    # 代码题抽查
    code = [it for it in bank if "\n" in it["stem"]]
    print(f"\n含代码/多行题干题数: {len(code)}")
    for it in code[:5]:
        print(f"  [{it['kind']} {it['num']}] 答案={it['answer']} 行数={it['stem'].count(chr(10))+1}")
        print("     " + it["stem"][:120].replace("\n", " ⏎ "))


if __name__ == "__main__":
    build()
