# -*- coding: utf-8 -*-
from __spork__ import JS, import_js, import_css, no_arg_check

if __debug__:
    import_js('jquery-1.7.1.js')
    import_js('core.js')
else:
    import_js('jquery-1.7.1.min.js')
    import_js('core.min.js')

JS('$b=$m;\n')

@no_arg_check
def _get_global_var(module, name):
    result = JS('module[$name$]')
    if result is NotImplemented:
        raise NameError("name '%s' is not defined." % name)
    return result

def __func_not_implemented(funcname):
    raise NotImplementedError(funcname + '() is not implemented.')

def callable(o):
    __func_not_implemented('callable')

def chr(o):
    return JS('String.fromCharCode(o)')

def ord(o):
    if not isString(o):
        raise TypeError('ord() expected string')
    if len(o) != 1:
        raise TypeError(
        'ord() expected a character, but string of length %s found' % len(o))
    return JS('o.charCodeAt(0)')

def compile(source, filename, mode):
    __func_not_implemented('compile')

def complex(real, imag):
    __func_not_implemented('complex')

def eval(code):
    __func_not_implemented('eval')

def file(filename, mode=None, bufsize=None):
    __func_not_implemented('file')

def open(filename, mode=None, bufsize=None):
    __func_not_implemented('open')

def execfile(filename):
    __func_not_implemented('execfile')

def filter(func, iterable):
    JS('''
    if (iterable.l === undefined) {
        var r = iterable.l.filter(function(x, i, arr) {
            return func(x);
        });
        return $m.list(r);
    }
    ''')
    result = []
    for item in iterable:
        if func(item):
            result.append(item)
    return result

def frozenset(iterable):
    __func_not_implemented('frozenset')

def globals():
    __func_not_implemented('globals')

def hex(x):
    if JS("(typeof x !== 'number')"):
        raise TypeError("hex() argument can't be converted to hex")
    if x < 0:
        return '-0x' + abs(x).toString(16)
    else:
        return '0x' + x.toString(16)

def oct(x):
    if JS("(typeof x !== 'number')"):
        raise TypeError("oct() argument can't be converted to hex")
    if x < 0:
        return '-0' + abs(x).toString(8)
    else:
        return '0' + x.toString(8)

def id(x):
    __func_not_implemented('id')

def input(x):
    __func_not_implemented('input')

def raw_input(prompt=''):
    return JS('window.prompt(prompt)')

def iter(x):
    if not isIteratable(x):
        raise TypeError("object is not iterable")
    return x.__iter__()

def locals():
    __func_not_implemented('locals')

def map(func, iterable):
    JS('''
    if (iterable.l) {
        var l = iterable.l.map(function(x, i, arr) {return func(x);});
        return $m.list(l);
    }
    ''')
    result = []
    for item in iterable:
        result.append(func(item))
    return result

def next(seq, default=NotImplemented):
    if not hasattr(seq, 'next'):
        raise TypeError('object is not an iterator')

    JS('try{')
    return seq.next()
    JS('''}catch(e){
        if (e.__name__!=='StopIteration') {
            throw e;
        }''')
    if default is not NotImplemented:
        return default
    JS('throw e;}')

def reduce(func, iterable, initializer=None):
    JS('''
    if (iterable.l !== undefined) {
        if (initializer === null) {
            return iterable.l.reduce(function(prev, cur, i, arr) {
                return func(prev, cur);
            });
        } else {
            return iterable.l.reduce(function(prev, cur, i, arr) {
                return func(prev, cur);
            }, initializer);
        }
    }
    ''')
    itera = iter(iterable)
    result = next(itera) if initializer is None else initializer
    for item in itera:
        result = func(result, item)
    return result

def reversed(seq):
    result = list(seq)
    result.reverse()
    return result

def round(x, n=0):
    result = abs(x)
    if x != 0:
        result *= JS('Math.pow(10, n)')
    result = JS('Math.round(result)')
    if x != 0:
        result /= JS('Math.pow(10, n)')
    if x < 0:
        return - result
    return result

def sorted(iterable, cmp=None, key=None, reverse=None):
    __func_not_implemented('sorted')

def sum(iterable, start=0):
    result = start
    for i in iterable:
        result += i
    return result

def unichr(i):
    __func_not_implemented('unichr')

def unicode(object, encoding=None, errors=None):
    __func_not_implemented('unicode')

def vars(obj = NotImplemented):
    if obj is NotImplemented:
        __func_not_implemented('vars')

    if obj is None:
        raise TypeError, 'vars() argument must have __dict__ attribute'
    r = {}
    for k in dir(obj):
        if not (k.startswith('__') and k.endswith('__') or k == '$H'):
            if len(k) > 2 and k[0] == '$' and k[-1] == '$':
                k = k[1:-1]
            r[k] = getattr(obj, k)
    return r

def zip(*args):
    result = []
    if len(args) == 0:
        return result

    iters = [iter(item) for item in args]
    while True:
        item = []
        for it in iters:
            JS('try {')
            item.append(it.next())
            JS('''} catch(e) {
                if (e.__name__ !== 'StopIteration') {
                    throw e;
                }
                return result;
            }
            ''')
        result.append(tuple(item))
    return result

@no_arg_check
def _add_loaded_module(module_name, module_obj):
    assert module_name not in _loaded_modules,\
            'module ' + module_name + ' is already loaded' 
    _loaded_modules[module_name] = module_obj

def _module_loaded(module_name):
    return module_name in _loaded_modules

def import_(module_name):
    if _module_loaded(module_name):
        return _loaded_modules[module_name]

    f = module_name.py_replace('.', '/') + '.js'
    if JS('_sf_import(f)'):
        return _loaded_modules[module_name]
    else:
        raise ImportError('No module named ' + module_name)

@no_arg_check
def _import_all_from_module(m, from_module):
    all = getattr(from_module, '__all__', None)
    if all is None:
        all = dir(from_module)

    for name in all:
        if not name.startswith('_'):
            setattr(m, name, getattr(from_module, name))

if __debug__:
    @no_arg_check
    def _valid_symbol(module_name, symbol_name, symbol):
        if symbol is NotImplemented:
            raise ImportError('cannot import name ' + symbol_name + ' from module ' +
                    module_name)
        return symbol

@no_arg_check
def _assert(test, msg):
    if __debug__:
        if not test:
            try:
                from logging import debug
                debug('*Assetion* ' + msg)
            except:
                pass
            raise AssertionError(msg or '')

def print_(objs, newline):
    from hal import do_print
    s = ''
    JS(r'''
    for(var i=0; i < objs.length; i++) {
        if(s !== "") {
            s += " ";
        }
        s += $m.str(objs[i]);
    }
    if (newline) {
        s+='\n';
    }
    ''')
    do_print(s)

