# -*- coding: utf-8 -*-
"""C刷题软件 · 崩溃测试
覆盖：题库损坏JSON / 空题库 / 缺字段题目 / progress损坏 / 题库缺失 / 极端题干 / 笔记损坏
用法：python test_crash.py
"""
import sys, io, os, json, shutil, faulthandler, tkinter as tk
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
faulthandler.dump_traceback_later(120, exit=True)

import importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("bs", os.path.join(HERE, "刷题软件.py"))
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)

BANK = os.path.join(HERE, "题库.json")
PROG = os.path.join(HERE, "progress.json")
BAK_BANK = os.path.join(HERE, "题库.json.bak")
BAK_PROG = os.path.join(HERE, "progress.json.bak")

PASS = 0
FAIL = 0

def ok(name, cond, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {extra}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {extra}")

_msgs = []
bs.messagebox.showinfo = lambda t, m: _msgs.append((t, m))
bs.messagebox.showerror = lambda t, m: _msgs.append((t, m))
bs.messagebox.askyesno = lambda t, m: True

def write_bank(data):
    with open(BANK, "w", encoding="utf-8") as f:
        f.write(data)

def make_app(root):
    try:
        app = bs.App(root)
        root.update()
        return app, None
    except Exception as e:
        return None, e

def test_normal():
    print("— 场景1: 正常题库 —")
    write_bank(open(BAK_BANK, encoding="utf-8").read())
    root = tk.Tk()
    root.geometry("1180x720")
    app, err = make_app(root)
    ok("正常题库启动不崩溃", err is None, str(err) if err else "")
    ok("题库130题", app is not None and len(app.bank) == 130,
       str(len(app.bank)) if app else "N/A")
    root.destroy()

def test_broken_json():
    print("— 场景2: 题库为损坏JSON —")
    write_bank('{"bad": json 截断!!!')
    root = tk.Tk()
    root.geometry("1180x720")
    app, err = make_app(root)
    ok("损坏JSON不崩溃(降级为空)", err is None, str(err) if err else "")
    ok("给出错误提示", any("题库" in t for t, _ in _msgs))
    root.destroy()

def test_empty_list():
    print("— 场景3: 空题库 [] —")
    write_bank("[]")
    root = tk.Tk()
    root.geometry("1180x720")
    app, err = make_app(root)
    ok("空题库不崩溃", err is None, str(err) if err else "")
    root.destroy()

def test_not_list():
    print("— 场景4: 题库为对象/字符串 —")
    write_bank('{"a": 1}')
    root = tk.Tk()
    root.geometry("1180x720")
    app, err = make_app(root)
    ok("非列表题库不崩溃", err is None, str(err) if err else "")
    root.destroy()

def test_missing_fields():
    print("— 场景5: 题目缺字段 —")
    bad = [
        {"kind": "choice", "id": "x1", "num": 1, "stem": "缺options/answer的单选题"},
        {"kind": "judge", "id": "x2", "num": 2},                    # 完全缺字段
        {"kind": "qa", "id": "x3", "num": 3, "stem": "缺答案简答"},
        {"id": "x4"},                                               # 连kind都没有
        {},
    ]
    write_bank(json.dumps(bad, ensure_ascii=False))
    root = tk.Tk()
    root.geometry("1180x720")
    app, err = make_app(root)
    ok("缺字段题库启动不崩溃", err is None, str(err) if err else "")
    err = 0
    if app:
        for i in range(len(app.bank)):
            try:
                app.idx = i
                app.show_question()
                app.check()
                app.answer_judge("√")
                app.reveal_qa()
                app.mark_qa(True)
                app.toggle_fav()
                app.redo_q()
            except Exception as e:
                err += 1
                if err <= 3:
                    print("    ERR@", i, e)
    ok("缺字段题目作答不崩溃", err == 0, f"err={err}")
    root.destroy()

def test_huge_stem():
    print("— 场景6: 极端超长题干/选项 —")
    huge = "很长的题干" * 2000
    q = {"kind": "choice", "id": "big", "num": 1, "stem": huge,
         "options": [{"key": "A", "text": "选项" * 1000}], "answer": "A"}
    write_bank(json.dumps([q] * 50, ensure_ascii=False))
    root = tk.Tk()
    root.geometry("1180x720")
    app, err = make_app(root)
    ok("超长题干不崩溃", err is None, str(err) if err else "")
    err = 0
    if app:
        for i in range(50):
            try:
                app.idx = i
                app.show_question()
                app.check()
            except Exception as e:
                err += 1
    ok("超长题作答不崩溃", err == 0, f"err={err}")
    root.destroy()

def test_broken_progress():
    print("— 场景7: progress.json 损坏 —")
    write_bank(open(BAK_BANK, encoding="utf-8").read())
    with open(PROG, "w", encoding="utf-8") as f:
        f.write("{ not valid !!")
    root = tk.Tk()
    root.geometry("1180x720")
    app, err = make_app(root)
    ok("损坏progress不崩溃(降级空)", err is None, str(err) if err else "")
    ok("进度被重置为空", app is not None and app.progress == {})
    root.destroy()

def test_missing_bank():
    print("— 场景8: 题库文件缺失 —")
    if os.path.exists(BANK):
        os.remove(BANK)
    root = tk.Tk()
    root.geometry("1180x720")
    app, err = make_app(root)
    ok("题库缺失不崩溃", err is None, str(err) if err else "")
    ok("给出错误提示", any("题库" in t for t, _ in _msgs))
    root.destroy()

def restore():
    if os.path.exists(BAK_BANK):
        shutil.copy(BAK_BANK, BANK)
    if os.path.exists(BAK_PROG):
        shutil.copy(BAK_PROG, PROG)
    for p in (BAK_BANK, BAK_PROG):
        if os.path.exists(p):
            os.remove(p)

def main():
    # 备份现场
    if os.path.exists(BANK):
        shutil.copy(BANK, BAK_BANK)
    if os.path.exists(PROG):
        shutil.copy(PROG, BAK_PROG)
    try:
        test_normal()
        test_broken_json()
        test_empty_list()
        test_not_list()
        test_missing_fields()
        test_huge_stem()
        test_broken_progress()
        test_missing_bank()
    finally:
        restore()
    print(f"\n===== 崩溃测试结果: PASS={PASS} FAIL={FAIL} =====")
    sys.exit(1 if FAIL else 0)

if __name__ == "__main__":
    main()
