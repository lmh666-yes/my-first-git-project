/* ============================================================
 *  utils_gui.c — UTILS 函数库 · 图形化查找工具 v2.0（Windows GUI）
 * ------------------------------------------------------------
 *  功能：
 *   1. 左侧列表按分类展示全部函数，支持关键词搜索 + 分类筛选 + 排序
 *   2. 右侧详情窗格显示功能说明、调用示例、源码位置及实现源码
 *   3. 双击函数 / 点击按钮，可直接跳转到 VS Code 对应行
 *   4. 支持 utils.h / utils_gen.h / utils.c / utils_gen.c 四个文件，
 *      自动生成区的函数也能正常显示源码并跳转
 *
 *  编译运行（需要 MinGW gcc）：
 *    gcc -finput-charset=UTF-8 -fexec-charset=GBK -I..\library \
 *        -o utils_gui.exe utils_gui.c -mwindows -lcomctl32 -lshell32
 * ============================================================ */

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include <commctrl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "func_index.h"

/* ---------- 控件 ID ---------- */
#define IDC_SEARCH        1001
#define IDC_CATEGORY      1002
#define IDC_LIST          1003
#define IDC_DETAIL        1004
#define IDC_OPEN_IMPL     1005
#define IDC_OPEN_DECL     1006
#define IDC_COUNT_LBL     1007
#define IDC_COPY_NAME     1008
#define IDC_COPY_EXAMPLE  1009
#define IDC_SORT_NAME     1010
#define IDC_SORT_CAT      1011
#define IDC_STATUS        1012

/* ---------- 文档文件索引 ---------- */
#define DOC_H     0   /* utils.h     */
#define DOC_GENH  1   /* utils_gen.h */
#define DOC_C     2   /* utils.c     */
#define DOC_GENC  3   /* utils_gen.c */
#define DOC_COUNT 4

typedef struct {
    char path[MAX_PATH];
    char display[32];
    char *text;                 /* 读取后已转为 ANSI/GBK */
} FileDoc;

typedef struct { int doc; int line; } Loc;

static HINSTANCE g_hInst;
static HFONT     g_hFont, g_hCodeFont;
static HWND      g_hSearch, g_hCategory, g_hList, g_hDetail;
static HWND      g_hBtnImpl, g_hBtnDecl, g_hCountLbl, g_hStatus;
static HWND      g_hBtnSortName, g_hBtnSortCat;
static HWND      g_hBtnCopyName, g_hBtnCopyEx;

static FileDoc   g_docs[DOC_COUNT];
static int       g_sortMode = 0;   /* 0 原始顺序, 1 按名称, 2 按分类 */
static int      *g_order = NULL;   /* 排序后的显示序列：g_funcs 下标 */
static int       g_order_cap = 0;

/* ---------- 文件读取与编码转换 ---------- */

static char* read_text_file(const char *path) {
    FILE *fp = fopen(path, "rb");
    if (!fp) return NULL;
    fseek(fp, 0, SEEK_END);
    long sz = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    char *buf = (char*)malloc((size_t)sz + 1);
    if (!buf) { fclose(fp); return NULL; }
    if (sz > 0) fread(buf, 1, (size_t)sz, fp);
    buf[sz] = '\0';
    fclose(fp);
    return buf;
}

/* UTF-8 字节串 -> 当前 ANSI 代码页(GBK)字符串，供 ANSI 控件显示 */
static char* u8_to_ansi(const char *u8) {
    if (!u8) return NULL;
    int wlen = MultiByteToWideChar(CP_UTF8, 0, u8, -1, NULL, 0);
    if (wlen <= 0) return NULL;
    wchar_t *w = (wchar_t*)malloc((size_t)wlen * sizeof(wchar_t));
    if (!w) return NULL;
    MultiByteToWideChar(CP_UTF8, 0, u8, -1, w, wlen);
    int alen = WideCharToMultiByte(CP_ACP, 0, w, -1, NULL, 0, NULL, NULL);
    char *a = (char*)malloc(alen > 0 ? (size_t)alen : 1);
    if (!a) { free(w); return NULL; }
    if (alen > 0) WideCharToMultiByte(CP_ACP, 0, w, -1, a, alen, NULL, NULL);
    else a[0] = '\0';
    free(w);
    return a;
}

