#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""临时脚本：重建 func_index.h"""
import re, os
from collections import Counter

BASE = r'd:\github\01函数库1.0\library'
H_PATH = os.path.join(BASE, 'utils.h')
GH_PATH = os.path.join(BASE, 'utils_gen.h')
IDX_PATH = os.path.join(BASE, 'func_index.h')

MACRO_DESC = {
    'UTILS_MIN': '取两个数中较小值', 'UTILS_MAX': '取两个数中较大值',
    'UTILS_ABS': '求绝对值', 'UTILS_ARRAY_SIZE': '求数组元素个数',
    'UTILS_BIT': '生成位掩码（第 n 位为 1）',
    'UTILS_CLAMP': '把数值限制在 [lo, hi] 区间内',
    'UTILS_SWAP': '交换两个变量的值（需指定类型）',
    'UTILS_IS_EVEN': '判断整数是否为偶数', 'UTILS_IS_ODD': '判断整数是否为奇数',
    'UTILS_IS_POW2': '判断正整数是否为 2 的幂',
    'UTILS_SIGN': '返回符号（正 1 / 负 -1 / 零 0）',
    'UTILS_MAX3': '取三个数中最大值', 'UTILS_MIN3': '取三个数中最小值',
    'UTILS_DIV_CEIL': '整数除法向上取整',
    'UTILS_ALIGN_UP': '向上对齐到 a 的整数倍', 'UTILS_ALIGN_DOWN': '向下对齐到 a 的整数倍',
    'UTILS_SET_BIT': '将整数 x 的第 n 位置 1', 'UTILS_CLEAR_BIT': '将整数 x 的第 n 位清 0',
    'UTILS_GET_BIT': '读取整数 x 的第 n 位', 'UTILS_TOGGLE_BIT': '翻转整数 x 的第 n 位',
    'UTILS_SQUARE': '计算平方',
}

def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()

def build_index(h_text):
    lines = h_text.split('\n')
    entries = []
    section = '其他'
    pending = ''
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith('//') and not s.startswith('//='):
            prev = lines[i-1].strip() if i > 0 else ''
            nxt = lines[i+1].strip() if i+1 < len(lines) else ''
            if re.match(r'//\s*=+\s*$', prev) and re.match(r'//\s*=+\s*$', nxt):
                title = s.lstrip('/').strip()
                if title:
                    title = title.replace('（自动生成）', '').strip()
                    if title:
                        section = title
        if s.startswith('/**'):
            inner = s[3:].strip().rstrip('*/').strip()
            if not inner:
                j = i + 1
                while j < len(lines):
                    t = lines[j].strip()
                    if '*/' in t:
                        if not inner:
                            inner = t.split('*/')[0].strip().lstrip('*').strip()
                        break
                    t = t.lstrip('*').strip()
                    if t and not inner:
                        inner = t
                    j += 1
            if inner:
                pending = inner
        elif s.startswith('//') and not s.startswith('//='):
            inner = s.lstrip('/').strip()
            if inner:
                pending = inner
        if s.startswith('#define'):
            m = re.match(r'#define\s+([A-Za-z_]\w*)\s*(\([^)]*\))', s)
            if m:
                name = m.group(1)
                desc = MACRO_DESC.get(name, '宏定义')
                entries.append((name, '常用宏', desc, name + m.group(2)))
                pending = ''
        if s.endswith(';') and '(' in s and ')' in s and not s.startswith('typedef') and not s.startswith('#'):
            names = list(re.finditer(r'([A-Za-z_]\w*)\s*\(', s))
            if names:
                name = names[0].group(1)
                start = s.find(name)
                depth = 0
                end = start
                for k in range(start, len(s)):
                    if s[k] == '(':
                        depth += 1
                    elif s[k] == ')':
                        depth -= 1
                        if depth == 0:
                            end = k
                            break
                example = s[start:end+1].strip()
                desc = pending or section
                entries.append((name, section, desc, example))
                pending = ''
    seen = set()
    uniq = []
    for e in entries:
        if e[0] not in seen:
            seen.add(e[0])
            uniq.append(e)
    return uniq

h_text = read(H_PATH) + '\n// ===== 自动生成区 =====\n' + read(GH_PATH)
entries = build_index(h_text)
names = [e[0] for e in entries]
dup = [n for n, c in Counter(names).items() if c > 1]
print('函数总数:', len(entries))
print('重复名字:', dup if dup else '无')

ilines = []
ilines.append('/* ============================================================')
ilines.append(' *  func_index.h — UTILS 函数库 · 函数索引表（由 gen_functions.py 自动生成）')
ilines.append(' * ============================================================ */')
ilines.append('')
ilines.append('#ifndef FUNC_INDEX_H')
ilines.append('#define FUNC_INDEX_H')
ilines.append('')
ilines.append('typedef struct {')
ilines.append('    const char *name;')
ilines.append('    const char *section;')
ilines.append('    const char *desc;')
ilines.append('    const char *example;')
ilines.append('} FuncInfo;')
ilines.append('')
ilines.append('static const FuncInfo g_funcs[] = {')
for name, section, desc, example in entries:
    def esc(x):
        return x.replace('\\', '\\\\').replace('"', '\\"')
    ilines.append(f'    {{"{esc(name)}", "{esc(section)}", "{esc(desc)}", "{esc(example)}"}},')
ilines.append('};')
ilines.append('')
ilines.append('#define FUNC_COUNT ((int)(sizeof(g_funcs) / sizeof(g_funcs[0])))')
ilines.append('')
ilines.append('#endif /* FUNC_INDEX_H */')

with open(IDX_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(ilines))
print('已重建 func_index.h')