def sprintf(strng, args):
    # See http://docs.python.org/library/stdtypes.html
    constructor = JS('get_pyjs_type_name(args)')
    JS(r"""
    var re_dict = 
        (/([^%]*)%[(]([^)]+)[)]([#0\x20\0x2B\-]*)(\d+)?(\.\d+)?[hlL]?(\.)((.|\\n)*)/);
    var re_list = 
        (/([^%]*)%([#0\x20\x2B\-]*)(\*|(\d+))?(\.\d+)?[hlL]?(.)((.|\\n)*)/);
    var re_exp = (/(.*)([+\-])(.*)/);
""")
    strlen = len(strng)
    argidx = 0
    nargs = 0
    result = []
    remainder = strng

    def next_arg():
        if argidx == nargs:
            raise TypeError("not enough arguments for format string")
        arg = args[argidx]
        argidx += 1
        return arg

    def formatarg(flags, minlen, precision, conversion, param):
        subst = ''
        numeric = True
        if not minlen:
            minlen=0
        else:
            minlen = int(minlen)
        if not precision:
            precision = None
        else:
            precision = int(precision)
        left_padding = 1
        if flags.find('-') >= 0:
            left_padding = 0
        if conversion == '%':
            numeric = False
            subst = '%'
        elif conversion == 'c':
            numeric = False
            subst = chr(int(param))
        elif conversion == 'd' or conversion == 'i' or conversion == 'u':
            subst = str(int(param))
        elif conversion == 'e':
            if precision is None:
                precision = 6
            JS("""
            subst = re_exp.exec(String(param.toExponential(precision)));
            if (subst[3].length === 1) {
                subst = subst[1] + subst[2] + '0' + subst[3];
            } else {
                subst = subst[1] + subst[2] + subst[3];
            }""")
        elif conversion == 'E':
            if precision is None:
                precision = 6
            JS("""
            subst = re_exp.exec(String(param.toExponential(precision)).toUpperCase());
            if (subst[3].length === 1) {
                subst = subst[1] + subst[2] + '0' + subst[3];
            } else {
                subst = subst[1] + subst[2] + subst[3];
            }""")
        elif conversion == 'f':
            if precision is None:
                precision = 6
            JS('subst = String(parseFloat(param).toFixed(precision));')
        elif conversion == 'F':
            if precision is None:
                precision = 6
            JS('subst = String(parseFloat(param).toFixed(precision)).'
                'toUpperCase();')
        elif conversion == 'g':
            if flags.find('#') >= 0:
                if precision is None:
                    precision = 6
            if param >= 1E6 or param < 1E-5:
                JS('subst = String(precision === null ? '
                    'param.toExponential() : '
                    'param.toExponential().toPrecision(precision));')
            else:
                JS('subst = String(precision === null ? '
                    'parseFloat(param) : '
                    'parseFloat(param).toPrecision(precision));')
        elif conversion == 'G':
            if flags.find('#') >= 0:
                if precision is None:
                    precision = 6
            if param >= 1E6 or param < 1E-5:
                JS('subst = String(precision === null ? '
                    'param.toExponential() : '
                    'param.toExponential().toPrecision(precision))'
                    '.toUpperCase();')
            else:
                JS('subst = String(precision === null ? '
                    'parseFloat(param) : '
                    'parseFloat(param).toPrecision(precision))'
                    '.toUpperCase().toUpperCase();')
        elif conversion == 'r':
            numeric = False
            subst = repr(param)
        elif conversion == 's':
            numeric = False
            subst = str(param)
        elif conversion == 'o':
            param = int(param)
            JS('subst = param.toString(8);')
            if flags.find('#') >= 0 and subst != '0':
                subst = '0' + subst
        elif conversion == 'x':
            param = int(param)
            JS('subst = param.toString(16);')
            if flags.find('#') >= 0:
                if left_padding:
                    subst = subst.rjust(minlen - 2, '0')
                subst = '0x' + subst
        elif conversion == 'X':
            param = int(param)
            JS('subst = param.toString(16).toUpperCase();')
            if flags.find('#') >= 0:
                if left_padding:
                    subst = subst.rjust(minlen - 2, '0')
                subst = '0X' + subst
        else:
            raise ValueError("unsupported format character '" + conversion + "' ("+hex(ord(conversion))+") at index " + (strlen - len(remainder) - 1))
        if minlen and len(subst) < minlen:
            padchar = ' '
            if numeric and left_padding and flags.find('0') >= 0:
                padchar = '0'
            if left_padding:
                subst = subst.rjust(minlen, padchar)
            else:
                subst = subst.ljust(minlen, padchar)
        return subst

    def sprintf_list(strng, args):
        while remainder:
            a = JS('re_list.exec(remainder)')
            if a is None:
                result.append(remainder)
                break
            left, flags = JS('a[1]'), JS('a[2]')
            minlen, precision, conversion = JS('a[3]'), JS('a[5]'), JS('a[6]')
            JS("""
            remainder = a[7];
            if (minlen === undefined) {
                minlen = null;
            }
            if (precision === undefined) {
                precision = null;
            }
            if (conversion === undefined) {
                conversion = null;
            }
""")
            result.append(left)
            if minlen == '*':
                minlen = next_arg()
                minlen_type = JS("typeof(minlen)")
                if minlen_type != 'number' or int(minlen) != minlen:
                    raise TypeError('* wants int')
            if conversion != '%':
                param = next_arg()
            result.append(formatarg(flags, minlen, precision, conversion, param))

    def sprintf_dict(strng, args):
        arg = args
        argidx += 1
        while remainder:
            a = JS('re_dict.exec(remainder)')
            if a is None:
                result.append(remainder)
                break;
            left, key, flags = JS('a[1]'), JS('a[2]'), JS('a[3]')
            minlen, precision, conversion = JS('a[4]'), JS('a[5]'), JS('a[6]')
            JS("""
            remainder = a[7];
            if (minlen === undefined) {
                minlen = null;
            }
            if (precision === undefined) {
                precision = null;
            }
            if (conversion === undefined) {
                conversion = null;
            }
""")
            result.append(left)
            if not arg.has_key(key):
                raise KeyError(key)
            else:
                param = arg[key]
            result.append(formatarg(flags, minlen, precision, conversion, param))

    a = JS('re_dict.exec(strng)')
    if a is None:
        if constructor != "tuple":
            args = (args,)
        nargs = len(args)
        sprintf_list(strng, args)
        if argidx != nargs:
            raise TypeError('not all arguments converted during string formatting')
    else:
        if constructor != "dict":
            raise TypeError("format requires a mapping")
        sprintf_dict(strng, args)
    return ''.join(result)

class object():
    def __init__(self):
        pass

    def __delattr__(self, attrname):
        if JS("self.hasOwnProperty(attrname)"):
            JS('delete self[attrname];')
        else:
            raise AttributeError(attrname)

    def __setattr__(self, name, value):
        JS(r'''
        if (self.hasOwnProperty($name$)) {
            self[$name$] = value;
        }

        var p = self[$name$];
        if (p && p.__set__) {
            p.__set__(self, value);
        } else {
            if (value && !value.__is_method__ && !self.__is_instance__ && $.isFunction(value)) {
                value = value.bind(null, this);
                self[$name$] = pyjs__bind_method($name$, value, value.__bind_type__, value.__args__);
            } else {
                self[$name$] = value;
            }
        }
    ''')

    def __str__(self):
        return JS('(this.__is_instance__ ? "instance of " : "class ") + \
               this.__module__ + "." + this.__name__')

    def toString(self):
        return self.__str__()

class _comp_expr(object):
    def __init__(self, items, select_func, filter=None):
        self._iter = iter(items)
        self.select_func = select_func
        self.filter = filter

    def __iter__(self):
        return self

    def next(self):
        while True:
            item = self._iter.next()
            if self.filter is None or self.filter(item):
                break
        return self.select_func(item)

class BaseException(object):
    def __init__(self, msg=''):
        self.message = msg
        self._stacktrace = _extract_stack()[:-2]

    def __str__(self):
        from traceback import format_list
        return type(self).__name__ + ': ' + self.message + '\n' +\
                '\n'.join(format_list(self._stacktrace))

    __repr__ = __str__

class Exception(BaseException): pass
class StopIteration(Exception): pass
class AssertionError(Exception): pass
class StandardError(Exception): pass
class TypeError(StandardError): pass
class AttributeError(StandardError): pass
class ValueError(StandardError): pass
class NameError(StandardError): pass
class UnboundLocalError(NameError): pass
class ImportError(StandardError): pass
class LookupError(StandardError): pass
class KeyError(LookupError): pass
class IndexError(LookupError): pass
class RuntimeError(StandardError): pass
class NotImplementedError(RuntimeError): pass
class SyntaxError(StandardError): pass
class IndentationError(SyntaxError): pass

@no_arg_check
def _bool(v):
    JS("""
    if (!v) {
        return false;
    }
    switch(typeof v){
    case 'boolean':
        return v;
    case 'object':
        if (v.__nonzero__) {
            return v.__nonzero__();
        } else if (v.__len__) {
            return v.__len__() !== 0;
        }
    }
""")
    return True

def bool(v):
    return _bool(v)