/* 读取文件：按 UTF-8 读取并转成 ANSI(GBK)；转换失败则原样返回 */
static char* read_text_ansi(const char *path) {
    char *raw = read_text_file(path);
    if (!raw) return NULL;
    char *conv = u8_to_ansi(raw);
    if (conv) { free(raw); return conv; }
    return raw;
}

/* ---------- 路径定位 ---------- */

static void join_path(char *out, int out_size, const char *dir, const char *file) {
    size_t n = strlen(dir);
    size_t fl = strlen(file);
    if (n + fl + 2 >= (size_t)out_size) {
        if (out_size > 0) out[0] = '\0';
        return;
    }
    memcpy(out, dir, n);
    out[n] = '\\';
    memcpy(out + n + 1, file, fl + 1);
}

static int file_exist(const char *p) {
    DWORD attr = GetFileAttributesA(p);
    return (attr != INVALID_FILE_ATTRIBUTES && !(attr & FILE_ATTRIBUTE_DIRECTORY));
}

static void join_dir(char *out, int out_size, const char *dir, const char *suffix) {
    size_t n = strlen(dir);
    size_t sl = strlen(suffix);
    if (n + sl + 1 >= (size_t)out_size) {
        if (out_size > 0) out[0] = '\0';
        return;
    }
    memcpy(out, dir, n);
    memcpy(out + n, suffix, sl + 1);
}

static void init_paths(void) {
    char exe_path[MAX_PATH];
    GetModuleFileNameA(NULL, exe_path, MAX_PATH);
    char *slash = strrchr(exe_path, '\\');
    if (slash) *slash = '\0';

    static const char *names[DOC_COUNT] = { "utils.h", "utils_gen.h", "utils.c", "utils_gen.c" };

    /* 依次尝试多种位置：
     *  0. exe 同目录
     *  1. exe\..\library      （推荐结构：programs\ + library\）
     *  2. exe\..\lib           （兼容旧结构：tools\ + lib\）
     *  3. exe\..\..\library
     *  4. exe\..\..\lib
     *  5. 当前目录
     */
    char dirs[6][MAX_PATH];
    join_dir(dirs[0], MAX_PATH, exe_path, "");
    join_dir(dirs[1], MAX_PATH, exe_path, "\\..\\library");
    join_dir(dirs[2], MAX_PATH, exe_path, "\\..\\lib");
    join_dir(dirs[3], MAX_PATH, exe_path, "\\..\\..\\library");
    join_dir(dirs[4], MAX_PATH, exe_path, "\\..\\..\\lib");
    GetCurrentDirectoryA(MAX_PATH, dirs[5]);

    int ok = 0;
    for (int d = 0; d < 6 && !ok; d++) {
        ok = 1;
        for (int i = 0; i < DOC_COUNT; i++) {
            join_path(g_docs[i].path, MAX_PATH, dirs[d], names[i]);
            if (!file_exist(g_docs[i].path)) { ok = 0; break; }
        }
    }
    for (int i = 0; i < DOC_COUNT; i++) {
        snprintf(g_docs[i].display, sizeof(g_docs[i].display), "%s", names[i]);
    }
}

/* ---------- 行号定位 ---------- */

/* 行内是否出现 "name("（函数名后紧跟左括号） */
static int line_has_call(const char *line, const char *name) {
    size_t nlen = strlen(name);
    const char *q = strstr(line, name);
    while (q) {
        if (q[nlen] == '(') return 1;
        q = strstr(q + 1, name);
    }
    return 0;
}

/* 在某个文档中查找函数行号
 * mode 0：声明行（含 "name("，或 "#define name"）；mode 1：定义行（以 '{' 结尾） */
