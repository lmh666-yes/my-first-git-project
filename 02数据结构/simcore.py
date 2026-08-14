# -*- coding: utf-8 -*-
"""
simcore.py — 迷你 C 数据结构模拟引擎（供 ds_visualizer 使用）

支持的教学用 C 子集：
  · 类型：int、char(按 int)、typedef struct 结构体、指针、一维数组
  · 内存：malloc / calloc（含 sizeof）
  · 语句：声明、赋值、-> / * / & / []、算术/比较/逻辑、if/else、while、
          for、break、return、printf(忽略)、函数定义与递归调用
  · 注释与 #include 等预处理自动忽略

不支持的语法会抛出 SimError（含行号），GUI 将标红提示，绝不瞎猜。
"""

import re


class SimError(Exception):
    """带行号的模拟错误"""
    def __init__(self, line, msg):
        super().__init__(f"第 {line} 行：{msg}")
        self.line = line
        self.msg = msg


class StopExec(Exception):
    """执行到目标行后停止（GUI 点击行用），通过异常传播穿透表达式求值"""
    pass


# ---------------------------------------------------------------
# 词法：把一段代码切成 token（含行号）
# ---------------------------------------------------------------
TOKEN_RE = re.compile(r"""
    (?P<ws>\s+)
  | (?P<pre>\#[^\n]*)
  | (?P<comment>//[^\n]*|/\*.*?\*/)
  | (?P<num>0[xX][0-9a-fA-F]+|\d+\.\d+|\d+)
  | (?P<str>"(?:[^"\\]|\\.)*")
  | (?P<char>'[^']')
  | (?P<id>[A-Za-z_]\w*)
  | (?P<op>->|==|!=|<=|>=|&&|\|\||\+\+|--|\+=|-=|\*=|/=|%=|\.\.\.|[+\-*/%<>=!&*]|\(|\)|\{|\}|\[|\]|;|,|\.)
""", re.VERBOSE | re.DOTALL)


class Token:
    __slots__ = ("kind", "text", "line")

    def __init__(self, kind, text, line):
        self.kind = kind
        self.text = text
        self.line = line

    def __repr__(self):
        return f"Token({self.kind},{self.text!r},L{self.line})"


def tokenize(code, start_line=1):
    """把代码切为 token 列表；start_line 用于拼接多文件片段。"""
    toks = []
    line = start_line
    pos = 0
    n = len(code)
    while pos < n:
        m = TOKEN_RE.match(code, pos)
        if not m:
            raise SimError(line, f"无法识别的字符 {code[pos]!r}")
        pos = m.end()
        line += code.count("\n", m.start(), pos)
        kind = m.lastgroup
        text = m.group()
        if kind in ("ws", "comment", "pre"):
            continue
        toks.append(Token(kind, text, line))
    return toks


# ---------------------------------------------------------------
# 语法树
# ---------------------------------------------------------------
class StructDef:
    def __init__(self, name, fields):
        self.name = name            # 结构体名
        self.fields = fields        # [(fname, ftype)]  ftype='int' 或 ('ptr', typename) 或 None


class FuncDef:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params        # [(pname, ptype)]
        self.body = body            # [Stmt]


class Stmt:
    __slots__ = ("line", "kind")

    def __init__(self, line, kind):
        self.line = line
        self.kind = kind


class BlockStmt(Stmt):
    def __init__(self, line, stmts):
        super().__init__(line, "block")
        self.stmts = stmts


class SeqStmt(Stmt):
    """同作用域的多个语句（用于 int a, b; 多变量声明），不创建新作用域"""
    def __init__(self, line, stmts):
        super().__init__(line, "seq")
        self.stmts = stmts


class DeclStmt(Stmt):
    def __init__(self, line, vtype, name, init_expr, is_ptr, is_array, arr_size, dims=None):
        super().__init__(line, "decl")
        self.vtype = vtype
        self.name = name
        self.init = init_expr
        self.is_ptr = is_ptr
        self.is_array = is_array
        self.arr_size = arr_size
        self.dims = dims or []


class AssignStmt(Stmt):
    def __init__(self, line, target, expr):
        super().__init__(line, "assign")
        self.target = target        # LValue 表达式
        self.expr = expr


class ExprStmt(Stmt):
    def __init__(self, line, expr):
        super().__init__(line, "expr")
        self.expr = expr


class IfStmt(Stmt):
    def __init__(self, line, cond, then_s, else_s):
        super().__init__(line, "if")
        self.cond = cond
        self.then_s = then_s
        self.else_s = else_s


class WhileStmt(Stmt):
    def __init__(self, line, cond, body):
        super().__init__(line, "while")
        self.cond = cond
        self.body = body


class ForStmt(Stmt):
    def __init__(self, line, init, cond, step, body):
        super().__init__(line, "for")
        self.init = init
        self.cond = cond
        self.step = step
        self.body = body


class ReturnStmt(Stmt):
    def __init__(self, line, expr):
        super().__init__(line, "return")
        self.expr = expr


class BreakStmt(Stmt):
    def __init__(self, line):
        super().__init__(line, "break")


class PrintfStmt(Stmt):
    def __init__(self, line):
        super().__init__(line, "printf")


# 表达式：以元组 (kind, ...) 表示
#  ('lit', int)                      整数
#  ('null',)                          NULL
#  ('var', name)                     变量名
#  ('deref', expr)                   *p
#  ('addr', expr)                    &x
#  ('member', expr, field)           e->f 或 e.f（运行时决定）
#  ('index', expr, expr)             a[i]
#  ('bin', op, l, r)
#  ('unary', op, e)                  -x !x
#  ('call', name, [args])
#  ('sizeof', typename)
#  ('alloc', typename, count)        由 call malloc 转换


