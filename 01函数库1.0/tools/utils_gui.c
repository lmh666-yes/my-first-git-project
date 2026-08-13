/* ============================================================
 *  utils_gui.c — UTILS 函数库 · 图形化查找工具（Windows GUI）
 * ------------------------------------------------------------
 *  功能：
 *   1. 左侧列表按分类展示全部函数，支持关键词搜索 + 分类筛选
 *   2. 右侧详情窗格显示功能说明、调用示例、源码位置及实现源码
 *   3. 双击函数 / 点击按钮，可直接跳转到 VS Code 中该函数的
 *      实现位置（utils.c 对应行）或头文件声明位置（utils.h 对应行）
 *
 *  编译运行（需要 MinGW gcc）：
 *    gcc -o utils_gui.exe utils_gui.c utils.c -mwindows -lcomctl32 -lshell32
 *    将 utils_gui.exe 放在 utils.h / utils.c 同目录下运行
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
#define IDC_SEARCH      1001
#define IDC_CATEGORY    1002
#define IDC_LIST        1003
#define IDC_DETAIL      1004
#define IDC_OPEN_IMPL   1005
#define IDC_OPEN_DECL   1006
#define IDC_COUNT_LBL   1007

static HINSTANCE g_hInst;
static HFONT     g_hFont;
static HWND      g_hSearch, g_hCategory, g_hList, g_hDetail;
static HWND      g_hBtnImpl, g_hBtnDecl, g_hCountLbl;

static char g_utils_h_path[MAX_PATH];
static char g_utils_c_path[MAX_PATH];
static char *g_utils_h_text = NULL;
static char *g_utils_c_text = NULL;

/* ---------- 文件读取与行号定位 ---------- */

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

    /* 依次尝试：exe 同目录、exe\..\lib（lib 与 tools 并列时）、当前目录 */
    char dirs[3][MAX_PATH];
    join_dir(dirs[0], MAX_PATH, exe_path, "");
    join_dir(dirs[1], MAX_PATH, exe_path, "\\..\\lib");
    GetCurrentDirectoryA(MAX_PATH, dirs[2]);

    for (int i = 0; i < 3; i++) {
        char h[MAX_PATH], c[MAX_PATH];
        join_path(h, MAX_PATH, dirs[i], "utils.h");
        join_path(c, MAX_PATH, dirs[i], "utils.c");
        if (file_exist(h) && file_exist(c)) {
            memcpy(g_utils_h_path, h, strlen(h) + 1);
            memcpy(g_utils_c_path, c, strlen(c) + 1);
            return;
        }
    }
    /* 兜底：exe 同目录 */
    join_path(g_utils_h_path, MAX_PATH, exe_path, "utils.h");
    join_path(g_utils_c_path, MAX_PATH, exe_path, "utils.c");
}

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

/* 在 utils.h 中查找声明行号（首个包含 "name(" 的行） */
static int find_decl_line(const char *name) {
    int line = 1;
    const char *p = g_utils_h_text;
    while (*p) {
        const char *nl = strchr(p, '\n');
        size_t len = nl ? (size_t)(nl - p) : strlen(p);
        char buf[512];
        size_t cl = len < sizeof(buf) - 1 ? len : sizeof(buf) - 1;
        memcpy(buf, p, cl); buf[cl] = '\0';
        if (line_has_call(buf, name)) return line;
        if (!nl) break;
        p = nl + 1;
        line++;
    }
    return 0;
}