static int find_in_doc(const FileDoc *doc, const char *name, int mode) {
    int line = 1;
    const char *p = doc->text;
    while (*p) {
        const char *nl = strchr(p, '\n');
        size_t len = nl ? (size_t)(nl - p) : strlen(p);
        char buf[512];
        size_t cl = len < sizeof(buf) - 1 ? len : sizeof(buf) - 1;
        memcpy(buf, p, cl); buf[cl] = '\0';
        if (mode == 1) {
            char *b = buf;
            while (*b == ' ' || *b == '\t') b++;
            size_t bl = strlen(b);
            while (bl > 0 && (b[bl-1]==' '||b[bl-1]=='\t'||b[bl-1]=='\r')) b[--bl] = '\0';
            if (bl > 0 && b[bl-1] == '{' && line_has_call(b, name)) return line;
        } else {
            if (line_has_call(buf, name)) return line;
            /* 宏定义： #define NAME 或 #define NAME(...) */
            char *b = buf;
            while (*b == ' ' || *b == '\t') b++;
            if (strncmp(b, "#define", 7) == 0) {
                char *q = b + 7;
                while (*q == ' ' || *q == '\t') q++;
                size_t nl2 = strlen(name);
                if (strncmp(q, name, nl2) == 0 &&
                    (q[nl2] == '(' || q[nl2] == ' ' || q[nl2] == '\t' || q[nl2] == '\0'))
                    return line;
            }
        }
        if (!nl) break;
        p = nl + 1;
        line++;
    }
    return 0;
}

/* 查找声明：优先 utils.h，其次 utils_gen.h */
static Loc find_decl(const char *name) {
    Loc loc;
    loc.doc = DOC_H;
    loc.line = find_in_doc(&g_docs[DOC_H], name, 0);
    if (loc.line > 0) return loc;
    loc.doc = DOC_GENH;
    loc.line = find_in_doc(&g_docs[DOC_GENH], name, 0);
    return loc;
}

/* 查找实现：优先 utils.c，其次 utils_gen.c；宏等无函数体的回退到声明行 */
static Loc find_impl(const char *name) {
    Loc loc;
    loc.doc = DOC_C;
    loc.line = find_in_doc(&g_docs[DOC_C], name, 1);
    if (loc.line > 0) return loc;
    loc.doc = DOC_GENC;
    loc.line = find_in_doc(&g_docs[DOC_GENC], name, 1);
    if (loc.line > 0) return loc;
    return find_decl(name);
}

/* 提取完整实现源码（从定义行到花括号闭合；宏等无花括号时取整行） */
static char* extract_function_source(const Loc *loc) {
    if (loc->line <= 0) return NULL;
    const char *text = g_docs[loc->doc].text;
    const char *pos = text;
    int line = 1;
    while (line < loc->line) {
        const char *nl = strchr(pos, '\n');
        if (!nl) return NULL;
        pos = nl + 1;
        line++;
    }
    int depth = 0, started = 0;
    const char *p = pos;
    const char *end = p;
    while (*p) {
        if (*p == '{') { depth++; started = 1; }
        else if (*p == '}') {
            depth--;
            if (started && depth == 0) { end = p + 1; break; }
        }
        p++;
    }
    if (!started) {
        /* 宏定义等无花括号：提取到本行末尾 */
        const char *nl = strchr(pos, '\n');
        size_t len = nl ? (size_t)(nl - pos) : strlen(pos);
        while (len > 0 && pos[len-1] == '\r') len--;
        char *src = (char*)malloc(len + 1);
        if (!src) return NULL;
        memcpy(src, pos, len);
        src[len] = '\0';
        return src;
    }
    size_t len = (size_t)(end - pos);
    char *src = (char*)malloc(len + 1);
    if (!src) return NULL;
    memcpy(src, pos, len);
    src[len] = '\0';
    return src;
}

/* ---------- 跳转与剪贴板 ---------- */

static void url_encode(const char *src, char *dst, int dst_size) {
    static const char hex[] = "0123456789ABCDEF";
    int j = 0;
    for (int i = 0; src[i] && j < dst_size - 4; i++) {
        unsigned char c = (unsigned char)src[i];
        if (isalnum(c) || c=='-'||c=='_'||c=='.'||c=='~'||c=='/'||c==':') {
            dst[j++] = (char)c;
        } else {
            dst[j++] = '%';
            dst[j++] = hex[c >> 4];
            dst[j++] = hex[c & 15];
        }
    }
    dst[j] = '\0';
}

static void open_in_vscode(const char *path, int line) {
    char fwd[MAX_PATH], enc[2048], uri[2200];
    int k = 0;
    for (int i = 0; path[i] && k < MAX_PATH - 1; i++) {
        fwd[k++] = (path[i] == '\\') ? '/' : path[i];
    }
    fwd[k] = '\0';
    url_encode(fwd, enc, sizeof(enc));
    if (line > 0) snprintf(uri, sizeof(uri), "vscode://file/%s:%d", enc, line);
    else          snprintf(uri, sizeof(uri), "vscode://file/%s", enc);
    ShellExecuteA(NULL, "open", uri, NULL, NULL, SW_SHOWNORMAL);
}

