# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
from re import search
from ConfigParser import SafeConfigParser
from functional import partial

import spork.test, sporktest
from spork import SporkError
from spork.jscompiler import compile, get_module_filename
from spork.io import IOUtil
import spork.virtual_fs as vir_fs

module_prefix = "var $p%(v)s;" \
    "if($b._module_loaded('%(m)s')){return;}"\
    "var $m=new $b.module('%(m)s','%(f)s.py');"

class JSCompilerTestBase(sporktest.MyTestCase):
    def setUp(self):
        super(JSCompilerTestBase, self).setUp()
        self.maxDiff = None
        vir_fs.hack()
        os.mkdir('/out')

    def do_compile(self, ioutil, code, module='t', **options):
        def_options = dict(pretty = False, embsrc = False, srcmap = False, 
                argcheck = False, debug=True, check_global=False)
        def_options.update(options)
        compile(module, code, ioutil, **def_options)

    def compile(self, code, module='t', **options):
        ioutil = IOUtil('/out')
        self.do_compile(ioutil, code, module, **options)
        return ioutil.open_read(get_module_filename(module, '.js')).read()

    def do_test(self, expected, code, module='t', **options):
        if options.get('pretty', False):
            expected = '(function() {\n' + expected + '}\n)();\n'
        else:
            expected = '(function(){' + expected + '})();'
        self.do_raw_test(expected, code, module, **options)

    def do_raw_test(self, expected, code, module='t', **options):
        back = self.compile(code, module, **options)
        self.assertEqual(expected, back)

