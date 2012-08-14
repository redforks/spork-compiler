if(!String.prototype.trim) {
  String.prototype.trim = function () {
    return this.replace(/^\s+|\s+$/g,'');
  };
}

if (!String.prototype.trimLeft) {
    String.prototype.trimLeft = function () {
        return this.replace(/^\s+/, "");
    }
}

if (!String.prototype.trimRight) {
    String.prototype.trimRight = function () {
        return this.replace(/\s+$/, "");
    }
}

if (!Function.prototype.bind) {
	Function.prototype.bind = function (oThis) {
			if (typeof this !== "function") {
				throw new TypeError("Function.prototype.bind - what is trying to be bound is not callable");
			}

			var aArgs = Array.prototype.slice.call(arguments, 1),
					fToBind = this,
					fNOP = function () {},
					fBound = function () {
					return fToBind.apply(this instanceof fNOP ? this : oThis || window,
							aArgs.concat(Array.prototype.slice.call(arguments)));
					};

			fNOP.prototype = this.prototype;
			fBound.prototype = new fNOP();

			return fBound;
	};
}

if (!Object.create) {
    Object.create = function (o) {
        if (arguments.length > 1) {
            throw new Error('Object.create implementation only accepts the first parameter.');
        }
        function F() {}
        F.prototype = o;
        return new F();
    };
}

if(!Array.isArray) {
  Array.isArray = function (vArg) {
    return Object.prototype.toString.call(vArg) === "[object Array]";
  };
}

if (!Object.keys) {
  Object.keys = (function () {
    var hasOwnProperty = Object.prototype.hasOwnProperty,
        hasDontEnumBug = !({toString: null}).propertyIsEnumerable('toString'),
        dontEnums = [
          'toString',
          'toLocaleString',
          'valueOf',
          'hasOwnProperty',
          'isPrototypeOf',
          'propertyIsEnumerable',
          'constructor'
        ],
        dontEnumsLength = dontEnums.length

    return function (obj) {
      if (typeof obj !== 'object' && typeof obj !== 'function' || obj === null) throw new TypeError('Object.keys called on non-object')

      var result = []

      for (var prop in obj) {
        if (hasOwnProperty.call(obj, prop)) result.push(prop)
      }

      if (hasDontEnumBug) {
        for (var i=0; i < dontEnumsLength; i++) {
          if (hasOwnProperty.call(obj, dontEnums[i])) result.push(dontEnums[i])
        }
      }
      return result
    }
  })()
};

if (!Date.now) {
  Date.now = function now() {
    return +(new Date);
  };
}

function _sf_import(js) {
	var code = null;
	$.ajax({
		async: false, 
		dataType: 'text', 
		cache: true,
		url: sflib + js,
		success: function(jscode) {
			code = jscode;
		}
	});
	if (code) {
		eval(code);
		return true;
	}
	return false;
}

function get_pyjs_type_name(x){
    if (x && x.__is_instance__) {
      return x.__name__;
    }
    return null;
}

function pyjs_copy_attrs(src, dst) {
    for (var p in src) {
        if (src.hasOwnProperty(p)) {
            dst[p] = src[p];
        }
    }
}

function pyjs__exception_func_unexpected_keyword(func_name, key) {
    throw $b.TypeError(String(func_name + "() got an unexpected keyword argument '" + key + "'"));
}

function pyjs_set_arg_call(obj, func, args) {
    "use strict";
    if (obj !== null) {
        func = obj[func];
    }

    var c_args = [], d_args = func.__args__, a, aname, d_idx = 2, c_idx = 1;
    if (obj === null) {
        if (func.__is_instance__ === false) {
            d_idx ++;
        }
    } else if (func.__bind_type__ > 0) {
        d_idx ++;
    }

    for (; d_idx < d_args.length; d_idx++, c_idx++) {
        aname = d_args[d_idx];
        a = args[0][aname];
        if (args[c_idx] === undefined) {
            c_args.push(a);
            delete args[0][aname];
        } else {
            c_args.push(args[c_idx]);
        }
    }

    if (d_args[0] !== null) {
        for (;c_idx < args.length;c_idx++) {
            c_args.push(args[c_idx]);
        }
    }

    if (d_args[1] !== null) {
        a = $b.dict(args[0]);
        a._pyjs_is_kwarg = true;
        c_args.push(a);
    } else {
        for (var kwname in args[0]) {
            if (args[0].hasOwnProperty(kwname)) {
                pyjs__exception_func_unexpected_keyword(func.__name__, kwname);
            }
        }
    }
    return func.apply(obj, c_args);
}

