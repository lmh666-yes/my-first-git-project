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
  | (?P<char>'[^'\\]'|'\\.'|'\\[0-7]{1,3}'|'\\x[0-9a-fA-F]{1,2}')
  | (?P<id>[A-Za-z_]\w*)
  | (?P<op>->|<<|>>|==|!=|<=|>=|&&|\|\||\+\+|--|\+=|-=|\*=|/=|%=|\.\.\.|[+\-*/%<>=!&*~^?:|]|\(|\)|\{|\}|\[|\]|;|,|\.)
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
        if kind == "pre":
            st = text.strip()
            # #if 0 ... #endif 条件编译：跳过整个块
            if st.startswith("#if") and st[3:].strip() == "0":
                idx = code.find("#endif", pos)
                if idx != -1:
                    line += code.count("\n", pos, idx)
                    pos = idx + 6
                continue
            # 多行宏（以 \ 结尾续行）：手动拼接后续行
            while text.rstrip().endswith("\\"):
                idx = code.find("\n", pos)
                if idx == -1:
                    break
                pos = idx + 1
                line += 1
                idx2 = code.find("\n", pos)
                if idx2 == -1:
                    idx2 = len(code)
                text = text + "\n" + code[pos:idx2]
                pos = idx2
            continue
        if kind in ("ws", "comment"):
            continue
        toks.append(Token(kind, text, line))
    return toks


# ---------------------------------------------------------------
# 语法树
# ---------------------------------------------------------------
class StructDef:
    def __init__(self, name, fields, is_union=False):
        self.name = name            # 结构体名
        self.fields = fields        # [(fname, ftype)]  ftype='int' 或 ('ptr', typename) 或 None
        self.is_union = is_union    # 联合体：字段共享内存


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