static void copy_to_clipboard(const char *text) {
    if (!text || !*text) return;
    if (!OpenClipboard(NULL)) return;
    EmptyClipboard();
    size_t len = strlen(text) + 1;
    HGLOBAL h = GlobalAlloc(GMEM_MOVEABLE, len);
    if (h) {
        char *dst = (char*)GlobalLock(h);
        if (dst) { memcpy(dst, text, len); GlobalUnlock(h); }
        SetClipboardData(CF_TEXT, h);
    }
    CloseClipboard();
}

/* ---------- 列表与详情 ---------- */

static int get_selected_func_index(void) {
    int sel = (int)ListView_GetNextItem(g_hList, -1, LVNI_SELECTED);
    if (sel < 0) return -1;
    LVITEMA item;
    memset(&item, 0, sizeof(item));
    item.mask = LVIF_PARAM;
    item.iItem = sel;
    if (ListView_GetItem(g_hList, &item)) return (int)item.lParam;
    return -1;
}

static int cmp_name(const void *a, const void *b) {
    return strcmp(g_funcs[*(const int*)a].name, g_funcs[*(const int*)b].name);
}
static int cmp_section(const void *a, const void *b) {
    int c = strcmp(g_funcs[*(const int*)a].section, g_funcs[*(const int*)b].section);
    if (c) return c;
    return strcmp(g_funcs[*(const int*)a].name, g_funcs[*(const int*)b].name);
}

static void update_sort_buttons(void) {
    SetWindowTextA(g_hBtnSortName, (g_sortMode == 1) ? "按名称排序 √" : "按名称排序");
    SetWindowTextA(g_hBtnSortCat,  (g_sortMode == 2) ? "按分类排序 √" : "按分类排序");
}

static void show_detail(int func_index) {
    const FuncInfo *f = &g_funcs[func_index];
    Loc decl = find_decl(f->name);
    Loc impl = find_impl(f->name);
    char *src = (impl.line > 0) ? extract_function_source(&impl) : NULL;

    size_t need = 1024 + strlen(f->name) + strlen(f->section) + strlen(f->desc)
                + strlen(f->example) + (src ? strlen(src) : 128);
    char *buf = (char*)malloc(need);
    if (!buf) { free(src); return; }
    int len = snprintf(buf, need,
        "函数名 : %s\r\n"
        "分类   : %s\r\n"
        "功能   : %s\r\n"
        "示例   : %s\r\n"
        "声明位置: %s 第 %d 行\r\n"
        "实现位置: %s 第 %d 行\r\n"
        "（单击查看详情 · 双击或点[打开实现]跳转 VS Code）\r\n"
        "\r\n---------- 实现源码 ----------\r\n%s",
        f->name, f->section, f->desc, f->example,
        decl.line > 0 ? g_docs[decl.doc].display : "-",
        decl.line,
        impl.line > 0 ? g_docs[impl.doc].display : "-",
        impl.line,
        src ? src : "(未能提取源码：请确认 utils.c / utils_gen.c 与 utils_gui.exe 在同一目录)");
    (void)len;
    SetWindowTextA(g_hDetail, buf);
    free(buf);
    free(src);
}