class JSCompilerTest(JSCompilerTestBase):
    def t(self, expected, code, module='t', vars='', **options):
        if vars:
            vars = ',' + ','.join(vars)
        prefix = module_prefix % {
                'm': module, 'f': module.replace('.', '/'), 'v': vars}
        if '.' in module:
            prefix += "$b.import_('a').b=$m;"
        expected = prefix + expected
        code = '# coding:utf8\n' + code
        self.do_test(expected, code, module, **options)

    def test_with(self):
        expected = \
        '$t1=$m.a;' \
        "$t1.__enter__();" \
        '$t2=true;' \
        'try{$m.c();}' \
        'catch($t3){' \
            '$t2=false;' \
            "if(!$t1.__exit__($t3.__class__,$t3,null)){" \
                'throw $t3;' \
            '}' \
        '}finally{' \
            'if($t2){' \
                '$t1.__exit__(null,null,null);' \
            '}' \
        '}'
        self.t(expected, 'with a: c()', vars=['$t1','$t2','$t3'])

    def test_with_var(self):
        expected = \
        '$t1=$m.a;' \
        "$m.d=$t1.__enter__();" \
        '$t2=true;' \
        'try{$m.c=$m.d;}' \
        'catch($t3){' \
            '$t2=false;' \
            "if(!$t1.__exit__($t3.__class__,$t3,null)){" \
                'throw $t3;' \
            '}' \
        '}finally{' \
            'if($t2){' \
                '$t1.__exit__(null,null,null);' \
            '}' \
        '}'
        self.t(expected, 'with a as d: c=d',
                vars=['$t1','$t2','$t3'])

    def test_tmp_var_in_package_module(self):
        self.t('$t1=$m.a;'
            '$m.b=$t1.__fastgetitem__(0);'
            '$m.c=$t1.__fastgetitem__(1);'
            'if($t1.__len__()!==2){'
            'throw $b.ValueError('
            "'too many values to unpack'"
            ');}',
            'b, c = a', 'a.b', vars=['$t1'])

    def test_literal(self):
        t = self.t
        t('1;', '1')
        t('1.0;', '1.0')
        t('-1.1;', '-1.1')
        t('null;', 'None')
        t('true;', 'True')
        t('false;', 'False')
        t("1;'d';", "1\n'd'")
        t("1;'d';", "1\nu'd'")
        t(r"1;'\x0D';", "1\n'\\r'")
        t(r"1;'\\';", "1\n'\\\\'")
        t(r"1;'\\n';", "1\n'\\\\n'")
        t("1;'汉子';", "1\n'汉子'")
        t("1;'汉子';", "1\nu'汉子'")
        t("1;'<>';", "1;'<>'")

    def test_rename_js_keyword(self):
        t = self.t
        # as id
        t('$m.$const$;', 'const')

        t("$b._getattr($m.a,'$const$');", 'a.const')
        t("$b._setattr($m.a,'$const$',2);", 'a.const = 2')

        # as local var / as argument
        # as function name
        t('$m.$do$=function $do$($delete$){'
                'var $const$;'
                '$const$=1;'
                '$delete$=3;'
                'return null;'
        '};'
        "$m.$do$.__name__='$do$';"
        "$m.$do$.__args__=[null,null,['$delete$']];"
        '$m.$do$.__bind_type__=0;', 
        'def do(delete): const=1;delete=3')

        t('$m.$const$=(function(){'
        'var $i={'
        "$do$:pyjs__bind_method('$do$',function $do$(){"
        'var self=this;'
        'return null;'
        '},'
        "1,[null,null,['self']])};"
        'return pyjs__class_function_single_base('
            "pyjs__class_instance('$const$','t'),$i,"
            '$m.object);})();',
                'class const(object):\n def do(self):\n  pass')

        t('$m.$do$();', 'do()')

    def test_more_js_keywords(self):
        t = self.t
        t('$m.$export$;', 'export')
        t('$m.$function$;', 'function')
        t('$m.$instanceOf$;', 'instanceOf')
        t('$m.$label$;', 'label')
        t('$m.$let$;', 'let')
        t('$m.$new$;', 'new')
        t('$m.$switch$;', 'switch')
        t('$m.$this$;', 'this')
        t('$m.$throw$;', 'throw')
        t('$m.$catch$;', 'catch')
        t('$m.$typeof$;', 'typeof')
        t('$m.$var$;', 'var')
        t('$m.$void$;', 'void')
        t('$m.$default$;', 'default')
        t('$m.$name$;', 'name')
        t('$m.$super$;', 'super')

    def test_get_global_var(self):
        t = self.t
        t('$m.a;', 'a', check_global=False)
        t("$b._get_global_var($m,'a');", 'a', check_global=True)
        t("$b._get_global_var($m,'c')();", 'c()', check_global=True)
        t("$m.a=1;", 'a=1', check_global=True)
        t("$b._get_global_var($m,'$super$');", 'super',
                check_global=True)

        # __builtin__ module does not enable check_global, 
        # __builtin__ local variable is global variable
        self.do_raw_test("(function(){var $p;var $m={};"
                '$m.__debug__=true;'
                "$m.__file__='__builtin__.py';"
                '$m.a;'
                '})();',
                'a', module='__builtin__', check_global=True)

    def test_package_var(self):
        self.do_test("var $p;"
            "if($b._module_loaded('sf.test')){return;}"
            "var $m=new $b.module('sf.test','sf/test.py');"
            "$b.import_('sf').test=$m;"
            '$m.a;',
            'a', module='sf.test')

    def test_format_op(self):
        t = self.t
        t("'%s'.__mod__(1);", "'%s' % 1")
        t("'%s+%s'.__mod__($b.tuple([1,2]));", "'%s+%s' % (1,2)")

    def test_tuple_expr(self):
        t = self.t
        t('$b.tuple([]);', '()')
        t("$b.tuple(['a']);", '("a",)')
        t('$b.tuple([1,2]);', '(1, 2)')

    def test_list_expr(self):
        t = self.t
        t('$b.list([]);', '[]')
        t("$b.list(['a']);", '["a",]')
        t('$b.list([1,2]);', '[1, 2]')
        t('$b.list([$b.tuple([])]);', '[()]')

    def test_dict_expr(self):
        t = self.t
        t('$b.dict([]);', '{}')
        t('$b.dict([[1,2]]);', '{1: 2}')
        t('$b.dict([[1,2],[3,4]]);', '{1: 2, 3: 4}')

    def test_assign(self):
        t = self.t
        t('$m.a=1;', 'a = 1')
        t('$m.a=1;$m.b=1;', 'a = b = 1')
        t('$m.a=1;$m.b=1;', 'a = 1\nb=1')
        t('$m.a=1;$m.b.__setitem__(3,1);', 'a = b[3] = 1')
        t('$t1=$m.c.__add__(2);$m.a=$t1;$m.b=$t1;', 'a = b = c+2',
                vars=['$t1'])

    def test_assign_subscription(self):
        t = self.t
        t('$m.s.__setitem__(0,1);', 's[0] = 1')
        t('$m.s.__setitem__($b.slice(null,null,1),$b.list([]));',
                's[:] = []')

    def test_side_assign(self):
        t = self.t
        t("$m.a=$m.a.__add__(2);", 'a+=2')
        t("$m.a=$m.a.__sub__(2);", 'a-=2')
        t("$m.a=$m.a.__mul__(2);", 'a*=2')
        t("$m.a=$m.a.__div__(2);", 'a/=2')
        t("$m.a=$m.a.__mod__(2);", 'a%=2')
        t("$m.a=$m.a>>>2;", 'a>>=2')
        t("$m.a=$m.a<<2;", 'a<<=2')
        t("$m.a=$m.a.__and__(1);", 'a&=1')
        t("$m.a=$m.a.__or__(1);", 'a|=1')
        t("$m.a=$m.a.__xor__(1);", 'a^=1')
        t("$m.a=$m.a.__floordiv__(1);", 'a//=1')
        t("$m.a=$b.pow($m.a,2);", 'a**=2')

    def test_side_assign_attr(self):
        t = self.t
        setattr = '$b._setattr'
        getattr = '$b._getattr'
        t(setattr + "($m.c,'b'," + getattr + "($m.c,'b').__add__(3));", 
                'c.b+=3')

    def test_NotImplemented(self):
        self.t('undefined;', 'NotImplemented')

    def test_attribute(self):
        t = self.t
        t("$b._getattr('','upper');", "''.upper")
        t("$b._getattr($b._getattr('','upper'),'length');",
                "''.upper.length")

        t("$b._setattr('','upper',1);", "''.upper=1")
        t("$b._setattr($b._getattr('','upper'),'length',1);",
                "''.upper.length=1")

    def test_subscriptions(self):
        t = self.t
        t("''.__getitem__(0);", "''[0]")

    def test_slice(self):
        t = self.t
        t("''.__getitem__($b.slice(0,1,1));", "''[0:1]")
        t("''.__getitem__($b.slice(null,1,1));", "''[:1]")
        t("''.__getitem__($b.slice(0,null,1));", "''[0:]")
        t("''.__getitem__($b.slice(null,null,1));", "''[:]")
        t("''.__getitem__($b.slice(null,null,-1));", "''[::-1]")
        t("''.__getitem__($b.slice(0,1,0));", "''[0:1:0]")

    def test_method_call(self):
        t = self.t
        t("''.upper();", "''.upper()")
        t("''.decode('utf8');", "''.decode('utf8')")
        t("''.count('a',1);", "''.count('a', 1)")
        t("pyjs_kwargs_call('','count',null,null,[{start:1},'a']);", 
                "''.count('a', start=1)")
        t("pyjs_kwargs_call('','count',null,null,[{start:1}]);", 
                "''.count(start=1)")
        t("pyjs_kwargs_call('','count',null,null,[{sub:'s',start:1}]);", 
                "''.count(sub='s',start=1)")
        t("pyjs_kwargs_call('','count',$b.tuple(['s',1]),null,[{}]);",
                "''.count(*('s', 1))")
        t("pyjs_kwargs_call('','count',null,"
                "$b.dict([['sub','s'],['start',1]]),[{}]);",
                "''.count(**{'sub':'s', 'start':1,})")

        t("$b._getattr($m.a,'n').f();", 'a.n.f()')
        t("$m.a.f();", 'a.f()')

    def test_function_call(self):
        t = self.t
        t("$m.len('');", "len('')")
        t("pyjs_kwargs_call(t,'length',null,null,[{start:1}]);", 
                'length(start=1)')
        t("pyjs_kwargs_call(t,'int',null,null,[{base:2},'11']);",
                "int('11',base=2)")
        t("pyjs_kwargs_call(t,'int',"
                "$b.tuple(['11',2]),null,[{}]);",
                "int(*('11', 2))")
        t("pyjs_kwargs_call(t,'int',null,"
                "$b.dict([['x','11'],['base',2]]),[{}]);",
                "int(**{'x':'11', 'base':2})")

    def test_nested_function_call(self):
        # empty
        self.do_no_arg_func(
                'var g;g=function g(){return null;};'
                "g.__name__='g';"
                'g.__args__=[null,null];'
                'g.__bind_type__=0;'
                'g();',
                "\n def g():pass\n g()")

        # kwargs
        self.do_no_arg_func(
                'var g;g=function g(){'
                'var args=arguments.length>0?arguments[arguments.length-1]:'
                '$b.__empty_kwarg();'
                'return null;};'
                "g.__name__='g';"
                "g.__args__=[null,'args'];"
                'g.__bind_type__=0;'
                'pyjs_kwargs_call(null,g,null,null,[{a:1}]);',
                "\n def g(**args):pass\n g(a=1)")

    def test_tuple_assign(self):
        t = self.t
        js ='$t1=$m.p;$m.a=$t1.__fastgetitem__(0);'\
            '$m.b=$t1.__fastgetitem__(1);'
        t(js, 'a,b=p', debug=False, vars=['$t1'])
        t(js + 'if($t1.__len__()!==2){'
        'throw $b.ValueError('
        "'too many values to unpack');}",
        'a,b=p', debug=True, vars=['$t1'])

        t('$t1=$b.tuple([3,4,5]);'
          '$m.a=$t1.__fastgetitem__(0);$m.b=$t1.__fastgetitem__(1);'
          '$m.c=$t1.__fastgetitem__(2);'
          'if($t1.__len__()!==3){'
          'throw $b.ValueError('
          "'too many values to unpack');}",
          'a,b,c=3,4,5', vars=['$t1'])

    def test_merge_var_declar(self):
        self.do_no_arg_func('var a,b;a=1;b=1;', '\n a=1\n b=1')

    def test_if(self):
        t = self.t
        t('if(true){}', 'if True: pass')
        t('if(true){}else{}', 'if True:pass;\nelse:pass')
        t('if(true){3;}else{}', 'if True:3;\nelse:pass')
        t('if(true){}else{if(false){}}',
            'if True:pass\nelif False:pass')

    def test_optimize_forced_bool_expr(self):
        # if inner expression is definitely bool expression, do not wrap with 
        # $b._bool
        t = self.t
        t('if($m.a===null){}', 'if a is None: pass')
        t('if($m.a===1){}', 'if a is 1: pass')
        t('if($m.a!==null){}', 'if a is not None: pass')
        t('if(true){}', 'if True: pass')
        t('if(false){}', 'if False: pass')
        t('if(!1){}', 'if not 1: pass')
        t('if(1===2){}', 'if 1==2: pass')
        t('if(1!==2){}', 'if 1!=2: pass')
        t('if(1>2){}', 'if 1>2: pass')
        t('if(1>=2){}', 'if 1>=2: pass')
        t('if(1<2){}', 'if 1<2: pass')
        t('if(1<=2){}', 'if 1<=2: pass')
        t('if($b.isinstance($m.a,$b.str)){}', 'if isinstance(a, str): pass')
        t('if(!$b.isinstance($m.a,$b.str)){}', 'if not isinstance(a, str): pass')
        t('if($b.hasattr($m.a,$b.str)){}', 'if hasattr(a, str): pass')
        t('if(!$b.hasattr($m.a,$b.str)){}', 'if not hasattr(a, str): pass')
        t('if(!$m.a.__contains__(1)){}', 'if 1 not in a: pass')
        t('if($m.a.__contains__(1)){}', 'if 1 in a: pass')
        t('if(a){}', 'from __spork__ import JS\nif JS("a"): pass')

    def test_optimize_range_for(self):
        t = self.t
        t('for($m.i=0;$m.i<10;$m.i++){}', 'for i in range(10): pass')
        t('for($m.i=0;$m.i<10;$m.i++){1;}', 'for i in xrange(10): 1')
        t('$t1=$m.a;for($m.i=0;$m.i<$t1;$m.i++){1;}',
                'for i in xrange(a): 1', vars=['$t1'])
        t('(function(){var $t1,i,$t2;$t1=$b.list();$t2=$m.a;'
            'for(i=0;i<$t2;i++){'
            '$t1.append(i);'
            '}return $t1;})();', '[i for i in xrange(a)]')
        t('(function(){var $t1,i;$t1=$b.list();'
            'for(i=0;i<10;i++){'
            '$t1.append(i);'
            '}return $t1;})();', '[i for i in range(10)]')

    def test_bin_op(self):
        t = self.t
        t('(1).__add__($m.a);', '1+a')
        t("$m.a.__add__('b');", "a+'b'")
        t('(1).__sub__($m.a);', '1-a')
        t('(1).__mul__($m.a);', '1*a')
        t('(1).__div__($m.a);', '1/a')
        t('(1).__floordiv__($m.a);', '1//a')
        t('(1).__mod__($m.a);', '1%a')
        t('$b.pow(1,$m.a);', '1**a')
        t('$m.a.__sub__($m.b).__mod__(3);', '(a-b) % 3')

    def test_optimize_literal_compute(self):
        t = self.t
        t('3;', '1 + 2')
        t('-1;', '1 - 2')
        t('2;', '1 * 2')
        t('0.5;', '1 / 2')
        t('1;', '4 // 3')
        t('2;', '5 % 3')
        t('8;', '2 ** 3')
        t('8.0;', '2 ** 3 + 4 % 3 - 3 * 4 / 3 // 3')
        t('9;', '(1 + 2) * 3')

    def test_cmp(self):
        t = self.t
        t('$m.a===true;', 'a is True')
        t('$m.a!==true;', 'a is not True')
        t('$b.__gt($m.a,3);', 'a>3')
        t('$b.__ge($m.a,3);', 'a>=3')
        t('$b.__lt($m.a,3);', 'a<3')
        t('$b.__le($m.a,3);', 'a<=3')
        t('$b.eq($m.a,3);', 'a==3')
        t('!$b.eq($m.a,3);', 'a!=3')
        t('$m.a.__contains__($m.b);', 'b in a')
        t('!$m.a.__contains__($m.b);', 'b not in a')

        t('1>3;', '1>3')
        t('1>=3;', '1>=3')
        t('1<3;', '1<3')
        t('1<=3;', '1<=3')
        t('1===3;', '1==3')
        t('1!==3;', '1!=3')

    def test_chain_cmp(self):
        self.t('$b.__lt(1,$m.a)&&$b.__lt($m.a,4);', '1<a<4')
        self.t('$b.__lt(1,$m.a)&&$b.__lt($m.a,$m.b)&&$b.__lt($m.b,5);',
                '1<a<b<5')
        self.t('$b.__lt(1,$m.a)&&$b.__lt($m.a,4);', '1<a<4')
        self.t('$b.__lt($m.f(),$m.a)&&$b.__lt($m.a,$m.g());', 'f()<a<g()')
        msg = 'In chain cmp, only literal and variable is allowed in the middle'
        with self.assertRaisesRegexp(NotImplementedError, msg):
            self.t('', '1<foo()<4')

    def test_bitop(self):
        t = self.t
        t('(1).__and__($m.a);', '1&a')
        t('(1).__or__($m.a);', '1|a')
        t('(1).__xor__($m.a);', '1^a')
        t('1>>>$m.a;', '1>>a')
        t('1<<$m.a;', '1<<a')
        t('~2;', '~2')

    def test_optimize_bitop_liternal_compute(self):
        t = self.t
        t('2;', '3 & 2')
        t('3;', '1 | 2')
        t('1;', '3 ^ 2')
        t('2;', '8 >> 2')
        t('8;', '2 << 2')

    def test_optimize_dircet_js_op(self):
        t = self.t
        t('1+$b.int($m.a);', '1 + int(a)')
        t('$b.int($m.a)+1;', 'int(a) + 1')
        t("$b.str($m.a)+'1';", 'str(a) + "1"')
        t("$b.str($m.a)+'1'+$b.str($m.b);", 'str(a) + "1" + str(b)')

    def test_optimize_plus_int_str(self):
        t = self.t
        t("1+'a';", "str(1) + 'a'")
        t("'a'+1;", "'a' + str(1)")
        t("1+$b.str(2);", "str(1) + str(2)")

    def test_logicop(self):
        t = self.t
        vars=['$t1']
        t('$t1=$m.a,$b._bool($t1)?2:$t1;',
                'a and 2', vars=vars)
        t('$t1=$m.a,$b._bool($t1)?$t1:2;',
                'a or 2', vars=vars)
        t('!true;', 'not True')
        t('!$b._bool($m.a);', 'not a')
        t('$t2=($t1=$m.a,$b._bool($t1)?2:$t1),$b._bool($t2)?3:$t2;',
                'a and 2 and 3', vars=['$t1', '$t2'])
        t('$t2=$m.a,$b._bool($t2)?$t2:'
                '($t1=$m.b,$b._bool($t1)?3:$t1);',
                'a or b and 3', vars=['$t1', '$t2'])

    def test_optimize_logicop(self):
        t = self.t
        t('1&&$m.a;', '1 and a')
        t('true&&2;', 'True and 2')
        t('1||$m.a;', '1 or a')
        t('true||2;', 'True or 2')
        t('$t1=1&&$m.a,$b._bool($t1)?$m.c:$t1;',
            '1 and a and c', vars=['$t1'])
        t('1&&2&&$m.c;', '1 and 2 and c')

    def test_conditional_op(self):
        self.t('true?1:0;', '1 if True else 0')
        self.t('(true?1:0).__add__($m.a);', '(1 if True else 0) + a')

    def test_unary_neg(self):
        self.t('$m.a.__neg__();', '-a')

    def test_repr_expr(self):
        t = self.t
        t('$m.repr($m.a);', 'repr(a)')
        t('$b.repr($m.a);', '`a`')

    def test_pass(self):
        self.t('', 'pass')

    def test_ignore_module_doc(self):
        self.t('', '"xx"')
        self.t('', '\n#abc\n"xx"')

    def test_del(self):
        self.t("delete $m.a;", 'del a')
        self.t("$b.delattr($m.a,'c');", 'del a.c')

        self.t('$m.a.__delitem__(0);', 'del a[0]')
        self.t('$m.a.__delitem__($b.slice(2,8,1));', 'del a[2:8]')

        self.do_no_arg_func('var a;a=1;delete a;', 'a=1;del a;')

    def test_print(self):
        t = self.t
        t('$b.print_([1],1);', 'print 1')
        t('$b.print_([1,$m.a],0);', 'print 1, a,')
        msg = 'print with redirection is not implemented.'
        with self.assertError(NotImplementedError, msg):
            t('', 'print >>f, 1')

    def test_raise(self):
        t = self.t
        t("throw $m.NameError();", 'raise NameError()')
        t("throw $m.NameError($m.msg);", 'raise NameError, msg')
        t("throw $m.NameError($m.msg);", 'raise NameError(msg)')

    def test_break(self):
        self.t('break;', 'break')

    def test_continue(self):
        self.t('continue;', 'continue')

    def test_lambda(self):
        t = self.t
        t('function(){return null;};', 'lambda: None')
        t('function(a){return null;};', 'lambda a: None')
        t('function(a,b){return b;};', 'lambda a,b: b')
        t('function(){'
            'var b=$b.tuple(Array.prototype.slice.call(arguments,0));'
            'return null;};', 'lambda *b: None')

    def assert_argstats(self, expected, actual):
        actual = actual[16:] # skip the outer module `function'
        idx1 = search(r'function( \w+)?\([^)]*\){', actual).end()
        idx2 = search('return null;|var [^$]', actual).start()
        self.assertEqual(expected, actual[idx1:idx2])

    def do_argcheck(self, argcheck_js, argprep_js, pycode):
        def do_test(pycode, jscode):
            back = self.compile(pycode, argcheck=True)
            self.assert_argstats(jscode, back)

        pycode1 = 'def f(' + pycode + '): pass'
        do_test(pycode1, argcheck_js + argprep_js)

        py_prefix = 'from __spork__ import no_arg_check\n@no_arg_check\n'
        pycode1 = py_prefix + 'def f(' + pycode + '): pass'
        do_test(pycode1, argprep_js)

        py_prefix = 'import __spork__\n@__spork__.no_arg_check\n'
        pycode1 = py_prefix + 'def f(' + pycode + '): pass'
        do_test(pycode1, argprep_js)

    def test_func_arg_check(self):
        self.do_argcheck(self.__js_exact_arg('f', 0), '', '')
        self.do_argcheck(self.__js_exact_arg('f', 1), '', 'a')

    def test_lambda_normal_argcheck(self):
        back = self.compile('lambda : None', argcheck = True)
        expected = self.__js_exact_arg('<lambda>', 0)
        self.assert_argstats(expected, back)

    def test_func_defarg_check(self):
        self.do_argcheck(
            self.__js_at_most_arg('f', '1'), "g!==undefined||(g=3);",
            'g=3')

        self.do_argcheck(
            self.__js_at_least_arg('f', 1) +
            "else " + self.__js_at_most_arg('f', '2'),
            'g!==undefined||(g=3);',
            'a,g=3')

    def test_func_vararg_check(self):
        self.do_argcheck('', '', '*g')
        self.do_argcheck(self.__js_at_least_arg('f', 1), '', 'a,*g')

    def test_kwarg_check(self):
        self.do_argcheck(self.__js_at_most_arg('f', 1), '', '**g')
        self.do_argcheck(
            self.__js_at_least_arg('f', 1) + "else " + 
            self.__js_at_most_arg('f', 2), '',
            'a,**g')

        self.t('$m.f=function f(){'
        + self.__js_at_most_arg('f', 1) +
                'var g=arguments.length>0?arguments[arguments.length-1]:'
                '$b.__empty_kwarg();'
                'return null;};'
                "$m.f.__name__='f';"
                "$m.f.__args__=[null,'g'];"
                "$m.f.__bind_type__=0;", 
                'def f(**g):pass', argcheck=True)

    def __js_at_least_arg(self, funcname, args):
        return ("if (arguments.length<%s){\n"
                "  throw $b.TypeError("
                    "'%s() takes at least %s arguments ('"
                    "+arguments.length+' given)');\n}\n") % (args, funcname, args)

    def __js_at_most_arg(self, funcname, args):
        return ("if (arguments.length>%s){\n"
                "  throw $b.TypeError("
                    "'%s() takes at most %s arguments ('"
                    "+arguments.length+' given)');\n}\n") % (args, funcname, args)

    def __js_exact_arg(self, funcname, arg_count):
        return (
            "if (arguments.length!==%s){\n"
                "  throw $b.TypeError("
                    "'%s() takes exactly %s"
                    " arguments ('+arguments.length+' given)');\n}\n" %
            (arg_count, funcname, arg_count))

    def do_no_arg_func(self, expected, pycode, **options):
        if options.get('debug', True):
            prefix = "$m.f=function f(){" 
        else:
            prefix = "$m.f=function(){" 

        self.t(prefix + expected + "return null;};$m.f.__name__='f';"
            "$m.f.__args__=[null,null];$m.f.__bind_type__=0;", 
            'def f():' + pycode, **options)

    def do_method_argcheck(self, jscode, pycode):
        back = self.compile('class C(object):\n def f(self' + 
                pycode + '): pass', argcheck=True)
        idx1 = search(r"var self=this;", back).end()
        idx2 = search('return null;', back).start()
        self.assertEqual(jscode, back[idx1:idx2])

    def test_no_arg_check_on_method(self):
        pycode = \
