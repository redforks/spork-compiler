# -*- coding: utf-8 -*-
from __future__ import absolute_import

from StringIO import StringIO
from unittest import TestCase
from functional import compose

import sporktest
import spork._jsast as j
from spork._jsvisitors import Render, DebugRender
from spork.collections import eat

n = j.Num
id = j.Name

class AstFieldsTest(TestCase):
    def do_test(self, expected, ast):
        self.assertEqual(expected, ast._fields)

    def test_empty_fiels(self):
        eat(self.assertEqual((), x._fields) for x in [
            n(1), id('a'), j.noneast, j.True_(), j.Js(''),
            j.Break(), j.Continue()
            ])

    def test_attribute(self):
        self.do_test(('value',), j.Attribute(n(1), 'x'))

    def test_array(self):
        self.do_test(('elms',), j.Array())

    def test_expr_stat(self):
        self.do_test(('expr',), j.Expr_stat(n(0)))

    def test_binexpr(self):
        self.do_test(('left', 'right'), j.Plus(n(1), n(2)))

    def test_unary(self):
        self.do_test(('expr',), j.Unary_neg(n(1)))

    def test_unary_postfix(self):
        self.do_test(('expr',), j.Inc_postfix(n(1)))

    def test_conditional_op(self):
        self.do_test(('value', 'first', 'second'), j.Conditional_op(
            n(0), n(1), n(2)))

    def test_delete(self):
        self.do_test(('expr',), j.Delete_stat(n(0)))

    def test_if(self):
        self.do_test(('value', 'first', 'second'), j.If(
            n(0), n(1), n(2)))

    def test_for(self):
        self.do_test(('init', 'cond', 'inc', 'stats'), j.For(
            n(0), n(1), n(2), ()))

    def test_for_in(self):
        self.do_test(('expr', 'stats'), j.For_in(
            'i', n(1), ()))

    def test_while(self):
        self.do_test(('cond', 'stats'), j.While(n(1), ()))

    def test_declare_var(self):
        self.do_test(('value',), j.DeclareVar('s', n(1)))

    def test_visit_file(self):
        self.do_test(('stats',), j.File(()))

    def test_new_object(self):
        self.do_test(('val', 'args'), j.New_object(n(1), ()))

    def test_call(self):
        self.do_test(('val', 'args'), j.Call(n(1), ()))

    def test_struct(self):
        self.do_test(('items',), j.Struct(()))

    def test_struct_item(self):
        self.do_test(('expr',), j.Struct_item('a', n(0)))

    def test_throw(self):
        self.do_test(('expr',), j.Throw(n(0)))

    def test_function_def(self):
        self.do_test(('args', 'body'), j.FunctionDef((), ()))

    def test_return(self):
        self.do_test(('expr',), j.Return(n(0)))

    def test_try(self):
        self.do_test(('body', 'handlers'), j.Try((), ()))

    def test_tryhandler(self):
        self.do_test(('var', 'body'), j.TryHandler(id('3'), []))

    def test_finally(self):
        self.do_test(('body',), j.Finally([]))

    def test_subscript(self):
        self.do_test(('value', 'idx'), j.Subscript(n(2), n(3)))

    def test_walk(self):
        node = j.Num(3)
        self.assertEqual([node], list(j.walk(node)))
        assign = j.Assign(node, node)
        self.assertEqual([assign, node, node], list(j.walk(assign)))

        f = j.File([node, assign])
        self.assertEqual([f, node, assign, node, node], list(j.walk(f)))

class RenderTestBase(sporktest.MyTestCase):
    def t(self, expected, ast, rendercls):
        output = StringIO()
        r = rendercls(output)
        r.visit(ast)
        self.assertEqual(expected, output.getvalue())

