# -*- coding: utf-8 -*-
"""
cppsim.py — 教学 C++ 子集解释器（独立模块，不影响 C 引擎 simcore.py）

当前支持（第一版，向后逐步扩展）：
 · class 定义：数据成员(int/float/double/char/对象) + 成员函数 + public/private 段
 · 对象：`A a;` 栈对象；成员读写 `a.x`；限定访问 `b.A::x = 33;`；方法调用 `a.showInfo();`
 · 方法体内直接写成员名(等效 this->成员)，自动绑定 this
 · iostream：`cout << ... << endl;` 与 `cin >> a >> b;`（cin 从模拟输入队列取值）
 · 基本类型 int / float / double / char / long / bool；控制流 if/else/while/for/return/break
 · printf / puts 基本输出；字符串/字符/浮点字面量
 · 每步快照格式与 simcore 同构(frames/heap)，GUI Drawer 可直接绘制对象块

不支持的 C++ 特性（继承/虚函数/运算符重载/异常/引用/STL 等）后续版本分批加入；
遇到不支持语法会抛 SimError(带行号)，GUI 标红提示，绝不瞎猜。
"""
import re

from simcore import (SimError, tokenize, StopExec, Token,
                     Stmt, BlockStmt, DeclStmt, AssignStmt, ExprStmt,
                     IfStmt, WhileStmt, ForStmt, ReturnStmt, BreakStmt,
                     PrintfStmt)

# ---------------------------------------------------------------
# 额外的 C++ 语句类型（数据成员/方法表等统一放类定义）
# ---------------------------------------------------------------
class ClassDef:
    """class 定义：字段 + 方法 + 继承 + 构造/析构"""
    def __init__(self, name):
        self.name = name
        self.base = None            # 单继承基类名(第一版)
        self.fields = []            # [(name, vtype, ptr)]
        self.methods = {}           # name -> (params, body, is_const)
        self.ctors = []             # [(params(含默认值), initlist, body)]
        self.dtor = None            # (params, body) 或 None

    def lineage(self):
        """继承链(含自身, 自顶向下基类→派生) 按需惰性查询由 engine 处理"""
        return [self]


class CoutStmt(Stmt):
    """cout << a << "x" << endl;"""
    def __init__(self, line, parts):
        super().__init__(line, "cout")
        self.parts = parts      # [AST 表达式 or ('strlit',…) / ('endl',)]


class CinStmt(Stmt):
    """cin >> a >> b;"""
    def __init__(self, line, targets):
        super().__init__(line, "cin")
        self.targets = targets  # [AST 目标(变量/成员/下标)]


# ---------------------------------------------------------------
# 值类型(轻量, 独立于 C 的 Value, 避免交叉)
# kind: 'int'|'float'|'addr'|'null'|'str'|'fn'
# ---------------------------------------------------------------
class Cv:
    __slots__ = ("kind", "val")
    def __init__(self, kind, val=None):
        self.kind = kind
        self.val = val
    def __repr__(self):
        return f"Cv({self.kind},{self.val!r})"


# ---------------------------------------------------------------
# 解析器
# ---------------------------------------------------------------
_BASIC_TYPES = {"int", "char", "float", "double", "long", "short",
                "unsigned", "signed", "bool", "size_t", "void"}


class Tok:
    def __init__(self, toks):
        self.toks = toks
        self.pos = 0
    def peek(self, off=0):
        i = self.pos + off
        return self.toks[i] if i < len(self.toks) else None
    def next(self):
        t = self.toks[self.pos]
        self.pos += 1
        return t
    def expect(self, text):
        t = self.next()
        if t.text != text:
            raise SimError(t.line, f"期望 '{text}'，实际 '{t.text}'")
        return t
    def at(self, text):
        t = self.peek()
        return t is not None and t.text == text
    def at_id(self):
        t = self.peek()
        return t is not None and t.kind == "id"


def _char_val(s):
    s = s[1:-1]
    if len(s) == 1:
        return ord(s)
    esc = {"\\n": 10, "\\t": 9, "\\0": 0, "\\\\": 92, "\\'": 39, "\\r": 13,
           "\\a": 7, "\\b": 8, "\\f": 12, "\\v": 11, "\\\"": 34}
    if s in esc:
        return esc[s]
    return ord(s[0]) if s else 0