def int(text, radix=10):
    JS("""
    if (typeof text === 'number' && text >= 0) {
        return Math.floor(text);
    }
    var i = parseInt(text, radix);
    if (!isNaN(i)) {
        return i;
    }
    """)
    raise ValueError("invalid literal for int() with base %d: '%s'" % (radix, text))
long = int

def float(text):
    if not JS('(/^[+\-]?[0-9.]+$/).test(text)'):
        raise ValueError('invalid literal for float(): ' + text)
    return JS('parseFloat(text)')

def cmp(a,b):
    if a is b:
        return 0
    if a is None:
        return 0 if b is None else -1
    if b is None:
        return 1
    JS(r"""
    if (a.__cmp__) {
        return a.__cmp__(b);
    }
    if (a > b) {
        return 1;
    }
    """)
    return -1

__cmp = cmp

@no_arg_check
def eq(a, b):
    if a is b:
        return True
    if a is None:
        return False
    if b is None:
        return False
    JS('''
    if (a.__eq__) {
        return a.__eq__(b);
    }
    if (a.__cmp__) {
        return a.__cmp__(b) === 0;
    }
    ''')
    return False

@no_arg_check
def __lt(a, b):
    if a is None:
        return True

    JS('''
    if (a.__lt__) {
        return a.__lt__(b);
    }
    ''')
    return JS('$m.cmp(a, b) < 0')

@no_arg_check
def __le(a, b):
    if a is None:
        return True

    JS('''
    if (a.__le__) {
        return a.__le__(b);
    }
    ''')
    return JS('$m.cmp(a, b) <= 0')

@no_arg_check
def __gt(a, b):
    if a is None:
        return False

    JS('''
    if (a.__gt__) {
        return a.__gt__(b);
    }
    ''')
    return JS('$m.cmp(a, b) > 0')

@no_arg_check
def __ge(a, b):
    if a is None:
        return False

    JS('''
    if (a.__ge__) {
        return a.__ge__(b);
    }
    ''')
    return JS('$m.cmp(a, b) >= 0')

def isObject(a):
    t = JS('typeof a')
    if t is 'object':
        return a is not None
    return t is not 'function'

def isNumber(a):
    #return JS('a === +a') faster, but can not pass unittests,
    #maybe my wield class structure.
    # isNumber(list), raise a javascript error:
    #  TypeError: Cannot read property 'length' of undefined
    return JS('typeof a === "number"')

def isIteratable(a):
    return JS("$m.isString(a) || ($m.isObject(a) && a.__iter__)")

def isString(a):
    return JS("typeof a === 'string'")

def isBool(a):
    return a is True or a is False

def isUndefined(a):
    return JS("a === undefined")

def hasattr(obj, name):
    JS('''
    if ((obj === null) || (obj === undefined)) {
        return false;
    }
    $name$ = $m._safe_id($name$);
    if (obj[$name$] !== undefined) {
        return true;
    }
    if (obj.__getattr__ !== undefined) {
        try {
            obj.__getattr__($name$);
            return true;
        } catch(e) {
            e = $m._errorMapping(e);
            if ($m.isinstance(e, $m.AttributeError)) {
                return false;
            } else {
                throw e;
            }
        }
    }
    ''')
    return False

_js_keywords= JS('''{
    'const' : 1,
    'delete' : 1, 
    'do' : 1, 
    'export' : 1, 
    'function' : 1, 
    'instanceOf' : 1,
    'label' : 1, 
    'let' : 1, 
    'new' : 1, 
    'switch' : 1, 
    'this' : 1, 
    'throw' : 1, 
    'catch' : 1,
    'typeof' : 1, 
    'var' : 1, 
    'void' : 1, 
    'default' : 1, 
    'super' : 1,
    'name' : 1
}''')

def _safe_id(id):
    JS('''
    if ($m._js_keywords.hasOwnProperty(id)) {
        return '$' + id + '$';
    }
    return id;
''')

@no_arg_check
def _getattr(obj, name, default_value):
    if (JS('!obj')):
        raise AttributeError("'NoneType' object has no attribute '%s'" % name)
    name = _safe_id(name)
    result = JS('obj[$name$]')
    if (JS('obj.hasOwnProperty($name$)')):
        if __debug__:
            JS('''
            if (result && result.__bind_type__ === 1 && obj.__is_instance__ === false) {
                throw $m.NotImplementedError(
                    'Not support get unbound function from class');
            }
            ''')
        return result

    JS("""
    if (result === undefined) {
        if (obj.__getattr__ !== undefined) {
            if (default_value == undefined) {
                return obj.__getattr__($name$);
            } else {
                try {
                    return obj.__getattr__($name$);
                } catch (e) {
                    if ($m.isinstance(e, $m.AttributeError)) {
                        return default_value;
                    }
                    throw e;
                }
            }
        }
        if (default_value === undefined) {
            throw $m.AttributeError('can not found attr ' + $name$ +
                ' on ' + $m.repr(obj));
        } else {
            return default_value;
        }
    }

    if (result && result.__get__) {
        return result.__get__(obj);
    }
    if (!$.isFunction(result)) {
        return result;
    }
    if (obj.__is_instance__ === false) {
        throw $m.NotImplementedError(
            'Not support get unbound function from class')
    }
    """)
    fnwrap = JS('result.bind(obj)')
    fnwrap.__name__ = name
    fnwrap.__args__ = result.__args__
    fnwrap.__bind_type__ = result.__bind_type__
    return fnwrap

def getattr(obj, name, default_value=NotImplemented):
    return _getattr(obj, name, default_value)

@no_arg_check
def _setattr(obj, name, value):
    JS('''
    $name$ = $m._safe_id($name$);
    if (!obj) {
        throw $m.AttributeError("'NoneType' object has no attribute '" + $name$ + "'");
    }

    if (obj.__is_instance__ && obj.__setattr__) {
        obj.__setattr__($name$, value);
    } else {
        obj[$name$] = value;
    }
    ''')

def setattr(obj, name, value):
    return _setattr(obj, name, value)

def delattr(obj, name):
    JS('''
    $name$ = $m._safe_id($name$);
    if (!obj) {
        throw $m.AttributeError("'NoneType' object has no attribute '" + $name$ + "'");
    }
    if (obj.__delattr__) {
        obj.__delattr__($name$);
    } else {
        var result = obj[$name$];
        if (!result || typeof(result) === "function") {
            throw $m.AttributeError($name$);
        }

        delete obj[$name$];
    }
    ''')

def dir(obj):
    JS("""
    return $m.list(Object.keys(obj).filter(function(val, idx, arr) {
        return obj.hasOwnProperty(val);
    }));
    """)

class NoneType(object): pass
class NotImplementedType(object): pass
class TypeType(object): pass

def type(o):
    if o is None:
        return NoneType
    if o is NotImplemented:
        return NotImplementedType

    if isNumber(o):
        return int if int(o) == o else float
    if isBool(o):
        return bool
    if isString(o):
        return str

    if hasattr(o, '__is_instance__'):
        if getattr(o, '__is_instance__'):
            cls = getattr(o, '__class__', None)
            if cls is not None:
                return cls
        else:
            return TypeType

    if o in (int, str, bool, float):
        return TypeType
    __func_not_implemented('type')

def len(obj):
    try:
        return obj.__len__()
    except AttributeError:
        raise TypeError('object %r has no len()' % obj)
    
def all(iterable):
    JS('''
    if (iterable.l !== undefined) {
        for (var i=0, l=iterable.l, len=l.length; i < len; i++) {
            if (!$m._bool(l[i])) {
                return false;
            }
        }
        return true;
    }
    ''')
    for element in iterable:
        if not element:
            return False
    return True

def any(iterable):
    JS('''
    if (iterable.l !== undefined) {
        for (var i=0, l=iterable.l, len=l.length; i < len; i++) {
            if ($m._bool(l[i])) {
                return true;
            }
        }
        return false;
    }
    ''')
    for element in iterable:
        if element:
            return True
    return False

