/* ============================================================
 *  utils_gui.c — UTILS 函数库 · 图形化查找工具 v2.1（Windows GUI）
 * ------------------------------------------------------------
 *  功能：
 *   1. 左侧列表展示全部函数：关键词搜索（支持子串 + 模糊匹配）、
 *      分类筛选（带数量）、排序（原序/名称/分类）
 *   2. 右侧详情窗格（RichEdit）：功能说明 + 调用示例 + 源码位置
 *      + 实现源码，源码按 VS Code Dark+ 风格语法高亮
 *   3. 双击函数 / 按钮跳转 VS Code（直接调用 Code.exe --goto）
 *   4. 复制函数名 / 示例 / 实现源码
 *   5. 支持 utils.h / utils_gen.h / utils.c / utils_gen.c 四文件
 *
 *  配色：读取同目录 theme.ini（不存在则用内置 Dark+ 默认值）
 *
 *  编译（MinGW gcc）：
 *    gcc -finput-charset=UTF-8 -fexec-charset=GBK -I..\library \
 *        -o utils_gui.exe utils_gui.c -mwindows -lcomctl32 -lshell32
 *
 *  文件组织结构：
 *    A. 头文件 / 常量 / 结构体 / 全局
 *    B. 文件读取与编码转换
 *    C. 路径定位
 *    D. 行号定位与源码提取
 *    E. 主题配色（theme.ini + 默认值）
 *    F. 跳转与剪贴板
 *    G. 语法高亮（RichEdit）
 *    H. 模糊查找与列表
 *    I. 详情显示
 *    J. 控件创建
 *    K. 窗口过程
 *    L. 入口
 * ============================================================ */

/* ============ A. 头文件 / 常量 / 结构体 / 全局 ============ */

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include <commctrl.h>
#include <richedit.h>
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
#define IDC_COPY_SRC      1013

/* ---------- 文档文件索引 ---------- */
#define DOC_H     0   /* utils.h     */
#define DOC_GENH  1   /* utils_gen.h */
#define DOC_C     2   /* utils.c     */
#define DOC_GENC  3   /* utils_gen.c */
#define DOC_COUNT 4

/* ---------- 结构体 ---------- */

typedef struct {                 /* 一个源文档 */
    char path[MAX_PATH];
    char display[32];
    char *text;                  /* 读取后已转为 ANSI/GBK */
} FileDoc;

typedef struct { int doc; int line; } Loc;   /* 位置：文档 + 行号 */

typedef struct {                 /* 列表匹配项（用于模糊查找排序） */
    int idx;                     /* g_funcs 下标 */
    int score;                   /* 匹配分，越大越靠前 */
} MatchItem;

typedef struct {                 /* 主题配色（参照 VS Code Dark+） */
    COLORREF background;         /* 详情背景（暗色） */
    COLORREF default_txt;        /* 普通文本 */
    COLORREF meta;               /* 元信息（函数名/分类等） */
    COLORREF keyword;            /* 类型关键字 int/void/uint8_t... */
    COLORREF control;            /* 控制关键字 if/for/return... */
    COLORREF type;               /* struct/enum 等类型名 */
    COLORREF func;               /* 函数名 */
    COLORREF param;              /* 形参 */
    COLORREF string;             /* 字符串/字符 */
    COLORREF number;             /* 数字 */
    COLORREF comment;            /* 注释 */
    COLORREF macro;              /* 宏/预处理 */
    COLORREF header;             /* #include <头文件> */
} Theme;

/* ---------- 全局变量 ---------- */

static HINSTANCE g_hInst;
static HFONT     g_hFont, g_hCodeFont;
static HWND      g_hSearch, g_hCategory, g_hList, g_hDetail;
static HWND      g_hBtnImpl, g_hBtnDecl, g_hCountLbl, g_hStatus;
static HWND      g_hBtnSortName, g_hBtnSortCat;
static HWND      g_hBtnCopyName, g_hBtnCopyEx, g_hBtnCopySrc;

static FileDoc   g_docs[DOC_COUNT];
static Theme     g_theme;
static int       g_sortMode = 0;   /* 0 原始顺序, 1 按名称, 2 按分类 */
static MatchItem *g_order = NULL;  /* 排序后的显示序列 */
static int       g_order_cap = 0;
static int       g_hoverRow = -1;  /* 鼠标悬停行（-1 表示无） */

/* ============ B. 文件读取与编码转换 ============ */

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

/* ============ C. 路径定位 ============ */

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