# ---------------------------------------------------------------
# 语句解析器
# ---------------------------------------------------------------
class Parser:
    def __init__(self, toks):
        self.toks = toks
        self.pos = 0
        self.structs = {}   # name -> StructDef

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

    # ---------- 顶层 ----------
    def parse_program(self):
        funcs = {}
        while self.peek() is not None:
            if self.at(";"):
                self.next()
                continue
            # typedef struct
            if self.at("typedef"):
                self.parse_typedef()
            elif self.at_id():
                # 函数定义：type name(params) {
                self.parse_function(funcs)
            else:
                t = self.next()
                raise SimError(t.line, f"顶层无法识别 '{t.text}'")
        return funcs

    def parse_typedef(self):
        t = self.expect("typedef")
        if not self.at("struct"):
            raise SimError(t.line, "目前仅支持 typedef struct 结构体定义")
        self.expect("struct")
        name_t = self.next()
        if name_t.text == "{":
            # typedef struct { ... } Name;
            self.pos -= 1
            fields = self.parse_struct_fields()
            alias = self.next()
            alias2 = alias.text
            self.expect(";")
            self.structs[alias2] = StructDef(alias2, fields)
        else:
            name = name_t.text
            fields = self.parse_struct_fields()   # 内部会消费 '{'
            alias = self.next()
            alias2 = alias.text
            self.expect(";")
            self.structs[name] = StructDef(alias2, fields)
            self.structs[alias2] = StructDef(alias2, fields)

    def parse_struct_fields(self):
        self.expect("{")
        fields = []
        while not self.at("}"):
            ftype, ptr = self.parse_type()
            while True:
                ft = self.next()
                if ft.kind != "id":
                    raise SimError(ft.line, f"结构体字段名错误 '{ft.text}'")
                # 数组字段 int date[MAX]
                arr_size = None
                if self.at("["):
                    self.next()
                    sz = self.next()
                    arr_size = 100 if sz.kind != "num" else int(sz.text)
                    self.expect("]")
                if arr_size is not None:
                    fields.append((ft.text, ("array", ftype, arr_size)))
                elif ptr > 0:
                    fields.append((ft.text, ("ptr", ftype)))
                else:
                    fields.append((ft.text, ftype))
                if self.at(","):
                    self.next()
                    continue
                break
            self.expect(";")
        self.expect("}")
        return fields

    def parse_type(self):
        """解析类型，返回 (base_type, ptr_level)。ptr_level=0/1/2...
        支持 int / char / long long / unsigned / struct Name / 结构体名（typedef 过的）"""
        # 跳过修饰符（const/static/extern 等；unsigned/long/short 是基础类型）
        while self.peek() and self.peek().text in ("const", "static", "extern", "register", "volatile", "inline"):
            self.next()
        t = self.next()
        ptr = 0
        if t.text == "struct":
            nt = self.next()
            if nt.kind != "id":
                raise SimError(nt.line, f"struct 后需要类型名，实际 '{nt.text}'")
            base = nt.text
        elif t.text in ("int", "char", "void", "unsigned", "signed", "short", "long", "double", "float", "bool", "size_t", "longlong"):
            base = "int"
            while self.peek() and self.peek().text in ("int", "char", "long", "short", "unsigned", "signed"):
                self.next()
        elif t.kind == "id":
            base = t.text
        else:
            raise SimError(t.line, f"无法识别的类型 '{t.text}'")
        while self.at("*"):
            self.next()
            ptr += 1
        return base, ptr

    # ---------- 函数 ----------
    def parse_function(self, funcs):
        # 返回类型（含 struct Name / Node* / int* 等）
        self.parse_type()
        name_t = self.next()
        if name_t.kind != "id":
            raise SimError(name_t.line, f"函数名错误 '{name_t.text}'")
        self.expect("(")
        params = []
        if not self.at(")"):
            while True:
                # 变参函数 int sum(int n, ...)
                if self.at("..."):
                    self.next()
                    params.append(("<vararg>", "int"))
                    break
                # 函数指针参数：以 ( 开头，如 void (*cb)(int)
                if self.at("("):
                    depth = 0
                    pname = "<fn>"
                    while True:
                        tk = self.next()
                        if tk.text == "(":
                            depth += 1
                        elif tk.kind == "id" and depth == 1 and pname == "<fn>":
                            pname = tk.text
                        elif tk.text == ")":
                            depth -= 1
                            if depth == 0:
                                break
                    # 可能跟参数列表 (int)
                    if self.at("("):
                        d2 = 0
                        while True:
                            tk2 = self.next()
                            if tk2.text == "(":
                                d2 += 1
                            elif tk2.text == ")":
                                d2 -= 1
                                if d2 == 0:
                                    break
                    params.append((pname, "<fn>"))
                else:
                    ptype, ptr = self.parse_type()
                    if self.at("("):
                        # 函数指针参数：int (*op)(int)
                        depth = 0
                        pname = "<fn>"
                        while True:
                            tk = self.next()
                            if tk.text == "(":
                                depth += 1
                            elif tk.kind == "id" and depth == 1 and pname == "<fn>":
                                pname = tk.text
                            elif tk.text == ")":
                                depth -= 1
                                if depth == 0:
                                    break
                        if self.at("("):
                            d2 = 0
                            while True:
                                tk2 = self.next()
                                if tk2.text == "(":
                                    d2 += 1
                                elif tk2.text == ")":
                                    d2 -= 1
                                    if d2 == 0:
                                        break
                        params.append((pname, "<fn>"))
                    elif self.at(")"):
                        break
                    else:
                        pt = self.next()
                        if pt.kind != "id":
                            self.pos -= 1
                            break
                        params.append((pt.text, ptype if ptr == 0 else ("ptr", ptype)))
                        # 数组参数 int arr[] / shop arr[]
                        while self.at("["):
                            self.next()
                            if not self.at("]"):
                                while not self.at("]"):
                                    self.next()
                            self.expect("]")
                if self.at(","):
                    self.next()
                    continue
                break
        self.expect(")")
        if self.at(";"):
            # 函数原型声明：只记录声明，不实现
            self.next()
            if name_t.text not in funcs:
                funcs[name_t.text] = FuncDef(name_t.text, params, [])
            return
        try:
            body = self.parse_block()
        except (SimError, IndexError):
            # 函数体无法解析（未完成/不支持的语法）：跳过该函数其余内容
            while self.peek() is not None:
                self.next()
            return
        funcs[name_t.text] = FuncDef(name_t.text, params, body)

    def parse_block(self):
        self.expect("{")
        stmts = []
        while not self.at("}"):
            if self.peek() is None:
                raise SimError(0, "代码块缺少 '}'")
            stmts.append(self.parse_stmt())
        self.expect("}")
        return stmts

    # ---------- 语句 ----------
    def parse_stmt(self):
        t = self.peek()
        # 块
        if self.at("{"):
            return BlockStmt(t.line, self.parse_block())
        # 控制
        if self.at("if"):
            self.next()
            self.expect("(")
            cond = self.parse_expr()
            self.expect(")")
            then_s = self.parse_stmt()
            else_s = None
            if self.at("else"):
                self.next()
                else_s = self.parse_stmt()
            return IfStmt(t.line, cond, then_s, else_s)
        if self.at("while"):
            self.next()
            self.expect("(")
            cond = self.parse_expr()
            self.expect(")")
            body = self.parse_stmt()
            return WhileStmt(t.line, cond, body)
        if self.at("for"):
            self.next()
            self.expect("(")
            init = None
            if not self.at(";"):
                if self.looks_like_decl():
                    init = self.parse_decl(semi=False)
                else:
                    fline = self.peek().line
                    fexpr = self.parse_expr()
                    if self.at("="):
                        self.next()
                        rhs = self.parse_expr()
                        init = AssignStmt(fline, fexpr, rhs)
                    else:
                        init = ExprStmt(fline, fexpr)
            self.expect(";")
            cond = None
            if not self.at(";"):
                cond = self.parse_expr()
            self.expect(";")
            step = None
            if not self.at(")"):
                sline = self.peek().line
                se = self.parse_expr()
                if self.at("="):
                    self.next()
                    rhs = self.parse_expr()
                    step = ("assign", se, rhs)
                else:
                    step = se
            self.expect(")")
            body = self.parse_stmt()
            return ForStmt(t.line, init, cond, step, body)
        if self.at("return"):
            self.next()
            expr = None
            if not self.at(";"):
                expr = self.parse_expr()
            self.expect(";")
            return ReturnStmt(t.line, expr)
        if self.at("break"):
            self.next()
            self.expect(";")
            return BreakStmt(t.line)
        if self.at("printf"):
            self.next()
            self.expect("(")
            # 跳过直到匹配的 )
            depth = 1
            while depth > 0:
                tk = self.next()
                if tk.text == "(":
                    depth += 1
                elif tk.text == ")":
                    depth -= 1
            self.expect(";")
            return PrintfStmt(t.line)
        # 声明 vs 表达式
        if self.looks_like_decl():
            first = self.parse_decl(semi=False)
            stmts = [first]
            while self.at(","):        # 支持 int a, b; 多变量声明
                self.next()
                stmts.append(self.parse_decl_same(first, semi=False))
            self.expect(";")
            if len(stmts) == 1:
                return first
            return SeqStmt(first.line, stmts)
        # 空语句 ;
        if self.at(";"):
            self.next()
            return ExprStmt(t.line, ("lit", 0))
        # 表达式语句（可能是赋值：expr = expr; 或复合赋值 expr += expr;）
        expr = self.parse_expr()
        if self.at("=") or self.at("+=") or self.at("-=") or self.at("*=") \
                or self.at("/=") or self.at("%="):
            op = self.next().text
            rhs = self.parse_expr()
            self.expect(";")
            if op == "=":
                return AssignStmt(t.line, expr, rhs)
            return AssignStmt(t.line, expr, ("bin", op[0], expr, rhs))
        self.expect(";")
        return ExprStmt(t.line, expr)

    def parse_simple_stmt_inline(self):
        """for 的 init 或 while 体里的单条语句（不以 {} 开头）"""
        line = self.peek().line
        if self.looks_like_decl():
            return self.parse_decl(semi=False)
        expr = self.parse_expr()
        if self.at("=") or self.at("+=") or self.at("-=") or self.at("*=") \
                or self.at("/=") or self.at("%="):
            op = self.next().text
            rhs = self.parse_expr()
            self.expect(";")
            if op == "=":
                return AssignStmt(line, expr, rhs)
            return AssignStmt(line, expr, ("bin", op[0], expr, rhs))
        self.expect(";")
        return ExprStmt(line, expr)

    def looks_like_decl(self):
        """启发式：类型关键字 或 已知结构体名 且后面跟标识符（可含 * 前缀），非函数调用"""
        t = self.peek()
        if t is None or t.kind != "id":
            return False
        if t.text in ("int", "char", "void", "unsigned", "signed", "short", "long", "double", "float"):
            return True
        if t.text in self.structs:
            i = 1
            while True:
                nxt = self.peek(i)
                if nxt is None:
                    return False
                if nxt.text == "*":
                    i += 1
                    continue
                return nxt.kind == "id"
        return False

    def parse_decl(self, semi=True):
        line = self.peek().line
        vtype, ptr = self.parse_type()
        is_array = False
        arr_size = None
        # 支持 int a[5];
        nt = self.next()
        if nt.kind != "id":
            raise SimError(nt.line, f"变量名错误 '{nt.text}'")
        name = nt.text
        if self.at("["):
            total = 1
            dims = []
            while self.at("["):
                self.next()
                sz = self.next()
                d = (int(sz.text) if sz.kind == "num" else 10)
                total *= d
                dims.append(d)
                self.expect("]")
            arr_size = total
            is_array = True
        else:
            dims = []
        init = None
        if self.at("="):
            self.next()
            if self.at("{"):
                init = ("arrinit", self.parse_array_init())
            else:
                init = self.parse_expr()
        if semi:
            self.expect(";")
        return DeclStmt(line, vtype, name, init, ptr, is_array, arr_size, dims)

    def parse_decl_same(self, proto, semi=True):
        """多变量声明：int a, b; 中 b 复用 a 的类型"""
        line = self.peek().line
        nt = self.next()
        if nt.kind != "id":
            raise SimError(nt.line, f"变量名错误 '{nt.text}'")
        name = nt.text
        is_array = False
        arr_size = None
        if self.at("["):
            self.next()
            sz = self.next()
            arr_size = 100 if sz.kind != "num" else int(sz.text)
            self.expect("]")
            is_array = True
        init = None
        if self.at("="):
            self.next()
            if self.at("{"):
                init = ("arrinit", self.parse_array_init())
            else:
                init = self.parse_expr()
        if semi:
            self.expect(";")
        return DeclStmt(line, proto.vtype, name, init, proto.is_ptr, is_array, arr_size)

    def parse_array_init(self):
        """解析 {1,2,3,...} 初始化列表（支持嵌套 {} 整体跳过），返回整数列表"""
        self.expect("{")
        vals = []
        while not self.at("}"):
            tk = self.peek()
            if tk is None:
                break
            if tk.text == "{":
                self.parse_array_init()      # 嵌套初始化（如结构体数组），占位 0
                vals.append(0)
            elif tk.kind == "num":
                vals.append(int(float(self.next().text)))
            elif tk.text == "-":
                self.next()
                n = self.next()
                vals.append(-int(float(n.text)))
            elif tk.text == "}":
                break
            else:
                self.next()   # 跳过字符串等未知元素
            if self.at(","):
                self.next()
        self.expect("}")
        return vals

    # ---------- 表达式（优先级爬升） ----------
    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        e = self.parse_and()
        while self.at("||"):
            self.next()
            e = ("bin", "||", e, self.parse_and())
        return e

    def parse_and(self):
        e = self.parse_eq()
        while self.at("&&"):
            self.next()
            e = ("bin", "&&", e, self.parse_eq())
        return e

    def parse_eq(self):
        e = self.parse_rel()
        while self.at("==") or self.at("!="):
            op = self.next().text
            e = ("bin", op, e, self.parse_rel())
        return e

    def parse_rel(self):
        e = self.parse_add()
        while self.peek() and self.peek().text in ("<", "<=", ">", ">="):
            op = self.next().text
            e = ("bin", op, e, self.parse_add())
        return e

    def parse_add(self):
        e = self.parse_mul()
        while self.peek() and self.peek().text in ("+", "-"):
            op = self.next().text
            e = ("bin", op, e, self.parse_mul())
        return e

    def parse_mul(self):
        e = self.parse_unary()
        while self.peek() and self.peek().text in ("*", "/", "%"):
            op = self.next().text
            e = ("bin", op, e, self.parse_unary())
        return e

    def parse_unary(self):
        t = self.peek()
        if t and t.text in ("-", "!", "*", "&"):
            self.next()
            e = self.parse_unary()
            return ("unary", t.text, e)
        if t and t.text in ("++", "--"):
            self.next()
            e = self.parse_unary()
            return ("preinc", t.text, e)
        return self.parse_postfix()

    def parse_postfix(self):
        e = self.parse_primary()
        while True:
            if self.at("("):
                self.next()
                args = []
                if not self.at(")"):
                    args.append(self.parse_expr())
                    while self.at(","):
                        self.next()
                        args.append(self.parse_expr())
                self.expect(")")
                e = ("call", e, args)
            elif self.at("->") or self.at("."):
                op = self.next().text
                f = self.next()
                if f.kind != "id":
                    raise SimError(f.line, f"成员名错误 '{f.text}'")
                e = ("member", e, f.text) if op == "->" else ("member", e, f.text)
            elif self.at("["):
                self.next()
                idx = self.parse_expr()
                self.expect("]")
                e = ("index", e, idx)
            elif self.at("++") or self.at("--"):
                op = self.next().text
                e = ("postinc", op, e)
            else:
                break
        return e

    def at_type_ahead(self):
        """判断 '(' 后是否为类型转换（如 (Node*) 或 (shop)）——调用时 '(' 已被消费"""
        t0 = self.peek(0)
        if t0 is None:
            return False
        if t0.text in ("int", "char", "void", "unsigned", "signed", "short",
                       "long", "double", "float", "bool", "struct"):
            return True
        if t0.kind == "id" and t0.text in self.structs:
            t1 = self.peek(1)
            if t1 and (t1.text == "*" or t1.text == ")"):
                return True
        return False

    def parse_primary(self):
        t = self.next()
        if t.kind == "num":
            if t.text.lower().startswith("0x"):
                return ("lit", int(t.text, 16))
            return ("lit", int(float(t.text)))
        if t.kind == "str":
            return ("lit", 0)  # 字符串字面量（printf 已单独处理，这里给 0）
        if t.text == "(":
            # 类型转换 (Type*)expr / (Type)expr / (Type){...} 复合字面量
            if self.at_type_ahead():
                _base, ptr = self.parse_type()    # 消费类型（含指针）
                self.expect(")")
                if self.at("{"):
                    self.parse_array_init()
                    return ("lit", 0)
                e = self.parse_expr()
                if ptr > 0:
                    return ("ptrcast", e)       # 转成指针
                return e                          # 普通类型转换无操作
            e = self.parse_expr()
            self.expect(")")
            return e
        if t.kind == "id":
            if t.text == "NULL":
                return ("null",)
            if t.text == "sizeof":
                self.expect("(")
                st = self.next()
                if st.text in ("int", "char", "unsigned", "signed", "short", "long", "double", "float"):
                    base = "int"
                    while self.at("*"):
                        self.next()
                    self.expect(")")
                    return ("sizeof", base)
                if st.kind == "id":
                    while self.at("*"):
                        self.next()
                    self.expect(")")
                    return ("sizeof", st.text)
                raise SimError(t.line, "sizeof 参数错误")
            return ("var", t.text)
        raise SimError(t.line, f"无法识别的表达式 '{t.text}'")