def __max_min(cmp_val, func_name):
    def func(*sequence, **kwarg):
        key = kwarg.get('key', lambda x: x)
        if len(sequence) == 1:
            sequence = sequence[0]
        result = None
        hit = False
        for item in iter(sequence):
            hit = True
            if result is None:
                result = item
            elif cmp(key(item), key(result)) == cmp_val:
                result = item
        if not hit:
            raise ValueError(func_name + '() arg is an empty sequence.')
        return result
    return func

min = __max_min(-1, 'min')
max = __max_min(1, 'max')

next_hash_id = 0
def hash(obj):
    JS("""
    if (obj === null) {
        return 0;
    }
    if (obj.$H) { 
        return obj.$H;
    }
    if (obj.__hash__) {
        return obj.__hash__();
    }
    if (obj.constructor === String || obj.constructor === Number ||
        obj.constructor === Date) {
        return obj;
    }
    obj.$H = ++$m.next_hash_id;
    """)
    return JS('obj.$H')

def isinstance(object_, classinfo):
    if object_ is None:
        return False
    if isUndefined(object_):
        return False
    if classinfo.__name__ == 'int':
        return isNumber(object_)
    if classinfo.__name__ == 'str':
        return isString(object_)
    if classinfo.__name__ == 'bool':
        return isBool(object_)
    if _isinstance(classinfo, tuple):
        for ci in classinfo:
            if isinstance(object_, ci):
                return True
        return False
    else:
        return _isinstance(object_, classinfo)
    if not isObject(object_):
        return False

def _isinstance(object_, classinfo):
    JS("""
    if (object_.__is_instance__ !== true) {
        return false;
    }
    var mro = object_.__mro__;
    for (var i=0,len=mro.length; i<len; i++) {
        if (mro[i] === classinfo) {
            return true;
        }
    }
    """)
    return False

class property(object):
    # From: http://users.rcn.com/python/download/Descriptor.htm
    # Extended with setter(), deleter() and fget.__doc_ copy
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if not doc is None or not hasattr(fget, '__doc__') :
            self.__doc__ = doc
        else:
            self.__doc__ = fget.__doc__

    def __get__(self, obj, objtype=None):
        if self.fget is None:
            raise AttributeError, "unreadable attribute"
        return JS('self.fget.apply(obj)')

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError, "can't set attribute"
        return JS('self.fset.apply(obj, [value])')

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError, "can't delete attribute"
        self.fdel(obj)

    def setter(self, fset):
        self.fset = fset
        return self

    def deleter(self, fdel):
        self.fdel = fdel
        return self

def staticmethod(func):
    func.__bind_type__ = 0
    return func

def issubclass(class_, classinfo):
    __func_not_implemented('issubclass')

def enumerate(sequence):
    JS('''
    if (sequence.l) {
        var tuple = $m.tuple, arr = sequence.l, length = arr.length;
        result = Array(length);
        for (var i=0; i<length; i ++) {
            result[i] = tuple([i, arr[i]]);
        }
        return $m.list(result);
    }
    ''')
    result = []
    nextIndex = 0
    for item in sequence:
        result.append((nextIndex, item))
        nextIndex += 1
    return result

def str(text):
    if text is None:
        return 'None'
    if text is NotImplemented:
        return 'NotImplemented'
    JS('''
    if (text.__str__) {
        return text.__str__();
    }
    ''')
    return JS('String(text)')

class list(object):
    def __init__(self, data=None):
        JS("""
        if (data === null) {
            this.l = [];
        } else if (Array.isArray(data)) {
            this.l = data.slice(0);
        } else if (data.l) {
            this.l = data.l.slice(0);
        } else {
            this.l = [];
            this.extend(data);
        }
        """)

    def append(self, item):
        JS('this.l[this.l.length] = item;')

    def extend(self, data):
        JS("""
        if (Array.isArray(data)) {
            Array.prototype.push.apply(this.l, data);
        } else if (data.l) {
            Array.prototype.push.apply(this.l, data.l);
        } else if ($m.isIteratable(data)) {
            var iter=data.__iter__();
            var i=this.l.length;
            try {
                while (true) {
                    this.l[i++]=iter.next();
                }
            }
            catch (e) {
                if (e.__name__ !== 'StopIteration') {
                    throw e;
                }
            }
        }
        """)

    def remove(self, value):
        JS("""
        var index=this.index(value);
        if (index<0) {
            return false;
        }
        this.l.splice(index, 1);
        """)
        return True

    def __find(self, value, start=0):
        for idx,item in enumerate(self):
            if item == value:
                return idx
        return -1

    def index(self, value, start=0):
        result = self.__find(value, start)
        if result == -1:
            raise ValueError('list.index(x): x not in list')
        return result

    def count(self, value):
        result = 0
        for item in self:
            if item == value:
                result += 1
        return result

    def insert(self, index, value):
        JS('''
            if (index === 0) {
                this.l.unshift(value);
            } else {
                var a = this.l;
                this.l.splice(index, 0, value);
            }
            ''')

    def pop(self, index = -1):
        result = self[index]
        del self[index]
        return result

    def __cmp__(self, l):
        if not isinstance(l, list):
            return -1
        ll = len(self) - len(l)
        if ll != 0:
            return ll
        for x in range(len(self)):
            ll = cmp(self[x], l[x])
            if ll != 0:
                return ll
        return 0

    def __eq__(self, other):
        if self is other:
            return True

        if not isinstance(other, list):
            return False

        if len(self) != len(other):
            return False

        for x, y in zip(self, other):
            if x != y:
                return False
        return True

    def _to_real_idx(self, index):
        if index < 0:
            index += len(self)
        if index >= len(self) or index < 0:
            raise IndexError('list index out of range')
        return index

    def __getitem__(self, index):
        if isNumber(index):
            index = self._to_real_idx(index)
            return JS('this.l[index]')
        elif isinstance(index, slice):
            lower, upper, step = index.indices(len(self))
            if step == 1:
                r = JS('this.l.slice(lower, upper)')
            else:
                @no_arg_check
                def filter(ele, idx, arr):
                    offset = idx - lower
                    return offset >= 0 and idx < upper and (offset % step) == 0
                r = JS('this.l.filter(filter)')
            return list(r)
        else:
            raise TypeError('list indices must be integers')

    def __fastgetitem__(self, index):
        ''' `index' always be positive int, used by jscompiler only '''
        result = JS('this.l[index]')
        if result is NotImplemented:
            if JS('index >= this.l.length'):
                raise IndexError('list index out of range')
        return result

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            lower, upper, step = index.indices(len(self))
            if step == 1:
                JS('''
                if (value.l) {
                    var args = [lower, upper - lower];
                    Array.prototype.push.apply(args, value.l);
                    Array.prototype.splice.apply(this.l, args);
                } else {
                ''')
                self.__delitem__(index)
                for v in value:
                    self.insert(lower, v)
                    lower += 1
                JS('}')
            else:
                r = _check_slice_match(value, lower, upper, step)
                for i, item in zip(r, value):
                    self[i] = item
        else:
            index = self._to_real_idx(index)
            JS('this.l[index]=value;')

    def __delitem__(self, index):
        if isinstance(index, slice):
            lower, upper, step = index.indices(len(self))
            if step == 1:
                JS('this.l.splice(lower, upper - lower);')
            else:
                for i in _rev_range(lower, upper, step):
                    del self[i]
        else:
            index = self._to_real_idx(index)
            JS('this.l.splice(index, 1);')

    def __len__(self):
        return JS('this.l.length')

    def __contains__(self, value):
        return self.__find(value) >= 0

    def __iter__(self):
        JS("""
        var i = 0;
        var l = this.l;
        """)
        return JS("""{
            'next': function() {
                if (i >= l.length) {
                    throw $m.StopIteration;
                }
                return l[i++];
            },
            '__iter__': function() {
                return this;
            }
        }
        """)

    def reverse(self):
        JS("""this.l.reverse();""")

    def sort(self, cmp=None, key=None, reverse=False):
        if not cmp:
            cmp = __cmp
        if key and reverse:
            def thisSort1(a,b):
                return -cmp(key(a), key(b))
            self.l.sort(thisSort1)
        elif key:
            def thisSort2(a,b):
                return cmp(key(a), key(b))
            self.l.sort(thisSort2)
        elif reverse:
            def thisSort3(a,b):
                return -cmp(a, b)
            self.l.sort(thisSort3)
        else:
            self.l.sort(cmp)

    def getArray(self):
        """
        Access the javascript Array that is used internally by this list
        """
        return self.l

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = '['
        JS("""
        for (var i=0; i < self.l.length; i++) {
            s += $m.repr(self.l[i]);
            if (i < self.l.length - 1) {
                s += ", ";
            }
        }
        s += "]";
        """)
        return s

    def __add__(self, other):
        result = list(self)
        result.extend(other)
        return result

    def __mul__(self, other):
        result = []
        for i in range(other):
            result.extend(self)
        return result

    def __hash__(self):
        raise TypeError, "unhashable type: 'list'"

