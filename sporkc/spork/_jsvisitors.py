# -*- coding: utf-8 -*-
from __future__ import absolute_import

from StringIO import StringIO
from itertools import repeat
from collections import Iterable

from . import SporkError
from .collections import eat
from .internal import nonef
import spork._jsast as j

# This is taken from the django project.
# Escape every ASCII character with a value less than 32.
JS_ESCAPES = (
    ('\\', '\\\\'),
    ('\'', r'\''),
    ('"', r'\"'),
    ) + tuple(('%c' % z, '\\x%02X' % z) for z in xrange(32))

def escapejs(value):
    """Hex encodes characters for use in JavaScript strings."""
    for bad, good in JS_ESCAPES:
        value = value.replace(bad, good)
    return value

class AstVisitor(object):
    def __init__(self, output):
        self.output = output

    def write_raw(self, s):
        self.output.write(s)

    write = write_raw

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise SporkError, 'lack visit method for ' + type(node).__name__

    def visit_list(self, node):
        v = self.visit
        for n in node:
            v(n)

    visit_tuple = visit_list

class Render(AstVisitor):
    def visit_Num(self, node):
        self.write(str(node.n))

    def visit_Name(self, node):
        self.write(node.id)

    def visit_Str(self, node):
        self.write("'")
        s = node.s
        if isinstance(s, unicode):
            s = s.encode('utf8')
        self.write(escapejs(s))
        self.write("'")

    def visit_Attribute(self, node):
        value, attr = node.value, node.attr
        if isinstance(value, j.Num):
            self.write('(')
            self.visit(value)
            self.write(')')
        else:
            self._visit_sub_expr(value)
        self.write('.')
        self.write(attr)

    def visit_Undefined(self, node):
        self.write('undefined')

    def visit_Null(self, node):
        self.write('null')

    def visit_True_(self, node):
        self.write('true')
    
    def visit_False_(self, node):
        self.write('false')

    def visit_This(self, node):
        self.write('this')

    def _visit_list(self, elements, sep = ',', newline=False, as_sub_expr=False):
        first = True
        for item in elements:
            if first:
                first = False
            else:
                if newline:
                    self._writeln(sep)
                else:
                    self.write(sep)
            if as_sub_expr:
                self._visit_sub_expr(item)
            else:
                self.visit(item)

    def visit_Array(self, node):
        self.write('[')
        self._visit_list(node.elms)
        self.write(']')

    def visit_Delete_stat(self, node):
        self.write('delete ')
        self.visit(node.expr)
        self._write_end_stat()

    def visit_Expr_stat(self, node):
        self.visit(node.expr)
        self._write_end_stat()

    def visit_Binexpr(self, node):
        self._visit_sub_expr(node.left)
        self._write_bin_op(node.op)
        self._visit_sub_expr(node.right)
        return True

    def visit_Assign_expr(self, node):
        self.visit(node.left)
        self._write_bin_op(node.op)
        self.visit(node.right)
        return True

    def _visit_sub_expr(self, expr):
        oldoutput = self.output
        output = self.output = StringIO()
        needgroup = False
        try:
            needgroup = self.visit(expr)
        finally:
            self.output = oldoutput
            if needgroup:
                self.write('(')
            self.write_raw(output.getvalue())
            if needgroup:
                self.write(')')

    def visit_Unary_expr(self, expr):
        self.write(expr.op)
        self._visit_sub_expr(expr.expr)
        return True

    def visit_Unary_postfix_expr(self, expr):
        self.visit(expr.expr)
        self.write(expr.op)
        return True

    def visit_Conditional_op(self, node):
        self._visit_sub_expr(node.value)
        self._write_bin_op('?')
        self._visit_sub_expr(node.first)
        self._write_bin_op(':')
        self._visit_sub_expr(node.second)
        return True

    def visit_If(self, node):
        self.write('if')
        self._write_pre_space('(')
        self.visit(node.value)
        self._write_end_space(')')
        self._write_left_brace()
        self.visit(node.first)
        self._write_right_brace()
        if node.second is not None:
            self._write_end_space('else')
            self._write_left_brace()
            self.visit(node.second)
            self._write_right_brace()

    def visit_For(self, node):
        self._write_end_space('for')
        self.write('(')
        n = j.noneast
        self._visit_list((node.init or n, node.cond or n, node.inc or n), ';')
        self._write_end_space(')')
        self._write_left_brace()
        self.visit(node.stats)
        self._write_right_brace()

    def visit_For_in(self, node):
        self._write_end_space('for')
        self.write('(')
        self.visit(node.name)
        self.write(' in ')
        self.visit(node.expr)
        self._write_end_space(')')
        self._write_left_brace()
        self.visit(node.stats)
        self._write_right_brace()

    def visit_While(self, node):
        self._write_end_space('while')
        self.write('(')
        self.visit(node.cond)
        self._write_end_space(')')
        self._write_left_brace()
        self.visit(node.stats)
        self._write_right_brace()

    def visit_DeclareVar(self, node):
        self.write('var ')
        self.write(node.name)
        if node.value:
            self._write_bin_op('=')
            self.visit(node.value)

    def visit_DeclareMultiVar(self, node):
        self.write('var ')
        self.write(','.join(node.names))
        self._write_end_stat()

    def visit_File(self, node):
        self.visit(node.stats)

    def visit_New_object(self, node):
        self.write('new ')
        self._visit_sub_expr(node.type)
        self.write('(')
        self._visit_list(node.args)
        self.write(')')

    def visit_Call(self, node):
        self._visit_sub_expr(node.val)
        self.write('(')
        self._visit_list(node.args, as_sub_expr=True)
        self.write(')')

    def visit_Struct(self, node):
        self._write_left_brace()
        self._visit_list(node.items, newline=True)
        self._write_right_brace()

    def visit_Struct_item(self, node):
        self.write(node.name)
        self._write_end_space(':')
        self.visit(node.expr)

    def visit_CommaOp(self, node):
        self._visit_list(node.items, as_sub_expr=True)
        return True

    def visit_ParenthesisOp(self, node):
        self.write('(')
        self.visit(node.expr)
        self.write(')')

    def visit_Js(self, node):
        self.write(node.js)

    def visit_Throw(self, node):
        self.write('throw ')
        self.visit(node.expr)
        self._write_end_stat()

    def visit_Break(self, node):
        self._writeln('break;')

    def visit_Continue(self, node):
        self._writeln('continue;')

    def visit_FunctionDef(self, node):
        if node.name:
            self.write('function ')
            self.write(node.name)
            self.write('(')
        else:
            self.write('function(')
        self._visit_list(node.args)
        self._write_end_space(')')
        self._write_left_brace()
        self.visit(node.body)
        self._write_right_brace()
        return True

    def visit_Return(self, node):
        if node.expr:
            self.write('return ')
            self.visit(node.expr)
            self._write_end_stat()
        else:
            self._writeln('return;')

    def visit_Try(self, node):
        self._write_end_space('try')
        self._write_left_brace()
        self.visit(node.body)
        self._write_right_brace()
        self.visit(node.handlers)

    def visit_TryHandler(self, node):
        self._write_end_space('catch')
        self.write('(')
        self.visit(node.var)
        self._write_end_space(')')
        self._write_left_brace()
        self.visit(node.body)
        self._write_right_brace()

    def visit_Finally(self, node):
        self._write_end_space('finally')
        self._write_left_brace()
        self.visit(node.body)
        self._write_right_brace()

    def visit_Subscript(self, node):
        self.visit(node.value)
        self.write('[')
        self.visit(node.idx)
        self.write(']')

    visit_Empty = nonef

    def _write_bin_op(self, op):
        self.write(op)

    _writeln = _write_pre_space = _write_end_space = _write_bin_op

    def _write_left_brace(self):
        self.write('{')

    def _write_right_brace(self):
        self.write('}')

    def _write_end_stat(self):
        self.write(';')

    indent = undent = nonef

    def visit_SrcMap(self, node):
        self.write('[]')