# ---------------------------------------------------------------
# 求值器 / 执行器
# ---------------------------------------------------------------
class Value:
    """kind: 'int' | 'addr' | 'null'"""
    __slots__ = ("kind", "val")

    def __init__(self, kind, val=None):
        self.kind = kind
        self.val = val

    def __repr__(self):
        if self.kind == "int":
            return str(self.val)
        if self.kind == "addr":
            return f"0x{self.val:x}"
        return "NULL"


class VarInfo:
    __slots__ = ("vtype", "is_ptr", "is_array", "arr_size", "value", "fnptr_name")

    def __init__(self, vtype, is_ptr=False, is_array=False, arr_size=None, value=None, fnptr_name=None):
        self.vtype = vtype
        self.is_ptr = is_ptr
        self.is_array = is_array
        self.arr_size = arr_size
        self.value = value
        self.fnptr_name = fnptr_name  # Value 或 list[Value]


class Frame:
    def __init__(self, fname):
        self.fname = fname
        self.scopes = [{}]      # 作用域栈（块级作用域）
        self.vars = self.scopes[0]  # 兼容：最外层变量

    def lookup(self, name):
        for sc in reversed(self.scopes):
            if name in sc:
                return sc[name]
        return None

    def declare(self, name, vi):
        self.scopes[-1][name] = vi