/* 在 utils.c 中查找实现起始行号：包含 "name(" 且以 '{' 结尾的定义行 */
static int find_impl_line(const char *name) {
    int line = 1;
    const char *p = g_utils_c_text;
    while (*p) {
        const char *nl = strchr(p, '\n');
        size_t len = nl ? (size_t)(nl - p) : strlen(p);
        char buf[512];
        size_t cl = len < sizeof(buf) - 1 ? len : sizeof(buf) - 1;
        memcpy(buf, p, cl); buf[cl] = '\0';
        /* 去首尾空白 */
        char *b = buf;
        while (*b == ' ' || *b == '\t') b++;
        size_t bl = strlen(b);
        while (bl > 0 && (b[bl - 1] == ' ' || b[bl - 1] == '\t' || b[bl - 1] == '\r')) b[--bl] = '\0';
        if (bl > 0 && b[bl - 1] == '{' && line_has_call(b, name)) return line;
        if (!nl) break;
        p = nl + 1;
        line++;
    }
    return 0;
}

/* 提取 utils.c 中函数的完整实现源码（从定义行到花括号闭合） */
static char* extract_function_source(const char *name) {
    int start_line = find_impl_line(name);
    if (start_line == 0) return NULL;
    const char *pos = g_utils_c_text;
    int line = 1;
    while (line < start_line) {
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
    if (!started) return NULL;
    size_t len = (size_t)(end - pos);
    char *src = (char*)malloc(len + 1);
    if (!src) return NULL;
    memcpy(src, pos, len);
    src[len] = '\0';
    return src;
}

/* ---------- URL 编码与 VS Code 跳转 ---------- */

static void url_encode(const char *src, char *dst, int dst_size) {
    static const char hex[] = "0123456789ABCDEF";
    int j = 0;
    for (int i = 0; src[i] && j < dst_size - 4; i++) {
        unsigned char c = (unsigned char)src[i];
        if (isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~' ||
            c == '/' || c == ':') {
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

static void refresh_list(void) {
    char kw[128], kw_low[128];
    GetWindowTextA(g_hSearch, kw, sizeof(kw));
    int i = 0;
    while (kw[i] && i < (int)sizeof(kw_low) - 1) {
        kw_low[i] = (char)tolower((unsigned char)kw[i]);
        i++;
    }
    kw_low[i] = '\0';

    char cat_name[128] = "";
    int cat_sel = (int)SendMessageA(g_hCategory, CB_GETCURSEL, 0, 0);
    if (cat_sel > 0) SendMessageA(g_hCategory, CB_GETLBTEXT, cat_sel, (LPARAM)cat_name);

    ListView_DeleteAllItems(g_hList);
    int idx = 0, shown = 0;
    for (i = 0; i < FUNC_COUNT; i++) {
        const FuncInfo *f = &g_funcs[i];
        if (cat_name[0] && strcmp(f->section, cat_name) != 0) continue;
        if (kw_low[0]) {
            char n[128], d[128], s[128];
            int j = 0;
            while (f->name[j] && j < 127) { n[j] = (char)tolower((unsigned char)f->name[j]); j++; }
            n[j] = '\0';
            j = 0;
            while (f->desc[j] && j < 127) { d[j] = (char)tolower((unsigned char)f->desc[j]); j++; }
            d[j] = '\0';
            j = 0;
            while (f->section[j] && j < 127) { s[j] = (char)tolower((unsigned char)f->section[j]); j++; }
            s[j] = '\0';
            if (!strstr(n, kw_low) && !strstr(d, kw_low) && !strstr(s, kw_low)) continue;
        }
        LVITEMA item;
        memset(&item, 0, sizeof(item));
        item.mask = LVIF_TEXT | LVIF_PARAM;
        item.iItem = idx;
        item.iSubItem = 0;
        item.pszText = (LPSTR)f->name;
        item.lParam = i;
        int row = (int)ListView_InsertItem(g_hList, &item);
        ListView_SetItemText(g_hList, row, 1, (LPSTR)f->section);
        ListView_SetItemText(g_hList, row, 2, (LPSTR)f->desc);
        idx++;
        shown++;
    }
    char cnt[128];
    snprintf(cnt, sizeof(cnt), "共 %d / %d 个函数", shown, FUNC_COUNT);
    SetWindowTextA(g_hCountLbl, cnt);
}

static void show_detail(int func_index) {
    const FuncInfo *f = &g_funcs[func_index];
    char buf[12000];
    int decl_line = find_decl_line(f->name);
    int impl_line = find_impl_line(f->name);
    char *src = extract_function_source(f->name);

    int len = snprintf(buf, sizeof(buf),
        "函数名 : %s\r\n"
        "分类   : %s\r\n"
        "功能   : %s\r\n"
        "示例   : %s\r\n"
        "声明位置: utils.h 第 %d 行\r\n"
        "实现位置: utils.c 第 %d 行\r\n"
        "（双击左侧函数 或 点击[打开实现] 可跳转到 VS Code 对应行）\r\n"
        "\r\n---------- 实现源码 ----------\r\n%s",
        f->name, f->section, f->desc, f->example,
        decl_line, impl_line,
        src ? src : "(未能提取源码)");
    (void)len;
    SetWindowTextA(g_hDetail, buf);
    free(src);
}

/* ---------- 窗口过程 ---------- */

static LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
    case WM_CREATE: {
        g_hFont = CreateFontA(-16, 0, 0, 0, FW_NORMAL, 0, 0, 0, DEFAULT_CHARSET,
            OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY,
            DEFAULT_PITCH, "Microsoft YaHei");

        CreateWindowA("STATIC", "搜索:", WS_CHILD | WS_VISIBLE, 10, 8, 46, 24,
            hwnd, NULL, g_hInst, NULL);
        g_hSearch = CreateWindowA("EDIT", "", WS_CHILD | WS_VISIBLE | WS_BORDER | ES_AUTOHSCROLL,
            58, 6, 200, 24, hwnd, (HMENU)IDC_SEARCH, g_hInst, NULL);

        CreateWindowA("STATIC", "分类:", WS_CHILD | WS_VISIBLE, 268, 8, 40, 24,
            hwnd, NULL, g_hInst, NULL);
        g_hCategory = CreateWindowA("COMBOBOX", "",
            WS_CHILD | WS_VISIBLE | WS_BORDER | CBS_DROPDOWNLIST | WS_VSCROLL,
            310, 6, 180, 320, hwnd, (HMENU)IDC_CATEGORY, g_hInst, NULL);
        SendMessageA(g_hCategory, CB_ADDSTRING, 0, (LPARAM)"全部");
        const char *last = "";
        for (int i = 0; i < FUNC_COUNT; i++) {
            if (strcmp(g_funcs[i].section, last) != 0) {
                last = g_funcs[i].section;
                SendMessageA(g_hCategory, CB_ADDSTRING, 0, (LPARAM)last);
            }
        }
        SendMessageA(g_hCategory, CB_SETCURSEL, 0, 0);

        g_hBtnImpl = CreateWindowA("BUTTON", "打开实现", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
            500, 6, 100, 26, hwnd, (HMENU)IDC_OPEN_IMPL, g_hInst, NULL);
        g_hBtnDecl = CreateWindowA("BUTTON", "打开声明", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
            608, 6, 100, 26, hwnd, (HMENU)IDC_OPEN_DECL, g_hInst, NULL);
        g_hCountLbl = CreateWindowA("STATIC", "", WS_CHILD | WS_VISIBLE,
            716, 8, 260, 24, hwnd, NULL, g_hInst, NULL);

        g_hList = CreateWindowA(WC_LISTVIEWA, "",
            WS_CHILD | WS_VISIBLE | WS_BORDER | LVS_REPORT | LVS_SINGLESEL | LVS_SHOWSELALWAYS,
            0, 0, 0, 0, hwnd, (HMENU)IDC_LIST, g_hInst, NULL);
        ListView_SetExtendedListViewStyle(g_hList, LVS_EX_FULLROWSELECT | LVS_EX_GRIDLINES | LVS_EX_DOUBLEBUFFER);
        LVCOLUMNA col;
        memset(&col, 0, sizeof(col));
        col.mask = LVCF_TEXT | LVCF_WIDTH;
        col.pszText = "函数名"; col.cx = 200; ListView_InsertColumn(g_hList, 0, &col);
        col.pszText = "分类";   col.cx = 130; ListView_InsertColumn(g_hList, 1, &col);
        col.pszText = "功能";   col.cx = 360; ListView_InsertColumn(g_hList, 2, &col);

        g_hDetail = CreateWindowA("EDIT", "",
            WS_CHILD | WS_VISIBLE | WS_BORDER | ES_MULTILINE | ES_READONLY |
            WS_VSCROLL | WS_HSCROLL | ES_AUTOVSCROLL,
            0, 0, 0, 0, hwnd, (HMENU)IDC_DETAIL, g_hInst, NULL);

        SendMessage(g_hSearch,   WM_SETFONT, (WPARAM)g_hFont, TRUE);
        SendMessage(g_hCategory, WM_SETFONT, (WPARAM)g_hFont, TRUE);
        SendMessage(g_hBtnImpl,  WM_SETFONT, (WPARAM)g_hFont, TRUE);
        SendMessage(g_hBtnDecl,  WM_SETFONT, (WPARAM)g_hFont, TRUE);
        SendMessage(g_hCountLbl, WM_SETFONT, (WPARAM)g_hFont, TRUE);
        SendMessage(g_hList,     WM_SETFONT, (WPARAM)g_hFont, TRUE);
        SendMessage(g_hDetail,   WM_SETFONT, (WPARAM)g_hFont, TRUE);

        refresh_list();
        ListView_SetItemState(g_hList, 0, LVIS_SELECTED | LVIS_FOCUSED, LVIS_SELECTED | LVIS_FOCUSED);
        return 0;
    }

    case WM_SIZE: {
        int w = LOWORD(lParam), h = HIWORD(lParam);
        int topH = 38;
        int detailW = 430;
        int listW = w - detailW - 25;
        if (listW < 300) listW = 300;
        MoveWindow(g_hList, 10, topH, listW, h - topH - 10, TRUE);
        MoveWindow(g_hDetail, 10 + listW + 10, topH, w - listW - 25, h - topH - 10, TRUE);
        return 0;
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
                int line = find_impl_line(g_funcs[idx].name);
                if (line > 0) open_in_vscode(g_utils_c_path, line);
                else          open_in_vscode(g_utils_h_path, find_decl_line(g_funcs[idx].name));
            }
        } else if (id == IDC_OPEN_DECL && code == BN_CLICKED) {
            int idx = get_selected_func_index();
            if (idx >= 0) {
                int line = find_decl_line(g_funcs[idx].name);
                if (line > 0) open_in_vscode(g_utils_h_path, line);
                else          open_in_vscode(g_utils_c_path, find_impl_line(g_funcs[idx].name));
            }
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
                    int line = find_impl_line(g_funcs[idx].name);
                    if (line > 0) open_in_vscode(g_utils_c_path, line);
                    else          open_in_vscode(g_utils_h_path, find_decl_line(g_funcs[idx].name));
                }
            }
        }
        return 0;
    }

    case WM_DESTROY:
        if (g_hFont) DeleteObject(g_hFont);
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
    g_utils_h_text = read_text_file(g_utils_h_path);
    g_utils_c_text = read_text_file(g_utils_c_path);
    if (!g_utils_h_text || !g_utils_c_text) {
        MessageBoxA(NULL,
            "未找到 utils.h / utils.c！\n请将 utils_gui.exe 放在与 utils.h、utils.c 相同的目录下运行。",
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
        "UTILS 函数库 · 图形化查找工具",
        WS_OVERLAPPEDWINDOW | WS_CLIPCHILDREN,
        CW_USEDEFAULT, CW_USEDEFAULT, 1080, 680,
        NULL, NULL, hInstance, NULL);
    if (!hwnd) return 1;
    ShowWindow(hwnd, nCmdShow);
    UpdateWindow(hwnd);

    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    free(g_utils_h_text);
    free(g_utils_c_text);
    return (int)msg.wParam;
}