class JSRenderTest(RenderTestBase):
    def t(self, expected, ast):
        super(JSRenderTest, self).t(expected, ast, Render)

    def test_undefined(self):
        self.t('undefined', j.Undefined())

    def test_null(self):
        self.t('null', j.Null())

    def test_Num(self):
        ast = n(2)
        self.t('2', ast)

    def test_true(self):
        self.t('true', j.True_())

    def test_false(self):
        self.t('false', j.False_())

    def test_this(self):
        self.t('this', j.This())

    def test_name(self):
        ast = id('abc')
        self.t('abc', ast)
        self.t('$do$', id('do'))

    def test_str(self):
        t = self.t
        s = j.Str
        t("'abc'", s('abc'))
        t(r"'\''", s('\''))
        t(r"'\"'", s('\"'))
        t(r"';'", s(';'))
        t(r"'&'", s('&'))
        t(r"'\x08'", s('\010'))
        t("'汉子'", s(u'汉子'))
        t("'汉子'", s('汉子'))

    def test_delete(self):
        t = self.t
        t('delete a;', j.Delete_stat(id('a')))

    def test_array(self):
        t = self.t
        t('[]', j.Array())
        t('[1]', j.Array([n(1)]))
        t('[1,2]', j.Array([n(1), n(2)]))
        t('[[]]', j.Array([j.Array()]))

    def test_assign(self):
        t = self.t
        a = j.Assign
        t('a=1', a(id('a'), n(1)))
        t('a=b=1', a(id('a'), a(id('b'), n(1))))
        t('a=b+(c=1)', a(
            id('a'),
            j.Plus(
                id('b'), 
                a(id('c'), n(1))
                )))
        t('a=(b,c)', a(id('a'), j.CommaOp([id('b'), id('c')])))

    def test_expr_stat(self):
        t = self.t
        t('a;', j.Expr_stat(id('a')))
        t('a=1;', j.Expr_stat(j.Assign(id('a'), n(1))))

    def test_attribute(self):
        self.t('a.b', j.Attribute(id('a'), 'b'))
        self.t('(1).b', j.Attribute(n(1), 'b'))
        self.t('$do$.$const$', j.Attribute(id('do'), 'const'))

    def test_plus(self):
        t = self.t
        t('1+2', j.Plus(n(1), n(2)))
        t('1+2+3', j.Plus(n(1), j.Plus(n(2), n(3))))
        t('1+2+3', j.Plus(j.Plus(n(1), n(2)), n(3)))
        t('1+2+3+4', j.Plus(n(1), j.Plus(n(2), j.Plus(n(3), n(4)))))

    def test_sub(self):
        t = self.t
        t('1-2', j.Sub(n(1), n(2)))
        t('1-2+3', j.Sub(n(1), j.Plus(n(2), n(3))))
        t('1-2+3', j.Plus(j.Sub(n(1), n(2)), n(3)))

    def test_mul(self):
        t = self.t
        t('1*2', j.Mul(n(1), n(2)))
        t('1*(2+3)', j.Mul(n(1), j.Plus(n(2), n(3))))
        t('1*2+3', j.Plus(j.Mul(n(1), n(2)), n(3)))

    def test_div(self):
        t = self.t
        t('1/2', j.Div(n(1), n(2)))
        t('1/(2+3)', j.Div(n(1), j.Plus(n(2), n(3))))
        t('1/2+3', j.Plus(j.Div(n(1), n(2)), n(3)))

    def test_mod(self):
        t = self.t
        t('1%2', j.Mod(n(1), n(2)))
        t('1%(2+3)', j.Mod(n(1), j.Plus(n(2), n(3))))
        t('1%2+3', j.Plus(j.Mod(n(1), n(2)), n(3)))

    def test_unary_neg(self):
        t = self.t
        t('-1', j.Unary_neg(n(1)))
        t('-(1+2)', j.Unary_neg(j.Plus(n(1), n(2))))
        t('1-(-1)', j.Sub(n(1), j.Unary_neg(n(1))))

    def test_inc_prefix(self):
        t = self.t
        t('++1', j.Inc_prefix(n(1)))
        t('1+(++1)', j.Plus(n(1), j.Inc_prefix(n(1))))

    def test_dec_prefix(self):
        t = self.t
        t('--1', j.Dec_prefix(n(1)))
        t('1+(--1)', j.Plus(n(1), j.Dec_prefix(n(1))))

    def test_inc_postfix(self):
        t = self.t
        t('1++', j.Inc_postfix(n(1)))
        t('(1++)+1', j.Plus(j.Inc_postfix(n(1)), n(1)))

    def test_dec_postfix(self):
        t = self.t
        t('1--', j.Dec_postfix(n(1)))
        t('(1--)+1', j.Plus(j.Dec_postfix(n(1)), n(1)))

    def test_side_assign(self):
        t = self.t
        args = id('a'), n(1)
        t('a+=1', j.Plus_assign(*args))
        t('a-=1', j.Sub_assign(*args))
        t('a*=1', j.Mul_assign(*args))
        t('a/=1', j.Div_assign(*args))
        t('a%=1', j.Mod_assign(*args))
        t('a>>=1', j.Rshift_assign(*args))
        t('a<<=1', j.Lshift_assign(*args))
        t('a>>>=1', j.Rshift_zero_fill_assign(*args))
        t('a|=1', j.Bit_or_assign(*args))
        t('a&=1', j.Bit_and_assign(*args))
        t('a^=1', j.Bit_xor_assign(*args))

    def test_cmp_operations(self):
        t = self.t
        args = id('a'), n(1)
        t('a==1', j.Eq(*args))
        t('a===1', j.Identical(*args))
        t('a!==1', j.Not_identical(*args))
        t('a!=1', j.Ne(*args))
        t('a>=1', j.Ge(*args))
        t('a<=1', j.Le(*args))
        t('a<1', j.Lt(*args))
        t('a>1', j.Gt(*args))

    def test_logical_ops(self):
        t = self.t
        args = id('a'), id('b')
        t('a&&b', j.Logic_and(*args))
        t('a||b', j.Logic_or(*args))
        t('!a', j.Logic_not(id('a')))
        t('!(a&&b)', j.Logic_not(j.Logic_and(*args)))

    def test_bitops(self):
        t = self.t
        args = n('3'), n('4')
        t('3&4', j.Bit_and(*args))
        t('3|4', j.Bit_or(*args))
        t('3^4', j.Bit_xor(*args))
        t('~3', j.Bit_inv(n(3)))
        t('1>>2', j.Bit_rshift(n(1), n(2)))
        t('1<<2', j.Bit_lshift(n(1), n(2)))
        t('1>>>2', j.Bit_rshift_zero_fill(n(1), n(2)))

    def test_conditional_op(self):
        t = self.t
        t('a?3:4', j.Conditional_op(id('a'), n(3), n(4))) 
        value = j.Plus(id('a'), n(1))
        t('a+1?3:4', j.Conditional_op(value, n(3), n(4)))

    def test_comma_op(self):
        t = self.t
        t('1,2', j.CommaOp([n(1), n(2)]))
        t('1,1+2', j.CommaOp([n(1), j.Plus(n(1), n(2))]))

    def test_parenthesis_op(self):
        self.t('(1)', j.ParenthesisOp(j.Num(1)))

    def test_if(self):
        t = self.t
        t('if(a){}', j.If(id('a'), (), None))
        t('if(a){}else{}', j.If(id('a'), (), ()))
        s = j.Expr_stat
        i = j.If
        t('if(a){3;}', i(id('a'), [s(n(3))], None))
        t('if(a){3;4;}', i(id('a'), [s(n(3)), s(n(4))], None))
        t('if(a){}else{3;4;}', i(id('a'), (), [s(n(3)), s(n(4))]))
        t('if(a){}else{if(b){}}', i(id('a'), (), [i(id('b'), (), None)]))

    def test_for(self):
        t = self.t
        f = j.For
        s = j.Expr_stat
        t('for(;;){}', f(None, None, None, ()))
        t('for(a;b;c){3;}', f(id('a'), id('b'), id('c'), [s(n(3))]))
        t('for(var a=1;b;c){3;}', f(j.DeclareVar('a',n(1)), id('b'), id('c'), 
            [s(n(3))]))

    def test_def_var(self):
        t = self.t
        t('var a', j.DeclareVar('a'))
        t('var a=1', j.DeclareVar('a', n(1)))
        t('var $do$=1', j.DeclareVar('do', n(1)))

    def test_def_var_stat(self):
        t = self.t
        t('var a;', j.Declare_var_stat('a'))
        t('var a=1;', j.Declare_var_stat('a', n(1)))

    def test_for_in(self):
        t = self.t
        f, s = j.For_in, j.Expr_stat
        t('for(var i in b){}', f('i', id('b'), ()))
        t('for(var i in b){1;}', f('i', id('b'), [s(n(1))]))

    def test_while(self):
        t = self.t
        w, s = j.While, j.Expr_stat
        t('while(true){}', w(j.True_(), ()))
        t('while(true){1;2;}', w(j.True_(), [s(n(1)), s(n(2))]))

    def test_jsfile(self):
        t = self.t
        s = j.Expr_stat
        t('', j.File(()))
        t('1;', j.File([s(n(1))]))
        t('1;2;', j.File([s(n(1)), s(n(2))]))

    def test_new_object(self):
        t = self.t
        t('new Object()', j.New_object(id('Object'), ()))
        t('new lib.MyList(a,3)', j.New_object(id('lib.MyList'), [id('a'), n(3)]))

    def test_call(self):
        t = self.t
        f = j.Call
        t('f()', f(id('f'), ()))
        t('f(d,3)', f(id('f'), [id('d'), n(3)]))
        t('(1+2)()', f(j.Plus(n(1), n(2)), ()))
        t('(function(){})()', f(j.FunctionDef((),()),()))
        t('f((1,2),2)', f(id('f'), [j.CommaOp([n(1), n(2)]), n(2)]))

    def test_struct(self):
        t = self.t
        s, k = j.Struct, j.Struct_item
        t('{}', s(()))
        t('{a:1}', s([k('a', n(1))]))
        t('{a:1,b:{}}', s([k('a', n(1)), k('b', s(()))]))
        t('{1:1,1.1:{}}', s([k(1, n(1)), k(1.1, s(()))]))

    def test_list(self):
        t = self.t
        t('', ())
        s = j.Expr_stat
        t('1;a;', [s(n(1)), s(id('a'))])

    def test_js(self):
        t = self.t
        t('what ever', j.Js('what ever'))
        t('1+2', j.Plus(n(1), j.Js('2')))

    def test_throw(self):
        self.t('throw 1;', j.Throw(n(1)))

    def test_break(self):
        self.t('break;', j.Break())

    def test_continue(self):
        self.t('continue;', j.Continue())

    def test_function(self):
        t = self.t
        t('function(){}', j.FunctionDef((), ()))
        t('function(a,b,c){}', j.FunctionDef([id('a'), id('b'), id('c')], ()))
        t('function(a,b,c){break;}', j.FunctionDef([id('a'), id('b'), id('c')],
            [j.Break()]))
        t('function(){1;break;}', j.FunctionDef((), [j.Expr_stat(n(1)), j.Break()]))
        t('function a(){}', j.FunctionDef((), (), 'a'))

    def test_return(self):
        t = self.t
        t('return;', j.Return(None))
        t('return 1;', j.Return(n(1)))

    def test_typeof(self):
        self.t('typeof 1', j.Typeof(n(1)))

    def test_try_catch(self):
        ns = compose(j.Expr_stat, n)
        self.t('try{}catch(e){}', j.Try((), j.TryHandler(j.Name('e'), ())))
        self.t('try{1;2;}catch(e){3;}', j.Try([ns(1),ns(2)], 
            j.TryHandler(id('e'), [ns(3)])))

    def test_try_finally(self):
        self.t('try{}finally{}', j.Try((), j.Finally(())))
        self.t('try{}catch(e){}finally{}', j.Try((), j.TryHandler(id('e'), ()),
            j.Finally(())))

    def test_isexpr(self):
        allasttypes = [t for t in vars(j).itervalues() if isinstance(t, type)]
        exprtypes = [j.Num, j.Name, j.Str, j.Attribute, j.Undefined,
                j.Null, j.True_, j.False_, j.Array, j.Binexpr,
                j.Unary_expr, j.Unary_postfix_expr, j.Conditional_op,
                j.Assign_expr, j.New_object, j.Call, j.Struct, j.Expr,
                j.Subscript, j.This, j.CommaOp, j.ParenthesisOp,
                j.FunctionDef, j.SrcMap, j.CallBase]
        allasttypes, exprtypes = set(allasttypes), set(exprtypes)
        nonexprtypes = allasttypes - exprtypes
        [self.assertTrue(issubclass(x, j.Expr), repr(x)) for x in exprtypes]
        [self.assertFalse(issubclass(x, j.Expr), repr(x)) for x in nonexprtypes]

    def test_is_literal(self):
        allasttypes = [t for t in vars(j).itervalues() if isinstance(t, type)]
        literaltypes = [j.Num, j.Str, j.Undefined, j.Literal,
                j.Null, j.True_, j.False_, j.This]
        allasttypes, literaltypes = set(allasttypes), set(literaltypes)
        nonliteraltypes = allasttypes - literaltypes
        [self.assertTrue(issubclass(x, j.Literal), repr(x)) for x in literaltypes]
        [self.assertFalse(issubclass(x, j.Literal), repr(x)) for x in nonliteraltypes]

    def test_subscriptions(self):
        t = self.t
        t('a[0]', j.Subscript(id('a'), n(0)))

    def test_srcmap(self):
        t = self.t
        t('[]', j.SrcMap())

        ast = j.File([n(0).set_location(1), j.SrcMap()])
        t('0[]', ast)