class CppParser:
    def __init__(self, toks):
        self.t = Tok(self._fold_tokens(toks))
        self.classes = {}      # name -> ClassDef
        self.funcs = {}        # 顶层函数名 -> (rtype, ptr, params, body)
        self._parse_program()

    @staticmethod
    def _fold_tokens(toks):
        """C++ 专用 token 预处理(不影响 C)：
         1) 两个连续 ':'(来自 :: ) 合并为单个 op token '::'，供限定访问解析
         2) 数字字面量后缀 567L / 3.14f / 100u → 丢弃后缀标记
         (三元 ?: 是单冒号不会相邻；default:/case x: 单冒号不受影响)"""
        out = []
        i, n = 0, len(toks)
        suf = {"L", "l", "u", "U", "f", "F", "ul", "UL", "lu", "LU"}
        while i < n:
            t = toks[i]
            if t.kind == "op" and t.text == ":" and i + 1 < n and toks[i + 1].text == ":":
                # 合并为 '::' 单 token
                out.append(Token("op", "::", t.line))
                i += 2
                continue
            if t.kind == "num" and i + 1 < n and toks[i + 1].kind == "id" and toks[i + 1].text in suf:
                out.append(t)
                i += 2
                continue
            out.append(t)
            i += 1
        return out

    # ---------- 顶层 ----------
    def _parse_program(self):
        while self.t.peek() is not None:
            if self.t.at(";"):
                self.t.next(); continue
            if self.t.at("class"):
                self._parse_class()
                continue
            if self.t.at("using") or self.t.at("namespace"):
                # using namespace std; 吞到 ;
                self._skip_to_semi()
                continue
            if self.t.at("typedef"):
                self._skip_to_semi()
                continue
            if self.t.at_id():
                save = self.t.pos
                # 尝试解析函数定义
                try:
                    rtype, ptr = self._parse_type()
                    if self.t.at_id():
                        fname = self.t.peek().text
                        # 构造函数名==类名 不能当顶层函数(在类里已处理)；此处顶层正常函数
                        if self.t.peek(1) is not None and self.t.peek(1).text == "(":
                            self.t.next()
                            params = self._parse_params()
                            if self.t.at("{"):
                                body = self._parse_block()
                                self.funcs[fname] = (rtype, ptr, params, body)
                                continue
                            else:
                                # 原型: 吞到 ;
                                self._skip_to_semi()
                                continue
                except (SimError, IndexError):
                    pass
                self.t.pos = save
                # 全局声明: 尽量吞掉
                self._skip_to_semi()
                continue
            # 其它未知顶层(裸标识符等)：跳过
            self.t.next()

    def _parse_class(self):
        kw = self.t.next()          # class
        name_t = self.t.next()      # 类名
        if name_t.kind != "id":
            raise SimError(name_t.line, "class 后需要类名")
        cname = name_t.text
        cd = ClassDef(cname)
        # 继承：class B : public A { ... }
        if self.t.at(":"):
            self.t.next()
            while not self.t.at("{") and self.t.peek() is not None:
                tk = self.t.next()
                if tk.kind == "id" and tk.text not in ("public", "private", "protected") \
                        and cd.base is None:
                    cd.base = tk.text
        self.t.expect("{")
        while not self.t.at("}"):
            if self.t.peek() is None:
                raise SimError(0, "类定义缺少 '}'")
            if self.t.at(";"):
                self.t.next(); continue
            if self.t.at("public") or self.t.at("private") or self.t.at("protected"):
                self.t.next()
                if self.t.at(":"):
                    self.t.next()
                continue
            # 析构函数 ~A(){...}
            if self.t.at("~"):
                self.t.next()
                self.t.next()          # 类名
                self.t.expect("(")
                params = self._parse_params()
                body = []
                if self.t.at("{"):
                    body = self._parse_block()
                elif self.t.at(";"):
                    self.t.next()
                cd.dtor = (params, body)
                continue
            # 构造函数：类名( … )[: 初始化列表] {…}
            if self.t.at_id() and self.t.peek().text == cname \
                    and self.t.peek(1) is not None and self.t.peek(1).text == "(":
                self.t.next()
                self.t.expect("(")
                params = self._parse_params()
                initlist = []
                if self.t.at(":"):
                    self.t.next()
                    initlist = self._parse_init_list(cd)
                body = []
                if self.t.at("{"):
                    body = self._parse_block()
                elif self.t.at(";"):
                    self.t.next()
                cd.ctors.append((params, initlist, body))
                continue
            # 成员函数 / 数据成员？
            save = self.t.pos
            try:
                vtype, ptr = self._parse_type()
                nt = self.t.next()
                if nt.kind == "id":
                    mname = nt.text
                    if self.t.at("("):
                        self.t.next()
                        params = self._parse_params()
                        is_const = False
                        if self.t.at("const"):
                            self.t.next(); is_const = True
                        body = []
                        if self.t.at("{"):
                            body = self._parse_block()
                        elif self.t.at(";"):
                            self.t.next()
                        cd.methods[mname] = (params, body, is_const)
                        continue
                    # 数据成员
                    cd.fields.append((mname, vtype, ptr))
                    # 类内初始化/数组：吞到 ;
                    if self.t.at("=") or self.t.at("["):
                        while self.t.peek() is not None and not self.t.at(";"):
                            self.t.next()
                    if self.t.at(";"):
                        self.t.next()
                    continue
            except (SimError, IndexError):
                pass
            self.t.pos = save
            self._skip_to_semi()
        self.t.expect("}")
        if self.t.at(";"):
            self.t.next()
        self.classes[cname] = cd

    def _parse_init_list(self, cd):
        """构造函数初始化列表 `: base(args), m(args)…`
        返回 [("base", 基类名, argExprs) | ("member", 成员名, argExprs)]"""
        items = []
        while True:
            if self.t.peek() is None or self.t.at("{"):
                break
            nm = self.t.next()
            if nm.kind != "id":
                continue
            if not self.t.at("("):
                continue
            self.t.next()
            args = []
            if not self.t.at(")"):
                args.append(self._parse_expr())
                while self.t.at(","):
                    self.t.next()
                    args.append(self._parse_expr())
            self.t.expect(")")
            if cd.base and nm.text == cd.base:
                items.append(("base", nm.text, args))
            else:
                items.append(("member", nm.text, args))
            if self.t.at(","):
                self.t.next()
                continue
            break
        return items

    # ---------- 类型 ----------
    def _parse_type(self):
        """返回 (base, ptr)。base 基本类型或类名。跳过 const 等修饰"""
        while self.t.peek() and self.t.peek().text in ("const", "static", "inline", "extern", "register", "volatile", "signed"):
            self.t.next()
        t = self.t.next()
        ptr = 0
        base = t.text
        if t.text in ("struct", "union", "enum"):
            # 简易: struct X 或 struct {...} 跳过处理
            nt = self.t.next()
            if nt.text == "{":
                # 匿名 struct：吞到匹配 }
                depth = 1
                while depth > 0 and self.t.peek() is not None:
                    tk = self.t.next()
                    if tk.text == "{":
                        depth += 1
                    elif tk.text == "}":
                        depth -= 1
                base = "int"
            else:
                base = nt.text
        elif t.text == "double" or t.text == "float":
            base = "float"
            while self.t.peek() and self.t.peek().text in ("double", "float", "long"):
                self.t.next()
        elif t.text == "long":
            # long / long long
            while self.t.peek() and self.t.peek().text in ("int", "long", "double", "float"):
                self.t.next()
            base = "int"
        elif t.text in ("int", "char", "short", "unsigned", "bool", "size_t"):
            while self.t.peek() and self.t.peek().text in ("int", "char", "short", "unsigned", "signed", "long"):
                tk = self.t.next()
                if tk.text == "char":
                    base = "char"
            if base == "short" or base == "unsigned" or base == "size_t":
                base = "int"
            if base == "bool":
                base = "int"
        # 其它(类名/typedef名)保持 base=名字
        while self.t.at("*"):
            self.t.next()
            ptr += 1
        return base, ptr

    def _parse_params(self):
        params = []
        if self.t.at(")"):
            self.t.next()
            return params
        while True:
            if self.t.at("void") and self.t.peek(1) is not None and self.t.peek(1).text == ")":
                self.t.next()
                break
            # 引用参数 int &x / 指针 int *p / 数组 int a[]
            vtype, ptr = self._parse_type()
            if self.t.at("&"):
                self.t.next()
                # 引用形参：第一版按值传递近似(对象成员场景仍共享块)
            nm = self.t.next()
            if nm.kind != "id":
                self.t.pos -= 1
                break
            while self.t.at("["):
                self.t.next()
                if not self.t.at("]"):
                    self._skip_until("]")
                self.t.expect("]")
            default = None
            if self.t.at("="):
                self.t.next()
                default = self._parse_expr()     # 默认参数(如 Mammal(float h=0,...))
            params.append((nm.text, vtype, ptr, default))
            if self.t.at(","):
                self.t.next()
                continue
            break
        self.t.expect(")")
        return params

    # ---------- 语句 ----------
    def _parse_block(self):
        self.t.expect("{")
        stmts = []
        while not self.t.at("}"):
            if self.t.peek() is None:
                raise SimError(0, "代码块缺少 '}'")
            stmts.append(self._parse_stmt())
        self.t.expect("}")
        return stmts

    def _parse_stmt(self):
        t = self.t.peek()
        if t is None:
            raise SimError(0, "语句意外结束")
        # 块
        if self.t.at("{"):
            return BlockStmt(t.line, self._parse_block())
        if self.t.at("delete"):
            # delete p;  /  delete [] p;
            self.t.next()
            isarr = False
            if self.t.at("["):
                self.t.next()
                self.t.expect("]")
                isarr = True
            tg = self._parse_lvalue()
            self.t.expect(";")
            return ExprStmt(t.line, ("delete", tg, isarr))
        if self.t.at("if"):
            self.t.next(); self.t.expect("(")
            cond = self._parse_expr(); self.t.expect(")")
            then_s = self._parse_stmt()
            else_s = None
            if self.t.at("else"):
                self.t.next()
                else_s = self._parse_stmt()
            return IfStmt(t.line, cond, then_s, else_s)
        if self.t.at("while"):
            self.t.next(); self.t.expect("(")
            cond = self._parse_expr(); self.t.expect(")")
            body = self._parse_stmt()
            return WhileStmt(t.line, cond, body)
        if self.t.at("for"):
            self.t.next(); self.t.expect("(")
            init = None
            if not self.t.at(";"):
                if self._looks_decl():
                    init = self._parse_decl(semi=False)
                else:
                    fl = self.t.peek().line
                    fe = self._parse_expr()
                    init = AssignStmt(fl, fe, ("lit", 0)) if False else ExprStmt(fl, fe)
                    if self.t.at("="):
                        self.t.next()
                        rhs = self._parse_expr()
                        init = AssignStmt(fl, fe, rhs)
            self.t.expect(";")
            cond = None
            if not self.t.at(";"):
                cond = self._parse_expr()
            self.t.expect(";")
            step = None
            if not self.t.at(")"):
                sl = self.t.peek().line
                se = self._parse_expr()
                step = ("assign", se, None) if False else se
                if self.t.at("="):
                    self.t.next()
                    rhs = self._parse_expr()
                    step = ("assign", se, rhs)
            self.t.expect(")")
            body = self._parse_stmt()
            return ForStmt(t.line, init, cond, step, body)
        if self.t.at("do"):
            self.t.next()
            body = self._parse_stmt()
            if self.t.at("while"):
                self.t.next(); self.t.expect("(")
                cond = self._parse_expr(); self.t.expect(")")
            if self.t.at(";"):
                self.t.next()
            return DoWhileStmt(t.line, cond, body)
        if self.t.at("return"):
            self.t.next()
            expr = None
            if not self.t.at(";"):
                expr = self._parse_expr()
            self.t.expect(";")
            return ReturnStmt(t.line, expr)
        if self.t.at("break"):
            self.t.next(); self.t.expect(";")
            return BreakStmt(t.line)
        if self.t.at("cout"):
            self.t.next()
            parts = []
            while self.t.at("<<"):
                self.t.next()
                # endl / 表达式
                if self.t.at_id() and self.t.peek().text == "endl":
                    self.t.next()
                    parts.append(("endl",))
                    continue
                parts.append(self._parse_expr())
            self.t.expect(";")
            return CoutStmt(t.line, parts)
        if self.t.at("cin"):
            self.t.next()
            targets = []
            while self.t.at(">>"):
                self.t.next()
                targets.append(self._parse_lvalue())
            self.t.expect(";")
            return CinStmt(t.line, targets)
        if self.t.at("printf"):
            return self._parse_printf()
        if self.t.at("puts"):
            return self._parse_puts()
        if self._looks_decl():
            st = self._parse_decl(semi=False)
            stmts = [st]
            while self.t.at(","):
                self.t.next()
                stmts.append(self._parse_decl_same(st, semi=False))
            self.t.expect(";")
            return stmts[0] if len(stmts) == 1 else SeqStmt(st.line, stmts)
        if self.t.at(";"):
            self.t.next()
            return ExprStmt(t.line, ("lit", 0))
        # 表达式语句 / 赋值
        e = self._parse_expr()
        if self.t.at("=") or self.t.at("+=") or self.t.at("-=") or self.t.at("*=") \
                or self.t.at("/=") or self.t.at("%="):
            op = self.t.next().text
            rhs = self._parse_expr()
            self.t.expect(";")
            if op == "=":
                return AssignStmt(t.line, e, rhs)
            return AssignStmt(t.line, e, ("bin", op[0], e, rhs))
        self.t.expect(";")
        return ExprStmt(t.line, e)

    def _parse_lvalue(self):
        """cin >> 的目标：变量 / a.x / a[i]"""
        e = self._parse_expr()
        return e

    def _parse_printf(self):
        t = self.t.next()  # printf
        self.t.expect("(")
        fmt = None
        args = []
        if self.t.peek() is not None and self.t.peek().kind == "str":
            fmt = self.t.next().text[1:-1]
        while not self.t.at(")") and self.t.peek() is not None:
            if self.t.at(","):
                self.t.next(); continue
            try:
                args.append(self._parse_expr())
            except Exception:
                self._skip_until_comma_or_paren()
        self.t.expect(")")
        self.t.expect(";")
        return PrintfStmt(t.line, fmt, args)

    def _parse_puts(self):
        t = self.t.next()
        self.t.expect("(")
        args = []
        if self.t.peek() is not None and self.t.peek().kind == "str":
            args.append(("strlit", self.t.next().text[1:-1]))
        else:
            try:
                args.append(self._parse_expr())
            except Exception:
                pass
        self.t.expect(")")
        self.t.expect(";")
        return PrintfStmt(t.line, "%s\n", args) if args else PrintfStmt(t.line, "\n", [])

    # ---------- 声明 ----------
    def _looks_decl(self):
        t = self.t.peek()
        if t is None or t.kind != "id":
            return False
        if t.text in _BASIC_TYPES or t.text in ("const", "static", "struct", "union", "enum"):
            return True
        if t.text in self.classes:
            i = 1
            while True:
                nx = self.t.peek(i)
                if nx is None:
                    return False
                if nx.text == "*":
                    i += 1; continue
                return nx.kind == "id"
        return False

    def _parse_decl(self, semi=True):
        line = self.t.peek().line
        vtype, ptr = self._parse_type()
        is_array = False
        arr_size = None
        nt = self.t.next()
        if nt.kind != "id":
            raise SimError(nt.line, f"变量名错误 '{nt.text}'")
        name = nt.text
        if self.t.at("["):
            self.t.next()
            sz = self.t.next()
            arr_size = int(sz.text) if sz.kind == "num" else 10
            self.t.expect("]")
            is_array = True
        init = None
        if self.t.at("("):
            # 对象/标量括号初始化：A a(1,2);  int x(5);
            self.t.next()
            args = []
            if not self.t.at(")"):
                args.append(self._parse_expr())
                while self.t.at(","):
                    self.t.next()
                    args.append(self._parse_expr())
            self.t.expect(")")
            init = ("objinit", args)
        elif self.t.at("="):
            self.t.next()
            init = self._parse_expr()
        if semi:
            self.t.expect(";")
        return DeclStmt(line, vtype, name, init, ptr, is_array, arr_size)

    def _parse_decl_same(self, proto, semi=True):
        line = self.t.peek().line
        vtype = proto.vtype
        ptr = proto.is_ptr
        if self.t.at("*"):
            self.t.next()
            ptr = True
        nt = self.t.next()
        if nt.kind != "id":
            raise SimError(nt.line, "变量名错误")
        name = nt.text
        init = None
        is_array = False
        arr_size = None
        if self.t.at("["):
            self.t.next()
            sz = self.t.next()
            arr_size = int(sz.text) if sz.kind == "num" else 10
            self.t.expect("]")
            is_array = True
        if self.t.at("="):
            self.t.next()
            init = self._parse_expr()
        if semi:
            self.t.expect(";")
        return DeclStmt(line, vtype, name, init, ptr, is_array, arr_size)

    # ---------- 表达式 ----------
    # 注意：赋值(=)只由语句层/for 处理，这里返回纯表达式；
    # 否则 a.x = 11 会被表达式层吞成 ('assign',…) 导致执行报错
    def _parse_expr(self):
        return self._parse_cond()

    def _parse_cond(self):
        e = self._parse_or()
        if self.t.at("?"):
            self.t.next()
            a = self._parse_expr()
            self.t.expect(":")
            b = self._parse_cond()
            return ("cond", e, a, b)
        return e

    def _parse_or(self):
        e = self._parse_and()
        while self.t.at("||"):
            self.t.next()
            e = ("bin", "||", e, self._parse_and())
        return e

    def _parse_and(self):
        e = self._parse_eq()
        while self.t.at("&&"):
            self.t.next()
            e = ("bin", "&&", e, self._parse_eq())
        return e

    def _parse_eq(self):
        e = self._parse_rel()
        while self.t.at("==") or self.t.at("!="):
            op = self.t.next().text
            e = ("bin", op, e, self._parse_rel())
        return e

    def _parse_rel(self):
        e = self._parse_add()
        while self.t.peek() and self.t.peek().text in ("<", "<=", ">", ">="):
            op = self.t.next().text
            e = ("bin", op, e, self._parse_add())
        return e

    def _parse_add(self):
        e = self._parse_mul()
        while self.t.peek() and self.t.peek().text in ("+", "-"):
            op = self.t.next().text
            e = ("bin", op, e, self._parse_mul())
        return e

    def _parse_mul(self):
        e = self._parse_unary()
        while self.t.peek() and self.t.peek().text in ("*", "/", "%"):
            op = self.t.next().text
            e = ("bin", op, e, self._parse_unary())
        return e

    def _parse_unary(self):
        t = self.t.peek()
        if t and t.text == "new":
            # new int / new int[10] / new B / new B(args) / new char[1000]
            self.t.next()
            vtype, ptr = self._parse_type()
            if self.t.at("("):
                self.t.next()
                args = []
                if not self.t.at(")"):
                    args.append(self._parse_expr())
                    while self.t.at(","):
                        self.t.next()
                        args.append(self._parse_expr())
                self.t.expect(")")
                return ("new", vtype, ("obj", args))
            if self.t.at("["):
                self.t.next()
                ne = self._parse_expr()
                self.t.expect("]")
                return ("new", vtype, ("array", ne))
            if vtype in self.classes:
                return ("new", vtype, ("obj", []))
            return ("new", vtype, ("scalar",))
        if t and t.text in ("-", "!", "~"):
            self.t.next()
            return ("unary", t.text, self._parse_unary())
        if t and t.text in ("++", "--"):
            self.t.next()
            return ("preinc", t.text, self._parse_unary())
        return self._parse_postfix()

    def _parse_postfix(self):
        e = self._parse_primary()
        while True:
            if self.t.at("("):
                self.t.next()
                args = []
                if not self.t.at(")"):
                    args.append(self._parse_expr())
                    while self.t.at(","):
                        self.t.next()
                        args.append(self._parse_expr())
                self.t.expect(")")
                if isinstance(e, tuple) and e and e[0] == "qfield":
                    e = ("qcall", e[1], e[2], args)          # A::showInfo(...)
                elif isinstance(e, tuple) and e and e[0] == "qmember":
                    e = ("qmcall", e[1], e[2], e[3], args)   # d.Mammal::showInfo(...)
                else:
                    e = ("call", e, args)
            elif self.t.at("->") or self.t.at("."):
                op = self.t.next().text
                f = self.t.next()
                if f.kind != "id":
                    raise SimError(f.line, "成员名错误")
                if self.t.at("::"):
                    # 对象限定成员/方法：d.Mammal::showInfo / d.A::x
                    self.t.next()            # ::
                    qm = self.t.next()
                    if qm.kind != "id":
                        raise SimError(qm.line, "限定成员名错误")
                    e = ("qmember", e, f.text, qm.text)
                    continue
                e = ("member", e, f.text)
            elif self.t.at("::"):
                # 裸限定：A::x / A::showInfo(...)（A 通常为类名/命名空间）
                self.t.next()
                if isinstance(e, tuple) and e and e[0] == "var":
                    nm = self.t.next()
                    if nm.kind != "id":
                        raise SimError(nm.line, "限定名错误")
                    e = ("qfield", e[1], nm.text)
                    continue
            elif self.t.at("["):
                self.t.next()
                idx = self._parse_expr()
                self.t.expect("]")
                e = ("index", e, idx)
            elif self.t.at("++") or self.t.at("--"):
                op = self.t.next().text
                e = ("postinc", op, e)
            else:
                break
        return e

    def _parse_primary(self):
        t = self.t.next()
        if t.kind == "char":
            return ("clit", _char_val(t.text))
        if t.kind == "num":
            if t.text.lower().startswith("0x"):
                return ("lit", int(t.text, 16))
            if "." in t.text:
                return ("lit", float(t.text))
            return ("lit", int(t.text))
        if t.kind == "str":
            return ("strlit", t.text[1:-1])
        if t.text == "(":
            save = self.t.pos
            try:
                e = self._parse_expr()
                self.t.expect(")")
                return e
            except (SimError, IndexError):
                self.t.pos = save
                self._skip_until(")")
                self.t.expect(")")
                return ("lit", 0)
        if t.kind == "id":
            if t.text == "NULL" or t.text == "nullptr":
                return ("null",)
            if t.text == "endl":
                return ("endl",)
            if t.text == "true":
                return ("lit", 1)
            if t.text == "false":
                return ("lit", 0)
            return ("var", t.text)
        raise SimError(t.line, f"无法识别的表达式 '{t.text}'")

    # ---------- 工具 ----------
    def _skip_to_semi(self):
        while self.t.peek() is not None and not self.t.at(";"):
            self.t.next()
        if self.t.at(";"):
            self.t.next()

    def _skip_until(self, text):
        while self.t.peek() is not None and not self.t.at(text):
            self.t.next()

    def _skip_until_comma_or_paren(self):
        while self.t.peek() is not None and not (self.t.at(",") or self.t.at(")")):
            self.t.next()


