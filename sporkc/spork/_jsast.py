# -*- coding: utf-8 -*-
from __future__ import absolute_import

from functools import partial
from functional import compose
from collections import Iterable

from .internal import Singleton

EXPR_TYPE_NUM = 'num'
EXPR_TYPE_BOOL = 'bool'
EXPR_TYPE_STR = 'str'
BUILTIN_VAR = '$b'

class Ast(object): 
    ''' Base class of all javascript ast '''
    def __init__(self):
        self.lineno = -1

    _fields = ()

    def set_location(self, pyline):
        self.lineno = pyline
        return self

    def __str__(self):
        from StringIO import StringIO
        from ._jsvisitors import Render
        output = StringIO()
        Render(output).visit(self)
        return output.getvalue()

    def __repr__(self):
        return '<' + self.__class__.__name__ + ' ' + str(self) + '>'

class Expr(Ast): 
    ''' Base class of all Expr ast '''

    _expr_type = None
    precedence = 0
    def _get_expr_type(self):
        return self._expr_type

    @property
    def expr_type(self):
        ''' If an expression can not determined, returns None'''
        return self._get_expr_type()

    @expr_type.setter
    def expr_type(self, value):
        self._expr_type = value

class Literal(Ast): 
    ''' Literal class also derived from Literal 

    Literal: such as Str, Num, Undefined, True, False
    '''

class Num(Expr, Literal):
    def __init__(self, num):
        super(Num, self).__init__()
        self.n = num

    def _get_expr_type(self):
        return EXPR_TYPE_NUM

def _safe_js_id(name, jskeywords=frozenset([
    'const', 'delete', 'do', 'export', 'function', 'instanceOf',
    'label', 'let', 'new', 'switch', 'this', 'throw', 'catch',
    'typeof', 'var', 'void', 'default', 'super',
    # although name is not keyword, but name is predefined property of
    # Function class. and all *python* object is *function*. 
    # assign to name property in javascript, javascript just ignored.
    'name', 
    ])):
    if name in jskeywords:
        return '$%s$' % name
    return name

class Name(Expr):
    def __init__(self, name):
        super(Name, self).__init__()
        self.id = _safe_js_id(name)

class Str(Expr, Literal):
    def __init__(self, string):
        super(Str, self).__init__()
        self.s = string

    def _get_expr_type(self):
        return EXPR_TYPE_STR

class Attribute(Expr):
    precedence = 1
    def __init__(self, value, attr):
        super(Attribute, self).__init__()
        self.value = value
        self.attr = _safe_js_id(attr)

    _fields = ('value',)

    def _get_expr_type(self):
        # assume all javascript .length attribute returns a num
        if self.attr == 'length':
            return EXPR_TYPE_NUM
        if self.attr == '__name__':
            return EXPR_TYPE_STR

class Undefined(Singleton, Expr, Literal): pass
class Null(Singleton, Expr, Literal): pass
class This(Singleton, Expr, Literal): pass
class SrcMap(Singleton, Expr): pass

class True_(Singleton, Expr, Literal):
    def _get_expr_type(self):
        return EXPR_TYPE_BOOL

class False_(Singleton, Expr, Literal):
    def _get_expr_type(self):
        return EXPR_TYPE_BOOL

class Array(Expr):
    def __init__(self, elms = ()):
        super(Array, self).__init__()
        self.elms = elms

    _fields = ('elms',)

class Expr_stat(Ast):
    def __init__(self, expr):
        super(Expr_stat, self).__init__()
        self.expr = expr
        self.lineno = expr.lineno

    _fields = ('expr',)

class Delete_stat(Ast):
    def __init__(self, expr):
        super(Delete_stat, self).__init__()
        self.expr = expr

    _fields = ('expr', )

class Binexpr(Expr):
    def __init__(self, op, left, right):
        super(Binexpr, self).__init__()
        self.left, self.right = left, right
        self.op = op
        if op in ['%', '/', '*']:
            self.precedence = 3
        elif op in ['+', '-']:
            self.precedence = 4
        elif op in ['<<', '>>', '>>>']:
            self.precedence = 5
        elif op in ['>', '<', '>=', '<=']:
            self.precedence = 6
        elif op in  ['==', '!=', '===', '!==']:
            self.precedence = 7
        elif op == '&':
            self.precedence = 8
        elif op == '^':
            self.precedence = 9
        elif op == '|':
            self.precedence = 10
        elif op == '&&':
            self.precedence = 11
        elif op == '||':
            self.precedence = 12
        elif op in ['=', '+=', '-=', '/=', '*=', '%=']:
            self.precedence = 14

    _fields = ('left', 'right')

    def _get_expr_type(self):
        if self.op in ['==', '===', '!=', '!==', '>=', '>', '<', '<=']:
            return EXPR_TYPE_BOOL

        expr_left, expr_right = self.left.expr_type, self.right.expr_type
        if expr_left == expr_right:
            if self.op in ['&&', '||']:
                return expr_left

            if expr_left == EXPR_TYPE_STR:
                return expr_left if self.op == '+' else None

            if self.op in ['&', '|', '^', '>>', '>>>', '<<']:
                return expr_left if expr_left == EXPR_TYPE_NUM else None
            return expr_left

