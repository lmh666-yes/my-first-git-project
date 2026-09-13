# -*- coding: utf-8 -*-
"""解析面试题库 md 文件（如 02_主观题.md）为 题库.json 数据。

格式：**N.** 题干 → **参考答案：**（或 **参考译文：**）→ **得分点：** → ---
每题生成 {id, kind:'subjective', num, stem, options:[], answer, explain}：
  · answer  = 参考答案（或参考译文）
  · explain = 得分点
"""
import os
import re
import shutil


def _split_blocks(lines):
    """按 '**N.**' 题号行切块；代码块（```）内的行不切。"""
    blocks, cur, in_code = [], None, False
    for ln in lines:
        s = ln.rstrip()
        if s.strip().startswith("```"):
            in_code = not in_code
        if not in_code:
            m = re.match(r"^\*\*(\d+)\.\*\*\s*(.*)$", s)
            if m:
                if cur is not None:
                    blocks.append(cur)
                cur = {"num": int(m.group(1)), "first": m.group(2), "lines": []}
                continue
        if cur is not None:
            cur["lines"].append(s)
    if cur is not None:
        blocks.append(cur)
    return blocks


def _norm_text(text):
    t = text.replace("**", "")
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _extract_src_links(line):
    """从一行文本中提取 [图...](path) 链接 → [相对路径, ...]"""
    return [m.group(1) for m in re.finditer(r"\[图[^\]]*\]\(([^)]+)\)", line)]


def _sync_images(md_path, bank, problems):
    """把 md 中引用的配图同步到软件 imgs/ 目录（已存在则跳过；找不到源文件告警）"""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    imgdir = os.path.join(root, "imgs")
    rel_map = {}
    with open(md_path, encoding="utf-8") as f:
        for ln in f:
            for rel in _extract_src_links(ln):
                rel_map[os.path.basename(rel)] = rel
    for it in bank:
        for name in it.get("imgs", []):
            dst = os.path.join(imgdir, name)
            if os.path.exists(dst):
                continue
            rel = rel_map.get(name)
            src = os.path.normpath(os.path.join(os.path.dirname(md_path), rel)) if rel else None
            if src and os.path.exists(src):
                os.makedirs(imgdir, exist_ok=True)
                shutil.copy(src, dst)
            else:
                problems.append(f"配图未找到: {name}（请把 面试题md 文件夹与软件放在同一位置）")


def _parse_block(b):
    """解析单个主观题块 → (item, warn)"""
    num, first = b["num"], b["first"]
    stem_lines = [first] if first.strip() else []
    ans_lines, exp_lines, srcs = [], [], []
    phase = "stem"          # stem → ans → explain → done
    in_code = False
    for ln in b["lines"]:
        if ln.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            if phase == "stem":
                stem_lines.append(ln)
            elif phase == "ans":
                ans_lines.append(ln)
            elif phase == "explain":
                exp_lines.append(ln)
            continue
        if ln.strip() == "---" or ln.startswith("#"):
            break
        m_src = re.match(r"^\*\*来源：\*\*\s*(.*)$", ln)
        if m_src:
            srcs += _extract_src_links(m_src.group(1))
            break
        if phase in ("stem", "ans"):
            m_a = re.match(r"^\*\*参考(答案|译文)：\*\*\s*(.*)$", ln)
            if m_a:
                if m_a.group(2).strip():
                    ans_lines.append(m_a.group(2))
                phase = "ans"
                continue
        if phase == "ans":
            m_e = re.match(r"^\*\*得分点：\*\*\s*(.*)$", ln)
            if m_e:
                if m_e.group(1).strip():
                    exp_lines.append(m_e.group(1))
                phase = "explain"
                continue
            if ln.strip():
                ans_lines.append(ln)
            continue
        if phase == "explain":
            if ln.strip():
                exp_lines.append(ln)
            continue
        if phase == "stem" and ln.strip():
            stem_lines.append(ln)

    item = {"id": f"sub-{num}", "kind": "subjective", "kind_name": "主观题",
            "num": num, "stem": _norm_text("\n".join(stem_lines)),
            "options": [], "answer": _norm_text("\n".join(ans_lines)),
            "explain": _norm_text("\n".join(exp_lines)),
            "imgs": [os.path.basename(p) for p in srcs]}
    warn = ""
    if not item["answer"]:
        warn = f"#{num} 缺参考答案"
    elif not item["explain"]:
        warn = f"#{num} 缺得分点"
    return item, warn


def parse_md(path):
    """解析 md 文件 → (题库列表, 告警列表)"""
    if not os.path.exists(path):
        return [], ["文件不存在: " + path]
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().split("\n")
    except Exception as e:
        return [], [f"无法读取文件：{e}"]
    bank, problems = [], []
    for b in _split_blocks(lines):
        item, warn = _parse_block(b)
        if item is not None and item["stem"]:
            bank.append(item)
        if warn:
            problems.append(warn)
    if any(it.get("imgs") for it in bank):
        _sync_images(path, bank, problems)
    return bank, problems


def count(bank):
    """统计题型分布"""
    c = {}
    for it in bank:
        c[it["kind"]] = c.get(it["kind"], 0) + 1
    return c