static void refresh_list(void) {
    char kw[128], kw_low[128];
    GetWindowTextA(g_hSearch, kw, sizeof(kw));
    int i = 0;
    while (kw[i] && i < (int)sizeof(kw_low) - 1) {
        kw_low[i] = (char)tolower((unsigned char)kw[i]);
        i++;
    }
    kw_low[i] = '\0';

    /* 空格分隔的多关键词（AND） */
    char *terms[16];
    int nterm = 0;
    {
        char tmp[128];
        strncpy(tmp, kw_low, sizeof(tmp) - 1); tmp[sizeof(tmp)-1] = '\0';
        char *tok = strtok(tmp, " ");
        while (tok && nterm < 16) {
            if (*tok) terms[nterm++] = tok;
            tok = strtok(NULL, " ");
        }
    }

    /* 当前选中的分类（CB_GETITEMDATA 存原始分类名） */
    const char *cat_name = "";
    int cat_sel = (int)SendMessageA(g_hCategory, CB_GETCURSEL, 0, 0);
    if (cat_sel > 0) {
        const char *cp = (const char*)SendMessageA(g_hCategory, CB_GETITEMDATA, (WPARAM)cat_sel, 0);
        if (cp) cat_name = cp;
    }

    /* 筛选 + 收集显示顺序 */
    int shown = 0;
    for (i = 0; i < FUNC_COUNT; i++) {
        const FuncInfo *f = &g_funcs[i];
        if (cat_name[0] && strcmp(f->section, cat_name) != 0) continue;
        if (nterm > 0) {
            char n[200], d[200], s[200];
            int j = 0;
            while (f->name[j] && j < 199) { n[j] = (char)tolower((unsigned char)f->name[j]); j++; }
            n[j] = '\0';
            j = 0;
            while (f->desc[j] && j < 199) { d[j] = (char)tolower((unsigned char)f->desc[j]); j++; }
            d[j] = '\0';
            j = 0;
            while (f->section[j] && j < 199) { s[j] = (char)tolower((unsigned char)f->section[j]); j++; }
            s[j] = '\0';
            int all = 1;
            for (int t = 0; t < nterm; t++) {
                if (!strstr(n, terms[t]) && !strstr(d, terms[t]) && !strstr(s, terms[t])) { all = 0; break; }
            }
            if (!all) continue;
        }
        if (shown >= g_order_cap) {
            int nc = g_order_cap ? g_order_cap * 2 : 256;
            int *np = (int*)realloc(g_order, (size_t)nc * sizeof(int));
            if (!np) break;
            g_order = np;
            g_order_cap = nc;
        }
        g_order[shown++] = i;
    }

    if (g_sortMode == 1) qsort(g_order, (size_t)shown, sizeof(int), cmp_name);
    else if (g_sortMode == 2) qsort(g_order, (size_t)shown, sizeof(int), cmp_section);

    ListView_DeleteAllItems(g_hList);
    for (int k = 0; k < shown; k++) {
        const FuncInfo *f = &g_funcs[g_order[k]];
        LVITEMA item;
        memset(&item, 0, sizeof(item));
        item.mask = LVIF_TEXT | LVIF_PARAM;
        item.iItem = k;
        item.iSubItem = 0;
        item.pszText = (LPSTR)f->name;
        item.lParam = g_order[k];
        int row = (int)ListView_InsertItem(g_hList, &item);
        ListView_SetItemText(g_hList, row, 1, (LPSTR)f->section);
        ListView_SetItemText(g_hList, row, 2, (LPSTR)f->desc);
    }

    char cnt[192];
    snprintf(cnt, sizeof(cnt), "显示 %d / %d 个函数", shown, FUNC_COUNT);
    SetWindowTextA(g_hCountLbl, cnt);
    SetWindowTextA(g_hStatus, cnt);

    /* 自动选中第一项并显示详情 */
    if (shown > 0) {
        ListView_SetItemState(g_hList, 0, LVIS_SELECTED | LVIS_FOCUSED, LVIS_SELECTED | LVIS_FOCUSED);
        show_detail(g_order[0]);
    } else {
        SetWindowTextA(g_hDetail, "（没有匹配的函数，请尝试更换关键词或分类）");
    }
}

/* ---------- 分类下拉（带数量） ---------- */

static void build_category_list(void) {
    const char *cats[256];
    int ncat = 0;
    for (int i = 0; i < FUNC_COUNT; i++) {
        const char *s = g_funcs[i].section;
        int found = 0;
        for (int j = 0; j < ncat; j++) if (strcmp(cats[j], s) == 0) { found = 1; break; }
        if (!found && ncat < 256) cats[ncat++] = s;
    }
    SendMessageA(g_hCategory, CB_RESETCONTENT, 0, 0);
    SendMessageA(g_hCategory, CB_ADDSTRING, 0, (LPARAM)"全部");
    for (int j = 0; j < ncat; j++) {
        int cnt = 0;
        for (int i = 0; i < FUNC_COUNT; i++) if (strcmp(g_funcs[i].section, cats[j]) == 0) cnt++;
        char label[220];
        snprintf(label, sizeof(label), "%s  [%d]", cats[j], cnt);
        int item = (int)SendMessageA(g_hCategory, CB_ADDSTRING, 0, (LPARAM)label);
        SendMessageA(g_hCategory, CB_SETITEMDATA, (WPARAM)item, (LPARAM)cats[j]);
    }
    SendMessageA(g_hCategory, CB_SETCURSEL, 0, 0);
}