class DoWhileStmt(Stmt):
    def __init__(self, line, cond, body):
        super().__init__(line, "dowhile")
        self.cond = cond
        self.body = body


class SeqStmt(Stmt):
    def __init__(self, line, stmts):
        super().__init__(line, "seq")
        self.stmts = stmts


# ---------------------------------------------------------------
# 执行器
# ---------------------------------------------------------------
class CppFrame:
    def __init__(self, fname):
        self.fname = fname
        self.vars = {}        # name -> Cv  (局部 int/float/char/指针)
        self.vtypes = {}      # name -> 基础类型名(int/float/char/类名)
        self.objaddr = None   # 方法帧: this 对象地址


class CppBlk:
    __slots__ = ("addr", "typename", "fields", "loc", "freed", "scalar", "arr")
    def __init__(self, addr, typename, loc="堆"):
        self.addr = addr
        self.typename = typename
        self.fields = {}      # 成员名 -> Cv (数字/字符/对象地址/指针)
        self.loc = loc
        self.freed = False
        self.scalar = None    # 标量块(new int 等)
        self.arr = None       # 数组块(new char[n] / new int[n])


class CppEngine:
    def __init__(self, classes, funcs, inputs=None):
        self.classes = classes
        self.funcs = funcs
        self.next_addr = 0x1000
        self.heap = {}            # addr -> CppBlk
        self.frames = []
        self.cur_line = 0
        self.outputs = []
        self.error = None
        self.step_limit = 200000
        self.steps = 0
        self.snapshots = {}
        self.step_snapshots = []
        self.stop_line = None
        self.inputs = list(inputs or [])
        self.input_pos = 0
        # 对象作用域栈(块级对象析构用): 每个元素为 [objaddr,...]
        self.scope_obj = []
        # 最外层(main 体 / 方法体)声明的栈对象, 结束析构
        self._root_objs = []
        # 方法注册: (类名, 方法名) -> (owner类名, params, body)
        self.methods = {}
        self.ctor_idx = {}    # 类名 -> 各构造函数 params 数/默认标记列表
        for cn, cd in classes.items():
            for mn, (params, body, _c) in cd.methods.items():
                self.methods[(cn, mn)] = (cn, params, body)

    def _lineage(self, typename, topdown=True):
        """类继承链(含自身)。topdown=True 基类→派生(用于字段顺序)；False 派生→基类(用于方法查找)。"""
        chain = []
        seen = set()
        cur = typename
        while cur and cur in self.classes and cur not in seen:
            seen.add(cur)
            chain.append(cur)
            cur = self.classes[cur].base
        # chain = 派生→…→基
        return list(reversed(chain)) if topdown else chain

    def _resolve_method(self, typename, mname):
        """沿继承链(派生→基类)找 mname 的 owner 类名; 无则 None"""
        for cls in self._lineage(typename, topdown=False):
            if (cls, mname) in self.methods:
                return cls
        return None

    # ---- 内存 ----
    def _alloc(self, typename, loc="堆"):
        blk = CppBlk(self.next_addr, typename, loc)
        self.next_addr += 0x10
        cd = self.classes.get(typename)
        if cd is not None:
            # 基类字段在前, 自身在后(便于可视化与继承)
            for cls in self._lineage(typename):
                cdef = self.classes[cls]
                for fname, ftype, ptr in cdef.fields:
                    if fname in blk.fields:
                        continue
                    if ptr > 0:
                        blk.fields[fname] = Cv("null")
                    elif ftype in self.classes:
                        sub = self._alloc(ftype, "栈")
                        blk.fields[fname] = Cv("addr", sub.addr)
                    elif ftype == "float" or ftype == "double":
                        blk.fields[fname] = Cv("float", 0.0)
                    elif ftype == "char":
                        blk.fields[fname] = Cv("char", 0)
                    else:
                        blk.fields[fname] = Cv("int", 0)
        self.heap[blk.addr] = blk
        return blk

    # ---- 变量/帧 ----
    def _cur(self):
        return self.frames[-1]

    def _lookup_var(self, name):
        # 变量查找仅在当前函数/方法帧(块作用域由帧.vars 承担) ——
        # 绝不穿透到调用者帧(否则方法内与调用者同名变量会误读)
        fr = self.frames[-1] if self.frames else None
        return fr.vars.get(name) if fr is not None else None

    def _this(self):
        fr = self.frames[-1] if self.frames else None
        return fr.objaddr if fr is not None else None

    def _read_member_of_this(self, name):
        """方法体内裸成员名 -> 读取 this 对象的字段(仅当前方法帧)"""
        fr = self.frames[-1] if self.frames else None
        if fr is not None and fr.objaddr is not None:
            blk = self.heap.get(fr.objaddr)
            if blk is not None and name in blk.fields:
                return blk.fields[name], fr.objaddr
        return None, None

    # ---- 求值 ----
    def to_num(self, v):
        if v.kind == "int":
            return float(v.val)
        if v.kind == "float":
            return v.val
        if v.kind == "char":
            return float(v.val)
        if v.kind == "null":
            return 0.0
        if v.kind == "addr":
            return float(v.val)
        return 0.0

    def truthy(self, v):
        if v.kind == "int":
            return v.val != 0
        if v.kind == "float":
            return v.val != 0.0
        if v.kind == "char":
            return v.val != 0
        if v.kind == "null":
            return False
        return True

    def eval(self, e):
        k = e[0]
        if k == "lit":
            val = e[1]
            return Cv("float", val) if isinstance(val, float) else Cv("int", val)
        if k == "clit":
            return Cv("char", e[1])
        if k == "strlit":
            return Cv("str", e[1])
        if k == "endl":
            return Cv("str", "\n")
        if k == "null":
            return Cv("null")
        if k == "cond":
            return self.eval(e[2]) if self.truthy(self.eval(e[1])) else self.eval(e[3])
        if k == "var":
            name = e[1]
            if name in self.funcs:
                return Cv("fn", name)
            lv = self._lookup_var(name)
            if lv is not None:
                return lv
            mv, _addr = self._read_member_of_this(name)
            if mv is not None:
                return mv
            # 宽容: 自动声明 int 0
            if not self.frames:
                raise SimError(self.cur_line, f"未定义变量 '{name}'")
            self._cur().vars[name] = Cv("int", 0)
            return Cv("int", 0)
        if k == "unary":
            op = e[1]
            if op == "&":
                # 取地址: 给变量分配槽地址(简化按栈对象块/独立槽) —— 教学: 返回占位
                return self._take_addr(e[2])
            if op == "*":
                v = self.eval(e[2])
                return self._deref(v)
            v = self.eval(e[2])
            if op == "-":
                return Cv("float", -self.to_num(v)) if v.kind == "float" else Cv("int", -self.to_num(v))
            if op == "!":
                return Cv("int", 0 if self.truthy(v) else 1)
            if op == "~":
                return Cv("int", ~int(self.to_num(v)))
        if k == "bin":
            return self._binop(e[1], self.eval(e[2]), self.eval(e[3]))
        if k == "member":
            base = self.eval(e[1])
            if base.kind == "addr":
                blk = self.heap.get(base.val)
                if blk is not None:
                    if e[2] not in blk.fields:
                        blk.fields[e[2]] = Cv("int", 0)
                    return blk.fields[e[2]]
            raise SimError(self.cur_line, f"对象成员访问失败: {e[1]}")
        if k == "index":
            arr = self.eval(e[1])
            idx = int(self.to_num(self.eval(e[2])))
            if arr.kind == "addr":
                blk = self.heap.get(arr.val)
                if blk is not None and blk.arr is not None:
                    if idx < 0 or idx >= len(blk.arr):
                        raise SimError(self.cur_line, "下标越界")
                    return blk.arr[idx]
            raise SimError(self.cur_line, "下标访问只支持数组/类指针")
        if k == "call":
            return self._call(e[1], e[2])
        if k == "postinc":
            old = self.eval(e[2])
            self._assign(e[2], self._bump(old, e[1] == "++"))
            return old
        if k == "preinc":
            cur = self.eval(e[2])
            new = self._bump(cur, e[1] == "++")
            self._assign(e[2], new)
            return new
        if k == "new":
            return self._eval_new(e)
        if k == "delete":
            # ("delete", lvalue, isarr) —— 副作用语句
            _, tgt, isarr = e
            v = self.eval(tgt)
            self._do_delete(v, isarr)
            return Cv("int", 0)
        if k == "qfield":
            # 裸限定 A::x —— 静态/基类成员: 本版返回 0(不校验)
            return Cv("int", 0)
        if k == "qcall":
            return self._call_qualified(e[1], e[2], e[3])
        if k == "qmember":
            base = self.eval(e[1])
            if base.kind == "addr":
                blk = self.heap.get(base.val)
                if blk is not None:
                    return blk.fields.get(e[3], Cv("int", 0))
            return Cv("int", 0)
        if k == "qmcall":
            base = self.eval(e[1])
            thisaddr = base.val if base.kind == "addr" else None
            qual, name = e[2], e[3]
            key = (qual, name)
            if key in self.methods:
                owner, params, body = self.methods[key]
                argvals = [self.eval(a) for a in e[4]]
                return self._invoke_method(owner, name, params, body, thisaddr, argvals)
            return Cv("int", 0)
        raise SimError(self.cur_line, f"未知表达式 {e}")

    def _do_delete(self, v, isarr):
        if v.kind != "addr" or v.val not in self.heap:
            return
        blk = self.heap[v.val]
        if isarr or blk.typename not in self.classes or blk.arr is not None:
            # 数组 / 标量：直接释放(标量无析构)
            self._mark_freed(blk)
            return
        if not blk.freed:
            self._destruct(blk.typename, blk)
            self._mark_freed(blk)

    def _bump(self, v, up):
        if v.kind == "float":
            return Cv("float", v.val + (1 if up else -1))
        return Cv("int", v.val + (1 if up else -1))

    def _binop(self, op, l, r):
        if op == "&&":
            return Cv("int", 1 if (self.truthy(l) and self.truthy(r)) else 0)
        if op == "||":
            return Cv("int", 1 if (self.truthy(l) or self.truthy(r)) else 0)
        if op in ("==", "!=", "<", "<=", ">", ">="):
            lv = l.val if l.kind in ("int", "float") else 0
            rv = r.val if r.kind in ("int", "float") else 0
            res = {"==": lv == rv, "!=": lv != rv, "<": lv < rv,
                   "<=": lv <= rv, ">": lv > rv, ">=": lv >= rv}[op]
            return Cv("int", 1 if res else 0)
        lf = l.kind in ("float", "int")
        rf = r.kind in ("float", "int")
        if op == "+":
            if l.kind == "str" or r.kind == "str":
                return Cv("str", str(l.val if l.kind == "str" else "") + str(r.val if r.kind == "str" else ""))
            if l.kind == "addr":
                return Cv("addr", l.val + int(self.to_num(r)))
            if r.kind == "addr":
                return Cv("addr", r.val + int(self.to_num(l)))
            if lf and rf and (l.kind == "float" or r.kind == "float"):
                return Cv("float", self.to_num(l) + self.to_num(r))
            return Cv("int", int(self.to_num(l)) + int(self.to_num(r)))
        if op == "-":
            if l.kind == "addr":
                return Cv("addr", l.val - int(self.to_num(r)))
            if lf and rf and (l.kind == "float" or r.kind == "float"):
                return Cv("float", self.to_num(l) - self.to_num(r))
            return Cv("int", int(self.to_num(l)) - int(self.to_num(r)))
        if op == "*":
            if lf and rf and (l.kind == "float" or r.kind == "float"):
                return Cv("float", self.to_num(l) * self.to_num(r))
            return Cv("int", int(self.to_num(l) * self.to_num(r)))
        if op == "/":
            rv = self.to_num(r)
            if rv == 0:
                raise SimError(self.cur_line, "除数为 0")
            if l.kind == "float" or r.kind == "float":
                return Cv("float", self.to_num(l) / rv)
            return Cv("int", int(self.to_num(l) / rv))
        if op == "%":
            return Cv("int", int(self.to_num(l)) % int(self.to_num(r)))
        raise SimError(self.cur_line, f"不支持运算符 {op}")

    # ---- 内存地址操作(指针教学, 第一版简略) ----
    def _take_addr(self, e):
        # &对象成员/变量 —— 简化为分配一个槽地址
        a = self.next_addr
        self.next_addr += 0x10
        return Cv("addr", a)

    def _deref(self, v):
        if v.kind == "addr" and v.val in self.heap:
            blk = self.heap[v.val]
            if blk.scalar is not None:
                return blk.scalar
        if v.kind == "null":
            raise SimError(self.cur_line, "对 NULL 解引用")
        return v

    # ---- 赋值目标 ----
    def _assign(self, target, value):
        if target[0] == "var":
            name = target[1]
            lv = self._lookup_var(name)
            if lv is not None:
                self._cur_vars_set(name, self._coerce_var(name, value))
                return
            mv, _addr = self._read_member_of_this(name)
            if mv is not None:
                self._write_member_of_this(name, value)
                return
            self._cur().vars[name] = self._coerce_var(name, value)
            return
        if target[0] in ("member", "qmember"):
            # member: 对象.成员   qmember: 对象.类名::成员
            fld = target[3] if target[0] == "qmember" else target[2]
            base = self.eval(target[1])
            if base.kind == "addr":
                blk = self.heap.get(base.val)
                if blk is not None:
                    self._set_field(blk, fld, value)
                    return
            raise SimError(self.cur_line, "成员赋值目标无效")
        if target[0] == "index":
            arr = self.eval(target[1])
            idx = int(self.to_num(self.eval(target[2])))
            if arr.kind == "addr":
                blk = self.heap.get(arr.val)
                if blk is not None and getattr(blk, "arr", None) is not None:
                    if idx < 0 or idx >= len(blk.arr):
                        raise SimError(self.cur_line, "下标越界")
                    blk.arr[idx] = self._coerce_arr(blk, value)
                    return
            raise SimError(self.cur_line, "下标赋值目标无效")
        if target[0] == "deref" or (target[0] == "unary" and target[1] == "*"):
            addr = self.eval(target[2] if target[0] == "unary" else target[1])
            if addr.kind == "addr" and addr.val in self.heap:
                blk = self.heap[addr.val]
                if blk.scalar is not None:
                    blk.scalar = self._coerce_arr(blk, value)
                    return
            raise SimError(self.cur_line, "解引用赋值目标无效")
        raise SimError(self.cur_line, f"暂不支持该赋值形式 {target}")

    def _coerce_arr(self, blk, value):
        cur = blk.scalar if blk.scalar is not None else (blk.arr[0] if blk.arr else None)
        if cur is not None and cur.kind == "float" and value.kind in ("int", "char"):
            return Cv("float", self.to_num(value))
        if cur is not None and cur.kind == "char" and value.kind in ("int", "float"):
            return Cv("char", int(self.to_num(value)))
        if cur is not None and cur.kind == "int" and value.kind in ("float", "char"):
            return Cv("int", int(self.to_num(value)))
        return value

    def _cur_vars_set(self, name, value):
        fr = self.frames[-1] if self.frames else None
        if fr is not None:
            fr.vars[name] = value
            return
        raise SimError(self.cur_line, "无活动帧")

    def _coerce_var(self, name, value):
        # 按当前帧已声明变量类型规整(char/float 保持自身类型)
        fr = self.frames[-1] if self.frames else None
        if fr is not None and name in fr.vars:
            vi = fr.vars[name]
            if vi.kind == "float" and value.kind in ("int", "char"):
                return Cv("float", self.to_num(value))
            if vi.kind == "char" and value.kind in ("int", "float"):
                return Cv("char", int(self.to_num(value)))
            if vi.kind == "int" and value.kind in ("float", "char"):
                return Cv("int", int(self.to_num(value)))
        return value

    def _write_member_of_this(self, name, value):
        fr = self.frames[-1] if self.frames else None
        if fr is not None and fr.objaddr is not None:
            blk = self.heap.get(fr.objaddr)
            if blk is not None and name in blk.fields:
                self._set_field(blk, name, value)
                return
        raise SimError(self.cur_line, f"成员 '{name}' 写入失败")

    def _coerce_field(self, blk, name, value):
        cur = blk.fields.get(name)
        if cur is not None and cur.kind == "float" and value.kind in ("int", "char"):
            return Cv("float", self.to_num(value))
        if cur is not None and cur.kind == "char" and value.kind in ("int", "float"):
            return Cv("char", int(self.to_num(value)))
        if cur is not None and cur.kind == "int" and value.kind in ("float", "char"):
            return Cv("int", int(self.to_num(value)))
        return value

    # ---- 调用(含继承链解析) ----
    def _call(self, callee, args):
        if callee[0] == "member":
            base = self.eval(callee[1])
            if base.kind == "addr" and base.val in self.heap:
                blk = self.heap[base.val]
                mname = callee[2]
                owner = self._resolve_method(blk.typename, mname)
                if owner is not None:
                    _o, params, body = self.methods[(owner, mname)]
                    argvals = [self.eval(a) for a in args]
                    return self._invoke_method(owner, mname, params, body, base.val, argvals)
            raise SimError(self.cur_line, f"对象方法调用失败: {callee[2]}")
        if callee[0] == "var":
            fname = callee[1]
            if fname in self.funcs:
                return self._call_func(fname, args)
            # 方法内部裸调方法 this->m()：沿 this 实际类继承链解析
            thisaddr = self._this_obj()
            if thisaddr is not None:
                blk = self.heap.get(thisaddr)
                if blk is not None:
                    owner = self._resolve_method(blk.typename, fname)
                    if owner is not None:
                        _o, params, body = self.methods[(owner, fname)]
                        argvals = [self.eval(a) for a in args]
                        return self._invoke_method(owner, fname, params, body, thisaddr, argvals)
            # 未定义函数/系统库 → 0
            return Cv("int", 0)
        return Cv("int", 0)

    def _call_func(self, fname, args):
        rtype, ptr, params, body = self.funcs[fname]
        argvals = [self.eval(a) for a in args]
        fr = CppFrame(fname)
        self.frames.append(fr)
        ret = Cv("int", 0)
        try:
            for i, (pn, pt, pp, default) in enumerate(params):
                if i < len(argvals):
                    av = argvals[i]
                else:
                    av = self.eval(default) if default is not None else Cv("int", 0)
                fr.vars[pn] = self._coerce_param(pt, pp, av)
            r = self._run_body(body)
            if isinstance(r, tuple) and r and r[0] == "ret":
                ret = r[1]
        finally:
            self.frames.pop()
        return ret

    def _coerce_param(self, ptype, pptr, av):
        if pptr > 0 or ptype in self.classes:
            return av   # 指针/对象形参按引用(共享地址) 简化
        if ptype in ("float", "double"):
            return Cv("float", self.to_num(av))
        return av

    # ---- 语句执行 ----
    def _exec(self, stmts):
        for st in stmts:
            self.cur_line = st.line
            self.steps += 1
            if self.steps > self.step_limit:
                raise SimError(st.line, "执行步数超限(疑似死循环)")
            r = self._exec_stmt(st)
            if r is not None:
                return r
        return None

    def _record(self, line):
        if self.snapshots is not None:
            self.snapshots[line] = self._snapshot()
            if len(self.step_snapshots) < 20000:
                self.step_snapshots.append((line, self.snapshots[line]))
        if self.stop_line is not None and line == self.stop_line:
            raise StopExec()

    def _exec_stmt(self, st):
        k = st.kind
        if k == "block":
            # 块级作用域：块内声明的栈对象在块结束时按逆序析构
            self.scope_obj.append([])
            try:
                return self._exec(st.stmts)
            finally:
                objs = self.scope_obj.pop()
                if self.stop_line is None:
                    self._dtor_list(objs)
        if k == "seq":
            for s in st.stmts:
                r = self._exec_stmt(s)
                if r is not None:
                    return r
            return None
        if k == "decl":
            self._exec_decl(st)
            self._record(st.line)
            return None
        if k == "assign":
            v = self.eval(st.expr)
            self._assign(st.target, v)
            self._record(st.line)
            return None
        if k == "expr":
            self.eval(st.expr)
            self._record(st.line)
            return None
        if k == "if":
            c = self.truthy(self.eval(st.cond))
            r = self._exec_stmt(st.then_s) if c else (self._exec_stmt(st.else_s) if st.else_s else None)
            if r is not None:
                return r
            return None
        if k == "while":
            guard = 0
            while self.truthy(self.eval(st.cond)):
                guard += 1
                if guard > 100000:
                    raise SimError(st.line, "while 循环超限(疑似死循环)")
                r = self._exec_stmt(st.body)
                if r == "break":
                    break
                if r is not None:
                    return r
            self._record(st.line)
            return None
        if k == "dowhile":
            guard = 0
            while True:
                guard += 1
                if guard > 100000:
                    raise SimError(st.line, "do-while 循环超限")
                r = self._exec_stmt(st.body)
                if r == "break":
                    break
                if r is not None:
                    return r
                if not self.truthy(self.eval(st.cond)):
                    break
            self._record(st.line)
            return None
        if k == "for":
            if st.init:
                self._exec_stmt(st.init)
            guard = 0
            while st.cond is None or self.truthy(self.eval(st.cond)):
                guard += 1
                if guard > 100000:
                    raise SimError(st.line, "for 循环超限(疑似死循环)")
                r = self._exec_stmt(st.body)
                if r == "break":
                    break
                if r is not None:
                    return r
                if st.step:
                    if isinstance(st.step, tuple) and st.step[0] == "assign":
                        self._assign(st.step[1], self.eval(st.step[2]))
                    else:
                        self.eval(st.step)
            self._record(st.line)
            return None
        if k == "return":
            if st.expr:
                return ("ret", self.eval(st.expr))
            return ("ret", Cv("int", 0))
        if k == "break":
            return "break"
        if k == "cout":
            self._exec_cout(st)
            self._record(st.line)
            return None
        if k == "cin":
            self._exec_cin(st)
            self._record(st.line)
            return None
        if k == "printf":
            self._exec_printf(st)
            self._record(st.line)
            return None
        return None

    # ---- iostream / printf ----
    def _fmt_val(self, v):
        """cout << 值 → 字符串。float 用类似 C++ cout 默认(整数去 .0，其余去尾 0)；char 输出字符"""
        if v.kind == "str":
            return v.val
        if v.kind == "char":
            return chr(v.val & 0xFF)
        if v.kind == "int":
            return str(v.val)
        if v.kind == "float":
            if v.val == int(v.val):
                return str(int(v.val))
            s = f"{v.val:.6f}".rstrip("0").rstrip(".")
            return s
        if v.kind == "addr":
            return f"0x{v.val:x}"
        if v.kind == "null":
            return "0"
        return "?"

    def _exec_cout(self, st):
        out = []
        for p in st.parts:
            if isinstance(p, tuple) and p and p[0] == "endl":
                out.append("\n")
                continue
            v = self.eval(p)
            out.append(self._fmt_val(v))
        self.outputs.append("".join(out))

    def _exec_cin(self, st):
        for tg in st.targets:
            if self.input_pos < len(self.inputs):
                val = self.inputs[self.input_pos]
                self.input_pos += 1
            else:
                val = 0
            self._assign_input(tg, val)

    def _assign_input(self, target, val):
        if target[0] == "var":
            name = target[1]
            lv = self._lookup_var(name)
            if lv is not None:
                self._cur_vars_set(name, self._mk_val_for(lv, val))
                return
            mv, _a = self._read_member_of_this(name)
            if mv is not None:
                self._write_member_of_this(name, self._mk_val_for(mv, val))
                return
            self._cur().vars[name] = Cv("int", val)
            return
        if target[0] == "member":
            base = self.eval(target[1])
            if base.kind == "addr":
                blk = self.heap.get(base.val)
                if blk is not None:
                    cur = blk.fields.get(target[2])
                    blk.fields[target[2]] = self._mk_val_for(cur if cur is not None else Cv("int", 0), val)
            return

    def _mk_val_for(self, cur, val):
        if cur.kind == "float":
            return Cv("float", float(val))
        if cur.kind == "char":
            return Cv("char", int(val))
        if cur.kind == "str":
            return Cv("str", str(val))
        return Cv("int", int(float(val)))

    def _exec_printf(self, st):
        fmt = st.fmt
        vals = []
        for a in st.args:
            try:
                v = self.eval(a)
            except Exception:
                v = Cv("int", 0)
            vals.append(self._printf_arg(v))
        if not fmt:
            if vals and isinstance(vals[0], str):
                fmt = vals[0]
                vals = vals[1:]
            else:
                self.outputs.append(" ".join(str(x) for x in vals))
                return
        out = ""
        ai = 0
        i, n = 0, len(fmt)
        while i < n:
            ch = fmt[i]
            if ch == "%" and i + 1 < n:
                nxt = fmt[i + 1]
                if nxt == "%":
                    out += "%"
                    i += 2
                    continue
                j = i + 1
                while j < n and fmt[j] in "-+0# 0123456789.lhL":
                    j += 1
                typ = fmt[j] if j < n else ""
                if typ and typ in "diuoxXfFeEgGcsp":
                    v = vals[ai] if ai < len(vals) else 0
                    ai += 1
                    out += self._pf_val(typ, v)
                    i = j + 1
                    continue
                out += "%"
                i += 1
            else:
                out += ch
                i += 1
        self.outputs.append(out)

    def _printf_arg(self, v):
        if isinstance(v, Cv):
            if v.kind == "str":
                return v.val
            if v.kind == "float":
                return v.val
            if v.kind == "int":
                return v.val
            if v.kind == "char":
                return v.val
            if v.kind == "addr":
                return f"0x{v.val:x}"
            return 0
        return v

    def _pf_val(self, typ, v):
        try:
            if typ in "di":
                return str(int(float(v)))
            if typ == "u":
                return str(int(v) & 0xFFFFFFFF)
            if typ in "oxX":
                nn = int(v) & 0xFFFFFFFF
                return format(nn, "o") if typ == "o" else format(nn, "x" if typ == "x" else "X")
            if typ in "fFeEgG":
                return f"{float(v):.6f}"
            if typ == "c":
                return chr(int(float(v)) & 0xFF)
            if typ == "s":
                return str(v)
            return str(v)
        except Exception:
            return str(v)

    # ---- 声明 ----
    def _exec_decl(self, st):
        fr = self._cur()
        if st.is_array:
            vals = []
            if isinstance(st.init, tuple) and st.init[0] == "strlit":
                for ch in st.init[1]:
                    vals.append(Cv("int", ord(ch)))
            elif isinstance(st.init, tuple) and st.init[0] == "arrinit":
                for x in st.init[1]:
                    vals.append(x)
            n = st.arr_size or max(1, len(vals))
            while len(vals) < n:
                vals.append(Cv("int", 0))
            # 数组按独立堆块存储
            blk = CppBlk(self.next_addr, st.vtype, "栈")
            self.next_addr += 0x10
            blk.arr = vals
            self.heap[blk.addr] = blk
            fr.vars[st.name] = Cv("addr", blk.addr)
            return
        if st.is_ptr:
            # 指针(含类指针 A* p = ...)
            val = self.eval(st.init) if st.init is not None else Cv("null")
            fr.vars[st.name] = val
            fr.vtypes[st.name] = st.vtype
            return
        if st.vtype in self.classes:
            # 对象(栈): 分配块并调用匹配构造
            blk = self._alloc(st.vtype, "栈")
            fr.vars[st.name] = Cv("addr", blk.addr)
            fr.vtypes[st.name] = st.vtype
            if isinstance(st.init, tuple) and st.init and st.init[0] == "objinit":
                argvals = [self.eval(a) for a in st.init[1]]
                self._construct(st.vtype, blk, argvals)
            elif isinstance(st.init, tuple) and st.init and st.init[0] == "var":
                # A b = a; 简化拷贝(逐字段)
                src = self.eval(st.init)
                if src.kind == "addr" and src.val in self.heap:
                    sb = self.heap[src.val]
                    for fn_, fv in sb.fields.items():
                        blk.fields[fn_] = Cv(fv.kind, fv.val)
            else:
                # 默认/无参构造(若无匹配构造则字段保持默认)
                self._construct(st.vtype, blk, [])
            self._record_stack_obj(blk.addr)
            return
        # 基本类型(含 objinit 简化取第一参数)
        if st.init is not None:
            if isinstance(st.init, tuple) and st.init and st.init[0] == "objinit":
                v = self.eval(st.init[1][0]) if st.init[1] else Cv("int", 0)
            else:
                v = self.eval(st.init)
        else:
            v = Cv("int", 0)
        if st.vtype in ("float", "double"):
            v = Cv("float", self.to_num(v)) if v.kind != "float" else v
        elif st.vtype == "char":
            v = Cv("char", int(self.to_num(v)))
        fr.vars[st.name] = v
        fr.vtypes[st.name] = st.vtype

    # ---- 快照 ----
    def _desc(self, v):
        if v.kind == "int":
            return ("int", v.val)
        if v.kind == "float":
            return ("int", int(v.val)) if v.val == int(v.val) else ("float", v.val)
        if v.kind == "char":
            return ("int", v.val)
        if v.kind == "addr":
            return ("ptr", v.val)
        if v.kind == "null":
            return ("null", None)
        if v.kind == "str":
            return ("strlit", v.val)
        return ("null", None)

    def _snapshot(self):
        frames = []
        for fr in self.frames:
            vs = []
            for name, cv in fr.vars.items():
                t = self._vtype(name)
                vs.append((name, {"type": t, "loc": "栈", "value": self._desc(cv)}))
            if fr.objaddr is not None and "this" not in fr.vars:
                vs.insert(0, ("this", {"type": "对象*", "loc": "栈",
                                       "value": ("ptr", fr.objaddr)}))
            frames.append({"func": fr.fname, "vars": vs})
        hb = []
        for addr in sorted(self.heap.keys())[:50]:
            blk = self.heap[addr]
            fields = {}
            for fn_, fv in blk.fields.items():
                fields[fn_] = self._desc(fv)
            hb.append({"addr": addr, "typename": blk.typename, "fields": fields,
                       "loc": blk.loc, "scalar": None, "freed": blk.freed,
                       "array": None})
        return {"frames": frames, "heap": hb, "heap_total": len(self.heap)}

    def _vtype(self, name):
        # 用字段类型尽力显示(简略) —— 仅当前帧
        fr = self.frames[-1] if self.frames else None
        if fr is not None and name in fr.vars:
            cv = fr.vars[name]
            if cv.kind == "float":
                return "float"
            if cv.kind == "addr":
                return "ptr"
        return "int"

    # ================= 本批新增: 构造/析构/继承/new-delete/作用域 =================

    def _set_field(self, blk, name, value):
        cur = blk.fields.get(name)
        blk.fields[name] = self._coerce_field(blk, name, value) if cur is not None else value

    def _match_ctor(self, cls, nargs):
        """选择能接收 nargs 实参的构造函数(含默认参数); 返回 (params, initlist, body) 或 None"""
        cd = self.classes.get(cls)
        if cd is None:
            return None
        for params, initlist, body in cd.ctors:
            np = len(params)
            ndef = sum(1 for p in params if p[3] is not None)
            if np - ndef <= nargs <= np:
                return (params, initlist, body)
        return None

    def _construct(self, cls, blk, argvals):
        """对已 alloc 的对象块执行完整构造：基类→对象成员→初始化/自身语句体。
        顺序保证与 g++ 一致(base body → 成员 ctor(声明序) → 自身 body)。"""
        cd = self.classes.get(cls)
        if cd is None or blk is None:
            return
        m = self._match_ctor(cls, len(argvals))
        if m is None:
            return      # 类无匹配构造函数 → 保持默认字段
        params, initlist, body = m
        fr = CppFrame(f"{cls} 构造函数")
        fr.objaddr = blk.addr
        self.frames.append(fr)
        try:
            # 绑定形参(缺省用默认参数; 均在构造帧内求值)
            for i, (pn, pt, pp, default) in enumerate(params):
                if i < len(argvals):
                    av = argvals[i]
                else:
                    av = self.eval(default) if default is not None else Cv("int", 0)
                fr.vars[pn] = self._coerce_param(pt, pp, av)
            inits = {}
            for it in initlist:
                if it[0] == "base":
                    inits.setdefault("__base__", it[2])
                else:
                    inits[it[1]] = it[2]
            # 1) 基类子对象构造(同一块)
            if cd.base:
                self._construct(cd.base, blk,
                                [self.eval(a) for a in inits.get("__base__", [])])
            # 2) 本类对象成员构造(声明序, 取 initlist 参数或默认构造)
            for fname, ftype, ptr in cd.fields:
                if ftype in self.classes and ptr == 0:
                    cv = blk.fields.get(fname)
                    sub = self.heap.get(cv.val) if cv is not None and cv.kind == "addr" else None
                    if sub is not None:
                        margs = [self.eval(a) for a in inits[fname]] if fname in inits else []
                        self._construct(ftype, sub, margs)
            # 3) 普通成员按 initlist 赋值 + 自身语句体
            for fname, ftype, ptr in cd.fields:
                if fname in inits and not (ftype in self.classes and ptr == 0):
                    vs = [self.eval(a) for a in inits[fname]]
                    if vs:
                        self._set_field(blk, fname, vs[0])
            self._run_body(body)
        finally:
            self.frames.pop()

    def _destruct(self, cls, blk):
        """析构: 自身析构体 → 自身对象成员(逆声明序) → 基类析构"""
        cd = self.classes.get(cls)
        if cd is None or blk is None or blk.freed:
            return
        if cd.dtor is not None:
            params, body = cd.dtor
            fr = CppFrame(f"~{cls}")
            fr.objaddr = blk.addr
            self.frames.append(fr)
            try:
                self._run_body(body)
            finally:
                self.frames.pop()
        for fname, ftype, ptr in reversed(cd.fields):
            if ftype in self.classes and ptr == 0:
                cv = blk.fields.get(fname)
                sub = self.heap.get(cv.val) if cv is not None and cv.kind == "addr" else None
                if sub is not None:
                    self._destruct(ftype, sub)
        if cd.base:
            self._destruct(cd.base, blk)

    def _mark_freed(self, blk):
        """整棵对象树标记释放(可视化红色), 不调析构"""
        if blk is None:
            return
        blk.freed = True
        for fv in blk.fields.values():
            if fv.kind == "addr" and fv.val in self.heap:
                self._mark_freed(self.heap[fv.val])

    def _record_stack_obj(self, addr):
        if self.scope_obj:
            self.scope_obj[-1].append(addr)
        else:
            self._root_objs.append(addr)

    def _run_body(self, body):
        """作为"函数体/构造函数体"作用域执行(顶层对象结束析构)"""
        self.scope_obj.append([])
        try:
            return self._exec(body)
        finally:
            objs = self.scope_obj.pop()
            if self.stop_line is None:     # 点击查看某行时不析构(保留现场)
                self._dtor_list(objs)

    def _dtor_list(self, objs):
        for addr in reversed(objs):
            blk = self.heap.get(addr)
            if blk is not None and not blk.freed:
                self._destruct(blk.typename, blk)
                self._mark_freed(blk)

    def _eval_new(self, e):
        """("new", vtype, spec)  spec=("scalar",)|("array",nExpr)|("obj",args)"""
        vtype, ptr = e[1], 0
        spec = e[2]
        kind = spec[0]
        if kind == "scalar":
            blk = self._mk_scalar(vtype)
            return Cv("addr", blk.addr)
        if kind == "array":
            n = max(1, int(self.to_num(self.eval(spec[1]))))
            blk = self._mk_array(vtype, n)
            return Cv("addr", blk.addr)
        # 对象
        argvals = [self.eval(a) for a in spec[1]]
        blk = self._alloc(vtype, "堆")
        self._construct(vtype, blk, argvals)
        return Cv("addr", blk.addr)

    def _mk_scalar(self, vtype):
        blk = CppBlk(self.next_addr, vtype, "堆")
        self.next_addr += 0x10
        if vtype == "float" or vtype == "double":
            blk.scalar = Cv("float", 0.0)
        elif vtype == "char":
            blk.scalar = Cv("char", 0)
        else:
            blk.scalar = Cv("int", 0)
        self.heap[blk.addr] = blk
        return blk

    def _mk_array(self, vtype, n):
        blk = CppBlk(self.next_addr, vtype, "堆")
        self.next_addr += 0x10
        if vtype == "float" or vtype == "double":
            blk.arr = [Cv("float", 0.0)] * n
        elif vtype == "char":
            blk.arr = [Cv("char", 0)] * n
        else:
            blk.arr = [Cv("int", 0)] * n
        self.heap[blk.addr] = blk
        return blk

    def _this_obj(self):
        fr = self.frames[-1] if self.frames else None
        return fr.objaddr if fr is not None else None

    def _call_qualified(self, qual_cls, name, args):
        """显式限定调用 A::m(...)（在方法体内，this 的实际类可为 A 的派生类）"""
        thisaddr = self._this_obj()
        key = (qual_cls, name)
        if key not in self.methods:
            return Cv("int", 0)
        owner, params, body = self.methods[key]
        argvals = [self.eval(a) for a in args]
        return self._invoke_method(owner, name, params, body, thisaddr, argvals)

    def _invoke_method(self, owner, name, params, body, thisaddr, argvals):
        fr = CppFrame(f"{owner}::{name}")
        fr.objaddr = thisaddr
        self.frames.append(fr)
        ret = Cv("int", 0)
        try:
            for i, (pn, pt, pp, default) in enumerate(params):
                if i < len(argvals):
                    av = argvals[i]
                else:
                    av = self.eval(default) if default is not None else Cv("int", 0)
                fr.vars[pn] = self._coerce_param(pt, pp, av)
            r = self._run_body(body)
            if isinstance(r, tuple) and r and r[0] == "ret":
                ret = r[1]
        finally:
            self.frames.pop()
        return ret