class DebugRender(Render):
    def __init__(self, output):
        super(DebugRender, self).__init__(output)
        self.__indents = ''
        self.__bol = True
        self.__linenoset = False
        self.__jslineno = 0
        self.__srcmap = []
        self._lastpyline = -1

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        if isinstance(node, Iterable):
            eat(self.visit(n) for n in node)
        else:
            if self.__bol and not self.__linenoset:
                self._lastpyline = node.lineno
                self.__linenoset = True
            visitor = getattr(self, method, self.generic_visit)
            return visitor(node)

    def visit_File(self, node):
        self.__linenoset = False
        super(DebugRender, self).visit_File(node)

    def write(self, v):
        if self.__bol:
            super(DebugRender, self).write(self.__indents)
            self.__bol = False
            self.__jslineno += 1
        super(DebugRender, self).write(v)

    def _visit_list(self, elements, sep = ',', newline=False, as_sub_expr=False):
        return super(DebugRender, self)._visit_list(elements, sep + ' ',
                newline, as_sub_expr)

    def indent(self):
        self.__indents += '  '

    def undent(self):
        self.__indents = self.__indents[:-2]

    def __newline(self):
        self.write('\n')
        self.__update_srcmap()

        self.__bol = True
        self.__linenoset = False

    def __update_srcmap(self):
        lack = self.__jslineno - len(self.__srcmap)
        if lack >= 0:
            self.__srcmap.extend(repeat(-1, lack + 1))
        if self.__srcmap[self.__jslineno] == -1:
            self.__srcmap[self.__jslineno] = self._lastpyline

    def _write_bin_op(self, op):
        self.write(' ')
        self.write(op)
        self.write(' ')

    def _write_pre_space(self, v):
        self.write(' ')
        self.write(v)

    def _write_end_space(self, v):
        self.write(v)
        self.write(' ')

    def _writeln(self, v):
        self.write(v)
        self.__newline()

    def _write_left_brace(self):
        self.write('{')
        self.__newline()
        self.indent()

    def _write_right_brace(self):
        self.undent()
        self.write('}')
        self.__newline()

    def _write_end_stat(self):
        self.write(';')
        self.__newline()

    def visit_Js(self, node):
        for line in node.js.splitlines(True):
            if line.endswith('\n'):
                self.write(line[:-1])
                self.__newline()
            else:
                self.write(line)
            self._lastpyline += 1

    def visit_SrcMap(self, node):
        self.__update_srcmap()
        self.write('[')
        self.write(','.join(str(n) for n in self.__srcmap))
        self.write(']')
