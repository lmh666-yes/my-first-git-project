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
  | (?P<num>\d+)
  | (?P<str>"(?:[^"\\]|\\.)*")
  | (?P<char>'[^']')
  | (?P<id>[A-Za-z_]\w*)
  | (?P<op>->|==|!=|<=|>=|&&|\|\||[+\-*/%<>=!&*]|\(|\)|\{|\}|\[|\]|;|,|\.)
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


class DeclStmt(Stmt):
    def __init__(self, line, vtype, name, init_expr, is_ptr, is_array, arr_size):
        super().__init__(line, "decl")
        self.vtype = vtype
        self.name = name
        self.init = init_expr
        self.is_ptr = is_ptr
        self.is_array = is_array
        self.arr_size = arr_size


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
            ftype, is_ptr = self.parse_type()
            while True:
                ft = self.next()
                if ft.kind != "id":
                    raise SimError(ft.line, f"结构体字段名错误 '{ft.text}'")
                # 可能是数组字段
                if self.at("["):
                    self.next()
                    sz = self.next()
                    self.expect("]")
                    # 数组字段简化为 int 字段名
                fields.append((ft.text, ftype if not is_ptr else ("ptr", ftype)))
                if self.at(","):
                    self.next()
                    continue
                break
            self.expect(";")
        self.expect("}")
        return fields

    def parse_type(self):
        """解析一个类型说明，返回 (base_type, is_ptr)。
        支持 int / char / struct Name / 结构体名（typedef 过的）"""
        t = self.next()
        is_ptr = False
        if t.text == "struct":
            nt = self.next()
            if nt.kind != "id":
                raise SimError(nt.line, f"struct 后需要类型名，实际 '{nt.text}'")
            base = nt.text
        elif t.text in ("int", "char", "void", "unsigned", "signed", "short", "long", "double", "float"):
            base = "int" if t.text in ("int", "char", "unsigned", "signed", "short", "long") else "int"
        elif t.kind == "id":
            base = t.text
        else:
            raise SimError(t.line, f"无法识别的类型 '{t.text}'")
        while self.at("*"):
            self.next()
            is_ptr = not is_ptr  # 多级指针简化：仍记指针
        return base, is_ptr

    # ---------- 函数 ----------
    def parse_function(self, funcs):
        ret_t = self.next()
        if ret_t.text == "struct":
            self.next()  # 结构体名
        name_t = self.next()
        if name_t.kind != "id" or name_t.text in funcs:
            raise SimError(name_t.line, f"函数名错误或重复定义 '{name_t.text}'")
        self.expect("(")
        params = []
        if not self.at(")"):
            while True:
                ptype, is_ptr = self.parse_type()
                pt = self.next()
                if pt.kind != "id":
                    raise SimError(pt.line, f"参数名错误 '{pt.text}'")
                params.append((pt.text, ptype if not is_ptr else ("ptr", ptype)))
                if self.at(","):
                    self.next()
                    continue
                break
        self.expect(")")
        body = self.parse_block()
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
            return self.parse_decl()
        # 表达式语句（可能是赋值：expr = expr;）
        expr = self.parse_expr()
        if self.at("="):
            self.next()
            rhs = self.parse_expr()
            self.expect(";")
            return AssignStmt(t.line, expr, rhs)
        self.expect(";")
        return ExprStmt(t.line, expr)

    def parse_simple_stmt_inline(self):
        """for 的 init 或 while 体里的单条语句（不以 {} 开头）"""
        line = self.peek().line
        if self.looks_like_decl():
            return self.parse_decl()
        expr = self.parse_expr()
        if self.at("="):
            self.next()
            rhs = self.parse_expr()
            self.expect(";")
            return AssignStmt(line, expr, rhs)
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
        vtype, is_ptr = self.parse_type()
        is_array = False
        arr_size = None
        # 支持 int a[5];
        nt = self.next()
        if nt.kind != "id":
            raise SimError(nt.line, f"变量名错误 '{nt.text}'")
        name = nt.text
        if self.at("["):
            self.next()
            sz = self.next()
            if sz.kind == "num":
                arr_size = int(sz.text)
            else:
                raise SimError(sz.line, "数组大小必须是整数")
            self.expect("]")
            is_array = True
        init = None
        if self.at("="):
            self.next()
            init = self.parse_expr()
        if semi:
            self.expect(";")
        return DeclStmt(line, vtype, name, init, is_ptr, is_array, arr_size)

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
            else:
                break
        return e

    def parse_primary(self):
        t = self.next()
        if t.kind == "num":
            return ("lit", int(t.text))
        if t.kind == "str":
            return ("lit", 0)  # 字符串字面量（printf 已单独处理，这里给 0）
        if t.text == "(":
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
    __slots__ = ("vtype", "is_ptr", "is_array", "arr_size", "value")

    def __init__(self, vtype, is_ptr=False, is_array=False, arr_size=None, value=None):
        self.vtype = vtype
        self.is_ptr = is_ptr
        self.is_array = is_array
        self.arr_size = arr_size
        self.value = value  # Value 或 list[Value]


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
    __slots__ = ("addr", "typename", "fields", "size", "array_vals")

    def __init__(self, addr, typename, fields):
        self.addr = addr
        self.typename = typename
        self.fields = fields    # name -> Value
        self.size = max(1, len(fields)) * 4
        self.array_vals = None  # 若是 malloc 数组则用


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
        # 结果
        self.snapshots = {}     # line -> Snapshot
        self.var_history = {}   # line -> (frames_copy, heap_copy) 记录
        self.outputs = []       # printf 输出（本版本忽略）
        self.error = None
        self.stop_line = None   # 执行到该行后停止（GUI 点击）
        self.snap_enabled = True

    # ---- 内存 ----
    def alloc(self, typename, count=1):
        blk = HeapBlock(self.next_addr, typename, {})
        self.next_addr += 0x10
        if typename in self.structs:
            sd = self.structs[typename]
            blk.fields = {fn: Value("null") for fn, _ft in sd.fields}
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
            return Value("int", self.to_int(l) + self.to_int(r))
        if op == "-":
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
            vi = self.lookup(e[1])
            if not vi.is_ptr:
                raise SimError(self.cur_line, f"无法对非指针变量 '{e[1]}' 取地址")
            return Value("addr", vi.value.val if vi.value.kind == "addr" else 0)
        raise SimError(self.cur_line, "暂不支持该形式的取地址")

    def deref(self, v):
        if v.kind == "null":
            raise SimError(self.cur_line, "对 NULL 指针解引用")
        if v.kind != "addr":
            raise SimError(self.cur_line, "对非指针解引用")
        if v.val not in self.heap:
            raise SimError(self.cur_line, f"指针 0x{v.val:x} 指向无效内存")
        return v  # 返回地址，供 member_get 使用

    def member_get(self, base, field):
        if base.kind == "null":
            raise SimError(self.cur_line, "对 NULL 指针访问成员")
        if base.kind != "addr":
            raise SimError(self.cur_line, "对非指针访问成员（结构体变量需用 . 访问）")
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
                arr[idx] = value
                return
            if arr.kind == "addr":
                blk = self.heap.get(arr.val)
                if blk and blk.array_vals is not None:
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
            # malloc(sizeof(T)) 或 calloc(n, sizeof(T))
            if len(args) == 1:
                sz = self.eval_expr(args[0])
                typename = self.sizeof_type(args[0])
                blk = self.alloc(typename, 1)
                return Value("addr", blk.addr)
            elif len(args) == 2:
                n = self.to_int(self.eval_expr(args[0]))
                sz = self.eval_expr(args[1])
                typename = self.sizeof_type(args[1])
                blk = self.alloc(typename, max(1, n))
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
        raise SimError(self.cur_line, f"未定义的函数 '{name}'")

    def sizeof_type(self, e):
        """从 sizeof(...) 表达式里提取类型名"""
        if e[0] == "sizeof":
            return e[1]
        return "int"

    def call_user(self, name, args):
        fd = self.funcs[name]
        if len(args) != len(fd.params):
            raise SimError(self.cur_line, f"函数 {name} 参数个数不符")
        # 先求实参
        argvals = []
        for a in args:
            argvals.append(self.eval_expr(a))
        frame = Frame(name)
        for (pname, ptype), av in zip(fd.params, argvals):
            if isinstance(ptype, tuple):  # 指针参数
                vi = VarInfo(ptype[1], is_ptr=True, value=av)
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
            vals = [Value("int", 0)] * size
            if st.init:
                # int a[3] = {1,2,3};
                if st.init[0] == "lit" and st.init[1] == 0:
                    pass
            vi = VarInfo(st.vtype, is_array=True, arr_size=size, value=vals)
            frame.declare(st.name, vi)
            return None
        if st.is_ptr:
            val = Value("null")
            if st.init:
                val = self.eval_expr(st.init)
            vi = VarInfo(st.vtype, is_ptr=True, value=val)
        else:
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
                       "array": [self.describe_value(x) for x in blk.array_vals] if blk.array_vals else None})
        return {"frames": fr, "heap": hb}

    def describe_var(self, vi):
        if vi.is_array:
            return {"type": f"{vi.vtype}[{vi.arr_size}]", "value": "数组",
                    "arr": [self.describe_value(x) for x in (vi.value or [])]}
        return {"type": (vi.vtype if not vi.is_ptr else vi.vtype + "*"),
                "value": self.describe_value(vi.value)}

    def describe_value(self, v):
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
        eng.frames.append(Frame(m))
        return self.funcs[m]

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