/* ---------- 控件创建 ---------- */

static void create_controls(HWND hwnd) {
    CreateWindowA("STATIC", "搜索:", WS_CHILD | WS_VISIBLE, 10, 8, 44, 24, hwnd, NULL, g_hInst, NULL);
    g_hSearch = CreateWindowA("EDIT", "", WS_CHILD | WS_VISIBLE | WS_BORDER | ES_AUTOHSCROLL,
        56, 6, 180, 24, hwnd, (HMENU)IDC_SEARCH, g_hInst, NULL);

    CreateWindowA("STATIC", "分类:", WS_CHILD | WS_VISIBLE, 246, 8, 40, 24, hwnd, NULL, g_hInst, NULL);
    g_hCategory = CreateWindowA("COMBOBOX", "",
        WS_CHILD | WS_VISIBLE | WS_BORDER | CBS_DROPDOWNLIST | WS_VSCROLL,
        288, 6, 190, 340, hwnd, (HMENU)IDC_CATEGORY, g_hInst, NULL);

    g_hBtnImpl = CreateWindowA("BUTTON", "打开实现", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
        488, 6, 92, 26, hwnd, (HMENU)IDC_OPEN_IMPL, g_hInst, NULL);
    g_hBtnDecl = CreateWindowA("BUTTON", "打开声明", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
        586, 6, 92, 26, hwnd, (HMENU)IDC_OPEN_DECL, g_hInst, NULL);

    g_hCountLbl = CreateWindowA("STATIC", "", WS_CHILD | WS_VISIBLE,
        690, 8, 470, 24, hwnd, NULL, g_hInst, NULL);

    /* 第二行 */
    g_hBtnSortName = CreateWindowA("BUTTON", "按名称排序", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
        10, 34, 100, 26, hwnd, (HMENU)IDC_SORT_NAME, g_hInst, NULL);
    g_hBtnSortCat = CreateWindowA("BUTTON", "按分类排序", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
        116, 34, 100, 26, hwnd, (HMENU)IDC_SORT_CAT, g_hInst, NULL);
    g_hBtnCopyName = CreateWindowA("BUTTON", "复制函数名", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
        222, 34, 100, 26, hwnd, (HMENU)IDC_COPY_NAME, g_hInst, NULL);
    g_hBtnCopyEx = CreateWindowA("BUTTON", "复制示例", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
        328, 34, 100, 26, hwnd, (HMENU)IDC_COPY_EXAMPLE, g_hInst, NULL);

    /* 列表 */
    g_hList = CreateWindowA(WC_LISTVIEWA, "",
        WS_CHILD | WS_VISIBLE | WS_BORDER | LVS_REPORT | LVS_SINGLESEL | LVS_SHOWSELALWAYS,
        0, 0, 0, 0, hwnd, (HMENU)IDC_LIST, g_hInst, NULL);
    ListView_SetExtendedListViewStyle(g_hList,
        LVS_EX_FULLROWSELECT | LVS_EX_GRIDLINES | LVS_EX_DOUBLEBUFFER);
    LVCOLUMNA col;
    memset(&col, 0, sizeof(col));
    col.mask = LVCF_TEXT | LVCF_WIDTH;
    col.pszText = "函数名"; col.cx = 240; ListView_InsertColumn(g_hList, 0, &col);
    col.pszText = "分类";   col.cx = 150; ListView_InsertColumn(g_hList, 1, &col);
    col.pszText = "功能";   col.cx = 380; ListView_InsertColumn(g_hList, 2, &col);

    /* 详情（代码字体） */
    g_hDetail = CreateWindowA("EDIT", "",
        WS_CHILD | WS_VISIBLE | WS_BORDER | ES_MULTILINE | ES_READONLY |
        WS_VSCROLL | WS_HSCROLL | ES_AUTOVSCROLL,
        0, 0, 0, 0, hwnd, (HMENU)IDC_DETAIL, g_hInst, NULL);
    SendMessage(g_hDetail, EM_SETLIMITTEXT, 0x7FFFFFFF, 0);

    /* 状态栏 */
    g_hStatus = CreateWindowA("STATIC", "", WS_CHILD | WS_VISIBLE,
        0, 0, 0, 0, hwnd, (HMENU)IDC_STATUS, g_hInst, NULL);

    /* 字体 */
    SendMessage(g_hSearch,   WM_SETFONT, (WPARAM)g_hFont, TRUE);
    SendMessage(g_hCategory, WM_SETFONT, (WPARAM)g_hFont, TRUE);
    SendMessage(g_hBtnImpl,  WM_SETFONT, (WPARAM)g_hFont, TRUE);
    SendMessage(g_hBtnDecl,  WM_SETFONT, (WPARAM)g_hFont, TRUE);
    SendMessage(g_hBtnSortName, WM_SETFONT, (WPARAM)g_hFont, TRUE);
    SendMessage(g_hBtnSortCat,  WM_SETFONT, (WPARAM)g_hFont, TRUE);
    SendMessage(g_hBtnCopyName, WM_SETFONT, (WPARAM)g_hFont, TRUE);
    SendMessage(g_hBtnCopyEx,   WM_SETFONT, (WPARAM)g_hFont, TRUE);
    SendMessage(g_hCountLbl, WM_SETFONT, (WPARAM)g_hFont, TRUE);
    SendMessage(g_hStatus,   WM_SETFONT, (WPARAM)g_hFont, TRUE);
    SendMessage(g_hList,     WM_SETFONT, (WPARAM)g_hFont, TRUE);
    SendMessage(g_hDetail,   WM_SETFONT, (WPARAM)g_hCodeFont, TRUE);

    build_category_list();
    update_sort_buttons();
    refresh_list();
}

