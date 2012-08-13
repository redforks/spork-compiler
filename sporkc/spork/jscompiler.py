# -*- coding: utf-8 -*-
from __future__ import absolute_import

import ast
from ast import parse, NodeVisitor, copy_location
from functools import partial
from functional import compose, scanl
from itertools import izip, islice, chain, repeat
from copy import copy
from ConfigParser import SafeConfigParser
from contextlib import contextmanager
from collections import Sequence
import operator

from . import SporkError
from .collections import OrderedSet, eat
import spork._jsast as j
from .io import IOUtil, read_file
import spork._jsvisitors
from ._jsvisitors import Render, DebugRender, escapejs
from .internal import constf, nonef
from ._jsast import _safe_js_id

id = j.Name

BUILTIN_MODULE = '__builtin__'
BUILTIN_VAR = j.BUILTIN_VAR
BUILTIN_VAR_id = id(BUILTIN_VAR)
_undefined = j.Undefined()

MODULE_VAR = '$m'
MODULE_VAR_id = id(MODULE_VAR)
IMPORT_TMP_VAR = '$p'
IMPORT_TMP_VAR_id = id(IMPORT_TMP_VAR)
CLS_DEF_VAR = '$i'
CLS_DEF_VAR_id = id('$i')

class Symbol(object):
    gen_home_html = False

    def __init__(self, module, debug):
        self._imports = []
        self.module = module
        self._css_files = []
        self._js_files = []
        self.debug = debug

    def add_import(self, item):
        if item not in self._imports:
            self._imports.append(item)

    def _do_add_file(self, list, file):
        if file in list:
            raise SporkError('import duplicate file ' + file)
        list.append(file)

    def add_css_file(self, file):
        self._do_add_file(self._css_files, file)

    def add_js_file(self, file):
        self._do_add_file(self._js_files, file)

    def write(self, output):
        config = SafeConfigParser()
        def write_section(section, items):
            config.add_section(section)
            for key, item in items:
                config.set(section, str(key), item)

        def misc_section():
            return (
                ('gen_home_html', str(self.gen_home_html)),
                ('module', self.module),
                ('debug', str(self.debug)),
            )

        write_section('import', enumerate(self._imports))
        write_section('misc', misc_section())
        write_section('css files', enumerate(self._css_files))
        write_section('js files', enumerate(self._js_files))

        config.write(output)

    @staticmethod
    def read(f):
        def load_config(f):
            result = SafeConfigParser()
            result.readfp(f)
            return result

        def get_module(config):
            return config.get('misc', 'module')

        def get_debug(config):
            return config.getboolean('misc', 'debug')

        def get_gen_home_html(config):
            return config.getboolean('misc', 'gen_home_html')

        def get_files(section, config):
            items = config.items(section)
            result = [None] * len(items)
            for k, v in config.items(section):
                result[int(k)] = v
            return result

        get_css_files = partial(get_files, 'css files')
        get_js_files = partial(get_files, 'js files')
        get_imports = partial(get_files, 'import')

        config = load_config(f)
        module = get_module(config)
        debug = get_debug(config)
        result = Symbol(module, debug)
        result.gen_home_html = get_gen_home_html(config)
        result._css_files = get_css_files(config)
        result._js_files = get_js_files(config)
        result._imports = get_imports(config)

        return result

def compile(module_name, code, ioutil, **options):
    def pop_debug_option(option_name):
        is_debug = options.get('debug', True)
        return options.pop(option_name, is_debug)

    need_embsrc = partial(pop_debug_option, 'embsrc')
    need_pretty = partial(pop_debug_option, 'pretty')

    def embsrc(code):
        def include_embsrc(code):
            return code + "\n__src__ = '" + escapejs(code) + "'.splitlines()"

        if need_embsrc():
            return include_embsrc(code)
        else:
            return code

    def get_render(output):
        pretty = need_pretty()
        render_cls = DebugRender if pretty else Render
        return render_cls(output)

    def do_compile():
        embcode = embsrc(code)
        pyast = parse(embcode)
        return AstVisitor(module_name, options).visit(pyast)

    def open_module_file(ext):
        filename = get_module_filename(module_name, ext)
        return ioutil.open_write(filename)

    def render_js(jsast):
        output = open_module_file('.js')
        get_render(output).visit(jsast)

    def write_symbol(symbol):
        output = open_module_file('.symbol')
        symbol.write(output)
    
    jsast, symbols = do_compile()
    render_js(jsast)
    write_symbol(symbols)

def get_module_filename(module_name, ext):
    basename = module_name.replace('.', '/')
    return basename + ext

def _parent_modules(module):
    names = module.split('.')
    if len(names) == 1:
        return ()
    parents = iter(names[:-1])
    return scanl(lambda x, y: x + '.' + y, next(parents), parents)

def gen_home_page(libdir, outdir, module, template=None):
    # first look up imported module's symbol in libdir, then outdir

    to_symbol_filename = lambda m: get_module_filename(m, '.symbol')
    to_html_filename = lambda m: get_module_filename(m, '.html')
    to_js_filename = lambda m: get_module_filename(m, '.js')
    to_custom_template_filename = lambda m: get_module_filename(m, '.t.html')

    def load_symbol(outdir, module):
        filename = to_symbol_filename(module)
        try:
            f = outdir.open_read(filename)
        except IOError:
            try:
                f = libdir.open_read(filename)
            except IOError:
                print filename
                raise
        return Symbol.read(f)

    def gen_template_args(symbol):
        def sflib():
            return '../' * module.count('.')

        def all_imported_modules():
            result = [BUILTIN_MODULE]
            loading = set()

            def add_name(name):
                if name not in result:
                    result.append(name)

            def add_module(module):
                if module not in loading:
                    loading.add(module)
                    symbol = load_symbol(outdir, module)
                    all_imports = chain(_parent_modules(module), symbol._imports)
                    for m in all_imports:
                        add_module(m)
                    add_name(module)

            add_module(symbol.module)
            return result

        def preload():
            def imported_files(template, module_path, files):
                return (template % (sflib(), module_path, x) for x in files)

            template = '        <link rel="stylesheet" href="%s%s%s">' 
            css_files = partial(imported_files, template)

            template = '        <script type="text/javascript"' \
                ' src="%s%s%s"></script>'
            imported_js_files = partial(imported_files, template)

            def js_files(f):
                template = '        <script type="text/javascript"' \
                    ' src="%s%s"></script>'
                return template % (sflib(), f)

            lines = []
            js_lines = []
            for m in all_imported_modules():
                module_file = to_js_filename(m)
                module_path = os.path.split(module_file)[0]
                if module_path:
                    module_path += '/'
                msymbol = load_symbol(outdir, m)
                lines.extend(css_files(module_path, msymbol._css_files))
                js_lines.extend(imported_js_files(module_path, msymbol._js_files))
                js_lines.append(js_files(module_file))
            lines.extend(js_lines)
            return '\n'.join(lines)

        return {
            'sflib': sflib(),
            'preload': preload()
        }

    def get_default_template(symbol):
        custom_template = to_custom_template_filename(module)
        if outdir.exist(custom_template):
            return outdir.open_read(custom_template).read()
        if symbol.debug:
            return HTML_TEMPLATE_DEBUG
        else:
            return HTML_TEMPLATE

    def gen_content(symbol, template):
        template = template or get_default_template(symbol)
        return template % gen_template_args(symbol)

    def write_html(ioutil, module, content):
        filename = to_html_filename(module)
        f = ioutil.open_write(filename)
        f.write(content)

    symbol = load_symbol(outdir, module)
    if symbol.gen_home_html:
        content = gen_content(symbol, template)
        write_html(outdir, module, content)

def _dump_members(node):
    from inspect import getmembers
    print node.__class__.__name__, [n for n in getmembers(node) if not \
        n[0].startswith('_') and n[0] not in ('lineno', 'col_offset')]

ATTR = j.Attribute
SF_ATTR = partial(ATTR, BUILTIN_VAR_id)

def _o_bin_op(op, left, right):
    if isinstance(left, j.Num) and isinstance(right, j.Num):
        val = op(left.n, right.n)
        return j.Num(val)