function pyjs_kwargs_call(obj, func, star_args, dstar_args, args)
{
    "use strict";
    var __i, i;

    if (dstar_args) {
        __i = $b._iter_init(dstar_args);
        while ((i = __i()) !== undefined) {
            args[0][i] = dstar_args.__getitem__(i);
        }
    }

    if (star_args) {
        args = args.concat(star_args.l);
    }

    return pyjs_set_arg_call(obj, func, args);
}

function pyjs__class_instance(class_name, module_name) {
"use strict";
    var cls_fn = function() {
        var instance = Object.create(cls_fn);
        instance.__class__ = cls_fn;
        instance.__is_instance__ = true;
        cls_fn.__init__.apply(instance, arguments);
        return instance;
    };
    cls_fn.__name__ = class_name;
    cls_fn.__module__ = module_name;
    return cls_fn;
}

function pyjs__bind_method(func_name, func, bind_type, args) {
"use strict";
    func.__bind_type__ = bind_type;
    func.__is_method__ = true;
    return pyjs__bind_func(func_name, func, args);
}

function pyjs__bind_func(func_name, func, args) {
"use strict";
    func.__name__ = func_name;
    func.__args__ = args;
    return func;
}

function _do_pyjs__class_function(cls_fn, prop, mro) {
    "use strict";
    var class_name = cls_fn.__name__;
    var class_module = cls_fn.__module__;

    for (var i = mro.length-1; i >= 1; i--) {
        pyjs_copy_attrs(mro[i], cls_fn);
    }
    pyjs_copy_attrs(prop, cls_fn);

    cls_fn.__name__ = class_name;
    cls_fn.__module__ = class_module;
    cls_fn.__mro__ = mro;
    cls_fn.prototype = cls_fn;
    cls_fn.__is_instance__ = false;
    cls_fn.__args__ = cls_fn.__init__.__args__;
    return cls_fn;
}

function pyjs__class_function_single_base(cls_fn, prop, base) {
    "use strict";
    var mro = [cls_fn].concat(base.__mro__);
    return _do_pyjs__class_function(cls_fn, prop, mro);
}

function pyjs__class_function(cls_fn, prop, bases) {
    "use strict";
    function pyjs__mro_merge(seqs, cls) {
        function isHead(seqs, cand) {
            for (var i = 0, len1=seqs.length; i < len1; i ++) {
                var seq1 = seqs[i];
                for (var j = 1, len2=seq1.length; j < len2; j++) {
                    if (cand === seq1[j]) {
                        return false;
                    }
                }
            }
            return true;
        }

        function getCand(seqs) {
            var candidates = [];
            for (var i=0, len=seqs.length; i<len; i++) {
                var cand = seqs[i][0];
                candidates.push(cand);
                if (isHead(seqs, cand)) {
                    return cand;
                }
            }
            throw $b.TypeError("Cannot create a consistent method resolution order (MRO) for bases " + candidates[0].__name__ + ", "+ candidates[1].__name__);
        }

        function remove_cand(seqs, cand) {
            for (var i = 0; i < seqs.length;) {
                var s = seqs[i];
                if (s[0] === cand) {
                    s.shift();
                    if (s.length === 0) {
                        seqs.splice(i, 1);
                        continue;
                    }
                }
                i ++;
            }
        }

        var res = [cls];
        for (; seqs.length!==0;) {
            var cand = getCand(seqs);
            res.push(cand);
            remove_cand(seqs, cand);
        }
        return res;
    }

    function merge_mro(cls, bases) {
        var result = [];
        for (var i = 0; i < bases.length; i++) {
            if (bases[i].__mro__ !== null) {
                result.push(bases[i].__mro__.slice(0));
            }
        }
        return pyjs__mro_merge(result, cls);
    }

    var mro = merge_mro(cls_fn, bases);
    return _do_pyjs__class_function(cls_fn, prop, mro);
}

/* creates a class, derived from bases, with methods and variables */
function pyjs_type(clsname, bases)
{
"use strict";
    var cls_instance = pyjs__class_instance(clsname);
    return pyjs__class_function(cls_instance, {}, bases);
}

$(window).error(function(e){
    e = e.originalEvent;
    if (e && e.message) {
        var msg = e.message;
        if (msg.indexOf('Uncaught ') === 0) {
            msg = msg.substring(9);
        }
        alert(msg);
    } else {
        alert('Runtime error');
    }
});