Plus = partial(Binexpr, '+')
Sub = partial(Binexpr, '-')
Mul = partial(Binexpr, '*')
Div = partial(Binexpr, '/')
Mod = partial(Binexpr, '%')

Eq = partial(Binexpr, '==')
Identical = partial(Binexpr, '===')
Ne = partial(Binexpr, '!=')
Not_identical = partial(Binexpr, '!==')
Ge = partial(Binexpr, '>=')
Gt = partial(Binexpr, '>')
Lt = partial(Binexpr, '<')
Le = partial(Binexpr, '<=')

Logic_and = partial(Binexpr, '&&')
Logic_or = partial(Binexpr, '||')

Bit_and = partial(Binexpr, '&')
Bit_or = partial(Binexpr, '|')
Bit_xor = partial(Binexpr, '^')
Bit_rshift = partial(Binexpr, '>>')
Bit_rshift_zero_fill = partial(Binexpr, '>>>')
Bit_lshift = partial(Binexpr, '<<')

class Unary_expr(Expr):
    precedence = 2
    def __init__(self, op, expr):
        super(Unary_expr, self).__init__()
        self.expr = expr
        self.op = op

    _fields = ('expr',)

    def _get_expr_type(self):
        if self.op == '!':
            return EXPR_TYPE_BOOL

        if self.expr.expr_type == EXPR_TYPE_NUM:
            if self.op in ('-', '+', '++', '--', '~'):
                return EXPR_TYPE_NUM

Unary_neg = partial(Unary_expr, '-')
Unary_add = partial(Unary_expr, '+')
Inc_prefix = partial(Unary_expr, '++')
Dec_prefix = partial(Unary_expr, '--')
Typeof = partial(Unary_expr, 'typeof ')

Logic_not = partial(Unary_expr, '!')

Bit_inv = partial(Unary_expr, '~')

class Unary_postfix_expr(Expr):
    precedence = 2
    def __init__(self, op, expr):
        super(Unary_postfix_expr, self).__init__()
        self.expr = expr
        self.op = op

    _fields = ('expr',)

    def _get_expr_type(self):
        if self.expr.expr_type == EXPR_TYPE_NUM:
            return EXPR_TYPE_NUM

Inc_postfix = partial(Unary_postfix_expr, '++')
Dec_postfix = partial(Unary_postfix_expr, '--')

class Conditional_op(Expr):
    precedence = 13
    def __init__(self, value, first, second):
        super(Conditional_op, self).__init__()
        self.value = value
        self.first, self.second = first, second

    _fields = ('value', 'first', 'second')

    def _get_expr_type(self):
        t = self.first.expr_type
        if t == self.second.expr_type:
            return t

class Assign_expr(Binexpr):
    def _get_expr_type(self):
        if self.op == '=':
            return self.right.expr_type
        else:
            return self.left.expr_type

Assign = partial(Assign_expr, '=')
Plus_assign = partial(Assign_expr, '+=')
Sub_assign = partial(Assign_expr, '-=')
Mul_assign = partial(Assign_expr, '*=')
Div_assign = partial(Assign_expr, '/=')
Mod_assign = partial(Assign_expr, '%=')
Rshift_assign = partial(Assign_expr, '>>=')
Rshift_zero_fill_assign = partial(Assign_expr, '>>>=')
Lshift_assign = partial(Assign_expr, '<<=')
Bit_or_assign = partial(Assign_expr, '|=')
Bit_and_assign = partial(Assign_expr, '&=')
Bit_xor_assign = partial(Assign_expr, '^=')
AssignStat = compose(Expr_stat, Assign)

class If(Ast):
    def __init__(self, value, first, second):
        super(If, self).__init__()
        self.value = value
        self.first, self.second = first, second

    _fields = ('value', 'first', 'second')

class For(Ast):
    def __init__(self, init, cond, inc, stats):
        super(For, self).__init__()
        self.init, self.cond = init, cond
        self.inc, self.stats = inc, stats

    _fields = ('init', 'cond', 'inc', 'stats')

class For_in(Ast):
    def __init__(self, name, expr, stats):
        super(For_in, self).__init__()
        self.expr, self.stats = expr, stats
        self.name = DeclareVar(name)

    _fields = ('expr', 'stats')

class While(Ast):
    def __init__(self, cond, stats):
        super(While, self).__init__()
        self.cond, self.stats = cond, stats

    _fields = ('cond', 'stats')

class Empty(Ast):
    precedence = 0

noneast = Empty()

