#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" ============================================================
    gen_functions.py — UTILS 函数库批量生成器
    ------------------------------------------------------------
    功能：
      1. 按"函数族"批量生成真实可用的 C 函数（类型变体 + 各领域分类），
         将 utils 函数库扩充到 1000+ 个函数。
      2. 自动把新函数声明写入 utils.h、实现写入 utils.c。
      3. 自动解析 utils.h 重建 func_index.h（查找工具使用的索引表）。
    用法：在 lib 目录下执行  py gen_functions.py
    ============================================================ """
import re, os

BASE = os.path.dirname(os.path.abspath(__file__))
H_PATH = os.path.join(BASE, 'utils.h')
C_PATH = os.path.join(BASE, 'utils.c')
IDX_PATH = os.path.join(BASE, 'func_index.h')

def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()

def write(p, s):
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)

def existing_names():
    t = read(H_PATH)
    names = set()
    for m in re.finditer(r'([A-Za-z_]\w*)\s*\(', t):
        names.add(m.group(1))
    return names

def clean_previous():
    """移除 utils.h / utils.c 中上次自动生成的内容，保证可重复运行"""
    # utils.h：删除"include 块之后、第一个 #ifdef __cplusplus 之前"的自动生成内容
    h = read(H_PATH)
    inc_marker = '#include <stdint.h>\n'
    inc_idx = h.find(inc_marker)
    inc_end = inc_idx + len(inc_marker) if inc_idx >= 0 else 0
    if_idx = h.find('#ifdef __cplusplus')
    if if_idx > inc_end:
        h = h[:inc_end] + h[if_idx:]
        write(H_PATH, h)
        print('[清理] utils.h 已移除上次自动生成的内容')
    # utils.c：截断到自动生成起始标记
    c = read(C_PATH)
    banner = c.find('以下函数由 gen_functions.py 自动生成')
    if banner >= 0:
        line_start = c.rfind('\n', 0, banner)
        c = c[:line_start] + '\n'
        write(C_PATH, c)
        print('[清理] utils.c 已移除上次自动生成的内容')

GENERATED = []  # (section, desc, ret, name, params, body_lines)

def add(section, desc, ret, name, params, body):
    if name in EXISTING:
        print(f'  [跳过] {name} 已存在')
        return
    GENERATED.append((section, desc, ret, name, params, body))

def simple(section, desc, ret, name, params, *body):
    add(section, desc, ret, name, params, list(body))

# ============================================================
#  1. 数组工具（类型扩展）：int/long/ll/short/uint/float/double/char/u8/u16/u32
# ============================================================
def family_array():
    TYPES = [
        ('int','int','%d','long long','int',''),
        ('long','long','%ld','long long','int',''),
        ('long_long','long long','%lld','long long','int',''),
        ('short','short','%d','long long','int',''),
        ('uint','unsigned int','%u','unsigned long long','uint',''),
        ('float','float','%.2f','double','float',''),
        ('double','double','%.2f','double','float',''),
        ('char','char','%c','int','int',''),
        ('uint8','uint8_t','%u','unsigned long long','uint','(unsigned)'),
        ('uint16','uint16_t','%u','unsigned long long','uint','(unsigned)'),
        ('uint32','uint32_t','%u','unsigned long long','uint',''),
    ]
    SEC = '数组工具(类型扩展)'
    for suf, T, F, SUM, CAT, CAST in TYPES:
        is_f = (CAT == 'float')
        is_u = (CAT == 'uint')
        absb = 'fabs(v)' if is_f else 'UTILS_ABS(v)'
        abs0 = 'fabs(arr[0])' if is_f else 'UTILS_ABS(arr[0])'
        abs_i = 'fabs(arr[i])' if is_f else 'UTILS_ABS(arr[i])'   # 修复：循环里取 arr[i] 而非自引用 v
        add(SEC, '打印数组元素', 'void', f'print_{suf}_array', f'{T} arr[], int size',
            [f'for (int i = 0; i < size; i++) printf("{F} ", {CAST}arr[i]);', 'printf("\\n");'])
        add(SEC, '数组元素求和', SUM, f'sum_{suf}_array', f'{T} arr[], int size',
            [f'{SUM} s = 0;', 'for (int i = 0; i < size; i++) s += arr[i];', 'return s;'])
        add(SEC, '数组平均值', 'double', f'avg_{suf}_array', f'{T} arr[], int size',
            ['if (size == 0) return 0.0;', f'{SUM} s = 0;', 'for (int i = 0; i < size; i++) s += arr[i];',
             'return (double)s / size;'])
        add(SEC, '数组最大值', T, f'max_{suf}_array', f'{T} arr[], int size',
            [f'{T} m = arr[0];', 'for (int i = 1; i < size; i++) if (arr[i] > m) m = arr[i];', 'return m;'])
        add(SEC, '数组最小值', T, f'min_{suf}_array', f'{T} arr[], int size',
            [f'{T} m = arr[0];', 'for (int i = 1; i < size; i++) if (arr[i] < m) m = arr[i];', 'return m;'])
        add(SEC, '用指定值填充数组', 'void', f'fill_{suf}_array', f'{T} arr[], int size, {T} value',
            ['for (int i = 0; i < size; i++) arr[i] = value;'])
        add(SEC, '反转数组', 'void', f'reverse_{suf}_array', f'{T} arr[], int size',
            ['for (int i = 0; i < size / 2; i++) {',
             f'    {T} t = arr[i]; arr[i] = arr[size - 1 - i]; arr[size - 1 - i] = t;', '}'])
        add(SEC, '查找元素下标', 'int', f'find_{suf}_array', f'{T} arr[], int size, {T} target',
            ['for (int i = 0; i < size; i++) if (arr[i] == target) return i;', 'return -1;'])
        add(SEC, '统计元素出现次数', 'int', f'count_{suf}_array', f'{T} arr[], int size, {T} target',
            ['int c = 0;', 'for (int i = 0; i < size; i++) if (arr[i] == target) c++;', 'return c;'])
        add(SEC, '数组元素乘积', SUM, f'product_{suf}_array', f'{T} arr[], int size',
            [f'{SUM} p = 1;', 'for (int i = 0; i < size; i++) p *= arr[i];', 'return p;'])
        add(SEC, '复制数组(需free)', f'{T}*', f'copy_{suf}_array', f'{T} arr[], int size',
            [f'{T} *r = ({T}*)malloc(size * sizeof({T}));', 'if (!r) return NULL;',
             f'memcpy(r, arr, size * sizeof({T}));', 'return r;'])
        if not is_u:
            add(SEC, '最大绝对值', T, f'max_abs_{suf}_array', f'{T} arr[], int size',
                [f'{T} m = {abs0};', 'for (int i = 1; i < size; i++) {',
                 f'    {T} v = {abs_i};', '    if (v > m) m = v;', '}', 'return m;'])
            add(SEC, '最小绝对值', T, f'min_abs_{suf}_array', f'{T} arr[], int size',
                [f'{T} m = {abs0};', 'for (int i = 1; i < size; i++) {',
                 f'    {T} v = {abs_i};', '    if (v < m) m = v;', '}', 'return m;'])
        add(SEC, '第二大元素', T, f'second_max_{suf}_array', f'{T} arr[], int size',
            ['if (size < 2) return (size > 0) ? arr[0] : 0;',
             f'{T} m1 = arr[0], m2 = arr[1];',
             f'if (m2 > m1) {{ {T} t = m1; m1 = m2; m2 = t; }}',
             'for (int i = 2; i < size; i++) {',
             '    if (arr[i] > m1) { m2 = m1; m1 = arr[i]; }',
             '    else if (arr[i] > m2 && arr[i] != m1) m2 = arr[i];',
             '}', 'return m2;'])
        add(SEC, '第二小元素', T, f'second_min_{suf}_array', f'{T} arr[], int size',
            ['if (size < 2) return (size > 0) ? arr[0] : 0;',
             f'{T} m1 = arr[0], m2 = arr[1];',
             f'if (m2 < m1) {{ {T} t = m1; m1 = m2; m2 = t; }}',
             'for (int i = 2; i < size; i++) {',
             '    if (arr[i] < m1) { m2 = m1; m1 = arr[i]; }',
             '    else if (arr[i] < m2 && arr[i] != m1) m2 = arr[i];',
             '}', 'return m2;'])
        add(SEC, '判断数组是否升序', 'int', f'is_sorted_asc_{suf}_array', f'{T} arr[], int size',
            ['for (int i = 1; i < size; i++) if (arr[i] < arr[i - 1]) return 0;', 'return 1;'])
        add(SEC, '判断数组是否降序', 'int', f'is_sorted_desc_{suf}_array', f'{T} arr[], int size',
            ['for (int i = 1; i < size; i++) if (arr[i] > arr[i - 1]) return 0;', 'return 1;'])

# ============================================================
#  2. 数组统计
# ============================================================
def family_stat():
    SEC = '数组统计'
    simple(SEC, '平均值(double数组)', 'double', 'mean_double_array', 'double arr[], int size',
           'if (size == 0) return 0.0;', 'double s = 0;', 'for (int i = 0; i < size; i++) s += arr[i];', 'return s / size;')
    simple(SEC, '中位数(double数组)', 'double', 'median_double_array', 'double arr[], int size',
           'if (size == 0) return 0.0;', 'double *c = (double*)malloc(size * sizeof(double));', 'if (!c) return 0.0;',
           'memcpy(c, arr, size * sizeof(double));',
           'for (int i = 0; i < size - 1; i++) for (int j = 0; j < size - 1 - i; j++) if (c[j] > c[j + 1]) { double t = c[j]; c[j] = c[j + 1]; c[j + 1] = t; }',
           'double r = (size % 2) ? c[size / 2] : (c[size / 2 - 1] + c[size / 2]) / 2.0;', 'free(c);', 'return r;')
    simple(SEC, '众数(int数组，返回出现最多的值)', 'int', 'mode_int_array', 'int arr[], int size',
           'int best = arr[0], bestc = 0;',
           'for (int i = 0; i < size; i++) { int c = 0; for (int j = 0; j < size; j++) if (arr[j] == arr[i]) c++; if (c > bestc) { bestc = c; best = arr[i]; } }',
           'return best;')
    simple(SEC, '方差(double数组)', 'double', 'variance_double_array', 'double arr[], int size',
           'if (size < 1) return 0.0;', 'double m = mean_double_array(arr, size), s = 0;',
           'for (int i = 0; i < size; i++) { double d = arr[i] - m; s += d * d; }', 'return s / size;')
    simple(SEC, '标准差(double数组)', 'double', 'stddev_double_array', 'double arr[], int size',
           'return sqrt(variance_double_array(arr, size));')
    simple(SEC, '极差(最大值-最小值)', 'double', 'range_double_array', 'double arr[], int size',
           'if (size < 1) return 0.0;', 'double mx = arr[0], mn = arr[0];',
           'for (int i = 1; i < size; i++) { if (arr[i] > mx) mx = arr[i]; if (arr[i] < mn) mn = arr[i]; }',
           'return mx - mn;')
    simple(SEC, '分位数(p为0~1)', 'double', 'percentile_double_array', 'double arr[], int size, double p',
           'if (size < 1) return 0.0;', 'double *c = (double*)malloc(size * sizeof(double));', 'if (!c) return 0.0;',
           'memcpy(c, arr, size * sizeof(double));',
           'for (int i = 0; i < size - 1; i++) for (int j = 0; j < size - 1 - i; j++) if (c[j] > c[j + 1]) { double t = c[j]; c[j] = c[j + 1]; c[j + 1] = t; }',
           'int idx = (int)(p * (size - 1));', 'double r = c[idx];', 'free(c);', 'return r;')
    simple(SEC, '几何平均数', 'double', 'geometric_mean_double', 'double arr[], int size',
           'if (size < 1) return 0.0;', 'double p = 1.0;', 'for (int i = 0; i < size; i++) p *= arr[i];',
           'return pow(p, 1.0 / size);')
    simple(SEC, '调和平均数', 'double', 'harmonic_mean_double', 'double arr[], int size',
           'if (size < 1) return 0.0;', 'double s = 0.0;', 'for (int i = 0; i < size; i++) s += 1.0 / arr[i];',
           'return size / s;')

# ============================================================
#  3. 数组查询与谓词
# ============================================================
def family_query():
    SEC = '数组查询与谓词'
    simple(SEC, '数组是否有重复', 'int', 'has_duplicates_int', 'int arr[], int size',
           'for (int i = 0; i < size; i++) for (int j = i + 1; j < size; j++) if (arr[i] == arr[j]) return 1;', 'return 0;')
    simple(SEC, '数组是否全部为正', 'int', 'all_positive_int', 'int arr[], int size',
           'for (int i = 0; i < size; i++) if (arr[i] <= 0) return 0;', 'return 1;')
    simple(SEC, '数组是否全部为负', 'int', 'all_negative_int', 'int arr[], int size',
           'for (int i = 0; i < size; i++) if (arr[i] >= 0) return 0;', 'return 1;')
    simple(SEC, '数组是否全部为偶数', 'int', 'all_even_int', 'int arr[], int size',
           'for (int i = 0; i < size; i++) if (arr[i] % 2) return 0;', 'return 1;')
    simple(SEC, '数组是否全部为奇数', 'int', 'all_odd_int', 'int arr[], int size',
           'for (int i = 0; i < size; i++) if (arr[i] % 2 == 0) return 0;', 'return 1;')
    simple(SEC, '统计大于 value 的元素个数', 'int', 'count_greater_int', 'int arr[], int size, int value',
           'int c = 0;', 'for (int i = 0; i < size; i++) if (arr[i] > value) c++;', 'return c;')
    simple(SEC, '统计小于 value 的元素个数', 'int', 'count_less_int', 'int arr[], int size, int value',
           'int c = 0;', 'for (int i = 0; i < size; i++) if (arr[i] < value) c++;', 'return c;')
    simple(SEC, '统计区间 [lo,hi] 内元素个数', 'int', 'count_between_int', 'int arr[], int size, int lo, int hi',
           'int c = 0;', 'for (int i = 0; i < size; i++) if (arr[i] >= lo && arr[i] <= hi) c++;', 'return c;')
    simple(SEC, '统计偶数个数', 'int', 'count_even_int', 'int arr[], int size',
           'int c = 0;', 'for (int i = 0; i < size; i++) if (arr[i] % 2 == 0) c++;', 'return c;')
    simple(SEC, '统计奇数个数', 'int', 'count_odd_int', 'int arr[], int size',
           'int c = 0;', 'for (int i = 0; i < size; i++) if (arr[i] % 2) c++;', 'return c;')
    simple(SEC, '统计正数个数', 'int', 'count_positive_int', 'int arr[], int size',
           'int c = 0;', 'for (int i = 0; i < size; i++) if (arr[i] > 0) c++;', 'return c;')
    simple(SEC, '统计负数个数', 'int', 'count_negative_int', 'int arr[], int size',
           'int c = 0;', 'for (int i = 0; i < size; i++) if (arr[i] < 0) c++;', 'return c;')
    simple(SEC, '统计零元素个数', 'int', 'count_zero_int', 'int arr[], int size',
           'int c = 0;', 'for (int i = 0; i < size; i++) if (arr[i] == 0) c++;', 'return c;')
    simple(SEC, '数组是否包含 value', 'int', 'contains_int', 'int arr[], int size, int value',
           'for (int i = 0; i < size; i++) if (arr[i] == value) return 1;', 'return 0;')
    simple(SEC, '两个数组是否相等', 'int', 'arrays_equal_int', 'int a[], int b[], int size',
           'for (int i = 0; i < size; i++) if (a[i] != b[i]) return 0;', 'return 1;')
    simple(SEC, 'a 是否为 b 的子集', 'int', 'is_subset_int', 'int a[], int na, int b[], int nb',
           'for (int i = 0; i < na; i++) { int f = 0; for (int j = 0; j < nb; j++) if (a[i] == b[j]) { f = 1; break; } if (!f) return 0; }',
           'return 1;')
    simple(SEC, '出现次数最多的元素', 'int', 'most_frequent_int', 'int arr[], int size',
           'int best = arr[0], bestc = 0;',
           'for (int i = 0; i < size; i++) { int c = 0; for (int j = 0; j < size; j++) if (arr[j] == arr[i]) c++; if (c > bestc) { bestc = c; best = arr[i]; } }',
           'return best;')

# ============================================================
#  4. 数组变换
# ============================================================
def family_transform():
    SEC = '数组变换'
    simple(SEC, '每个元素平方(原地)', 'void', 'map_square_int', 'int arr[], int size',
           'for (int i = 0; i < size; i++) arr[i] = arr[i] * arr[i];')
    simple(SEC, '每个元素取反(原地)', 'void', 'map_negate_int', 'int arr[], int size',
           'for (int i = 0; i < size; i++) arr[i] = -arr[i];')
    simple(SEC, '每个元素翻倍(原地)', 'void', 'map_double_int', 'int arr[], int size',
           'for (int i = 0; i < size; i++) arr[i] *= 2;')
    simple(SEC, '每个元素加 offset', 'void', 'map_add_int', 'int arr[], int size, int offset',
           'for (int i = 0; i < size; i++) arr[i] += offset;')
    simple(SEC, '数组裁剪到 [lo,hi]', 'void', 'clip_array_int', 'int arr[], int size, int lo, int hi',
           'for (int i = 0; i < size; i++) { if (arr[i] < lo) arr[i] = lo; if (arr[i] > hi) arr[i] = hi; }')
    simple(SEC, '前缀和(原地覆盖)', 'void', 'cumulative_sum_int', 'int arr[], int size',
           'for (int i = 1; i < size; i++) arr[i] += arr[i - 1];')
    simple(SEC, '前缀积(原地覆盖)', 'void', 'cumulative_product_int', 'int arr[], int size',
           'for (int i = 1; i < size; i++) arr[i] *= arr[i - 1];')
    simple(SEC, '前缀最小值(原地覆盖)', 'void', 'prefix_min_int', 'int arr[], int size',
           'for (int i = 1; i < size; i++) if (arr[i] > arr[i - 1]) arr[i] = arr[i - 1];')
    simple(SEC, '前缀最大值(原地覆盖)', 'void', 'prefix_max_int', 'int arr[], int size',
           'for (int i = 1; i < size; i++) if (arr[i] < arr[i - 1]) arr[i] = arr[i - 1];')
    simple(SEC, '相邻元素差分(原地)', 'void', 'differences_int', 'int arr[], int size',
           'for (int i = size - 1; i > 0; i--) arr[i] = arr[i] - arr[i - 1];')
    simple(SEC, '拼接两个数组(需free)', 'int*', 'concat_int_arrays', 'int a[], int na, int b[], int nb, int *out_size',
           'int *r = (int*)malloc((na + nb) * sizeof(int));', 'if (!r) return NULL;',
           'memcpy(r, a, na * sizeof(int));', 'memcpy(r + na, b, nb * sizeof(int));', '*out_size = na + nb;', 'return r;')

# ============================================================
#  5. 排序算法补充
# ============================================================
def family_sort():
    SEC = '排序算法(补充)'
    simple(SEC, '希尔排序', 'void', 'shell_sort', 'int arr[], int size',
           'for (int gap = size / 2; gap > 0; gap /= 2)',
           '    for (int i = gap; i < size; i++) { int t = arr[i], j; for (j = i; j >= gap && arr[j - gap] > t; j -= gap) arr[j] = arr[j - gap]; arr[j] = t; }')
    simple(SEC, '鸡尾酒排序', 'void', 'cocktail_sort', 'int arr[], int size',
           'int lo = 0, hi = size - 1, swapped = 1;',
           'while (swapped) { swapped = 0;',
           '    for (int i = lo; i < hi; i++) if (arr[i] > arr[i + 1]) { int t = arr[i]; arr[i] = arr[i + 1]; arr[i + 1] = t; swapped = 1; }',
           '    hi--;',
           '    for (int i = hi; i > lo; i--) if (arr[i] < arr[i - 1]) { int t = arr[i]; arr[i] = arr[i - 1]; arr[i - 1] = t; swapped = 1; }',
           '    lo++;', '}')
    simple(SEC, '侏儒排序', 'void', 'gnome_sort', 'int arr[], int size',
           'int i = 0;', 'while (i < size) { if (i == 0 || arr[i - 1] <= arr[i]) i++; else { int t = arr[i]; arr[i] = arr[i - 1]; arr[i - 1] = t; i--; } }')
    simple(SEC, '梳排序', 'void', 'comb_sort', 'int arr[], int size',
           'int gap = size, swapped = 1;', 'while (gap > 1 || swapped) {',
           '    gap = (gap * 10) / 13; if (gap < 1) gap = 1; swapped = 0;',
           '    for (int i = 0; i + gap < size; i++) if (arr[i] > arr[i + gap]) { int t = arr[i]; arr[i] = arr[i + gap]; arr[i + gap] = t; swapped = 1; }',
           '}')
    simple(SEC, '圈排序', 'void', 'cycle_sort', 'int arr[], int size',
           'for (int start = 0; start < size - 1; start++) {',
           '    int item = arr[start], pos = start;',
           '    for (int i = start + 1; i < size; i++) if (arr[i] < item) pos++;',
           '    if (pos == start) continue;',
           '    while (item == arr[pos]) pos++;',
           '    int t = arr[pos]; arr[pos] = item; item = t;',
           '    while (pos != start) { pos = start;',
           '        for (int i = start + 1; i < size; i++) if (arr[i] < item) pos++;',
           '        while (item == arr[pos]) pos++;',
           '        t = arr[pos]; arr[pos] = item; item = t;', '}', '}')
    simple(SEC, '计数排序(值域0~max_val)', 'void', 'counting_sort', 'int arr[], int size, int max_val',
           'int *cnt = (int*)calloc(max_val + 1, sizeof(int));', 'if (!cnt) return;',
           'for (int i = 0; i < size; i++) cnt[arr[i]]++;',
           'int k = 0;', 'for (int v = 0; v <= max_val; v++) for (int j = 0; j < cnt[v]; j++) arr[k++] = v;',
           'free(cnt);')
    simple(SEC, '基数排序', 'void', 'radix_sort', 'int arr[], int size',
           'int mx = 0; for (int i = 0; i < size; i++) if (arr[i] > mx) mx = arr[i];',
           'int *out = (int*)malloc(size * sizeof(int)); if (!out) return;',
           'for (int exp = 1; mx / exp > 0; exp *= 10) {',
           '    int cnt[10] = {0};',
           '    for (int i = 0; i < size; i++) cnt[(arr[i] / exp) % 10]++;',
           '    for (int i = 1; i < 10; i++) cnt[i] += cnt[i - 1];',
           '    for (int i = size - 1; i >= 0; i--) out[--cnt[(arr[i] / exp) % 10]] = arr[i];',
           '    for (int i = 0; i < size; i++) arr[i] = out[i];', '}',
           'free(out);')
    simple(SEC, '双调排序', 'void', 'bitonic_sort', 'int arr[], int size',
           'for (int k = 2; k <= size; k *= 2)', '    for (int j = k / 2; j > 0; j /= 2)',
           '        for (int i = 0; i < size; i++) { int l = i ^ j; if (l > i) {',
           '            int asc = ((i & k) == 0);',
           '            if ((asc && arr[i] > arr[l]) || (!asc && arr[i] < arr[l])) { int t = arr[i]; arr[i] = arr[l]; arr[l] = t; }', '} }')

# ============================================================
#  6. 查找算法补充
# ============================================================
def family_search():
    SEC = '查找算法(补充)'
    simple(SEC, '下界：第一个 >= target 的下标', 'int', 'lower_bound_int', 'int arr[], int size, int target',
           'int lo = 0, hi = size;', 'while (lo < hi) { int mid = lo + (hi - lo) / 2; if (arr[mid] < target) lo = mid + 1; else hi = mid; }',
           'return lo;')
    simple(SEC, '上界：第一个 > target 的下标', 'int', 'upper_bound_int', 'int arr[], int size, int target',
           'int lo = 0, hi = size;', 'while (lo < hi) { int mid = lo + (hi - lo) / 2; if (arr[mid] <= target) lo = mid + 1; else hi = mid; }',
           'return lo;')
    simple(SEC, '指数查找(升序)', 'int', 'exponential_search', 'int arr[], int size, int target',
           'if (size == 0) return -1;', 'if (arr[0] == target) return 0;', 'int i = 1;',
           'while (i < size && arr[i] <= target) i *= 2;',
           'int lo = i / 2, hi = (i < size) ? i : size - 1;',
           'while (lo <= hi) { int mid = lo + (hi - lo) / 2; if (arr[mid] == target) return mid; if (arr[mid] < target) lo = mid + 1; else hi = mid - 1; }',
           'return -1;')
    simple(SEC, '跳跃查找(升序，步长 sqrt)', 'int', 'jump_search', 'int arr[], int size, int target',
           'if (size == 0) return -1;', 'int step = (int)sqrt(size), prev = 0;',
           'while (arr[(step < size ? step : size) - 1] < target) { prev = step; step += (int)sqrt(size); if (prev >= size) return -1; }',
           'for (int i = prev; i < (step < size ? step : size); i++) if (arr[i] == target) return i;', 'return -1;')
    simple(SEC, '三分查找(单峰数组最大值)', 'double', 'ternary_search_max', 'double arr[], int size',
           'int lo = 0, hi = size - 1;',
           'while (hi - lo > 2) { int m1 = lo + (hi - lo) / 3, m2 = hi - (hi - lo) / 3; if (arr[m1] < arr[m2]) lo = m1; else hi = m2; }',
           'double best = arr[lo]; for (int i = lo + 1; i <= hi; i++) if (arr[i] > best) best = arr[i]; return best;')
    simple(SEC, '浮点二分查找(升序)', 'int', 'binary_search_double', 'double arr[], int size, double target',
           'int lo = 0, hi = size - 1;',
           'while (lo <= hi) { int mid = lo + (hi - lo) / 2; if (arr[mid] == target) return mid; if (arr[mid] < target) lo = mid + 1; else hi = mid - 1; }',
           'return -1;')
    simple(SEC, '线性查找全部匹配下标(需free)', 'int*', 'find_all_int', 'int arr[], int size, int target, int *count',
           '*count = 0;', 'for (int i = 0; i < size; i++) if (arr[i] == target) (*count)++;',
           'int *r = (int*)malloc(*count * sizeof(int));', 'if (!r) { *count = 0; return NULL; }',
           'int k = 0;', 'for (int i = 0; i < size; i++) if (arr[i] == target) r[k++] = i;', 'return r;')

# ============================================================
#  7. 字符串工具（扩展）
# ============================================================
def family_string():
    SEC = '字符串工具(扩展)'
    simple(SEC, '返回大写副本(需free)', 'char*', 'str_upper_copy', 'const char *str',
           'if (!str) return NULL;', 'char *r = (char*)malloc(str_len(str) + 1);', 'if (!r) return NULL;',
           'int i = 0;', 'while (str[i]) { r[i] = char_to_upper(str[i]); i++; }', 'r[i] = \'\\0\';', 'return r;')
    simple(SEC, '返回小写副本(需free)', 'char*', 'str_lower_copy', 'const char *str',
           'if (!str) return NULL;', 'char *r = (char*)malloc(str_len(str) + 1);', 'if (!r) return NULL;',
           'int i = 0;', 'while (str[i]) { r[i] = char_to_lower(str[i]); i++; }', 'r[i] = \'\\0\';', 'return r;')
    simple(SEC, '返回反转副本(需free)', 'char*', 'str_reverse_copy', 'const char *str',
           'if (!str) return NULL;', 'int n = str_len(str);', 'char *r = (char*)malloc(n + 1);', 'if (!r) return NULL;',
           'for (int i = 0; i < n; i++) r[i] = str[n - 1 - i];', 'r[n] = \'\\0\';', 'return r;')
    simple(SEC, '返回去空格副本(需free)', 'char*', 'str_trim_copy', 'const char *str',
           'if (!str) return NULL;', 'char *r = (char*)malloc(str_len(str) + 1);', 'if (!r) return NULL;',
           'str_copy(r, str);', 'trim(r);', 'return r;')
    simple(SEC, '左侧补齐到 length 位', 'void', 'str_pad_left', 'char *buf, int buf_size, char pad, int length',
           'int n = str_len(buf);', 'if (n >= length || buf_size <= length) return;',
           'int shift = length - n;', 'for (int i = n; i >= 0; i--) buf[i + shift] = buf[i];',
           'for (int i = 0; i < shift; i++) buf[i] = pad;')
    simple(SEC, '右侧补齐到 length 位', 'void', 'str_pad_right', 'char *buf, int buf_size, char pad, int length',
           'int n = str_len(buf);', 'if (n >= length || buf_size <= length) return;',
           'for (int i = n; i < length; i++) buf[i] = pad;', 'buf[length] = \'\\0\';')
    simple(SEC, '截断到 max_len', 'void', 'str_truncate', 'char *str, int max_len',
           'if (max_len < 0) return;', 'int n = str_len(str);', 'if (n > max_len) str[max_len] = \'\\0\';')
    simple(SEC, '重复字符串 times 次写入 buf', 'void', 'str_repeat', 'char *buf, int buf_size, const char *str, int times',
           'int n = str_len(str);', 'int k = 0;', 'for (int t = 0; t < times && k < buf_size - 1; t++)',
           '    for (int i = 0; i < n && k < buf_size - 1; i++) buf[k++] = str[i];',
           'buf[k] = \'\\0\';')
    simple(SEC, '统计子串出现次数', 'int', 'str_count_substr', 'const char *str, const char *sub',
           'int c = 0, n = str_len(sub);', 'if (n == 0) return 0;', 'const char *p = str;',
           'while ((p = str_find(p, sub)) != NULL) { c++; p += n; }', 'return c;')
    simple(SEC, '判断是否全为字母', 'int', 'str_is_alpha', 'const char *str',
           'if (!str || !*str) return 0;', 'while (*str) { if (!is_alpha_char(*str)) return 0; str++; }', 'return 1;')
    simple(SEC, '判断是否全为数字', 'int', 'str_is_digit', 'const char *str',
           'if (!str || !*str) return 0;', 'while (*str) { if (!is_digit_char(*str)) return 0; str++; }', 'return 1;')
    simple(SEC, '判断是否全为字母数字', 'int', 'str_is_alnum', 'const char *str',
           'if (!str || !*str) return 0;', 'while (*str) { if (!is_alnum_char(*str)) return 0; str++; }', 'return 1;')
    simple(SEC, '判断是否全为小写', 'int', 'str_is_lower', 'const char *str',
           'if (!str || !*str) return 0;', 'while (*str) { if (is_upper_char(*str)) return 0; str++; }', 'return 1;')
    simple(SEC, '判断是否全为大写', 'int', 'str_is_upper', 'const char *str',
           'if (!str || !*str) return 0;', 'while (*str) { if (is_lower_char(*str)) return 0; str++; }', 'return 1;')
    simple(SEC, '大小写互换(原地)', 'void', 'str_swap_case', 'char *str',
           'while (*str) { if (is_upper_char(*str)) *str = char_to_lower(*str); else if (is_lower_char(*str)) *str = char_to_upper(*str); str++; }')
    simple(SEC, '单词首字母大写(原地)', 'void', 'str_title_case', 'char *str',
           'int cap = 1;', 'while (*str) { if (is_alpha_char(*str)) { if (cap) *str = char_to_upper(*str); else *str = char_to_lower(*str); cap = 0; } else if (*str == \' \') cap = 1; str++; }')
    simple(SEC, '删除所有空白字符(原地)', 'void', 'str_remove_whitespace', 'char *str',
           'char *w = str;', 'while (*str) { if (!is_space_char(*str)) *w++ = *str; str++; }', '*w = \'\\0\';')
    simple(SEC, '删除所有元音(原地)', 'void', 'str_remove_vowels', 'char *str',
           'char *w = str;', 'while (*str) { if (!is_vowel_char(*str)) *w++ = *str; str++; }', '*w = \'\\0\';')
    simple(SEC, '是否互为字母异位词', 'int', 'str_are_anagrams', 'const char *a, const char *b',
           'int ca[26] = {0}, cb[26] = {0};',
           'while (*a) { if (is_alpha_char(*a)) ca[char_to_lower(*a) - \'a\']++; a++; }',
           'while (*b) { if (is_alpha_char(*b)) cb[char_to_lower(*b) - \'a\']++; b++; }',
           'for (int i = 0; i < 26; i++) if (ca[i] != cb[i]) return 0;', 'return 1;')
    simple(SEC, '是否为子序列', 'int', 'str_is_subsequence', 'const char *s, const char *t',
           'while (*s && *t) { if (*s == *t) s++; t++; }', 'return (*s == \'\\0\');')
    simple(SEC, '取前 n 个字符', 'char*', 'str_left', 'const char *str, int n, char *buf, int buf_size',
           'return str_substr(str, 0, n, buf, buf_size);')
    simple(SEC, '取后 n 个字符', 'char*', 'str_right', 'const char *str, int n, char *buf, int buf_size',
           'int len = str_len(str);', 'int start = (n >= len) ? 0 : len - n;', 'return str_substr(str, start, len - start, buf, buf_size);')
    simple(SEC, '统计行数', 'int', 'str_count_lines', 'const char *str',
           'int c = 0;', 'while (*str) { if (*str == \'\\n\') c++; str++; }', 'return c;')
    simple(SEC, '最长单词长度', 'int', 'str_longest_word_len', 'const char *str',
           'int best = 0, cur = 0;', 'while (*str) { if (is_space_char(*str)) { if (cur > best) best = cur; cur = 0; } else cur++; str++; }',
           'if (cur > best) best = cur;', 'return best;')
    simple(SEC, '出现最多的字符', 'char', 'str_most_common_char', 'const char *str',
           'int cnt[256] = {0};', 'while (*str) cnt[(unsigned char)*str++]++;',
           'char best = 0; int bc = 0;', 'for (int i = 0; i < 256; i++) if (cnt[i] > bc) { bc = cnt[i]; best = (char)i; }', 'return best;')
    simple(SEC, '统计元音个数', 'int', 'str_count_vowels', 'const char *str',
           'int c = 0;', 'while (*str) { if (is_vowel_char(*str)) c++; str++; }', 'return c;')
    simple(SEC, '凯撒加密(原地)', 'void', 'str_caesar_shift', 'char *str, int shift',
           'while (*str) { if (is_alpha_char(*str)) { char base = is_upper_char(*str) ? \'A\' : \'a\'; *str = (char)(base + (*str - base + shift % 26 + 26) % 26); } str++; }')
    simple(SEC, 'ROT13 加密(原地)', 'void', 'str_rot13', 'char *str',
           'while (*str) { if (is_alpha_char(*str)) { char base = is_upper_char(*str) ? \'A\' : \'a\'; *str = (char)(base + (*str - base + 13) % 26); } str++; }')

# ============================================================
#  8. 字符工具
# ============================================================
def family_char():
    SEC = '字符工具'
    simple(SEC, '是否大写字母', 'int', 'is_upper_char', 'char c', 'return (c >= \'A\' && c <= \'Z\');')
    simple(SEC, '是否小写字母', 'int', 'is_lower_char', 'char c', 'return (c >= \'a\' && c <= \'z\');')
    simple(SEC, '是否十六进制字符', 'int', 'is_hex_char', 'char c', 'return is_digit_char(c) || (c >= \'a\' && c <= \'f\') || (c >= \'A\' && c <= \'F\');')
    simple(SEC, '是否八进制字符', 'int', 'is_octal_char', 'char c', 'return (c >= \'0\' && c <= \'7\');')
    simple(SEC, '是否可打印字符', 'int', 'is_printable_char', 'char c', 'return (c >= 32 && c < 127);')
    simple(SEC, '是否标点字符', 'int', 'is_punctuation_char', 'char c', 'return is_printable_char(c) && !is_alnum_char(c) && !is_space_char(c);')
    simple(SEC, '是否元音', 'int', 'is_vowel_char', 'char c',
           'c = char_to_lower(c);', 'return (c == \'a\' || c == \'e\' || c == \'i\' || c == \'o\' || c == \'u\');')
    simple(SEC, '是否辅音', 'int', 'is_consonant_char', 'char c', 'return is_alpha_char(c) && !is_vowel_char(c);')
    simple(SEC, '下一个字符', 'char', 'next_char', 'char c', 'return (char)(c + 1);')
    simple(SEC, '上一个字符', 'char', 'prev_char', 'char c', 'return (char)(c - 1);')
    simple(SEC, '字符循环右移 n', 'char', 'char_rotate', 'char c, int n',
           'if (!is_alpha_char(c)) return c;', 'char base = is_upper_char(c) ? \'A\' : \'a\';', 'return (char)(base + (c - base + n % 26 + 26) % 26);')
    simple(SEC, '数字字符转数值', 'int', 'digit_char_to_int', 'char c', 'return is_digit_char(c) ? (c - \'0\') : -1;')
    simple(SEC, '数值转数字字符(0~9)', 'char', 'int_to_digit_char', 'int v', 'return (v >= 0 && v <= 9) ? (char)(\'0\' + v) : \'?\';')

# ============================================================
#  9. 数论与数学(扩展)
# ============================================================
def family_math():
    SEC = '数论与数学(扩展)'
    simple(SEC, '是否偶数', 'int', 'is_even', 'int n', 'return (n % 2 == 0);')
    simple(SEC, '是否奇数', 'int', 'is_odd', 'int n', 'return (n % 2 != 0);')
    simple(SEC, '是否完全平方数', 'int', 'is_square', 'int n', 'if (n < 0) return 0;', 'int r = (int)sqrt(n);', 'return r * r == n;')
    simple(SEC, '是否完全立方数', 'int', 'is_cube', 'int n', 'if (n < 0) return 0;', 'int r = (int)cbrt(n);', 'return r * r * r == n;')
    simple(SEC, '数字根(数位反复求和)', 'int', 'digital_root', 'int n', 'if (n == 0) return 0;', 'int r = n % 9;', 'return (r == 0) ? 9 : r;')
    simple(SEC, '第 n 个素数', 'int', 'nth_prime', 'int n',
           'if (n <= 0) return -1;', 'int count = 0, num = 2;',
           'while (1) { if (is_prime(num)) { count++; if (count == n) return num; } num++; }')
    simple(SEC, '下一个素数(大于 n)', 'int', 'next_prime', 'int n',
           'int p = n + 1;', 'while (!is_prime(p)) p++;', 'return p;')
    simple(SEC, '上一个素数(小于 n)', 'int', 'prev_prime', 'int n',
           'for (int p = n - 1; p > 1; p--) if (is_prime(p)) return p;', 'return -1;')
    simple(SEC, 'n 以内素数个数', 'int', 'count_primes_upto', 'int n',
           'int c = 0;', 'for (int i = 2; i <= n; i++) if (is_prime(i)) c++;', 'return c;')
    simple(SEC, 'n 以内素数之和', 'long long', 'sum_primes_upto', 'int n',
           'long long s = 0;', 'for (int i = 2; i <= n; i++) if (is_prime(i)) s += i;', 'return s;')
    simple(SEC, '组合数 C(n,r)', 'long long', 'binomial_coefficient', 'int n, int r',
           'if (r < 0 || r > n) return 0;', 'if (r > n - r) r = n - r;', 'long long res = 1;',
           'for (int i = 0; i < r; i++) { res = res * (n - i) / (i + 1); }', 'return res;')
    simple(SEC, '排列数 P(n,r)', 'long long', 'permutation_count', 'int n, int r',
           'if (r < 0 || r > n) return 0;', 'long long res = 1;', 'for (int i = 0; i < r; i++) res *= (n - i);', 'return res;')
    simple(SEC, '第 n 个调和数', 'double', 'harmonic_number', 'int n',
           'double s = 0;', 'for (int i = 1; i <= n; i++) s += 1.0 / i;', 'return s;')
    simple(SEC, '是否盈数(真因子和>自身)', 'int', 'is_abundant', 'int n',
           'if (n <= 1) return 0;', 'int s = 0;', 'for (int i = 1; i <= n / 2; i++) if (n % i == 0) s += i;', 'return s > n;')
    simple(SEC, '是否亏数', 'int', 'is_deficient', 'int n',
           'if (n <= 1) return 1;', 'int s = 0;', 'for (int i = 1; i <= n / 2; i++) if (n % i == 0) s += i;', 'return s < n;')
    simple(SEC, '是否亲和数对(a,b)', 'int', 'is_amicable', 'int a, int b',
           'int sa = 0, sb = 0;', 'for (int i = 1; i <= a / 2; i++) if (a % i == 0) sa += i;',
           'for (int i = 1; i <= b / 2; i++) if (b % i == 0) sb += i;', 'return sa == b && sb == a && a != b;')
    simple(SEC, '是否快乐数', 'int', 'is_happy', 'int n',
           'int seen[1000] = {0};', 'while (n != 1 && !seen[n % 1000]) { seen[n % 1000] = 1; int s = 0; while (n) { int d = n % 10; s += d * d; n /= 10; } n = s; }',
           'return n == 1;')
    simple(SEC, '是否哈沙德数(可被数位和整除)', 'int', 'is_harshad', 'int n',
           'if (n <= 0) return 0;', 'int s = sum_digits(n);', 'return s != 0 && n % s == 0;')
    simple(SEC, '是否卡普雷卡数', 'int', 'is_kaprekar', 'int n',
           'if (n <= 0) return 0;', 'long long sq = (long long)n * n;', 'int d = count_digits(n);',
           'long long p = 1;', 'for (int i = 0; i < d; i++) p *= 10;',
           'long long hi = sq / p, lo = sq % p;', 'return hi + lo == n;')
    simple(SEC, '是否自守数', 'int', 'is_automorphic', 'int n',
           'long long sq = (long long)n * n;', 'int d = count_digits(n);', 'long long p = 1;',
           'for (int i = 0; i < d; i++) p *= 10;', 'return (sq % p) == n;')
    simple(SEC, '是否三角形数', 'int', 'is_triangular', 'int n',
           'int d = 1 + 8 * n;', 'int r = (int)sqrt(d);', 'return r * r == d;')
    simple(SEC, '科拉兹猜想步数', 'int', 'collatz_steps', 'int n',
           'int steps = 0;', 'while (n != 1) { if (n % 2) n = 3 * n + 1; else n /= 2; steps++; }', 'return steps;')
    simple(SEC, '真因子之和(别名)', 'int', 'aliquot_sum', 'int n',
           'int s = 0;', 'for (int i = 1; i <= n / 2; i++) if (n % i == 0) s += i;', 'return s;')
    simple(SEC, '因子个数', 'int', 'count_divisors', 'int n',
           'int c = 0;', 'for (int i = 1; i * i <= n; i++) if (n % i == 0) c += (i * i == n) ? 1 : 2;', 'return c;')
    simple(SEC, '因子之和', 'long long', 'sum_divisors', 'int n',
           'long long s = 0;', 'for (int i = 1; i * i <= n; i++) if (n % i == 0) { s += i; if (i != n / i) s += n / i; }', 'return s;')
    simple(SEC, '欧拉函数 φ(n)', 'int', 'euler_phi', 'int n',
           'int result = n;', 'for (int p = 2; p * p <= n; p++) { if (n % p == 0) { while (n % p == 0) n /= p; result -= result / p; } }',
           'if (n > 1) result -= result / n;', 'return result;')
    simple(SEC, '双阶乘 n!!', 'long long', 'double_factorial', 'int n',
           'if (n < 0) return -1;', 'long long r = 1;', 'for (int i = n; i > 0; i -= 2) r *= i;', 'return r;')
    simple(SEC, '第 n 个卡塔兰数', 'long long', 'catalan_number', 'int n',
           'if (n < 0) return 0;', 'long long c = 1;', 'for (int i = 0; i < n; i++) c = c * 2 * (2 * i + 1) / (i + 2);', 'return c;')
    simple(SEC, 'n 个圆盘汉诺塔最少步数', 'long long', 'hanoi_moves', 'int n',
           'if (n < 0) return 0;', 'return power(2, n) - 1;')
    simple(SEC, '约瑟夫环幸存者', 'int', 'josephus', 'int n, int k',
           'if (n <= 0 || k <= 0) return -1;', 'int r = 0;', 'for (int i = 2; i <= n; i++) r = (r + k) % i;', 'return r + 1;')
    simple(SEC, '弧度转角度', 'double', 'radians_to_degrees', 'double rad', 'return rad * 180.0 / 3.141592653589793;')
    simple(SEC, '角度转弧度', 'double', 'degrees_to_radians', 'double deg', 'return deg * 3.141592653589793 / 180.0;')
    simple(SEC, 'Sigmoid 函数', 'double', 'sigmoid', 'double x', 'return 1.0 / (1.0 + exp(-x));')
    simple(SEC, 'ReLU 函数', 'double', 'relu', 'double x', 'return (x > 0) ? x : 0.0;')
    simple(SEC, '角度归一化到 [0,360)', 'double', 'angle_normalize', 'double deg',
           'double r = fmod(deg, 360.0);', 'if (r < 0) r += 360.0;', 'return r;')
    simple(SEC, '四舍五入(到整数)', 'long long', 'round_half_up', 'double x', 'return (long long)floor(x + 0.5);')
    simple(SEC, '百分比', 'double', 'percentage', 'double part, double total', 'return (total == 0) ? 0.0 : part * 100.0 / total;')
    simple(SEC, '三个数的中位数', 'double', 'median_of_three', 'double a, double b, double c',
           'if (a > b) { double t = a; a = b; b = t; }', 'if (b > c) { double t = b; b = c; c = t; }',
           'if (a > b) { double t = a; a = b; b = t; }', 'return b;')
    simple(SEC, '加权平均', 'double', 'weighted_average', 'double values[], double weights[], int size',
           'double sv = 0, sw = 0;', 'for (int i = 0; i < size; i++) { sv += values[i] * weights[i]; sw += weights[i]; }',
           'return (sw == 0) ? 0.0 : sv / sw;')

# ============================================================
#  10. 进制与转换(扩展)
# ============================================================
def family_convert():
    SEC = '进制与转换(扩展)'
    simple(SEC, '十进制转任意进制(2~36)', 'char*', 'int_to_base_str', 'int num, int base, char *buf, int buf_size',
           'if (base < 2 || base > 36 || !buf || buf_size < 2) return buf;',
           'static const char digits[] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";',
           'int neg = 0;', 'if (num < 0) { neg = 1; num = -num; }',
           'char tmp[40]; int i = 0;', 'if (num == 0) tmp[i++] = \'0\';',
           'while (num > 0) { tmp[i++] = digits[num % base]; num /= base; }',
           'int k = 0;', 'if (neg && k < buf_size - 1) buf[k++] = \'-\';',
           'for (int j = i - 1; j >= 0 && k < buf_size - 1; j--) buf[k++] = tmp[j];',
           'buf[k] = \'\\0\';', 'return buf;')
    simple(SEC, '任意进制字符串转十进制', 'long', 'base_str_to_int', 'const char *str, int base',
           'if (base < 2 || base > 36 || !str) return 0;', 'long r = 0;',
           'while (*str) { int v = hex_char_to_int(*str); if (v < 0 || v >= base) break; r = r * base + v; str++; }', 'return r;')
    simple(SEC, '字符串转 long', 'long', 'str_to_long', 'const char *str', 'return strtol(str, NULL, 10);')
    simple(SEC, '字符串转 double', 'double', 'str_to_double', 'const char *str', 'return atof(str);')
    simple(SEC, 'double 转字符串', 'char*', 'double_to_str', 'double num, char *buf', 'sprintf(buf, "%.6f", num);', 'return buf;')
    simple(SEC, '十进制转罗马数字', 'char*', 'int_to_roman', 'int num, char *buf, int buf_size',
           'if (num <= 0 || num >= 4000 || !buf || buf_size < 2) { if (buf && buf_size > 0) buf[0] = \'\\0\'; return buf; }',
           'static const int vals[] = {1000,900,500,400,100,90,50,40,10,9,5,4,1};',
           'static const char *syms[] = {"M","CM","D","CD","C","XC","L","XL","X","IX","V","IV","I"};',
           'int k = 0;', 'for (int i = 0; i < 13 && k < buf_size - 1; i++)',
           '    while (num >= vals[i] && k < buf_size - 1) { buf[k++] = syms[i][0]; if (syms[i][1]) buf[k++] = syms[i][1]; num -= vals[i]; }',
           'buf[k] = \'\\0\';', 'return buf;')
    simple(SEC, '罗马数字转十进制', 'int', 'roman_to_int', 'const char *s',
           'int r = 0;', 'for (int i = 0; s[i]; i++) {',
           '    int v = (s[i] == \'I\') ? 1 : (s[i] == \'V\') ? 5 : (s[i] == \'X\') ? 10 : (s[i] == \'L\') ? 50 : (s[i] == \'C\') ? 100 : (s[i] == \'D\') ? 500 : (s[i] == \'M\') ? 1000 : 0;',
           '    int nv = (s[i+1]) ? ((s[i+1] == \'I\') ? 1 : (s[i+1] == \'V\') ? 5 : (s[i+1] == \'X\') ? 10 : (s[i+1] == \'L\') ? 50 : (s[i+1] == \'C\') ? 100 : (s[i+1] == \'D\') ? 500 : (s[i+1] == \'M\') ? 1000 : 0) : 0;',
           '    if (v < nv) r -= v; else r += v;', '}', 'return r;')
    simple(SEC, '千位分隔符格式化', 'char*', 'format_thousands', 'long long num, char *buf, int buf_size',
           'char tmp[32];', 'sprintf(tmp, "%lld", num);',
           'int neg = 0, i = 0;', 'if (tmp[0] == \'-\') { neg = 1; i = 1; }',
           'int digits = 0, k = 0;',
           'for (int j = (int)strlen(tmp) - 1; j >= i; j--) {',
           '    if (digits > 0 && digits % 3 == 0 && k < buf_size - 1) buf[k++] = \',\';',
           '    if (k < buf_size - 1) buf[k++] = tmp[j];',
           '    digits++;',
           '}', 'if (neg && k < buf_size - 1) buf[k++] = \'-\';',
           'int lo = 0, hi = k - 1;', 'while (lo < hi) { char t = buf[lo]; buf[lo] = buf[hi]; buf[hi] = t; lo++; hi--; }',
           'buf[k] = \'\\0\';', 'return buf;')
    simple(SEC, '字节大小格式化(KB/MB/GB)', 'char*', 'format_bytes', 'long long bytes, char *buf, int buf_size',
           'if (!buf || buf_size < 2) return buf;',
           'const char *units[] = {"B","KB","MB","GB","TB"};',
           'double v = (double)bytes; int u = 0;',
           'while (v >= 1024 && u < 4) { v /= 1024; u++; }',
           'sprintf(buf, "%.2f %s", v, units[u]);', 'return buf;')

# ============================================================
#  11. 位运算(扩展)
# ============================================================
def family_bit():
    SEC = '位运算(扩展)'
    simple(SEC, '读取第 bit 位(0/1)', 'int', 'get_bit', 'uint32_t val, int bit',
           'if (bit < 0 || bit > 31) return 0;', 'return (val >> bit) & 1u;')
    simple(SEC, '把第 bit 位设为 value(0/1)', 'uint32_t', 'set_bit_value', 'uint32_t val, int bit, int value',
           'if (bit < 0 || bit > 31) return val;', 'if (value) return val | (1u << bit);', 'return val & ~(1u << bit);')
    simple(SEC, '统计 0 的个数', 'int', 'count_zeros', 'uint32_t val', 'return 32 - (int)count_ones(val);')
    simple(SEC, '最高位 1 的位置(0~31)', 'int', 'msb_position', 'uint32_t val',
           'if (val == 0) return -1;', 'int pos = 0;', 'while (val >>= 1) pos++;', 'return pos;')
    simple(SEC, '下一个 2 的幂', 'uint32_t', 'next_power_of_two', 'uint32_t n',
           'if (n == 0) return 1;', 'if ((n & (n - 1)) == 0) return n;',
           'uint32_t p = 1;', 'while (p < n) p <<= 1;', 'return p;')
    simple(SEC, '上一个 2 的幂', 'uint32_t', 'prev_power_of_two', 'uint32_t n',
           'if (n == 0) return 0;', 'uint32_t p = 1;', 'while ((p << 1) <= n) p <<= 1;', 'return p;')
    simple(SEC, '反转二进制位', 'uint32_t', 'reverse_bits', 'uint32_t val',
           'uint32_t r = 0;', 'for (int i = 0; i < 32; i++) { r = (r << 1) | (val & 1u); val >>= 1; }', 'return r;')
    simple(SEC, '取高 4 位', 'uint8_t', 'nibble_high', 'uint8_t val', 'return (uint8_t)(val >> 4);')
    simple(SEC, '取低 4 位', 'uint8_t', 'nibble_low', 'uint8_t val', 'return (uint8_t)(val & 0x0F);')
    simple(SEC, '交换高低 4 位', 'uint8_t', 'nibble_swap', 'uint8_t val', 'return (uint8_t)((val << 4) | (val >> 4));')
    simple(SEC, '取位域(从 start 起 len 位)', 'uint32_t', 'bit_field_get', 'uint32_t val, int start, int len',
           'if (start < 0 || len <= 0 || start + len > 32) return 0;',
           'return (val >> start) & ((1u << len) - 1);')
    simple(SEC, '把位域写入(从 start 起 len 位)', 'uint32_t', 'bit_field_set', 'uint32_t val, int start, int len, uint32_t data',
           'if (start < 0 || len <= 0 || start + len > 32) return val;',
           'uint32_t mask = ((1u << len) - 1) << start;', 'return (val & ~mask) | ((data << start) & mask);')
    simple(SEC, '生成低 n 位全 1 掩码', 'uint32_t', 'low_bit_mask', 'int n',
           'if (n <= 0) return 0;', 'if (n >= 32) return 0xFFFFFFFFu;', 'return (1u << n) - 1;')
    simple(SEC, '生成高 n 位全 1 掩码', 'uint32_t', 'high_bit_mask', 'int n',
           'if (n <= 0) return 0;', 'if (n >= 32) return 0xFFFFFFFFu;', 'return 0xFFFFFFFFu << (32 - n);')
    simple(SEC, '无临时变量交换', 'void', 'swap_no_temp', 'int *a, int *b',
           'if (a == b) return;', '*a ^= *b; *b ^= *a; *a ^= *b;')
    simple(SEC, '判断二进制是否为连续 1', 'int', 'is_mask_contiguous', 'uint32_t val',
           'if (val == 0) return 0;', 'return ((val + (val & -val)) & val) == 0;')
    simple(SEC, '整数符号(1/-1/0)', 'int', 'sign_int', 'int n', 'return (n > 0) - (n < 0);')

# ============================================================
#  12. 校验与CRC(扩展)
# ============================================================
def family_crc():
    SEC = '校验与CRC(扩展)'
    simple(SEC, 'CRC-16/CCITT', 'uint16_t', 'crc16_ccitt', 'const uint8_t *data, uint16_t len',
           'uint16_t crc = 0xFFFF;',
           'for (uint16_t i = 0; i < len; i++) { crc ^= (uint16_t)data[i] << 8;',
           '    for (uint8_t j = 0; j < 8; j++) crc = (crc & 0x8000) ? (uint16_t)((crc << 1) ^ 0x1021) : (uint16_t)(crc << 1); }',
           'return crc;')
    simple(SEC, 'CRC-16/XMODEM', 'uint16_t', 'crc16_xmodem', 'const uint8_t *data, uint16_t len',
           'uint16_t crc = 0x0000;',
           'for (uint16_t i = 0; i < len; i++) { crc ^= (uint16_t)data[i] << 8;',
           '    for (uint8_t j = 0; j < 8; j++) crc = (crc & 0x8000) ? (uint16_t)((crc << 1) ^ 0x1021) : (uint16_t)(crc << 1); }',
           'return crc;')
    simple(SEC, 'CRC-32', 'uint32_t', 'crc32', 'const uint8_t *data, uint16_t len',
           'uint32_t crc = 0xFFFFFFFF;',
           'for (uint16_t i = 0; i < len; i++) { crc ^= data[i];',
           '    for (uint8_t j = 0; j < 8; j++) crc = (crc & 1) ? (crc >> 1) ^ 0xEDB88320u : crc >> 1; }',
           'return ~crc;')
    simple(SEC, 'Fletcher-16 校验', 'uint16_t', 'fletcher16', 'const uint8_t *data, uint16_t len',
           'uint16_t sum1 = 0, sum2 = 0;',
           'for (uint16_t i = 0; i < len; i++) { sum1 = (uint16_t)((sum1 + data[i]) % 255); sum2 = (uint16_t)((sum2 + sum1) % 255); }',
           'return (uint16_t)((sum2 << 8) | sum1);')
    simple(SEC, 'Fletcher-32 校验', 'uint32_t', 'fletcher32', 'const uint16_t *data, uint16_t len',
           'uint32_t sum1 = 0xFFFF, sum2 = 0xFFFF;',
           'for (uint16_t i = 0; i < len; i++) { sum1 = (sum1 + data[i]) % 65535; sum2 = (sum2 + sum1) % 65535; }',
           'return (sum2 << 16) | sum1;')
    simple(SEC, 'Adler-32 校验', 'uint32_t', 'adler32', 'const uint8_t *data, uint16_t len',
           'uint32_t a = 1, b = 0;',
           'for (uint16_t i = 0; i < len; i++) { a = (a + data[i]) % 65521; b = (b + a) % 65521; }',
           'return (b << 16) | a;')
    simple(SEC, 'LRC 纵向冗余校验', 'uint8_t', 'lrc_checksum', 'const uint8_t *data, uint16_t len',
           'uint8_t sum = 0;', 'for (uint16_t i = 0; i < len; i++) sum += data[i];', 'return (uint8_t)(-sum);')
    simple(SEC, '加权校验和', 'uint16_t', 'weighted_checksum', 'const uint8_t *data, uint16_t len',
           'uint16_t sum = 0;', 'for (uint16_t i = 0; i < len; i++) sum += (uint16_t)data[i] * (i + 1);',
           'return sum;')
    simple(SEC, 'NMEA 校验($ 与 * 之间异或)', 'uint8_t', 'nmea_checksum', 'const char *sentence',
           'uint8_t c = 0;', 'const char *p = sentence;',
           'while (*p && *p != \'$\') p++;', 'if (*p == \'$\') p++;',
           'while (*p && *p != \'*\') { c ^= (uint8_t)*p; p++; }', 'return c;')

# ============================================================
#  13. 哈希函数(扩展)
# ============================================================
def family_hash():
    SEC = '哈希函数(扩展)'
    simple(SEC, 'RS 哈希', 'uint32_t', 'rshash', 'const char *str',
           'uint32_t b = 378551, a = 63689, h = 0;',
           'while (*str) { h = h * a + (unsigned char)*str++; a *= b; }', 'return h;')
    simple(SEC, 'JS 哈希', 'uint32_t', 'jshash', 'const char *str',
           'uint32_t h = 1315423911;', 'while (*str) { h ^= ((h << 5) + (unsigned char)*str++ + (h >> 2)); }', 'return h;')
    simple(SEC, 'PJW 哈希', 'uint32_t', 'pjwhash', 'const char *str',
           'uint32_t h = 0, high;', 'while (*str) { h = (h << 4) + (unsigned char)*str++;',
           '    if ((high = h & 0xF0000000) != 0) h ^= high >> 24;',
           '    h &= ~high; }', 'return h;')
    simple(SEC, 'ELF 哈希', 'uint32_t', 'elfhash', 'const char *str',
           'uint32_t h = 0, g;', 'while (*str) { h = (h << 4) + (unsigned char)*str++;',
           '    if ((g = h & 0xF0000000) != 0) { h ^= g >> 24; h &= ~g; } }', 'return h;')
    simple(SEC, 'AP 哈希', 'uint32_t', 'aphash', 'const char *str',
           'uint32_t h = 0xAAAAAAAA;', 'int i = 0;', 'while (*str) {',
           '    h ^= ((i & 1) == 0) ? ((h << 7) ^ (unsigned char)*str * (h >> 3)) : (~((h << 11) + ((unsigned char)*str ^ (h >> 5))));',
           '    i++; str++; }', 'return h;')
    simple(SEC, 'Java 字符串哈希', 'uint32_t', 'java_hash', 'const char *str',
           'uint32_t h = 0;', 'while (*str) h = h * 31 + (unsigned char)*str++;', 'return h;')
    simple(SEC, 'DJB2-XOR 哈希', 'uint32_t', 'djb2_xor_hash', 'const char *str',
           'uint32_t h = 5381;', 'while (*str) h = ((h << 5) + h) ^ (unsigned char)*str++;', 'return h;')
    simple(SEC, 'FNV-1 哈希', 'uint32_t', 'fnv1_hash', 'const char *str',
           'uint32_t h = 2166136261u;', 'while (*str) { h *= 16777619u; h ^= (unsigned char)*str++; }', 'return h;')
    simple(SEC, 'DEK 哈希', 'uint32_t', 'dekhash', 'const char *str',
           'uint32_t h = (uint32_t)strlen(str);',
           'while (*str) { h = ((h << 5) ^ (h >> 27)) ^ (unsigned char)*str++; }', 'return h;')
    simple(SEC, 'BP 哈希', 'uint32_t', 'bphash', 'const char *str',
           'uint32_t h = 0;', 'while (*str) h = h * 7 + (unsigned char)*str++;', 'return h;')
    simple(SEC, 'BKDR 哈希(可指定种子)', 'uint32_t', 'bkdr_hash_seed', 'const char *str, uint32_t seed',
           'uint32_t h = 0;', 'while (*str) h = h * seed + (unsigned char)*str++;', 'return h;')

# ============================================================
#  14. 时间与日期
# ============================================================
def family_time():
    SEC = '时间与日期'
    simple(SEC, '判断日期是否有效', 'int', 'is_valid_date', 'int year, int month, int day',
           'if (month < 1 || month > 12 || day < 1) return 0;',
           'int dim = days_in_month(year, month);', 'return day <= dim;')
    simple(SEC, '某月天数', 'int', 'days_in_month', 'int year, int month',
           'static const int d[] = {31,28,31,30,31,30,31,31,30,31,30,31};',
           'if (month < 1 || month > 12) return 0;', 'if (month == 2 && is_leap_year(year)) return 29;', 'return d[month - 1];')
    simple(SEC, '一年中的第几天', 'int', 'day_of_year', 'int year, int month, int day',
           'int d = 0;', 'for (int m = 1; m < month; m++) d += days_in_month(year, m);', 'return d + day;')
    simple(SEC, '一年有多少天', 'int', 'days_in_year', 'int year', 'return is_leap_year(year) ? 366 : 365;')
    simple(SEC, '当前年', 'int', 'get_year_now', 'void',
           'time_t t = time(NULL); struct tm *tm = localtime(&t); return tm->tm_year + 1900;')
    simple(SEC, '当前月(1~12)', 'int', 'get_month_now', 'void',
           'time_t t = time(NULL); struct tm *tm = localtime(&t); return tm->tm_mon + 1;')
    simple(SEC, '当前日(1~31)', 'int', 'get_day_now', 'void',
           'time_t t = time(NULL); struct tm *tm = localtime(&t); return tm->tm_mday;')
    simple(SEC, '当前小时(0~23)', 'int', 'get_hour_now', 'void',
           'time_t t = time(NULL); struct tm *tm = localtime(&t); return tm->tm_hour;')
    simple(SEC, '当前分钟(0~59)', 'int', 'get_minute_now', 'void',
           'time_t t = time(NULL); struct tm *tm = localtime(&t); return tm->tm_min;')
    simple(SEC, '当前秒(0~59)', 'int', 'get_second_now', 'void',
           'time_t t = time(NULL); struct tm *tm = localtime(&t); return tm->tm_sec;')
    simple(SEC, '当前星期几(0=周日)', 'int', 'get_weekday_now', 'void',
           'time_t t = time(NULL); struct tm *tm = localtime(&t); return tm->tm_wday;')
    simple(SEC, '时间戳转日期字符串', 'char*', 'timestamp_to_date_str', 'long long ts, char *buf, int buf_size',
           'time_t t = (time_t)ts; struct tm *tm = localtime(&t);',
           'strftime(buf, (size_t)buf_size, "%Y-%m-%d %H:%M:%S", tm);', 'return buf;')

# ============================================================
#  15. 随机工具
# ============================================================
def family_random():
    SEC = '随机工具'
    simple(SEC, '用当前时间设置随机种子', 'void', 'rand_seed_time', 'void', 'srand((unsigned)time(NULL));')
    simple(SEC, '随机布尔值', 'int', 'rand_bool', 'void', 'return rand() % 2;')
    simple(SEC, '随机浮点数 [0,1)', 'double', 'rand_double', 'void', 'return (double)rand() / (RAND_MAX + 1.0);')
    simple(SEC, '随机浮点数 [min,max)', 'double', 'rand_double_range', 'double min, double max',
           'return min + (max - min) * ((double)rand() / (RAND_MAX + 1.0));')
    simple(SEC, '随机选择数组元素', 'int', 'rand_choice_int', 'int arr[], int size',
           'if (size <= 0) return 0;', 'return arr[rand() % size];')
    simple(SEC, '生成随机字符串(可打印字符)', 'char*', 'rand_string', 'char *buf, int buf_size, int len',
           'if (!buf || buf_size <= 0) return buf;', 'if (len >= buf_size) len = buf_size - 1;',
           'for (int i = 0; i < len; i++) buf[i] = (char)(33 + rand() % 94);', 'buf[len] = \'\\0\';', 'return buf;')
    simple(SEC, '生成随机数字字符串', 'char*', 'rand_digits_string', 'char *buf, int buf_size, int len',
           'if (!buf || buf_size <= 0) return buf;', 'if (len >= buf_size) len = buf_size - 1;',
           'for (int i = 0; i < len; i++) buf[i] = (char)(\'0\' + rand() % 10);', 'buf[len] = \'\\0\';', 'return buf;')
    simple(SEC, '打乱字符串(原地)', 'void', 'rand_shuffle_str', 'char *str',
           'int n = str_len(str);', 'for (int i = n - 1; i > 0; i--) { int j = rand() % (i + 1); char t = str[i]; str[i] = str[j]; str[j] = t; }')
    simple(SEC, '在 [min,max] 生成 n 个不重复随机数', 'int*', 'rand_unique_ints', 'int min, int max, int n',
           'if (min > max || n <= 0) return NULL;', 'int range = max - min + 1;',
           'if (n > range) n = range;', 'int *r = (int*)malloc(n * sizeof(int));', 'if (!r) return NULL;',
           'int cnt = 0;', 'while (cnt < n) { int v = min + rand() % range; int dup = 0; for (int i = 0; i < cnt; i++) if (r[i] == v) { dup = 1; break; } if (!dup) r[cnt++] = v; }',
           'return r;')

# ============================================================
#  16. 几何工具
# ============================================================
def family_geom():
    SEC = '几何工具'
    simple(SEC, '二维两点距离', 'double', 'distance_2d', 'double x1, double y1, double x2, double y2',
           'double dx = x2 - x1, dy = y2 - y1;', 'return sqrt(dx * dx + dy * dy);')
    simple(SEC, '三维两点距离', 'double', 'distance_3d', 'double x1, double y1, double z1, double x2, double y2, double z2',
           'double dx = x2 - x1, dy = y2 - y1, dz = z2 - z1;', 'return sqrt(dx * dx + dy * dy + dz * dz);')
    simple(SEC, '海伦公式三角形面积', 'double', 'area_triangle_heron', 'double a, double b, double c',
           'double s = (a + b + c) / 2.0;', 'double t = s * (s - a) * (s - b) * (s - c);', 'return (t > 0) ? sqrt(t) : 0.0;')
    simple(SEC, '三角形周长', 'double', 'perimeter_triangle', 'double a, double b, double c', 'return a + b + c;')
    simple(SEC, '圆面积', 'double', 'circle_area', 'double r', 'return 3.141592653589793 * r * r;')
    simple(SEC, '圆周长', 'double', 'circle_circumference', 'double r', 'return 2.0 * 3.141592653589793 * r;')
    simple(SEC, '圆直径', 'double', 'circle_diameter', 'double r', 'return 2.0 * r;')
    simple(SEC, '球体积', 'double', 'sphere_volume', 'double r', 'return 4.0 / 3.0 * 3.141592653589793 * r * r * r;')
    simple(SEC, '球表面积', 'double', 'sphere_surface_area', 'double r', 'return 4.0 * 3.141592653589793 * r * r;')
    simple(SEC, '矩形面积', 'double', 'rect_area', 'double w, double h', 'return w * h;')
    simple(SEC, '矩形周长', 'double', 'rect_perimeter', 'double w, double h', 'return 2.0 * (w + h);')
    simple(SEC, '点是否在矩形内', 'int', 'is_point_in_rect', 'double px, double py, double x, double y, double w, double h',
           'return (px >= x && px <= x + w && py >= y && py <= y + h);')
    simple(SEC, '点是否在圆内', 'int', 'is_point_in_circle', 'double px, double py, double cx, double cy, double r',
           'return distance_2d(px, py, cx, cy) <= r;')
    simple(SEC, '两点斜率', 'double', 'slope_between', 'double x1, double y1, double x2, double y2',
           'if (x2 == x1) return 0.0;', 'return (y2 - y1) / (x2 - x1);')
    simple(SEC, '二维中点', 'void', 'midpoint_2d', 'double x1, double y1, double x2, double y2, double *mx, double *my',
           '*mx = (x1 + x2) / 2.0;', '*my = (y1 + y2) / 2.0;')
    simple(SEC, '正六边形面积', 'double', 'hexagon_area', 'double side', 'return (3.0 * sqrt(3.0) / 2.0) * side * side;')
    simple(SEC, '圆柱体积', 'double', 'cylinder_volume', 'double r, double h', 'return 3.141592653589793 * r * r * h;')

# ============================================================
#  17. 数值工具
# ============================================================
def family_numtool():
    SEC = '数值工具'
    simple(SEC, '整数裁剪到 [lo,hi]', 'int', 'clamp_int', 'int v, int lo, int hi',
           'if (v < lo) return lo;', 'if (v > hi) return hi;', 'return v;')
    simple(SEC, '浮点裁剪到 [lo,hi]', 'double', 'clamp_double', 'double v, double lo, double hi',
           'if (v < lo) return lo;', 'if (v > hi) return hi;', 'return v;')
    simple(SEC, '线性插值', 'double', 'lerp_double', 'double a, double b, double t', 'return a + (b - a) * t;')
    simple(SEC, '整数线性插值', 'int', 'lerp_int', 'int a, int b, int t, int max_t',
           'if (max_t == 0) return a;', 'return a + (b - a) * t / max_t;')
    simple(SEC, '数值映射(从 [s1,s2] 到 [d1,d2])', 'double', 'map_range_double', 'double v, double s1, double s2, double d1, double d2',
           'if (s2 == s1) return d1;', 'return d1 + (v - s1) * (d2 - d1) / (s2 - s1);')
    simple(SEC, '取整到最近整数', 'long long', 'round_to_int', 'double x', 'return (long long)floor(x + 0.5);')
    simple(SEC, '向上取整到 m 的倍数', 'long long', 'ceil_to_multiple', 'long long v, long long m',
           'if (m <= 0) return v;', 'return ((v + m - 1) / m) * m;')
    simple(SEC, '向下取整到 m 的倍数', 'long long', 'floor_to_multiple', 'long long v, long long m',
           'if (m <= 0) return v;', 'return (v / m) * m;')
    simple(SEC, '是否近似相等(误差 eps)', 'int', 'approx_equal_double', 'double a, double b, double eps',
           'return (fabs(a - b) <= eps);')
    simple(SEC, '三数最大值', 'int', 'max3_int', 'int a, int b, int c',
           'int m = a;', 'if (b > m) m = b;', 'if (c > m) m = c;', 'return m;')
    simple(SEC, '三数最小值', 'int', 'min3_int', 'int a, int b, int c',
           'int m = a;', 'if (b < m) m = b;', 'if (c < m) m = c;', 'return m;')
    simple(SEC, '四数最大值', 'int', 'max4_int', 'int a, int b, int c, int d',
           'int m = max3_int(a, b, c);', 'if (d > m) m = d;', 'return m;')
    simple(SEC, '浮点绝对值', 'double', 'fabs_double', 'double x', 'return fabs(x);')
    simple(SEC, '高斯取整(向下取整)', 'long long', 'floor_int', 'double x', 'return (long long)floor(x);')
    simple(SEC, '向上取整', 'long long', 'ceil_int', 'double x', 'return (long long)ceil(x);')
    simple(SEC, '自然数 1..n 之和', 'long long', 'sum_natural', 'int n', 'return (n <= 0) ? 0 : (long long)n * (n + 1) / 2;')
    simple(SEC, '平方和 1^2+..+n^2', 'long long', 'sum_squares', 'int n',
           'if (n <= 0) return 0;', 'return (long long)n * (n + 1) * (2 * n + 1) / 6;')
    simple(SEC, '立方和 1^3+..+n^3', 'long long', 'sum_cubes', 'int n',
           'long long s = sum_natural(n);', 'return s * s;')
    simple(SEC, '等差数列前 n 项和', 'long long', 'arithmetic_sum', 'long long a1, long long d, int n',
           'if (n <= 0) return 0;', 'return n * (2 * a1 + (n - 1) * d) / 2;')

# ============================================================
#  18. 数据结构（双链表/双端队列/最小堆/整数集合/字符串哈希表/图）
# ============================================================
DS_HEADER = []
def family_ds():
    SEC = '数据结构(扩展)'
    DS_HEADER.clear()
    # ---- 双向链表 ----
    DS_HEADER.append('typedef struct DNode { int data; struct DNode *prev, *next; } DNode;')
    DS_HEADER.append('typedef struct { DNode *head, *tail; int size; } DList;')
    simple(SEC, '创建空双向链表', 'DList*', 'dlist_create', 'void',
           'DList *l = (DList*)malloc(sizeof(DList));', 'if (!l) return NULL;', 'l->head = l->tail = NULL; l->size = 0;', 'return l;')
    simple(SEC, '头部插入', 'int', 'dlist_push_front', 'DList *l, int data',
           'if (!l) return -1;', 'DNode *n = (DNode*)malloc(sizeof(DNode));', 'if (!n) return -1;',
           'n->data = data; n->prev = NULL; n->next = l->head;',
           'if (l->head) l->head->prev = n; else l->tail = n;', 'l->head = n; l->size++;', 'return 0;')
    simple(SEC, '尾部插入', 'int', 'dlist_push_back', 'DList *l, int data',
           'if (!l) return -1;', 'DNode *n = (DNode*)malloc(sizeof(DNode));', 'if (!n) return -1;',
           'n->data = data; n->next = NULL; n->prev = l->tail;',
           'if (l->tail) l->tail->next = n; else l->head = n;', 'l->tail = n; l->size++;', 'return 0;')
    simple(SEC, '删除第一个等于 data 的节点', 'int', 'dlist_remove', 'DList *l, int data',
           'if (!l) return -1;', 'for (DNode *p = l->head; p; p = p->next) {',
           '    if (p->data == data) {',
           '        if (p->prev) p->prev->next = p->next; else l->head = p->next;',
           '        if (p->next) p->next->prev = p->prev; else l->tail = p->prev;',
           '        free(p); l->size--; return 0;', '    }', '}', 'return -1;')
    simple(SEC, '查找节点', 'DNode*', 'dlist_search', 'DList *l, int data',
           'if (!l) return NULL;', 'for (DNode *p = l->head; p; p = p->next) if (p->data == data) return p;', 'return NULL;')
    simple(SEC, '链表长度', 'int', 'dlist_length', 'DList *l', 'return (l == NULL) ? 0 : l->size;')
    simple(SEC, '正序打印', 'void', 'dlist_print', 'DList *l',
           'if (!l) return;', 'for (DNode *p = l->head; p; p = p->next) printf("%d <-> ", p->data);', 'printf("NULL\\n");')
    simple(SEC, '反转链表', 'void', 'dlist_reverse', 'DList *l',
           'if (!l || l->size < 2) return;', 'DNode *p = l->head, *t = l->tail;',
           'while (p) { DNode *n = p->next; p->next = p->prev; p->prev = n; p = n; }',
           'l->head = t; l->tail = l->head ? l->head->prev : NULL;')
    simple(SEC, '释放链表', 'void', 'dlist_free', 'DList *l',
           'if (!l) return;', 'DNode *p = l->head;', 'while (p) { DNode *n = p->next; free(p); p = n; }', 'free(l);')
    # ---- 双端队列 ----
    DS_HEADER.append('typedef struct { int *data; int front, rear, size, capacity; } Deque;')
    simple(SEC, '创建双端队列', 'Deque*', 'deque_create', 'int capacity',
           'if (capacity <= 0) return NULL;', 'Deque *d = (Deque*)malloc(sizeof(Deque));', 'if (!d) return NULL;',
           'd->data = (int*)malloc(capacity * sizeof(int));', 'if (!d->data) { free(d); return NULL; }',
           'd->front = 0; d->rear = 0; d->size = 0; d->capacity = capacity;', 'return d;')
    simple(SEC, '销毁双端队列', 'void', 'deque_destroy', 'Deque *d', 'if (!d) return;', 'free(d->data);', 'free(d);')
    simple(SEC, '头部入队', 'int', 'deque_push_front', 'Deque *d, int value',
           'if (!d || d->size >= d->capacity) return -1;', 'd->front = (d->front - 1 + d->capacity) % d->capacity;',
           'd->data[d->front] = value; d->size++;', 'return 0;')
    simple(SEC, '尾部入队', 'int', 'deque_push_back', 'Deque *d, int value',
           'if (!d || d->size >= d->capacity) return -1;', 'd->data[d->rear] = value;',
           'd->rear = (d->rear + 1) % d->capacity; d->size++;', 'return 0;')
    simple(SEC, '头部出队', 'int', 'deque_pop_front', 'Deque *d, int *out',
           'if (!d || d->size <= 0 || !out) return -1;', '*out = d->data[d->front];',
           'd->front = (d->front + 1) % d->capacity; d->size--;', 'return 0;')
    simple(SEC, '尾部出队', 'int', 'deque_pop_back', 'Deque *d, int *out',
           'if (!d || d->size <= 0 || !out) return -1;', 'd->rear = (d->rear - 1 + d->capacity) % d->capacity;',
           '*out = d->data[d->rear]; d->size--;', 'return 0;')
    simple(SEC, '查看头部', 'int', 'deque_peek_front', 'Deque *d, int *out',
           'if (!d || d->size <= 0 || !out) return -1;', '*out = d->data[d->front];', 'return 0;')
    simple(SEC, '查看尾部', 'int', 'deque_peek_back', 'Deque *d, int *out',
           'if (!d || d->size <= 0 || !out) return -1;', '*out = d->data[(d->rear - 1 + d->capacity) % d->capacity];', 'return 0;')
    simple(SEC, '元素个数', 'int', 'deque_size', 'Deque *d', 'return (d == NULL) ? 0 : d->size;')
    simple(SEC, '是否为空', 'int', 'deque_is_empty', 'Deque *d', 'return (d == NULL || d->size == 0);')
    simple(SEC, '是否已满', 'int', 'deque_is_full', 'Deque *d', 'return (d != NULL && d->size >= d->capacity);')
    simple(SEC, '清空', 'void', 'deque_clear', 'Deque *d',
           'if (!d) return;', 'd->front = 0; d->rear = 0; d->size = 0;')
    # ---- 最小堆 ----
    DS_HEADER.append('typedef struct { int *data; int size, capacity; } MinHeap;')
    simple(SEC, '创建最小堆', 'MinHeap*', 'mheap_create', 'int capacity',
           'if (capacity <= 0) return NULL;', 'MinHeap *h = (MinHeap*)malloc(sizeof(MinHeap));', 'if (!h) return NULL;',
           'h->data = (int*)malloc(capacity * sizeof(int));', 'if (!h->data) { free(h); return NULL; }',
           'h->size = 0; h->capacity = capacity;', 'return h;')
    simple(SEC, '销毁最小堆', 'void', 'mheap_destroy', 'MinHeap *h', 'if (!h) return;', 'free(h->data);', 'free(h);')
    simple(SEC, '入堆', 'int', 'mheap_push', 'MinHeap *h, int value',
           'if (!h) return -1;', 'if (h->size >= h->capacity) return -1;', 'int i = h->size++;', 'h->data[i] = value;',
           'while (i > 0) { int p = (i - 1) / 2; if (h->data[p] <= h->data[i]) break; int t = h->data[p]; h->data[p] = h->data[i]; h->data[i] = t; i = p; }',
           'return 0;')
    simple(SEC, '弹出最小值', 'int', 'mheap_pop', 'MinHeap *h, int *out',
           'if (!h || h->size <= 0 || !out) return -1;', '*out = h->data[0];',
           'h->data[0] = h->data[--h->size];', 'int i = 0;',
           'while (1) { int l = 2 * i + 1, r = 2 * i + 2, s = i;',
           '    if (l < h->size && h->data[l] < h->data[s]) s = l;',
           '    if (r < h->size && h->data[r] < h->data[s]) s = r;',
           '    if (s == i) break;', '    int t = h->data[s]; h->data[s] = h->data[i]; h->data[i] = t; i = s; }',
           'return 0;')
    simple(SEC, '查看最小值', 'int', 'mheap_peek', 'MinHeap *h, int *out',
           'if (!h || h->size <= 0 || !out) return -1;', '*out = h->data[0];', 'return 0;')
    simple(SEC, '堆大小', 'int', 'mheap_size', 'MinHeap *h', 'return (h == NULL) ? 0 : h->size;')
    simple(SEC, '堆是否为空', 'int', 'mheap_is_empty', 'MinHeap *h', 'return (h == NULL || h->size == 0);')
    # ---- 整数集合（开放寻址+墓碑） ----
    DS_HEADER.append('typedef struct { int *data; char *used, *del; int size, capacity; } IntSet;')
    simple(SEC, '创建整数集合', 'IntSet*', 'iset_create', 'int capacity',
           'if (capacity <= 0) capacity = 16;', 'IntSet *s = (IntSet*)malloc(sizeof(IntSet));', 'if (!s) return NULL;',
           's->data = (int*)calloc(capacity, sizeof(int));', 's->used = (char*)calloc(capacity, 1);', 's->del = (char*)calloc(capacity, 1);',
           'if (!s->data || !s->used || !s->del) { free(s->data); free(s->used); free(s->del); free(s); return NULL; }',
           's->size = 0; s->capacity = capacity;', 'return s;')
    simple(SEC, '销毁整数集合', 'void', 'iset_destroy', 'IntSet *s',
           'if (!s) return;', 'free(s->data); free(s->used); free(s->del); free(s);')
    simple(SEC, '添加元素', 'int', 'iset_add', 'IntSet *s, int key',
           'if (!s) return -1;', 'if (s->size * 2 >= s->capacity) return -1;',
           'int i = ((key * 2654435761u) & 0x7FFFFFFF) % s->capacity;',
           'while (s->used[i]) { if (!s->del[i] && s->data[i] == key) return 0; i = (i + 1) % s->capacity; }',
           's->used[i] = 1; s->del[i] = 0; s->data[i] = key; s->size++;', 'return 0;')
    simple(SEC, '是否包含元素', 'int', 'iset_contains', 'IntSet *s, int key',
           'if (!s) return 0;', 'int i = ((key * 2654435761u) & 0x7FFFFFFF) % s->capacity;',
           'while (s->used[i]) { if (!s->del[i] && s->data[i] == key) return 1; i = (i + 1) % s->capacity; }', 'return 0;')
    simple(SEC, '删除元素', 'int', 'iset_remove', 'IntSet *s, int key',
           'if (!s) return -1;', 'int i = ((key * 2654435761u) & 0x7FFFFFFF) % s->capacity;',
           'while (s->used[i]) { if (!s->del[i] && s->data[i] == key) { s->del[i] = 1; s->size--; return 0; } i = (i + 1) % s->capacity; }',
           'return -1;')
    simple(SEC, '元素个数', 'int', 'iset_size', 'IntSet *s', 'return (s == NULL) ? 0 : s->size;')
    simple(SEC, '清空集合', 'void', 'iset_clear', 'IntSet *s',
           'if (!s) return;', 'for (int i = 0; i < s->capacity; i++) { s->used[i] = 0; s->del[i] = 0; }', 's->size = 0;')
    # ---- 字符串哈希表 ----
    DS_HEADER.append('typedef struct { char **keys; int *values; char *used; int size, capacity; } StrMap;')
    simple(SEC, '创建字符串哈希表', 'StrMap*', 'smap_create', 'int capacity',
           'if (capacity <= 0) capacity = 16;', 'StrMap *m = (StrMap*)malloc(sizeof(StrMap));', 'if (!m) return NULL;',
           'm->keys = (char**)calloc(capacity, sizeof(char*));', 'm->values = (int*)calloc(capacity, sizeof(int));', 'm->used = (char*)calloc(capacity, 1);',
           'if (!m->keys || !m->values || !m->used) { free(m->keys); free(m->values); free(m->used); free(m); return NULL; }',
           'm->size = 0; m->capacity = capacity;', 'return m;')
    simple(SEC, '销毁哈希表', 'void', 'smap_destroy', 'StrMap *m',
           'if (!m) return;', 'for (int i = 0; i < m->capacity; i++) if (m->used[i]) free(m->keys[i]);',
           'free(m->keys); free(m->values); free(m->used); free(m);')
    simple(SEC, '写入键值对', 'int', 'smap_put', 'StrMap *m, const char *key, int value',
           'if (!m || !key) return -1;', 'if (m->size * 2 >= m->capacity) return -1;',
           'uint32_t h = djb2_hash(key);', 'int i = h % m->capacity;',
           'while (m->used[i]) { if (str_cmp(m->keys[i], key) == 0) { m->values[i] = value; return 0; } i = (i + 1) % m->capacity; }',
           'm->keys[i] = copy_string(key); if (!m->keys[i]) return -1;',
           'm->values[i] = value; m->used[i] = 1; m->size++;', 'return 0;')
    simple(SEC, '读取键对应的值', 'int', 'smap_get', 'StrMap *m, const char *key, int *out',
           'if (!m || !key || !out) return -1;', 'uint32_t h = djb2_hash(key);', 'int i = h % m->capacity;',
           'while (m->used[i]) { if (str_cmp(m->keys[i], key) == 0) { *out = m->values[i]; return 0; } i = (i + 1) % m->capacity; }',
           'return -1;')
    simple(SEC, '是否包含键', 'int', 'smap_contains', 'StrMap *m, const char *key',
           'if (!m || !key) return 0;', 'uint32_t h = djb2_hash(key);', 'int i = h % m->capacity;',
           'while (m->used[i]) { if (str_cmp(m->keys[i], key) == 0) return 1; i = (i + 1) % m->capacity; }', 'return 0;')
    simple(SEC, '删除键', 'int', 'smap_remove', 'StrMap *m, const char *key',
           'if (!m || !key) return -1;', 'uint32_t h = djb2_hash(key);', 'int i = h % m->capacity;',
           'while (m->used[i]) { if (str_cmp(m->keys[i], key) == 0) { free(m->keys[i]); m->keys[i] = NULL; m->used[i] = 0; m->size--; return 0; } i = (i + 1) % m->capacity; }',
           'return -1;')
    simple(SEC, '键值对数量', 'int', 'smap_size', 'StrMap *m', 'return (m == NULL) ? 0 : m->size;')
    # ---- 图（邻接矩阵） ----
    DS_HEADER.append('typedef struct { int **adj; int n; } Graph;')
    simple(SEC, '创建 n 个节点的图', 'Graph*', 'graph_create', 'int n',
           'if (n <= 0) return NULL;', 'Graph *g = (Graph*)malloc(sizeof(Graph));', 'if (!g) return NULL;',
           'g->n = n;', 'g->adj = (int**)calloc(n, sizeof(int*));', 'if (!g->adj) { free(g); return NULL; }',
           'for (int i = 0; i < n; i++) { g->adj[i] = (int*)calloc(n, sizeof(int)); if (!g->adj[i]) return NULL; }',
           'return g;')
    simple(SEC, '销毁图', 'void', 'graph_destroy', 'Graph *g',
           'if (!g) return;', 'for (int i = 0; i < g->n; i++) free(g->adj[i]);', 'free(g->adj);', 'free(g);')
    simple(SEC, '添加无向边', 'void', 'graph_add_edge', 'Graph *g, int u, int v',
           'if (!g || u < 0 || u >= g->n || v < 0 || v >= g->n) return;', 'g->adj[u][v] = 1; g->adj[v][u] = 1;')
    simple(SEC, '删除无向边', 'void', 'graph_remove_edge', 'Graph *g, int u, int v',
           'if (!g || u < 0 || u >= g->n || v < 0 || v >= g->n) return;', 'g->adj[u][v] = 0; g->adj[v][u] = 0;')
    simple(SEC, '是否有边', 'int', 'graph_has_edge', 'Graph *g, int u, int v',
           'if (!g || u < 0 || u >= g->n || v < 0 || v >= g->n) return 0;', 'return g->adj[u][v];')
    simple(SEC, '节点度数', 'int', 'graph_degree', 'Graph *g, int v',
           'if (!g || v < 0 || v >= g->n) return 0;', 'int d = 0;', 'for (int i = 0; i < g->n; i++) d += g->adj[v][i];', 'return d;')
    simple(SEC, '打印邻接矩阵', 'void', 'graph_print', 'Graph *g',
           'if (!g) return;', 'for (int i = 0; i < g->n; i++) { for (int j = 0; j < g->n; j++) printf("%d ", g->adj[i][j]); printf("\\n"); }')
    simple(SEC, '广度优先遍历(打印)', 'void', 'graph_bfs', 'Graph *g, int start',
           'if (!g || start < 0 || start >= g->n) return;', 'char *vis = (char*)calloc(g->n, 1);',
           'int *q = (int*)malloc(g->n * sizeof(int));', 'int head = 0, tail = 0;',
           'vis[start] = 1; q[tail++] = start;',
           'while (head < tail) { int v = q[head++]; printf("%d ", v);',
           '    for (int i = 0; i < g->n; i++) if (g->adj[v][i] && !vis[i]) { vis[i] = 1; q[tail++] = i; } }',
           'printf("\\n");', 'free(vis); free(q);')
    simple(SEC, '深度优先遍历(打印)', 'void', 'graph_dfs', 'Graph *g, int start',
           'if (!g || start < 0 || start >= g->n) return;',
           'char *vis = (char*)calloc(g->n, 1);',
           'int st[1024], top = 0;', 'vis[start] = 1; st[top++] = start;',
           'while (top > 0) { int v = st[--top]; printf("%d ", v);',
           '    for (int i = g->n - 1; i >= 0; i--) if (g->adj[v][i] && !vis[i]) { vis[i] = 1; st[top++] = i; } }',
           'printf("\\n");', 'free(vis);')
    simple(SEC, 'Dijkstra 单源最短路(需free)', 'int*', 'graph_dijkstra', 'Graph *g, int src',
           'if (!g || src < 0 || src >= g->n) return NULL;',
           'int *dist = (int*)malloc(g->n * sizeof(int));', 'char *done = (char*)calloc(g->n, 1);',
           'for (int i = 0; i < g->n; i++) dist[i] = 1000000000;', 'dist[src] = 0;',
           'for (int k = 0; k < g->n; k++) {',
           '    int u = -1;', '    for (int i = 0; i < g->n; i++) if (!done[i] && (u < 0 || dist[i] < dist[u])) u = i;',
           '    if (u < 0) break;', '    done[u] = 1;',
           '    for (int v = 0; v < g->n; v++) if (g->adj[u][v] && dist[u] + 1 < dist[v]) dist[v] = dist[u] + 1;', '}',
           'free(done);', 'return dist;')

# ============================================================
#  19. 文件工具(扩展)
# ============================================================
def family_file():
    SEC = '文件工具(扩展)'
    simple(SEC, '追加一行', 'int', 'file_append_line', 'const char *filename, const char *line',
           'FILE *fp = fopen(filename, "a");', 'if (!fp) return -1;', 'fprintf(fp, "%s\\n", line);', 'fclose(fp);', 'return 0;')
    simple(SEC, '文件是否为空', 'int', 'file_is_empty', 'const char *filename',
           'FILE *fp = fopen(filename, "rb");', 'if (!fp) return 1;', 'fseek(fp, 0, SEEK_END);', 'int e = (ftell(fp) == 0);', 'fclose(fp);', 'return e;')
    simple(SEC, '创建空文件', 'int', 'file_touch', 'const char *filename',
           'FILE *fp = fopen(filename, "a");', 'if (!fp) return -1;', 'fclose(fp);', 'return 0;')
    simple(SEC, '删除文件', 'int', 'file_delete', 'const char *filename', 'return remove(filename);')
    simple(SEC, '重命名文件', 'int', 'file_rename', 'const char *old, const char *new', 'return rename(old, new);')
    simple(SEC, '取文件主名(不含扩展名)', 'char*', 'file_stem', 'const char *path, char *buf, int buf_size',
           'if (!path || !buf || buf_size <= 0) return NULL;',
           'get_base_name(path, buf, buf_size);',
           'const char *dot = strrchr(buf, \'.\');', 'if (dot) *((char*)dot) = \'\\0\';', 'return buf;')
    simple(SEC, '读取一行到缓冲区', 'char*', 'file_read_line', 'FILE *fp, char *buf, int buf_size',
           'return safe_fgets(buf, (size_t)buf_size, fp);')

# ============================================================
#  20. 内存工具(扩展)
# ============================================================
def family_mem():
    SEC = '内存工具(扩展)'
    simple(SEC, '复制内存块(需free)', 'void*', 'safe_memdup', 'const void *src, size_t size',
           'if (!src) return NULL;', 'void *r = malloc(size);', 'if (!r) return NULL;', 'memcpy(r, src, size);', 'return r;')
    simple(SEC, '内存清零', 'void', 'zero_memory', 'void *ptr, size_t size', 'if (ptr) memset(ptr, 0, size);')
    simple(SEC, '内存填充', 'void', 'fill_memory', 'void *ptr, size_t size, unsigned char value',
           'if (ptr) memset(ptr, value, size);')
    simple(SEC, '内存比较', 'int', 'compare_memory', 'const void *a, const void *b, size_t size',
           'return memcmp(a, b, size);')
    simple(SEC, '交换内存块', 'void', 'swap_memory', 'void *a, void *b, size_t size',
           'if (!a || !b || a == b) return;', 'unsigned char *pa = (unsigned char*)a, *pb = (unsigned char*)b;',
           'for (size_t i = 0; i < size; i++) { unsigned char t = pa[i]; pa[i] = pb[i]; pb[i] = t; }')

# ============================================================
#  21. 控制台与调试(扩展)
# ============================================================
def family_console():
    SEC = '控制台与调试(扩展)'
    simple(SEC, '打印整数', 'void', 'print_int', 'int v', 'printf("%d\\n", v);')
    simple(SEC, '打印长整数', 'void', 'print_long', 'long v', 'printf("%ld\\n", v);')
    simple(SEC, '打印浮点数', 'void', 'print_double', 'double v', 'printf("%.6f\\n", v);')
    simple(SEC, '打印十六进制', 'void', 'print_hex', 'unsigned int v', 'printf("0x%X\\n", v);')
    simple(SEC, '打印单个字符', 'void', 'print_char', 'char c', 'printf("%c\\n", c);')
    simple(SEC, '打印分隔线', 'void', 'print_separator', 'void', 'printf("----------------------------------------\\n");')
    simple(SEC, '打印带边框标题', 'void', 'print_box_title', 'const char *title',
           'int n = str_len(title);', 'printf("=="); for (int i = 0; i < n; i++) printf("="); printf("==\\n");',
           'printf("  %s\\n", title);', 'printf("=="); for (int i = 0; i < n; i++) printf("="); printf("==\\n");')
    simple(SEC, '打印字符串数组', 'void', 'print_str_array', 'char *arr[], int size',
           'for (int i = 0; i < size; i++) printf("%s\\n", arr[i]);')
    simple(SEC, '清空控制台', 'void', 'clear_console', 'void', 'printf("\\033[2J\\033[H");')
    simple(SEC, '打印信息日志', 'void', 'log_info', 'const char *msg', 'printf("[INFO] %s\\n", msg);')
    simple(SEC, '打印警告日志', 'void', 'log_warn', 'const char *msg', 'printf("[WARN] %s\\n", msg);')
    simple(SEC, '打印错误日志', 'void', 'log_error', 'const char *msg', 'printf("[ERROR] %s\\n", msg);')

# ============================================================
#  22. 矩阵工具
# ============================================================
def family_matrix():
    SEC = '矩阵工具'
    simple(SEC, '创建 rows x cols 双精度矩阵', 'double**', 'mat_create', 'int rows, int cols',
           'if (rows <= 0 || cols <= 0) return NULL;', 'double **m = (double**)malloc(rows * sizeof(double*));',
           'if (!m) return NULL;', 'for (int i = 0; i < rows; i++) { m[i] = (double*)calloc(cols, sizeof(double)); if (!m[i]) return NULL; }',
           'return m;')
    simple(SEC, '释放矩阵', 'void', 'mat_free', 'double **m, int rows',
           'if (!m) return;', 'for (int i = 0; i < rows; i++) free(m[i]);', 'free(m);')
    simple(SEC, '用值填充矩阵', 'void', 'mat_fill', 'double **m, int rows, int cols, double v',
           'for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) m[i][j] = v;')
    simple(SEC, '打印矩阵', 'void', 'mat_print', 'double **m, int rows, int cols',
           'for (int i = 0; i < rows; i++) { for (int j = 0; j < cols; j++) printf("%.2f ", m[i][j]); printf("\\n"); }')
    simple(SEC, '矩阵转置(写入 out)', 'void', 'mat_transpose', 'double **m, int rows, int cols, double **out',
           'for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) out[j][i] = m[i][j];')
    simple(SEC, '矩阵加法(out = a + b)', 'void', 'mat_add', 'double **a, double **b, int rows, int cols, double **out',
           'for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) out[i][j] = a[i][j] + b[i][j];')
    simple(SEC, '矩阵减法(out = a - b)', 'void', 'mat_sub', 'double **a, double **b, int rows, int cols, double **out',
           'for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) out[i][j] = a[i][j] - b[i][j];')
    simple(SEC, '矩阵乘法(out = a * b)', 'void', 'mat_mul', 'double **a, int ar, int ac, double **b, int bc, double **out',
           'for (int i = 0; i < ar; i++) for (int j = 0; j < bc; j++) { out[i][j] = 0; for (int k = 0; k < ac; k++) out[i][j] += a[i][k] * b[k][j]; }')
    simple(SEC, '单位矩阵', 'void', 'mat_identity', 'double **m, int n',
           'for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) m[i][j] = (i == j) ? 1.0 : 0.0;')
    simple(SEC, '数乘矩阵', 'void', 'mat_scalar_mul', 'double **m, int rows, int cols, double s, double **out',
           'for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) out[i][j] = m[i][j] * s;')
    simple(SEC, '方阵迹(对角线之和)', 'double', 'mat_trace', 'double **m, int n',
           'double t = 0;', 'for (int i = 0; i < n; i++) t += m[i][i];', 'return t;')
    simple(SEC, '2x2 行列式', 'double', 'mat_det2', 'double **m',
           'return m[0][0] * m[1][1] - m[0][1] * m[1][0];')
    simple(SEC, '3x3 行列式', 'double', 'mat_det3', 'double **m',
           'return m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1]) - m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0]) + m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]);')
    simple(SEC, '矩阵元素和', 'double', 'mat_sum', 'double **m, int rows, int cols',
           'double s = 0;', 'for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) s += m[i][j];', 'return s;')
    simple(SEC, '矩阵最大值', 'double', 'mat_max', 'double **m, int rows, int cols',
           'double v = m[0][0];', 'for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) if (m[i][j] > v) v = m[i][j];', 'return v;')
    simple(SEC, '矩阵最小值', 'double', 'mat_min', 'double **m, int rows, int cols',
           'double v = m[0][0];', 'for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) if (m[i][j] < v) v = m[i][j];', 'return v;')
    simple(SEC, '行元素和', 'double', 'mat_row_sum', 'double **m, int cols, int row',
           'double s = 0;', 'for (int j = 0; j < cols; j++) s += m[row][j];', 'return s;')
    simple(SEC, '列元素和', 'double', 'mat_col_sum', 'double **m, int rows, int col',
           'double s = 0;', 'for (int i = 0; i < rows; i++) s += m[i][col];', 'return s;')
    simple(SEC, '复制矩阵', 'double**', 'mat_copy', 'double **m, int rows, int cols',
           'double **r = mat_create(rows, cols);', 'if (!r) return NULL;',
           'for (int i = 0; i < rows; i++) memcpy(r[i], m[i], cols * sizeof(double));', 'return r;')

# ============================================================
#  23. 向量与杂项
# ============================================================
def family_misc():
    SEC = '向量与杂项'
    simple(SEC, '向量点积', 'double', 'dot_product', 'double a[], double b[], int size',
           'double s = 0;', 'for (int i = 0; i < size; i++) s += a[i] * b[i];', 'return s;')
    simple(SEC, '二维向量长度', 'double', 'vector_length_2d', 'double x, double y', 'return sqrt(x * x + y * y);')
    simple(SEC, '三维向量长度', 'double', 'vector_length_3d', 'double x, double y, double z', 'return sqrt(x * x + y * y + z * z);')
    simple(SEC, '二维向量归一化(写入 out)', 'void', 'normalize_2d', 'double x, double y, double *ox, double *oy',
           'double len = sqrt(x * x + y * y);', 'if (len == 0) { *ox = 0; *oy = 0; return; }', '*ox = x / len; *oy = y / len;')
    simple(SEC, '二维叉积(带符号面积)', 'double', 'cross_product_2d', 'double ax, double ay, double bx, double by',
           'return ax * by - ay * bx;')
    simple(SEC, '移动平均(写入 out)', 'void', 'moving_average', 'double arr[], int size, int window, double out[]',
           'for (int i = 0; i < size; i++) { double s = 0; int c = 0;',
           '    for (int j = (i - window + 1 < 0) ? 0 : i - window + 1; j <= i; j++) { s += arr[j]; c++; }',
           '    out[i] = s / c; }')
    simple(SEC, '整数数组转 double 数组', 'void', 'int_array_to_double', 'int src[], double dst[], int size',
           'for (int i = 0; i < size; i++) dst[i] = (double)src[i];')
    simple(SEC, 'double 数组转 int 数组', 'void', 'double_array_to_int', 'double src[], int dst[], int size',
           'for (int i = 0; i < size; i++) dst[i] = (int)src[i];')
    simple(SEC, 'Base64 编码(需free)', 'char*', 'base64_encode', 'const uint8_t *data, int len',
           'static const char tbl[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";',
           'int out_len = ((len + 2) / 3) * 4;', 'char *out = (char*)malloc(out_len + 1);', 'if (!out) return NULL;',
           'int i = 0, j = 0;', 'for (; i + 2 < len; i += 3) {',
           '    unsigned v = ((unsigned)data[i] << 16) | ((unsigned)data[i+1] << 8) | (unsigned)data[i+2];',
           '    out[j++] = tbl[(v >> 18) & 63]; out[j++] = tbl[(v >> 12) & 63]; out[j++] = tbl[(v >> 6) & 63]; out[j++] = tbl[v & 63];',
           '}', 'int rem = len - i;', 'if (rem == 1) {',
           '    unsigned v = (unsigned)data[i] << 16;', '    out[j++] = tbl[(v >> 18) & 63]; out[j++] = tbl[(v >> 12) & 63]; out[j++] = \'=\'; out[j++] = \'=\';',
           '} else if (rem == 2) {',
           '    unsigned v = ((unsigned)data[i] << 16) | ((unsigned)data[i+1] << 8);',
           '    out[j++] = tbl[(v >> 18) & 63]; out[j++] = tbl[(v >> 12) & 63]; out[j++] = tbl[(v >> 6) & 63]; out[j++] = \'=\';',
           '}', 'out[j] = \'\\0\';', 'return out;')
    simple(SEC, 'Base64 解码(需free)', 'uint8_t*', 'base64_decode', 'const char *s, int *out_len',
           'static const int T[] = {-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,62,-1,-1,-1,63,52,53,54,55,56,57,58,59,60,61,-1,-1,-1,-1,-1,-1,-1,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,-1,-1,-1,-1,-1,-1,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,-1,-1,-1,-1,-1};',
           'int len = str_len(s);', 'uint8_t *out = (uint8_t*)malloc((len / 4) * 3 + 3);', 'if (!out) return NULL;',
           'int j = 0, val = 0, bits = 0;', 'for (int i = 0; i < len; i++) {',
           '    if (s[i] == \'=\') break;', '    int d = ((unsigned char)s[i] < 128) ? T[(unsigned char)s[i]] : -1;', '    if (d < 0) continue;',
           '    val = (val << 6) | d; bits += 6;',
           '    if (bits >= 8) { bits -= 8; out[j++] = (uint8_t)((val >> bits) & 0xFF); }', '}',
           '*out_len = j;', 'return out;')
    simple(SEC, 'URL 编码(需free)', 'char*', 'url_encode_str', 'const char *s',
           'static const char hex[] = "0123456789ABCDEF";', 'int n = str_len(s);',
           'char *r = (char*)malloc(n * 3 + 1);', 'if (!r) return NULL;', 'int j = 0;',
           'for (int i = 0; i < n; i++) { unsigned char c = (unsigned char)s[i];',
           '    if (isalnum(c) || c == \'-\' || c == \'_\' || c == \'.\' || c == \'~\') r[j++] = (char)c;',
           '    else { r[j++] = \'%\'; r[j++] = hex[c >> 4]; r[j++] = hex[c & 15]; } }',
           'r[j] = \'\\0\';', 'return r;')

# ============================================================
#  24. 字符串工具（第二批）
# ============================================================
def family_string2():
    SEC = '字符串工具(第二批)'
    simple(SEC, '忽略大小写判断是否包含子串', 'int', 'str_contains_ignore_case', 'const char *haystack, const char *needle',
           'int n = str_len(needle);', 'if (n == 0) return 1;', 'const char *p = haystack;',
           'while (*p) { int ok = 1; for (int i = 0; i < n; i++) if (char_to_lower(p[i]) != char_to_lower(needle[i])) { ok = 0; break; } if (ok) return 1; p++; }',
           'return 0;')
    simple(SEC, '忽略大小写比较字符串', 'int', 'str_compare_case_insensitive', 'const char *a, const char *b',
           'while (*a && *b) { if (char_to_lower(*a) != char_to_lower(*b)) break; a++; b++; }',
           'return (unsigned char)char_to_lower(*a) - (unsigned char)char_to_lower(*b);')
    simple(SEC, '忽略大小写判断回文', 'int', 'str_is_palindrome_ignore_case', 'const char *str',
           'int len = str_len(str);', 'for (int i = 0; i < len / 2; i++) if (char_to_lower(str[i]) != char_to_lower(str[len - 1 - i])) return 0;',
           'return 1;')
    simple(SEC, '反转每个单词内部的字母', 'void', 'str_reverse_each_word', 'char *str',
           'int len = str_len(str), i = 0;',
           'while (i < len) { while (i < len && str[i] == \' \') i++; int s = i; while (i < len && str[i] != \' \') i++; int a = s, b = i - 1; while (a < b) { char t = str[a]; str[a] = str[b]; str[b] = t; a++; b--; } }')
    simple(SEC, '字符串左循环移动 n 位', 'void', 'str_shift_left', 'char *str, int n',
           'int len = str_len(str);', 'if (len == 0) return;', 'n %= len;',
           'for (int k = 0; k < n; k++) { char c = str[0]; for (int i = 0; i < len - 1; i++) str[i] = str[i + 1]; str[len - 1] = c; }')
    simple(SEC, '字符串右循环移动 n 位', 'void', 'str_shift_right', 'char *str, int n',
           'int len = str_len(str);', 'if (len == 0) return;', 'n %= len;',
           'for (int k = 0; k < n; k++) { char c = str[len - 1]; for (int i = len - 1; i > 0; i--) str[i] = str[i - 1]; str[0] = c; }')
    simple(SEC, '去除相邻重复字符', 'void', 'str_deduplicate_chars', 'char *str',
           'char *w = str; char prev = \'\\0\';', 'while (*str) { if (*str != prev) { *w++ = *str; prev = *str; } str++; }', '*w = \'\\0\';')
    simple(SEC, '删除所有辅音字母', 'void', 'str_remove_consonants', 'char *str',
           'char *w = str;', 'while (*str) { if (!is_alpha_char(*str) || is_vowel_char(*str)) *w++ = *str; str++; }', '*w = \'\\0\';')
    simple(SEC, '统计辅音字母个数', 'int', 'str_count_consonants', 'const char *str',
           'int c = 0;', 'while (*str) { if (is_alpha_char(*str) && !is_vowel_char(*str)) c++; str++; }', 'return c;')
    simple(SEC, '尾部追加一个字符', 'void', 'str_append_char', 'char *buf, int buf_size, char c',
           'int n = str_len(buf);', 'if (n + 1 < buf_size) { buf[n] = c; buf[n + 1] = \'\\0\'; }')
    simple(SEC, '删除第一个字符', 'void', 'str_remove_first_char', 'char *str',
           'if (*str) { char *p = str; while (*p) { *p = *(p + 1); p++; } }')
    simple(SEC, '删除最后一个字符', 'void', 'str_remove_last_char', 'char *str',
           'int n = str_len(str);', 'if (n > 0) str[n - 1] = \'\\0\';')
    simple(SEC, '查找第 n 次出现的子串下标(0起)', 'int', 'str_find_nth', 'const char *str, const char *sub, int n',
           'int cnt = 0, sl = str_len(sub);', 'if (n < 0 || sl == 0) return -1;', 'const char *p = str;',
           'while ((p = str_find(p, sub)) != NULL) { if (cnt == n) return (int)(p - str); cnt++; p += sl; }', 'return -1;')
    simple(SEC, '统计数字字符个数', 'int', 'str_count_digits', 'const char *str',
           'int c = 0;', 'while (*str) { if (is_digit_char(*str)) c++; str++; }', 'return c;')
    simple(SEC, '统计字母个数', 'int', 'str_count_letters', 'const char *str',
           'int c = 0;', 'while (*str) { if (is_alpha_char(*str)) c++; str++; }', 'return c;')
    simple(SEC, '统计大写字母个数', 'int', 'str_count_uppercase', 'const char *str',
           'int c = 0;', 'while (*str) { if (is_upper_char(*str)) c++; str++; }', 'return c;')
    simple(SEC, '统计小写字母个数', 'int', 'str_count_lowercase', 'const char *str',
           'int c = 0;', 'while (*str) { if (is_lower_char(*str)) c++; str++; }', 'return c;')
    simple(SEC, '统计空格个数', 'int', 'str_count_spaces', 'const char *str',
           'int c = 0;', 'while (*str) { if (*str == \' \') c++; str++; }', 'return c;')
    simple(SEC, '把连续多个空格合并为一个', 'void', 'str_normalize_spaces', 'char *str',
           'char *w = str; int sp = 0;',
           'while (*str) { if (*str == \' \' || *str == \'\\t\') { if (!sp && w != str) { *w++ = \' \'; sp = 1; } } else { *w++ = *str; sp = 0; } str++; }',
           'if (w != str && w[-1] == \' \') w--;', '*w = \'\\0\';')
    simple(SEC, '取每个单词首字母缩写', 'char*', 'str_abbreviate', 'const char *str, char *buf, int buf_size',
           'int k = 0, in = 0;', 'if (buf_size <= 0) return buf;',
           'while (*str && k < buf_size - 1) { if (is_space_char(*str)) in = 0; else if (!in) { buf[k++] = *str; in = 1; } str++; }',
           'buf[k] = \'\\0\';', 'return buf;')
    simple(SEC, '提取第 n 个单词(0起)', 'char*', 'str_word_at', 'const char *str, int n, char *buf, int buf_size',
           'int idx = 0, k = 0, in = 0;', 'if (buf_size <= 0) return buf;', 'buf[0] = \'\\0\';',
           'while (*str) {',
           '    if (is_space_char(*str)) { in = 0; str++; continue; }',
           '    if (!in) { in = 1; if (idx == n) { while (*str && !is_space_char(*str) && k < buf_size - 1) buf[k++] = *str++; buf[k] = \'\\0\'; return buf; } idx++; }',
           '    str++;',
           '}', 'return buf;')
    simple(SEC, '敏感信息打码(保留后4位)', 'char*', 'str_mask_sensitive', 'const char *str, char *buf, int buf_size',
           'int n = str_len(str);', 'if (buf_size <= 0) return buf;',
           'int keep = (n < 4) ? n : 4, mask = n - keep, k = 0;',
           'for (int i = 0; i < mask && k < buf_size - 1; i++) buf[k++] = \'*\';',
           'for (int i = mask; i < n && k < buf_size - 1; i++) buf[k++] = str[i];', 'buf[k] = \'\\0\';', 'return buf;')
    simple(SEC, '简单邮箱格式校验', 'int', 'str_is_valid_email', 'const char *s',
           'const char *at = str_find(s, "@");', 'if (!at || at == s) return 0;',
           'const char *dot = strrchr(s, \'.\');', 'if (!dot || dot < at || dot[1] == \'\\0\') return 0;', 'return 1;')
    simple(SEC, '统计句子数(. ! ?)', 'int', 'str_count_sentences', 'const char *str',
           'int c = 0;', 'while (*str) { if (*str == \'.\' || *str == \'!\' || *str == \'?\') c++; str++; }', 'return c;')
    simple(SEC, '最长回文子串长度(动态规划)', 'int', 'str_longest_palindrome_substr_len', 'const char *s',
           'int n = str_len(s);', 'if (n < 2) return n;',
           'int *dp = (int*)calloc((size_t)n * n, sizeof(int));', 'if (!dp) return n > 0 ? 1 : 0;',
           'int best = 1;', 'for (int i = 0; i < n; i++) dp[i * n + i] = 1;',
           'for (int i = 0; i < n - 1; i++) if (s[i] == s[i + 1]) { dp[i * n + i + 1] = 1; best = 2; }',
           'for (int len = 3; len <= n; len++) for (int i = 0; i + len - 1 < n; i++) {',
           '    int j = i + len - 1;', '    if (s[i] == s[j] && dp[(i + 1) * n + j - 1]) { dp[i * n + j] = 1; if (len > best) best = len; } }',
           'free(dp);', 'return best;')
    simple(SEC, '反转元音字母顺序', 'void', 'str_reverse_vowels', 'char *str',
           'int len = str_len(str), i = 0, j = len - 1;',
           'while (i < j) { while (i < j && !is_vowel_char(str[i])) i++; while (i < j && !is_vowel_char(str[j])) j--;',
           '    if (i < j) { char t = str[i]; str[i] = str[j]; str[j] = t; i++; j--; } }')
    simple(SEC, '删除所有数字', 'void', 'str_remove_digits', 'char *str',
           'char *w = str;', 'while (*str) { if (!is_digit_char(*str)) *w++ = *str; str++; }', '*w = \'\\0\';')
    simple(SEC, '只保留数字', 'void', 'str_keep_digits_only', 'char *str',
           'char *w = str;', 'while (*str) { if (is_digit_char(*str)) *w++ = *str; str++; }', '*w = \'\\0\';')
    simple(SEC, '只保留字母', 'void', 'str_keep_letters_only', 'char *str',
           'char *w = str;', 'while (*str) { if (is_alpha_char(*str)) *w++ = *str; str++; }', '*w = \'\\0\';')
    simple(SEC, '用字符填满缓冲区', 'void', 'str_fill', 'char *buf, int buf_size, char c, int len',
           'if (!buf || buf_size <= 0) return;', 'int n = (len < buf_size - 1) ? len : buf_size - 1;',
           'for (int i = 0; i < n; i++) buf[i] = c;', 'buf[n] = \'\\0\';')
    simple(SEC, '交换两个位置的字符', 'void', 'str_swap_chars', 'char *str, int i, int j',
           'int n = str_len(str);', 'if (i < 0 || j < 0 || i >= n || j >= n) return;',
           'char t = str[i]; str[i] = str[j]; str[j] = t;')
    simple(SEC, '最短单词长度', 'int', 'str_shortest_word_len', 'const char *str',
           'int best = 0, cur = 0, started = 0;',
           'while (*str) { if (is_space_char(*str)) { if (started && (best == 0 || cur < best)) best = cur; cur = 0; started = 0; } else { cur++; started = 1; } str++; }',
           'if (started && (best == 0 || cur < best)) best = cur;', 'return best;')
    simple(SEC, '平均单词长度', 'double', 'str_avg_word_len', 'const char *str',
           'int words = 0, chars = 0, in = 0;',
           'while (*str) { if (is_space_char(*str)) in = 0; else { chars++; if (!in) { words++; in = 1; } } str++; }',
           'return (words == 0) ? 0.0 : (double)chars / words;')
    simple(SEC, '字符串是否为空', 'int', 'str_is_empty', 'const char *str', 'return (str == NULL || *str == \'\\0\');')

# ============================================================
#  25. 数论与数学（第二批）
# ============================================================
def family_math2():
    SEC = '数论与数学(第二批)'
    simple(SEC, '三数最大公约数', 'int', 'gcd3', 'int a, int b, int c', 'return gcd(gcd(a, b), c);')
    simple(SEC, '四数最大公约数', 'int', 'gcd4', 'int a, int b, int c, int d', 'return gcd(gcd(a, b), gcd(c, d));')
    simple(SEC, '三数最小公倍数', 'long long', 'lcm3', 'int a, int b, int c', 'return lcm(lcm(a, b), c);')
    simple(SEC, '是否互质', 'int', 'is_relatively_prime', 'int a, int b', 'return gcd(a, b) == 1;')
    simple(SEC, '模加法 (a+b)%m', 'long long', 'mod_add', 'long long a, long long b, long long m',
           'return ((a % m) + (b % m)) % m;')
    simple(SEC, '模减法 (a-b)%m', 'long long', 'mod_sub', 'long long a, long long b, long long m',
           'long long r = ((a % m) - (b % m)) % m;', 'return (r < 0) ? r + m : r;')
    simple(SEC, '模乘法 (a*b)%m', 'long long', 'mod_mul', 'long long a, long long b, long long m',
           'return ((a % m) * (b % m)) % m;')
    simple(SEC, '模逆元(需互质，否则-1)', 'int', 'mod_inverse', 'int a, int m',
           'int x, y;', 'int g = extended_gcd(a, m, &x, &y);', 'if (g != 1) return -1;', 'return ((x % m) + m) % m;')
    simple(SEC, '快速加倍法求斐波那契', 'long long', 'fast_fibonacci', 'int n',
           'if (n < 0) return -1;', 'if (n == 0) return 0;',
           'int bit = 0;', 'while ((1 << bit) <= n && bit < 31) bit++;', 'bit--;',
           'long long a = 0, b = 1;',
           'for (int i = bit; i >= 0; i--) { long long c = a * (2 * b - a); long long d = a * a + b * b;',
           '    if ((n >> i) & 1) { a = d; b = c + d; } else { a = c; b = d; } }',
           'return a;')
    simple(SEC, '整数平方根', 'int', 'integer_sqrt', 'int n',
           'if (n < 0) return -1;', 'int r = (int)sqrt((double)n);',
           'while ((long long)(r + 1) * (r + 1) <= n) r++;', 'while ((long long)r * r > n) r--;', 'return r;')
    simple(SEC, '整数立方根', 'int', 'integer_cbrt', 'int n',
           'if (n < 0) return -1;', 'int r = (int)cbrt((double)n);',
           'while ((long long)(r + 1) * (r + 1) * (r + 1) <= n) r++;', 'return r;')
    simple(SEC, 'log2 向下取整', 'int', 'log2_floor', 'int n',
           'if (n <= 0) return -1;', 'int r = 0;', 'while (n >>= 1) r++;', 'return r;')
    simple(SEC, 'log10 向下取整', 'int', 'log10_floor', 'int n',
           'if (n <= 0) return -1;', 'int r = 0;', 'while (n >= 10) { n /= 10; r++; }', 'return r;')
    simple(SEC, '阶乘取模 n! % m', 'long long', 'factorial_mod', 'int n, long long m',
           'long long r = 1;', 'for (int i = 2; i <= n; i++) r = (r * i) % m;', 'return r;')
    simple(SEC, '是否为斐波那契数', 'int', 'is_fibonacci_number', 'int n',
           'if (n < 0) return 0;', 'long long x = 5LL * n * n;',
           'long long r1 = (long long)sqrt((double)(x + 4)), r2 = (long long)sqrt((double)(x - 4));',
           'return (r1 * r1 == x + 4) || (r2 * r2 == x - 4);')
    simple(SEC, 'n 在 base 进制下的位数', 'int', 'count_digits_in_base', 'int n, int base',
           'if (base < 2) return 0;', 'if (n == 0) return 1;', 'int c = 0;', 'while (n) { n /= base; c++; }', 'return c;')
    simple(SEC, '是否为半素数(两素数之积)', 'int', 'is_semiprime', 'int n',
           'if (n < 4) return 0;', 'for (int i = 2; i * i <= n; i++) if (n % i == 0) return is_prime(i) && is_prime(n / i);',
           'return 0;')
    simple(SEC, '是否为回文素数', 'int', 'is_palindromic_prime', 'int n', 'return is_prime(n) && is_palindrome_num(n);')
    simple(SEC, '字符串是否只含0/1', 'int', 'is_binary_str', 'const char *s',
           'if (!s || !*s) return 0;', 'while (*s) { if (*s != \'0\' && *s != \'1\') return 0; s++; }', 'return 1;')
    simple(SEC, '字符串是否只含八进制字符', 'int', 'is_octal_str', 'const char *s',
           'if (!s || !*s) return 0;', 'while (*s) { if (!is_octal_char(*s)) return 0; s++; }', 'return 1;')
    simple(SEC, '字符串是否为十进制数', 'int', 'is_decimal_str', 'const char *s',
           'if (!s || !*s) return 0;', 'while (*s) { if (!is_digit_char(*s)) return 0; s++; }', 'return 1;')
    simple(SEC, '字符串是否为十六进制数', 'int', 'is_hex_str', 'const char *s',
           'if (!s || !*s) return 0;', 'while (*s) { if (!is_hex_char(*s)) return 0; s++; }', 'return 1;')
    simple(SEC, '字符串是否为数字(可带符号)', 'int', 'is_number_string', 'const char *s',
           'if (!s || !*s) return 0;', 'if (*s == \'+\' || *s == \'-\') s++;',
           'if (!*s) return 0;', 'while (*s) { if (!is_digit_char(*s)) return 0; s++; }', 'return 1;')
    simple(SEC, 'Stein 二进制最大公约数', 'int', 'gcd_binary', 'int a, int b',
           'a = abs(a); b = abs(b);', 'if (a == 0) return b;', 'if (b == 0) return a;',
           'int shift = 0;', 'while (!((a | b) & 1)) { a >>= 1; b >>= 1; shift++; }',
           'while (!(a & 1)) a >>= 1;',
           'while (b) { while (!(b & 1)) b >>= 1; if (a > b) { int t = a; a = b; b = t; } b -= a; }',
           'return a << shift;')
    simple(SEC, '到下一个素数的间隔', 'int', 'prime_gap', 'int n', 'return next_prime(n) - n;')
    simple(SEC, '二进制末尾 0 的个数', 'int', 'count_trailing_zeros', 'uint32_t n',
           'if (n == 0) return 32;', 'int c = 0;', 'while (!(n & 1u)) { n >>= 1; c++; }', 'return c;')
    simple(SEC, '是否为 3 的幂', 'int', 'is_power_of_three', 'int n',
           'if (n <= 0) return 0;', 'while (n % 3 == 0) n /= 3;', 'return n == 1;')
    simple(SEC, '是否为 4 的幂', 'int', 'is_power_of_four', 'int n', 'return is_power_of_two(n) && (n % 3 == 1);')
    simple(SEC, '数字 d 在 n 中出现次数', 'int', 'digit_frequency', 'int n, int d',
           'int c = 0;', 'if (n < 0) n = -n;', 'while (n) { if (n % 10 == d) c++; n /= 10; }', 'return c;')

# ============================================================
#  26. 数组工具（第二批）
# ============================================================
def family_array2():
    SEC = '数组工具(第二批)'
    simple(SEC, '绝对值之和', 'long long', 'sum_abs_int', 'int arr[], int size',
           'long long s = 0;', 'for (int i = 0; i < size; i++) s += UTILS_ABS(arr[i]);', 'return s;')
    simple(SEC, '两个数组点积', 'long long', 'dot_product_int', 'int a[], int b[], int size',
           'long long s = 0;', 'for (int i = 0; i < size; i++) s += (long long)a[i] * b[i];', 'return s;')
    simple(SEC, '最长连续相同段长度', 'int', 'longest_run_length', 'int arr[], int size',
           'if (size < 1) return 0;', 'int best = 1, cur = 1;',
           'for (int i = 1; i < size; i++) { if (arr[i] == arr[i - 1]) { cur++; if (cur > best) best = cur; } else cur = 1; }',
           'return best;')
    simple(SEC, '局部极大值下标', 'int', 'find_local_max_idx', 'int arr[], int size',
           'if (size <= 0) return -1;', 'if (size == 1) return 0;',
           'if (arr[0] >= arr[1]) return 0;', 'if (arr[size - 1] >= arr[size - 2]) return size - 1;',
           'for (int i = 1; i < size - 1; i++) if (arr[i] >= arr[i - 1] && arr[i] >= arr[i + 1]) return i;', 'return -1;')
    simple(SEC, '局部极小值下标', 'int', 'find_local_min_idx', 'int arr[], int size',
           'if (size <= 0) return -1;', 'if (size == 1) return 0;',
           'if (arr[0] <= arr[1]) return 0;', 'if (arr[size - 1] <= arr[size - 2]) return size - 1;',
           'for (int i = 1; i < size - 1; i++) if (arr[i] <= arr[i - 1] && arr[i] <= arr[i + 1]) return i;', 'return -1;')
    simple(SEC, '平衡点下标(左右和相等)', 'int', 'equilibrium_index', 'int arr[], int size',
           'long long total = 0, left = 0;', 'for (int i = 0; i < size; i++) total += arr[i];',
           'for (int i = 0; i < size; i++) { total -= arr[i]; if (left == total) return i; left += arr[i]; }', 'return -1;')
    simple(SEC, '反转子数组 [lo,hi]', 'void', 'reverse_subarray', 'int arr[], int size, int lo, int hi',
           'if (lo < 0) lo = 0;', 'if (hi >= size) hi = size - 1;', 'while (lo < hi) { int t = arr[lo]; arr[lo] = arr[hi]; arr[hi] = t; lo++; hi--; }')
    simple(SEC, '交换两个元素', 'void', 'swap_elements_int', 'int arr[], int i, int j',
           'int t = arr[i]; arr[i] = arr[j]; arr[j] = t;')
    simple(SEC, '填充递增序列 start..start+n-1', 'void', 'fill_sequence_int', 'int arr[], int size, int start',
           'for (int i = 0; i < size; i++) arr[i] = start + i;')
    simple(SEC, '填充随机浮点数范围', 'void', 'fill_random_double_range', 'double arr[], int size, double min, double max',
           'for (int i = 0; i < size; i++) arr[i] = min + (max - min) * ((double)rand() / (RAND_MAX + 1.0));')
    simple(SEC, '删除所有等于 value 的元素', 'int', 'remove_all_value', 'int arr[], int *size, int value',
           'int j = 0;', 'for (int i = 0; i < *size; i++) if (arr[i] != value) arr[j++] = arr[i];',
           '*size = j;', 'return j;')
    simple(SEC, '不同元素个数', 'int', 'count_distinct_int', 'int arr[], int size',
           'int c = 0;', 'for (int i = 0; i < size; i++) { int dup = 0; for (int j = 0; j < i; j++) if (arr[j] == arr[i]) { dup = 1; break; } if (!dup) c++; }',
           'return c;')
    simple(SEC, '最小值下标', 'int', 'array_min_index', 'int arr[], int size',
           'if (size <= 0) return -1;', 'int idx = 0;', 'for (int i = 1; i < size; i++) if (arr[i] < arr[idx]) idx = i;', 'return idx;')
    simple(SEC, '最大值下标', 'int', 'array_max_index', 'int arr[], int size',
           'if (size <= 0) return -1;', 'int idx = 0;', 'for (int i = 1; i < size; i++) if (arr[i] > arr[idx]) idx = i;', 'return idx;')
    simple(SEC, '倒序打印数组', 'void', 'print_array_reverse_int', 'int arr[], int size',
           'for (int i = size - 1; i >= 0; i--) printf("%d ", arr[i]);', 'printf("\\n");')
    simple(SEC, '是否严格递增', 'int', 'check_sorted_strict', 'int arr[], int size',
           'for (int i = 1; i < size; i++) if (arr[i] <= arr[i - 1]) return 0;', 'return 1;')
    simple(SEC, '相邻最小差值(需已排序)', 'int', 'min_gap', 'int arr[], int size',
           'if (size < 2) return 0;', 'int g = arr[1] - arr[0];', 'for (int i = 2; i < size; i++) { int d = arr[i] - arr[i - 1]; if (d < g) g = d; }', 'return g;')
    simple(SEC, '相邻最大差值(需已排序)', 'int', 'max_gap', 'int arr[], int size',
           'if (size < 2) return 0;', 'int g = arr[1] - arr[0];', 'for (int i = 2; i < size; i++) { int d = arr[i] - arr[i - 1]; if (d > g) g = d; }', 'return g;')

# ============================================================
#  27. 链表工具（对已有 ListNode 的扩展）
# ============================================================
def family_list_extra():
    SEC = '链表工具(扩展)'
    simple(SEC, '取第 n 个节点的值', 'int', 'list_get_nth', 'ListNode *head, int n, int *out',
           'int i = 0;', 'while (head) { if (i == n) { *out = head->data; return 0; } i++; head = head->next; }', 'return -1;')
    simple(SEC, '删除第 n 个节点', 'int', 'list_delete_nth', 'ListNode **head, int n',
           'if (!head) return -1;', 'if (n == 0) { ListNode *t = *head; if (!t) return -1; *head = t->next; free(t); return 0; }',
           'ListNode *p = *head;', 'for (int i = 0; p && i < n - 1; i++) p = p->next;',
           'if (!p || !p->next) return -1;', 'ListNode *t = p->next; p->next = t->next; free(t);', 'return 0;')
    simple(SEC, '在第 n 个位置插入', 'int', 'list_insert_nth', 'ListNode **head, int n, int data',
           'if (!head || n < 0) return -1;', 'if (n == 0) { list_insert_head(head, data); return 0; }',
           'ListNode *p = *head;', 'for (int i = 0; p && i < n - 1; i++) p = p->next;',
           'if (!p) return -1;', 'ListNode *node = list_create(data);', 'if (!node) return -1;',
           'node->next = p->next; p->next = node;', 'return 0;')
    simple(SEC, '检测链表是否有环(快慢指针)', 'int', 'list_has_cycle', 'ListNode *head',
           'ListNode *slow = head, *fast = head;',
           'while (fast && fast->next) { slow = slow->next; fast = fast->next->next; if (slow == fast) return 1; }', 'return 0;')
    simple(SEC, '链表中间节点', 'ListNode*', 'list_middle_node', 'ListNode *head',
           'ListNode *slow = head, *fast = head;', 'while (fast && fast->next) { slow = slow->next; fast = fast->next->next; }', 'return slow;')
    simple(SEC, '由数组构建链表', 'ListNode*', 'list_from_array', 'int arr[], int size',
           'ListNode *head = NULL;', 'for (int i = size - 1; i >= 0; i--) list_insert_head(&head, arr[i]);', 'return head;')
    simple(SEC, '链表最大值', 'int', 'list_max', 'ListNode *head',
           'if (!head) return 0;', 'int m = head->data;', 'for (ListNode *p = head->next; p; p = p->next) if (p->data > m) m = p->data;', 'return m;')
    simple(SEC, '链表最小值', 'int', 'list_min', 'ListNode *head',
           'if (!head) return 0;', 'int m = head->data;', 'for (ListNode *p = head->next; p; p = p->next) if (p->data < m) m = p->data;', 'return m;')
    simple(SEC, '链表元素之和', 'long long', 'list_sum', 'ListNode *head',
           'long long s = 0;', 'for (ListNode *p = head; p; p = p->next) s += p->data;', 'return s;')
    simple(SEC, '链表排序(冒泡)', 'void', 'list_sort', 'ListNode *head',
           'if (!head) return;', 'int swapped = 1;',
           'while (swapped) { swapped = 0; for (ListNode *p = head; p->next; p = p->next) if (p->data > p->next->data) { int t = p->data; p->data = p->next->data; p->next->data = t; swapped = 1; } }')
    simple(SEC, '合并两个升序链表', 'ListNode*', 'list_merge_sorted', 'ListNode *a, ListNode *b',
           'ListNode *head = NULL, **tail = &head;',
           'while (a && b) { if (a->data <= b->data) { *tail = a; a = a->next; } else { *tail = b; b = b->next; } tail = &(*tail)->next; }',
           '*tail = a ? a : b;', 'return head;')
    simple(SEC, '把 b 接到 a 末尾(破坏性)', 'ListNode*', 'list_append_list', 'ListNode *a, ListNode *b',
           'if (!a) return b;', 'ListNode *p = a;', 'while (p->next) p = p->next;', 'p->next = b;', 'return a;')
    simple(SEC, '深拷贝链表', 'ListNode*', 'list_clone', 'ListNode *head',
           'ListNode *new_head = NULL, **tail = &new_head;',
           'while (head) { ListNode *node = list_create(head->data); if (!node) return NULL; *tail = node; tail = &node->next; head = head->next; }',
           'return new_head;')
    simple(SEC, '链表是否升序', 'int', 'list_is_sorted', 'ListNode *head',
           'for (ListNode *p = head; p && p->next; p = p->next) if (p->data > p->next->data) return 0;', 'return 1;')
    simple(SEC, '统计值等于 value 的节点数', 'int', 'list_count_value', 'ListNode *head, int value',
           'int c = 0;', 'for (ListNode *p = head; p; p = p->next) if (p->data == value) c++;', 'return c;')
    simple(SEC, '链表右旋 k 次', 'void', 'list_rotate_right', 'ListNode **head, int k',
           'if (!head || !*head || k <= 0) return;', 'int len = list_length(*head);', 'k %= len;', 'if (k == 0) return;',
           'ListNode *p = *head;', 'for (int i = 0; i < len - k - 1; i++) p = p->next;',
           'ListNode *new_head = p->next;', 'p->next = NULL;',
           'ListNode *t = new_head;', 'while (t->next) t = t->next;', 't->next = *head;', '*head = new_head;')

# ============================================================
#  28. 进制转换（第二批）
# ============================================================
def family_convert2():
    SEC = '进制转换(第二批)'
    simple(SEC, '定宽二进制字符串(补0)', 'char*', 'int_to_binary_padded', 'int num, int width, char *buf, int buf_size',
           'if (!buf || buf_size <= 0) return buf;', 'if (width >= buf_size) width = buf_size - 1;',
           'for (int i = width - 1; i >= 0; i--) { if (i < buf_size - 1) buf[i] = (num & 1) ? \'1\' : \'0\'; num >>= 1; }',
           'buf[width] = \'\\0\';', 'return buf;')
    simple(SEC, 'BCD 码转二进制', 'int', 'bcd_to_binary', 'int bcd',
           'int r = 0, m = 1;', 'while (bcd) { r += (bcd & 0x0F) * m; m *= 10; bcd >>= 4; }', 'return r;')
    simple(SEC, '二进制转 BCD 码', 'int', 'binary_to_bcd', 'int n',
           'int bcd = 0, shift = 0;', 'while (n) { bcd |= (n % 10) << (shift * 4); n /= 10; shift++; }', 'return bcd;')
    simple(SEC, '浮点位模式转整数', 'int', 'float_bits_to_int', 'float f',
           'int i;', 'memcpy(&i, &f, 4);', 'return i;')
    simple(SEC, '整数位模式转浮点', 'float', 'int_bits_to_float', 'int i',
           'float f;', 'memcpy(&f, &i, 4);', 'return f;')
    simple(SEC, '浮点转十六进制字符串', 'char*', 'double_to_hex_str', 'double d, char *buf',
           'sprintf(buf, "%a", d);', 'return buf;')
    simple(SEC, '字符转 ASCII 码', 'int', 'char_to_ascii_code', 'char c', 'return (int)(unsigned char)c;')
    simple(SEC, 'ASCII 码转字符', 'char', 'ascii_code_to_char', 'int code', 'return (char)code;')
    simple(SEC, '整数转大端字节', 'void', 'int_to_bytes_be', 'int val, uint8_t out[4]',
           'out[0] = (uint8_t)((val >> 24) & 0xFF);', 'out[1] = (uint8_t)((val >> 16) & 0xFF);',
           'out[2] = (uint8_t)((val >> 8) & 0xFF);', 'out[3] = (uint8_t)(val & 0xFF);')
    simple(SEC, '大端字节转整数', 'int', 'bytes_to_int_be', 'uint8_t b[4]',
           'return ((int)b[0] << 24) | ((int)b[1] << 16) | ((int)b[2] << 8) | b[3];')
    simple(SEC, '定宽十六进制字符串(补0)', 'char*', 'int_to_hex_padded', 'int num, int width, char *buf, int buf_size',
           'if (!buf || buf_size <= 0) return buf;', 'if (width >= buf_size) width = buf_size - 1;',
           'for (int i = width - 1; i >= 0; i--) { int d = num & 0xF; buf[i] = int_to_hex_char(d); num >>= 4; }',
           'buf[width] = \'\\0\';', 'return buf;')

# ============================================================
#  29. 几何工具（第二批）
# ============================================================
def family_geom2():
    SEC = '几何工具(第二批)'
    simple(SEC, '三点坐标三角形面积', 'double', 'triangle_area_coords', 'double x1, double y1, double x2, double y2, double x3, double y3',
           'return fabs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0);')
    simple(SEC, '多边形面积(鞋带公式)', 'double', 'polygon_area', 'double x[], double y[], int n',
           'if (n < 3) return 0.0;', 'double s = 0;',
           'for (int i = 0; i < n; i++) { int j = (i + 1) % n; s += x[i] * y[j] - x[j] * y[i]; }',
           'return fabs(s) / 2.0;')
    simple(SEC, '点到直线距离', 'double', 'distance_point_line', 'double px, double py, double ax, double ay, double bx, double by',
           'double dx = bx - ax, dy = by - ay;', 'double len = sqrt(dx * dx + dy * dy);',
           'if (len == 0) return distance_2d(px, py, ax, ay);',
           'return fabs(dy * px - dx * py + bx * ay - by * ax) / len;')
    simple(SEC, '点到线段距离', 'double', 'distance_point_segment', 'double px, double py, double ax, double ay, double bx, double by',
           'double dx = bx - ax, dy = by - ay;', 'double len2 = dx * dx + dy * dy;',
           'double t = (len2 == 0) ? 0 : ((px - ax) * dx + (py - ay) * dy) / len2;',
           'if (t < 0) t = 0;', 'if (t > 1) t = 1;',
           'double cx = ax + t * dx, cy = ay + t * dy;', 'return distance_2d(px, py, cx, cy);')
    simple(SEC, '扇形面积', 'double', 'area_sector', 'double r, double angle_rad', 'return 0.5 * r * r * angle_rad;')
    simple(SEC, '弧长', 'double', 'arc_length', 'double r, double angle_rad', 'return r * angle_rad;')
    simple(SEC, '正弦(角度制)', 'double', 'sin_deg', 'double deg', 'return sin(degrees_to_radians(deg));')
    simple(SEC, '余弦(角度制)', 'double', 'cos_deg', 'double deg', 'return cos(degrees_to_radians(deg));')
    simple(SEC, '正切(角度制)', 'double', 'tan_deg', 'double deg', 'return tan(degrees_to_radians(deg));')
    simple(SEC, '两向量夹角(弧度)', 'double', 'angle_between_vectors', 'double ax, double ay, double bx, double by',
           'double la = sqrt(ax * ax + ay * ay), lb = sqrt(bx * bx + by * by);',
           'if (la == 0 || lb == 0) return 0.0;',
           'double c = (ax * bx + ay * by) / (la * lb);', 'if (c > 1) c = 1;', 'if (c < -1) c = -1;', 'return acos(c);')
    simple(SEC, '点是否在线段上', 'int', 'is_point_on_segment', 'double px, double py, double ax, double ay, double bx, double by',
           'double d = distance_point_segment(px, py, ax, ay, bx, by);', 'return (d < 1e-9);')

# ============================================================
#  30. 数值工具（第二批）
# ============================================================
def family_numtool2():
    SEC = '数值工具(第二批)'
    simple(SEC, '是否为正数', 'int', 'is_positive_double', 'double x', 'return x > 0;')
    simple(SEC, '是否为负数', 'int', 'is_negative_double', 'double x', 'return x < 0;')
    simple(SEC, '是否为零', 'int', 'is_zero_double', 'double x', 'return x == 0;')
    simple(SEC, '阶跃函数', 'double', 'step_function', 'double x', 'return (x >= 0) ? 1.0 : 0.0;')
    simple(SEC, '保留 n 位小数', 'double', 'round_to_n_decimals', 'double x, int n',
           'double p = pow(10, n);', 'return round(x * p) / p;')
    simple(SEC, '整数绝对差', 'int', 'abs_diff_int', 'int a, int b', 'return UTILS_ABS(a - b);')
    simple(SEC, '浮点绝对差', 'double', 'abs_diff_double', 'double a, double b', 'return fabs(a - b);')
    simple(SEC, '两数最大值', 'double', 'max_double', 'double a, double b', 'return (a > b) ? a : b;')
    simple(SEC, '两数最小值', 'double', 'min_double', 'double a, double b', 'return (a < b) ? a : b;')
    simple(SEC, '分数约分', 'void', 'reduce_fraction', 'int num, int den, int *out_num, int *out_den',
           'if (den == 0) return;', 'int g = gcd(num, den);', '*out_num = num / g;', '*out_den = den / g;')
    simple(SEC, '是否为有限浮点数', 'int', 'is_finite_double', 'double x', 'return isfinite(x);')
    simple(SEC, '是否为 NaN', 'int', 'is_nan_double', 'double x', 'return isnan(x);')

# ============================================================
#  31. 编码与杂项（第二批）
# ============================================================
def family_misc2():
    SEC = '编码与杂项(第二批)'
    simple(SEC, 'URL 解码(需free)', 'char*', 'url_decode_str', 'const char *s',
           'if (!s) return NULL;', 'int n = str_len(s);', 'char *r = (char*)malloc(n + 1);', 'if (!r) return NULL;',
           'int j = 0;', 'for (int i = 0; i < n; i++) {',
           '    if (s[i] == \'%\' && i + 2 < n) { int hi = hex_char_to_int(s[i + 1]), lo = hex_char_to_int(s[i + 2]);',
           '        if (hi >= 0 && lo >= 0) { r[j++] = (char)((hi << 4) | lo); i += 2; continue; } }',
           '    if (s[i] == \'+\') r[j++] = \' \'; else r[j++] = s[i]; }',
           'r[j] = \'\\0\';', 'return r;')
    simple(SEC, 'HTML 转义(需free)', 'char*', 'html_escape_str', 'const char *s',
           'if (!s) return NULL;', 'int n = str_len(s);', 'char *r = (char*)malloc(n * 6 + 1);', 'if (!r) return NULL;',
           'int j = 0;', 'for (int i = 0; i < n; i++) {',
           '    switch (s[i]) { case \'&\': strcpy(r + j, "&amp;"); j += 5; break; case \'<\': strcpy(r + j, "&lt;"); j += 4; break; case \'>\': strcpy(r + j, "&gt;"); j += 4; break; case \'\"\': strcpy(r + j, "&quot;"); j += 6; break; case \'\\\'\': strcpy(r + j, "&#39;"); j += 5; break; default: r[j++] = s[i]; } }',
           'r[j] = \'\\0\';', 'return r;')
    simple(SEC, '小写十六进制字符串', 'char*', 'bytes_to_hex_lower', 'const uint8_t *data, uint16_t len, char *buf, uint16_t buf_size',
           'if (buf_size < (uint16_t)(len * 2 + 1)) { if (buf && buf_size > 0) buf[0] = \'\\0\'; return buf; }',
           'for (uint16_t i = 0; i < len; i++) {',
           '    buf[i * 2] = int_to_hex_char((data[i] >> 4) & 0x0F);', '    buf[i * 2 + 1] = int_to_hex_char(data[i] & 0x0F); }',
           'for (uint16_t i = 0; i < len * 2; i++) buf[i] = char_to_lower(buf[i]);', 'buf[len * 2] = \'\\0\';', 'return buf;')
    simple(SEC, '十六进制字符串转大写', 'char*', 'hex_str_to_upper', 'const char *hex, char *buf, int buf_size',
           'if (!hex || !buf || buf_size <= 0) return buf;', 'int i = 0;',
           'while (hex[i] && i < buf_size - 1) { buf[i] = char_to_upper(hex[i]); i++; }', 'buf[i] = \'\\0\';', 'return buf;')

# ============================================================
#  32. 图算法（第二批）
# ============================================================
def family_graph2():
    SEC = '图算法(第二批)'
    simple(SEC, '图是否连通', 'int', 'graph_is_connected', 'Graph *g',
           'if (!g || g->n <= 1) return 1;', 'char *vis = (char*)calloc(g->n, 1);',
           'int *q = (int*)malloc(g->n * sizeof(int));', 'int head = 0, tail = 0;',
           'vis[0] = 1; q[tail++] = 0;',
           'while (head < tail) { int v = q[head++]; for (int i = 0; i < g->n; i++) if (g->adj[v][i] && !vis[i]) { vis[i] = 1; q[tail++] = i; } }',
           'int ok = 1;', 'for (int i = 0; i < g->n; i++) if (!vis[i]) { ok = 0; break; }',
           'free(vis); free(q);', 'return ok;')
    simple(SEC, '无向边数量', 'int', 'graph_edge_count', 'Graph *g',
           'if (!g) return 0;', 'int c = 0;', 'for (int i = 0; i < g->n; i++) for (int j = i + 1; j < g->n; j++) if (g->adj[i][j]) c++;', 'return c;')
    simple(SEC, '图的转置(out 需已分配 n x n)', 'void', 'graph_transpose', 'Graph *g, int **out',
           'if (!g) return;', 'for (int i = 0; i < g->n; i++) for (int j = 0; j < g->n; j++) out[j][i] = g->adj[i][j];')
    simple(SEC, 'u 到 v 是否有路径(BFS)', 'int', 'graph_path_exists', 'Graph *g, int u, int v',
           'if (!g || u < 0 || v < 0 || u >= g->n || v >= g->n) return 0;',
           'if (u == v) return 1;', 'char *vis = (char*)calloc(g->n, 1);',
           'int *q = (int*)malloc(g->n * sizeof(int));', 'int head = 0, tail = 0;',
           'vis[u] = 1; q[tail++] = u;',
           'while (head < tail) { int x = q[head++]; for (int i = 0; i < g->n; i++) if (g->adj[x][i] && !vis[i]) { if (i == v) { free(vis); free(q); return 1; } vis[i] = 1; q[tail++] = i; } }',
           'free(vis); free(q);', 'return 0;')

# ============================================================
#  33. 随机工具（第二批）
# ============================================================
def family_random2():
    SEC = '随机工具(第二批)'
    simple(SEC, '排除某个值的区间随机数', 'int', 'rand_range_excluding', 'int min, int max, int excl',
           'int v;', 'do { v = rand_range(min, max); } while (v == excl && min < max);', 'return v;')
    simple(SEC, '填充随机整数列表', 'void', 'rand_fill_int_list', 'int arr[], int size, int min, int max',
           'for (int i = 0; i < size; i++) arr[i] = rand_range(min, max);')
    simple(SEC, '填充随机浮点数组', 'void', 'rand_fill_float_array', 'double arr[], int size, double min, double max',
           'for (int i = 0; i < size; i++) arr[i] = min + (max - min) * ((double)rand() / (RAND_MAX + 1.0));')
    simple(SEC, '随机数字字符', 'char', 'rand_digit_char', 'void', 'return (char)(\'0\' + rand() % 10);')
    simple(SEC, '随机小写字母', 'char', 'rand_lowercase_char', 'void', 'return (char)(\'a\' + rand() % 26);')
    simple(SEC, '随机大写字母', 'char', 'rand_uppercase_char', 'void', 'return (char)(\'A\' + rand() % 26);')
    simple(SEC, '随机字母(大小写)', 'char', 'rand_letter_char', 'void', 'return (rand() % 2) ? rand_uppercase_char() : rand_lowercase_char();')

# ============================================================
#  34. 二叉搜索树（第二批）
# ============================================================
def family_bst_extra():
    SEC = '二叉搜索树(第二批)'
    simple(SEC, '最小值', 'int', 'bst_min_value', 'BSTNode *root',
           'BSTNode *n = bst_find_min(root);', 'return n ? n->data : 0;')
    simple(SEC, '最大值', 'int', 'bst_max_value', 'BSTNode *root',
           'BSTNode *n = bst_find_max(root);', 'return n ? n->data : 0;')
    simple(SEC, '叶子节点数', 'int', 'bst_count_leaves', 'BSTNode *root',
           'if (!root) return 0;', 'if (!root->left && !root->right) return 1;',
           'return bst_count_leaves(root->left) + bst_count_leaves(root->right);')
    simple(SEC, '内部节点数', 'int', 'bst_count_internal', 'BSTNode *root',
           'if (!root || (!root->left && !root->right)) return 0;',
           'return 1 + bst_count_internal(root->left) + bst_count_internal(root->right);')
    simple(SEC, '是否为合法 BST', 'int', 'bst_is_valid', 'BSTNode *root',
           'if (!root) return 1;',
           'if (root->left && bst_max_value(root->left) >= root->data) return 0;',
           'if (root->right && bst_min_value(root->right) <= root->data) return 0;',
           'return bst_is_valid(root->left) && bst_is_valid(root->right);')
    simple(SEC, '是否平衡(左右子树高差<=1)', 'int', 'bst_is_balanced', 'BSTNode *root',
           'if (!root) return 1;',
           'int l = bst_height(root->left), r = bst_height(root->right);',
           'if (abs(l - r) > 1) return 0;',
           'return bst_is_balanced(root->left) && bst_is_balanced(root->right);')
    simple(SEC, '镜像翻转(返回新根)', 'BSTNode*', 'bst_mirror', 'BSTNode *root',
           'if (!root) return NULL;', 'BSTNode *t = root->left; root->left = root->right; root->right = t;',
           'bst_mirror(root->left);', 'bst_mirror(root->right);', 'return root;')
    simple(SEC, '两棵树是否相同', 'int', 'bst_same_tree', 'BSTNode *a, BSTNode *b',
           'if (!a && !b) return 1;', 'if (!a || !b) return 0;',
           'return (a->data == b->data) && bst_same_tree(a->left, b->left) && bst_same_tree(a->right, b->right);')
    simple(SEC, '值为 value 的节点深度(根为0)', 'int', 'bst_depth_of_value', 'BSTNode *root, int value',
           'int d = 0;', 'while (root) { if (root->data == value) return d; d++; root = (value < root->data) ? root->left : root->right; }',
           'return -1;')

# ============================================================
#  35. 矩阵工具（第二批）
# ============================================================
def family_matrix2():
    SEC = '矩阵工具(第二批)'
    simple(SEC, '创建全零矩阵', 'double**', 'mat_zeros', 'int rows, int cols', 'return mat_create(rows, cols);')
    simple(SEC, '创建全一矩阵', 'double**', 'mat_ones', 'int rows, int cols',
           'double **m = mat_create(rows, cols);', 'if (!m) return NULL;', 'mat_fill(m, rows, cols, 1.0);', 'return m;')
    simple(SEC, '创建单位矩阵', 'double**', 'mat_identity_alloc', 'int n',
           'double **m = mat_create(n, n);', 'if (!m) return NULL;', 'mat_identity(m, n);', 'return m;')
    simple(SEC, '转置并返回新矩阵', 'double**', 'mat_transpose_alloc', 'double **m, int rows, int cols',
           'double **out = mat_create(cols, rows);', 'if (!out) return NULL;', 'mat_transpose(m, rows, cols, out);', 'return out;')
    simple(SEC, '是否对称矩阵', 'int', 'mat_is_symmetric', 'double **m, int n',
           'for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if (m[i][j] != m[j][i]) return 0;', 'return 1;')
    simple(SEC, '矩阵加标量', 'void', 'mat_add_scalar', 'double **m, int rows, int cols, double s, double **out',
           'for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) out[i][j] = m[i][j] + s;')
    simple(SEC, '矩阵取负', 'void', 'mat_negate', 'double **m, int rows, int cols, double **out',
           'for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) out[i][j] = -m[i][j];')
    simple(SEC, '矩阵元素平均值', 'double', 'mat_avg', 'double **m, int rows, int cols',
           'if (rows <= 0 || cols <= 0) return 0.0;', 'return mat_sum(m, rows, cols) / (rows * cols);')
    simple(SEC, '随机填充矩阵', 'void', 'mat_rand_fill', 'double **m, int rows, int cols, double min, double max',
           'for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) m[i][j] = min + (max - min) * ((double)rand() / (RAND_MAX + 1.0));')

# ============================================================
#  36. 数组统计（第二批）
# ============================================================
def family_stat2():
    SEC = '数组统计(第二批)'
    simple(SEC, '众数(double数组)', 'double', 'mode_double_array', 'double arr[], int size',
           'double best = arr[0]; int bestc = 0;',
           'for (int i = 0; i < size; i++) { int c = 0; for (int j = 0; j < size; j++) if (arr[j] == arr[i]) c++; if (c > bestc) { bestc = c; best = arr[i]; } }',
           'return best;')
    simple(SEC, '中位数(int数组)', 'double', 'median_int_array', 'int arr[], int size',
           'if (size == 0) return 0.0;', 'int *c = (int*)malloc(size * sizeof(int));', 'if (!c) return 0.0;',
           'memcpy(c, arr, size * sizeof(int));',
           'for (int i = 0; i < size - 1; i++) for (int j = 0; j < size - 1 - i; j++) if (c[j] > c[j + 1]) { int t = c[j]; c[j] = c[j + 1]; c[j + 1] = t; }',
           'double r = (size % 2) ? c[size / 2] : (c[size / 2 - 1] + c[size / 2]) / 2.0;', 'free(c);', 'return r;')
    simple(SEC, '方差(int数组)', 'double', 'variance_int_array', 'int arr[], int size',
           'if (size < 1) return 0.0;', 'double m = avg_int_array(arr, size), s = 0;',
           'for (int i = 0; i < size; i++) { double d = arr[i] - m; s += d * d; }', 'return s / size;')
    simple(SEC, '标准差(int数组)', 'double', 'stddev_int_array', 'int arr[], int size',
           'return sqrt(variance_int_array(arr, size));')
    simple(SEC, '极差(int数组)', 'int', 'range_int_array', 'int arr[], int size',
           'if (size < 1) return 0;', 'return max_int_array(arr, size) - min_int_array(arr, size);')

# ============================================================
#  37. 数组工具（类型变体，第二批）
# ============================================================
def family_array_variants():
    SEC = '数组工具(类型变体)'
    TYPES = [
        ('int','int','long long','int',''),
        ('long','long','long long','int',''),
        ('long_long','long long','long long','int',''),
        ('short','short','long long','int',''),
        ('uint','unsigned int','unsigned long long','uint',''),
        ('float','float','double','float','fabs(v)'),
        ('double','double','double','float','fabs(v)'),
        ('char','char','int','int',''),
        ('uint8','uint8_t','unsigned long long','uint',''),
        ('uint16','uint16_t','unsigned long long','uint',''),
        ('uint32','uint32_t','unsigned long long','uint',''),
    ]
    for suf, T, SUM, CAT, ABSB in TYPES:
        is_u = (CAT == 'uint')
        add(SEC, '最小值下标', 'int', f'{suf}_array_min_index', f'{T} arr[], int size',
            ['if (size <= 0) return -1;', 'int idx = 0;', 'for (int i = 1; i < size; i++) if (arr[i] < arr[idx]) idx = i;', 'return idx;'])
        add(SEC, '最大值下标', 'int', f'{suf}_array_max_index', f'{T} arr[], int size',
            ['if (size <= 0) return -1;', 'int idx = 0;', 'for (int i = 1; i < size; i++) if (arr[i] > arr[idx]) idx = i;', 'return idx;'])
        add(SEC, '统计大于 value 的元素个数', 'int', f'{suf}_array_count_greater', f'{T} arr[], int size, {T} value',
            ['int c = 0;', 'for (int i = 0; i < size; i++) if (arr[i] > value) c++;', 'return c;'])
        add(SEC, '统计小于 value 的元素个数', 'int', f'{suf}_array_count_less', f'{T} arr[], int size, {T} value',
            ['int c = 0;', 'for (int i = 0; i < size; i++) if (arr[i] < value) c++;', 'return c;'])
        add(SEC, '每个元素乘以 scalar', 'void', f'{suf}_array_scale', f'{T} arr[], int size, {T} scalar',
            [f'for (int i = 0; i < size; i++) arr[i] = ({T})(arr[i] * scalar);'])
        add(SEC, '每个元素加 offset', 'void', f'{suf}_array_add_scalar', f'{T} arr[], int size, {T} offset',
            [f'for (int i = 0; i < size; i++) arr[i] = ({T})(arr[i] + offset);'])
        add(SEC, '数组是否有重复', 'int', f'{suf}_array_has_duplicates', f'{T} arr[], int size',
            ['for (int i = 0; i < size; i++) for (int j = i + 1; j < size; j++) if (arr[i] == arr[j]) return 1;', 'return 0;'])
        add(SEC, '数组左旋 k 位', 'void', f'{suf}_array_rotate_left', f'{T} arr[], int size, int k',
            ['if (size <= 1 || k <= 0) return;', 'k %= size;', 'if (k == 0) return;',
             f'{T} *tmp = ({T}*)malloc(k * sizeof({T}));', 'if (!tmp) return;',
             'for (int i = 0; i < k; i++) tmp[i] = arr[i];',
             'for (int i = 0; i < size - k; i++) arr[i] = arr[i + k];',
             'for (int i = 0; i < k; i++) arr[size - k + i] = tmp[i];', 'free(tmp);'])
        if not is_u and ABSB:
            absbody = ABSB
        elif not is_u:
            absbody = 'UTILS_ABS(v)'
        else:
            absbody = None
        if absbody:
            add(SEC, '绝对值之和', SUM, f'{suf}_array_sum_abs', f'{T} arr[], int size',
                [f'{SUM} s = 0;', f'for (int i = 0; i < size; i++) {{ {T} v = arr[i]; s += ( {absbody} ); }}', 'return s;'])

# ============================================================
#  38. 数组工具（第三批）
# ============================================================
def family_array3():
    SEC = '数组工具(第三批)'
    simple(SEC, '连续相同段的数量', 'int', 'count_runs_int', 'int arr[], int size',
           'if (size < 1) return 0;', 'int runs = 1;',
           'for (int i = 1; i < size; i++) if (arr[i] != arr[i - 1]) runs++;', 'return runs;')
    simple(SEC, '是否为 1..n 的排列', 'int', 'is_permutation_int', 'int arr[], int size',
           'for (int v = 1; v <= size; v++) { int f = 0; for (int i = 0; i < size; i++) if (arr[i] == v) { f = 1; break; } if (!f) return 0; }',
           'return 1;')
    simple(SEC, '任意两数最大乘积', 'long long', 'max_pair_product', 'int arr[], int size',
           'if (size < 2) return 0;', 'long long best = (long long)arr[0] * arr[1];',
           'for (int i = 0; i < size; i++) for (int j = i + 1; j < size; j++) { long long p = (long long)arr[i] * arr[j]; if (p > best) best = p; }',
           'return best;')
    simple(SEC, '找缺失数字(0..n 缺一个)', 'int', 'find_missing_number', 'int arr[], int n',
           'long long total = (long long)n * (n + 1) / 2, s = 0;',
           'for (int i = 0; i < n; i++) s += arr[i];', 'return (int)(total - s);')
    simple(SEC, '找重复数字(1..n 有一个重复)', 'int', 'find_duplicate_number', 'int arr[], int n',
           'long long sum = 0, sum_sq = 0;', 'long long expect = (long long)n * (n + 1) / 2;',
           'long long expect_sq = (long long)n * (n + 1) * (2 * n + 1) / 6;',
           'for (int i = 0; i < n + 1; i++) { sum += arr[i]; sum_sq += (long long)arr[i] * arr[i]; }',
           'long long diff_sum = sum - expect;', 'long long diff_sq = sum_sq - expect_sq;',
           'return (int)((diff_sq / diff_sum + diff_sum) / 2);')
    simple(SEC, '把 0 移到末尾', 'void', 'move_zeros_to_end', 'int arr[], int size',
           'int j = 0;', 'for (int i = 0; i < size; i++) if (arr[i] != 0) arr[j++] = arr[i];',
           'while (j < size) arr[j++] = 0;')
    simple(SEC, '把负数移到前面', 'void', 'move_negatives_to_front', 'int arr[], int size',
           'int j = 0;', 'for (int i = 0; i < size; i++) if (arr[i] < 0) { int t = arr[i]; arr[i] = arr[j]; arr[j] = t; j++; }')
    simple(SEC, '奇偶分离(偶数在前)', 'void', 'separate_even_odd', 'int arr[], int size',
           'int j = 0;', 'for (int i = 0; i < size; i++) if (arr[i] % 2 == 0) { int t = arr[i]; arr[i] = arr[j]; arr[j] = t; j++; }')
    simple(SEC, '区间和(直接计算)', 'long long', 'sum_range_int', 'int arr[], int lo, int hi',
           'long long s = 0;', 'for (int i = lo; i <= hi; i++) s += arr[i];', 'return s;')
    simple(SEC, '排序数组中 target 出现次数', 'int', 'count_occurrences_sorted', 'int arr[], int size, int target',
           'int l = lower_bound_int(arr, size, target);', 'if (l >= size || arr[l] != target) return 0;',
           'int u = upper_bound_int(arr, size, target);', 'return u - l;')
    simple(SEC, '按 k 分组反转', 'void', 'reverse_in_groups', 'int arr[], int size, int k',
           'if (k <= 1) return;', 'for (int i = 0; i < size; i += k) { int lo = i, hi = (i + k - 1 < size) ? i + k - 1 : size - 1; while (lo < hi) { int t = arr[lo]; arr[lo] = arr[hi]; arr[hi] = t; lo++; hi--; } }')
    simple(SEC, '是否为山脉数组', 'int', 'is_mountain_array', 'int arr[], int size',
           'if (size < 3) return 0;', 'int i = 0;',
           'while (i + 1 < size && arr[i] < arr[i + 1]) i++;',
           'if (i == 0 || i == size - 1) return 0;',
           'while (i + 1 < size && arr[i] > arr[i + 1]) i++;', 'return i == size - 1;')
    simple(SEC, '多数元素(Boyer-Moore)', 'int', 'majority_element', 'int arr[], int size',
           'int cand = arr[0], count = 1;',
           'for (int i = 1; i < size; i++) { if (arr[i] == cand) count++; else if (--count == 0) { cand = arr[i]; count = 1; } }',
           'return cand;')
    simple(SEC, '和为 target 的数对数量', 'int', 'pairs_with_sum', 'int arr[], int size, int target',
           'int c = 0;', 'for (int i = 0; i < size; i++) for (int j = i + 1; j < size; j++) if (arr[i] + arr[j] == target) c++;', 'return c;')
    simple(SEC, '单调递增栈(写入结果数组)', 'int', 'next_greater_element', 'int arr[], int size, int out[]',
           'for (int i = 0; i < size; i++) { out[i] = -1; for (int j = i + 1; j < size; j++) if (arr[j] > arr[i]) { out[i] = arr[j]; break; } }',
           'return 0;')
    simple(SEC, '山峰下标(严格单峰)', 'int', 'find_peak_index', 'int arr[], int size',
           'if (size < 3) return -1;', 'for (int i = 1; i < size - 1; i++) if (arr[i] > arr[i - 1] && arr[i] > arr[i + 1]) return i;', 'return -1;')

# ============================================================
#  39. 字符串工具（第三批）
# ============================================================
def family_string3():
    SEC = '字符串工具(第三批)'
    simple(SEC, 'ROT13 副本(需free)', 'char*', 'str_rot13_copy', 'const char *s',
           'if (!s) return NULL;', 'char *r = (char*)malloc(str_len(s) + 1);', 'if (!r) return NULL;',
           'int i = 0;', 'while (s[i]) { char c = s[i]; if (is_alpha_char(c)) { char b = is_upper_char(c) ? \'A\' : \'a\'; r[i] = (char)(b + (c - b + 13) % 26); } else r[i] = c; i++; }',
           'r[i] = \'\\0\';', 'return r;')
    simple(SEC, '凯撒加密副本(需free)', 'char*', 'str_caesar_copy', 'const char *s, int shift',
           'if (!s) return NULL;', 'char *r = (char*)malloc(str_len(s) + 1);', 'if (!r) return NULL;',
           'int i = 0;', 'while (s[i]) { char c = s[i]; if (is_alpha_char(c)) { char b = is_upper_char(c) ? \'A\' : \'a\'; r[i] = (char)(b + (c - b + shift % 26 + 26) % 26); } else r[i] = c; i++; }',
           'r[i] = \'\\0\';', 'return r;')
    simple(SEC, '替换所有子串(需free)', 'char*', 'str_replace_all', 'const char *s, const char *old, const char *new',
           'if (!s || !old || !*old) return NULL;', 'int count = str_count_substr(s, old);',
           'int old_len = str_len(old), new_len = str_len(new), slen = str_len(s);',
           'char *r = (char*)malloc(slen + count * (new_len - old_len) + 1);', 'if (!r) return NULL;',
           'const char *p = s;', 'char *w = r;',
           'while (*p) { if (strncmp(p, old, (size_t)old_len) == 0) { memcpy(w, new, (size_t)new_len); w += new_len; p += old_len; } else *w++ = *p++; }',
           '*w = \'\\0\';', 'return r;')
    simple(SEC, '提取数字(需free)', 'char*', 'str_extract_digits', 'const char *s',
           'if (!s) return NULL;', 'char *r = (char*)malloc(str_len(s) + 1);', 'if (!r) return NULL;',
           'int j = 0;', 'while (*s) { if (is_digit_char(*s)) r[j++] = *s; s++; }', 'r[j] = \'\\0\';', 'return r;')
    simple(SEC, '删除指定位置字符', 'void', 'str_remove_char_at', 'char *str, int pos',
           'int n = str_len(str);', 'if (pos < 0 || pos >= n) return;',
           'for (int i = pos; i < n; i++) str[i] = str[i + 1];')
    simple(SEC, '在指定位置插入字符', 'void', 'str_insert_char_at', 'char *str, int buf_size, int pos, char c',
           'int n = str_len(str);', 'if (pos < 0 || pos > n || n + 1 >= buf_size) return;',
           'for (int i = n; i >= pos; i--) str[i + 1] = str[i];', 'str[pos] = c;')
    simple(SEC, '是否所有字符相同', 'int', 'str_is_all_same_char', 'const char *str',
           'if (!str || !*str) return 0;', 'char c = str[0];', 'while (*str) { if (*str != c) return 0; str++; }', 'return 1;')
    simple(SEC, '是否有重复字符', 'int', 'str_has_duplicate_chars', 'const char *str',
           'for (int i = 0; str[i]; i++) for (int j = i + 1; str[j]; j++) if (str[i] == str[j]) return 1;', 'return 0;')
    simple(SEC, '两字符串最长公共前缀长度', 'int', 'str_longest_common_prefix', 'const char *a, const char *b',
           'int i = 0;', 'while (a[i] && b[i] && a[i] == b[i]) i++;', 'return i;')
    simple(SEC, '不同字符个数', 'int', 'str_count_unique_chars', 'const char *str',
           'int cnt[256] = {0}, c = 0;', 'while (*str) { if (!cnt[(unsigned char)*str]) c++; cnt[(unsigned char)*str] = 1; str++; }', 'return c;')
    simple(SEC, '最后一个单词长度', 'int', 'str_last_word_len', 'const char *str',
           'int n = str_len(str), len = 0;', 'int i = n - 1;',
           'while (i >= 0 && is_space_char(str[i])) i--;',
           'while (i >= 0 && !is_space_char(str[i])) { len++; i--; }', 'return len;')
    simple(SEC, '第一个单词长度', 'int', 'str_first_word_len', 'const char *str',
           'int len = 0;', 'while (*str && is_space_char(*str)) str++;', 'while (*str && !is_space_char(*str)) { len++; str++; }', 'return len;')
    simple(SEC, '是否包含任意给定字符', 'int', 'str_contains_any_char', 'const char *str, const char *chars',
           'while (*str) { if (str_find(chars, (char[]){*str, \'\\0\'})) return 1; str++; }', 'return 0;')
    simple(SEC, '括号是否匹配', 'int', 'str_is_balanced_parens', 'const char *str',
           'int depth = 0;', 'while (*str) { if (*str == \'(\') depth++; else if (*str == \')\') { if (--depth < 0) return 0; } str++; }', 'return depth == 0;')
    simple(SEC, '括号组是否合法({[]})', 'int', 'str_is_valid_brackets', 'const char *s',
           'int n = str_len(s);', 'char *st = (char*)malloc(n + 1);', 'if (!st) return 0;', 'int top = 0;',
           'while (*s) { char c = *s++;',
           '    if (c == \'(\' || c == \'[\' || c == \'{\') st[top++] = c;',
           '    else { if (top == 0) { free(st); return 0; } char o = st[--top];',
           '        if (!((o == \'(\' && c == \')\') || (o == \'[\' && c == \']\') || (o == \'{\' && c == \'}\'))) { free(st); return 0; } } }',
           'int ok = (top == 0);', 'free(st);', 'return ok;')
    simple(SEC, '字符串相似度(简单字符重合率0~100)', 'double', 'str_similarity', 'const char *a, const char *b',
           'int na = str_len(a), nb = str_len(b);', 'if (na + nb == 0) return 100.0;',
           'int same = 0;', 'int n = (na < nb) ? na : nb;', 'for (int i = 0; i < n; i++) if (a[i] == b[i]) same++;',
           'return 100.0 * same / ((na + nb + 1) / 2);')

# ============================================================
#  40. 数论与数学（第三批）
# ============================================================
def family_math3():
    SEC = '数论与数学(第三批)'
    simple(SEC, '数组的最大公约数', 'int', 'gcd_of_array', 'int arr[], int size',
           'if (size < 1) return 0;', 'int g = arr[0];', 'for (int i = 1; i < size; i++) g = gcd(g, arr[i]);', 'return g;')
    simple(SEC, '数组的最小公倍数', 'long long', 'lcm_of_array', 'int arr[], int size',
           'if (size < 1) return 0;', 'long long l = arr[0];', 'for (int i = 1; i < size; i++) l = lcm((int)l, arr[i]);', 'return l;')
    simple(SEC, '各位数字平方和', 'int', 'sum_of_squares_digits', 'int n',
           'int s = 0;', 'if (n < 0) n = -n;', 'while (n) { int d = n % 10; s += d * d; n /= 10; }', 'return s;')
    simple(SEC, '是否全数字数(1..len各一次)', 'int', 'is_pandigital', 'int n',
           'if (n <= 0) return 0;', 'int seen[10] = {0}, len = 0;', 'while (n) { int d = n % 10; if (d == 0 || seen[d]) return 0; seen[d] = 1; len++; n /= 10; }',
           'for (int i = 1; i <= len; i++) if (!seen[i]) return 0;', 'return 1;')
    simple(SEC, '是否重位数(各位相同)', 'int', 'is_repdigit', 'int n',
           'if (n < 0) n = -n;', 'int d = n % 10;', 'while (n) { if (n % 10 != d) return 0; n /= 10; }', 'return 1;')
    simple(SEC, '各位数字之积', 'int', 'digit_product', 'int n',
           'int p = 1;', 'if (n < 0) n = -n;', 'if (n == 0) return 0;', 'while (n) { p *= n % 10; n /= 10; }', 'return p;')
    simple(SEC, '第 n 个三角形数', 'long long', 'nth_triangular', 'int n', 'return (n <= 0) ? 0 : (long long)n * (n + 1) / 2;')
    simple(SEC, '前 n 个斐波那契和', 'long long', 'fib_sum_first', 'int n',
           'long long a = 0, b = 1, s = 0;', 'for (int i = 0; i < n; i++) { s += a; long long t = a + b; a = b; b = t; }', 'return s;')
    simple(SEC, '是否丑数(因子只有2,3,5)', 'int', 'is_ugly_number', 'int n',
           'if (n <= 0) return 0;', 'while (n % 2 == 0) n /= 2;', 'while (n % 3 == 0) n /= 3;', 'while (n % 5 == 0) n /= 5;', 'return n == 1;')
    simple(SEC, '是否无平方因子数', 'int', 'is_square_free', 'int n',
           'if (n < 1) return 0;', 'for (int i = 2; i * i <= n; i++) if (n % (i * i) == 0) return 0;', 'return 1;')
    simple(SEC, '无平方因子积(radical)', 'int', 'radical', 'int n',
           'int r = 1;', 'for (int i = 2; i * i <= n; i++) if (n % i == 0) { r *= i; while (n % i == 0) n /= i; }', 'if (n > 1) r *= n;', 'return r;')
    simple(SEC, '是否反素数(逆转仍是素数)', 'int', 'is_emirp', 'int n',
           'if (!is_prime(n)) return 0;', 'int r = reverse_int(n);', 'return (r != n) && is_prime(r);')
    simple(SEC, '1..n 中与 n 互质的个数', 'int', 'count_coprimes', 'int n',
           'int c = 0;', 'for (int i = 1; i <= n; i++) if (gcd(i, n) == 1) c++;', 'return c;')
    simple(SEC, '十进制转格雷码', 'uint32_t', 'int_to_gray', 'uint32_t n', 'return n ^ (n >> 1);')
    simple(SEC, '格雷码转十进制', 'uint32_t', 'gray_to_int', 'uint32_t g',
           'uint32_t n = 0;', 'while (g) { n ^= g; g >>= 1; }', 'return n;')

# ============================================================
#  41. 数值工具（第三批）
# ============================================================
def family_numtool3():
    SEC = '数值工具(第三批)'
    simple(SEC, '长整数裁剪', 'long', 'clamp_long', 'long v, long lo, long hi',
           'if (v < lo) return lo;', 'if (v > hi) return hi;', 'return v;')
    simple(SEC, '单精度裁剪', 'float', 'clamp_float', 'float v, float lo, float hi',
           'if (v < lo) return lo;', 'if (v > hi) return hi;', 'return v;')
    simple(SEC, '限制线性插值', 'double', 'lerp_clamped', 'double a, double b, double t',
           'if (t < 0) t = 0;', 'if (t > 1) t = 1;', 'return a + (b - a) * t;')
    simple(SEC, 'Smoothstep 平滑插值', 'double', 'smoothstep', 'double x',
           'if (x <= 0) return 0.0;', 'if (x >= 1) return 1.0;', 'return x * x * (3 - 2 * x);')
    simple(SEC, '归一化到 [0,1]', 'double', 'normalize_01', 'double x, double min, double max',
           'if (max == min) return 0.0;', 'return (x - min) / (max - min);')
    simple(SEC, '整数向上整除', 'long long', 'int_divide_ceil', 'long long a, long long b',
           'if (b == 0) return 0;', 'return (a + b - 1) / b;')
    simple(SEC, '整数向下整除', 'long long', 'int_divide_floor', 'long long a, long long b',
           'if (b == 0) return 0;', 'return a / b;')
    simple(SEC, '是否在区间内(含端点)', 'int', 'is_between_int', 'int v, int lo, int hi', 'return (v >= lo && v <= hi);')
    simple(SEC, '是否在区间内(浮点)', 'int', 'is_between_double', 'double v, double lo, double hi', 'return (v >= lo && v <= hi);')
    simple(SEC, '百分比变化', 'double', 'percent_delta', 'double a, double b',
           'if (a == 0) return 0.0;', 'return (b - a) * 100.0 / a;')
    simple(SEC, '三个数平均值', 'double', 'average_of_three', 'double a, double b, double c', 'return (a + b + c) / 3.0;')
    simple(SEC, '三个数乘积', 'double', 'product_of_three', 'double a, double b, double c', 'return a * b * c;')
    simple(SEC, '浮点符号(1/-1/0)', 'int', 'sign_double', 'double x', 'return (x > 0) - (x < 0);')
    simple(SEC, '百分比保留', 'double', 'percent_of', 'double part, double total', 'return (total == 0) ? 0.0 : part / total * 100.0;')
    simple(SEC, '两点在数轴上的距离', 'double', 'distance_1d', 'double a, double b', 'return fabs(a - b);')

# ============================================================
#  42. 位运算（第三批）
# ============================================================
def family_bit2():
    SEC = '位运算(第三批)'
    simple(SEC, '保留低 n 位', 'uint32_t', 'clear_high_bits', 'uint32_t val, int n',
           'if (n <= 0) return 0;', 'if (n >= 32) return val;', 'return val & ((1u << n) - 1);')
    simple(SEC, '按掩码翻转位', 'uint32_t', 'toggle_bits', 'uint32_t val, uint32_t mask', 'return val ^ mask;')
    simple(SEC, '按掩码置位', 'uint32_t', 'set_bits_mask', 'uint32_t val, uint32_t mask', 'return val | mask;')
    simple(SEC, '按掩码清位', 'uint32_t', 'clear_bits_mask', 'uint32_t val, uint32_t mask', 'return val & ~mask;')
    simple(SEC, '反转单个字节', 'uint8_t', 'bit_reverse_byte', 'uint8_t b',
           'uint8_t r = 0;', 'for (int i = 0; i < 8; i++) { r = (uint8_t)((r << 1) | (b & 1)); b >>= 1; }', 'return r;')
    simple(SEC, '16 位格雷码转换', 'uint16_t', 'int_to_gray16', 'uint16_t n', 'return (uint16_t)(n ^ (n >> 1));')
    simple(SEC, '判断是否只有一个 1', 'int', 'is_single_bit', 'uint32_t val',
           'return (val != 0) && ((val & (val - 1)) == 0);')
    simple(SEC, '最低位 1 的值', 'uint32_t', 'lowest_one', 'uint32_t val',
           'return val & (uint32_t)(-(int32_t)val);')

# ============================================================
#  43. 进制转换（第三批）
# ============================================================
def family_convert3():
    SEC = '进制转换(第三批)'
    simple(SEC, '字节转 8 位二进制字符串', 'char*', 'byte_to_bin_str', 'uint8_t b, char *buf, int buf_size',
           'if (!buf || buf_size < 9) return buf;', 'for (int i = 7; i >= 0; i--) buf[7 - i] = (b & (1u << i)) ? \'1\' : \'0\';', 'buf[8] = \'\\0\';', 'return buf;')
    simple(SEC, '16 位转二进制字符串', 'char*', 'word_to_bin_str', 'uint16_t w, char *buf, int buf_size',
           'if (!buf || buf_size < 17) return buf;', 'for (int i = 15; i >= 0; i--) buf[15 - i] = (w & (1u << i)) ? \'1\' : \'0\';', 'buf[16] = \'\\0\';', 'return buf;')
    simple(SEC, '浮点转整数(四舍五入)', 'long long', 'float_to_int_round', 'float f', 'return (long long)(f >= 0 ? f + 0.5f : f - 0.5f);')
    simple(SEC, '浮点转整数(截断)', 'long long', 'float_to_int_truncate', 'float f', 'return (long long)f;')
    simple(SEC, '整数转 long 字符串', 'char*', 'long_to_str', 'long v, char *buf', 'sprintf(buf, "%ld", v);', 'return buf;')
    simple(SEC, '字符数组转长整数(限长)', 'long', 'char_array_to_long', 'const char *s, int len',
           'long r = 0;', 'for (int i = 0; i < len && s[i]; i++) { if (!is_digit_char(s[i])) break; r = r * 10 + (s[i] - \'0\'); }', 'return r;')
    simple(SEC, '十进制字符串直接转十六进制字符串', 'char*', 'dec_str_to_hex_str', 'const char *dec, char *buf, int buf_size',
           '(void)buf_size;', 'long v = str_to_long(dec);', 'return int_to_hex_str((int)v, buf);')

# ============================================================
#  44. 控制台与调试（第三批）
# ============================================================
def family_console2():
    SEC = '控制台与调试(第三批)'
    simple(SEC, '打印进度条', 'void', 'print_progress_bar', 'int percent, int width',
           'if (percent < 0) percent = 0;', 'if (percent > 100) percent = 100;',
           'int fill = width * percent / 100;', 'printf("[");',
           'for (int i = 0; i < width; i++) putchar(i < fill ? \'#\' : \' \');',
           'printf("] %d%%\\n", percent);')
    simple(SEC, '打印带颜色的成功信息', 'void', 'print_ok', 'const char *msg', 'printf("\\033[32m[OK] %s\\033[0m\\n", msg);')
    simple(SEC, '打印带颜色的失败信息', 'void', 'print_fail', 'const char *msg', 'printf("\\033[31m[FAIL] %s\\033[0m\\n", msg);')
    simple(SEC, '打印带颜色的警告信息', 'void', 'print_warn', 'const char *msg', 'printf("\\033[33m[WARN] %s\\033[0m\\n", msg);')
    simple(SEC, '带时间戳打印普通日志', 'void', 'log_timestamp', 'const char *msg',
           'char ts[20];', 'get_time_str(ts);', 'printf("[%s] %s\\n", ts, msg);')
    simple(SEC, '定宽打印整数', 'void', 'print_padded_int', 'int v, int width', 'printf("%*d\\n", width, v);')
    simple(SEC, '打印布尔值', 'void', 'print_bool', 'int b', 'printf("%s\\n", b ? "true" : "false");')
    simple(SEC, '居中打印标题', 'void', 'print_center', 'const char *title, int width',
           'int n = str_len(title), pad = (width - n) / 2;',
           'if (pad < 0) pad = 0;', 'for (int i = 0; i < pad; i++) putchar(\' \');', 'printf("%s\\n", title);')

# ============================================================
#  45. 数列与序列
# ============================================================
def family_seq():
    SEC = '数列与序列'
    simple(SEC, '填充前 n 个斐波那契数', 'void', 'fibonacci_array', 'long long out[], int n',
           'if (n < 1) return;', 'out[0] = 0;', 'if (n > 1) out[1] = 1;',
           'for (int i = 2; i < n; i++) out[i] = out[i - 1] + out[i - 2];')
    simple(SEC, '填充前 n 个平方数', 'void', 'square_array', 'long long out[], int n',
           'for (int i = 0; i < n; i++) out[i] = (long long)(i + 1) * (i + 1);')
    simple(SEC, '填充前 n 个三角形数', 'void', 'triangular_array', 'long long out[], int n',
           'for (int i = 0; i < n; i++) out[i] = (long long)(i + 1) * (i + 2) / 2;')
    simple(SEC, '填充科拉茨序列', 'int', 'collatz_sequence', 'int n, int out[], int max_len',
           'int c = 0;', 'while (n != 1 && c < max_len) { out[c++] = n; n = (n % 2) ? 3 * n + 1 : n / 2; }',
           'if (c < max_len) out[c++] = 1;', 'return c;')
    simple(SEC, '杨辉三角第 n 行', 'int', 'pascal_row', 'int n, int out[], int *len',
           'if (n < 0) { *len = 0; return 0; }', '*len = n + 1;',
           'long long v = 1;', 'for (int k = 0; k <= n; k++) { out[k] = (int)v; v = v * (n - k) / (k + 1); }', 'return 0;')
    simple(SEC, '是否等差数列', 'int', 'is_arithmetic_sequence', 'int arr[], int size',
           'if (size < 3) return 1;', 'int d = arr[1] - arr[0];', 'for (int i = 2; i < size; i++) if (arr[i] - arr[i - 1] != d) return 0;', 'return 1;')
    simple(SEC, '是否等比数列', 'int', 'is_geometric_sequence', 'double arr[], int size',
           'if (size < 3) return 1;', 'if (arr[0] == 0) return 0;', 'double r = arr[1] / arr[0];',
           'for (int i = 2; i < size; i++) if (fabs(arr[i] / arr[i - 1] - r) > 1e-9) return 0;', 'return 1;')
    simple(SEC, '错排数(子阶乘)', 'long long', 'subfactorial', 'int n',
           'if (n < 0) return 0;', 'if (n == 0) return 1;', 'if (n == 1) return 0;',
           'long long a = 1, b = 0, c;', 'for (int i = 2; i <= n; i++) { c = (long long)(i - 1) * (a + b); a = b; b = c; }', 'return b;')
    simple(SEC, '第 n 个卢卡斯数', 'long long', 'lucas_number', 'int n',
           'if (n < 0) return -1;', 'if (n == 0) return 2;', 'if (n == 1) return 1;',
           'long long a = 2, b = 1, c;', 'for (int i = 2; i <= n; i++) { c = a + b; a = b; b = c; }', 'return b;')

# ============================================================
#  46. 文件工具（第三批）
# ============================================================
def family_file2():
    SEC = '文件工具(第三批)'
    simple(SEC, '清空文件内容', 'int', 'file_clear', 'const char *filename',
           'FILE *fp = fopen(filename, "w");', 'if (!fp) return -1;', 'fclose(fp);', 'return 0;')
    simple(SEC, '读取整个文件为字节(需free)', 'uint8_t*', 'file_read_all_bytes', 'const char *filename, size_t *out_len',
           'FILE *fp = fopen(filename, "rb");', 'if (!fp) return NULL;',
           'fseek(fp, 0, SEEK_END);', 'long sz = ftell(fp);', 'fseek(fp, 0, SEEK_SET);',
           'uint8_t *buf = (uint8_t*)malloc((size_t)sz);', 'if (!buf) { fclose(fp); return NULL; }',
           'fread(buf, 1, (size_t)sz, fp);', 'fclose(fp);', '*out_len = (size_t)sz;', 'return buf;')
    simple(SEC, '写入字节到文件', 'int', 'file_write_bytes', 'const char *filename, const uint8_t *data, size_t len',
           'FILE *fp = fopen(filename, "wb");', 'if (!fp) return -1;', 'fwrite(data, 1, len, fp);', 'fclose(fp);', 'return 0;')
    simple(SEC, '统计文件中的单词数', 'int', 'file_count_words', 'const char *filename',
           'char *s = read_file(filename);', 'if (!s) return -1;', 'int c = count_words(s);', 'free(s);', 'return c;')
    simple(SEC, '文件是否包含指定行', 'int', 'file_has_line', 'const char *filename, const char *line',
           'FILE *fp = fopen(filename, "r");', 'if (!fp) return 0;', 'char buf[1024];',
           'while (safe_fgets(buf, sizeof(buf), fp)) { if (str_cmp(buf, line) == 0) { fclose(fp); return 1; } }',
           'fclose(fp);', 'return 0;')

# ============================================================
#  47. 排序算法（第三批）
# ============================================================
def family_sort2():
    SEC = '排序算法(第三批)'
    simple(SEC, '升序排序(包装冒泡)', 'void', 'sort_asc', 'int arr[], int size', 'bubble_sort(arr, size);')
    simple(SEC, '降序排序', 'void', 'sort_desc', 'int arr[], int size',
           'bubble_sort(arr, size);', 'reverse_int_array(arr, size);')
    simple(SEC, 'double 数组升序(冒泡)', 'void', 'sort_double_asc', 'double arr[], int size',
           'for (int i = 0; i < size - 1; i++) for (int j = 0; j < size - 1 - i; j++) if (arr[j] > arr[j + 1]) { double t = arr[j]; arr[j] = arr[j + 1]; arr[j + 1] = t; }')
    simple(SEC, 'float 数组升序(冒泡)', 'void', 'sort_float_asc', 'float arr[], int size',
           'for (int i = 0; i < size - 1; i++) for (int j = 0; j < size - 1 - i; j++) if (arr[j] > arr[j + 1]) { float t = arr[j]; arr[j] = arr[j + 1]; arr[j + 1] = t; }')
    simple(SEC, 'long 数组升序(冒泡)', 'void', 'sort_long_asc', 'long arr[], int size',
           'for (int i = 0; i < size - 1; i++) for (int j = 0; j < size - 1 - i; j++) if (arr[j] > arr[j + 1]) { long t = arr[j]; arr[j] = arr[j + 1]; arr[j + 1] = t; }')
    simple(SEC, 'char 数组升序(冒泡)', 'void', 'sort_char_asc', 'char arr[], int size',
           'for (int i = 0; i < size - 1; i++) for (int j = 0; j < size - 1 - i; j++) if (arr[j] > arr[j + 1]) { char t = arr[j]; arr[j] = arr[j + 1]; arr[j + 1] = t; }')
    simple(SEC, '排序并去重(返回新长度)', 'int', 'sort_unique', 'int arr[], int *size',
           'bubble_sort(arr, *size);', 'return remove_duplicates_int(arr, size);')
    simple(SEC, '排序索引(返回索引数组需free)', 'int*', 'sort_indices', 'int arr[], int size',
           'int *idx = (int*)malloc(size * sizeof(int));', 'if (!idx) return NULL;',
           'for (int i = 0; i < size; i++) idx[i] = i;',
           'for (int i = 0; i < size - 1; i++) for (int j = 0; j < size - 1 - i; j++) if (arr[idx[j]] > arr[idx[j + 1]]) { int t = idx[j]; idx[j] = idx[j + 1]; idx[j + 1] = t; }',
           'return idx;')

# ============================================================
#  48. 核心补齐（若原始 utils.h 缺少则自动生成，保证库自洽）
# ============================================================
def family_core():
    SEC = '核心算法(补齐)'
    # ---- 查找 ----
    simple(SEC, '插值查找(升序)', 'int', 'interpolation_search', 'int arr[], int size, int target',
           'int lo = 0, hi = size - 1;',
           'while (lo <= hi && target >= arr[lo] && target <= arr[hi]) {',
           '    if (arr[hi] == arr[lo]) return (arr[lo] == target) ? lo : -1;',
           '    int pos = lo + (int)(((long long)(target - arr[lo]) * (hi - lo)) / (arr[hi] - arr[lo]));',
           '    if (arr[pos] == target) return pos;',
           '    if (arr[pos] < target) lo = pos + 1; else hi = pos - 1; }',
           'return -1;')
    simple(SEC, '哨兵查找', 'int', 'sentinel_search', 'int arr[], int size, int target',
           'if (size <= 0) return -1;', 'int last = arr[size - 1];',
           'arr[size - 1] = target;', 'int i = 0;', 'while (arr[i] != target) i++;',
           'arr[size - 1] = last;', 'if (i < size - 1) return i;', 'return (last == target) ? size - 1 : -1;')
    simple(SEC, '斐波那契查找(升序)', 'int', 'fibonacci_search', 'int arr[], int size, int target',
           'int f2 = 0, f1 = 1, f = f2 + f1;', 'while (f < size) { f2 = f1; f1 = f; f = f2 + f1; }',
           'int offset = -1;', 'while (f > 1) {',
           '    int i = (offset + f2 < size - 1) ? offset + f2 : size - 1;',
           '    if (arr[i] < target) { f = f1; f1 = f2; f2 = f - f1; offset = i; }',
           '    else if (arr[i] > target) { f = f2; f1 = f1 - f2; f2 = f - f1; }',
           '    else return i; }',
           'if (f1 && offset + 1 < size && arr[offset + 1] == target) return offset + 1;', 'return -1;')
    # ---- 字符串算法 ----
    simple(SEC, 'KMP 字符串匹配', 'int', 'kmp_search', 'const char *text, const char *pattern',
           'if (!text || !pattern) return -1;', 'int m = str_len(pattern);', 'if (m == 0) return 0;',
           'int n = str_len(text);', 'int *next = (int*)malloc(m * sizeof(int));', 'if (!next) return -1;',
           'next[0] = 0;', 'int j = 0;',
           'for (int i = 1; i < m; i++) { while (j > 0 && pattern[i] != pattern[j]) j = next[j - 1]; if (pattern[i] == pattern[j]) j++; next[i] = j; }',
           'j = 0;', 'int found = -1;',
           'for (int i = 0; i < n; i++) { while (j > 0 && text[i] != pattern[j]) j = next[j - 1]; if (text[i] == pattern[j]) j++; if (j == m) { found = i - m + 1; break; } }',
           'free(next);', 'return found;')
    simple(SEC, '最长公共子串长度', 'int', 'str_longest_common_substr', 'const char *s1, const char *s2',
           'int n1 = str_len(s1), n2 = str_len(s2), best = 0;',
           'for (int i = 0; i < n1; i++) for (int j = 0; j < n2; j++) {',
           '    int l = 0;', '    while (i + l < n1 && j + l < n2 && s1[i + l] == s2[j + l]) l++;',
           '    if (l > best) best = l; }', 'return best;')
    simple(SEC, '编辑距离(莱文斯坦)', 'int', 'str_edit_distance', 'const char *s1, const char *s2',
           'int n1 = str_len(s1), n2 = str_len(s2);', 'if (n1 == 0) return n2;', 'if (n2 == 0) return n1;',
           'int *dp = (int*)malloc((n2 + 1) * sizeof(int));', 'if (!dp) return -1;',
           'for (int j = 0; j <= n2; j++) dp[j] = j;',
           'for (int i = 1; i <= n1; i++) { int prev = dp[0]; dp[0] = i;',
           '    for (int j = 1; j <= n2; j++) { int t = dp[j];',
           '        if (s1[i - 1] == s2[j - 1]) dp[j] = prev;',
           '        else { int d = dp[j - 1] + 1, ins = dp[j] + 1, rep = prev + 1; dp[j] = UTILS_MIN(d, UTILS_MIN(ins, rep)); }',
           '        prev = t; } }',
           'int r = dp[n2];', 'free(dp);', 'return r;')
    simple(SEC, '反转句子单词顺序', 'void', 'str_reverse_words', 'char *str',
           'int len = str_len(str);',
           'for (int i = 0; i < len / 2; i++) { char t = str[i]; str[i] = str[len - 1 - i]; str[len - 1 - i] = t; }',
           'int i = 0;', 'while (i < len) { while (i < len && str[i] == \' \') i++; int s = i; while (i < len && str[i] != \' \') i++; int a = s, b = i - 1; while (a < b) { char t = str[a]; str[a] = str[b]; str[b] = t; a++; b--; } }')
    # ---- 前缀和与差分 ----
    simple(SEC, '构建前缀和数组(需free)', 'long long*', 'build_prefix_sum', 'int arr[], int size',
           'long long *pre = (long long*)malloc((size + 1) * sizeof(long long));', 'if (!pre) return NULL;',
           'pre[0] = 0;', 'for (int i = 0; i < size; i++) pre[i + 1] = pre[i] + arr[i];', 'return pre;')
    simple(SEC, '前缀和区间查询', 'long long', 'range_sum_query', 'long long pre[], int l, int r',
           'if (!pre || l > r) return 0;', 'return pre[r + 1] - pre[l];')
    simple(SEC, '构建差分数组', 'void', 'build_diff_array', 'int arr[], int size, int diff[]',
           'diff[0] = arr[0];', 'for (int i = 1; i < size; i++) diff[i] = arr[i] - arr[i - 1];', 'diff[size] = 0;')
    simple(SEC, '差分数组还原', 'void', 'apply_diff_array', 'int diff[], int size, int out[]',
           'out[0] = diff[0];', 'for (int i = 1; i < size; i++) out[i] = out[i - 1] + diff[i];')
    # ---- 数论 ----
    simple(SEC, '埃氏筛求素数(需free)', 'int*', 'sieve_primes', 'int n, int *count',
           '*count = 0;', 'if (n < 2) return NULL;', 'char *mark = (char*)calloc(n + 1, 1);', 'if (!mark) return NULL;',
           'for (int i = 2; i <= n; i++) mark[i] = 1;',
           'for (int i = 2; i * i <= n; i++) if (mark[i]) for (int j = i * i; j <= n; j += i) mark[j] = 0;',
           'int cnt = 0;', 'for (int i = 2; i <= n; i++) if (mark[i]) cnt++;',
           'int *p = (int*)malloc(cnt * sizeof(int));', 'if (!p) { free(mark); return NULL; }',
           'int k = 0;', 'for (int i = 2; i <= n; i++) if (mark[i]) p[k++] = i;', 'free(mark);', '*count = cnt;', 'return p;')
    simple(SEC, '质因数分解', 'int', 'prime_factors', 'int n, int factors[], int *count',
           '*count = 0;', 'if (n <= 1) return 0;',
           'for (int i = 2; (long long)i * i <= n; i++) while (n % i == 0) { factors[*count] = i; (*count)++; n /= i; }',
           'if (n > 1) { factors[*count] = n; (*count)++; }', 'return *count;')
    simple(SEC, '快速幂取模', 'long long', 'mod_pow', 'long long base, long long exp, long long mod',
           'long long r = 1 % mod;', 'base %= mod;',
           'while (exp > 0) { if (exp & 1) r = (r * base) % mod; base = (base * base) % mod; exp >>= 1; }', 'return r;')
    simple(SEC, '扩展欧几里得', 'int', 'extended_gcd', 'int a, int b, int *x, int *y',
           'if (b == 0) { *x = 1; *y = 0; return a; }',
           'int x1, y1;', 'int g = extended_gcd(b, a % b, &x1, &y1);', '*x = y1;', '*y = x1 - (a / b) * y1;', 'return g;')
    simple(SEC, '下一个字典序排列', 'int', 'next_permutation', 'int arr[], int size',
           'if (size <= 1) return 0;', 'int i = size - 2;', 'while (i >= 0 && arr[i] >= arr[i + 1]) i--;',
           'if (i < 0) return 0;', 'int j = size - 1;', 'while (arr[j] <= arr[i]) j--;',
           'int t = arr[i]; arr[i] = arr[j]; arr[j] = t;', 'int l = i + 1, r = size - 1;',
           'while (l < r) { t = arr[l]; arr[l] = arr[r]; arr[r] = t; l++; r--; }', 'return 1;')
    simple(SEC, '闰年判断', 'int', 'is_leap_year', 'int year',
           'return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);')
    simple(SEC, '判断 2 的幂', 'int', 'is_power_of_two', 'int n', 'return (n > 0) && ((n & (n - 1)) == 0);')
    simple(SEC, '统计整数位数', 'int', 'count_digits', 'int n',
           'if (n == 0) return 1;', 'if (n < 0) n = -n;', 'int c = 0;', 'while (n) { c++; n /= 10; }', 'return c;')
    simple(SEC, '反转整数', 'int', 'reverse_int', 'int n',
           'int r = 0, neg = (n < 0);', 'if (neg) n = -n;', 'while (n) { r = r * 10 + n % 10; n /= 10; }',
           'return neg ? -r : r;')
    simple(SEC, '回文数判断', 'int', 'is_palindrome_num', 'int n', 'if (n < 0) return 0;', 'return n == reverse_int(n);')
    # ---- 位运算技巧 ----
    simple(SEC, '最低位 1 的位置', 'int', 'lowest_set_bit', 'uint32_t n',
           'if (n == 0) return -1;', 'int p = 0;', 'while (!(n & 1u)) { n >>= 1; p++; }', 'return p;')
    simple(SEC, '异或找唯一出现一次的数', 'int', 'find_single_number', 'int arr[], int size',
           'int r = 0;', 'for (int i = 0; i < size; i++) r ^= arr[i];', 'return r;')
    simple(SEC, '汉明距离', 'int', 'hamming_distance', 'uint32_t a, uint32_t b',
           'uint32_t x = a ^ b;', 'int c = 0;', 'while (x) { c += (int)(x & 1u); x >>= 1; }', 'return c;')
    # ---- 动态规划 ----
    simple(SEC, '0-1 背包最大价值', 'int', 'knapsack01', 'int weights[], int values[], int n, int capacity',
           'int *dp = (int*)calloc(capacity + 1, sizeof(int));', 'if (!dp) return 0;',
           'for (int i = 0; i < n; i++) for (int c = capacity; c >= weights[i]; c--) {',
           '    int take = dp[c - weights[i]] + values[i];', '    if (take > dp[c]) dp[c] = take; }',
           'int r = dp[capacity];', 'free(dp);', 'return r;')
    simple(SEC, '最长递增子序列长度', 'int', 'lis_length', 'int arr[], int size',
           'if (size <= 0) return 0;', 'int *dp = (int*)malloc(size * sizeof(int));', 'if (!dp) return 0;',
           'int best = 1;',
           'for (int i = 0; i < size; i++) { dp[i] = 1; for (int j = 0; j < i; j++) if (arr[j] < arr[i] && dp[j] + 1 > dp[i]) dp[i] = dp[j] + 1; if (dp[i] > best) best = dp[i]; }',
           'free(dp);', 'return best;')
    # ---- 哈希（核心） ----
    simple(SEC, 'DJB2 哈希', 'uint32_t', 'djb2_hash', 'const char *str',
           'uint32_t h = 5381;', 'while (*str) h = ((h << 5) + h) + (uint32_t)(unsigned char)*str++;', 'return h;')
    simple(SEC, 'FNV-1a 哈希', 'uint32_t', 'fnv1a_hash', 'const char *str',
           'uint32_t h = 2166136261u;', 'while (*str) { h ^= (uint32_t)(unsigned char)*str++; h *= 16777619u; }', 'return h;')
    simple(SEC, 'SDBM 哈希', 'uint32_t', 'sdbm_hash', 'const char *str',
           'uint32_t h = 0;', 'while (*str) h = (uint32_t)(unsigned char)*str++ + (h << 6) + (h << 16) - h;', 'return h;')
    simple(SEC, 'BKDR 哈希', 'uint32_t', 'bkdr_hash', 'const char *str',
           'uint32_t h = 0;', 'while (*str) h = h * 131 + (uint32_t)(unsigned char)*str++;', 'return h;')
    # ---- 字符 ----
    simple(SEC, '字符转小写', 'char', 'char_to_lower', 'char c', 'return (c >= \'A\' && c <= \'Z\') ? (char)(c + 32) : c;')
    simple(SEC, '字符转大写', 'char', 'char_to_upper', 'char c', 'return (c >= \'a\' && c <= \'z\') ? (char)(c - 32) : c;')
    # ---- 环形缓冲区 ----
    simple(SEC, '创建环形缓冲区', 'RingBuffer*', 'rb_create', 'uint16_t capacity',
           'if (capacity == 0) return NULL;', 'RingBuffer *rb = (RingBuffer*)malloc(sizeof(RingBuffer));', 'if (!rb) return NULL;',
           'rb->buffer = (uint8_t*)malloc(capacity);', 'if (!rb->buffer) { free(rb); return NULL; }',
           'rb->head = 0; rb->tail = 0; rb->capacity = capacity; rb->count = 0;', 'return rb;')
    simple(SEC, '销毁环形缓冲区', 'void', 'rb_destroy', 'RingBuffer *rb', 'if (!rb) return;', 'free(rb->buffer);', 'free(rb);')
    simple(SEC, '写入一个字节', 'int', 'rb_write', 'RingBuffer *rb, uint8_t byte',
           'if (!rb || rb->count >= rb->capacity) return -1;', 'rb->buffer[rb->head] = byte;',
           'rb->head = (uint16_t)((rb->head + 1) % rb->capacity);', 'rb->count++;', 'return 0;')
    simple(SEC, '读取一个字节', 'int', 'rb_read', 'RingBuffer *rb, uint8_t *out',
           'if (!rb || rb->count == 0 || !out) return -1;', '*out = rb->buffer[rb->tail];',
           'rb->tail = (uint16_t)((rb->tail + 1) % rb->capacity);', 'rb->count--;', 'return 0;')
    simple(SEC, '查看队首字节', 'int', 'rb_peek', 'RingBuffer *rb, uint8_t *out',
           'if (!rb || rb->count == 0 || !out) return -1;', '*out = rb->buffer[rb->tail];', 'return 0;')
    simple(SEC, '可读字节数', 'uint16_t', 'rb_available', 'RingBuffer *rb', 'return (rb == NULL) ? 0 : rb->count;')
    simple(SEC, '剩余空间', 'uint16_t', 'rb_free', 'RingBuffer *rb',
           'return (rb == NULL) ? 0 : (uint16_t)(rb->capacity - rb->count);')
    simple(SEC, '是否为空', 'int', 'rb_is_empty', 'RingBuffer *rb', 'return (rb == NULL || rb->count == 0);')
    simple(SEC, '是否为满', 'int', 'rb_is_full', 'RingBuffer *rb', 'return (rb != NULL && rb->count >= rb->capacity);')
    simple(SEC, '清空缓冲区', 'void', 'rb_clear', 'RingBuffer *rb',
           'if (!rb) return;', 'rb->head = 0; rb->tail = 0; rb->count = 0;')
    # ---- 动态数组 ----
    simple(SEC, '创建动态数组', 'Vector*', 'vec_create', 'int init_capacity',
           'if (init_capacity <= 0) init_capacity = 4;', 'Vector *v = (Vector*)malloc(sizeof(Vector));', 'if (!v) return NULL;',
           'v->data = (int*)malloc(init_capacity * sizeof(int));', 'if (!v->data) { free(v); return NULL; }',
           'v->size = 0; v->capacity = init_capacity;', 'return v;')
    simple(SEC, '销毁动态数组', 'void', 'vec_destroy', 'Vector *v', 'if (!v) return;', 'free(v->data);', 'free(v);')
    simple(SEC, '尾部追加', 'int', 'vec_push_back', 'Vector *v, int value',
           'if (!v) return -1;', 'if (v->size >= v->capacity) {',
           '    int nc = v->capacity * 2;', '    int *nd = (int*)realloc(v->data, nc * sizeof(int));', '    if (!nd) return -1;',
           '    v->data = nd; v->capacity = nc; }',
           'v->data[v->size++] = value;', 'return 0;')
    simple(SEC, '尾部弹出', 'int', 'vec_pop_back', 'Vector *v, int *out',
           'if (!v || v->size <= 0 || !out) return -1;', '*out = v->data[--v->size];', 'return 0;')
    simple(SEC, '按下标取值', 'int', 'vec_get', 'Vector *v, int index, int *out',
           'if (!v || index < 0 || index >= v->size || !out) return -1;', '*out = v->data[index];', 'return 0;')
    simple(SEC, '按下标赋值', 'int', 'vec_set', 'Vector *v, int index, int value',
           'if (!v || index < 0 || index >= v->size) return -1;', 'v->data[index] = value;', 'return 0;')
    simple(SEC, '元素个数', 'int', 'vec_size', 'Vector *v', 'return (v == NULL) ? 0 : v->size;')
    simple(SEC, '当前容量', 'int', 'vec_capacity', 'Vector *v', 'return (v == NULL) ? 0 : v->capacity;')
    simple(SEC, '是否为空', 'int', 'vec_is_empty', 'Vector *v', 'return (v == NULL || v->size == 0);')
    simple(SEC, '清空(不释放)', 'void', 'vec_clear', 'Vector *v', 'if (v) v->size = 0;')
    simple(SEC, '按下标插入', 'int', 'vec_insert', 'Vector *v, int index, int value',
           'if (!v || index < 0 || index > v->size) return -1;',
           'if (v->size >= v->capacity) { int nc = v->capacity * 2; int *nd = (int*)realloc(v->data, nc * sizeof(int)); if (!nd) return -1; v->data = nd; v->capacity = nc; }',
           'for (int i = v->size; i > index; i--) v->data[i] = v->data[i - 1];', 'v->data[index] = value; v->size++;', 'return 0;')
    simple(SEC, '按下标删除', 'int', 'vec_remove', 'Vector *v, int index, int *out',
           'if (!v || index < 0 || index >= v->size) return -1;', 'if (out) *out = v->data[index];',
           'for (int i = index; i < v->size - 1; i++) v->data[i] = v->data[i + 1];', 'v->size--;', 'return 0;')
    # ---- 优先级队列 ----
    simple(SEC, '创建最大堆队列', 'PriorityQueue*', 'pq_create', 'int capacity',
           'if (capacity <= 0) capacity = 16;', 'PriorityQueue *pq = (PriorityQueue*)malloc(sizeof(PriorityQueue));', 'if (!pq) return NULL;',
           'pq->data = (int*)malloc(capacity * sizeof(int));', 'if (!pq->data) { free(pq); return NULL; }',
           'pq->size = 0; pq->capacity = capacity;', 'return pq;')
    simple(SEC, '销毁队列', 'void', 'pq_destroy', 'PriorityQueue *pq', 'if (!pq) return;', 'free(pq->data);', 'free(pq);')
    simple(SEC, '入队', 'int', 'pq_push', 'PriorityQueue *pq, int value',
           'if (!pq) return -1;',
           'if (pq->size >= pq->capacity) { int nc = pq->capacity * 2; int *nd = (int*)realloc(pq->data, nc * sizeof(int)); if (!nd) return -1; pq->data = nd; pq->capacity = nc; }',
           'int i = pq->size++;', 'pq->data[i] = value;',
           'while (i > 0) { int p = (i - 1) / 2; if (pq->data[p] >= pq->data[i]) break; int t = pq->data[p]; pq->data[p] = pq->data[i]; pq->data[i] = t; i = p; }',
           'return 0;')
    simple(SEC, '弹出最大值', 'int', 'pq_pop', 'PriorityQueue *pq, int *out',
           'if (!pq || pq->size <= 0 || !out) return -1;', '*out = pq->data[0];', 'pq->data[0] = pq->data[--pq->size];',
           'int i = 0;',
           'while (1) { int l = 2 * i + 1, r = 2 * i + 2, s = i;',
           '    if (l < pq->size && pq->data[l] > pq->data[s]) s = l;',
           '    if (r < pq->size && pq->data[r] > pq->data[s]) s = r;',
           '    if (s == i) break;', '    int t = pq->data[s]; pq->data[s] = pq->data[i]; pq->data[i] = t; i = s; }',
           'return 0;')
    simple(SEC, '查看最大值', 'int', 'pq_peek', 'PriorityQueue *pq, int *out',
           'if (!pq || pq->size <= 0 || !out) return -1;', '*out = pq->data[0];', 'return 0;')
    simple(SEC, '是否为空', 'int', 'pq_is_empty', 'PriorityQueue *pq', 'return (pq == NULL || pq->size == 0);')
    simple(SEC, '元素个数', 'int', 'pq_size', 'PriorityQueue *pq', 'return (pq == NULL) ? 0 : pq->size;')
    # ---- 二叉搜索树（核心） ----
    simple(SEC, 'BST 插入节点', 'BSTNode*', 'bst_insert', 'BSTNode *root, int data',
           'if (root == NULL) { BSTNode *n = (BSTNode*)malloc(sizeof(BSTNode)); if (!n) return NULL; n->data = data; n->left = n->right = NULL; return n; }',
           'if (data < root->data) root->left = bst_insert(root->left, data);',
           'else if (data > root->data) root->right = bst_insert(root->right, data);', 'return root;')
    simple(SEC, 'BST 查找节点', 'BSTNode*', 'bst_search', 'BSTNode *root, int data',
           'while (root) { if (data == root->data) return root; root = (data < root->data) ? root->left : root->right; }', 'return NULL;')
    simple(SEC, 'BST 最小节点', 'BSTNode*', 'bst_find_min', 'BSTNode *root',
           'if (!root) return NULL;', 'while (root->left) root = root->left;', 'return root;')
    simple(SEC, 'BST 最大节点', 'BSTNode*', 'bst_find_max', 'BSTNode *root',
           'if (!root) return NULL;', 'while (root->right) root = root->right;', 'return root;')
    simple(SEC, 'BST 删除节点', 'BSTNode*', 'bst_delete', 'BSTNode *root, int data',
           'if (!root) return NULL;',
           'if (data < root->data) root->left = bst_delete(root->left, data);',
           'else if (data > root->data) root->right = bst_delete(root->right, data);',
           'else { if (!root->left) { BSTNode *r = root->right; free(root); return r; }',
           '    if (!root->right) { BSTNode *l = root->left; free(root); return l; }',
           '    BSTNode *mn = bst_find_min(root->right);', '    root->data = mn->data;',
           '    root->right = bst_delete(root->right, mn->data); }', 'return root;')
    simple(SEC, 'BST 树高', 'int', 'bst_height', 'BSTNode *root',
           'if (!root) return 0;', 'int l = bst_height(root->left), r = bst_height(root->right);', 'return (l > r ? l : r) + 1;')
    simple(SEC, 'BST 节点数', 'int', 'bst_node_count', 'BSTNode *root',
           'if (!root) return 0;', 'return 1 + bst_node_count(root->left) + bst_node_count(root->right);')
    simple(SEC, 'BST 中序遍历', 'void', 'bst_inorder', 'BSTNode *root',
           'if (!root) return;', 'bst_inorder(root->left);', 'printf("%d ", root->data);', 'bst_inorder(root->right);')
    simple(SEC, 'BST 前序遍历', 'void', 'bst_preorder', 'BSTNode *root',
           'if (!root) return;', 'printf("%d ", root->data);', 'bst_preorder(root->left);', 'bst_preorder(root->right);')
    simple(SEC, 'BST 后序遍历', 'void', 'bst_postorder', 'BSTNode *root',
           'if (!root) return;', 'bst_postorder(root->left);', 'bst_postorder(root->right);', 'printf("%d ", root->data);')
    simple(SEC, 'BST 层序遍历', 'void', 'bst_levelorder', 'BSTNode *root',
           'if (!root) return;', 'BSTNode **q = (BSTNode**)malloc(128 * sizeof(BSTNode*));', 'if (!q) return;',
           'int head = 0, tail = 0;', 'q[tail++] = root;',
           'while (head < tail) { BSTNode *n = q[head++]; printf("%d ", n->data); if (n->left) q[tail++] = n->left; if (n->right) q[tail++] = n->right; }',
           'free(q);')
    simple(SEC, 'BST 释放整棵树', 'void', 'bst_free', 'BSTNode *root',
           'if (!root) return;', 'bst_free(root->left);', 'bst_free(root->right);', 'free(root);')
    # ---- 时间戳与日志 ----
    simple(SEC, '毫秒级时间戳', 'long long', 'get_timestamp_ms', 'void',
           '#if defined(_WIN32)', 'FILETIME ft;', 'GetSystemTimeAsFileTime(&ft);',
           'const long long DIFF = 116444736000000000LL;',
           'long long t = ((long long)ft.dwHighDateTime << 32) | ft.dwLowDateTime;',
           'return (t - DIFF) / 10000;',
           '#elif defined(__unix__) || defined(__linux__) || defined(__APPLE__)',
           'struct timeval tv;', 'gettimeofday(&tv, NULL);',
           'return (long long)tv.tv_sec * 1000 + tv.tv_usec / 1000;',
           '#else', 'return (long long)time(NULL) * 1000;', '#endif')
    simple(SEC, '微秒级时间戳', 'long long', 'get_timestamp_us', 'void',
           '#if defined(_WIN32)', 'FILETIME ft;', 'GetSystemTimeAsFileTime(&ft);',
           'const long long DIFF = 116444736000000000LL;',
           'long long t = ((long long)ft.dwHighDateTime << 32) | ft.dwLowDateTime;',
           'return (t - DIFF) / 10;',
           '#elif defined(__unix__) || defined(__linux__) || defined(__APPLE__)',
           'struct timeval tv;', 'gettimeofday(&tv, NULL);',
           'return (long long)tv.tv_sec * 1000000 + tv.tv_usec;',
           '#else', 'return (long long)time(NULL) * 1000000;', '#endif')
    simple(SEC, '带时间戳写入日志文件', 'void', 'log_to_file', 'const char *filename, const char *format, ...',
           'if (!filename || !format) return;', 'FILE *fp = fopen(filename, "a");', 'if (!fp) return;',
           'char ts[20];', 'get_time_str(ts);', 'fprintf(fp, "[%s] ", ts);',
           'va_list args;', 'va_start(args, format);', 'vfprintf(fp, format, args);', 'va_end(args);',
           'fprintf(fp, "\\n");', 'fclose(fp);')

# ============================================================
#  运行：生成全部函数
# ============================================================
print('== UTILS 函数库批量生成器 ==')
clean_previous()
EXISTING = existing_names()
print(f'已存在函数/标识符: {len(EXISTING)} 个')

family_array()
family_stat()
family_query()
family_transform()
family_sort()
family_search()
family_string()
family_char()
family_math()
family_convert()
family_bit()
family_crc()
family_hash()
family_time()
family_random()
family_geom()
family_numtool()
family_ds()
family_file()
family_mem()
family_console()
family_matrix()
family_misc()
family_string2()
family_math2()
family_array2()
family_list_extra()
family_convert2()
family_geom2()
family_numtool2()
family_misc2()
family_graph2()
family_random2()
family_bst_extra()
family_matrix2()
family_stat2()
family_array_variants()
family_array3()
family_string3()
family_math3()
family_numtool3()
family_bit2()
family_convert3()
family_console2()
family_seq()
family_file2()
family_sort2()
family_core()

print(f'新生成函数: {len(GENERATED)} 个')

# ---------- 生成 utils_gen.h（数据结构 + 函数声明） ----------
GH_PATH = os.path.join(BASE, 'utils_gen.h')
GC_PATH = os.path.join(BASE, 'utils_gen.c')

# 收集分区顺序
secs = []
for (sec, desc, ret, name, params, body) in GENERATED:
    if sec not in secs:
        secs.append(sec)

gh = []
gh.append('/* ============================================================')
gh.append(' *  utils_gen.h — 自动生成的函数声明（由 gen_functions.py 生成，请勿手改）')
gh.append(' * ============================================================ */')
gh.append('')
gh.append('#ifndef UTILS_GEN_H')
gh.append('#define UTILS_GEN_H')
gh.append('')
gh.append('/* ===== 常用宏兜底（若 utils.h 已定义则跳过，避免重复定义） ===== */')
gh.append('#ifndef UTILS_MIN')
gh.append('#define UTILS_MIN(a, b) ((a) < (b) ? (a) : (b))')
gh.append('#endif')
gh.append('#ifndef UTILS_MAX')
gh.append('#define UTILS_MAX(a, b) ((a) > (b) ? (a) : (b))')
gh.append('#endif')
gh.append('#ifndef UTILS_ABS')
gh.append('#define UTILS_ABS(x) ((x) < 0 ? -(x) : (x))')
gh.append('#endif')
gh.append('#ifndef UTILS_ARRAY_SIZE')
gh.append('#define UTILS_ARRAY_SIZE(arr) ((int)(sizeof(arr) / sizeof((arr)[0])))')
gh.append('#endif')
gh.append('#ifndef UTILS_BIT')
gh.append('#define UTILS_BIT(n) (1u << (n))')
gh.append('#endif')
gh.append('')
gh.append('/* ===== 数据结构兜底（若 utils.h 已定义相同类型请删除对应行） ===== */')
gh.append('typedef struct { int *data; int size, capacity; } Vector;')
gh.append('typedef struct { int *data; int size, capacity; } PriorityQueue;')
gh.append('typedef struct { uint8_t *buffer; uint16_t head, tail, capacity, count; } RingBuffer;')
gh.append('typedef struct BSTNode { int data; struct BSTNode *left, *right; } BSTNode;')
gh.append('')
for ds in DS_HEADER:
    gh.append('/** 自动生成的数据结构 */')
    gh.append(ds)
    gh.append('')
for sec in secs:
    gh.append('')
    gh.append('// ============================================================')
    gh.append(f'//                     {sec}（自动生成）')
    gh.append('// ============================================================')
    gh.append('')
    for (s, desc, ret, name, params, body) in GENERATED:
        if s != sec:
            continue
        gh.append(f'/** {desc} */')
        gh.append(f'{ret} {name}({params});')
        gh.append('')
gh.append('#endif /* UTILS_GEN_H */')
gh.append('')
write(GH_PATH, '\n'.join(gh))
print('[OK] utils_gen.h 已生成')

# ---------- 生成 utils_gen.c（函数实现） ----------
gc = []
gc.append('/* ============================================================')
gc.append(' *  utils_gen.c — 自动生成的函数实现（由 gen_functions.py 生成，请勿手改）')
gc.append(' *  通过 utils.c 末尾的 #include "utils_gen.c" 编译进库')
gc.append(' * ============================================================ */')
gc.append('')
for sec in secs:
    gc.append('')
    gc.append('// ============================================================')
    gc.append(f'//                     {sec}（自动生成）')
    gc.append('// ============================================================')
    for (s, desc, ret, name, params, body) in GENERATED:
        if s != sec:
            continue
        gc.append('')
        gc.append(f'{ret} {name}({params}) {{')
        for bl in body:
            gc.append('    ' + bl)
        gc.append('}')
write(GC_PATH, '\n'.join(gc) + '\n')
print('[OK] utils_gen.c 已生成')

# ---------- 在 utils.h 末尾加入 #include "utils_gen.h"（关闭 extern "C" 之前） ----------
h = read(H_PATH)
if '#include "utils_gen.h"' not in h:
    marker = '#ifdef __cplusplus'
    idx = h.rfind(marker)
    if idx < 0:
        print('[ERROR] utils.h 中找不到 #ifdef __cplusplus 标记！')
        raise SystemExit(1)
    inc = '\n\n// 自动生成的函数声明（由 gen_functions.py 生成）\n#include "utils_gen.h"\n'
    h = h[:idx] + inc + h[idx:]
    write(H_PATH, h)
    print('[OK] utils.h 已加入 #include "utils_gen.h"')

# ---------- 在 utils.c 末尾加入 #include "utils_gen.c" ----------
c = read(C_PATH)
if '#include "utils_gen.c"' not in c:
    c = c.rstrip() + '\n\n// 自动生成的函数实现（由 gen_functions.py 生成）\n#include "utils_gen.c"\n'
    write(C_PATH, c)
    print('[OK] utils.c 已加入 #include "utils_gen.c"')

# ---------- 重建 func_index.h ----------
# 常用宏的功能描述（用于函数索引表，保证功能介绍准确）
MACRO_DESC = {
    'UTILS_MIN': '取两个数中较小值',
    'UTILS_MAX': '取两个数中较大值',
    'UTILS_ABS': '求绝对值',
    'UTILS_ARRAY_SIZE': '求数组元素个数',
    'UTILS_BIT': '生成位掩码（第 n 位为 1）',
}

def build_index():
    lines = h_text.split('\n')
    entries = []
    section = '其他'
    pending = ''
    for i, ln in enumerate(lines):
        s = ln.strip()
        # 分区标题
        if s.startswith('//') and not s.startswith('//='):
            prev = lines[i-1].strip() if i > 0 else ''
            nxt = lines[i+1].strip() if i+1 < len(lines) else ''
            # 分隔线可能是 "// ====" 或 "//===="（// 后是否带空格都能识别）
            if re.match(r'//\s*=+\s*$', prev) and re.match(r'//\s*=+\s*$', nxt):
                title = s.lstrip('/').strip()
                if title:
                    # 去掉生成器标注后缀，让下拉框分类名更简洁
                    title = title.replace('（自动生成）', '').strip()
                    if title:
                        section = title
        # 文档注释（支持单行 /** xxx */ 和多行 /** ... */）
        if s.startswith('/**'):
            inner = s[3:].strip().rstrip('*/').strip()
            if not inner:
                # 多行注释：取第一行非空描述
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
        # 宏（函数式宏，如 #define UTILS_MIN(a, b) ...）
        if s.startswith('#define'):
            m = re.match(r'#define\s+([A-Za-z_]\w*)\s*(\([^)]*\))', s)
            if m:
                name = m.group(1)
                desc = MACRO_DESC.get(name, '宏定义')
                example = name + m.group(2)
                entries.append((name, '常用宏', desc, example))
                pending = ''
        # 函数声明
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

# 解析 utils.h 与 utils_gen.h（合并）生成索引
h_text = read(H_PATH) + '\n// ===== 自动生成区 =====\n' + read(GH_PATH)
entries = build_index()
print(f'索引函数总数: {len(entries)}')

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
ilines.append('')
write(IDX_PATH, '\n'.join(ilines))
print('[OK] func_index.h 已重建')

total = len(EXISTING) + len(GENERATED)
print(f'== 完成！函数总量约 {total} 个 ==')
