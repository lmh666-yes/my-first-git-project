# -*- coding: utf-8 -*-
"""从桌面版题库 生成 手机版 index.html（题库数据内嵌，单文件离线可用）。

用法：python build_web.py
读取：../C刷题软件/题库.json + www/template.html
输出：www/index.html（浏览器直接打开） + android/app/src/main/assets/index.html（APK 用）
"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "C刷题软件", "题库.json")
TEMPLATE = os.path.join(HERE, "www", "template.html")
OUT = os.path.join(HERE, "www", "index.html")
APK_OUT = os.path.join(HERE, "android", "app", "src", "main", "assets", "index.html")


def main():
    if not os.path.exists(SRC):
        sys.exit("[错误] 未找到桌面版题库: " + SRC)
    if not os.path.exists(TEMPLATE):
        sys.exit("[错误] 未找到模板: " + TEMPLATE)
    bank = json.load(open(SRC, encoding="utf-8"))
    html = open(TEMPLATE, encoding="utf-8").read()
    js = "const BANK=" + json.dumps(bank, ensure_ascii=False) + ";"
    if "/*__BANK__*/" not in html:
        sys.exit("[错误] 模板缺少题库占位符 /*__BANK__*/")
    html = html.replace("/*__BANK__*/", js)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    os.makedirs(os.path.dirname(APK_OUT), exist_ok=True)
    with open(APK_OUT, "w", encoding="utf-8") as f:
        f.write(html)
    cnt = {}
    for it in bank:
        cnt[it["kind"]] = cnt.get(it["kind"], 0) + 1
    print("已生成:")
    print("  ", OUT)
    print("  ", APK_OUT)
    print("题库:", {k: v for k, v in cnt.items()}, "共", len(bank), "题")


if __name__ == "__main__":
    main()