class DeclareVar(Ast):
    def __init__(self, name, value=None):
        super(DeclareVar, self).__init__()
        self.name = _safe_js_id(name)
        self.value = value

    _fields = ('value',)

class DeclareMultiVar(Ast):
    def __init__(self, names):
        super(DeclareMultiVar, self).__init__()
        self.names = tuple(_safe_js_id(x) for x in names)

    _fields = ('names',)

Declare_var_stat = compose(Expr_stat, DeclareVar)

class File(Ast):
    def __init__(self, stats):
        super(File, self).__init__()
        self.stats = stats

    _fields = ('stats',)

class CallBase(Expr):
    precedence = 1
    def __init__(self, val, args):
        super(CallBase, self).__init__()
        self.val, self.args = val, args

    _fields = ('val', 'args')

class New_object(CallBase):
    pass

def as_global_func_call(expr):
    if isinstance(expr, Call) and isinstance(expr.val, Attribute) and\
            _is_builtin(expr.val.value):
        return expr.val.attr

def _is_builtin(expr):
    return isinstance(expr, Name) and expr.id == BUILTIN_VAR

BOOL_GLOBAL_FUNCS = {'bool', 'hasattr', 'isinstance', 'eq',
    '__gt', '__ge', '__lt', '__le', 'isString', 'isIteratable'}

class Call(CallBase):
    def _get_expr_type(self):

        def resolve_builtin_func(func_name):
            if func_name in ['len', 'int']:
                return EXPR_TYPE_NUM

            if func_name in ['str', 'repr']:
                return EXPR_TYPE_STR

            if func_name in BOOL_GLOBAL_FUNCS:
                return EXPR_TYPE_BOOL

        # assume .toString() always return str
        if isinstance(self.val, Attribute):
            attr = self.val.attr
            if _is_builtin(self.val.value):
                return resolve_builtin_func(attr)
            if attr == 'toString':
                return EXPR_TYPE_STR
            if attr == '__contains__':
                return EXPR_TYPE_BOOL
            if self.val.value.expr_type == EXPR_TYPE_STR:
                if attr in ['startswith', 'endswith']:
                    return EXPR_TYPE_BOOL

class Struct(Expr):
    def __init__(self, items):
        super(Struct, self).__init__()
        self.items = items

    _fields = ('items',)

class Struct_item(Ast):
    def __init__(self, name, expr):
        super(Struct_item, self).__init__()
        self.name = name
        self.expr = expr

    _fields = ('expr',)

class CommaOp(Expr):
    precedence = 15
    def __init__(self, items):
        super(CommaOp, self).__init__()
        self.items = items

    def _get_expr_type(self):
        if self.items:
            return self.items[-1].expr_type

class ParenthesisOp(Expr):
    ''' Parenthesis operator

        Such as `(1 + 2)'
    '''
    def __init__(self, expr):
        super(ParenthesisOp, self)
        self.expr = expr

class Js(Ast):
    def __init__(self, js):
        super(Js, self).__init__()
        self.js = js

    # Although Js is not strictly an expression, but Js can used as expression
    @property
    def expr_type(self):
        return None
    precedence = 0

class Throw(Ast):
    def __init__(self, expr):
        super(Throw, self).__init__()
        self.expr = expr

    _fields = ('expr',)

class Break(Singleton, Ast):
    def __init__(self):
        super(Break, self).__init__()

class Continue(Singleton, Ast):
    def __init__(self):
        super(Continue, self).__init__()

class FunctionDef(Expr):
    precedence = 2
    def __init__(self, args, body, name=None):
        super(FunctionDef, self).__init__()
        self.args, self.body, self.name = args, body, name

    _fields = 'args', 'body'

class Return(Ast):
    def __init__(self, expr):
        super(Return, self).__init__()
        self.expr = expr

    _fields = 'expr',

class Try(Ast):
    def __init__(self, body, *handlers):
        super(Try, self).__init__()
        self.body, self.handlers = body, handlers

    _fields = 'body', 'handlers'

class TryHandler(Ast):
    def __init__(self, var, body):
        super(TryHandler, self).__init__()
        self.var, self.body = var, body

    _fields = 'var', 'body'

class Finally(Ast):
    def __init__(self, body):
        super(Finally, self).__init__()
        self.body = body

    _fields = 'body',

class Subscript(Expr):
    precedence = 1
    def __init__(self, value, idx):
        super(Subscript, self).__init__()
        self.value, self.idx = value, idx

    _fields = 'value', 'idx'

def isexpr(o):
    return isinstance(o, Expr)

def isliteral(o):
    return isinstance(o, Literal)

def walk(node):
    '''
    Recursively yield *node* and all its child nodes. 

    *NOTE*: don't yield *node* itself.
    '''
    yield node
    for name in node._fields:
        val = getattr(node, name)
        iter = val if isinstance(val, Iterable) else (val,)
        for item in iter:
            for sub in walk(item):
                yield sub