def _special_bin_op(methodname, op, js_op, left, right):
    result = _o_bin_op(op, left, right)
    if result is not None:
        return result

    left_type, right_type = left.expr_type, right.expr_type
    if js_op and left_type == j.EXPR_TYPE_NUM == right_type:
        return js_op(left, right)

    def is_num_str(expr):
        return j.as_global_func_call(expr) == 'str' and\
                expr.args[0].expr_type == j.EXPR_TYPE_NUM
    if js_op is j.Plus and left_type == j.EXPR_TYPE_STR == right_type:
        if is_num_str(left) or is_num_str(right):
            if is_num_str(left):
                left = left.args[0]
            else:
                right = right.args[0]
        return js_op(left, right)

    method = ATTR(left, methodname)
    args = right,
    return j.Call(method, args)

def _pow(left, right):
    result = _o_bin_op(operator.pow, left, right)
    if result is not None:
        return result

    pow = SF_ATTR('pow')
    args = left, right
    return j.Call(pow, args)

def _shift_op(op, j_op, left, right):
    result = _o_bin_op(op, left, right)
    if result is not None:
        return result

    return j_op(left, right)

def _is_inited(expr):
    return j.Identical(expr, _undefined)

def _is_not_inited(expr):
    return j.Not_identical(expr, _undefined)

def _cmp_op(helper_func, js_op, left, right):
    if left.expr_type == j.EXPR_TYPE_NUM == right.expr_type:
        return js_op(left, right)

    cmp = SF_ATTR(helper_func)
    cmp_args = left, right
    return j.Call(cmp, cmp_args)

_eq = partial(_cmp_op, 'eq', j.Identical)
_gt = partial(_cmp_op, '__gt', j.Gt)
_ge = partial(_cmp_op, '__ge', j.Ge)
_lt = partial(_cmp_op, '__lt', j.Lt)
_le = partial(_cmp_op, '__le', j.Le)
del _cmp_op

def _ne(left, right):
    if left.expr_type == j.EXPR_TYPE_NUM == right.expr_type:
        return j.Not_identical(left, right)
    eq = _eq(left, right)
    return j.Logic_not(eq)

def _as_builtin_func(expr):
    if isinstance(expr, j.Call):
        attr = expr.val
        if isinstance(attr, j.Attribute):
            name = attr.value
            if j._is_builtin(name):
                return attr.attr

def is_JS(expr):
    return isinstance(expr, j.Js)

def _is_compatible_bool(expr):
    return expr.expr_type in (j.EXPR_TYPE_BOOL, j.EXPR_TYPE_NUM) or is_JS(expr)

def _do_force_bool(expr):
    bool_func = SF_ATTR('_bool')
    return j.Call(bool_func, (expr,))

def _force_bool(expr):
    if _is_compatible_bool(expr):
        return expr
    return _do_force_bool(expr)

def _clo(jsast, pyast):
    ''' clo: copy line offset info from pyast to jsast, returns jsast. '''
    return jsast.set_location(getattr(pyast, 'lineno', -1))

def _cplo(func):
    def _do(self, node, *args):
        result = func(self, node, *args)
        return _clo(result, node)
    return _do

class Call(ast.expr_context):
    pass

class ModuleName(ast.Name):
    pass

class Scope(object):
    def __init__(self, visitor):
        self.visitor = visitor
        self._var_idx = 0

    def unique_name(self):
        self._var_idx += 1
        return '$t' + str(self._var_idx)

    def unique_var(self):
        result = self.unique_name()
        self.add(result)
        return id(result)

    add = nonef

def _is_builtin_module(module_name):
    return module_name == BUILTIN_MODULE

class ModuleScope(Scope):
    def __init__(self, visitor, module_name):
        super(ModuleScope, self).__init__(visitor)
        self.symbols = set()
        self.module_name = module_name
        self.locals = OrderedSet()

    __predefined = {'None': j.Null(), 'True': j.True_(), 'False': j.False_(),
                'NotImplemented': _undefined}
    __known_globals = ['isinstance', 'hasattr', 'int', 'str', 'len', 'repr',
            'getattr']

    def add(self, symbol):
        if symbol.startswith('$t'):
            self.locals[symbol] = None

    def resolve(self, symbol, ctx):
        if symbol in self.locals:
            return id(symbol)
        if symbol in self.__predefined:
            return self.__predefined[symbol]
        elif symbol in self.__known_globals:
            return SF_ATTR(symbol)
        else:
            if self.visitor.check_global and isinstance(ctx, (ast.Load, Call)) \
                    and not _is_builtin_module(self.module_name):
                _get_global_var = SF_ATTR('_get_global_var')
                module_name = MODULE_VAR_id
                var_name = j.Str(_safe_js_id(symbol))
                return j.Call(_get_global_var, [module_name, var_name])
            else:
                return ATTR(MODULE_VAR_id, symbol)

class ParentedScope(Scope):
    def __init__(self, parent):
        super(ParentedScope, self).__init__(parent.visitor)
        self.parent = parent
        self.locals = OrderedSet()

class FunctionScope(ParentedScope):
    def __init__(self, parent, locals, args):
        super(FunctionScope, self).__init__(parent)
        self.locals.update(locals)
        self.args = set(args)

    def add(self, symbol):
        if symbol not in self.args:
            self.locals.add(symbol)

    def resolve(self, symbol, ctx):
        if symbol in self.locals or symbol in self.args:
            return id(symbol)
        else:
            parent = self.parent
            if isinstance(self.parent, ClassDefScope):
                parent = parent.parent
            return parent.resolve(symbol, ctx)

class ListCompScope(ParentedScope):
    def resolve(self, symbol, ctx):
        if symbol in self.locals:
            return id(symbol)
        else:
            return self.parent.resolve(symbol, ctx)

    def add(self, symbol):
        self.locals.add(symbol)

class ExceptionHandlerScope(ParentedScope):
    def __init__(self, parent, except_var):
        super(ExceptionHandlerScope, self).__init__(parent)
        self._var_idx = parent._var_idx
        self.except_var = except_var

    def resolve(self, symbol, ctx):
        if symbol == self.except_var:
            return id(symbol)
        else:
            return self.parent.resolve(symbol, ctx)

    def add(self, symbol):
        self.parent.add(symbol)

class ClassDefScope(ParentedScope):
    def resolve(self, symbol, ctx):
        if symbol in self.locals:
            return ATTR(CLS_DEF_VAR_id, symbol)
        else:
            return self.parent.resolve(symbol, ctx)

    def add(self, symbol):
        self.locals.add(symbol)

def _check_arg_count(func, count, args):
    if len(args) != count:
        if count == 0:
            desc = 'no arguments'
        elif count == 1:
            desc = 'exactly one argument'
        else:
            raise NotImplemented('more args not implemented.')
        raise TypeError(func + '() takes %s (%s given)' % (desc, len(args)))

def _expect_str_const_arg(arg):
    if not isinstance(arg, ast.Str):
        raise TypeError('expected str parameter.')