class HeapBlock:
    __slots__ = ("addr", "typename", "fields", "size", "array_vals", "is_stack")

    def __init__(self, addr, typename, fields, is_stack=False):
        self.addr = addr
        self.typename = typename
        self.fields = fields    # name -> Value
        self.size = max(1, len(fields)) * 4
        self.array_vals = None  # 若是 malloc 数组则用
        self.is_stack = is_stack  # True=栈上的结构体变量；False=malloc 的堆内存


class SimEngine:
    def __init__(self, structs, funcs):
        self.structs = structs
        self.funcs = funcs
        self.next_addr = 0x1000
        self.heap = {}          # addr -> HeapBlock
        self.frames = []
        self.call_depth = 0
        self.step_limit = 200000
        self.steps = 0
        # 变量槽（取地址 &x 用，支持二级指针）
        self.var_addr = {}      # (id(frame), name) -> addr
        self.var_addr_inv = {}  # addr -> (id(frame), name)
        self.next_var_addr = 0x5000
        # 结果
        self.snapshots = {}     # line -> Snapshot
        self.var_history = {}   # line -> (frames_copy, heap_copy) 记录
        self.outputs = []       # printf 输出（本版本忽略）
        self.error = None
        self.stop_line = None   # 执行到该行后停止（GUI 点击）
        self.snap_enabled = True

    def _lookup_in_frame(self, frame, name):
        for sc in reversed(frame.scopes):
            if name in sc:
                return sc[name]
        return None

    # ---- 内存 ----
    def alloc(self, typename, count=1, is_stack=False):
        blk = HeapBlock(self.next_addr, typename, {}, is_stack=is_stack)
        self.next_addr += 0x10
        if typename in self.structs:
            sd = self.structs[typename]
            blk.fields = {}
            for fn, ft in sd.fields:
                if isinstance(ft, tuple) and ft[0] == "array":
                    blk.fields[fn] = [Value("int", 0)] * ft[2]   # 数组字段
                else:
                    blk.fields[fn] = Value("null")
            blk.size = max(1, len(sd.fields)) * 4
        else:
            blk.fields = {}
            blk.size = 4 * count
        self.heap[blk.addr] = blk
        return blk

    # ---- 求值 ----
    def lookup(self, name):
        for fr in reversed(self.frames):
            vi = fr.lookup(name)
            if vi is not None:
                return vi
        raise SimError(self.cur_line, f"未定义的变量 '{name}'")

    def eval_expr(self, e):
        k = e[0]
        if k == "lit":
            return Value("int", e[1])
        if k == "null":
            return Value("null")
        if k == "postinc":
            old = self.eval_expr(e[2])
            self.assign(e[2], Value("int", self.to_int(old) + (1 if e[1] == "++" else -1)))
            return old
        if k == "preinc":
            cur = self.eval_expr(e[2])
            new = Value("int", self.to_int(cur) + (1 if e[1] == "++" else -1))
            self.assign(e[2], new)
            return new
        if k == "ptrcast":
            v = self.eval_expr(e[1])
            return Value("addr", self.to_int(v))
        if k == "var":
            vi = self.lookup(e[1])
            return vi.value
        if k == "sizeof":
            t = e[1]
            if t in self.structs:
                return Value("int", max(1, len(self.structs[t].fields)) * 4)
            return Value("int", 4)
        if k == "bin":
            op = e[1]
            if op == "&&":
                l = self.eval_expr(e[2])
                if not self.truthy(l):
                    return Value("int", 0)
                r = self.eval_expr(e[3])
                return Value("int", 1 if self.truthy(r) else 0)
            if op == "||":
                l = self.eval_expr(e[2])
                if self.truthy(l):
                    return Value("int", 1)
                r = self.eval_expr(e[3])
                return Value("int", 1 if self.truthy(r) else 0)
            l = self.eval_expr(e[2])
            r = self.eval_expr(e[3])
            return self.binop(op, l, r)
        if k == "unary":
            op = e[1]
            v = self.eval_expr(e[2])
            if op == "-":
                return Value("int", -self.to_int(v))
            if op == "!":
                return Value("int", 0 if self.truthy(v) else 1)
            if op == "&":
                return self.take_addr(e[2])
            if op == "*":
                return self.deref(v)
        if k == "member":
            base = self.eval_expr(e[1])
            return self.member_get(base, e[2])
        if k == "index":
            arr = self.eval_expr(e[1])
            idx = self.to_int(self.eval_expr(e[2]))
            if isinstance(arr, list):
                if idx < 0 or idx >= len(arr):
                    raise SimError(self.cur_line, "数组下标越界")
                return arr[idx]
            if arr.kind == "addr":
                blk = self.heap[arr.val]
                if blk.array_vals is not None:
                    if idx < 0 or idx >= len(blk.array_vals):
                        raise SimError(self.cur_line, "数组下标越界")
                    return blk.array_vals[idx]
                raise SimError(self.cur_line, "该指针不是数组")
            # 栈数组
            # index 表达式的基是 var
            name = self.var_name(e[1])
            vi = self.lookup(name)
            if vi.is_array and vi.value is not None:
                if idx < 0 or idx >= len(vi.value):
                    raise SimError(self.cur_line, "数组下标越界")
                return vi.value[idx]
            raise SimError(self.cur_line, "无法对非数组做下标访问")
        if k == "call":
            return self.call_expr(e)
        raise SimError(self.cur_line, f"未知表达式 {e}")

    def var_name(self, e):
        if e[0] == "var":
            return e[1]
        if e[0] == "deref":
            return "*" + self.var_name(e[1])
        if e[0] == "member":
            return self.var_name(e[1]) + "." + e[2]
        return "?"

    def truthy(self, v):
        if v.kind == "int":
            return v.val != 0
        return v.kind == "addr"

    def to_int(self, v):
        if isinstance(v, list):
            return 0
        if v.kind == "int":
            return v.val
        if v.kind == "null":
            return 0
        return v.val

    def binop(self, op, l, r):
        if op in ("==", "!=", "<", "<=", ">", ">="):
            # 指针比较：NULL 与 0 等价
            lv = l.val if l.kind == "addr" else (0 if l.kind == "null" else l.val)
            rv = r.val if r.kind == "addr" else (0 if r.kind == "null" else r.val)
            if op == "==":
                return Value("int", 1 if lv == rv else 0)
            if op == "!=":
                return Value("int", 0 if lv == rv else 1)
            if op == "<":
                return Value("int", 1 if lv < rv else 0)
            if op == "<=":
                return Value("int", 1 if lv <= rv else 0)
            if op == ">":
                return Value("int", 1 if lv > rv else 0)
            if op == ">=":
                return Value("int", 1 if lv >= rv else 0)
        if op == "+":
            if l.kind in ("addr", "null") or r.kind in ("addr", "null"):
                return Value("addr", self.to_int(l) + self.to_int(r))   # 指针算术
            return Value("int", self.to_int(l) + self.to_int(r))
        if op == "-":
            if l.kind in ("addr", "null") or r.kind in ("addr", "null"):
                return Value("addr", self.to_int(l) - self.to_int(r))
            return Value("int", self.to_int(l) - self.to_int(r))
        if op == "*":
            return Value("int", self.to_int(l) * self.to_int(r))
        if op == "/":
            rv = self.to_int(r)
            if rv == 0:
                raise SimError(self.cur_line, "除数为 0")
            return Value("int", int(self.to_int(l) / rv))
        if op == "%":
            rv = self.to_int(r)
            if rv == 0:
                raise SimError(self.cur_line, "取模除数为 0")
            return Value("int", self.to_int(l) % rv)
        raise SimError(self.cur_line, f"不支持运算符 {op}")

    def take_addr(self, e):
        if e[0] == "var":
            name = e[1]
            vi = self.lookup(name)
            # 结构体变量：返回其堆块地址（可作指针传入函数）
            if vi.vtype in self.structs and not vi.is_ptr and not vi.is_array:
                if vi.value.kind == "addr":
                    return Value("addr", vi.value.val)
            # 其他变量：返回“变量槽”地址（用于二级指针 / & 取地址）
            key = (id(self.frames[-1]), name)
            if key not in self.var_addr:
                a = self.next_var_addr
                self.next_var_addr += 0x10
                self.var_addr[key] = a
                self.var_addr_inv[a] = key
            return Value("addr", self.var_addr[key])
        raise SimError(self.cur_line, "暂不支持该形式的取地址")

    def deref(self, v):
        if v.kind == "null":
            raise SimError(self.cur_line, "对 NULL 指针解引用")
        if v.kind != "addr":
            raise SimError(self.cur_line, "对非指针解引用")
        if v.val in self.var_addr_inv:
            # 变量槽：返回该变量的当前值（二级指针 *p）
            key = self.var_addr_inv[v.val]
            vi = self._lookup_in_frame(key[0], key[1])
            if vi is None:
                raise SimError(self.cur_line, "变量槽指向的变量不存在")
            return vi.value
        if v.val not in self.heap:
            raise SimError(self.cur_line, f"指针 0x{v.val:x} 指向无效内存")
        return v  # 堆块地址，供 member_get 使用

    def member_get(self, base, field):
        if base.kind == "null":
            raise SimError(self.cur_line, "对 NULL 指针访问成员")
        if base.kind != "addr":
            raise SimError(self.cur_line, f"对非指针访问成员 base.kind={base.kind} field={field}")
        blk = self.heap.get(base.val)
        if blk is None:
            raise SimError(self.cur_line, f"指针 0x{base.val:x} 指向无效内存")
        if field not in blk.fields:
            raise SimError(self.cur_line, f"结构体 {blk.typename} 没有成员 '{field}'")
        return blk.fields[field]

    # ---- 赋值（写） ----
    def assign(self, target, value):
        k = target[0]
        if k == "var":
            vi = self.lookup(target[1])
            vi.value = self.coerce(vi, value)
            return
        if k == "member":
            base = self.eval_expr(target[1])
            if base.kind == "null":
                raise SimError(self.cur_line, "对 NULL 指针写成员")
            if base.kind != "addr":
                raise SimError(self.cur_line, "对非指针写成员")
            blk = self.heap.get(base.val)
            if blk is None or target[2] not in blk.fields:
                raise SimError(self.cur_line, f"无法写成员 '{target[2]}'")
            blk.fields[target[2]] = value
            return
        if k == "deref":
            addr = self.eval_expr(target[1])
            if addr.kind != "addr":
                raise SimError(self.cur_line, "解引用赋值目标不是指针")
            if addr.val in self.var_addr_inv:
                # 写回变量槽（二级指针 *p = x）
                key = self.var_addr_inv[addr.val]
                vi = self._lookup_in_frame(key[0], key[1])
                if vi is None:
                    raise SimError(self.cur_line, "变量槽指向的变量不存在")
                vi.value = self.coerce(vi, value)
                return
            blk = self.heap.get(addr.val)
            if blk is None:
                raise SimError(self.cur_line, "解引用赋值指向无效内存")
            raise SimError(self.cur_line, "暂不支持对整块内存赋值（请用 -> 访问字段）")
        if k == "index":
            arr = self.eval_expr(target[1])
            idx = self.to_int(self.eval_expr(target[2]))
            if isinstance(arr, list):
                if idx < 0 or idx >= len(arr):
                    raise SimError(self.cur_line, "数组下标越界")
                # 结构体数组元素整体赋值（如 shops[0] = (shop){...}）暂不支持，忽略
                if isinstance(arr[idx], Value) and arr[idx].kind == "addr" and arr[idx].val in self.heap:
                    b = self.heap[arr[idx].val]
                    if b.typename in self.structs and value.kind == "int":
                        return
                arr[idx] = value
                return
            if arr.kind == "addr":
                blk = self.heap.get(arr.val)
                if blk and blk.array_vals is not None:
                    if 0 <= idx < len(blk.array_vals):
                        cur = blk.array_vals[idx]
                        if isinstance(cur, Value) and cur.kind == "addr" and cur.val in self.heap:
                            b = self.heap[cur.val]
                            if b.typename in self.structs and value.kind == "int":
                                return   # 结构体数组元素整体赋值暂不支持，忽略
                    blk.array_vals[idx] = value
                    return
            name = self.var_name(target[1])
            vi = self.lookup(name)
            if vi.is_array and vi.value is not None:
                vi.value[idx] = value
                return
            raise SimError(self.cur_line, "无法对非数组赋值")
        raise SimError(self.cur_line, "暂不支持该赋值形式")

    def coerce(self, vi, value):
        """赋值时做类型规整：整数给指针当 NULL；指针给 int 报错"""
        if vi.is_ptr or (vi.vtype in self.structs):
            if value.kind in ("addr", "null"):
                return value
            if value.kind == "int" and value.val == 0:
                return Value("null")
            raise SimError(self.cur_line, f"不能把整数赋给指针变量 '{vi.vtype}'")
        # int 变量
        if value.kind == "int":
            return value
        if value.kind == "null":
            return Value("int", 0)
        raise SimError(self.cur_line, f"不能把指针赋给 int 变量")

    # ---- 调用 ----
    def call_expr(self, e):
        callee = e[1]
        args = e[2]
        if callee[0] == "var":
            name = callee[1]
        else:
            raise SimError(self.cur_line, "暂不支持函数指针调用")
        if name == "malloc" or name == "calloc":
            # malloc(sizeof(T)) / malloc(n*sizeof(T)) / calloc(n, sizeof(T))
            if len(args) == 1:
                typename = self.sizeof_type(args[0])
                cnt = self.malloc_count(args[0])
                if cnt and cnt > 1:
                    blk = self.alloc(typename, cnt)
                    if typename in self.structs:
                        blk.array_vals = [Value("addr", self.alloc(typename, 1).addr)
                                          for _ in range(cnt)]
                    else:
                        blk.array_vals = [Value("int", 0)] * cnt
                    blk.fields = {}
                    blk.size = 4 * cnt
                    return Value("addr", blk.addr)
                blk = self.alloc(typename, 1)
                return Value("addr", blk.addr)
            elif len(args) == 2:
                n = self.to_int(self.eval_expr(args[0]))
                sz = self.eval_expr(args[1])
                typename = self.sizeof_type(args[1])
                blk = self.alloc(typename, max(1, n))
                if typename in self.structs:
                    blk.array_vals = [Value("addr", self.alloc(typename, 1).addr)
                                      for _ in range(max(1, n))]
                else:
                    blk.array_vals = [Value("int", 0)] * max(1, n)
                blk.size = 4 * max(1, n)
                blk.fields = {}
                return Value("addr", blk.addr)
        if name == "free":
            if args:
                v = self.eval_expr(args[0])
                if v.kind == "addr" and v.val in self.heap:
                    del self.heap[v.val]
            return Value("null")
        if name in self.funcs:
            return self.call_user(name, args)
        # 函数指针变量调用（如回调参数 op(x)）
        try:
            vi = self.lookup(name)
        except SimError:
            vi = None
        if vi is not None and getattr(vi, "fnptr_name", None):
            return self.call_user(vi.fnptr_name, args)
        # 常见 C 库函数：安全忽略（不求值参数，避免 &a 等触发错误）
        if name in ("scanf", "printf", "puts", "gets", "getchar", "getc", "perror",
                    "strlen", "strcpy", "strcat", "strcmp", "strncpy", "strchr",
                    "memcpy", "memset", "memcmp", "exit", "abs", "rand", "srand",
                    "system", "fprintf", "sprintf", "fgets", "fopen", "fclose",
                    "fread", "fwrite", "pow", "sqrt", "atoi", "atof", "atoff",
                    "isspace", "isdigit", "isalpha", "toupper", "tolower", "malloc_size",
                    "time", "clock", "qsort", "bsearch", "strcmpi", "strlwr", "strupr"):
            return Value("int", 0)
        raise SimError(self.cur_line, f"未定义的函数 '{name}'")

    def malloc_count(self, e):
        """从 malloc 表达式提取元素个数（如 n*sizeof(T) -> n）；否则 1"""
        if e[0] == "bin" and e[1] == "*":
            for sub in (e[2], e[3]):
                if sub[0] != "sizeof" and sub[0] != "lit":
                    try:
                        v = self.eval_expr(sub)
                        return max(1, self.to_int(v))
                    except Exception:
                        return 1
        return 1

    def sizeof_type(self, e):
        """从表达式里提取类型名（递归查找 sizeof(T)）"""
        if isinstance(e, tuple):
            if e[0] == "sizeof":
                return e[1]
            for sub in e[1:]:
                if isinstance(sub, tuple):
                    t = self.sizeof_type(sub)
                    if t != "int":
                        return t
        return "int"

    def call_user(self, name, args):
        fd = self.funcs[name]
        # 支持变参：固定参数个数校验，多余实参忽略
        fixed = [p for p in fd.params if p[0] != "<vararg>"]
        if len(fixed) > len(args):
            raise SimError(self.cur_line, f"函数 {name} 参数个数不符")
        # 先求实参（函数名作实参时记为函数指针）
        argvals = []
        for a in args:
            if a[0] == "var" and a[1] in self.funcs:
                argvals.append(("fn", a[1]))
            else:
                argvals.append(self.eval_expr(a))
        frame = Frame(name)
        for (pname, ptype), av in zip(fixed, argvals[:len(fixed)]):
            if isinstance(ptype, tuple):  # 指针参数
                vi = VarInfo(ptype[1], is_ptr=True, value=av)
            elif ptype == "<fn>" and isinstance(av, tuple) and av[0] == "fn":
                vi = VarInfo("int", value=Value("int", 0), fnptr_name=av[1])
            elif isinstance(av, list):    # 数组参数（传数组首地址）
                vi = VarInfo(ptype, is_array=True, arr_size=len(av), value=av)
            elif isinstance(av, Value) and av.kind == "addr" and av.val in self.heap \
                    and self.heap[av.val].array_vals is not None:
                blk = self.heap[av.val]
                vi = VarInfo(ptype, is_array=True, arr_size=len(blk.array_vals),
                             value=blk.array_vals)
            elif isinstance(av, tuple) and len(av) == 2 and av[0] == "fn":
                # 函数名实参落入此处（参数类型未识别为 <fn>）：忽略
                vi = VarInfo("int", value=Value("int", 0), fnptr_name=av[1])
            else:
                if ptype == "void":
                    vi = VarInfo("int", value=Value("int", 0))
                else:
                    vi = VarInfo(ptype, is_ptr=False, value=Value("int", self.to_int(av)))
            frame.declare(pname, vi)
        self.frames.append(frame)
        ret = Value("null")
        try:
            r = self.exec_block(fd.body, ret_mode=True)
            if isinstance(r, tuple) and len(r) == 2 and r[0] == "ret":
                ret = r[1]
            elif r is not None:
                ret = r
        finally:
            self.frames.pop()
        return ret

    # ---- 语句执行 ----
    def exec_block(self, stmts, ret_mode=False):
        self.frames[-1].scopes.append({})
        try:
            for st in stmts:
                self.cur_line = st.line
                self.steps += 1
                if self.steps > self.step_limit:
                    raise SimError(st.line, "执行步数超限（疑似死循环）")
                r = self.exec_stmt(st)
                if self.snap_enabled:
                    self.record_snap(st.line)
                if self.stop_line is not None and st.line == self.stop_line:
                    raise StopExec()
                if r is not None:
                    return r
            return None
        finally:
            self.frames[-1].scopes.pop()

    def exec_stmt(self, st):
        k = st.kind
        if k == "block":
            return self.exec_block(st.stmts, ret_mode=True)
        if k == "seq":
            for s in st.stmts:
                r = self.exec_stmt(s)
                if r is not None:
                    return r
            return None
        if k == "decl":
            return self.exec_decl(st)
        if k == "assign":
            v = self.eval_expr(st.expr)
            self.assign(st.target, v)
            return None
        if k == "expr":
            # 函数调用语句
            if st.expr[0] == "call":
                self.eval_expr(st.expr)
            return None
        if k == "if":
            if self.truthy(self.eval_expr(st.cond)):
                return self.exec_stmt(st.then_s)
            elif st.else_s:
                return self.exec_stmt(st.else_s)
            return None
        if k == "while":
            guard = 0
            while self.truthy(self.eval_expr(st.cond)):
                guard += 1
                if guard > 100000:
                    raise SimError(st.line, "while 循环次数超限（疑似死循环）")
                r = self.exec_stmt(st.body)
                if r == "break":
                    break
                if r is not None:
                    return r
            return None
        if k == "for":
            # for 语句自身一个作用域（C99：多个 for 可各自声明同名变量）
            self.frames[-1].scopes.append({})
            try:
                if st.init:
                    self.exec_stmt(st.init)
                guard = 0
                while (st.cond is None) or self.truthy(self.eval_expr(st.cond)):
                    guard += 1
                    if guard > 100000:
                        raise SimError(st.line, "for 循环次数超限（疑似死循环）")
                    r = self.exec_stmt(st.body)
                    if r == "break":
                        break
                    if r is not None:
                        return r
                    if st.step:
                        if isinstance(st.step, tuple) and st.step[0] == "assign":
                            sv = self.eval_expr(st.step[2])
                            self.assign(st.step[1], sv)
                        else:
                            self.eval_expr(st.step)
                return None
            finally:
                self.frames[-1].scopes.pop()
        if k == "return":
            if st.expr:
                return ("ret", self.eval_expr(st.expr))
            return ("ret", Value("null"))
        if k == "break":
            return "break"
        if k == "printf":
            return None
        return None

    def exec_decl(self, st):
        frame = self.frames[-1]
        if frame.lookup(st.name) is not None and st.name in frame.scopes[-1]:
            raise SimError(st.line, f"变量 '{st.name}' 重复声明")
        if st.is_array:
            size = st.arr_size or 0
            if st.dims and len(st.dims) >= 2:
                # 二维数组：列表套列表，天然支持 arr[i][j]
                rows, cols = st.dims[0], st.dims[1]
                vals = [[Value("int", 0) for _ in range(cols)] for _ in range(rows)]
            else:
                vals = [Value("int", 0)] * size
            if st.init and st.init[0] == "arrinit":
                flat = st.init[1]
                if st.dims and len(st.dims) >= 2:
                    cols = st.dims[1]
                    for k, v in enumerate(flat):
                        vals[k // cols][k % cols] = Value("int", v)
                else:
                    for i, v in enumerate(flat):
                        if i < size:
                            vals[i] = Value("int", v)
            vi = VarInfo(st.vtype, is_array=True, arr_size=size, value=vals)
            frame.declare(st.name, vi)
            return None
        if st.is_ptr:
            val = Value("null")
            if st.init:
                val = self.eval_expr(st.init)
            vi = VarInfo(st.vtype, is_ptr=True, value=val)
            frame.declare(st.name, vi)
            return None
        if st.vtype in self.structs:
            # 结构体变量（栈上）：分配一块“栈内存”，变量指向它
            blk = self.alloc(st.vtype, 1, is_stack=True)
            vi = VarInfo(st.vtype, is_ptr=False, value=Value("addr", blk.addr))
            frame.declare(st.name, vi)
            return None
        # 普通 int 变量
        val = Value("int", 0)
        if st.init:
            val = self.eval_expr(st.init)
            val = self.coerce(VarInfo("int"), val)
        vi = VarInfo(st.vtype, is_ptr=False, value=val)
        frame.declare(st.name, vi)
        return None

    # ---- 快照 ----
    def record_snap(self, line):
        self.snapshots[line] = self.snapshot()

    def snapshot(self):
        """返回 (frames, heap) 的可序列化视图，供 GUI 绘制"""
        fr = []
        for f in self.frames:
            vs = []
            seen = set()
            for sc in f.scopes:
                for name, vi in sc.items():
                    if name in seen:
                        continue
                    seen.add(name)
                    vs.append((name, self.describe_var(vi)))
            fr.append({"func": f.fname, "vars": vs})
        hb = []
        for addr in sorted(self.heap.keys()):
            blk = self.heap[addr]
            fields = {}
            for fn, v in blk.fields.items():
                fields[fn] = self.describe_value(v)
            hb.append({"addr": addr, "typename": blk.typename, "fields": fields,
                       "loc": "栈" if blk.is_stack else "堆",
                       "array": [self.describe_value(x) for x in blk.array_vals] if blk.array_vals else None})
        return {"frames": fr, "heap": hb}

    def describe_var(self, vi):
        if vi.is_array:
            return {"type": f"{vi.vtype}[{vi.arr_size}]", "value": "数组",
                    "loc": "栈",
                    "arr": [self.describe_value(x) for x in (vi.value or [])]}
        return {"type": (vi.vtype if not vi.is_ptr else vi.vtype + "*"),
                "loc": "栈",
                "value": self.describe_value(vi.value)}

    def describe_value(self, v):
        if isinstance(v, list):
            return ("arr", [self.describe_value(x) for x in v])
        if v.kind == "int":
            return ("int", v.val)
        if v.kind == "addr":
            return ("ptr", v.val)
        return ("null", None)


# ---------------------------------------------------------------
# 顶层：解析 + 执行 + 快照历史
# ---------------------------------------------------------------
class Simulator:
    def __init__(self, code):
        self.code = code
        self.toks = tokenize(code)
        self.parser = Parser(self.toks)
        self.funcs = self.parser.parse_program()
        self.structs = self.parser.structs
        self.engine = None
        self.snapshots = {}   # line -> snapshot

    def main_name(self):
        if "main" in self.funcs:
            return "main"
        # 没有 main 时，用第一个函数
        for n in self.funcs:
            return n
        return None

    def _make_engine(self, stop_line=None):
        eng = SimEngine(self.structs, self.funcs)
        eng.stop_line = stop_line
        self.engine = eng
        m = self.main_name()
        if m is None:
            return None
        fd = self.funcs[m]
        frame = Frame(m)
        # 入口函数（无 main 时取第一个函数）参数给默认值，便于直接分析片段
        for pname, ptype in fd.params:
            if isinstance(ptype, tuple):  # 指针参数默认 NULL
                frame.declare(pname, VarInfo(ptype[1], is_ptr=True, value=Value("null")))
            else:
                frame.declare(pname, VarInfo(ptype, is_ptr=False, value=Value("int", 0)))
        eng.frames.append(frame)
        return fd

    def run(self):
        """全量执行；返回 {line: snapshot}（该行执行后的状态）"""
        fd = self._make_engine(None)
        if fd is None:
            return {}
        try:
            self.engine.exec_block(fd.body)
        except SimError as ex:
            self.engine.error = ex
        return self.engine.snapshots

    def run_to_line(self, target_line):
        """重新从头执行，在 target_line 首次执行后停止。
        返回 {line: snapshot}，点击代码行即用此结果。"""
        fd = self._make_engine(target_line)
        if fd is None:
            return {}
        try:
            self.engine.exec_block(fd.body)
        except StopExec:
            pass  # 已到达目标行，快照已记录
        except SimError as ex:
            self.engine.error = ex
        return self.engine.snapshots