/* 定位四个源文件 + theme.ini，自动尝试多种目录 */
static void init_paths(void) {
    char exe_path[MAX_PATH];
    GetModuleFileNameA(NULL, exe_path, MAX_PATH);
    char *slash = strrchr(exe_path, '\\');
    if (slash) *slash = '\0';

    static const char *names[DOC_COUNT] = { "utils.h", "utils_gen.h", "utils.c", "utils_gen.c" };

    /* 依次尝试：exe 同目录 / ..\library / ..\lib / ..\..\library / ..\..\lib / 当前目录 */
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

/* ============ D. 行号定位与源码提取 ============ */

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

/* 提取完整实现源码（定义行到花括号闭合）。
 * 注意：会跳过字符串/字符/注释，避免其中的花括号干扰配对 */
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
        char c = *p;
        if (c == '/' && p[1] == '/') {          /* 行注释 */
            while (*p && *p != '\n') p++;
            continue;
        }
        if (c == '/' && p[1] == '*') {          /* 块注释 */
            p += 2;
            while (*p && !(p[0] == '*' && p[1] == '/')) p++;
            if (*p) p += 2;
            continue;
        }
        if (c == '"') {                         /* 字符串 */
            p++;
            while (*p && *p != '"' && *p != '\n') {
                if (*p == '\\' && p[1]) p++;
                p++;
            }
            if (*p == '"') p++;
            continue;
        }
        if (c == '\'') {                        /* 字符字面量 */
            p++;
            while (*p && *p != '\'' && *p != '\n') {
                if (*p == '\\' && p[1]) p++;
                p++;
            }
            if (*p == '\'') p++;
            continue;
        }
        if (c == '{') { depth++; started = 1; }
        else if (c == '}') {
            depth--;
            if (started && depth == 0) { end = p + 1; break; }
        }
        p++;
    }
    if (!started) {
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

/* 提取函数声明前的文档注释块（含 @param / @return 等），返回清理后的文本 */
static char* extract_doc_block(const Loc *decl) {
    if (decl->line <= 0) return NULL;
    const char *text = g_docs[decl->doc].text;
    const char *pos = text;
    int line = 1;
    while (line < decl->line) {
        const char *nl = strchr(pos, '\n');
        if (!nl) return NULL;
        pos = nl + 1;
        line++;
    }
    /* 从文本开头到声明行，找最后一个文档注释起始标记（斜杠+双星号） */
    const char *p = text;
    const char *last = NULL;
    while (p < pos) {
        if (p[0] == '/' && p[1] == '*' && p[2] == '*') last = p;
        p++;
    }
    if (!last) return NULL;
    /* 找注释结束标记（星号+斜杠） */
    const char *q = last + 3;
    const char *end = NULL;
    while (q + 1 < pos) {
        if (q[0] == '*' && q[1] == '/') { end = q; break; }
        q++;
    }
    if (!end) return NULL;

    size_t cap = (size_t)(end - last) + 4;
    char *out = (char*)malloc(cap);
    if (!out) return NULL;
    size_t o = 0;
    const char *ln = last;
    while (ln < end) {
        const char *nl2 = strchr(ln, '\n');
        const char *le = (nl2 && nl2 < end) ? nl2 : end;
        const char *a = ln;
        const char *b = le;
        while (a < b && (*a == ' ' || *a == '\t')) a++;
        if (a < b && *a == '*') {
            a++;
            if (a < b && *a == ' ') a++;
        }
        while (b > a && (b[-1] == ' ' || b[-1] == '\t' || b[-1] == '\r')) b--;
        size_t linelen = (size_t)(b - a);
        if (linelen > 0) {
            if (o + linelen + 3 > cap) break;
            memcpy(out + o, a, linelen);
            o += linelen;
            out[o++] = '\r';
            out[o++] = '\n';
        }
        if (!nl2) break;
        ln = nl2 + 1;
    }
    if (o > 0 && out[o-1] == '\n') o--;
    if (o > 0 && out[o-1] == '\r') o--;
    out[o] = '\0';
    if (o == 0) { free(out); return NULL; }
    return out;
}

/* ============ E. 主题配色（theme.ini + 默认值） ============ */

static COLORREF rgb(int r, int g, int b) { return RGB(r, g, b); }

/* 十六进制 "RRGGBB" -> COLORREF */
static COLORREF parse_color(const char *s) {
    unsigned v = 0;
    int n = 0;
    while (*s && n < 6) {
        int d;
        if      (*s >= '0' && *s <= '9') d = *s - '0';
        else if (*s >= 'a' && *s <= 'f') d = *s - 'a' + 10;
        else if (*s >= 'A' && *s <= 'F') d = *s - 'A' + 10;
        else break;
        v = v * 16 + (unsigned)d;
        s++;
        n++;
    }
    if (n < 6) return 0;
    return RGB((v >> 16) & 0xFF, (v >> 8) & 0xFF, v & 0xFF);
}

/* 内置默认配色：VS Code Dark+ 风格 */
static void theme_default(Theme *t) {
    /* Notepad++ 默认风格（白底黑字） */
    t->background = rgb(0xFF, 0xFF, 0xFF);
    t->default_txt= rgb(0x00, 0x00, 0x00);
    t->meta       = rgb(0x00, 0x80, 0x00);   /* 介绍/详细说明：注释绿 */
    t->keyword    = rgb(0x00, 0x00, 0xFF);
    t->control    = rgb(0x7F, 0x00, 0x55);
    t->type       = rgb(0x2F, 0x6F, 0x9F);
    t->func       = rgb(0x00, 0x00, 0xC0);
    t->param      = rgb(0x00, 0x00, 0x00);
    t->string     = rgb(0x80, 0x80, 0x80);
    t->number     = rgb(0x00, 0x00, 0x00);
    t->comment    = rgb(0x00, 0x80, 0x00);
    t->macro      = rgb(0x7F, 0x00, 0x55);
    t->header     = rgb(0x2F, 0x6F, 0x9F);
}

/* 从 theme.ini 读取配色（格式：# 注释 / key=RRGGBB） */
static void load_theme(const char *path) {
    theme_default(&g_theme);
    FILE *fp = fopen(path, "r");
    if (!fp) return;
    char line[128];
    while (fgets(line, sizeof(line), fp)) {
        char *p = line;
        while (*p == ' ' || *p == '\t') p++;
        if (*p == '#' || *p == '\n' || *p == '\0') continue;
        char key[32], val[32];
        if (sscanf(p, "%31[^= \t]=%31s", key, val) == 2) {
            COLORREF c = parse_color(val);
            if      (strcmp(key, "background") == 0) g_theme.background = c;
            else if (strcmp(key, "default")    == 0) g_theme.default_txt = c;
            else if (strcmp(key, "meta")       == 0) g_theme.meta        = c;
            else if (strcmp(key, "keyword")    == 0) g_theme.keyword     = c;
            else if (strcmp(key, "control")    == 0) g_theme.control     = c;
            else if (strcmp(key, "type")       == 0) g_theme.type        = c;
            else if (strcmp(key, "func")       == 0) g_theme.func        = c;
            else if (strcmp(key, "param")      == 0) g_theme.param       = c;
            else if (strcmp(key, "string")     == 0) g_theme.string      = c;
            else if (strcmp(key, "number")     == 0) g_theme.number      = c;
            else if (strcmp(key, "comment")    == 0) g_theme.comment     = c;
            else if (strcmp(key, "macro")      == 0) g_theme.macro       = c;
            else if (strcmp(key, "header")     == 0) g_theme.header      = c;
        }
    }
    fclose(fp);
}

/* ============ F. 跳转与剪贴板 ============ */

/* 定位 VS Code 可执行文件（Code.exe） */
static int find_code_exe(char *out, int out_size) {
    char local[MAX_PATH];
    if (GetEnvironmentVariableA("LOCALAPPDATA", local, MAX_PATH) > 0) {
        snprintf(out, out_size, "%s\\Programs\\Microsoft VS Code\\Code.exe", local);
        if (file_exist(out)) return 1;
    }
    static const char *cands[] = {
        "C:\\Program Files\\Microsoft VS Code\\Code.exe",
        "C:\\Program Files (x86)\\Microsoft VS Code\\Code.exe",
        "C:\\Program Files\\Microsoft VS Code\\bin\\code.cmd",
    };
    for (int i = 0; i < 3; i++) {
        if (file_exist(cands[i])) {
            strncpy(out, cands[i], out_size - 1);
            out[out_size - 1] = '\0';
            return 1;
        }
    }
    return 0;
}

static void open_in_vscode(const char *path, int line) {
    char code[MAX_PATH];
    if (find_code_exe(code, sizeof(code))) {
        /* 直接调用 Code.exe --goto "文件路径:行号"，最可靠 */
        char args[1100];
        if (line > 0) snprintf(args, sizeof(args), "--goto \"%s:%d\"", path, line);
        else          snprintf(args, sizeof(args), "\"%s\"", path);
        ShellExecuteA(NULL, "open", code, args, NULL, SW_SHOWNORMAL);
        return;
    }
    /* 回退：vscode:// 协议 */
    char uri[2200];
    snprintf(uri, sizeof(uri), "vscode://file/%s:%d", path, line);
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

/* ============ G. 语法高亮（RichEdit，Dark+ 风格） ============ */

static void apply_rich_color(int start, int end, COLORREF color, int bold) {
    if (start >= end) return;
    CHARFORMATA cf;
    memset(&cf, 0, sizeof(cf));
    cf.cbSize = sizeof(cf);
    cf.dwMask = CFM_COLOR | (bold ? CFM_BOLD : 0);
    cf.dwEffects = bold ? CFE_BOLD : 0;
    cf.crTextColor = color;
    SendMessage(g_hDetail, EM_SETSEL, start, end);
    SendMessage(g_hDetail, EM_SETCHARFORMAT, SCF_SELECTION, (LPARAM)&cf);
}

static int is_ident_char(char c) {
    return ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
            (c >= '0' && c <= '9') || c == '_');
}

/* 返回 0=非关键字, 1=类型关键字, 2=控制关键字 */
static int keyword_class(const char *w) {
    static const char *ctrl[] = {
        "if","else","for","while","do","return","break","continue",
        "switch","case","default","goto"
    };
    for (size_t i = 0; i < sizeof(ctrl)/sizeof(ctrl[0]); i++)
        if (strcmp(w, ctrl[i]) == 0) return 2;
    static const char *types[] = {
        "void","char","short","int","long","float","double","signed","unsigned",
        "const","volatile","static","struct","union","enum","typedef","extern",
        "register","inline","bool","sizeof",
        "uint8_t","uint16_t","uint32_t","uint64_t","int8_t","int16_t","int32_t",
        "int64_t","size_t","FILE","NULL"
    };
    for (size_t i = 0; i < sizeof(types)/sizeof(types[0]); i++)
        if (strcmp(w, types[i]) == 0) return 1;
    return 0;
}

/* 对详情文本做语法高亮；code_start 为“实现源码”正文起始位置 */
static void highlight_code(const char *text, int code_start, int code_end) {
    int len = (int)strlen(text);
    if (code_end < code_start) code_end = code_start;
    if (code_end > len) code_end = len;
    apply_rich_color(0, code_start, g_theme.meta, 0);          /* 介绍：绿 */
    apply_rich_color(code_end, len, g_theme.meta, 0);          /* 详细说明：绿 */
    apply_rich_color(code_start, code_end, g_theme.default_txt, 0);

    int first_func = 1;   /* 代码区第一个函数名为定义处，括号内为形参 */
    int prev_struct = 0;  /* 上一个 token 是 struct/enum/union */
    int i = code_start;
    while (i < code_end) {
        char c = text[i];

        /* 行注释 */
        if (c == '/' && i + 1 < len && text[i+1] == '/') {
            int s = i;
            while (i < code_end && text[i] != '\n') i++;
            apply_rich_color(s, i, g_theme.comment, 0);
            continue;
        }
        /* 块注释 */
        if (c == '/' && i + 1 < len && text[i+1] == '*') {
            int s = i; i += 2;
            while (i + 1 < len && !(text[i] == '*' && text[i+1] == '/')) i++;
            i += 2; if (i > code_end) i = code_end;
            apply_rich_color(s, i, g_theme.comment, 0);
            continue;
        }
        /* 字符串 */
        if (c == '"') {
            int s = i; i++;
            while (i < code_end && text[i] != '"' && text[i] != '\n') i++;
            if (i < code_end && text[i] == '"') i++;
            apply_rich_color(s, i, g_theme.string, 0);
            continue;
        }
        /* 字符字面量 */
        if (c == '\'') {
            int s = i; i++;
            while (i < code_end && text[i] != '\'' && text[i] != '\n') i++;
            if (i < code_end && text[i] == '\'') i++;
            apply_rich_color(s, i, g_theme.string, 0);
            continue;
        }
        /* 预处理 / 宏 */
        if (c == '#') {
            int s = i;
            while (i < code_end && text[i] != '\n') i++;
            int e = i;
            apply_rich_color(s, e, g_theme.macro, 0);
            /* #include <头文件>：尖括号内容用 header 色加粗 */
            for (int p = s; p < e; p++) {
                if (text[p] == '<') {
                    int q = p + 1;
                    while (q < e && text[q] != '>') q++;
                    if (q < e) { apply_rich_color(p, q + 1, g_theme.header, 1); p = q; }
                }
            }
            continue;
        }
        /* 数字 */
        if (c >= '0' && c <= '9') {
            int s = i;
            while (i < code_end && (is_ident_char(text[i]) || text[i] == '.')) i++;
            apply_rich_color(s, i, g_theme.number, 0);
            continue;
        }
        /* 标识符 */
        if (is_ident_char(c)) {
            int s = i;
            while (i < code_end && is_ident_char(text[i])) i++;
            int e = i;
            char word[64];
            size_t wl = (size_t)(e - s);
            if (wl >= sizeof(word)) { i = e; continue; }
            memcpy(word, text + s, wl); word[wl] = '\0';
            int kc = keyword_class(word);

            if (kc == 2) {                     /* 控制关键字：紫 */
                apply_rich_color(s, e, g_theme.control, 0);
                prev_struct = 0;
                continue;
            }
            if (kc == 1) {                     /* 类型关键字：蓝 */
                apply_rich_color(s, e, g_theme.keyword, 0);
                prev_struct = (strcmp(word, "struct") == 0 ||
                               strcmp(word, "enum") == 0 ||
                               strcmp(word, "union") == 0);
                continue;
            }

            /* 非关键字：是否为函数名（后跟 '('，允许空白） */
            int j = e;
            while (j < code_end && (text[j] == ' ' || text[j] == '\t')) j++;
            if (j < code_end && text[j] == '(') {
                apply_rich_color(s, e, g_theme.func, 1);   /* 函数名：黄加粗 */
                if (first_func) {
                    /* 定义处参数列表：类型=蓝，形参名=浅蓝加粗 */
                    int depth = 1;
                    int k = j + 1;
                    while (k < code_end && depth > 0) {
                        if (text[k] == '(') depth++;
                        else if (text[k] == ')') { depth--; if (depth == 0) break; }
                        else if (depth == 1 && is_ident_char(text[k])) {
                            int ps = k;
                            while (k < code_end && is_ident_char(text[k])) k++;
                            int pe = k;
                            char w2[64];
                            size_t l2 = (size_t)(pe - ps);
                            if (l2 < sizeof(w2)) {
                                memcpy(w2, text + ps, l2); w2[l2] = '\0';
                                int kc2 = keyword_class(w2);
                                if (kc2 == 2) apply_rich_color(ps, pe, g_theme.control, 0);
                                else if (kc2 == 1) apply_rich_color(ps, pe, g_theme.keyword, 0);
                                else apply_rich_color(ps, pe, g_theme.param, 1);
                            }
                            continue;
                        }
                        k++;
                    }
                    first_func = 0;
                    i = k + 1;
                    continue;
                }
                first_func = 0;
                continue;
            }

            /* 普通标识符：struct 名用 type 色，变量用 param 浅蓝 */
            if (prev_struct) { apply_rich_color(s, e, g_theme.type, 0); prev_struct = 0; }
            else             { apply_rich_color(s, e, g_theme.param, 0); }
            continue;
        }
        i++;
    }
    /* 取消残留选区 */
    SendMessage(g_hDetail, EM_SETSEL, (WPARAM)-1, 0);
}

/* ============ H. 模糊查找与列表 ============ */

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

/* 模糊子序列匹配：kw 的每个字符按顺序出现在 text 中（均已小写） */
static int fuzzy_subseq(const char *kw, const char *text) {
    while (*kw) {
        text = strchr(text, *kw);
        if (!text) return 0;
        text++;
        kw++;
    }
    return 1;
}

/* 单个关键词的匹配分：0=不匹配；子串 > 模糊；名称 > 描述 > 分类。
   注意：模糊子序列仅对 ASCII 名称有效——描述/分类是 GBK 中文，
   逐字节模糊匹配会把汉字第二字节（可能等于 a-z）误判为命中，
   导致中文描述被大量误匹配，因此描述/分类只做精确子串匹配。 */
static int match_score(const char *kw, const char *n, const char *d, const char *s) {
    if (strstr(n, kw)) return 100;
    if (strstr(d, kw)) return 80;
    if (strstr(s, kw)) return 70;
    if (fuzzy_subseq(kw, n)) return 50;
    return 0;
}

/* 截断 GBK 文本到指定字节数（避免截断半个汉字），超出加 "..." */
static void trunc_gbk(char *out, size_t outsz, const char *text, int maxbytes) {
    size_t l = strlen(text);
    if (l <= (size_t)maxbytes) {
        snprintf(out, outsz, "%s", text);
        return;
    }
    size_t n = (size_t)maxbytes;
    if (n > 0 && n < l && (unsigned char)text[n-1] >= 0x81 && (unsigned char)text[n-1] <= 0xFE)
        n--;
    memcpy(out, text, n);
    out[n] = '\0';
    snprintf(out + n, outsz - n, "...");
}

static int cmp_score(const void *a, const void *b) {
    const MatchItem *x = (const MatchItem*)a;
    const MatchItem *y = (const MatchItem*)b;
    if (x->score != y->score) return y->score - x->score;
    return x->idx - y->idx;
}
static int cmp_name(const void *a, const void *b) {
    const MatchItem *x = (const MatchItem*)a;
    const MatchItem *y = (const MatchItem*)b;
    return strcmp(g_funcs[x->idx].name, g_funcs[y->idx].name);
}
static int cmp_section(const void *a, const void *b) {
    const MatchItem *x = (const MatchItem*)a;
    const MatchItem *y = (const MatchItem*)b;
    int c = strcmp(g_funcs[x->idx].section, g_funcs[y->idx].section);
    if (c) return c;
    return strcmp(g_funcs[x->idx].name, g_funcs[y->idx].name);
}

static void update_sort_buttons(void) {
    SetWindowTextA(g_hBtnSortName, (g_sortMode == 1) ? "按名称排序 √" : "按名称排序");
    SetWindowTextA(g_hBtnSortCat,  (g_sortMode == 2) ? "按分类排序 √" : "按分类排序");
}

static void show_detail(int func_index);   /* 前置声明 */

static void refresh_list(void) {
    char kw[128], kw_low[128];
    GetWindowTextA(g_hSearch, kw, sizeof(kw));
    int i = 0;
    while (kw[i] && i < (int)sizeof(kw_low) - 1) {
        kw_low[i] = (char)tolower((unsigned char)kw[i]);
        i++;
    }
    kw_low[i] = '\0';

    /* 空格分隔的多关键词（tmp 为函数级变量，保证 terms 指针有效） */
    char tmp[128];
    char *terms[16];
    int nterm = 0;
    strncpy(tmp, kw_low, sizeof(tmp) - 1); tmp[sizeof(tmp)-1] = '\0';
    char *tok = strtok(tmp, " ");
    while (tok && nterm < 16) {
        if (*tok) terms[nterm++] = tok;
        tok = strtok(NULL, " ");
    }

    /* 当前分类（CB_GETITEMDATA 存原始分类名） */
    const char *cat_name = "";
    int cat_sel = (int)SendMessageA(g_hCategory, CB_GETCURSEL, 0, 0);
    if (cat_sel > 0) {
        const char *cp = (const char*)SendMessageA(g_hCategory, CB_GETITEMDATA, (WPARAM)cat_sel, 0);
        if (cp) cat_name = cp;
    }

    /* 筛选 + 收集匹配项（带分数） */
    int shown = 0;
    for (i = 0; i < FUNC_COUNT; i++) {
        const FuncInfo *f = &g_funcs[i];
        if (cat_name[0] && strcmp(f->section, cat_name) != 0) continue;
        int score = 0, all = 1;
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
            for (int t = 0; t < nterm; t++) {
                int sc = match_score(terms[t], n, d, s);
                if (sc == 0) { all = 0; break; }
                score += sc;
            }
            if (!all) continue;
        }
        if (shown >= g_order_cap) {
            int nc = g_order_cap ? g_order_cap * 2 : 256;
            MatchItem *np = (MatchItem*)realloc(g_order, (size_t)nc * sizeof(MatchItem));
            if (!np) break;
            g_order = np;
            g_order_cap = nc;
        }
        g_order[shown].idx = i;
        g_order[shown].score = score;
        shown++;
    }

    /* 排序：有搜索词按匹配分，否则按当前模式 */
    if (nterm > 0) {
        qsort(g_order, (size_t)shown, sizeof(MatchItem), cmp_score);
    } else if (g_sortMode == 1) {
        qsort(g_order, (size_t)shown, sizeof(MatchItem), cmp_name);
    } else if (g_sortMode == 2) {
        qsort(g_order, (size_t)shown, sizeof(MatchItem), cmp_section);
    }

    ListView_DeleteAllItems(g_hList);
    for (int k = 0; k < shown; k++) {
        const FuncInfo *f = &g_funcs[g_order[k].idx];
        LVITEMA item;
        memset(&item, 0, sizeof(item));
        item.mask = LVIF_TEXT | LVIF_PARAM;
        item.iItem = k;
        item.iSubItem = 0;
        item.pszText = (LPSTR)f->name;
        item.lParam = g_order[k].idx;
        int row = (int)ListView_InsertItem(g_hList, &item);
        ListView_SetItemText(g_hList, row, 1, (LPSTR)f->section);
        char dshort[64];
        trunc_gbk(dshort, sizeof(dshort), f->desc, 18);   /* 功能列精简 */
        ListView_SetItemText(g_hList, row, 2, dshort);
    }

    char cnt[192];
    snprintf(cnt, sizeof(cnt), "显示 %d / %d 个函数%s", shown, FUNC_COUNT,
             nterm > 0 ? "（模糊匹配）" : "");
    SetWindowTextA(g_hCountLbl, cnt);
    SetWindowTextA(g_hStatus, cnt);

    /* 自动选中第一项并显示详情 */
    if (shown > 0) {
        ListView_SetItemState(g_hList, 0, LVIS_SELECTED | LVIS_FOCUSED, LVIS_SELECTED | LVIS_FOCUSED);
        show_detail(g_order[0].idx);
    } else {
        SetWindowTextA(g_hDetail, "（没有匹配的函数，请尝试更换关键词或分类）");
    }
}