'''from __spork__ import no_arg_check
class C(object):
    @no_arg_check
    def f(self):
        pass
'''
        with self.assertRaises(NotImplementedError):
            self.compile(pycode, argcheck=True)

    def test_method_normal_argcheck(self):
        self.do_method_argcheck(self.__js_exact_arg('f', 0), '')

    def test_method_defarg_argcheck(self):
        self.do_method_argcheck(
                self.__js_at_most_arg('f', '1') +
                "s!==undefined||(s=1);", ',s=1')
        self.do_method_argcheck(
                self.__js_at_least_arg('f', 1) + 'else ' +
                self.__js_at_most_arg('f', '2') +
                "s!==undefined||(s=1);",
                ',a,s=1')

    def test_func(self):
        t = self.t
        self.do_no_arg_func('', 'pass')
        t("$m.a=function a(){"
            "1;return null;};$m.a.__name__='a';"
            "$m.a.__args__=[null,null];$m.a.__bind_type__=0;",
            'def a():1;return None')
        t("$m.a=function a(b){return b;};$m.a.__name__='a';"
            "$m.a.__args__=[null,null,['b']];$m.a.__bind_type__=0;", 
            'def a(b):return b')
        t('$m.a=function a(b){'
            'var c,d,$t1;'
            '$t1=$b.tuple([1,2]);'
            'c=$t1.__fastgetitem__(0);'
            'd=$t1.__fastgetitem__(1);'
            'if($t1.__len__()!==2){'
            'throw $b.ValueError('
            "'too many values to unpack'"
            ');}'
            'return null;};'
            "$m.a.__name__='a';"
            "$m.a.__args__=[null,null,['b']];$m.a.__bind_type__=0;", 
            'def a(b):c,d=1,2')

    def test_unbounded_local_var(self):
        with self.assertError(SyntaxError, 
            "local variable 'a' referenced before assign. line: 4"):
            self.do_no_arg_func('', '\n c=a\n a=1')

        self.do_no_arg_func('var c;c=$m.a;$m.a=1;', 
                '\n global a\n c=a\n a=1')

        self.compile('def f():\n [x for x in []]\n x=1')
        self.compile('def f(x):\n a=x\n x=1')
        self.compile('def f(x):\n a=1\n def g():\n  c=a\n def h():\n  c=a\n')

    def test_no_auto_return_after_raise(self):
        self.t("$m.a=function a(){"
            "throw $m.TypeError('');};$m.a.__name__='a';"
            "$m.a.__args__=[null,null];$m.a.__bind_type__=0;",
            'def a():raise TypeError("")')

    def test_ignore_func_doc(self):
        self.do_no_arg_func('', "\n ''' doc '''")

    def test_func_defaultarg(self):
        t = self.t
        t("$m.a=function a(a,b){b!==undefined||(b=null);return null;};"
            "$m.a.__name__='a';$m.a.__args__=[null,null,['a'],['b',null]];$m.a.__bind_type__=0;",
            'def a(a,b=None):return None')
        t("$m.a=function a(c,a,b){a!==undefined||(a=null);"
                "b!==undefined||(b=1);return null;};"
            "$m.a.__name__='a';$m.a.__args__=[null,null,['c'],['a',null],['b',1]];$m.a.__bind_type__=0;",
            'def a(c,a=None,b=1):return None')

    def test_func_varargs(self):
        t = self.t
        t('$m.a=function a(){'
            'var b=$b.tuple(Array.prototype.slice.call(arguments,0));'
            "return null;};$m.a.__name__='a';$m.a.__args__=['b',null];"
            '$m.a.__bind_type__=0;', 
            'def a(*b): return None')
        t('$m.a=function a(b){'
            'var c=$b.tuple(Array.prototype.slice.call(arguments,1));'
            'c=c.__getitem__(0);'
            "return null;};$m.a.__name__='a';$m.a.__args__=['c',null,['b']];"
            '$m.a.__bind_type__=0;', 
            'def a(b,*c): c=c[0]')

    def test_func_kargs(self):
        t = self.t
        t('$m.f=function f(){'
            'var b=arguments.length>0?arguments[arguments.length-1]:'
                '$b.__empty_kwarg();'
            "return b;};$m.f.__name__='f';$m.f.__args__=[null,'b'];" 
            '$m.f.__bind_type__=0;', 
            'def f(**b): return b')

        t('$m.f=function f(){'
            'var b=arguments.length>0?arguments[arguments.length-1]:'
                '$b.__empty_kwarg();'
                'b=1;'
                "return null;};$m.f.__name__='f';$m.f.__args__=[null,'b'];" 
                '$m.f.__bind_type__=0;', 
                'def f(**b): b=1')

        t('$m.f=function f(){'
            'var a=$b.tuple(Array.prototype.slice.call('
                'arguments,0,arguments.length-1));'
           'var b=arguments.length>0?arguments[arguments.length-1]:'
               '$b.__empty_kwarg();'
            'if(b._pyjs_is_kwarg===undefined){'
                'a.l.push(b);'
                'b=$b.__empty_kwarg();'
            '}'
            "return null;};$m.f.__name__='f';$m.f.__args__=['a','b'];" 
            '$m.f.__bind_type__=0;', 
            'def f(*a,**b): return None')

        t('$m.f=function f(a,b){'
           'var c=arguments.length>2?arguments[arguments.length-1]:'
               '$b.__empty_kwarg();'
		"if(c===undefined){"
			'c=$b.dict({});'
			"if(b!==undefined){"
				"if($b.get_pyjs_classtype(b)=='dict'){"
					'c=b;'
					'b=arguments[2];'
				'}'
			"}else{if(a!==undefined){"
				"if($b.get_pyjs_classtype(a)=='dict'){"
					'c=a;'
					'a=arguments[2];'
				'}}'
		'}}'
        'b!==undefined||(b=1);'
            "return null;};$m.f.__name__='f';$m.f.__args__=[null,'c',['a'],['b',1]];" 
            '$m.f.__bind_type__=0;', 
            'def f(a,b=1,**c): return None')

        t('$m.f=function f(a,b){'
            'var c=$b.tuple(Array.prototype.slice.call('
            'arguments,2,arguments.length-1));'
		'var d=arguments.length>2?arguments[arguments.length-1]:'
            '$b.__empty_kwarg();'
		"if(d._pyjs_is_kwarg===undefined)"
        '{'
			"c.l.push(d);"
            'd=$b.__empty_kwarg();'
		'}'
		"if(d===undefined){"
			'd=$b.dict({});'
			"if(b!==undefined){"
				"if($b.get_pyjs_classtype(b)=='dict'){"
					'd=b;'
					'b=arguments[2];'
				'}'
			"}else{if(a!==undefined){"
				"if($b.get_pyjs_classtype(a)=='dict'){"
					'd=a;'
					'a=arguments[2];'
				'}'
			'}}'
		'}'
            "return a;};$m.f.__name__='f';$m.f.__args__=['c','d',['a'],['b']];" 
            '$m.f.__bind_type__=0;', 
            'def f(a,b,*c,**d): return a')

        with self.assertError(NotImplementedError, 
            'use both default argument and vararg is not supported'):
            self.compile('def f(a,b=1,*c):pass')

    def test_local_var(self):
        self.t(
            '$m.foo=function foo(c){'
                'var s;'
                's=1;'
                '$m.a=2;'
                'c=3;'
                'return null;'
            '};'
            "$m.foo.__name__='foo';"
            "$m.foo.__args__=[null,null,['c']];"
            '$m.foo.__bind_type__=0;',
            'def foo(c): s=1;global a;a=2;c=3')

    def test_nested_func(self):
        self.do_no_arg_func(
                'var a,bar;'
                'a=3;'
                'bar=function bar(){'
                    'var a,b;'
                    'a=4;'
                    'b=1;'
                    'return null;'
                '};'
                "bar.__name__='bar';"
                'bar.__args__=[null,null];'
                'bar.__bind_type__=0;',
            '\n a=3\n def bar():\n  a=4;b=1')

    def test_lambda_in_func(self):
        self.do_no_arg_func(
                'var a,f;'
                'a=3;'
                'f=function(){return a;};',
            '\n a=3\n f=lambda : a'
        )

    def test_class_in_func(self):
        self.t(
            '$m.f=function f(val){'
                'var C;'
                'C=(function(){'
                    'var $i={'
                    "g:pyjs__bind_method('g',"
                    "function g(){var self=this;return val;}"
                    ",1,[null,null,['self']])};"
                    'return pyjs__class_function_single_base('
                        "pyjs__class_instance('C','t'),$i,"
                        '$m.object);})();'
                'return C;'
            '};'
            "$m.f.__name__='f';"
            "$m.f.__args__=[null,null,['val']];"
            '$m.f.__bind_type__=0;',
            'def f(val):\n class C(object):\n'
            '  def g(self):   return val\n'
            ' return C')

    def test_class_in_class(self):
        msg = 'class defined in class is not supported.'
        with self.assertError(NotImplementedError, msg):
            self.t('', 'class C(object):\n class bar(object):\n  pass')

    def test_for(self):
        t = self.t
        t(
            '$m.s=0;'
            '$t1=$b._iter_init($m.foo(10));'
            'while(($m.i=$t1())!==undefined){'
                '$m.s=$m.s.__add__($m.i);'
            '}',
            's=0\nfor i in foo(10):s+=i', vars=('$t1',))

        with self.assertError(NotImplementedError, 'else in loop is not implemented.'):
            t('', 'for i in range(10):pass\nelse:pass;')

        self.do_no_arg_func(
                'var i,s,$t1;'
                's=0;'
                '$t1=$b._iter_init($m.foo(10));'
                'while((i=$t1())!==undefined){'
                    's=s.__add__(i);'
                '}',
            '\n s=0\n for i in foo(10):s+=i')

        self.do_no_arg_func(
                'var i,s,j,$t1,$t2;'
                's=0;'
                '$t1=$b._iter_init($m.foo(10));'
                'while(($t2=$t1())!==undefined){'
                        'i=$t2.__fastgetitem__(0);'
                        'j=$t2.__fastgetitem__(1);'
                        'if($t2.__len__()!==2){'
                        'throw $b.ValueError('
                        "'too many values to unpack'"
                        ');}'
                        's=s.__add__(i);'
                '}',
            '\n s=0\n for i,j in foo(10):s+=i')

    def test_nested_for(self):
        self.do_no_arg_func(
            'var i,s,j,$t1,$t2;'
            's=0;'
            '$t1=$b._iter_init($m.foo(10));'
            'while((i=$t1())!==undefined){'
                '$t2=$b._iter_init($m.foo(2));'
                'while((j=$t2())!==undefined){'
                    's=s.__add__(i.__add__(j));'
                '}'
            '}',

            '''
    s=0
    for i in foo(10):
        for j in foo(2):
            s += i + j
''')

    def test_while(self):
        t = self.t
        t('while(true){}', 'while True: pass')
        t('while($b._bool($m.a)){3;}', 'while a: 3')
        with self.assertError(NotImplementedError, 'else in loop is not implemented.'):
            t('', 'while True: pass\nelse:pass;')

    def test_try_finally(self):
        t = self.t
        t('try{}finally{}', 'try:pass\nfinally:pass')
        t('try{(1).__add__($m.a);}finally{(3).__add__($m.b);}', 'try:1+a\nfinally:3+b')

    def test_try_except(self):
        def valid(jscode, pycode):
            jscode = 'try{}catch($t1)' \
                '{$t1=$b._errorMapping($t1);'\
                + jscode + '}'
            pycode = 'try:pass\n' + pycode
            self.t(jscode, pycode)

        valid('1;', 'except:1')
        valid('if($b.isinstance($t1,$m.Exception))'
                '{1;}else{'
                'throw $t1;}',
                'except Exception:1')
        valid('if($b.isinstance($t1,$m.Exception)){'
			'$m.e=$t1;'
            "$m.e=$m.e.__add__(1);"
		'}else{1;}',
        'except Exception as e:e+=1\nexcept:1')

        valid('if($b.isinstance($t1,$m.Exception)){'
			'$m.e=$t1;'
            "$m.e=$m.e.__add__(1);"
		'}else{throw $t1;}',
        'except Exception as e:e+=1')

    def test_try_except_in_func(self):
        def valid(jscode, pycode):
            jscode = '$m.f=function f(){var e;' \
            'try{}catch($t1)' \
                '{$t1=$b._errorMapping($t1);'\
                + jscode + '}return null;};$m.f.__name__=\'f\';'\
                '$m.f.__args__=[null,null];$m.f.__bind_type__=0;'
            pycode = '''
def f():
    try:
        pass
    ''' + pycode
            self.t(jscode, pycode)

        valid('if($b.isinstance($t1,$m.Exception)){'
			'e=$t1;'
            "e=e.__add__(1);"
        '}else{1;}',
        'except Exception as e:e+=1\n'
        '    except: 1')

    def test_try_else(self):
        with self.assertError(NotImplementedError, 
                'else in try is not implemented.'):
            self.t('', 'try:pass\nexcept:pass\nelse:pass')

    def test_class(self):
        t = self.t
        t('$m.Foo=(function(){'
            'var $i={};'
            'return pyjs__class_function_single_base('
                "pyjs__class_instance('Foo','t'),$i,"
		                            '$m.object);'
            '})();',
           'class Foo(object):pass')

        with self.assertError(NotImplementedError, 'old style class is not '
            'supported.'):
            t('', 'class Foo():pass')

        with self.assertError(NotImplementedError, 'decorator on class is not '
            'supported.'):
            t('', '@foo\nclass Foo(object):pass')

        t('$m.Foo=(function(){'
            'var $i={Bar:1};'
            'return pyjs__class_function('
                "pyjs__class_instance('Foo','t'),$i,"
		                            '[$m.object,$m.Bar]);'
            '})();',
           'class Foo(object, Bar):\n Bar=1')

    def test_ignore_class_doc(self):
        self.do_cls_member('', '', "\n '''doc'''")

    def do_cls_member(self, expected1, expected2, py, **options):
        prefix = (
            '$m.Foo=(function(){'
            'var $i={'
            )
        suffix = (
            'return pyjs__class_function_single_base('
                "pyjs__class_instance('Foo','t'),$i,"
                                    '$m.object);'
            '})();')
        expected = prefix + expected1 + '};' + expected2 + suffix
        self.t(expected, 'class Foo(object):' + py, **options)

    def test_attr_in_class(self):
        self.do_cls_member('a:1', '', 'a=1')
        self.do_cls_member('a:1,b:1', '', 'a=b=1')
        self.do_cls_member('', '$t1=$m.c;$i.a=$t1;$i.b=$t1;',
                'a=b=c')

    def test_method_in_class(self):
        self.do_cls_member(
            "f:pyjs__bind_method('f',function f(){"
                'var first=this;'
                'return null;'
            '}'
            ",1,[null,null,['first']])", '',
            '\n def f(first):  pass')

        self.do_cls_member(
            "f:pyjs__bind_method('f',function f(a){"
            'var b;'
            'var self=this;'
            'b=1;'
			'return a.__add__(b);'
            '}'
            ",1,[null,null,['self'],['a']])", '',
            '\n def f(self, a):\n  b=1\n  return a+b')

        self.do_cls_member(
            "f:pyjs__bind_method('f',function f(a){"
            'var self=this;'
            "a!==undefined||(a=1);"
			'return a.__add__(self);'
            '}'
            ",1,[null,null,['self'],['a',1]])", '',
            '\n def f(self, a=1):  return a+self')

        self.do_cls_member(
            "f:pyjs__bind_method('f',function f(b){"
            'var self=this;'
            'var a=$b.tuple(Array.prototype.slice.call(arguments,1));'
			'return a.__add__(self);'
            '}'
            ",1,['a',null,['self'],['b']])", '',
            '\n def f(self, b, *a):  return a+self')

        self.do_cls_member(
                "f:pyjs__bind_method('f',"
                'function f(){'
                'var self=this;'
                'var b=arguments.length>0?arguments[arguments.length-1]:'
                    '$b.__empty_kwarg();'
                        "return null;}"
                ",1,[null,'b',['self']])", '',
                '\n def f(self,**b): pass')

    def test_class_super(self):
        self.do_cls_member(
            "f:pyjs__bind_method('f',function f(){"
                'var self=this;'
                "$m._get_super_method($m.Foo,self,'f')();"
                'return null;'
            '}'
            ",1,[null,null,['self']])", '',
            '\n def f(self):  super(Foo, self).f()')

        self.do_cls_member(
            "f:pyjs__bind_method('f',function f(){"
                'var a;'
                'var self=this;'
                "a=$m._get_super_method($m.Foo,self,'f')(1,2);"
                'return null;'
            '}'
            ",1,[null,null,['self']])", '',
            '\n def f(self):  a = super(Foo, self).f(1, 2)')

        self.do_cls_member(
            "f:pyjs__bind_method('f',function f(){"
                'var self=this;'
                "pyjs_kwargs_call($m.$super$($m.Foo,self),'f',null,null,[{a:1}]);"
                'return null;'
            '}'
            ",1,[null,null,['self']])", '',
            '\n def f(self):  super(Foo, self).f(a=1)')

    def test_no_auto_return_after_return_in_method(self):
        self.do_cls_member(
                "f:pyjs__bind_method('f',"
                'function f(){'
                'var self=this;'
                "return 1;}"
                ",1,[null,null,['self']])", '',
                '\n def f(self): return 1')

    def test_no_auto_return_after_raise_in_method(self):
        self.do_cls_member(
                "f:pyjs__bind_method('f',"
                'function f(){'
                'var self=this;'
                "throw 1;}"
                ",1,[null,null,['self']])", '',
                '\n def f(self): raise 1')

    def test_static_method(self):
        self.do_cls_member(
            "f:pyjs__bind_method('f',function f(){"
                'return null;'
            '}'
            ",0,[null,null])", '',
            '\n @staticmethod\n def f():  pass')

        self.do_cls_member(
            "f:pyjs__bind_method('f',function f(a,b){"
                'var c;'
                "a!==undefined||(a=1);"
                "b!==undefined||(b=2);"
                'c=3;'
                'return null;'
            '}'
            ",0,[null,null,['a',1],['b',2]])", '',
            '\n @staticmethod\n'
            ' def f(a=1,b=2):  c=3')

    def test_class_method(self):
        self.do_cls_member(
            "f:pyjs__bind_method('f',function f(){"
                'var cls=this.prototype;'
                'return null;'
            '}'
            ",2,[null,null,['cls']])", '',
            '\n @classmethod\n def f(cls):  pass')

        self.do_cls_member(
            "f:pyjs__bind_method('f',function f(a){"
                'var b;'
                'var cls=this.prototype;'
                'a!==undefined||(a=3);'
                'b=1;'
                'return null;'
            '}'
            ",2,[null,null,['cls'],['a',3]])", '',
            '\n @classmethod\n'
            ' def f(cls,a=3):  b=1')

    def test_property(self):
        self.do_cls_member(
            "f:$m.property(pyjs__bind_method('f',function f(){"
                'var self=this;'
                'return null;'
            '}'
            ",1,[null,null,['self']]))",

            '$i.f='
            "$b._getattr($i.f,'setter')"
            "(pyjs__bind_method('f',function f(){"
                'var self=this;'
                'return null;'
            '}'
            ",1,[null,null,['self']]));",
            '\n @property\n def f(self):  pass\n'
            ' @f.setter\n def f(self): pass')

    def test_cls_member_not_in_method_scope(self):
        self.do_cls_member(
            'g:1,'
            "f:pyjs__bind_method('f',function f(){"
                'var first=this;'
                'return $m.g;'
            '}'
            ",1,[null,null,['first']])", '',
            '\n g = 1\n def f(first):  return g')

    def test_import(self):
        t = self.t
        t("$m.a=$b.import_('a');", 'import a')
        t("$m.a=$b.import_('a');$m.b=$b.import_('b');",
                'import a, b')
        t("$m.d=$b.import_('a');", 'import a as d')
        t("$m.t=$b.import_('a');$b.import_('a.b');$m.t;",
                'import a.b as t\nt')
        t("$m.a=$b.import_('a');$b.import_('a.b');"
        "$m.a=$b.import_('a');$b.import_('a.b.c');"
                "$b._getattr($m.a,'b');", 'import a.b, a.b.c\na.b')

    def test_import_from_in_func(self):
        self.do_no_arg_func("var b;"
                "b=$b.import_('a').b;",
            '\n from a import b', debug=False)
        self.do_no_arg_func("var c;"
                "c=$b.import_('a').b;",
            '\n from a import b as c', debug=False)

    def test_import_in_func(self):
        self.do_no_arg_func("var a;a=$b.import_('a');",
                '\n import a')
        self.do_no_arg_func("var a,b;a=$b.import_('a');"
                "b=$b.import_('b');",
                '\n import a,b')
        self.do_no_arg_func("var b;b=$b.import_('a');",
                '\n import a as b')
        self.do_no_arg_func("var a;a=$b.import_('a');"
                "$b.import_('a.b');",
                '\n import a.b')

    def test_import_future(self):
        msg = '__future__ import is not implemented.'
        with self.assertError(NotImplementedError, msg):
            self.t('', 'from __future__ import absolute_import')

        msg = 'relative import is not implemented.'
        with self.assertError(NotImplementedError, msg):
            self.t('', 'from .core import abc')

    def test_import_from(self):
        t = self.t
        t("$m.d=$b._valid_symbol('a','d',$b.import_('a').d);",
            'from a import d')
        t("$b.import_('a');"
            "$p=$b.import_('a.b');"
            "$m.c=$b._valid_symbol('a.b','d',$p.d);"
            "$m.ee=$b._valid_symbol('a.b','ee',$p.ee);",
            'from a.b import d as c, ee')

        t("$m.d=$b.import_('a').d;", 'from a import d', debug=False)
        t("$b.import_('a');"
            "$p=$b.import_('a.b');"
            "$m.c=$p.d;"
            "$m.ee=$p.ee;",
            'from a.b import d as c, ee', debug=False)

        t("$b._import_all_from_module($m,$b.import_('a'));",
            'from a import *')
        t("$b.import_('a');"
            "$b._import_all_from_module($m,$b.import_('a.b'));",
            'from a.b import *')

    def test_auto_import_parent_package(self):
        def do_test(expected, module):
            back = self.compile('', module, debug=False)
            expected = '(function(){var $p;' + expected
            assert back.startswith(expected), back

        do_test("if($b._module_loaded('a.b')){return;}"
                "var $m=new $b.module('a.b','a/b.py');"
                "$b.import_('a').b=$m;", 'a.b')
        do_test("if($b._module_loaded('a.b.c')){return;}"
                "var $m=new $b.module('a.b.c','a/b/c.py');"
                "$b.import_('a');"
                "$b.import_('a.b').c=$m;",
                'a.b.c')

    def test_yield(self):
        msg = 'Do not support yield statement.'
        with self.assertError(NotImplementedError, msg):
            self.t('', 'def foo(): yield 1')

    def test_list_comp(self):
        t = self.t
        t(
            '(function(){'
                'var $t1,$t2,i;'
                '$t1=$b.list();'
                '$t2=$b._iter_init($m.foo(10));'
                'while((i=$t2())!==undefined){'
                    '$t1.append(i);'
                '}'
            'return $t1;})();', '[i for i in foo(10)]')

        t(
            '(function(){'
                'var $t1,$t2,i;'
                '$t1=$b.list();'
                '$t2=$b._iter_init($m.foo(10));'
                'while((i=$t2())!==undefined){'
                    'if(!$b.eq(i,10)){'
                        '$t1.append(i);'
                    '}'
                '}'
            'return $t1;})();', '[i for i in foo(10) if i != 10]')

        t(
            '(function(){'
                'var $t1,$t2,x,$t3,y;'
                '$t1=$b.list();'
                '$t2=$b._iter_init($m.foo(10));'
                'while((x=$t2())!==undefined){'
                    '$t3=$b._iter_init($m.bar(20));'
                    'while((y=$t3())!==undefined){'
                        '$t1.append(x.__add__(y));'
                    '}'
                '}'
            'return $t1;})();'
            , '[x + y for x in foo(10) for y in bar(20)]')

        t(
            '(function(){'
                'var $t1,$t2,x,$t3,y;'
                '$t1=$b.list();'
                '$t2=$b._iter_init($m.foo(10));'
                'while((x=$t2())!==undefined){'
                    'if($b.__lt(x,5)){'
                        '$t3=$b._iter_init($m.bar(20));'
                        'while((y=$t3())!==undefined){'
                            'if($b.eq(y,3)){'
                                '$t1.append(x);'
                            '}'
                        '}'
                    '}'
                '}'
            'return $t1;})();'
            , '[x for x in foo(10) if x< 5 for y in bar(20) if y==3]')

    def test_list_comp_not_support_multi_var(self):
        msg = 'List competency with more than 1 vars is not supported.'
        with self.assertError(NotImplementedError, msg):
            self.t('', '[f(x,y) for x,y in range(10)]')

    def test_genxp(self):
        t = self.t
        t('$b._comp_expr($m.range(10),'
          'function(i){return i;},null);', '(i for i in range(10))')

        t('$b._comp_expr($m.range(10),'
          'function(i){return i.__mul__(i);},null);', '(i * i for i in range(10))')

        t('$b._comp_expr($m.range(10),'
          'function(i){return i.__mul__(i);},'
          'function(i){return $b.__gt(i,3);});',
          '(i * i for i in range(10) if i > 3)')

    def test_genxp_unsupported(self):
        t = partial(self.t, '')
        msg = 'comprehension with more than 1 vars is not supported'
        with self.assertError(NotImplementedError, msg):
            t('(x+y for x,y in range(10))')

        msg = 'comprehension with more than 1 iter source is not supported'
        with self.assertError(NotImplementedError, msg):
            t('(x for x in range(10) for y in range(10))')

    def test_JS(self):
        t = self.t
        t("$m.JS('a');", 'JS("a")')

        t("a", 'from __spork__ import JS\nJS("a")')
        t('\\n', 'from __spork__ import JS as js\njs("\\\\n")')
        t("a", 'import __spork__\n__spork__.JS("a")')

    def test_redefine_symbol(self):
        self.t('$m.NameError=1;', 'NameError = 1')

    def test_constructor(self):
        t = self.t
        t(
        '$m.Foo=(function(){'
            'var $i={'
            "__init__:pyjs__bind_method('__init__',"
            "function __init__(){"
                'var self=this;'
                'return null;'
            '}'
        ",1,[null,null,['self']])};"
            'return pyjs__class_function_single_base('
                "pyjs__class_instance('Foo','t'),$i,$m.object);"
        '})();',
                'class Foo(object):\n def __init__(self):\n  pass')

    def test_assign_class_member(self):
        self.t(
            '$m.foo=(function(){'
                'var $i={'
                    'a:pyjs__bind_method('
                    "'a',"
                    'function a(){'
                    'var self=this;'
                    'return null;}'
                    ",1,[null,null,['self']])};"
                '$i.b=$i.a;'
                'return pyjs__class_function_single_base('
                    "pyjs__class_instance('foo','t'),$i,$m.object);})();",
                'class foo(object):\n  def a(self):pass\n  b=a\n')

    def test_assert(self):
        self.t('$b._assert(true,null);', 'assert True')
        self.t("$b._assert(true,'abc');", 'assert True, "abc"')
        self.t('', 'assert True, "abc"', debug=False)

    def test_emb_py_src(self):
        self.do_test("var $p;"
                "if($b._module_loaded('t.a')){return;}"
                "var $m=new $b.module('t.a','t/a.py');"
                "$b.import_('t').a=$m;",
                'pass', module='t.a')

        self.do_test("var $p;"
                "if($b._module_loaded('t')){return;}"
                "var $m=new $b.module('t','t.py');"
                "$m.__src__='pass'.splitlines();",
                'pass', embsrc=True) 

    def test_src_map(self):
        self.do_test("  var $p;\n"
            "  if ($b._module_loaded('t')) {\n    return;\n  }\n"
            "  var $m = new $b.module('t', 't.py');\n"
            '  $m.a = 1;\n'
            "  $m.__srcmap__ = [-1,-1,-1,-1,-1,-1,-1,1,-1];\n", 'a=1',
            debug=True, embsrc=False, pretty=True, srcmap=True)

        code = r'''from __spork__ import JS
JS("""line 2;
'\\n'
line 3;
""")
3;'''
        self.do_test("  var $p;\n"
            "  if ($b._module_loaded('t')) {\n    return;\n  }\n"
            "  var $m = new $b.module('t', 't.py');\n"
            '  line 2;\n'
            "  '\\n'\n"
            '  line 3;\n'
            '  3;\n'
            "  $m.__srcmap__ = [-1,-1,-1,-1,-1,-1,-1,2,3,4,6,-1];\n", code,
            debug=True, embsrc=False, pretty=True, srcmap=True)

    def test_builtin_module(self):
        self.do_raw_test("(function(){var $p;var $m={};"
                '$m.__debug__=true;'
                "$m.__file__='__builtin__.py';"
                '})();',
                '', module='__builtin__')

        self.do_raw_test("(function(){var $p;var $m={};"
                '$m.__debug__=false;'
                "$m.__file__='__builtin__.py';"
                '})();',
                '', module='__builtin__',
                debug=False)

    def test_auto_debug_if_stat(self):
        t = self.t
        t('1;', 'if __debug__: 1\nelse: 2', debug=True)
        t('2;', 'if __debug__: 1\nelse: 2', debug=False)
        t('', 'if __debug__: 1\n', debug=False)

        t('2;', 'if not __debug__: 1\nelse: 2', debug=True)
        t('1;', 'if not __debug__: 1\nelse: 2', debug=False)

    def test_auto_debug_if_func(self):
        self.t('', 'if __debug__:\n def f(): pass', debug=False)

    def test_auto_debug_cls_member(self):
        self.do_cls_member('', '', '\n if __debug__:\n  f=1', debug=False)

        self.do_cls_member(
                'f:1',
                '$i.g=$i.f;',
                '\n if __debug__:\n  f=1\n  g=f',
                debug=True)

        self.do_cls_member(
                'f:1',
                '$i.g=$i.f;',
                '\n if __debug__:\n  pass\n else:\n  f=1\n  g=f',
                debug=False)

    def _test_const(self):
        self.t('', 'from __spork__ import const_value\nconst_value(x, 3)')
        #TODO: bad argument count
        #TODO: bad first argument type, must be name
        #TODO: bad 2nd argument, must be value

    def test_gen_home_page_bad_arg_count(self):
        with self.assertError(TypeError, 
            'gen_home_html() takes no arguments (1 given)'):
            self.t('', 'from __spork__ import gen_home_html as gen\ngen(1)')

    def test_not_exist_compiler_func(self):
        with self.assertError(ImportError, 'can not import name not_exist'):
            self.t('', 'from __spork__ import not_exist')

        with self.assertError(AttributeError, 
                "'module' object has no attribute 'not_ava'"):
            self.t('', 'import __spork__ as sp\nsp.not_ava()')