class tuple(object):
    def __init__(self, data=None):
        JS("""
        if (data === null) {
            this.l = [];
        } else if (Array.isArray(data)) {
            this.l = data.slice(0);
        } else if (data.l) {
            this.l = data.l.slice(0);
        } else if ($m.isIteratable(data)) {
            this.l = [];
            var i = 0;
            var iter=data.__iter__();
            try {
                while (true) {
                    this.l[i++]=iter.next();
                }
            }
            catch (e) {
                if (e.__name__ !== 'StopIteration') {
                    throw e;
                }
            }
        } else {
            this.l = [];
        }
        """)

    def __find(self, value, start=0):
        for idx,item in enumerate(self):
            if item == value:
                return idx
        return -1

    def index(self, value, start=0):
        result = self.__find(value, start)
        if result == -1:
            raise ValueError('tuple.index(x): x not in list')
        return result

    def __cmp__(self, l):
        if not isinstance(l, tuple):
            return 1
        ll = len(self) - len(l)
        if ll != 0:
            return ll
        for x in range(len(self)):
            ll = cmp(self[x], l[x])
            if ll != 0:
                return ll
        return 0

    def __eq__(self, other):
        if self is other:
            return True

        if not isinstance(other, tuple):
            return False

        if len(self) != len(other):
            return False

        for x, y in zip(self, other):
            if x != y:
                return False
        return True

    def __getitem__(self, index):
        if isNumber(index):
            if index < 0:
                index += len(self)
            if index >= len(self) or index < 0:
                raise IndexError('list index out of range')
            return JS('this.l[index]')
        elif isinstance(index, slice):
            lower, upper, step = index.indices(len(self))
            if step == 1:
                r = JS('this.l.slice(lower, upper)')
            else:
                @no_arg_check
                def filter(ele, idx, arr):
                    offset = idx - lower
                    return offset >= 0 and idx < upper and (offset % step) == 0
                r = JS('this.l.filter(filter)')
            return tuple(r)
        else:
            raise TypeError('list indices must be integers')

    def __fastgetitem__(self, index):
        ''' `index' always be positive int, used by jscompiler only '''
        result = JS('this.l[index]')
        if result is NotImplemented:
            if JS('index >= this.l.length'):
                raise IndexError('list index out of range')
        return result

    def __len__(self):
        return JS('this.l.length')

    def __add__(self, other):
        arr = JS('this.l.concat(other.l)')
        return tuple(arr)

    def __mul__(self, other):
        result = []
        for i in range(other):
            result.extend(self)
        return tuple(result)

    def count(self, value):
        result = 0
        for item in self:
            if item == value:
                result += 1
        return result

    def __contains__(self, value):
        return self.__find(value) >= 0

    def __iter__(self):
        JS("""
        var i = 0;
        var l = this.l;
        """)
        return JS("""{
            'next': function() {
                if (i >= l.length) {
                    throw $m.StopIteration;
                }
                return l[i++];
            },
            '__iter__': function() {
                return this;
            }
        }
        """)

    def getArray(self):
        """
        Access the javascript Array that is used internally by this list
        """
        return self.l

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = "("
        JS("""
        for (var i=0; i < self.l.length; i++) {
            s += $m.repr(self.l[i]);
            if (i < self.l.length - 1) {
                s += ", ";
            }
        }
        if (self.l.length === 1) {
            s += ",";
        }
        s += ")";
        """)
        return s

    __hash = None
    def __hash__(self):
        def gen_hash():
            return reduce(lambda x,y: x + hash(y), self, 0)

        if self.__hash is None:
            self.__hash = gen_hash()
        return self.__hash

class dict(object):
    def __init__(self, data=None):
        JS("""
        this.d = {};
        var item;

        if (Array.isArray(data)) {
            for (var i in data) {
                if (data.hasOwnProperty(i)) {
                    item=data[i];
                    this.__setitem__(item[0], item[1]);
                }
            }
        } else if ($m.isIteratable(data)) {
            var iter=data.__iter__();
            try {
                while (true) {
                    item=iter.next();
                    this.__setitem__(item.__getitem__(0), item.__getitem__(1));
                }
            }
            catch (e) {
                if (e.__name__ !== 'StopIteration') {
                    throw e;
                }
            }
        }
        else if ($m.isObject(data)) {
            for (var key in data) {
                if (data.hasOwnProperty(key)) {
                    this.__setitem__(key, data[key]);
                }
            }
        }
        """)

    def clear(self):
        for k in self.keys():
            del self[k]

    @staticmethod
    def fromkeys(seq, value=None):
        result = {}
        for item in seq:
            result[item] = value
        return result

    def __setitem__(self, key, value):
        JS("""
        var sKey = $m.hash(key);
        this.d[sKey]=[key, value];
        """)

    def __getitem__(self, key):
        sKey = hash(key)
        value = JS('this.d[sKey]')
        if isUndefined(value):
            raise KeyError(repr(key));
        return JS('value[1]')

    def __eq__(self, other):
        if self is other:
            return True

        if type(self) != type(other):
            return False

        if len(self) != len(other):
            return False

        for k, v in self.iteritems():
            if k not in other or v != other[k]:
                return False
        return True

    def __cmp__(self, other):
        l1 = len(self)
        l2 = len(other)
        if l1 != l2:
            return l1 - l2
    
        for k in self:
            if k not in other:
                return 1
            r = cmp(self[k], other[k])
            if r != 0:
                return r
        return 0

    def __nonzero__(self):
        return len(self) != 0

    def __len__(self):
        size = 0
        JS("""
        for (var i in this.d) {
            if (this.d.hasOwnProperty(i)) {
                size++;
            }
        }
        """)
        return size

    def has_key(self, key):
        return self.__contains__(key)

    def __delitem__(self, key):
        len_before = len(self)
        JS("""
        var sKey = $m.hash(key);
        delete this.d[sKey];
        """)
        if len_before == len(self):
            raise KeyError(repr(key))

    def __contains__(self, key):
        shash = hash(key)
        return not isUndefined(JS('this.d[shash]'))

    def keys(self):
        result = []
        JS("""
        for (var key in this.d) {
            if (this.d.hasOwnProperty(key)) {
                result.append(this.d[key][0]);
            }
        }
        """)
        return result

    def values(self):
        values = []
        JS("""
        for (var key in this.d) {
            if (this.d.hasOwnProperty(key)) {
                values.append(this.d[key][1]);
            }
        }
        """)
        return values

    def items(self):
        items = []
        JS("""
        for (var key in this.d) {
            if (this.d.hasOwnProperty(key)) {
                items.append($m.tuple(this.d[key]));
            }
        }
        """)
        return items

    def pop(self, key, defval=None):
        if key in self:
            result = self[key]
            del self[key]
            return result

        if defval is not None:
            return defval
        return self[key] # just trigger KeyError

    def popitem(self):
        result = None
        for item in self.iteritems():
            result = item
            break
        if result is None:
            raise KeyError, 'popitem(): dictionary is empty'
        del self[result[0]]
        return result

    def __iter__(self):
        return self.keys().__iter__()

    def iterkeys(self):
        return self.__iter__()

    def itervalues(self):
        return self.values().__iter__();

    def iteritems(self):
        return self.items().__iter__();

    def setdefault(self, key, default_value=None):
        if not self.has_key(key):
            self[key] = default_value
        return self[key]

    def get(self, key, default_value=None):
        if not self.has_key(key):
            return default_value
        return self[key]

    def update(self, d):
        for k,v in d.iteritems():
            self[k] = v

    def getObject(self):
        """
        Return the javascript Object which this class uses to store
        dictionary keys and values
        """
        return self.d

    def copy(self):
        return dict(self.items())

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        JS("""
        var key;
        var keys = [];
        for (key in self.d) {
            if (self.d.hasOwnProperty(key)) {
                keys.push(key);
            }
        }
        """)

        s = JS('"{"')
        JS("""
        for (var i=0; i<keys.length; i++) {
            var v = self.d[keys[i]];
            s += $m.repr(v[0]) + ": " + $m.repr(v[1]);
            if (i < keys.length-1) {
                s += ", ";
            }
        }
        s += "}";
        """)
        return s

    def __hash__(self):
        raise TypeError, "unhashable type: 'dict'"

