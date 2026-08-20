# -*- coding: utf-8 -*-
"""题库构建器：读取「原题目.docx」+「原题目答案.docx」，解析为 题库.json。
题型：一、单选题(80) 二、判断题(50) 三、简答与编程题(11)。"""
import sys, io, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
import docx

HERE = os.path.dirname(os.path.abspath(__file__))
QP = os.path.join(HERE, "原题目.docx")
AP = os.path.join(HERE, "原题目答案.docx")
OUT = os.path.join(HERE, "题库.json")

# ---------- 按大题切分段落 ----------
def split_sections(doc):
    """返回 [{'title':..., 'lines':[...]}]，按 '一、二、三、...、' 标题切分"""
    sections = []
    cur = None
    for p in doc.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        m = re.match(r'^([一二三四五六七八九十]+)、(.+)$', t)
        if m:
            if cur:
                sections.append(cur)
            cur = {"title": t, "lines": []}
        elif cur is not None:
            cur["lines"].append(t)
    if cur:
        sections.append(cur)
    return sections

# ---------- 题目块切分 ----------
def split_questions(lines):
    """按 '第N题' 切分为块。返回 [(num, [行])]"""
    blocks = []
    cur_num = None
    cur_lines = []
    for t in lines:
        m = re.match(r'^第(\d+)题\s*[:：]?', t)
        if m:
            if cur_num is not None:
                blocks.append((cur_num, cur_lines))
            cur_num = int(m.group(1))
            cur_lines = []
        else:
            if cur_num is not None:
                cur_lines.append(t)
    if cur_num is not None:
        blocks.append((cur_num, cur_lines))
    return blocks

# ---------- 单选：题干 + 选项 ----------
def parse_choice(block):
    """块 = [题干行, 选项行...]。识别 A、B、C、D 前缀；无前缀则按行顺序编号。"""
    lines = block
    stem = lines[0] if lines else ""
    rest = lines[1:]
    opts = []
    prefixed = [ln for ln in rest if re.match(r'^[A-Da-d][\.、．]', ln)]
    if prefixed:
        for ln in rest:
            m = re.match(r'^([A-Da-d])[\.、．]\s*(.*)$', ln)
            if m:
                opts.append({"key": m.group(1).upper(), "text": m.group(2)})
    else:
        # 无前缀：题干后每行一个选项，按 A、B、C... 顺序
        keys = "ABCDEFGH"
        for i, ln in enumerate(rest[:8]):
            if ln and i < len(keys):
                opts.append({"key": keys[i], "text": ln})
    return stem, opts

# ---------- 答案解析 ----------
def parse_answers(lines):
    """返回 {题号: {'raw':..., 'text':...}}。
    支持单行 "第N题 答案：X"(单选/判断) 与 "第N题 答案：" 后多段(简答)。"""
    ans = {}
    cur = None
    for t in lines:
        m = re.match(r'^第(\d+)题\s*答案\s*[:：]\s*(.*)$', t)
        if m:
            num = int(m.group(1))
            rest = m.group(2).strip()
            cur = {"raw": rest, "text": rest}
            ans[num] = cur
            continue
        m2 = re.match(r'^第(\d+)题', t)
        if m2:
            continue          # 新的题头（无答案标记），跳过
        if cur is not None:
            cur["text"] = (cur["text"] + "\n" + t).strip()
    return ans

def build():
    qd = docx.Document(QP)
    ad = docx.Document(AP)
    qsections = split_sections(qd)
    asections = split_sections(ad)

    bank = []
    used_kinds = set()
    for sec in qsections:
        title = sec["title"]
        kind = None
        if "单选题" in title:
            kind = "choice"
        elif "判断题" in title:
            kind = "judge"
        elif "简答" in title or "编程" in title:
            kind = "qa"
        if kind is None:
            continue
        # 找对应答案 section（按标题关键字匹配）
        akw = "单选" if kind == "choice" else ("判断" if kind == "judge" else "简答")
        asec = next((s for s in asections if akw in s["title"]), None)
        answers = parse_answers(asec["lines"]) if asec else {}

        for num, blk in split_questions(sec["lines"]):
            if kind == "choice":
                stem, opts = parse_choice(blk)
                a = answers.get(num, {})
                item = {
                    "id": f"choice-{num}", "kind": "choice", "kind_name": "单选题",
                    "num": num, "stem": stem, "options": opts,
                    "answer": a.get("raw", ""), "explain": a.get("text", ""),
                }
            elif kind == "judge":
                stem = blk[0] if blk else ""
                a = answers.get(num, {})
                item = {
                    "id": f"judge-{num}", "kind": "judge", "kind_name": "判断题",
                    "num": num, "stem": stem, "options": [],
                    "answer": a.get("raw", ""), "explain": a.get("text", ""),
                }
            else:
                stem = "\n".join(blk)
                a = answers.get(num, {})
                item = {
                    "id": f"qa-{num}", "kind": "qa", "kind_name": "简答/编程题",
                    "num": num, "stem": stem, "options": [],
                    "answer": a.get("raw", ""), "explain": a.get("text", ""),
                }
            bank.append(item)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(bank, f, ensure_ascii=False, indent=1)

    # 统计
    cnt = {}
    for it in bank:
        cnt[it["kind"]] = cnt.get(it["kind"], 0) + 1
    print("已生成:", OUT)
    print("题数统计:", {k: v for k, v in cnt.items()}, "共", len(bank), "题")
    # 抽查
    for it in bank[:3] + bank[80:83]:
        print(f"  [{it['kind_name']} {it['num']}] 答案={it['answer']!r}")
        print("    题干:", it["stem"][:60].replace("\n", " "))
        if it["options"]:
            print("    选项:", ", ".join(f"{o['key']}.{o['text'][:20]}" for o in it["options"]))

if __name__ == "__main__":
    build()