class AstVisitor(object):
    def __init__(self, module_name, options):
        # .__init__ should removed before call AstVisitor
        assert not module_name.endswith('.__init__')
        super(AstVisitor, self).__init__()
        self.module_name = module_name
        self._var_idx = 0
        self.debug = debug = options.get('debug', True)
        self.check_global = options.get('check_global', debug)
        self.srcmap = options.get('srcmap', debug)
        self.argcheck = options.get('argcheck', debug)
        self.scope = ModuleScope(self, module_name)
        self.__imported_spork_funcs = {}
        self.__spork_imported_as = None
        self._symbol = Symbol(module_name, debug)
        self._modules_imported = set()

    def __is_spork_module(self, node):
        return isinstance(node, ast.Name) and \
                node.id == self.__spork_imported_as

    def __is_spork_func(self, node, func):
        if isinstance(node, ast.Name):
            return node.id == func and func in self.__imported_spork_funcs
        if isinstance(node, ast.Attribute):
            return self.__is_spork_module(node.value) and node.attr == func
        return False

    def __as_spork_func(self, node):
        if isinstance(node, ast.Name):
            return self.__imported_spork_funcs.get(node.id)
        if isinstance(node, ast.Attribute) and \
            self.__is_spork_module(node.value):
            return self._spork_funcs[node.attr]
        return None

    def on_gen_home_html(self, node):
        _check_arg_count('gen_home_html', 0, node.args)
        self._symbol.gen_home_html = True
        return j.noneast

    def on_JS(self, node):
        def visit_item(item):
            if isinstance(item, ast.List):
                args = [visit_item(x) for x in item.elts]
                return j.Array(args)
            if isinstance(item, ast.Dict):
                items = []
                for k, v in izip(item.keys, item.values):
                    if not isinstance(k, ast.Str):
                        raise SporkError(
                        'JS() dict key must be str literal. line: ' +
                        str(k.lineno))
                    k = self.visit(k).s
                    v = visit_item(v)
                    items.append(j.Struct_item(k, v))
                return j.Struct(items)
            return self.visit(item)

        if len(node.args) != 1:
            raise SporkError(
                    "JS() function have exactly 1 argument. line: " +
                    str(node.lineno))

        arg = node.args[0]
        if isinstance(arg, ast.Str):
            return j.Js(node.args[0].s)
        elif isinstance(arg, (ast.List, ast.Dict)):
            return visit_item(arg)
        else:
            raise SporkError('Bad argument for JS() function. line: ' +
                    str(node.lineno))

    def on_import_css(self, node):
        _check_arg_count('import_css', 1, node.args)
        _expect_str_const_arg(node.args[0])
        self._symbol.add_css_file(node.args[0].s)
        return j.noneast

    def on_import_js(self, node):
        _check_arg_count('import_js', 1, node.args)
        _expect_str_const_arg(node.args[0])
        self._symbol.add_js_file(node.args[0].s)
        return j.noneast

    def on_no_arg_check(self, node):
        return j.noneast

    _spork_funcs = {
            'gen_home_html': on_gen_home_html,
            'JS': on_JS,
            'import_css': on_import_css,
            'import_js': on_import_js,
            'no_arg_check': on_no_arg_check,
            }

    del on_gen_home_html, on_import_css, on_JS, on_import_js, on_no_arg_check

    _on_head_importing = True

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        if isinstance(node, ast.stmt) and \
            not (isinstance(node, (ast.Import, ast.ImportFrom))):
            self._on_head_importing = False
        return visitor(node)

    def generic_visit(self, node):
        raise SporkError, 'Lack visit_%s method' % node.__class__.__name__

    def visit_With(self, node):
        body, expr, enter_var = node.body, node.context_expr, \
            node.optional_vars
        stat, context_var = self._unique_var_n_init(self.visit(expr))
        result = [stat]

        enter = ATTR(context_var, '__enter__')
        enter = j.Call(enter, ())
        if enter_var:
            enter = j.Assign(self.visit(enter_var), enter)
        enter = j.Expr_stat(enter)
        result.append(enter)

        exc, exc_var = self._unique_var_n_init(j.True_())
        result.append(exc)

        catch_var = self._unique_var()
        catch_body = []
        catch_body.append(j.AssignStat(exc_var, j.False_()))
        exit_func = ATTR(context_var, '__exit__')
        exit_call = j.Call(exit_func, [ATTR(catch_var,
            '__class__'), catch_var, j.Null()])
        exit_call = j.Logic_not(exit_call)
        if_exit = j.If(exit_call, [j.Throw(catch_var)], None)
        catch_body.append(if_exit)
        catch = j.TryHandler(catch_var, catch_body)

        exit_call = j.Expr_stat(j.Call(exit_func, (j.Null(), j.Null(),
            j.Null())))
        finally_if = j.If(exc_var, (exit_call,), None)
        finally_ = j.Finally((finally_if,))
        try_stat = j.Try(self._visit_stats(body), catch, finally_)
        result.append(try_stat)
        return result

    def _remove_docstring(self, node):
        body = node.body
        if body and isinstance(body[0], ast.Expr) and \
                isinstance(body[0].value, ast.Str):
            del body[0]

    def visit_Module(self, node):
        def import_parent_packages(m):
            pkg, _, module_name = m.rpartition('.')
            if pkg:
                names = list(self.__get_import_seq(pkg))
                result = self.__gen_import_stat(names[:-1], node)
                e = self.__gen_import_expr(names[-1])
                e = j.AssignStat(ATTR(e, module_name), MODULE_VAR_id)
                result.append(e)
                return result
            return ()

        self._remove_docstring(node)
        
        m = self.module_name
        stats = []
        if _is_builtin_module(m):
            stats.append(j.Declare_var_stat(MODULE_VAR, j.Struct(())))
            stats.append(j.AssignStat(ATTR(MODULE_VAR_id, '__debug__'),
                j.True_() if self.debug else j.False_()))
            stats.append(j.AssignStat(
                ATTR(MODULE_VAR_id, '__file__'),
                j.Str(get_module_filename(m, '.py'))))
        else:
            is_load = j.Call(SF_ATTR('_module_loaded'), (j.Str(m),))
            stats.append(j.If(is_load, (j.Return(None),), None))
            module_obj = j.New_object(SF_ATTR('module'),
                    (j.Str(m), j.Str(get_module_filename(m, '.py'))))
            stats.append(j.Declare_var_stat(MODULE_VAR, module_obj))
            stats.extend(import_parent_packages(m))

        stats.extend(self._visit_stats(node.body))
        if self.srcmap:
            stats.append(j.AssignStat(
                ATTR(MODULE_VAR_id, '__srcmap__'),
                j.SrcMap()))
        vars = [IMPORT_TMP_VAR]
        vars.extend(self.scope.locals)
        stats.insert(0, j.DeclareMultiVar(vars))

        module_func = j.FunctionDef((), stats)
        module_stat = j.Expr_stat(j.Call(module_func, ()))
        return j.File((module_stat,)), self._symbol

    def visit_Expr(self, node):
        result = self.visit(node.value)
        if not is_JS(result):
            result = j.Expr_stat(result)
        return result

    @_cplo
    def visit_Num(self, node):
        return j.Num(node.n)

    @_cplo
    def visit_Name(self, node):
        return self.scope.resolve(node.id, getattr(node, 'ctx', None))

    def visit_ModuleName(self, node):
        return id(node.id)

    def visit_Str(self, node):
        return j.Str(node.s)

    def _visit_list_tuple(self, jstype, node):
        type = SF_ATTR(jstype)
        args = [self.visit(n) for n in node.elts]
        return j.Call(type, (j.Array(args),))

    @_cplo
    def visit_Tuple(self, node):
        return self._visit_list_tuple('tuple', node)

    @_cplo
    def visit_List(self, node):
        return self._visit_list_tuple('list', node)

    @_cplo
    def visit_Dict(self, node):
        def visit_item(p):
            return j.Array([self.visit(n) for n in p])

        v = SF_ATTR('dict')
        arr = [visit_item(n) for n in izip(node.keys, node.values)]
        return j.Call(v, (j.Array(arr),))

    def _unique_name(self):
        return self.scope.unique_name()

    def _unique_var(self):
        return self.scope.unique_var()

    def _unique_var_n_init(self, initval):
        var = self._unique_var()
        return j.AssignStat(var, initval), var

    def _do_assign(self, target, value):
        def do_subscript(target, value):
            v, slice = target.value, target.slice
            result = j.Expr_stat(j.Call(ATTR(self.visit(v), '__setitem__'),
                    [self.visit(slice), value]))
            return _clo(result, target),

        def do_normal(target, value):
            if not isinstance(self.scope, FunctionScope):
                self.scope.add(target.id)
            result = j.AssignStat(self.visit(target), value)
            return _clo(result, target),

        def do_tuple(target, value):
            n = j.Num
            for idx, item in enumerate(target.elts):
                right = j.Call(ATTR(value, '__fastgetitem__'), (n(idx),))
                for stat in self._do_assign(item, right):
                    yield stat
            if self.debug:
                cond_expr = ATTR(value, '__len__')
                cond_expr = j.Call(cond_expr, ())
                right = j.Num(len(target.elts))
                cond_expr = j.Not_identical(cond_expr, right)

                msg = j.Str('too many values to unpack')
                raise_stat = j.Throw(j.Call(SF_ATTR('ValueError'), (msg,)))
                yield j.If(cond_expr, (raise_stat,), None)

        def do_attribute(target, value):
            val, attr = target.value, target.attr
            attr = _safe_js_id(attr)
            result = j.Call(SF_ATTR('_setattr'), [
                    self.visit(val), j.Str(attr), value])
            return _clo(j.Expr_stat(result), target),

        funcs = {
            ast.Subscript: do_subscript,
            ast.Tuple: do_tuple,
            ast.Attribute: do_attribute,
            }

        return funcs.get(type(target), do_normal)(target, value)

    def visit_Assign(self, node):
        class NameVisitor(NodeVisitor):
            def __init__(self):
                super(NameVisitor, self).__init__()
                self.names = set()

            def visit_Name(self, node):
                self.names.add(node.id)

            @staticmethod
            def scan(node):
                visitor = NameVisitor()
                visitor.visit(node)
                return visitor.names

        def is_assign_one_by_one(left, value):
            if isinstance(value, ast.Tuple) and isinstance(left, ast.Tuple):
                left_len, right_len = len(left.elts), len(value.elts)
                if left_len > 1:
                    if right_len != left_len:
                        fmt = ('too many value to unpack (expected %s),'
                            ' at line %s')
                        raise SporkError(fmt % (left_len, node.lineno))
                    left_ids = NameVisitor.scan(left)
                    right_ids = NameVisitor.scan(value)
                    return left_ids.isdisjoint(right_ids)

        def assign_one_by_one(target, value):
            pairs = izip(target.elts, value.elts)
            visit, do_assign = self.visit, self._do_assign
            return chain.from_iterable(do_assign(left, visit(right))
                    for left, right in pairs)

        targets, value = node.targets, node.value
        if len(targets) == 1 and is_assign_one_by_one(targets[0], value):
            return tuple(assign_one_by_one(targets[0], value))

        value = self.visit(value)
        if len(targets) == 1 and not isinstance(targets[0], ast.Tuple):
            return tuple(self._do_assign(targets[0], value))

        if j.isliteral(value) or isinstance(value, j.Name):
            result = []
        else:
            tmpvardeclare, tmpvar = self._unique_var_n_init(value)
            tmpvardeclare = _clo(tmpvardeclare, value)
            value = tmpvar
            result = [tmpvardeclare]

        for t in targets:
            result.extend(self._do_assign(t, value))

        return result

    def _do_getattr(self, expr, attrname):
        attrname = _safe_js_id(attrname)
        return j.Call(SF_ATTR('_getattr'), [self.visit(expr), j.Str(attrname)])

    @_cplo
    def visit_Attribute(self, node):
        if isinstance(node.ctx, ast.Load):
            return self._do_getattr(node.value, node.attr)
        return ATTR(self.visit(node.value), node.attr)

    @_cplo
    def visit_Subscript(self, node):
        v = ATTR(self.visit(node.value), '__getitem__')
        return j.Call(v, (self.visit(node.slice),))

    def visit_Index(self, node):
        return self.visit(node.value)

    def visit_Slice(self, node):
        step = node.step
        if not step:
            step = ast.Num(1)
        return j.Call(SF_ATTR('slice'),
                [self.visit(node.lower), self.visit(node.upper),
                    self.visit(step)])

    def visit_NoneType(self, node):
        return j.Null()

    @_cplo
    def visit_Call(self, node):
        func = node.func
        func.ctx = Call()
        try:
            spork_f = self.__as_spork_func(func)
        except KeyError:
            raise AttributeError(
                    "'module' object has no attribute '%s'" % func.attr)
        if spork_f is not None:
            return spork_f(self, node)

        if node.keywords or node.starargs or node.kwargs:
            if isinstance(func, ast.Attribute):
                strnode = ast.Str(func.attr)
                o = func.value
            elif isinstance(func, ast.Name):
                if isinstance(self.scope, ModuleScope):
                    strnode = j.Str(func.id)
                    o = ModuleName(id=self.module_name)
                else:
                    strnode = func
                    o = None
            else:
                assert False

            args = [self.visit(n) for n in (o, strnode,
                node.starargs, node.kwargs)]
            arr = [j.Struct([self.visit(n) for n in node.keywords])]
            if node.args:
                arr.extend(self.visit(n) for n in node.args)
            args.append(j.Array(arr))
            if node.starargs is None and node.kwargs is None:
                del args[2:4]
                v = id('pyjs_set_arg_call')
            else:
                v = id('pyjs_kwargs_call')
            return j.Call(v, args)

        def optimized_super(expr):
            val = expr
            func = val.func
            args = val.args
            if isinstance(func, ast.Attribute):
                attr_name = func.attr
                val = func.value
                if isinstance(val, ast.Call):
                    func = val.func
                    if isinstance(func, ast.Name) and \
                            func.id == 'super' and len(val.args) == 2:
                        super_args = list(val.args)
                        super_args.append(ast.Str(attr_name))
                        expr = ast.Call(
                            ast.Name('_get_super_method', func.ctx),
                            super_args,
                            (), None, None)
                        expr = ast.Call(expr, args, (), None,
                                None)
            return expr

        node = optimized_super(node) 
        v = self.visit(node.func)
        args = [self.visit(n) for n in node.args]
        return j.Call(v, args)

    def visit_keyword(self, node):
        return j.Struct_item(node.arg, self.visit(node.value))

    def _visit_stats(self, stats):
        result = []
        for item in stats:
            js = self.visit(item)
            if not js:
                continue
            result.append(js)
        return result

    def _force_bool_expr(self, expr):
        return _force_bool(self.visit(expr))

    def visit_If(self, node):
        def is_debug(n):
            return isinstance(n, ast.Name) and n.id == '__debug__'

        test = node.test
        if is_debug(test):
            n = node.body if self.debug else node.orelse
            return self._visit_stats(n)
        elif isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not) \
                and is_debug(test.operand):
            n = node.orelse if self.debug else node.body
            return self._visit_stats(n)

        truepart = self._visit_stats(node.body)
        elsepart = self._visit_stats(node.orelse) if node.orelse else None
        return _clo(j.If(self._force_bool_expr(node.test),
            truepart, elsepart), node)

    visit_Assert = visit_Global = visit_Pass = constf(j.noneast)

    @_cplo
    def visit_Assert(self, node):
        if not self.debug:
            return j.noneast
        test, msg = node.test, node.msg
        call = j.Call(SF_ATTR('_assert'), [self.visit(test),
            self.visit(msg)])
        return j.Expr_stat(call)

    def __in(left, right):
        return j.Call(ATTR(right, '__contains__'), (left,))

    __compare_op_maps = {
            ast.Is: j.Identical,
            ast.IsNot: j.Not_identical,
            ast.Gt: _gt,
            ast.GtE: _ge,
            ast.Lt: _lt,
            ast.LtE: _le,
            ast.Eq: _eq,
            ast.NotEq: _ne,
            ast.In: __in,
            ast.NotIn: compose(j.Logic_not, __in),
        }

    @_cplo
    def visit_Compare(self, node):
        def check_oprand(oprand):
            if not isinstance(oprand, (ast.Num, ast.Str, ast.Name)):
                msg = 'In chain cmp, only literal and variable is allowed '\
                    'in the middle'
                raise NotImplementedError(msg)
            return True
        all(check_oprand(oprand) for oprand in node.comparators[0:-1])

        last = node.left
        result = None
        for op, oprand in zip(node.ops, node.comparators):
            exp = self.__compare_op_maps[type(op)](self.visit(last),
                    self.visit(oprand))
            last = oprand
            if result is not None:
                result = j.Logic_and(result, exp)
            else:
                result = exp
        return result

    __bin_op_maps = {
            ast.Add: partial(_special_bin_op, '__add__', operator.add, j.Plus),
            ast.Sub: partial(_special_bin_op, '__sub__', operator.sub, j.Sub),
            ast.Mult: partial(_special_bin_op, '__mul__', operator.mul, j.Mul),
            ast.Div: partial(_special_bin_op, '__div__', operator.truediv, None),
            ast.Mod: partial(_special_bin_op, '__mod__', operator.mod, j.Mod),
            ast.FloorDiv: partial(_special_bin_op, '__floordiv__',
                operator.floordiv, None),
            ast.Pow: _pow,
            ast.BitAnd: partial(_special_bin_op, '__and__', operator.and_, None),
            ast.BitOr: partial(_special_bin_op, '__or__', operator.or_, None),
            ast.BitXor: partial(_special_bin_op, '__xor__', operator.xor, None),
            ast.RShift: partial(_shift_op, operator.rshift,
                j.Bit_rshift_zero_fill),
            ast.LShift: partial(_shift_op, operator.lshift, j.Bit_lshift)
        }

    @_cplo
    def visit_BinOp(self, node):
        t = self.__bin_op_maps[type(node.op)]
        return t(self.visit(node.left), self.visit(node.right))

    def _logic_and_or(self, left, right, condition_op, js_logic_op):
        if _is_compatible_bool(left):
            return js_logic_op(left, right)

        assign, first_var = self._unique_var_n_init(left)
        assign = assign.expr
        bool_first = _do_force_bool(first_var)
        cond_expr = condition_op(bool_first, right, first_var)
        return j.CommaOp((assign, cond_expr))

    def _logic_and(self, left, right):
        op = j.Conditional_op
        return self._logic_and_or(left, right, op, j.Logic_and)

    def _logic_or(self, left, right):
        op = lambda bool_first, right_exp, left_var: \
                j.Conditional_op(bool_first, left_var, right_exp)
        return self._logic_and_or(left, right, op, j.Logic_or)

    __bool_op_maps = {
            ast.And: _logic_and,
            ast.Or: _logic_or
        }
    del _logic_and, _logic_or

    def visit_BoolOp(self, node):
        t = self.__bool_op_maps[type(node.op)]
        values = iter(node.values)
        func = lambda last,cur: t(self, last, self.visit(cur))
        return reduce(func, values, self.visit(next(values)))

    __unary_op_maps = {
            ast.Not: j.Logic_not,
            ast.Invert: j.Bit_inv,
            ast.USub: lambda o: j.Call(ATTR(o, '__neg__'), ()),
            ast.UAdd: j.Unary_add,
        }

    @_cplo
    def visit_UnaryOp(self, node):
        t = self.__unary_op_maps[type(node.op)]
        val = self.visit(node.operand)
        if isinstance(node.op, ast.Not):
            val = _force_bool(val)
        return t(val)

    @_cplo
    def visit_IfExp(self, node):
        return j.Conditional_op(
                _force_bool(self.visit(node.test)),
                self.visit(node.body), self.visit(node.orelse))

    @_cplo
    def visit_Repr(self, node):
        return j.Call(SF_ATTR('repr'), (self.visit(node.value),))

    def __pow_assign(left, right):
        return j.Assign(left, _pow(left, right))

    def visit_AugAssign(self, node):
        left = copy(node.target)
        left.ctx = ast.Load()
        n = ast.Assign([node.target], 
                copy_location(
                    ast.BinOp(left, node.op, node.value), node))
        result = self.visit(n)
        assert len(result) == 1
        return result[0]

    def visit_Delete(self, node):
        targets = node.targets
        result = []
        for t in targets:
            if isinstance(t, ast.Subscript):
                idx = self.visit(t.slice)
                call = j.Call(ATTR(self.visit(t.value),
                    '__delitem__'), [idx])
                result.append(_clo(j.Expr_stat(call), t))
            elif isinstance(t, ast.Attribute):
                call = j.Call(SF_ATTR('delattr'),
                        [self.visit(t.value), j.Str(t.attr)])
                call = j.Expr_stat(call)
                result.append(_clo(call, t))
            elif isinstance(t, ast.Name):
                result.append(_clo(j.Delete_stat(self.visit(t)), t))
            else:
                raise TypeError('do not support del %s.' % type(t))

        return result

    @_cplo
    def visit_Print(self, node):
        if node.dest:
            raise NotImplementedError, \
                'print with redirection is not implemented.'
        result = j.Call(SF_ATTR('print_'),
            (j.Array([self.visit(n) for n in node.values]), 
            j.Num(1) if node.nl else j.Num(0)))
        return j.Expr_stat(result)

    @_cplo
    def visit_Raise(self, node):
        if not node.inst:
            call = self.visit(node.type)
        else:
            call = j.Call(self.visit(node.type), (self.visit(node.inst),))
        return j.Throw(call)

    @_cplo
    def visit_Break(self, node):
        return j.Break()

    @_cplo
    def visit_Continue(self, node):
        return j.Continue()

    def function_scope(func):
        def result(self, node):
            scaner = LocalVarScaner()
            scaner.scan(node)
            if hasattr(node, 'name'):
                self.scope.add(node.name)
            with self._push_scope(FunctionScope(self.scope, scaner.local_vars, scaner.args)):
                return func(self, node)

        return result

    @_cplo
    @function_scope
    def visit_Lambda(self, node):
        stats, args = self._do_visit_arguments(node, self.argcheck)
        stats.append(j.Return(self.visit(node.body)))
        return j.FunctionDef(args, stats)

    def _do_visit_arguments(self, node, argcheck, ignore_self=False):
        def do_argcheck(has_arg_prep_stat, node):
            def gen_check_js(funcname, op, arg_count, adj):
                s_arg_count = str(arg_count)
                return ('if (arguments.length' + op + s_arg_count + ')'
                    "{\n  throw " + BUILTIN_VAR + ".TypeError("
                    "'"+funcname+"() takes " + adj + ' ' + s_arg_count +
                    " arguments ('+arguments.length+' given)');\n}\n")

            args = node.args
            minlen = len(args.args)
            if ignore_self:
                minlen -= 1
            funcname = getattr(node, 'name', '<lambda>')

            if not has_arg_prep_stat:
                return j.Js(gen_check_js(funcname, '!==', minlen, 'exactly'))
            else:
                maxlen = minlen
                minlen -= len(args.defaults)
                js = elsejs = ''

                if minlen:
                    js = gen_check_js(funcname, '<', minlen, 'at least')

                if args.kwarg:
                    if not args.vararg:
                        elsejs = gen_check_js(funcname, '>', minlen + 1,
                            'at most')
                elif args.defaults and not args.vararg:
                    elsejs += gen_check_js(funcname, '>', maxlen, 'at most')
                if js or elsejs:
                    if elsejs:
                        js = (js + 'else ' + elsejs) if js else (js + elsejs)
                    return j.Js(js)
                return j.noneast

        def prepare_varargs(name, has_kwarg):
            start = len(args)
            arguments = id('arguments')

            slice = ATTR(ATTR(ATTR(id('Array'), 'prototype'), 'slice'), 'call')
            slice_args = [arguments, j.Num(start)]
            if has_kwarg:
                slice_args.append(j.Sub(ATTR(arguments, 'length'),
                    j.Num(1)))
            return j.Declare_var_stat(name, j.Call(SF_ATTR('tuple'), [
                    j.Call(slice, slice_args)
                ])),

        def prepare_kwarg(name, vararg):
            var_arguments = id('arguments')
            arguments_length = ATTR(var_arguments, 'length')
            namevar = id(name)
            yield j.Declare_var_stat(name, 
                j.Conditional_op(j.Gt(arguments_length, j.Num(len(args))),
                    j.Subscript(var_arguments, 
                        j.Sub(arguments_length, j.Num(1))),
                    j.Call(SF_ATTR('__empty_kwarg'), [])))

            if vararg:
                if_body = (
                    j.Expr_stat(j.Call(
                        ATTR(ATTR(id(vararg), 'l'), 'push'),
                        [namevar])),
                    j.AssignStat(namevar, j.Call(SF_ATTR('__empty_kwarg'), ()))
                )
                yield j.If(
                    j.Identical(ATTR(namevar, '_pyjs_is_kwarg'),
                        _undefined), if_body, None)

            if args:
                kwargvar = id(name)
                body = [j.AssignStat(kwargvar,
                    j.Call(SF_ATTR('dict'), (j.Struct(()),)))]
                else_ = None
                for arg in args:
                    argvar = self.visit(arg)
                    cond = j.Eq(j.Call(
                        SF_ATTR('get_pyjs_classtype'), (argvar,)), j.Str('dict'))
                    else_ = [j.If(_is_not_inited(argvar), (j.If(cond, (
                        j.AssignStat(kwargvar, argvar),
                        j.AssignStat(argvar, 
                            j.Subscript(id('arguments'), j.Num(len(args))))
                        ), None),), else_)]
                if else_:
                    body.extend(else_)
                yield j.If(_is_inited(kwargvar), body, None)

        def build_default_arg(arg, val):
            var = self.visit(arg)
            cond = _is_not_inited(var)
            assign = j.Assign(var, self.visit(val))
            return j.Expr_stat(j.Logic_or(cond, assign))

        args, vararg, kwarg = node.args.args, node.args.vararg, node.args.kwarg
        defaults = node.args.defaults
        if ignore_self:
            args = args[1:]
        stats = []
        if vararg:
            if defaults:
                raise NotImplementedError(
                'use both default argument and vararg is not supported')
            stats.extend(prepare_varargs(vararg, kwarg))
        if kwarg:
            stats.extend(prepare_kwarg(kwarg, vararg))
        if defaults:
            stats.extend(build_default_arg(arg, val) for arg, val in
                    izip(args[-len(defaults):], defaults))

        if argcheck:
            stats.insert(0, do_argcheck(stats, node))
        return stats, [self.visit(n) for n in args]

    @function_scope
    def visit_FunctionDef(self, node):
        def is_no_arg_check_decor(decor_list):
            return len(decor_list) == 1 and \
                    self.__is_spork_func(decor_list[0], 'no_arg_check')

        self._remove_docstring(node)

        if isinstance(self.scope.parent, ClassDefScope):
            return self.visit_MethodDef(node)

        argcheck = self.argcheck
        if node.decorator_list:
            if is_no_arg_check_decor(node.decorator_list):
                argcheck = False
            else:
                raise NotImplementedError, 'function decorator is not supported'

        stats = []
        argstats, arglist = self._do_visit_arguments(node, argcheck)

        stats.extend(argstats)
        stats.extend(self._visit_stats(node.body))
        if self.scope.locals:
            stats.insert(0, j.DeclareMultiVar(self.scope.locals))
        self._auto_return(stats)
        f = j.FunctionDef(arglist, stats,
                j._safe_js_id(node.name) if self.debug else None)

        f = j.Call(id('pyjs__bind_func'), (
                j.Str(j._safe_js_id(node.name)),
                f, j.Num(0), self.build_js_args(node.args)
            ))
        funcvar = self.scope.parent.resolve(node.name, getattr(node, 'ctx',
            None))
        j_as = j.AssignStat
        return _clo(j_as(funcvar, f), node)
        
    def build_js_args(self, args):
        s = j.Str
        def _arg_def(arg, val):
            arr = [s(j._safe_js_id(arg.id))]
            if val:
                arr.append(self.visit(val))
            return j.Array(arr)

        vararg, kwarg = args.vararg, args.kwarg
        arr = [s(n) if n else j.Null() for n in (vararg, kwarg)]
        arr.extend(_arg_def(arg, v) for arg, v in izip(args.args,
            chain(repeat(None, len(args.args) - len(args.defaults)),
                args.defaults)))
        return j.Array(arr)

    def _auto_return(self, stats):
        if not stats or not isinstance(stats[-1], (j.Return, j.Throw)):
            stats.append(j.Return(j.Null()))

    def visit_MethodDef(self, node):
        def do_class(args):
            if not args:
                raise SporkError("lack `cls' arguments.")
            thisvar = j.This()
            arg = args[0]
            return [j.Declare_var_stat(arg.id, ATTR(thisvar,
                'prototype'))]

        def do_normal(args):
            if not args:
                raise SporkError("lack `self' argument.")
            thisvar = j.This()
            truepart = j.Declare_var_stat(args[0].id, thisvar)
            return [truepart]

        def do_static(args):
            return []

        funcs = [do_static, do_normal, do_class]
        del do_class, do_normal, do_static

        NORMAL, STATIC, CLASS = 1, 0, 2
        method_type = NORMAL
        name, body, args = node.name, node.body, node.args
        decorator_list = node.decorator_list
        no_arg_check = False
        for decorator in decorator_list[:]:
            if self.__is_spork_func(decorator, 'no_arg_check'):
                no_arg_check = True
                decorator_list.remove(decorator)

            if isinstance(decorator, ast.Name):
                if decorator.id == 'staticmethod':
                    method_type = STATIC
                    decorator_list.remove(decorator)
                elif decorator.id == 'classmethod':
                    method_type = CLASS
                    decorator_list.remove(decorator)

        stats = []
        stats.extend(funcs[method_type](args.args))
        argstats, arglist = self._do_visit_arguments(node,
                not no_arg_check and self.argcheck, method_type != STATIC)
        stats.extend(argstats)
        stats.extend(self._visit_stats(body))
        if self.scope.locals:
            stats.insert(0, j.DeclareMultiVar(self.scope.locals))
        self._auto_return(stats)

        result = j.Call(id('pyjs__bind_method'), (
            j.Str(j._safe_js_id(name)), 
            j.FunctionDef(arglist, stats,
                j._safe_js_id(name) if self.debug else None), 
            j.Num(method_type), self.build_js_args(args)
            ))

        with self._push_scope(self.scope.parent):
            for decor in decorator_list:
                result = j.Call(self.visit(decor), [result])

        result = j.AssignStat(ATTR(CLS_DEF_VAR_id, name), result)
        return _clo(result, node)

    @_cplo
    def visit_Return(self, node):
        return j.Return(self.visit(node.value))

    def visit_For(self, node):
        target, iter, orelse, body = node.target, node.iter, node.orelse, \
            node.body

        if orelse:
            raise NotImplementedError, 'else in loop is not implemented.'

        def is_range(node):
            if not isinstance(node, ast.Call):
                return False
            func = node.func
            return isinstance(func, ast.Name) and func.id in ('range', 'xrange') \
                    and node.kwargs is None and node.starargs is None \
                    and not node.keywords and len(node.args) == 1

        def try_optimize():
            if is_range(iter):
                stop = iter.args[0]
                self.scope.add(target.id)
                init = j.Assign(self.visit(target), j.Num(0))
                stats = []
                if not isinstance(stop, ast.Num):
                    stat, stop = self._unique_var_n_init(self.visit(stop))
                    stats.append(stat)
                else:
                    stop = self.visit(stop)
                cond = j.Lt(self.visit(target), stop)
                inc = j.Inc_postfix(self.visit(target))
                stat = j.For(init, cond, inc, self._visit_stats(body)),
                stats.append(stat)
                return stats
            return None

        def as_normal():
            assert isinstance(target, (ast.Tuple, ast.Name))

            is_tuple = isinstance(target, ast.Tuple)
            right = j.Call(SF_ATTR('_iter_init'), (self.visit(iter),))
            itervardeclare, iterfunc = self._unique_var_n_init(right)

            right = j.Call(iterfunc, ())
            tmp_var = self._unique_var() if is_tuple else target
            itervar_assign = tuple(self._do_assign(tmp_var, right))
            assert len(itervar_assign) == 1
            itervar_assign = itervar_assign[0].expr
            itervar = itervar_assign.left
            cond_expr = j.Not_identical(itervar_assign, j.Undefined())

            stats = list(self._do_assign(target, tmp_var)) if is_tuple else []
            stats += self._visit_stats(body)
            w = j.While(cond_expr, stats)

            return _clo(itervardeclare, node), _clo(w, node)

        return try_optimize() or as_normal()

    @_cplo
    def visit_While(self, node):
        body, orelse, test = node.body, node.orelse, node.test
        if orelse:
            raise NotImplementedError, 'else in loop is not implemented.'
        return j.While(self._force_bool_expr(test), self._visit_stats(body))

    @_cplo
    def visit_TryExcept(self, node):
        errvar = self._unique_name()
        with self._push_scope(ExceptionHandlerScope(self.scope, errvar)):
            errvar = id(errvar)
            stats = []
            stats.append(j.AssignStat(errvar,
                j.Call(SF_ATTR('_errorMapping'), (errvar,))))

            handlers, body, orelse = node.handlers, node.body, node.orelse
            if orelse:
                raise NotImplementedError, 'else in try is not implemented.'

            s = stats
            for h in handlers:
                stat, elsepart = self._do_ExceptHandler(h, errvar)
                s.append(stat)
                s = elsepart
            if handlers[-1].type:
                s.append(j.Throw(errvar))
            catch = j.TryHandler(errvar, stats)
            catch = _clo(catch, node)

            return j.Try(self._visit_stats(body), catch)

    @_cplo
    def visit_TryFinally(self, node):
        body, finalbody = node.body, node.finalbody
        return j.Try(self._visit_stats(body),
                _clo(j.Finally(self._visit_stats(finalbody)), finalbody[0]))

    def _do_ExceptHandler(self, node, errvar):
        body, name, type = node.body, node.name, node.type
        if type:
            cond = j.Call(SF_ATTR('isinstance'), [errvar, self.visit(type)])
            ifstats = []
            if name:
                ifstats.append(j.AssignStat(self.visit(name), errvar))
            ifstats.extend(self._visit_stats(body))
            elsepart = []
            return j.If(cond, ifstats, elsepart), elsepart
        else:
            return self._visit_stats(body), ()

    @_cplo
    def visit_ClassDef(self, node):
        class ClsInstanceScanner(spork._jsvisitors.AstVisitor):
            exist = False
            def __init__(self):
                super(ClsInstanceScanner, self).__init__(None)

            def visit_Name(self, node):
                if node.id == CLS_DEF_VAR:
                    self.exist = True

            def generic_visit(self, node):
                if isinstance(node, str):
                    return

                if isinstance(node, (tuple, list)):
                    for item in node:
                        self.visit(item)
                    return

                for field in node._fields:
                    val = getattr(node, field)
                    if val is not None:
                        self.visit(val)

        def is_ref_cls_instance(node):
            scanner = ClsInstanceScanner()
            scanner.visit(node)
            return scanner.exist

        if isinstance(self.scope, ClassDefScope):
            raise NotImplementedError( \
                    'class defined in class is not supported.')

        self._remove_docstring(node)
        with self._push_scope(ClassDefScope(self.scope)):
            bases, body, name = node.bases, node.body, node.name
            if not bases and name != 'object':
                raise NotImplementedError(_('old style class is not supported.'))
            if node.decorator_list:
                raise NotImplementedError(
                        _('decorator on class is not supported.'))

            cls_def = []
            stats = [j.Declare_var_stat(CLS_DEF_VAR, j.Struct(cls_def))]
            members = self._visit_stats(body)
            while members:
                member = members[0]
                while isinstance(member, Sequence):
                    members[0:1] = member
                    member = members[0]

                if isinstance(member, j.Expr_stat):
                    assign = member.expr
                    left, right = assign.left, assign.right
                    if not isinstance(left, j.Attribute) or\
                            is_ref_cls_instance(right):
                        break
                    else:
                        cls_def.append(j.Struct_item(left.attr, right))
                        del members[0]
                else:
                    break
            stats.extend(members)

        if len(node.bases) == 1:
            bases = self.visit(node.bases[0])
            create_func = 'pyjs__class_function_single_base'
        else:
            bases = j.Array([self.visit(n) for n in node.bases])
            create_func = 'pyjs__class_function'

        cls_instance = j.Call(id('pyjs__class_instance'),
            (j.Str(j._safe_js_id(name)), j.Str(self.module_name)))
        args = cls_instance, CLS_DEF_VAR_id, bases
        create_cls = j.Call(id(create_func), args)
        stats.append(j.Return(create_cls))

        left = self.scope.resolve(name, None)
        right = j.FunctionDef((), stats)
        right = j.Call(right, ())
        return j.AssignStat(left, right)

    def __get_import_seq(self, module_name):
        combine = lambda x, y: x + '.' + y
        names = iter(module_name.split('.'))
        add_import = self._symbol.add_import if self._on_head_importing else\
                nonef
        for item in scanl(combine, next(names), names):
            add_import(item)
            yield item

    def __gen_import_expr(self, module_name):
        self._modules_imported.add(module_name)
        return j.Call(SF_ATTR('import_'), [j.Str(module_name)])

    def __gen_import_stat(self, module_names, node=None):
        def do_gen(module_name):
            if not module_name in self._modules_imported:
                self._modules_imported.add(module_name)
                r = self.__gen_import_expr(module_name)
                r = j.Expr_stat(r)
                return _clo(r, node)
        result = []
        for m in module_names:
            stat = do_gen(m)
            if stat is not None:
                result.append(stat)
        return result

    def visit_Import(self, node):
        names = node.names
        result = []
        for name, asname in self.__iter_aliases(names):
            if name == '__spork__':
                self.__spork_imported_as = asname
            else:
                modules = iter(self.__get_import_seq(name))

                e = self.__gen_import_expr(next(modules))
                left = self.scope.resolve(asname, None)
                stat = _clo(j.AssignStat(left, e), node)
                result.append(stat)

                result.extend(self.__gen_import_stat(modules, node))
        return result

    def __iter_aliases(self, names):
        for name in names:
            name, asname = name.name, name.asname
            yield name, asname or name.partition('.')[0]

    def visit_ImportFrom(self, node):
        def gen_import_from_expr(module_expr, name, asname):
            if name == '*':
                result = j.Call(SF_ATTR('_import_all_from_module'),[
                        MODULE_VAR_id,
                        module_expr
                    ])
            else:
                left = self.scope.resolve(asname or name, None)
                if self.debug:
                    right = j.Call(SF_ATTR('_valid_symbol'), [
                            j.Str(module), j.Str(name),
                            ATTR(module_expr, name)
                        ])
                else:
                    right = ATTR(module_expr, name)
                result = j.Assign(left, right)
            result = j.Expr_stat(result)
            _clo(result, node)
            return result

        level, module, names = node.level, node.module, node.names
        if module == '__future__':
            raise NotImplementedError(
                _('__future__ import is not implemented.'))
        if level & 0x01:
            raise NotImplementedError(
                _('relative import is not implemented.'))

        if module == '__spork__':
            for name, asname in self.__iter_aliases(names):
                try:
                    self.__imported_spork_funcs[asname] = self._spork_funcs[name]
                except KeyError:
                    raise ImportError('can not import name ' + name)
            return

        name_seq = list(self.__get_import_seq(module))
        result = self.__gen_import_stat(name_seq[:-1], node)
        e = self.__gen_import_expr(name_seq[-1])
        pairs = list(self.__iter_aliases(names))
        if len(pairs) != 1:
            result.append(j.AssignStat(IMPORT_TMP_VAR_id, e))
            e = IMPORT_TMP_VAR_id

        result.extend(gen_import_from_expr(e, *x) for x in pairs)
        return result

    def visit_Yield(self, node):
        raise NotImplementedError(_('Do not support yield statement.'))

    @_cplo
    def visit_ListComp(self, node):
        def For(target, iter, body):
            r = ast.For()
            r.target, r.iter, r.body = target, iter, body
            r.orelse = None
            return copy_location(r, node)

        def Call(func, args):
            r = ast.Call()
            r.func, r.args = func, args
            r.keywords = r.starargs = r.kwargs = None
            r = ast.Expr(r)
            return copy_location(r, node)

        def Attribute(value, attr):
            r = ast.Attribute()
            r.value, r.attr = value, attr
            return copy_location(r, node)

        def Name(id):
            r = ast.Name()
            r.id = id
            return r

        def If(test, body, orelse):
            r = ast.If()
            r.test, r.body, r.orelse = test, body, orelse
            return copy_location(r, node)

        with self._push_scope(ListCompScope(self.scope)):
            elt, generators = node.elt, node.generators

            def check_one_target_var(generator):
                target = generator.target
                try:
                    return target.id
                except AttributeError:
                    raise NotImplementedError(
                        'List competency with more than 1 vars is not supported.')

            resultvar = self._unique_var()
            stats = []
            stats.append(j.AssignStat(id(resultvar.id), 
                j.Call(SF_ATTR('list'), ())))
            body = Call(Attribute(Name(resultvar.id), 'append'), (elt,))
            for generator in reversed(generators):
                check_one_target_var(generator)
                ifs, iter, target = generator.ifs, generator.iter, generator.target
                assert len(ifs) <= 1

                if ifs:
                    body = If(ifs[0], (body,), None)
                body = For(target, iter, (body,))
            stats.extend(self.visit(body))
            stats.append(j.Return(resultvar))
            if self.scope.locals:
                stats.insert(0, j.DeclareMultiVar(self.scope.locals))
            func = j.ParenthesisOp(j.FunctionDef((), stats))
            return j.Call(func, ())

    def visit_GeneratorExp(self, node):
        def create_args(args):
            return ast.arguments(args = args, vararg=None, kwarg=None,
                    defaults=())

        def select_func(elt, expr):
            result = ast.Lambda()
            result.args = create_args((elt,))
            result.body = expr
            return result

        def if_func(elt, if_expr):
            result = ast.Lambda()
            result.args = create_args((elt,))
            result.body = if_expr
            return result

        with self._push_scope(ListCompScope(self.scope)):
            elt, generators = node.elt, node.generators
            if len(generators) != 1:
                msg = 'comprehension with more than 1 iter source is not supported'
                raise NotImplementedError(msg)

            generator = generators[0]
            ifs, iter, target = generator.ifs, generator.iter, generator.target
            assert len(ifs) <= 1

            if isinstance(target, ast.Tuple):
                msg = 'comprehension with more than 1 vars is not supported'
                raise NotImplementedError(msg)
            comp_expr = SF_ATTR('_comp_expr')
            iter_js = self.visit(iter)
            select_js = self.visit(select_func(target, elt))
            if_js = self.visit(if_func(target, ifs[0])) if ifs else j.Null()
            return j.Call(comp_expr, (iter_js,select_js, if_js))

    @contextmanager
    def _push_scope(self, scope):
        old_scope = self.scope
        self.scope = scope
        yield
        self.scope = old_scope