class set(object):
    def __init__(self, items=None):
        if items is not None:
            self._data = dict.fromkeys(items)
        else:
            self._data = {}

    def __len__(self):
        return len(self._data)

    def __contains__(self, item):
        return item in self._data

    def __getitem__(self, idx):
        raise TypeError, "'set' object does not support indexing"

    def __setitem__(self, idx, val):
        raise TypeError, "'set' object does not support item assignment"

    def __hash__(self):
        raise TypeError, "unhashable type: 'set'"

    def _all_exist_in(self, other):
        for i in self:
            if i not in other:
                return False
        return True

    def __le__(self, other):
        if self is other:
            return True

        self._other_should_be_set(other)

        if self._all_exist_in(other):
            return True
        return False

    def __lt__(self, other):
        if self is other:
            return False

        self._other_should_be_set(other)

        if self._all_exist_in(other) and len(self) != len(other):
            return True
        return False

    def __ge__(self, other):
        return other.__le__(self)

    def __gt__(self, other):
        return other.__lt__(self)

    issubset = __le__
    issuperset = __ge__

    def __cmp__(self, other):
        raise TypeError('cannot compare sets using cmp()')

    @staticmethod
    def _other_should_be_set(other):
        if type(other) is not set:
            raise TypeError('can only compare to a set')

    def __eq__(self, other):
        if self is other:
            return True
        self._other_should_be_set(other)
        if self._all_exist_in(other) and len(self) == len(other):
            return True

    def union(self, other):
        result = set(self)
        result.update(other)
        return result

    __or__ = union

    def intersection(self, other):
        result = self.copy()
        result.intersection_update(other)
        return result

    __and__ = intersection

    def difference(self, other):
        result = self.copy()
        result.difference_update(other)
        return result

    __sub__ = difference

    def symmetric_difference(self, other):
        result = self - other
        result.update(other - self)
        return result

    __xor__ = symmetric_difference

    def copy(self):
        return set(self)

    def update(self, other):
        for item in other:
            self.add(item)

    def intersection_update(self, other):
        for item in self:
            if item not in other:
                self.remove(item)

    def difference_update(self, other):
        for item in self:
            if item in other:
                self.remove(item)

    def symmetric_difference_update(self, other):
        s = other - self
        self.difference_update(other)
        self.update(s)

    def add(self, item):
        self._data[item] = 1

    def remove(self, item):
        del self._data[item]

    def discard(self, item):
        try:
            self.remove(item)
        except KeyError:
            pass

    def pop(self):
        return self._data.popitem()[0]

    def clear(self):
        self._data.clear()

    def __str__(self):
        return 'set(' + repr(list(self)) + ')'

    __repr__ = __str__

    def __iter__(self):
        return self._data.__iter__()

class slice(object):
    def __init__(self, start, stop, step):
        self.start = start
        self.stop = stop
        self.step = step
        if step <= 0:
            raise NotImplementedError('step <= 0 is not supported')

    def indices(self, len):
        start = min(len, self.start or 0)
        if start < 0:
            start = len + start

        if self.stop is None:
            stop = len
        else:
            stop = min(self.stop, len)
        if stop < 0:
            stop = len + stop
        return start, stop, self.step

def repr(x):
    """ Return the string representation of 'x'.
    """
    if hasattr(x, '__repr__'):
        return x.__repr__()
    JS("""
    if (x === null) {
       return "None";
    }

    if (x === undefined) {
       return "undefined";
    }

    var t = typeof(x);

    if (t === "boolean") {
       return x.toString();
    }

    if (t === "function") {
       return "<function " + x.toString() + ">";
    }

    if (t === "number") {
       return x.toString();
    }

    if (t === "string") {
       if (x.indexOf("'") === -1) {
           return "'" + x + "'";
        }
       if (x.indexOf('"') === -1) {
           return '"' + x + '"';
        }
       var s = x.replace(new RegExp('"', "g"), '\\\\"');
       return '"' + s + '"';
    }

    // If we get here, x is an object.  See if it's a Pyjamas class.

    if (!$m.hasattr(x, "__init__")) {
       return "<" + x.toString() + ">";
    }

    // Handle the common Pyjamas data types.
    """)

    constructor = JS('get_pyjs_type_name(x)')

    JS("""
    // If we get here, the class isn't one we know -> return the class name.
    // Note that we replace underscores with dots so that the name will
    // (hopefully!) look like the original Python name.

    //var s = constructor.replace(new RegExp('_', "g"), '.');
    """)
    return "<" + constructor + " object>"

def _errorMapping(err):
    if JS('err instanceof(TypeError)'):
        try:
            message = err.message
        except:
            message = ''
        return AttributeError(message)
    return err

def range(start, stop=None, step=1):
    if stop is None:
        stop = start
        start = 0

    JS('''
    var index = -1,
        length = Math.max(0, Math.ceil((stop - start) / step)),
        result = Array(length);

    while (++index < length) {
      result[index] = start;
      start += step;
    }
    return $m.list(result);
    ''')

def _rev_range(start, stop, step):
    ''' Create a reversed range

        Equivalent to reversed(range(start, stop, step)), but
        more efficient.
    '''

    return range(stop - ((stop - start - 1) % step + 1),
            start - (1 if step > 0 else -1), -step)

def _check_slice_match(val, lower, upper, step):
    r = range(lower, upper, step)
    if len(r) != len(val):
        msg = 'attempt to assign sequence of of size %s'\
            ' to extended slice of size %s'
        msg = msg % (len(val), len(r))
        raise ValueError(msg)
    return r

class xrange(object):
    def __init__(self, start, stop=None, step=1):
        if stop is None:
            stop = start
            start = 0
        self.start = start
        self.stop = stop
        self.step = step
        self.curval = start

    def __iter__(self):
        return self

    def next(self):
        result = self.curval
        self.curval += self.step
        if self.step > 0:
            if result < self.stop:
                return result
        else:
            if result > self.stop:
                return result
        raise StopIteration

def divmod(x, y):
    if int(x) == x and int(y) == y:
        return (int(x / y), int(x % y))
    f = JS("Math.floor(x / y)")
    f = float(f)
    return (f, x - f * y)

def isNull(a):
    return JS("typeof a === 'object' && !a")

def __String_count(sub):
    s = JS('this')
    result = 0
    start = 0
    while True:
        idx = s.find(sub, start)
        if idx == -1:
            return result
        result += 1
        start = idx + 1

def __String_index(sub, start=0):
    s = JS('this')
    result = s.find(sub, start)
    if result ==- 1:
        raise ValueError('substring not found')
    return result

def __String_rindex(sub):
    s = JS('this')
    result = s.rfind(sub)
    if result==-1:
        raise ValueError()
    return result

def __String_splitlines(keepends=False):
    if keepends:
        msg = 'keepends argument of str.splitlines() is not supported'
        raise NotImplementedError(msg)
    s = JS('this')
    return s.py_split('\n')