/* ============ I. 详情显示 ============ */

static void show_detail(int func_index) {
    const FuncInfo *f = &g_funcs[func_index];
    Loc decl = find_decl(f->name);
    Loc impl = find_impl(f->name);
    char *src = (impl.line > 0) ? extract_function_source(&impl) : NULL;
    char *doc = extract_doc_block(&decl);   /* 详细说明（@param/@return） */
    char fshort[96];
    trunc_gbk(fshort, sizeof(fshort), f->desc, 44);   /* 功能描述精简 */

    size_t need = 1024 + strlen(f->name) + strlen(f->section) + strlen(f->desc)
                + strlen(f->example) + (src ? strlen(src) : 128) + (doc ? strlen(doc) : 64);
    char *buf = (char*)malloc(need);
    if (!buf) { free(src); free(doc); return; }
    int len = snprintf(buf, need,
        "函数名 : %s\r\n"
        "分类   : %s\r\n"
        "功能   : %s\r\n"
        "示例   : %s\r\n"
        "声明位置: %s 第 %d 行\r\n"
        "实现位置: %s 第 %d 行\r\n"
        "（单击查看详情 · 双击或点[打开实现]跳转 VS Code）\r\n"
        "\r\n---------- 实现源码 ----------\r\n%s"
        "\r\n---------- 详细说明 ----------\r\n%s",
        f->name, f->section, fshort, f->example,
        decl.line > 0 ? g_docs[decl.doc].display : "-",
        decl.line,
        impl.line > 0 ? g_docs[impl.doc].display : "-",
        impl.line,
        src ? src : "(未能提取源码：请确认 utils.c / utils_gen.c 与 utils_gui.exe 在同一目录)",
        doc ? doc : "（无详细注释）");
    (void)len;
    SetWindowTextA(g_hDetail, buf);
    /* 语法高亮：源码区着色，介绍与详细说明为绿色 */
    {
        const char *m1 = "---------- 实现源码 ----------\r\n";
        const char *p1 = strstr(buf, m1);
        int cs = p1 ? (int)(p1 - buf) + (int)strlen(m1) : 0;
        const char *m2 = "---------- 详细说明 ----------\r\n";
        const char *p2 = strstr(buf, m2);
        int ce = p2 ? (int)(p2 - buf) : (int)strlen(buf);
        SendMessage(g_hDetail, WM_SETREDRAW, FALSE, 0);
        highlight_code(buf, cs, ce);
        SendMessage(g_hDetail, WM_SETREDRAW, TRUE, 0);
        InvalidateRect(g_hDetail, NULL, TRUE);
    }
    free(buf);
    free(src);
    free(doc);
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

/* ============ J. 控件创建 ============ */

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
    g_hBtnCopySrc = CreateWindowA("BUTTON", "复制实现源码", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
        434, 34, 108, 26, hwnd, (HMENU)IDC_COPY_SRC, g_hInst, NULL);

    /* 列表 */
    g_hList = CreateWindowA(WC_LISTVIEWA, "",
        WS_CHILD | WS_VISIBLE | WS_BORDER | LVS_REPORT | LVS_SINGLESEL | LVS_SHOWSELALWAYS,
        0, 0, 0, 0, hwnd, (HMENU)IDC_LIST, g_hInst, NULL);
    ListView_SetExtendedListViewStyle(g_hList,
        LVS_EX_FULLROWSELECT | LVS_EX_GRIDLINES | LVS_EX_DOUBLEBUFFER);
    LVCOLUMNA col;
    memset(&col, 0, sizeof(col));
    col.mask = LVCF_TEXT | LVCF_WIDTH;
    col.pszText = "函数名"; col.cx = 200; ListView_InsertColumn(g_hList, 0, &col);
    col.pszText = "分类";   col.cx = 130; ListView_InsertColumn(g_hList, 1, &col);
    col.pszText = "功能";   col.cx = 210; ListView_InsertColumn(g_hList, 2, &col);

    /* 详情（RichEdit，支持语法高亮，暗色背景） */
    g_hDetail = CreateWindowA("RichEdit20A", "",
        WS_CHILD | WS_VISIBLE | WS_BORDER | ES_MULTILINE | ES_READONLY |
        WS_VSCROLL | WS_HSCROLL | ES_AUTOVSCROLL,
        0, 0, 0, 0, hwnd, (HMENU)IDC_DETAIL, g_hInst, NULL);
    SendMessage(g_hDetail, EM_SETLIMITTEXT, 0x7FFFFFFF, 0);
    SendMessage(g_hDetail, EM_SETBKGNDCOLOR, 0, (LPARAM)g_theme.background);

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
    SendMessage(g_hBtnCopySrc,  WM_SETFONT, (WPARAM)g_hFont, TRUE);
    SendMessage(g_hCountLbl, WM_SETFONT, (WPARAM)g_hFont, TRUE);
    SendMessage(g_hStatus,   WM_SETFONT, (WPARAM)g_hFont, TRUE);
    SendMessage(g_hList,     WM_SETFONT, (WPARAM)g_hFont, TRUE);
    SendMessage(g_hDetail,   WM_SETFONT, (WPARAM)g_hCodeFont, TRUE);

    build_category_list();
    update_sort_buttons();
    refresh_list();
}