class LocalVarScaner(NodeVisitor):
    def __init__(self):
        super(LocalVarScaner, self).__init__()
        self.local_vars = set()
        self.globals = set()
        self.args = set()
        self.expected_globals = set()

    def _add_var(self, var):
        self.local_vars.add(var)

    def visit_arguments(self, node):
        eat(self.args.add(n.id) for n in node.args)
        if node.vararg:
            self.args.add(node.vararg)
        if node.kwarg:
            self.args.add(node.kwarg)

    def visit_ListComp(self, node):
        pass

    def visit_Name(self, node):
        name = node.id
        if name not in self.local_vars and \
                name not in self.globals and \
                name not in self.args:
            self.expected_globals.add(name)

    def visit_Assign(self, node):
        def do_name(node):
            if isinstance(node, ast.Name):
                if node.id in self.expected_globals:
                    raise SyntaxError(
                        "local variable '%s' referenced before assign. line: %s" %
                        (node.id, node.lineno))
                self._add_var(node.id)
                return True
            return False

        for t in node.targets:
            if not do_name(t) and isinstance(t, ast.Tuple):
                eat(do_name(item) for item in t.elts)
        super(LocalVarScaner, self).generic_visit(node)

    def visit_ClassDef(self, node):
        self._add_var(node.name)

    def visit_For(self, node):
        target, iter, orelse, body = node.target, node.iter, node.orelse, \
            node.body
        if isinstance(target, ast.Name):
            self._add_var(target.id)
        elif isinstance(target, ast.Tuple):
            eat(self._add_var(n.id) for n in target.elts)
        else:
            assert False, 'can not handle ' + str(target)
        super(LocalVarScaner, self).generic_visit(iter)
        eat(super(LocalVarScaner, self).visit(s) for s in body)
        eat(super(LocalVarScaner, self).visit(s) for s in orelse)

    def visit_Global(self, node):
        eat(self.globals.add(n) for n in node.names)

    hit = False

    def visit_FunctionDef(self, node):
        if self.hit:
            self._add_var(node.name)
        else:
            self.hit = True
            return super(LocalVarScaner, self).generic_visit(node)

    def visit_Import(self, node):
        for n in node.names:
            name = n.asname or n.name.partition('.')[0]
            self._add_var(name)
        return super(LocalVarScaner, self).generic_visit(node)

    def visit_ExceptHandler(self, node):
        if node.name:
            self._add_var(node.name.id)
        return super(LocalVarScaner, self).generic_visit(node)

    visit_ImportFrom = visit_Import

    def scan(self, node):
        self.visit(node)
        result = self.local_vars
        result -= self.globals
        result -= self.args
        return result