class SymbolFileTest(JSCompilerTestBase):
    def setUp(self):
        super(SymbolFileTest, self).setUp()
        self.ioutil = IOUtil('/out')

    def compile_symbol(self, code, module='t', **options):
        code = '# coding:utf8\n' + code
        ioutil = self.ioutil
        self.do_compile(ioutil, code, module, **options)
        f = ioutil.open_read(get_module_filename('t', '.symbol'))
        parser = SafeConfigParser()
        parser.readfp(f)
        return parser

    def read_items(self, config, section):
        assert config.has_section(section), section
        items = config.items(section)
        result = [None] * len(items)
        for key, value in items:
            result[int(key)] = value
        assert all(x is not None for x in result)
        return result

    def test_import(self):
        def valid(symbols, code):
            back = self.compile_symbol(code)
            self.assertEqual(symbols, self.read_items(back, 'import'))

        valid([], '1')
        valid(['a'], 'import a')
        valid(['a', 'a.b'], 'import a.b')
        valid(['a', 'a.b'], 'import a.b as c')
        valid(['a', 'a.b', 'a.c'], 'import a.b, a.c')
        valid([], 'if a: pass\nimport a')

        valid(['a',], 'from a import b')

    def assert_boolean_option(self, config, option, expected):
        assert config.has_section('misc')
        back = config.getboolean('misc', option)
        self.assertEquals(expected, back)

    def assert_gen_home_page(self, config, expected):
        self.assert_boolean_option(config, 'gen_home_html', expected)

    def assert_module(self, config, expected):
        assert config.has_section('misc')
        back = config.get('misc', 'module') 
        self.assertEquals(expected, back)

    def test_module(self):
        def valid(module):
            config = self.compile_symbol('', module)
            self.assert_module(config, module)
        valid('t')

    def test_gen_home_page(self):
        def valid(expected, code):
            back = self.compile_symbol(code)
            self.assert_gen_home_page(back, expected)

        valid(False, '')
        valid(True, 'from __spork__ import gen_home_html\ngen_home_html()')

    def do_assert_import_files(self, config, section, expected):
        assert config.has_section(section)
        back = self.read_items(config, section)
        self.assertEqual(expected, back)

    def assert_cssfiles(self, config, expected):
        self.do_assert_import_files(config, 'css files', expected)

    def test_cssfiles(self):
        def valid(expected, code):
            code = 'from __spork__ import import_css as css\n' + code
            config = self.compile_symbol(code)
            self.assert_cssfiles(config, expected)

        valid([], '')
        valid(['a.css'], 'css("a.css")')
        valid(['a.css', 'b.css'], 'css("a.css")\ncss("b.css")')

        with self.assertError(SporkError, 'import duplicate file a.css'):
            valid([], "css('a.css')\ncss('a.css')")

        with self.assertError(TypeError, 
                'import_css() takes exactly one argument (0 given)'):
            valid([], "css()")

        with self.assertError(TypeError, 'expected str parameter.'):
            valid([], "css(1)")

    def assert_jsfiles(self, config, expected):
        self.do_assert_import_files(config, 'js files', expected)

    def test_jsfiles(self):
        def valid(expected, code):
            code = 'from __spork__ import import_js as js\n' + code
            config = self.compile_symbol(code)
            self.assert_jsfiles(config, expected)

        valid([], '')
        valid(['a.js'], 'js("a.js")')
        valid(['a.js', 'b.js'], 'js("a.js")\njs("b.js")')

        with self.assertError(SporkError, 'import duplicate file a.js'):
            valid([], "js('a.js')\njs('a.js')")

        with self.assertError(TypeError, 
                'import_js() takes exactly one argument (0 given)'):
            valid([], "js()")

        with self.assertError(TypeError, 'expected str parameter.'):
            valid([], "js(1)")

    def assert_debug(self, config, expected):
        self.assert_boolean_option(config, 'debug', expected)

    def test_debug(self):
        def valid(debug):
            code = ''
            config = self.compile_symbol(code, debug=debug)
            self.assert_debug(config, debug)

        valid(True)
        valid(False)