def __String_translate(table):
    raise NotImplementedError('str.translate() is not supported.')

def __String_zfill(length):
    s = JS('this')
    if len(s) >= length:
        return JS('this.valueOf()')
    else:
        f = '0' * (length - len(s))
        if s[0] == '+' or s[0] == '-':
            return s[0] + f + s[1:]
        return f + s

def __String_getitem(index):
    if isinstance(index, slice):
        s = JS('this')
        lower, upper, step = index.indices(len(s))
        if step == 1:
            return JS('this.slice(lower, upper)')
        elif step == -1:
            msg = 'slice with negative step is not implemented'
            raise NotImplementedError(msg)
        else:
            return ''.join(JS('s.charAt(i)') for i in range(lower, upper, step))
    else:
        if index < 0:
            index += JS('this.length')
        return JS('this.charAt(index)')

JS(r'''
String.prototype.__add__ = function(other) {
    return this + other;
};

String.prototype.__mul__ = function(other) {
	var result = '';
	for(var i = 0; i < other; i ++) {
		result += this;
	}
	return result;
};

String.prototype.__mod__ = function(other) {
	return $m.sprintf(this, other);
};

String.prototype.__len__ = function() {
    return this.length;
};

$m.String_find = function(sub, start, end) {
    var pos=this.indexOf(sub, start);
    if ($m.isUndefined(end)) {
        return pos;
    }

    if (pos + sub.length>end) {
        return -1;
    }
    return pos;
};

$m.String_join = function(data) {
    if (Array.isArray(data)) {
        return data.join(this);
    } else if ($m.isIteratable(data)) {
        var str = $m.str;
        var iter = data.__iter__();
        var arr = [];
        try {
            while (true) {
                arr.push(str(iter.next()));
            }
        } catch (e) {
            if (e.__name__ !== 'StopIteration') {
                throw e;
            }
        }
        return arr.join(this);
    } else {
        throw new $m.TypeError();
    }
};

$m.String_isdigit = function() {
    return (this.match(/^\d+$/g) !== null);
};

$m.String_replace = function(old, replace, count) {
    var do_max=false;
    var start=0;
    var new_str="";
    var pos=0;

    if (!$m.isString(old)) {
        return this.replace(old, replace);
    }
    if (!$m.isUndefined(count)) {
        do_max=true;
    }

    while (start<this.length) {
        if (do_max && !count--) {
            break;
        }

        pos=this.indexOf(old, start);
        if (pos<0) {
            break;
        }

        new_str+=this.substring(start, pos) + replace;
        start=pos+old.length;
    }
    if (start<this.length) {
        new_str+=this.substring(start);
    }

    return new_str;
};

$m.String_split = function(sep, maxsplit) {
    var items=$m.list();
    var do_max=false;
    var subject=this;
    var start=0;
    var pos=0;

    if (sep === undefined || $m.isNull(sep)) {
        sep=" ";
        subject=subject.strip();
        subject=subject.replace(/\s+/g, sep);
    } else {
        if (subject.length === 0) {
            items.append('');
        }
        if (maxsplit !== undefined) {
            do_max=true;
        }
    }

    if (subject.length === 0) {
        return items;
    }

    while (start<subject.length) {
        if (do_max && !maxsplit--) {
            break;
        }

        pos=subject.indexOf(sep, start);
        if (pos<0) {
            break;
        }

        items.append(subject.substring(start, pos));
        start=pos+sep.length;
    }
    if (start<=subject.length) {
        items.append(subject.substring(start));
    }

    return items;
};

$m.String___iter__ = function() {
    var i = 0;
    var s = this;
    return {
        'next': function() {
            if (i >= s.length) {
                throw $m.StopIteration;
            }
            return s.substring(i++, i, 1);
        },
        '__iter__': function() {
            return this;
        }
    };
};

$m.String_strip = function(chars) {
    if (chars === undefined) {
        return this.trim();
    }
    return this.lstrip(chars).rstrip(chars);
};

$m.String_lstrip = function(chars) {
    if (chars === undefined) {
        return this.trimLeft();
    }

    return this.replace(new RegExp("^[" + chars + "]+"), "");
};

$m.String_rstrip = function(chars) {
    if (chars === undefined) {
        return this.trimRight();
    }

    return this.replace(new RegExp("[" + chars + "]+$"), "");
};

$m.String_startswith = function(prefix, start, end) {
    // FIXME: accept tuples as suffix (since 2.5)
    if ($m.isUndefined(start)) {
        start = 0;
    }
    if ($m.isUndefined(end)) {
        end = this.length;
    }

    if ((end - start) < prefix.length) {
        return false;
    }
    return this.indexOf(prefix) === 0;
};

$m.String_endswith = function(suffix, start, end) {
    // FIXME: accept tuples as suffix (since 2.5)
    if ($m.isUndefined(start)) {
        start = 0;
    }
    if ($m.isUndefined(end)) {
        end = this.length;
    }

    if ((end - start) < suffix.length) {
        return false;
    }
    return this.lastIndexOf(suffix) === this.length - suffix.length;
};

$m.String_ljust = function(width, fillchar) {
    if (typeof(width) !== 'number' ||
        parseInt(width, 10) !== width) {
        throw ($m.TypeError("an integer is required"));
    }
    if ($m.isUndefined(fillchar)) {
        fillchar = ' ';
    }
    if (typeof(fillchar) !== 'string' || fillchar.length !== 1) {
        throw ($m.TypeError("ljust() argument 2 must be char, not " + typeof(fillchar)));
    }
    if (this.length >= width) {
        return this.valueOf();
    }
    return this + new Array(width+1 - this.length).join(fillchar);
};
$m.String_rjust = function(width, fillchar) {
    if (typeof(width) !== 'number' || parseInt(width, 10) !== width) {
        throw ($m.TypeError("an integer is required"));
    }
    if ($m.isUndefined(fillchar)) {
        fillchar = ' ';
    }
    if (typeof(fillchar) !== 'string' || fillchar.length !== 1) {
        throw ($m.TypeError("rjust() argument 2 must be char, not " + typeof(fillchar)));
    }
    if (this.length >= width) {
        return this.valueOf();
    }
    return new Array(width + 1 - this.length).join(fillchar) + this;
};

$m.String_center = function(width, fillchar) {
    if (typeof(width) !== 'number' || parseInt(width, 10) !== width) {
        throw ($m.TypeError("an integer is required"));
    }
    if ($m.isUndefined(fillchar)) {
        fillchar = ' ';
    }
    if (typeof(fillchar) !== 'string' || fillchar.length !== 1) {
        throw ($m.TypeError("center() argument 2 must be char, not " + typeof(fillchar)));
    }
    if (this.length >= width) {
        return this.valueOf();
    }
    var padlen = width - this.length;
    var right = Math.ceil(padlen / 2);
    var left = padlen - right;
    var result = new Array(left+1).join(fillchar) + this + new Array(right+1).join(fillchar);
    return result.valueOf();
};

$m.String___contains__ = function(s){
    return this.indexOf(s)>=0;
};

String.prototype.__getitem__ = $m.__String_getitem;
String.prototype.upper = String.prototype.toUpperCase;
String.prototype.lower = String.prototype.toLowerCase;
String.prototype.find=$m.String_find;
String.prototype.join=$m.String_join;
String.prototype.isdigit=$m.String_isdigit;
String.prototype.__iter__=$m.String___iter__;
String.prototype.__contains__=$m.String___contains__;

String.prototype.py_replace=$m.String_replace;

String.prototype.__split=String.prototype.split;
String.prototype.py_split=$m.String_split;
String.prototype.strip=$m.String_strip;
String.prototype.lstrip=$m.String_lstrip;
String.prototype.rstrip=$m.String_rstrip;
String.prototype.startswith=$m.String_startswith;
String.prototype.endswith=$m.String_endswith;
String.prototype.ljust=$m.String_ljust;
String.prototype.rjust=$m.String_rjust;
String.prototype.center=$m.String_center;
String.prototype.capitalize=function() {
    return this.charAt(0).toUpperCase() + this.substr(1).toLowerCase();
};
String.prototype.index=$m.__String_index;
String.prototype.count=$m.__String_count;
String.prototype.isalnum=function() {
    return (/^\w+$/).test(this);
};
String.prototype.isalpha=function() {
    return (/^[a-zA-Z]+$/).test(this);
};
String.prototype.isdigit=function() {
    return (/^\d+$/).test(this);
};
String.prototype.islower=function() {
    return (/[a-z]/).test(this) && ! (/[A-Z]/).test(this);
};
String.prototype.isspace=function() {
    return (/^\s+$/).test(this);
};
String.prototype.istitle=function() {
    return (/^(\s*\b[A-Z]\w*\b\s*)+$/).test(this);
};
String.prototype.isupper=function() {
    return (/[A-Z]/).test(this) && ! (/[a-z]/).test(this);
};
String.prototype.rfind=function(sub) {
    return this.lastIndexOf(sub);
};
String.prototype.rindex=$m.__String_rindex;
String.prototype.splitlines=$m.__String_splitlines;
String.prototype.swapcase=function() {
    return this.replace((/[a-zA-Z]/g), function(s) {
        if (s.isupper()) {
            return s.toLowerCase();
        } else {
            return s.toUpperCase();
        }
    });
};
String.prototype.title=function() {
    return this.replace((/\b[\S]+\b/g), function(s){
        return s.capitalize();
        });
};
String.prototype.translate=$m.__String_translate;
String.prototype.zfill=$m.__String_zfill;
String.prototype.slice=function(lower, upper) {
    if (upper === null) {
        upper = this.length;
    }
    if (lower === null) {
        lower = 0;
    }
    return this.substring(lower, upper);
};

delete $m.__String_count;
delete $m.String_split;
delete $m.__String_index;
delete $m.__String_rindex;
delete $m.__String_splitlines;
delete $m.__String_translate;
delete $m.__String_zfill;
delete $m.__String_getitem;

$m.pow=Math.pow;
''')