/* ============ K. 窗口过程 ============ */

static LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
    case WM_CREATE:
        g_hFont = CreateFontA(-17, 0, 0, 0, FW_BOLD, 0, 0, 0, DEFAULT_CHARSET,
            OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, NONANTIALIASED_QUALITY,
            DEFAULT_PITCH, "Microsoft YaHei");
        g_hCodeFont = CreateFontA(-16, 0, 0, 0, FW_BOLD, 0, 0, 0, DEFAULT_CHARSET,
            OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, NONANTIALIASED_QUALITY,
            FIXED_PITCH, "Courier New");
        create_controls(hwnd);
        return 0;

    case WM_SIZE: {
        int w = LOWORD(lParam), h = HIWORD(lParam);
        int topY = 64;
        int statusH = 24;
        int gap = 10;
        /* 详情宽度约占窗口 42%，限制在 [430, 800]，避免过大/过小 */
        int detailW = w * 42 / 100;
        if (detailW < 430) detailW = 430;
        if (detailW > 800) detailW = 800;
        int listW = w - detailW - gap * 3 - 4;
        if (listW < 320) {            /* 窗口过窄时保证列表最小宽 */
            listW = 320;
            detailW = w - listW - gap * 3 - 4;
            if (detailW < 400) detailW = 400;
        }
        MoveWindow(g_hList, 10, topY, listW, h - topY - statusH - 10, TRUE);
        MoveWindow(g_hDetail, 10 + listW + gap, topY, detailW, h - topY - statusH - 10, TRUE);
        MoveWindow(g_hStatus, 0, h - statusH, w, statusH, TRUE);
        /* 列表列自适应：前两列固定，功能列自动填满剩余宽度，避免全屏留白；
           窗口过窄时前两列按比例收缩，避免列总宽超出列表宽度 */ 
        int c0 = 200, c1 = 130, need = c0 + c1 + 120 + 22;
        if (listW < need) {                 /* 窄窗口按比例压缩前两列 */
            c0 = listW * 200 / need;
            c1 = listW * 130 / need;
            if (c0 < 90) c0 = 90;
            if (c1 < 70) c1 = 70;
        }
        ListView_SetColumnWidth(g_hList, 0, c0);
        ListView_SetColumnWidth(g_hList, 1, c1);
        int third = listW - c0 - c1 - 22;   /* 预留垂直滚动条与边距 */
        if (third < 80) third = 80;
        ListView_SetColumnWidth(g_hList, 2, third);
        return 0;
    }

    case WM_MOUSEMOVE: {
        /* 跟踪鼠标悬停行，用于列表高亮 */
        POINT sp = { (short)LOWORD(lParam), (short)HIWORD(lParam) };
        ClientToScreen(hwnd, &sp);
        RECT lr;
        GetWindowRect(g_hList, &lr);
        if (PtInRect(&lr, sp)) {
            POINT lp = sp;
            ScreenToClient(g_hList, &lp);
            LVHITTESTINFO hi;
            memset(&hi, 0, sizeof(hi));
            hi.pt = lp;
            int row = ListView_HitTest(g_hList, &hi);
            if (row != g_hoverRow) {
                g_hoverRow = row;
                InvalidateRect(g_hList, NULL, TRUE);
            }
        } else if (g_hoverRow != -1) {
            g_hoverRow = -1;
            InvalidateRect(g_hList, NULL, TRUE);
        }
        break;
    }

    case WM_CTLCOLORSTATIC: {
        HDC hdc = (HDC)wParam;
        SetBkColor(hdc, RGB(255, 255, 255));
        SetTextColor(hdc, RGB(30, 30, 30));
        return (LRESULT)GetStockObject(WHITE_BRUSH);
    }
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
        } else if (id == IDC_COPY_SRC && code == BN_CLICKED) {
            int idx = get_selected_func_index();
            if (idx >= 0) {
                Loc impl = find_impl(g_funcs[idx].name);
                if (impl.line > 0) {
                    char *src = extract_function_source(&impl);
                    if (src) { copy_to_clipboard(src); free(src); }
                }
            }
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
            } else if (nm->code == NM_CUSTOMDRAW) {
                /* 列表三态：普通条纹 / 悬停亮色 / 选中深色（失焦淡一点） */
                NMLVCUSTOMDRAW *lvd = (NMLVCUSTOMDRAW*)lParam;
                if (lvd->nmcd.dwDrawStage == CDDS_PREPAINT) return CDRF_NOTIFYITEMDRAW;
                if (lvd->nmcd.dwDrawStage == CDDS_ITEMPREPAINT) {
                    int row = (int)lvd->nmcd.dwItemSpec;
                    UINT st = lvd->nmcd.uItemState;
                    if (st & CDIS_SELECTED) {
                        if (st & CDIS_FOCUS) {   /* 选中且焦点：最深 */
                            lvd->clrText = RGB(255, 255, 255);
                            lvd->clrTextBk = RGB(0, 80, 160);
                        } else {                 /* 选中但失焦：淡一点 */
                            lvd->clrText = RGB(255, 255, 255);
                            lvd->clrTextBk = RGB(100, 150, 205);
                        }
                    } else if (row == g_hoverRow) {   /* 鼠标悬停：亮色 */
                        lvd->clrText = RGB(20, 20, 20);
                        lvd->clrTextBk = RGB(200, 226, 250);
                    } else {                         /* 普通：白底 / 加深灰底条纹 */
                        lvd->clrText = RGB(25, 25, 25);
                        lvd->clrTextBk = (row % 2 == 0) ? RGB(255, 255, 255) : RGB(219, 226, 235);
                    }
                    return CDRF_NEWFONT;
                }
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

/* ============ L. 入口 ============ */

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrev, LPSTR lpCmdLine, int nCmdShow) {
    (void)hPrev; (void)lpCmdLine;
    g_hInst = hInstance;

    INITCOMMONCONTROLSEX icc;
    icc.dwSize = sizeof(icc);
    icc.dwICC = ICC_LISTVIEW_CLASSES;
    InitCommonControlsEx(&icc);
    LoadLibraryA("riched20.dll");   /* 语法高亮用 RichEdit */

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

    /* 加载主题配色（exe 同目录 theme.ini，缺失则用默认 Dark+） */
    {
        char exe_path[MAX_PATH];
        GetModuleFileNameA(NULL, exe_path, MAX_PATH);
        char *slash = strrchr(exe_path, '\\');
        if (slash) *slash = '\0';
        char theme_path[MAX_PATH];
        join_path(theme_path, MAX_PATH, exe_path, "theme.ini");
        load_theme(theme_path);
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
        "UTILS 函数库 v2.1 · 图形化查找工具",
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