/* ---------- 窗口过程 ---------- */

static LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
    case WM_CREATE:
        g_hFont = CreateFontA(-16, 0, 0, 0, FW_NORMAL, 0, 0, 0, DEFAULT_CHARSET,
            OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY,
            DEFAULT_PITCH, "Microsoft YaHei");
        g_hCodeFont = CreateFontA(-15, 0, 0, 0, FW_NORMAL, 0, 0, 0, DEFAULT_CHARSET,
            OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY,
            FIXED_PITCH, "Consolas");
        create_controls(hwnd);
        return 0;

    case WM_SIZE: {
        int w = LOWORD(lParam), h = HIWORD(lParam);
        int topY = 64;
        int statusH = 24;
        int detailW = 450;
        int listW = w - detailW - 25;
        if (listW < 320) listW = 320;
        MoveWindow(g_hList, 10, topY, listW, h - topY - statusH - 10, TRUE);
        MoveWindow(g_hDetail, 10 + listW + 10, topY, w - listW - 25, h - topY - statusH - 10, TRUE);
        MoveWindow(g_hStatus, 0, h - statusH, w, statusH, TRUE);
        return 0;
    }

    case WM_CTLCOLORSTATIC:
    case WM_CTLCOLOREDIT: {
        HDC hdc = (HDC)wParam;
        SetBkColor(hdc, RGB(255, 255, 255));
        SetTextColor(hdc, RGB(30, 30, 30));
        return (LRESULT)GetStockObject(WHITE_BRUSH);
    }

    case WM_COMMAND: {
        int id = LOWORD(wParam), code = HIWORD(wParam);
        if (id == IDC_SEARCH && code == EN_CHANGE) {
            refresh_list();
        } else if (id == IDC_CATEGORY && code == CBN_SELCHANGE) {
            refresh_list();
        } else if (id == IDC_OPEN_IMPL && code == BN_CLICKED) {
            int idx = get_selected_func_index();
            if (idx >= 0) {
                Loc impl = find_impl(g_funcs[idx].name);
                if (impl.line > 0) open_in_vscode(g_docs[impl.doc].path, impl.line);
                else { Loc d = find_decl(g_funcs[idx].name); if (d.line > 0) open_in_vscode(g_docs[d.doc].path, d.line); }
            }
        } else if (id == IDC_OPEN_DECL && code == BN_CLICKED) {
            int idx = get_selected_func_index();
            if (idx >= 0) {
                Loc d = find_decl(g_funcs[idx].name);
                if (d.line > 0) open_in_vscode(g_docs[d.doc].path, d.line);
                else { Loc impl = find_impl(g_funcs[idx].name); if (impl.line > 0) open_in_vscode(g_docs[impl.doc].path, impl.line); }
            }
        } else if (id == IDC_COPY_NAME && code == BN_CLICKED) {
            int idx = get_selected_func_index();
            if (idx >= 0) copy_to_clipboard(g_funcs[idx].name);
        } else if (id == IDC_COPY_EXAMPLE && code == BN_CLICKED) {
            int idx = get_selected_func_index();
            if (idx >= 0) copy_to_clipboard(g_funcs[idx].example);
        } else if (id == IDC_SORT_NAME && code == BN_CLICKED) {
            g_sortMode = (g_sortMode == 1) ? 0 : 1;
            update_sort_buttons();
            refresh_list();
        } else if (id == IDC_SORT_CAT && code == BN_CLICKED) {
            g_sortMode = (g_sortMode == 2) ? 0 : 2;
            update_sort_buttons();
            refresh_list();
        }
        return 0;
    }

    case WM_NOTIFY: {
        NMHDR *nm = (NMHDR*)lParam;
        if (nm->hwndFrom == g_hList) {
            if (nm->code == LVN_ITEMCHANGED) {
                NMLISTVIEW *nmlv = (NMLISTVIEW*)lParam;
                if (nmlv->uNewState & LVIS_SELECTED) {
                    int idx = get_selected_func_index();
                    if (idx >= 0) show_detail(idx);
                }
            } else if (nm->code == NM_DBLCLK) {
                int idx = get_selected_func_index();
                if (idx >= 0) {
                    Loc impl = find_impl(g_funcs[idx].name);
                    if (impl.line > 0) open_in_vscode(g_docs[impl.doc].path, impl.line);
                    else { Loc d = find_decl(g_funcs[idx].name); if (d.line > 0) open_in_vscode(g_docs[d.doc].path, d.line); }
                }
            } else if (nm->code == LVN_COLUMNCLICK) {
                NMLISTVIEW *nmlv = (NMLISTVIEW*)lParam;
                if (nmlv->iSubItem == 0) g_sortMode = 1;
                else if (nmlv->iSubItem == 1) g_sortMode = 2;
                else g_sortMode = 0;
                update_sort_buttons();
                refresh_list();
            }
        }
        return 0;
    }

    case WM_DESTROY:
        if (g_hFont) DeleteObject(g_hFont);
        if (g_hCodeFont) DeleteObject(g_hCodeFont);
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProcA(hwnd, msg, wParam, lParam);
}