def abs(x):
    return x.__abs__(x)
def __Number_as_integer_ratio():
    raise NotImplementedError('float.as_integer_ratio() is not supported.')

def __Number_hex():
    raise NotImplementedError('float.hex() is not supported.')

def __Number_fromhex():
    raise NotImplementedError('float.fromhex() is not supported.')

JS('''
Number.prototype.as_integer_ratio=$m.__Number_as_integer_ratio;
Number.prototype.hex=$m.__Number_hex;
Number.prototype.fromhex=$m.__Number_fromhex;
Number.prototype.__mul__ = function(other) {
	return this * other;
};

Number.prototype.__mod__ = function(other) {
	return this % other;
};

Number.prototype.__add__ = function(other) {
    return this + other;
};

Number.prototype.__sub__ = function(other) {
    return this - other;
};

Number.prototype.__abs__ = Math.abs;

Number.prototype.__neg__ = function() {
    return -this;        
};

Number.prototype.__floordiv__ = function(other) {
    var remainder = this % other;
    return (this - remainder) / other;
};

Number.prototype.__div__ = function(other) {
    return this / other;
};

Number.prototype.__and__ = function(other) {
    return this & other;
}

Number.prototype.__or__ = function(other) {
    return this | other;
}

Number.prototype.__xor__ = function(other) {
    return this ^ other;
}

delete $m.__Number_as_integer_ratio;
delete $m.__Number_hex;
delete $m.__Number_fromhex;
''')
_loaded_modules = {'__builtin__': JS('$m')}

def _get_stack_trace():
    def rsplit_two(s):
        idx = s.rfind(':')
        if idx == -1:
            return s, '-1'
        return s[:idx], s[idx + 1:]

    lines = ''
    result = []
    JS(r'''
    try {
        throw new Error('');
    } catch(e) {
        if (e.stack) { //Firefox or chrome
            lines = e.stack;''')

    for line in lines.splitlines():
        if line.count('/') < 4:
            continue
        idx = line.find('/')
        idx = line.find('/', idx+1)
        idx = line.find('/', idx+1)
        line = line[idx+1:]
        words = line.py_split(':')
        if len(words) < 2:
            continue
        file = words[0]
        file = file[file.index('/') + 1:]
        jsline = words[1]
        result.append([jsline, file])

    JS(r'''
    } else if (e.stacktrace) { //Opera
        lines = e.stacktrace;''')
    lineno = 0
    words = None
    re = JS('/Line\s(\d+) of linked script (.*)/')
    for line in lines.splitlines():
        lineno += 1
        if lineno % 2 == 0:
            continue
        words = JS('$m.list(re.exec(line))')
        if len(words) < 3:
            continue
        result.append(words[1:3])
    JS('''
    }
}
''')
    return result[2:]

def _get_pyfile(module_obj):
    if module_obj is not None:
        return getattr(module_obj, '__file__', None)
    else:
        return None

def _get_pyline(m, jsline):
    if not m or not hasattr(m, '__srcmap__'):
        return -1
    JS('''
    for (var i = jsline; i >= 0; i --) {
        var result = m.__srcmap__[i];
        if (result === undefined) {
            return -1;
        } else if (result !== -1) {
            return result;
        }
    }
    ''')
    return -1

def _get_pysrc(m, pyline):
    if pyline == -1:
        return 'n/a'
    return m.__src__[pyline - 1].lstrip()

def _basename(url):
    idx = url.rfind('/')
    return url[idx + 1:]

def _extract_stack():
    def get_module_name(jsfile):
        result = jsfile[:-3]
        result = result.py_replace('/', '.')
        return result

    lines = _get_stack_trace()
    result = []
    for l in lines:
        jsline, jsfile = int(l[0]), l[1] 
        module_name = get_module_name(jsfile)

        m = _loaded_modules.get(module_name, None)
        file = _get_pyfile(m)
        line = _get_pyline(m, jsline)
        src = _get_pysrc(m, line)
        result.append((src, file, line, jsline))

    result.reverse()
    return result

def _issubtype(object_, classinfo):
    JS("""
    if (object_.__is_instance__ === null || classinfo.__is_instance__ === null) {
        return false;
    }
    for (var c in object_.__mro__) {
        if (object_.__mro__.hasOwnProperty(c) && 
            object_.__mro__[c] === classinfo.prototype) {
            return true;
        }
    }
    """)
    return False

def _get_super_method(type_, instance, name):
    JS("""
    var bases = type_.__mro__;
    var len = bases.length;
    for (var i = 1; i < len; i ++) {
        if (bases[i].hasOwnProperty($name$)) {
            var func = bases[i][$name$];
            var result = func.bind(instance);
            result.__name__ = $name$;
            result.__args__ = func._args__;
            result.__bind_type__ = func.__bind_type__;
            return result;
        }
    }
    """)
    raise TypeError('can not get super method')

def super(type_, object_or_type=None):
    # This is a partially implementation: only super(type, object)
    if not _issubtype(object_or_type, type_):
        raise TypeError("super(type, obj): obj must be an instance or subtype of type")
    JS("""
    var fn = pyjs_type('super', type_.__mro__.slice(1));
    fn.__init__ = fn.__mro__[1].__init__;
    if (object_or_type.__is_instance__ === false) {
        return fn;
    }
    var obj = {};
    function wrapper(obj, $name$) {
        var fnwrap = obj[$name$].bind(object_or_type);
        fnwrap.__name__ = $name$;
        fnwrap.__args__ = obj[$name$].__args__;
        fnwrap.__bind_type__ = obj[$name$].__bind_type__;
        return fnwrap;
    }
    for (var m in fn) {
        if (fn.hasOwnProperty(m) && typeof fn[m] === 'function') {
            obj[m] = wrapper(fn, m);
        }
    }
    return obj;
    """)

def __empty_kwarg():
    result = {}
    result._pyjs_is_kwarg = True
    return result

JS('''
$m.module = function(name, file) {
    this.__name__ = name;
    this.__file__ = file;
    $m._add_loaded_module(name, this);
};
$m.module.prototype = $m;
''')

import hal