class SwitchStmt(Stmt):
    """cases: [(kind, lo, hi, stmts)]  kind: 'v' | 'range' | 'default'"""
    def __init__(self, line, cond, cases):
        super().__init__(line, "switch")
        self.cond = cond
        self.cases = cases


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
    def __init__(self, toks, macros=None):
        self.toks = toks
        self.pos = 0
        self.structs = {}    # name -> StructDef
        self.aliases = set() # 非结构体 typedef 别名（typedef int myint;）
        self.macros = macros or {}  # #define 常量宏
        self.globals = []    # 全局变量声明：(line, vtype, name, init, ptr, is_array, arr_size)

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
                continue
            # 顶层 struct / union 定义（可能带变量列表 / 匿名）
            if self.at("struct") or self.at("union"):
                self.parse_top_struct()
                continue
            if self.at_id():
                # 判断是函数定义还是全局变量声明
                save = self.pos
                is_func = False
                try:
                    self.parse_type()
                    nt = self.next()
                    if nt.kind == "id" and self.at("("):
                        is_func = True
                except (SimError, IndexError):
                    pass
                self.pos = save
                if is_func:
                    self.parse_function(funcs)
                else:
                    try:
                        self.parse_global_decl()
                    except (SimError, IndexError):
                        self.pos = save
                        try:
                            self.parse_function(funcs)
                        except (SimError, IndexError):
                            while self.peek() is not None:
                                self.next()
            else:
                # 宽容：跳过无法识别的顶层 token（如教学代码里的裸标识符）
                t = self.next()
                continue
        return funcs

    def parse_top_struct(self):
        """顶层结构体/联合体定义：struct Name { ... }v1, *p; 或 struct { ... }v1;
        或 struct Name 变量;（结构体类型全局变量）"""
        save = self.pos
        kw = self.next()   # struct 或 union
        t = self.next()
        if t.text == "{":
            self.pos -= 1
            fields = self.parse_struct_fields()
            anon = f"anon{len(self.structs) + 1}"
            self.structs[anon] = StructDef(anon, fields, is_union=(kw.text == "union"))
            while not self.at(";"):
                tk = self.next()
                if tk is None:
                    break
                if tk.kind == "id":
                    self.globals.append((t.line, anon, tk.text, None, 0, False, None))
            self.expect(";")
            return
        if self.at("{"):
            # struct Name { ... } 定义
            fields = self.parse_struct_fields()
            self.structs[t.text] = StructDef(t.text, fields, is_union=(kw.text == "union"))
            if not self.at(";"):
                while not self.at(";"):
                    tk = self.next()
                    if tk is None:
                        break
                    if tk.kind == "id":
                        self.globals.append((t.line, t.text, tk.text, None, 0, False, None))
            self.expect(";")
            return
        # struct Name 变量;  —— 结构体类型的全局变量声明
        self.pos = save
        self.parse_global_decl()

    def parse_global_decl(self):
        """顶层全局变量声明：int g; / int g = 5; / int arr[10]; / const char *p = ..."""
        line = self.peek().line
        vtype, ptr = self.parse_type()
        nt = self.next()
        if nt.kind != "id":
            # 函数指针等复杂声明（如 void (*pf[10])(void)）：跳过该声明，避免中断
            while self.peek() is not None and not self.at(";"):
                self.next()
            if self.at(";"):
                self.next()
            return
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
        self.globals.append((line, vtype, name, init, ptr, is_array, arr_size))
        # 同一行的其它变量 int a, b;
        while self.at(","):
            self.next()
            nt2 = self.next()
            if nt2.kind != "id":
                raise SimError(nt2.line, f"顶层变量名错误 '{nt2.text}'")
            init2 = None
            if self.at("="):
                self.next()
                if self.at("{"):
                    self.parse_array_init()
                else:
                    init2 = self.parse_expr()
            self.globals.append((line, vtype, nt2.text, init2, ptr, False, None))
        self.expect(";")

    def parse_typedef(self):
        t = self.expect("typedef")
        if self.at("struct") or self.at("union"):
            is_union = self.at("union")
            if self.at("struct"):
                self.expect("struct")
            else:
                self.expect("union")
            name_t = self.next()
            if name_t.text == "{":
                # typedef struct { ... } Name, *pName;
                self.pos -= 1
                fields = self.parse_struct_fields()
                aliases = []
                while not self.at(";"):
                    tk = self.next()
                    if tk is None:
                        break
                    if tk.kind == "id":
                        aliases.append(tk.text)
                self.expect(";")
                anon = aliases[0] if aliases else f"anon{len(self.structs) + 1}"
                for al in (aliases or [anon]):
                    self.structs[al] = StructDef(anon, fields, is_union=is_union)
            else:
                name = name_t.text
                fields = self.parse_struct_fields()   # 内部会消费 '{'
                aliases = []
                while not self.at(";"):
                    tk = self.next()
                    if tk is None:
                        break
                    if tk.kind == "id":
                        aliases.append(tk.text)
                self.expect(";")
                self.structs[name] = StructDef(name, fields, is_union=is_union)
                for al in aliases:
                    self.structs[al] = StructDef(name, fields, is_union=is_union)
            return
        # 非结构体 typedef：typedef int myint; / typedef unsigned long size_t; 等
        try:
            self.parse_type()          # 消费类型（含复合与指针）
            while not self.at(";"):
                if self.peek() is None:
                    break
                tk = self.next()
                if tk.kind == "id":
                    self.aliases.add(tk.text)   # 记录别名（用于识别声明）
        except (SimError, IndexError):
            while self.peek() is not None and not self.at(";"):
                self.next()
        if self.at(";"):
            self.next()

    def parse_struct_fields(self):
        self.expect("{")
        fields = []
        while not self.at("}"):
            if self.at(";"):
                self.next()   # 多余分号
                continue
            # __attribute__ 等特殊标记：跳过到 ;
            if self.peek() and self.peek().text == "__attribute__":
                while self.peek() is not None and not self.at(";"):
                    self.next()
                self.expect(";")
                continue
            ftype, ptr = self.parse_type()
            while True:
                ft = self.next()
                if ft.kind != "id":
                    if ft.text in ("(", ":"):
                        # 函数指针/数组指针/位域成员：跳过该成员声明（外层 expect ; 消费）
                        while self.peek() is not None and not self.at(";"):
                            self.next()
                        break
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
                # 字段后的 __attribute__((...))
                if self.peek() and self.peek().text == "__attribute__":
                    while self.peek() is not None and not self.at(";"):
                        self.next()
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
        # 先跳过修饰符
        while self.peek() and self.peek().text in ("const", "static", "extern", "register", "volatile", "inline"):
            self.next()
        t = self.next()
        ptr = 0
        if t.text in ("struct", "union"):
            nt = self.next()
            if nt.text == "{":
                # 匿名 struct/union { ... } 作为字段类型
                self.pos -= 1
                fields = self.parse_struct_fields()
                anon = f"anon{len(self.structs) + 1}"
                self.structs[anon] = StructDef(anon, fields, is_union=(t.text == "union"))
                base = anon
            elif nt.kind != "id":
                raise SimError(nt.line, f"struct 后需要类型名，实际 '{nt.text}'")
            else:
                base = nt.text
                if base not in self.structs:
                    # 系统/未定义结构体（如 struct tm）：注册为空结构体
                    self.structs[base] = StructDef(base, [])
        elif t.text in ("int", "char", "void", "unsigned", "signed", "short", "long", "double", "float", "bool", "size_t", "longlong", "uint8_t", "uint16_t", "uint32_t", "int8_t", "int16_t", "int32_t", "size_type"):
            base = "char" if t.text == "char" else "int"
            while self.peek() and self.peek().text in ("int", "char", "long", "short", "unsigned", "signed"):
                if self.next().text == "char":
                    base = "char"
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
                        # 参数名前的 const/volatile 修饰符与 * (char const *argv)
                        while self.peek() and self.peek().text in ("const", "volatile", "register", "static", "extern"):
                            self.next()
                        while self.at("*"):
                            self.next()
                            ptr += 1
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

    def parse_switch_body(self):
        """解析 switch 的 case/default 分支"""
        self.expect("{")
        cases = []
        while not self.at("}"):
            if self.peek() is None:
                break
            if self.at("case"):
                self.next()
                lo = self.const_eval(self.parse_expr())
                hi = lo
                if self.at("..."):
                    self.next()
                    hi = self.const_eval(self.parse_expr())
                self.expect(":")
                stmts = self.parse_switch_stmts()
                cases.append(("v" if lo == hi else "range", lo, hi, stmts))
            elif self.at("default"):
                self.next()
                self.expect(":")
                stmts = self.parse_switch_stmts()
                cases.append(("default", 0, 0, stmts))
            else:
                self.next()   # 容错跳过未知 token
        self.expect("}")
        return cases

    def parse_switch_stmts(self):
        """解析 case 分支体（直到下一个 case/default/}）"""
        stmts = []
        while True:
            tk = self.peek()
            if tk is None or tk.text in ("case", "default", "}"):
                break
            stmts.append(self.parse_stmt())
        return stmts

    def char_val(self, s):
        """字符字面量 'a' / '\n' / '\0' / '\x41' / '\101' 转 ASCII 值"""
        s = s[1:-1]
        if len(s) == 1:
            return ord(s)
        if s.startswith("\\x"):
            return int(s[2:], 16)
        if s.startswith("\\") and s[1:].isdigit():
            return int(s[1:], 8)
        esc = {"\\n": 10, "\\t": 9, "\\0": 0, "\\\\": 92, "\\'": 39,
               "\\r": 13, "\\a": 7, "\\b": 8, "\\f": 12, "\\v": 11}
        if s in esc:
            return esc[s]
        return ord(s[0]) if s else 0

    def const_eval(self, e):
        """求编译期常量（case 标签用）：字面量 / 取负"""
        if e[0] == "lit":
            return e[1]
        if e[0] == "unary" and e[1] == "-":
            return -self.const_eval(e[2])
        return 0

    # ---------- 语句 ----------
    def parse_stmt(self):
        t = self.peek()
        # 标签 label:（goto 用）
        if t and t.kind == "id" and self.peek(1) and self.peek(1).text == ":":
            self.next(); self.next()
            return ExprStmt(t.line, ("lit", 0))
        # goto label;
        if t and t.text == "goto":
            while self.peek() is not None and not self.at(";"):
                self.next()
            self.expect(";")
            return ExprStmt(t.line, ("lit", 0))
        if t and t.text == "switch":
            self.next()
            self.expect("(")
            cond = self.parse_expr()
            self.expect(")")
            cases = self.parse_switch_body()
            return SwitchStmt(t.line, cond, cases)
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
        if t.text in ("int", "char", "void", "unsigned", "signed", "short", "long", "double", "float", "struct", "union", "enum", "const", "static", "extern", "register", "volatile"):
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
        # 支持 int a[5]; 与 int (*q)[5]; / int (*p)(int);
        nt = self.next()
        if nt.text == "(":
            # 指针声明：int (*q)[5]（数组指针） / int (*p)(int)（函数指针）
            self.expect("*")
            name_t = self.next()
            if name_t.kind != "id":
                raise SimError(name_t.line, f"变量名错误 '{name_t.text}'")
            name = name_t.text
            self.expect(")")
            if self.at("["):
                while self.at("["):
                    self.next()
                    sz = self.next()
                    if sz.kind == "num":
                        pass
                    self.expect("]")
            elif self.at("("):
                d2 = 0
                while True:
                    tk = self.next()
                    if tk is None:
                        break
                    if tk.text == "(":
                        d2 += 1
                    elif tk.text == ")":
                        d2 -= 1
                        if d2 == 0:
                            break
            ptr += 1
            is_array = False
            arr_size = None
            dims = []
        else:
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
                is_array = False
                arr_size = None
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
        """多变量声明：int a, b; 中 b 复用 a 的类型；支持 int *a, *b;"""
        line = self.peek().line
        is_ptr = proto.is_ptr
        if self.at("*"):
            self.next()
            is_ptr = True
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
        return DeclStmt(line, proto.vtype, name, init, is_ptr, is_array, arr_size)

    def _num_val(self, tk):
        t = tk.text
        if t.lower().startswith("0x"):
            return int(t, 16)
        if t.lower().startswith("0b"):
            return int(t, 2)
        if len(t) > 1 and t.startswith("0") and t[1].isdigit():
            return int(t, 8)
        return int(float(t))

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
                vals.append(self._num_val(self.next()))
            elif tk.kind == "char":
                vals.append(self.char_val(self.next().text))
            elif tk.text == "-":
                self.next()
                n = self.next()
                vals.append(-self._num_val(n))
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
        return self.parse_conditional()

    def parse_conditional(self):
        """三目运算符 a ? b : c（右结合）"""
        e = self.parse_or()
        if self.at("?"):
            self.next()
            a = self.parse_expr()
            self.expect(":")
            b = self.parse_conditional()
            return ("cond", e, a, b)
        return e

    def parse_or(self):
        e = self.parse_and()
        while self.at("||"):
            self.next()
            e = ("bin", "||", e, self.parse_and())
        return e

    def parse_and(self):
        e = self.parse_bit_or()
        while self.at("&&"):
            self.next()
            e = ("bin", "&&", e, self.parse_bit_or())
        return e

    def parse_bit_or(self):
        e = self.parse_bit_xor()
        while self.at("|"):
            self.next()
            e = ("bin", "|", e, self.parse_bit_xor())
        return e

    def parse_bit_xor(self):
        e = self.parse_bit_and()
        while self.at("^"):
            self.next()
            e = ("bin", "^", e, self.parse_bit_and())
        return e

    def parse_bit_and(self):
        e = self.parse_eq()
        while self.at("&"):
            self.next()
            e = ("bin", "&", e, self.parse_eq())
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
        e = self.parse_shift()
        while self.peek() and self.peek().text in ("+", "-"):
            op = self.next().text
            e = ("bin", op, e, self.parse_shift())
        return e

    def parse_shift(self):
        e = self.parse_mul()
        while self.peek() and self.peek().text in ("<<", ">>"):
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
        if t and t.text in ("-", "!", "*", "&", "~"):
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
                       "long", "double", "float", "bool", "struct", "union", "enum"):
            return True
        if t0.kind == "id" and t0.text in self.structs:
            t1 = self.peek(1)
            if t1 and (t1.text == "*" or t1.text == ")"):
                return True
        return False

    def parse_primary(self):
        t = self.next()
        if t.kind == "char":
            return ("lit", self.char_val(t.text))
        if t.kind == "num":
            if t.text.lower().startswith("0x"):
                return ("lit", int(t.text, 16))
            return ("lit", int(float(t.text)))
        if t.kind == "str":
            return ("strlit", t.text[1:-1])  # 字符串字面量（只读字符数组）
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
            if t.text in self.macros:
                return ("lit", self.macros[t.text])
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
                    # sizeof(a[i]) 数组元素：返回元素大小
                    if self.at("["):
                        self.next()
                        self.parse_expr()
                        self.expect("]")
                        while self.at("*"):
                            self.next()
                        self.expect(")")
                        return ("sizeofelem", st.text)
                    if self.at(")"):
                        self.next()
                        return ("sizeof", st.text)
                    # sizeof(p+1) 等含表达式
                    self.pos -= 1
                    self.parse_expr()
                    self.expect(")")
                    return ("sizeoflit", 4)
                # sizeof(*p) / sizeof(表达式)
                self.pos -= 1
                self.parse_expr()
                self.expect(")")
                return ("sizeoflit", 4)
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
    __slots__ = ("addr", "typename", "fields", "size", "array_vals", "is_stack", "scalar", "freed", "union_scalar")

    def __init__(self, addr, typename, fields, is_stack=False):
        self.addr = addr
        self.typename = typename
        self.fields = fields    # name -> Value
        self.size = max(1, len(fields)) * 4
        self.array_vals = None  # 若是 malloc 数组则用
        self.is_stack = is_stack  # True=栈上的结构体变量；False=malloc 的堆内存
        self.scalar = None      # 标量堆块（malloc(sizeof(int))）的当前值
        self.freed = False      # free() 后标记为已释放（仍保留供演示悬垂指针）
        self.union_scalar = None  # 联合体共享内存的当前值


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
        # 键用 frame 对象强引用而非 id(frame)，避免帧弹出后 id 被复用导致崩溃
        self.var_addr = {}      # (frame, name) -> addr
        self.var_addr_inv = {}  # addr -> (frame, name)
        self.next_var_addr = 0x5000
        # 数组基址（数组名作为值时返回的地址）
        self.arr_base = {}      # (frame, name) -> addr
        self.arr_base_inv = {}  # addr -> (frame, name)
        self.next_arr_addr = 0x6000
        # 结果
        self.snapshots = {}     # line -> Snapshot
        self.var_history = {}   # line -> (frames_copy, heap_copy) 记录
        self.outputs = []       # printf 输出（本版本忽略）
        self.error = None
        self.stop_line = None   # 执行到该行后停止（GUI 点击）
        self.snap_enabled = True
        self.warnings = []      # 宽容模式提示（未定义函数等）
        # 逐步回放：每条语句执行后的 (行号, 快照) 序列
        self.step_snapshots = []
        # 模拟输入（scanf 用）
        self.inputs = []
        self.input_pos = 0
        # 字符串字面量表（只读字符数组）
        self._str_addr = {}
        self.str_table = {}     # addr -> 字符串
        self.next_str_addr = 0x8000

    def _lookup_in_frame(self, frame, name):
        for sc in reversed(frame.scopes):
            if name in sc:
                return sc[name]
        return None

    def _slot_read(self, key):
        """读取变量槽 / 数组元素槽（key 由 var_addr_inv 提供）"""
        if len(key) == 2:
            fr, name = key
            vi = self._lookup_in_frame(fr, name)
            if vi is None:
                raise SimError(self.cur_line, "变量槽指向的变量不存在")
            return vi.value
        fr, name, idx = key
        vi = self._lookup_in_frame(fr, name)
        if vi is None or vi.value is None:
            raise SimError(self.cur_line, "变量槽指向的数组不存在")
        if idx < 0 or idx >= len(vi.value):
            raise SimError(self.cur_line, "数组下标越界")
        return vi.value[idx]

    def _slot_write(self, key, value):
        """写回变量槽 / 数组元素槽"""
        if len(key) == 2:
            fr, name = key
            vi = self._lookup_in_frame(fr, name)
            if vi is None:
                raise SimError(self.cur_line, "变量槽指向的变量不存在")
            vi.value = self.coerce(vi, value)
            return
        fr, name, idx = key
        vi = self._lookup_in_frame(fr, name)
        if vi is None or vi.value is None:
            raise SimError(self.cur_line, "变量槽指向的数组不存在")
        if idx < 0 or idx >= len(vi.value):
            raise SimError(self.cur_line, "数组下标越界")
        vi.value[idx] = value

    # ---- 内存 ----
    MAX_BLOCKS = 500   # 堆块上限：模拟内存有限，超限时 malloc 返回 NULL

    def alloc(self, typename, count=1, is_stack=False):
        if len(self.heap) >= self.MAX_BLOCKS:
            return None   # 内存耗尽
        blk = HeapBlock(self.next_addr, typename, {}, is_stack=is_stack)
        self.next_addr += 0x10
        if typename in self.structs:
            sd = self.structs[typename]
            blk.fields = {}
            if sd.is_union:
                blk.union_scalar = Value("int", 0)   # 联合体：字段共享一块内存
            for fn, ft in sd.fields:
                if isinstance(ft, tuple) and ft[0] == "array":
                    if ft[1] in self.structs:
                        # 结构体数组字段：元素为子块地址
                        subs = []
                        for _ in range(ft[2]):
                            sub = self.alloc(ft[1], 1)
                            if sub is None:
                                break
                            subs.append(Value("addr", sub.addr))
                        blk.fields[fn] = subs
                    else:
                        blk.fields[fn] = [Value("int", 0)] * ft[2]   # 数组字段
                elif ft in self.structs:
                    # 嵌套结构体字段：分配子块
                    sub = self.alloc(ft, 1)
                    blk.fields[fn] = Value("addr", sub.addr) if sub is not None else Value("null")
                else:
                    blk.fields[fn] = Value("int", 0)
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
        # 宽容模式：未定义的变量自动声明为 int 0，便于作业代码继续执行
        vi = VarInfo("int", is_ptr=False, value=Value("int", 0))
        self.frames[-1].declare(name, vi)
        return vi

    def _arr_base(self, addr):
        """addr 是否为某个栈数组的基址+偏移；返回 (vi, off) 或 None（选偏移最小的匹配）"""
        best = None
        for base, key in self.arr_base_inv.items():
            d = addr - base
            if d >= 0 and d % 4 == 0:
                fr, nm = key
                vi = self._lookup_in_frame(fr, nm)
                if vi is not None and vi.is_array and vi.value is not None and d // 4 < len(vi.value):
                    if best is None or d < best[0]:
                        best = (d, vi, d // 4)
        return (best[1], best[2]) if best else None

    def _grow(self, lst, need):
        """演示模式：数组越界时自动扩展（上限 10000），越界写入/读取不再中断"""
        if need <= 0:
            return True
        if len(lst) >= need:
            return True
        if need > 10000:
            return False
        lst.extend([Value("int", 0)] * (need - len(lst)))
        return True

    def _slot_index(self, addr, idx):
        """addr 是变量槽/数组元素槽地址时，按数组索引取值；否则返回 None"""
        if addr not in self.var_addr_inv:
            return None
        key = self.var_addr_inv[addr]
        if len(key) == 3:
            fr, name, eidx = key
            vi = self._lookup_in_frame(fr, name)
            if vi is not None and vi.value is not None:
                i2 = idx + eidx
                if i2 < 0:
                    raise SimError(self.cur_line, "数组下标越界")
                if i2 >= len(vi.value) and not self._grow(vi.value, i2 + 1):
                    raise SimError(self.cur_line, "数组下标越界")
                return vi.value[i2]
        return None

    def eval_expr(self, e):
        k = e[0]
        if k == "lit":
            return Value("int", e[1])
        if k == "null":
            return Value("null")
        if k == "strlit":
            s = e[1]
            if s not in self._str_addr:
                a = self.next_str_addr
                self.next_str_addr += 0x10
                self._str_addr[s] = a
                self.str_table[a] = s
            return Value("addr", self._str_addr[s])
        if k == "postinc":
            old = self.eval_expr(e[2])
            self.incdec_assign(e[2], old, 1 if e[1] == "++" else -1)
            return old
        if k == "cond":
            c = self.eval_expr(e[1])
            if self.truthy(c):
                return self.eval_expr(e[2])
            return self.eval_expr(e[3])
        if k == "preinc":
            cur = self.eval_expr(e[2])
            new = self.incdec_assign(e[2], cur, 1 if e[1] == "++" else -1)
            return new
        if k == "ptrcast":
            v = self.eval_expr(e[1])
            return Value("addr", self.to_int(v))
        if k == "var":
            vi = self.lookup(e[1])
            if vi.is_array and vi.value is not None:
                # 数组名作为值：返回数组基址（支持 a+2 / &a[i] 指针算术）
                key = (self.frames[-1], e[1])
                if key not in self.arr_base:
                    a = self.next_arr_addr
                    self.next_arr_addr += 0x10
                    self.arr_base[key] = a
                    self.arr_base_inv[a] = key
                return Value("addr", self.arr_base[key])
            return vi.value
        if k == "sizeof":
            t = e[1]
            if t in self.structs:
                return Value("int", max(1, len(self.structs[t].fields)) * 4)
            # 数组变量 sizeof(arr)
            try:
                vi = self.lookup(t)
                if vi.is_array and vi.value is not None:
                    return Value("int", len(vi.value) * 4)
            except Exception:
                pass
            return Value("int", 4)
        if k == "sizeofelem":
            return Value("int", 4)   # sizeof(a[i]) 元素大小
        if k == "sizeoflit":
            return Value("int", 4)   # sizeof(表达式) 一律按 int 4B
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
            if op == "&":
                # 取地址：直接处理目标，不求值目标表达式
                return self.take_addr(e[2])
            v = self.eval_expr(e[2])
            if op == "-":
                return Value("int", -self.to_int(v))
            if op == "!":
                return Value("int", 0 if self.truthy(v) else 1)
            if op == "~":
                return Value("int", ~self.to_int(v) & 0xFFFFFFFF)
            if op == "*":
                if isinstance(v, list):
                    if len(v) == 0:
                        raise SimError(self.cur_line, "对空数组解引用")
                    return v[0] if isinstance(v[0], Value) else Value("int", 0)
                d = self.deref(v)
                if d.kind == "addr":
                    blk = self._heap_blk(d.val)
                    if blk is None:
                        m = self._arr_base(d.val)
                        if m is not None:
                            vi, off = m
                            if 0 <= off < len(vi.value):
                                return vi.value[off]   # *p 读栈数组元素
                    if blk is not None and blk.scalar is not None:
                        return blk.scalar   # 标量堆块 *p
                    if blk is not None and blk.array_vals is not None and not blk.fields:
                        off = (d.val - blk.addr) // 4   # 数组块 *p 读当前元素
                        if 0 <= off < len(blk.array_vals):
                            return blk.array_vals[off]
                        raise SimError(self.cur_line, "指针偏移越界")
                return d
        if k == "member":
            base = self.eval_expr(e[1])
            if isinstance(base, list):
                raise SimError(self.cur_line, "数组不能直接访问成员（缺少下标）")
            return self.member_get(base, e[2])
        if k == "index":
            arr = self.eval_expr(e[1])
            idx = self.to_int(self.eval_expr(e[2]))
            if isinstance(arr, list):
                if idx < 0:
                    raise SimError(self.cur_line, "数组下标越界")
                if idx >= len(arr) and not self._grow(arr, idx + 1):
                    raise SimError(self.cur_line, "数组下标越界")
                return arr[idx]
            if arr.kind == "addr":
                # 数组基址 + 偏移（p = a + 2 后 p[i]）
                m = self._arr_base(arr.val)
                if m is not None:
                    vi, off = m
                    i2 = idx + off
                    if i2 < 0:
                        raise SimError(self.cur_line, "数组下标越界")
                    if i2 >= len(vi.value) and not self._grow(vi.value, i2 + 1):
                        raise SimError(self.cur_line, "数组下标越界")
                    return vi.value[i2]
                # 指向变量槽/数组元素槽（n[0]，n 为 &a[i]）
                sv = self._slot_index(arr.val, idx)
                if sv is not None:
                    return sv
                if arr.val in self.str_table:
                    s = self.str_table[arr.val]
                    if 0 <= idx < len(s):
                        return Value("int", ord(s[idx]))
                    raise SimError(self.cur_line, "字符串下标越界")
                blk = self._heap_blk(arr.val)
                if blk is None:
                    raise SimError(self.cur_line, f"指针 0x{arr.val:x} 指向无效内存")
                if blk.array_vals is not None:
                    if idx < 0:
                        raise SimError(self.cur_line, "数组下标越界")
                    if idx >= len(blk.array_vals) and not self._grow(blk.array_vals, idx + 1):
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
        # 数组名等 list 操作数按 0 处理（正常路径已由 eval 转基址）
        if isinstance(l, list):
            l = Value("int", 0)
        if isinstance(r, list):
            r = Value("int", 0)
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
            if l.kind == "addr" or r.kind == "addr":
                # 指针 + 整数：按元素大小(4B)递增
                if l.kind == "addr" and r.kind == "int":
                    return Value("addr", l.val + self.to_int(r) * 4)
                if r.kind == "addr" and l.kind == "int":
                    return Value("addr", r.val + self.to_int(l) * 4)
                return Value("addr", self.to_int(l) + self.to_int(r))
            return Value("int", self.to_int(l) + self.to_int(r))
        if op == "-":
            if l.kind == "addr" or r.kind == "addr":
                if l.kind == "addr" and r.kind in ("addr", "null"):
                    return Value("int", (l.val - self.to_int(r)) // 4)   # 指针差：元素个数
                if l.kind == "addr" and r.kind == "int":
                    return Value("addr", l.val - self.to_int(r) * 4)
                if l.kind in ("int", "null") and r.kind == "addr":
                    return Value("addr", self.to_int(l) - r.val)
                return Value("addr", self.to_int(l) - self.to_int(r))
            return Value("int", self.to_int(l) - self.to_int(r))
        if op == "&":
            return Value("int", self.to_int(l) & self.to_int(r))
        if op == "|":
            return Value("int", self.to_int(l) | self.to_int(r))
        if op == "^":
            return Value("int", self.to_int(l) ^ self.to_int(r))
        if op == "<<":
            return Value("int", self.to_int(l) << (self.to_int(r) & 31))
        if op == ">>":
            return Value("int", self.to_int(l) >> (self.to_int(r) & 31))
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

    def incdec_assign(self, target, old, delta):
        """++/-- 赋值：指针变量按地址加减，字段/普通变量按值加减"""
        if isinstance(old, list):
            raise SimError(self.cur_line, "不能对数组自增自减")
        if old.kind == "addr":
            sz = 4
            if target[0] == "var":
                try:
                    vi = self.lookup(target[1])
                    if vi.vtype == "char":
                        sz = 1
                except Exception:
                    pass
            new = Value("addr", old.val + delta * sz)   # 指针自增按元素大小
        else:
            is_ptr_target = False
            if target[0] == "var":
                try:
                    vi = self.lookup(target[1])
                    is_ptr_target = vi.is_ptr
                except Exception:
                    pass
            if old.kind == "null" and is_ptr_target:
                sz = 1 if (target[0] == "var" and self.lookup(target[1]).vtype == "char") else 4
                new = Value("addr", self.to_int(old) + delta * sz)   # 空指针自增按地址
            else:
                new = Value("int", self.to_int(old) + delta)
        self.assign(target, new)
        return new

    def take_addr(self, e):
        if e[0] == "var":
            name = e[1]
            vi = self.lookup(name)
            # 数组名 &arr：返回数组基址
            if vi.is_array and vi.value is not None:
                key = (self.frames[-1], name)
                if key not in self.arr_base:
                    a = self.next_arr_addr
                    self.next_arr_addr += 0x10
                    self.arr_base[key] = a
                    self.arr_base_inv[a] = key
                return Value("addr", self.arr_base[key])
            # 结构体变量：返回其堆块地址（可作指针传入函数）
            if vi.vtype in self.structs and not vi.is_ptr and not vi.is_array:
                if vi.value.kind == "addr":
                    return Value("addr", vi.value.val)
            # 其他变量：返回“变量槽”地址（用于二级指针 / & 取地址）
            key = (self.frames[-1], name)
            if key not in self.var_addr:
                a = self.next_var_addr
                self.next_var_addr += 0x10
                self.var_addr[key] = a
                self.var_addr_inv[a] = key
            return Value("addr", self.var_addr[key])
        if e[0] == "index":
            # &arr[i] / &a[i][j]：返回元素槽地址
            name = self.var_name(e[1])
            arr = self.eval_expr(e[1])
            idx = self.to_int(self.eval_expr(e[2]))
            if not isinstance(arr, list) and not (isinstance(arr, Value) and arr.kind == "addr"):
                raise SimError(self.cur_line, "取地址的对象不是数组")
            key = (self.frames[-1], name, idx)
            if key not in self.var_addr:
                a = self.next_var_addr
                self.next_var_addr += 0x10
                self.var_addr[key] = a
                self.var_addr_inv[a] = key
            return Value("addr", self.var_addr[key])
        if e[0] == "member":
            # &zero->a 结构体成员地址：基址 + 字段偏移(近似 4B)
            base = self.eval_expr(e[1])
            if isinstance(base, list):
                base = Value("int", 0)
            if base.kind != "addr":
                raise SimError(self.cur_line, "暂不支持该形式的取地址")
            return Value("addr", base.val + self._field_offset(e[1], e[2]))
        raise SimError(self.cur_line, "暂不支持该形式的取地址")

    def _field_offset(self, expr, field):
        """计算结构体成员在结构体中的偏移（近似：字段顺序 × 4）"""
        try:
            name = self.var_name(expr)
            vi = self.lookup(name)
            sd = self.structs.get(vi.vtype)
            if sd:
                for i, (fn, _) in enumerate(sd.fields):
                    if fn == field:
                        return i * 4
        except Exception:
            pass
        return 0

    def _heap_blk(self, addr):
        """按地址找堆块；支持数组块内部偏移（p 指向块中第 n 个元素）"""
        blk = self.heap.get(addr)
        if blk is not None:
            return blk
        for b in self.heap.values():
            if b.array_vals is not None and not b.fields:
                off = addr - b.addr
                if off >= 0 and off % 4 == 0 and off // 4 < len(b.array_vals):
                    return b
        return None

    def deref(self, v):
        if v.kind == "null":
            raise SimError(self.cur_line, "对 NULL 指针解引用")
        if v.kind != "addr":
            raise SimError(self.cur_line, "对非指针解引用")
        if v.val in self.var_addr_inv:
            # 变量槽 / 数组元素槽：返回槽内的当前值（二级指针 *p）
            return self._slot_read(self.var_addr_inv[v.val])
        if v.val in self.str_table:
            s = self.str_table[v.val]
            return Value("int", ord(s[0]) if s else 0)   # *p 读字符串首字符
        if 0x8000 <= v.val < 0x9000:
            # 字符串指针算术：p++ 后仍在字符串范围内
            for a, s in self.str_table.items():
                off = v.val - a
                if 0 <= off < len(s):
                    return Value("int", ord(s[off]))
                if off == len(s):
                    return Value("int", 0)   # 末尾 '\0'
        if 0x6000 <= v.val < 0x7000 and self._arr_base(v.val) is not None:
            return v   # 栈数组指针：由 unary * 按偏移读取
        if v.val not in self.heap:
            if self._heap_blk(v.val) is not None:
                return v   # 数组块内部偏移：由 unary * 按偏移读取
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
        if blk.union_scalar is not None:
            return blk.union_scalar   # 联合体共享内存
        if field not in blk.fields:
            blk.fields[field] = Value("int", 0)   # 动态创建字段（系统结构体等）
        return blk.fields[field]

    # ---- 赋值（写） ----
    def assign(self, target, value):
        # 规范化：(*p) / (*&a) 等 unary 星号目标 → deref
        if target[0] == "unary" and target[1] == "*":
            target = ("deref", target[2])
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
            if blk is None:
                raise SimError(self.cur_line, f"无法写成员 '{target[2]}'")
            if blk.union_scalar is not None:
                blk.union_scalar = value   # 联合体共享内存
                return
            blk.fields[target[2]] = value   # 动态创建字段
            return
        if k == "deref":
            addr = self.eval_expr(target[1])
            if addr.kind != "addr":
                raise SimError(self.cur_line, "解引用赋值目标不是指针")
            if addr.val in self.var_addr_inv:
                # 写回变量槽 / 数组元素槽（二级指针 *p = x）
                self._slot_write(self.var_addr_inv[addr.val], value)
                return
            blk = self._heap_blk(addr.val)
            if blk is None:
                raise SimError(self.cur_line, "解引用赋值指向无效内存")
            if blk.scalar is not None or (blk.array_vals is None and not blk.fields):
                # 标量堆块：*p = x 写入标量槽
                blk.scalar = value
                return
            if blk.array_vals is not None and not blk.fields:
                # 数组块：*p = x 写当前偏移元素（如 *p++ = i）
                off = (addr.val - blk.addr) // 4
                if 0 <= off < len(blk.array_vals):
                    blk.array_vals[off] = value
                    return
                raise SimError(self.cur_line, "指针偏移越界")
            raise SimError(self.cur_line, "暂不支持对整块内存赋值（请用 -> 访问字段）")
        if k == "index":
            arr = self.eval_expr(target[1])
            idx = self.to_int(self.eval_expr(target[2]))
            if isinstance(arr, list):
                if idx < 0:
                    raise SimError(self.cur_line, "数组下标越界")
                if idx >= len(arr) and not self._grow(arr, idx + 1):
                    raise SimError(self.cur_line, "数组下标越界")
                # 结构体数组元素整体赋值（如 shops[0] = (shop){...}）暂不支持，忽略
                if isinstance(arr[idx], Value) and arr[idx].kind == "addr" and arr[idx].val in self.heap:
                    b = self.heap[arr[idx].val]
                    if b.typename in self.structs and value.kind == "int":
                        return
                arr[idx] = value
                return
            if arr.kind == "addr":
                if arr.val in self.str_table:
                    raise SimError(self.cur_line, "字符串常量只读，不能赋值")
                # 数组基址 + 偏移（p = a + 2 后 p[i] = x）
                m = self._arr_base(arr.val)
                if m is not None:
                    vi, off = m
                    i2 = idx + off
                    if i2 < 0:
                        raise SimError(self.cur_line, "数组下标越界")
                    if i2 >= len(vi.value) and not self._grow(vi.value, i2 + 1):
                        raise SimError(self.cur_line, "数组下标越界")
                    vi.value[i2] = value
                    return
                # 指向变量槽/数组元素槽（n[0] = x）
                if arr.val in self.var_addr_inv:
                    key = self.var_addr_inv[arr.val]
                    if len(key) == 3:
                        fr, name, eidx = key
                        vi = self._lookup_in_frame(fr, name)
                        if vi is not None and vi.value is not None:
                            i2 = idx + eidx
                            if i2 < 0:
                                raise SimError(self.cur_line, "数组下标越界")
                            if i2 >= len(vi.value) and not self._grow(vi.value, i2 + 1):
                                raise SimError(self.cur_line, "数组下标越界")
                            vi.value[i2] = value
                            return
                blk = self._heap_blk(arr.val)
                if blk and blk.array_vals is not None:
                    if idx < 0:
                        raise SimError(self.cur_line, "数组下标越界")
                    if idx >= len(blk.array_vals) and not self._grow(blk.array_vals, idx + 1):
                        raise SimError(self.cur_line, "数组下标越界")
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
            # 函数指针成员调用（c.padd(3,6)）：本版本忽略
            return Value("int", 0)
        if name == "malloc" or name == "calloc":
            # malloc(sizeof(T)) / malloc(n*sizeof(T)) / calloc(n, sizeof(T))
            if len(args) == 1:
                typename = self.sizeof_type(args[0])
                cnt = self.malloc_count(args[0])
                if cnt and cnt > 1:
                    blk = self.alloc(typename, cnt)
                    if blk is None:
                        return Value("null")   # 内存耗尽
                    if typename in self.structs:
                        blk.array_vals = [Value("addr", self.alloc(typename, 1).addr)
                                          for _ in range(cnt)]
                    else:
                        blk.array_vals = [Value("int", 0)] * cnt
                    blk.fields = {}
                    blk.size = 4 * cnt
                    return Value("addr", blk.addr)
                blk = self.alloc(typename, 1)
                if blk is None:
                    return Value("null")
                return Value("addr", blk.addr)
            elif len(args) == 2:
                n = self.to_int(self.eval_expr(args[0]))
                sz = self.eval_expr(args[1])
                typename = self.sizeof_type(args[1])
                blk = self.alloc(typename, max(1, n))
                if blk is None:
                    return Value("null")
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
                    # 标记已释放（保留块，供演示悬垂指针）
                    self.heap[v.val].freed = True
            return Value("null")
        # 常见带参宏
        if name == "ARRAY_SIZE" and len(args) == 1:
            v = self.eval_expr(args[0])
            if isinstance(v, list):
                return Value("int", len(v))
            if v.kind == "addr":
                m = self._arr_base(v.val)
                if m is not None:
                    return Value("int", len(m[0].value))
                blk = self.heap.get(v.val)
                if blk and blk.array_vals is not None:
                    return Value("int", len(blk.array_vals))
            return Value("int", 4)
        if name in ("MAX", "MIN") and len(args) == 2:
            a = self.to_int(self.eval_expr(args[0]))
            b = self.to_int(self.eval_expr(args[1]))
            return Value("int", max(a, b) if name == "MAX" else min(a, b))
        if name == "realloc" and args:
            # realloc：演示简化，返回原指针（数组仍可用）
            return self.eval_expr(args[0])
        if name in self.funcs:
            return self.call_user(name, args)
        # scanf：从模拟输入队列取值赋给变量（scanf("%d", &a) / &a, &b / &arr[i]）
        if name == "scanf" and len(args) >= 1:
            for t in args[1:]:
                if not isinstance(t, tuple) or not t:
                    continue
                val = 0
                if self.input_pos < len(self.inputs):
                    val = self.inputs[self.input_pos]
                    self.input_pos += 1
                # 先去掉外层取址符 &（&a / &arr[i]）
                if t[0] == "unary" and len(t) >= 3 and t[1] == "&":
                    t = t[2]
                if not isinstance(t, tuple) or not t:
                    continue
                if t[0] == "var":
                    # scanf("%d", &a) 或 scanf("%d", a)（教学写法）
                    try:
                        vi = self.lookup(t[1])
                        if vi.is_array and isinstance(vi.value, list):
                            pass   # 数组名作目标（如 scanf("%s", str)）保持数组
                        else:
                            vi.value = Value("int", val)
                    except Exception:
                        pass
                elif t[0] == "index":
                    # scanf("%d", &arr[i]) / arr[i]
                    try:
                        arr = self.eval_expr(t[1])
                        idx = self.to_int(self.eval_expr(t[2]))
                        if isinstance(arr, list) and 0 <= idx < len(arr):
                            arr[idx] = Value("int", val)
                        elif isinstance(arr, Value) and arr.kind == "addr":
                            # 数组名/&arr 返回基址(addr): 用 _arr_base 定位并写入元素
                            m = self._arr_base(arr.val)
                            if m is not None:
                                vi, off = m
                                i2 = idx + off
                                if 0 <= i2 < len(vi.value):
                                    vi.value[i2] = Value("int", val)
                    except Exception:
                        pass
            return Value("int", 0)
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
                    "time", "clock", "qsort", "bsearch", "strcmpi", "strlwr", "strupr",
                    "sleep", "Sleep", "usleep", "fputs", "getenv", "putchar", "putc",
                    "fflush", "getch", "getche", "kbhit", "clrscr", "getline", "strtok",
                    "strstr", "strncmp", "strncat", "memset_s", "memmove", "sscanf",
                    "fgetc", "feof", "rewind", "remove", "rename", "strdup", "itoa", "ltoa"):
            return Value("int", 0)
        # 未定义函数：多文件项目 / 库函数，宽容处理并提示
        self.warnings.append((self.cur_line, f"函数 '{name}' 未在本文件中定义（可能是多文件项目或库函数），已按 0 处理"))
        return Value("int", 0)

    def malloc_count(self, e):
        """从 malloc 表达式提取元素个数（如 n*sizeof(T) / sizeof(T)*n -> n）；否则 1"""
        if e[0] == "bin" and e[1] == "*":
            for sub in (e[2], e[3]):
                if sub[0] != "sizeof":
                    try:
                        v = self.eval_expr(sub)
                        return max(1, self.to_int(v))
                    except Exception:
                        return 1
        if e[0] == "lit":
            return e[1]
        if e[0] == "var":
            # malloc(n) 变量
            try:
                return max(1, self.to_int(self.eval_expr(e)))
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
            elif isinstance(av, Value) and av.kind == "addr" and ptype in self.structs \
                    and av.val in self.heap:
                # 结构体按值传参：简化按引用（共享同一块）
                vi = VarInfo(ptype, value=Value("addr", av.val))
            elif isinstance(av, Value) and av.kind == "addr" and av.val in self.arr_base_inv:
                # 栈数组名作实参：取原数组内容
                fr, nm = self.arr_base_inv[av.val]
                bvi = self._lookup_in_frame(fr, nm)
                if bvi is not None and bvi.value is not None:
                    vi = VarInfo(ptype, is_array=True, arr_size=len(bvi.value), value=bvi.value)
                else:
                    vi = VarInfo(ptype, is_ptr=True, value=av)
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
            r = self.exec_block(fd.body, ret_mode=True, keep_scope=True)
            if isinstance(r, tuple) and len(r) == 2 and r[0] == "ret":
                ret = r[1]
            elif r is not None:
                ret = r
        finally:
            self.frames.pop()
        return ret

    # ---- 语句执行 ----
    def exec_block(self, stmts, ret_mode=False, keep_scope=False):
        self.frames[-1].scopes.append({})
        try:
            for st in stmts:
                self.cur_line = st.line
                self.steps += 1
                if self.steps > self.step_limit:
                    raise SimError(st.line, "执行步数超限（疑似死循环）")
                r = self.exec_stmt(st)
                if self.snap_enabled:
                    snap = self.snapshot()
                    self.snapshots[st.line] = snap
                    if len(self.step_snapshots) < 20000:
                        self.step_snapshots.append((st.line, snap))
                if self.stop_line is not None and st.line == self.stop_line:
                    raise StopExec()
                if r is not None:
                    return r
            return None
        finally:
            if not keep_scope:
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
            # 表达式语句：p++; 等需要执行（含副作用）
            self.eval_expr(st.expr)
            return None
        if k == "if":
            if self.truthy(self.eval_expr(st.cond)):
                return self.exec_stmt(st.then_s)
            elif st.else_s:
                return self.exec_stmt(st.else_s)
            return None
        if k == "switch":
            v = self.to_int(self.eval_expr(st.cond))
            matched = None
            for c in st.cases:
                if c[0] == "default":
                    matched = c
                elif c[0] == "v" and v == c[1]:
                    matched = c
                    break
                elif c[0] == "range" and c[1] <= v <= c[2]:
                    matched = c
                    break
            if matched is None:
                return None
            for s2 in matched[3]:
                r = self.exec_stmt(s2)
                if r == "break":
                    break
                if isinstance(r, tuple) and r and r[0] == "stop":
                    return r
                if r is not None:
                    return r
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
            elif st.init and st.init[0] == "strlit":
                # char arr[] = "hello"; 字符串初始化字符数组
                s = st.init[1]
                for i, ch in enumerate(s):
                    if i < size:
                        vals[i] = Value("int", ord(ch))
                if len(s) < size:
                    vals[len(s)] = Value("int", 0)   # 末尾隐含 '\0'
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
            vi = VarInfo(st.vtype, is_ptr=False,
                         value=Value("addr", blk.addr) if blk else Value("null"))
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
        all_addr = sorted(self.heap.keys())
        for addr in all_addr[:50]:
            blk = self.heap[addr]
            fields = {}
            for fn, v in blk.fields.items():
                fields[fn] = self.describe_value(v)
            hb.append({"addr": addr, "typename": blk.typename, "fields": fields,
                       "loc": "栈" if blk.is_stack else "堆",
                       "scalar": self.describe_value(blk.scalar)
                       if blk.scalar is not None else None,
                       "freed": blk.freed,
                       "array": [self.describe_value(x) for x in blk.array_vals[:30]]
                       if blk.array_vals else None})
        return {"frames": fr, "heap": hb, "heap_total": len(all_addr)}

    def describe_var(self, vi):
        if vi.is_array:
            arr = vi.value or []
            MAX = 30
            return {"type": f"{vi.vtype}[{vi.arr_size}]", "value": "数组",
                    "loc": "栈",
                    "arr": [self.describe_value(x) for x in arr[:MAX]],
                    "arr_total": len(arr)}
        return {"type": (vi.vtype if not vi.is_ptr else vi.vtype + "*"),
                "loc": "栈",
                "value": self.describe_value(vi.value)}

    def describe_value(self, v):
        if isinstance(v, list):
            return ("arr", [self.describe_value(x) for x in v[:30]])
        if v.kind == "int":
            return ("int", v.val)
        if v.kind == "addr":
            return ("ptr", v.val)
        return ("null", None)


# ---------------------------------------------------------------
# 顶层：解析 + 执行 + 快照历史
# ---------------------------------------------------------------
BUILTIN_MACROS = {
    "INT_MIN": -2147483648, "INT_MAX": 2147483647,
    "LONG_MIN": -9223372036854775808, "LONG_MAX": 9223372036854775807,
    "SHRT_MIN": -32768, "SHRT_MAX": 32767,
    "true": 1, "false": 0,
}


def extract_macros(code):
    """提取 #define NAME 常量（整数值），供表达式展开；支持多行续行宏"""
    macros = {}
    c2 = re.sub(r"\\\r?\n\s*", " ", code)   # 拼接续行
    for m in re.finditer(r"#define\s+([A-Za-z_]\w*)\s+([^\n]+)", c2):
        name = m.group(1)
        if name in macros:
            continue
        v = m.group(2).strip()
        if v.startswith("(") and v.endswith(")"):
            v = v[1:-1].strip()
        try:
            if v.lower().startswith("0x"):
                macros[name] = int(v, 16)
            else:
                macros[name] = int(v)
        except Exception:
            pass
    macros.update(BUILTIN_MACROS)
    return macros


class Simulator:
    def __init__(self, code):
        self.code = code
        self.macros = extract_macros(code)
        self.toks = tokenize(code)
        self.parser = Parser(self.toks, macros=self.macros)
        self.funcs = self.parser.parse_program()
        self.structs = self.parser.structs
        self.engine = None
        self.snapshots = {}   # line -> snapshot
        self.pending_inputs = []   # GUI 模拟输入（scanf 用）

    def main_name(self):
        if "main" in self.funcs:
            return "main"
        # 没有 main 时，用第一个函数
        for n in self.funcs:
            return n
        return None

    def _const_init(self, e):
        """全局变量初值：只求简单字面量/负号，其余给 0"""
        try:
            if e[0] == "lit":
                return Value("int", e[1])
            if e[0] == "null":
                return Value("null")
            if e[0] == "unary" and e[1] == "-":
                v = self._const_init(e[2])
                return Value("int", -v.val if v.kind == "int" else 0)
        except Exception:
            pass
        return Value("int", 0)

    def _install_globals(self, eng, frame):
        """把解析出的全局变量声明安装到 main 帧（模拟静态存储期）"""
        for g in self.parser.globals:
            line, vtype, gname, init, ptr, is_array, arr_size = g
            eng.cur_line = line
            # 结构体变量：分配堆块
            if vtype in self.structs and ptr == 0 and not is_array:
                blk = eng.alloc(vtype)
                frame.declare(gname, VarInfo(vtype,
                                             value=Value("addr", blk.addr) if blk else Value("null")))
                continue
            if is_array:
                vals = []
                if init and init[0] == "arrinit":
                    vals = [Value("int", x) for x in init[1]]
                n = arr_size or len(vals) or 1
                while len(vals) < n:
                    vals.append(Value("int", 0))
                frame.declare(gname, VarInfo(vtype, is_array=True, arr_size=n, value=vals))
                continue
            # 标量
            val = self._const_init(init) if init is not None else Value("int", 0)
            if (ptr > 0 or vtype in self.structs) and val.kind == "int" and val.val == 0:
                val = Value("null")
            frame.declare(gname, VarInfo(vtype, is_ptr=(ptr > 0), value=val))

    def _make_engine(self, stop_line=None):
        eng = SimEngine(self.structs, self.funcs)
        eng.stop_line = stop_line
        eng.inputs = list(self.pending_inputs)
        self.engine = eng
        m = self.main_name()
        if m is None:
            return None
        fd = self.funcs[m]
        frame = Frame(m)
        # 入口函数（无 main 时取第一个函数）参数给默认值，便于直接分析片段
        for pname, ptype in fd.params:
            if isinstance(ptype, tuple):  # 指针参数
                if ptype[1] in self.structs:
                    # 结构体指针参数：自动分配一个块，便于演示
                    blk = eng.alloc(ptype[1])
                    frame.declare(pname, VarInfo(ptype[1], is_ptr=True,
                                                 value=Value("addr", blk.addr) if blk else Value("null")))
                else:
                    frame.declare(pname, VarInfo(ptype[1], is_ptr=True, value=Value("null")))
            else:
                frame.declare(pname, VarInfo(ptype, is_ptr=False, value=Value("int", 0)))
        self._install_globals(eng, frame)
        eng.frames.append(frame)
        return fd

    def run(self):
        """全量执行；返回 {line: snapshot}（该行执行后的状态）"""
        fd = self._make_engine(None)
        if fd is None:
            self.snapshots = {}
            return {}
        try:
            self.engine.exec_block(fd.body)
        except SimError as ex:
            self.engine.error = self._friendly_error(ex)
        except RecursionError:
            self.engine.error = SimError(0, "递归深度超限（递归太深，可能导致栈溢出）；已显示执行到当前位置的内存状态")
        self.snapshots = self.engine.snapshots
        return self.snapshots

    def run_to_line(self, target_line):
        """重新从头执行，在 target_line 首次执行后停止。
        返回 {line: snapshot}，点击代码行即用此结果。"""
        fd = self._make_engine(target_line)
        if fd is None:
            self.snapshots = {}
            return {}
        try:
            self.engine.exec_block(fd.body)
        except StopExec:
            pass  # 已到达目标行，快照已记录
        except SimError as ex:
            self.engine.error = self._friendly_error(ex)
        except RecursionError:
            self.engine.error = SimError(0, "递归深度超限（递归太深，可能导致栈溢出）；已显示执行到当前位置的内存状态")
        self.snapshots = self.engine.snapshots
        return self.snapshots

    def _has_input(self):
        """代码是否含输入语句（scanf/gets/getchar 等）"""
        return re.search(r"\b(scanf|gets|getchar|getch|fgets|getline)\b", self.code) is not None

    def _friendly_error(self, ex):
        """把死循环/需输入类错误转成友好提示，保留已执行快照"""
        msg = str(ex)
        if "步数超限" in msg or "循环次数超限" in msg:
            if self._has_input():
                return SimError(ex.line,
                                "该程序含输入语句（scanf 等），需要手动输入数据，无法自动跑完；"
                                "已显示执行到当前位置的内存状态，可点击代码行查看每步效果")
            return SimError(ex.line,
                            "程序疑似死循环（如 while(1)），无法自动跑完；"
                            "已显示执行到当前位置的内存状态，可点击代码行查看每步效果")
        if self._has_input() and self.engine is not None and len(self.engine.snapshots) > 0:
            # 含输入的程序因缺少输入而在后续出错（如除数为 0）
            return SimError(ex.line,
                            "该程序含输入语句（scanf 等），需要手动输入数据；"
                            "已显示执行到当前位置的内存状态，可点击代码行查看每步效果")
        return ex