/* ---------- 入口 ---------- */

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrev, LPSTR lpCmdLine, int nCmdShow) {
    (void)hPrev; (void)lpCmdLine;
    g_hInst = hInstance;

    INITCOMMONCONTROLSEX icc;
    icc.dwSize = sizeof(icc);
    icc.dwICC = ICC_LISTVIEW_CLASSES;
    InitCommonControlsEx(&icc);

    init_paths();
    for (int i = 0; i < DOC_COUNT; i++) {
        g_docs[i].text = read_text_ansi(g_docs[i].path);
    }
    if (!g_docs[DOC_H].text || !g_docs[DOC_GENH].text || !g_docs[DOC_C].text || !g_docs[DOC_GENC].text) {
        MessageBoxA(NULL,
            "未找到 utils.h / utils_gen.h / utils.c / utils_gen.c！\n"
            "请将 utils_gui.exe 放在与这 4 个文件相同的目录下运行。",
            "UTILS 图形化查找工具", MB_ICONERROR);
        return 1;
    }

    WNDCLASSA wc;
    memset(&wc, 0, sizeof(wc));
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInstance;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_BTNFACE + 1);
    wc.lpszClassName = "UtilsGuiMain";
    if (!RegisterClassA(&wc)) return 1;

    HWND hwnd = CreateWindowA("UtilsGuiMain",
        "UTILS 函数库 v2.0 · 图形化查找工具",
        WS_OVERLAPPEDWINDOW | WS_CLIPCHILDREN,
        CW_USEDEFAULT, CW_USEDEFAULT, 1180, 720,
        NULL, NULL, hInstance, NULL);
    if (!hwnd) return 1;
    ShowWindow(hwnd, nCmdShow);
    UpdateWindow(hwnd);

    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    for (int i = 0; i < DOC_COUNT; i++) free(g_docs[i].text);
    free(g_order);
    return (int)msg.wParam;
}