from os.path import expanduser

HTML_TEMPLATE_DEBUG = '''<!DOCTYPE html>
<html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
        <meta charset="utf-8">
        <![if gte IE 8]>
        <script type='text/javascript'>
            sflib = '%(sflib)s';
        </script>
%(preload)s
        <![endif]>
    </head>
	<body>
        <!--[if lt IE 8]>
        <h1>Sorry, Internet Explorer 7 and below, can not use this web
        application. Please use Internet Explorer 8 and up, or Google Chrome,
        Safari, firefox.
        <![endif]-->
        <pre id='__console__' style='word-wrap:break-word'></pre>
	</body>
</html>
'''

HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
        <meta charset='utf-8'>
        <![if gte IE 9]>
        <script type='text/javascript'>
            sflib = '%(sflib)s';
        </script>
%(preload)s
        <![endif]>
    </head>
	<body>
        <!--[if lt IE 8]>
        <h1>Sorry, Internet Explorer 7 and below, can not use this web
        application. Please use Internet Explorer 8 and up, or Google Chrome,
        Safari, firefox.
        <![endif]-->
	</body>
</html>
'''

import os
from os.path import dirname
from distutils.core import setup
from distutils.command.build_py import build_py as _build_py
from distutils.dep_util import newer
from .io import change_ext

class _my_build_py_base(_build_py):
    def get_targetfile(self, package, module):
        package_list = package.split('.')
        return self.get_module_outfile(self.build_lib, package_list, module)

    def get_module_outfile(self, build_dir, package, module):
        result = _build_py\
                .get_module_outfile(self, build_dir, package, module)
        if result.endswith('__init__.py'):
            result = dirname(result) + self._target_ext
        else:
            result = change_ext(result, self._target_ext)
        return result

    def build_module(self, module, module_file, package):
        targetfile = self.get_targetfile(package, module)
        if newer(module_file, targetfile):
            self.build_file(package, module, module_file)

    def build_file(self, package, module, module_file):
        if package:
            module = package + '.' + module
        try:
            self.do_build_module(module, module_file)
        except Exception as e:
            target_file = self.get_targetfile(package, module)
            print `e`
            print 'build failed, remove target file', target_file
            try:
                os.remove(target_file)
            except:
                pass
            raise

def _get_real_module_name(module_name):
    init_module = '.__init__'
    if module_name.endswith(init_module):
        result = module_name[:-len(init_module)]
    else:
        result = module_name
    return result

class build_py(_my_build_py_base):
    _target_ext = '.js'

    def do_build_module(self, module, module_file):
        py_code = read_file(module_file)
        ioutil = IOUtil(self.build_lib)
        module = _get_real_module_name(module)
        debug = not self.optimize
        compile(module, py_code, ioutil, debug=debug)

    def run(self):
        _build_py.run(self)
        self.run_command('gen_home_pages')

class _gen_home_pages_cmd(_my_build_py_base):
    _target_ext = '.html'
    user_options = _my_build_py_base.user_options + [
        ('lib-dir=', 'd', 'directory to "spork lib path"')
    ]

    def initialize_options (self):
        _my_build_py_base.initialize_options(self)
        self.lib_dir = None

    def do_build_module(self, module, module_file):
        ioutil = IOUtil(self.build_lib)
        if self.lib_dir:
            libdir = expanduser(self.lib_dir)
            libdir = IOUtil(libdir)
        else:
            libdir = ioutil
        module = _get_real_module_name(module)
        gen_home_page(libdir, ioutil, module)

setup = partial(setup, cmdclass={
    'build_py': build_py,
    'gen_home_pages': _gen_home_pages_cmd,
})

import sys
sys.dont_write_bytecode = True
del sys