class JSPrettyRenderTest(RenderTestBase):
    def t(self, expected, ast):
        super(JSPrettyRenderTest, self).t(expected, ast, DebugRender)

    def test_array(self):
        t = self.t
        t('[]', j.Array())
        t('[1]', j.Array([n(1)]))
        t('[1, 2]', j.Array([n(1), n(2)]))
        t('[[], 2]', j.Array([j.Array(), n(2)]))

    def test_assign(self):
        t = self.t
        a = j.Assign
        t('a = 1', a(id('a'), n(1)))
        t('a = b = 1', a(id('a'), a(id('b'), n(1))))
        t('a = b + (c = 1)', a(
            id('a'),
            j.Plus(
                id('b'), 
                a(id('c'), n(1))
                )))

    def test_expr_stat(self):
        t = self.t
        t('a;\n', j.Expr_stat(id('a')))
        t('a = 1;\n', j.Expr_stat(j.Assign(id('a'), n(1))))

    def test_plus(self):
        t = self.t
        t('1 + 2', j.Plus(n(1), n(2)))
        t('1 + 2 + 3', j.Plus(n(1), j.Plus(n(2), n(3))))
        t('1 + 2 + 3', j.Plus(j.Plus(n(1), n(2)), n(3)))
        t('1 + 2 + 3 + 4', j.Plus(n(1), j.Plus(n(2), j.Plus(n(3), n(4)))))

    def test_side_assign(self):
        t = self.t
        args = id('a'), n(1)
        t('a += 1', j.Plus_assign(*args))

    def test_conditional_op(self):
        t = self.t
        t('a ? 3 : 4', j.Conditional_op(id('a'), n(3), n(4))) 
        value = j.Plus(id('a'), n(1))
        t('a + 1 ? 3 : 4', j.Conditional_op(value, n(3), n(4)))

    def test_if(self):
        t = self.t
        t('if (a) {\n}\n', j.If(id('a'), (), None))
        t('if (a) {\n}\nelse {\n}\n', j.If(id('a'), (), ()))
        s = j.Expr_stat
        i = j.If
        t('if (a) {\n  1;\n}\nelse {\n  3;\n  4;\n}\n', 
                i(id('a'), (s(n(1)),), [s(n(3)), s(n(4))]))
        t('if (a) {\n}\nelse {\n  if (b) {\n    3;\n  }\n}\n', 
                i(id('a'), (), [i(id('b'), (s(n(3)),), None)]))

    def test_for(self):
        t = self.t
        f = j.For
        s = j.Expr_stat
        t('for (; ; ) {\n}\n', f(None, None, None, ()))
        t('for (a; b; c) {\n  3;\n}\n', f(id('a'), id('b'), id('c'), [s(n(3))]))
        t('for (var a = 1; b; c) {\n  3;\n}\n', 
                f(j.DeclareVar('a',n(1)), id('b'), id('c'), [s(n(3))]))

    def test_def_var(self):
        t = self.t
        t('var a = 1', j.DeclareVar('a', n(1)))

    def test_def_var_stat(self):
        t = self.t
        t('var a;\n', j.Declare_var_stat('a'))
        t('var a = 1;\n', j.Declare_var_stat('a', n(1)))

    def test_for_in(self):
        t = self.t
        f, s = j.For_in, j.Expr_stat
        t('for (var i in b) {\n}\n', f('i', id('b'), ()))
        t('for (var i in b) {\n  1;\n}\n', f('i', id('b'), [s(n(1))]))

    def test_while(self):
        t = self.t
        w, s = j.While, j.Expr_stat
        t('while (true) {\n}\n', w(j.True_(), ()))

    def test_new_object(self):
        t = self.t
        t('new lib.MyList(a, 3)', j.New_object(id('lib.MyList'), [id('a'), n(3)]))

    def test_call(self):
        t = self.t
        f = j.Call
        t('f()', f(id('f'), ()))
        t('f(d, 3)', f(id('f'), [id('d'), n(3)]))

    def test_struct(self):
        print 'wow'
        t = self.t
        s, k = j.Struct, j.Struct_item
        t('{\n}\n', s(()))
        t('{\n  a: 1}\n', s([k('a', n(1))]))
        t('{\n  a: 1, \n  b: {\n  }\n}\n', s([k('a', n(1)), k('b', s(()))]))

    def test_throw(self):
        self.t('throw 1;\n', j.Throw(n(1)))

    def test_break(self):
        self.t('break;\n', j.Break())

    def test_continue(self):
        self.t('continue;\n', j.Continue())

    def test_function(self):
        t = self.t
        t('function() {\n}\n', j.FunctionDef((), ()))
        t('function(a, b, c) {\n}\n', j.FunctionDef([id('a'), id('b'), id('c')], ()))
        t('function(a, b, c) {\n  break;\n}\n', 
                j.FunctionDef([id('a'), id('b'), id('c')], [j.Break()]))
        t('function() {\n  1;\n  break;\n}\n', 
                j.FunctionDef((), [j.Expr_stat(n(1)), j.Break()]))

    def test_js(self):
        t = self.t
        t('a', j.Js('a'))

        output = StringIO()
        r = DebugRender(output)
        r.indent()
        r.visit(j.Js('a'))
        self.assertEqual('  a', output.getvalue())
        r.visit(j.Js('b'))
        self.assertEqual('  ab', output.getvalue())

        r.output = output = StringIO()
        r.visit(j.Js('a\nb'))
        self.assertEqual('a\n  b', output.getvalue())

        r.output = output = StringIO()
        r.visit(j.Return(j.Js('1')))
        self.assertEqual('return 1;\n', output.getvalue())

    def test_return(self):
        t = self.t
        t('return;\n', j.Return(None))
        t('return 1;\n', j.Return(n(1)))

    def test_try_catch(self):
        ns = compose(j.Expr_stat, n)
        self.t('try {\n}\ncatch (e) {\n}\n', j.Try((), j.TryHandler(j.Name('e'), ())))
        self.t('try {\n  1;\n  2;\n}\ncatch (e) {\n  3;\n}\n', j.Try([ns(1),ns(2)], 
            j.TryHandler(id('e'), [ns(3)])))

    def test_try_finally(self):
        self.t('try {\n}\nfinally {\n}\n', j.Try((), j.Finally(())))
        self.t('try {\n}\ncatch (e) {\n}\nfinally {\n}\n', 
                j.Try((), j.TryHandler(id('e'), ()), j.Finally(())))

    def test_srcmap(self):
        t = self.t
        #t('[-1]', j.SrcMap())

        ast = j.File([n(0).set_location(1), j.SrcMap()])
        t('0[-1,1]', ast)

        ast = j.File([j.AssignStat(id('a'), n(1)).set_location(1), j.SrcMap()])
        t('a = 1;\n[-1,1]', ast)