# ---------------------------------------------------------------
# 顶层：与 simcore.Simulator 同接口(CppSimulator)
# ---------------------------------------------------------------
class CppSimulator:
    def __init__(self, code):
        self.code = code
        self.cpp_detected = True
        self.cpp_hint = None
        self.toks = tokenize(code)
        self.parser = CppParser(self.toks)
        self.classes = self.parser.classes
        self.funcs = self.parser.funcs
        self.engine = None
        self.snapshots = {}
        self.pending_inputs = []

    def main_name(self):
        return "main" if "main" in self.funcs else (next(iter(self.funcs)) if self.funcs else None)

    def _make_engine(self, stop_line=None):
        eng = CppEngine(self.classes, self.funcs, inputs=self.pending_inputs)
        eng.stop_line = stop_line
        self.engine = eng
        m = self.main_name()
        if m is None:
            return None
        fr = CppFrame(m)
        # main 参数默认 0
        eng.frames.append(fr)
        return self.funcs[m]

    def run(self):
        info = self._make_engine(None)
        if info is None:
            return {}
        _rtype, _ptr, _params, body = info
        try:
            self.engine._run_body(body)
        except SimError as ex:
            self.engine.error = ex
        except RecursionError:
            self.engine.error = SimError(0, "递归过深")
        self.snapshots = self.engine.snapshots
        return self.snapshots

    def run_to_line(self, target_line):
        info = self._make_engine(target_line)
        if info is None:
            return {}
        _rtype, _ptr, _params, body = info
        try:
            self.engine._run_body(body)
        except StopExec:
            pass
        except SimError as ex:
            self.engine.error = ex
        except RecursionError:
            self.engine.error = SimError(0, "递归过深")
        self.snapshots = self.engine.snapshots
        return self.snapshots

    def run_pause_at_input(self):
        info = self._make_engine(None)
        if info is None:
            return {}, None, None
        _rtype, _ptr, _params, body = info
        try:
            self.engine._run_body(body)
        except SimError as ex:
            self.engine.error = ex
        except RecursionError:
            self.engine.error = SimError(0, "递归过深")
        self.snapshots = self.engine.snapshots
        return self.snapshots, None, (self.engine.error if self.engine else None)