from spork.jscompiler import gen_home_page, Symbol

class GenHomePageTest(JSCompilerTestBase):
    template = '''
sflib: %(sflib)s
preload: %(preload)s
'''
    def setUp(self):
        super(GenHomePageTest, self).setUp()
        os.mkdir('/lib')
        self.ioutil = IOUtil('/out')
        self.libdir = IOUtil('/lib')
        self.new_debug_symbol_file('__builtin__')

    def do_write_symbol(self, dir, symbol):
        filename = get_module_filename(symbol.module, '.symbol')
        f = dir.open_write(filename)
        symbol.write(f)

    def write_symbol(self, symbol):
        self.do_write_symbol(self.ioutil, symbol)

    def write_symbol_in_libdir(self, symbol):
        self.do_write_symbol(self.libdir, symbol)

    def gen_home_page(self, module):
        gen_home_page(self.libdir, self.ioutil, module, self.template)

    def gen_home_page_default_template(self, module):
        gen_home_page(self.libdir, self.ioutil, module)

    def assert_file_not_exist(self, path):
        self.assertFalse(self.ioutil.exist(path))

    def read_all(self, path):
        return self.ioutil.open_read(path).read()

    def assert_html(self, path, expected):
        back = self.read_all(path)
        self.assertEquals(expected, back)

    def new_symbol(self, module, debug):
        result = Symbol(module, debug)
        result.gen_home_html = True
        return result

    def new_debug_symbol(self, module):
        return self.new_symbol(module, True)

    def new_release_symbol(self, module):
        return self.new_symbol(module, False)

    def new_debug_symbol_file(self, module):
        symbol = self.new_debug_symbol(module)
        self.write_symbol(symbol)

    def test_no_home_page(self):
        symbol = Symbol('a', True)

        self.write_symbol(symbol)
        self.gen_home_page('a')
        self.assert_file_not_exist('a.html')

    def __console__in_file(self, filename):
        html = self.read_all(filename)
        return '__console__' in html

    def assert_default_debug_html(self, filename):
        assert self.__console__in_file(filename)

    def assert_default_release_html(self, filename):
        assert not self.__console__in_file(filename)

    def test_no_static_import(self):
        symbol = self.new_debug_symbol('a')

        self.write_symbol(symbol)
        self.gen_home_page('a')
        self.assert_html('a.html', '''
sflib: 
preload:         <script type="text/javascript" src="__builtin__.js"></script>
        <script type="text/javascript" src="a.js"></script>
''')

    def test_default_debug_template(self):
        symbol = self.new_debug_symbol('a')

        self.write_symbol(symbol)
        self.gen_home_page_default_template('a')
        self.assert_default_debug_html('a.html')

    def test_default_release_template(self):
        symbol = self.new_release_symbol('a')

        self.write_symbol(symbol)
        self.gen_home_page_default_template('a')
        self.assert_default_release_html('a.html')

    def test_package(self):
        self.new_debug_symbol_file('a')
        self.new_debug_symbol_file('a.b')
        symbol = self.new_debug_symbol('a.b.c')

        self.write_symbol(symbol)
        self.gen_home_page('a.b.c')
        self.assert_html('a/b/c.html','''
sflib: ../../
preload:         <script type="text/javascript" src="../../__builtin__.js"></script>
        <script type="text/javascript" src="../../a.js"></script>
        <script type="text/javascript" src="../../a/b.js"></script>
        <script type="text/javascript" src="../../a/b/c.js"></script>
''')

    def test_import_css(self):
        symbol = self.new_debug_symbol('a')
        symbol.add_css_file('a.css')

        self.write_symbol(symbol)
        self.gen_home_page('a')
        self.assert_html('a.html', '''
sflib: 
preload:         <link rel="stylesheet" href="a.css">
        <script type="text/javascript" src="__builtin__.js"></script>
        <script type="text/javascript" src="a.js"></script>
''')

    def test_import_css_in_package(self):
        symbol = self.new_debug_symbol('a')
        symbol.add_css_file('a.css')
        symbol.add_css_file('styles/a.css')
        self.write_symbol(symbol)

        self.new_debug_symbol_file('a.b')

        self.gen_home_page('a.b')
        self.assert_html('a/b.html', '''
sflib: ../
preload:         <link rel="stylesheet" href="../a.css">
        <link rel="stylesheet" href="../styles/a.css">
        <script type="text/javascript" src="../__builtin__.js"></script>
        <script type="text/javascript" src="../a.js"></script>
        <script type="text/javascript" src="../a/b.js"></script>
''')

    def test_import_css_in_package2(self):
        self.new_debug_symbol_file('a')
        symbol = self.new_debug_symbol('a.b')
        symbol.add_css_file('a.css')
        symbol.add_js_file('core.js')
        self.write_symbol(symbol)

        symbol = self.new_debug_symbol('b')
        symbol.add_import('a.b')
        self.write_symbol(symbol)

        self.gen_home_page('b')
        self.assert_html('b.html', '''
sflib: 
preload:         <link rel="stylesheet" href="a/a.css">
        <script type="text/javascript" src="__builtin__.js"></script>
        <script type="text/javascript" src="a.js"></script>
        <script type="text/javascript" src="a/core.js"></script>
        <script type="text/javascript" src="a/b.js"></script>
        <script type="text/javascript" src="b.js"></script>
''')

    def test_import_js(self):
        symbol = self.new_debug_symbol('a')
        symbol.add_js_file('b.js')

        self.write_symbol(symbol)
        self.gen_home_page('a')
        self.assert_html('a.html', '''
sflib: 
preload:         <script type="text/javascript" src="__builtin__.js"></script>
        <script type="text/javascript" src="b.js"></script>
        <script type="text/javascript" src="a.js"></script>
''')

    def test_import_js_in_package(self):
        symbol = self.new_debug_symbol('a')
        symbol.add_js_file('a.js')
        symbol.add_js_file('styles/a.js')
        self.write_symbol(symbol)

        self.new_debug_symbol_file('a.b')

        self.gen_home_page('a.b')
        self.assert_html('a/b.html', '''
sflib: ../
preload:         <script type="text/javascript" src="../__builtin__.js"></script>
        <script type="text/javascript" src="../a.js"></script>
        <script type="text/javascript" src="../styles/a.js"></script>
        <script type="text/javascript" src="../a.js"></script>
        <script type="text/javascript" src="../a/b.js"></script>
''')

    def test_auto_import_one_module(self):
        symbol = self.new_debug_symbol('b')
        self.write_symbol(symbol)

        symbol = self.new_debug_symbol('a')
        symbol.add_import('b')

        self.write_symbol(symbol)
        self.gen_home_page('a')
        self.assert_html('a.html', '''
sflib: 
preload:         <script type="text/javascript" src="__builtin__.js"></script>
        <script type="text/javascript" src="b.js"></script>
        <script type="text/javascript" src="a.js"></script>
''')

    def test_preload_order(self):
        self.new_debug_symbol_file('b')
        symbol = self.new_debug_symbol('a')
        symbol.add_import('b')
        symbol.add_js_file('extra.js')
        symbol.add_css_file('a.css')

        self.write_symbol(symbol)
        self.gen_home_page('a')
        self.assert_html('a.html', '''
sflib: 
preload:         <link rel="stylesheet" href="a.css">
        <script type="text/javascript" src="__builtin__.js"></script>
        <script type="text/javascript" src="b.js"></script>
        <script type="text/javascript" src="extra.js"></script>
        <script type="text/javascript" src="a.js"></script>
''')

    def test_parent_modules(self):
        def valid(expected, module):
            from spork.jscompiler import _parent_modules
            back = list(_parent_modules(module))
            self.assertEquals(expected, back)
        valid([], 'a')
        valid(['a'], 'a.b')
        valid(['a', 'a.b'], 'a.b.c')

    def test_auto_import_parent(self):
        self.new_debug_symbol_file('b')
        self.new_debug_symbol_file('b.c')
        symbol = self.new_debug_symbol('a')
        symbol.add_import('b.c')

        self.write_symbol(symbol)
        self.gen_home_page('a')
        self.assert_html('a.html', '''
sflib: 
preload:         <script type="text/javascript" src="__builtin__.js"></script>
        <script type="text/javascript" src="b.js"></script>
        <script type="text/javascript" src="b/c.js"></script>
        <script type="text/javascript" src="a.js"></script>
''')

    def test_auto_self_parent_package(self):
        self.new_debug_symbol_file('another')
        symbol = self.new_debug_symbol('a')
        symbol.add_import('another')
        self.write_symbol(symbol)
        self.new_debug_symbol_file('a.b')
        self.new_debug_symbol_file('a.b.c')
        self.gen_home_page('a.b.c')
        self.assert_html('a/b/c.html', '''
sflib: ../../
preload:         <script type="text/javascript" src="../../__builtin__.js"></script>
        <script type="text/javascript" src="../../another.js"></script>
        <script type="text/javascript" src="../../a.js"></script>
        <script type="text/javascript" src="../../a/b.js"></script>
        <script type="text/javascript" src="../../a/b/c.js"></script>
''')

    def test_auto_remove_duplicate_import(self):
        self.new_debug_symbol_file('a')
        self.new_debug_symbol_file('a.b')
        self.new_debug_symbol_file('a.b.d')
        self.new_debug_symbol_file('a.c')
        self.new_debug_symbol_file('a.c.d')
        symbol = self.new_debug_symbol('a.b.c')
        symbol.add_import('a.b.d')
        symbol.add_import('a.c.d')

        self.write_symbol(symbol)
        self.gen_home_page('a.b.c')
        self.assert_html('a/b/c.html', '''
sflib: ../../
preload:         <script type="text/javascript" src="../../__builtin__.js"></script>
        <script type="text/javascript" src="../../a.js"></script>
        <script type="text/javascript" src="../../a/b.js"></script>
        <script type="text/javascript" src="../../a/b/d.js"></script>
        <script type="text/javascript" src="../../a/c.js"></script>
        <script type="text/javascript" src="../../a/c/d.js"></script>
        <script type="text/javascript" src="../../a/b/c.js"></script>
''')

    def test_include_depende_module_js(self):
        symbol = self.new_debug_symbol('a')
        symbol.add_js_file('for_a.js')
        self.write_symbol(symbol)

        symbol = self.new_debug_symbol('b')
        symbol.add_import('a')
        self.write_symbol(symbol)

        symbol = self.new_debug_symbol('c')
        symbol.add_import('b')
        self.write_symbol(symbol)

        self.gen_home_page('c')
        self.assert_html('c.html', '''
sflib: 
preload:         <script type="text/javascript" src="__builtin__.js"></script>
        <script type="text/javascript" src="for_a.js"></script>
        <script type="text/javascript" src="a.js"></script>
        <script type="text/javascript" src="b.js"></script>
        <script type="text/javascript" src="c.js"></script>
''')

    def test_read_symbol_in_libdir(self):
        symbol = self.new_debug_symbol('a')
        symbol.add_js_file('for_a.js')
        self.write_symbol_in_libdir(symbol)

        symbol = self.new_debug_symbol('b')
        symbol.add_import('a')
        self.write_symbol(symbol)

        symbol = self.new_debug_symbol('c')
        symbol.add_import('b')
        self.write_symbol(symbol)

        self.gen_home_page('c')
        self.assert_html('c.html', '''
sflib: 
preload:         <script type="text/javascript" src="__builtin__.js"></script>
        <script type="text/javascript" src="for_a.js"></script>
        <script type="text/javascript" src="a.js"></script>
        <script type="text/javascript" src="b.js"></script>
        <script type="text/javascript" src="c.js"></script>
''')