from spork._jsast import EXPR_TYPE_NUM, EXPR_TYPE_STR, EXPR_TYPE_BOOL

class ExprTypeTest(TestCase):
    def test_literals(self):
        self.assert_num(j.Num(0))
        self.assert_bool(j.True_())
        self.assert_bool(j.False_())
        self.assert_str(j.Str(''))

    def test_name(self):
        n = j.Name('a')
        self.assert_none(n)
        n.expr_type = EXPR_TYPE_STR
        self.assert_str(n)

    def test_bin_op(self):
        self.assert_none(j.Plus(n(0), j.Str('')))
        self.assert_num(j.Plus(n(0), n(1))) 
        self.assert_num(j.Sub(n(0), n(1))) 
        self.assert_num(j.Mul(n(0), n(1))) 
        self.assert_num(j.Div(n(0), n(1))) 
        self.assert_num(j.Mod(n(0), n(1))) 
        self.assert_num(j.Bit_and(n(0), n(1))) 
        self.assert_num(j.Bit_or(n(0), n(1))) 
        self.assert_num(j.Bit_xor(n(0), n(1))) 
        self.assert_num(j.Bit_rshift(n(0), n(1))) 
        self.assert_num(j.Bit_rshift_zero_fill(n(0), n(1))) 
        self.assert_num(j.Bit_lshift(n(0), n(1))) 

        self.assert_none(j.Bit_and(j.True_(), j.True_()))

        self.assert_str(j.Plus(j.Str(''), j.Str(''))) 
        self.assert_none(j.Sub(j.Str(''), j.Str('')))
        self.assert_none(j.Mul(j.Str(''), j.Str('')))
        self.assert_none(j.Div(j.Str(''), j.Str('')))
        self.assert_none(j.Mod(j.Str(''), j.Str('')))

        for op in [j.Eq, j.Identical, j.Ne, j.Not_identical, j.Ge, j.Gt,
                j.Lt, j.Le]:
            self.assert_bool(op(n(0), j.Str('')))

        for op in [j.Logic_and, j.Logic_or]:
            self.assert_num(op(n(0), n(0)))
            self.assert_bool(op(j.True_(), j.False_()))
            self.assert_str(op(j.Str(''), j.Str('')))
        self.assert_none(j.Logic_or(n(0), j.False_()))

    def test_unary(self):
        for op in [j.Unary_add, j.Unary_neg, j.Inc_postfix, j.Inc_postfix,
                j.Dec_prefix, j.Dec_postfix]:
            self.assert_num(op(n(0)))
        self.assert_none(j.Unary_neg(j.Str('')))
        for expr in [n(0), j.True_(), j.Str(''), j.False_()]:
            self.assert_bool(j.Logic_not(expr))

    def test_condition_op(self):
        self.assert_num(j.Conditional_op(n(0), n(0), n(0)))
        self.assert_str(j.Conditional_op(n(0), j.Str(''), j.Str('')))
        self.assert_bool(j.Conditional_op(n(0), j.True_(), j.False_()))
        self.assert_none(j.Conditional_op(n(0), n(0), j.Str('')))

    def test_assign(self):
        self.assert_num(j.Assign(n(0), n(0)))
        self.assert_str(j.Assign(n(0), j.Str('')))
        self.assert_bool(j.Assign(n(0), j.True_()))

        self.assert_num(j.Plus_assign(n(0), j.Str('')))

    def test_comma(self):
        self.assert_none(j.CommaOp([]))
        self.assert_num(j.CommaOp([j.Str(''), n(0)]))

    def test_wellknown_attr(self):
        self.assert_num(j.Attribute(j.Name('x'), 'length'))
        self.assert_str(j.Attribute(j.Name('x'), '__name__'))

    def test_wellknow_func(self):
        self.assert_str(j.Call(j.Attribute(n(0), 'toString'), ()))
        self.assert_bool(j.Call(j.Attribute(n(0), '__contains__'), ()))

        mk_builtin_call = lambda f: j.Call(j.Attribute(j.Name(j.BUILTIN_VAR),
            f), ())
        self.assert_num(mk_builtin_call('len'))
        self.assert_num(mk_builtin_call('int'))
        self.assert_str(mk_builtin_call('str'))
        self.assert_str(mk_builtin_call('repr'))

        for f in ['bool', 'hasattr', 'isinstance', 'eq', '__gt', '__ge',
                '__lt', '__le', 'isString', 'isIteratable']:
            self.assert_bool(mk_builtin_call(f))

        self.assert_bool(j.Call(j.Attribute(j.Str(''), 'startswith'), ()))
        self.assert_bool(j.Call(j.Attribute(j.Str(''), 'endswith'), ()))

    def assert_num(self, expr):
        self.assertEqual(EXPR_TYPE_NUM, expr.expr_type)

    def assert_str(self, expr):
        self.assertEqual(EXPR_TYPE_STR, expr.expr_type)

    def assert_bool(self, expr):
        self.assertEqual(EXPR_TYPE_BOOL, expr.expr_type)

    def assert_none(self, expr):
        self.assertIsNone(expr.expr_type)
