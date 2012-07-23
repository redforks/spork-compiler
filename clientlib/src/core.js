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
    throw __builtin__.TypeError(String(func_name + "() got an unexpected keyword argument '" + key + "'"));
}

function pyjs_kwargs_call(obj, func, star_args, dstar_args, args)
{
    "use strict";
    var __i, i;
    if (obj !== null) {
        func = obj[func];
    }

    // Merge dstar_args into args[0]
    if (dstar_args) {
        __i = dstar_args.__iter__();
        try {
            while (true) {
                i = __i.next();
                args[0][i] = dstar_args.__getitem__(i);
            }
        } catch (e) {
            if (e.__name__ !== 'StopIteration') {
                throw e;
            }
        }
    }

    // Append star_args to args
    if (star_args) {
        args = args.concat(star_args.l);
    }

    // Now convert args to call_args
    // args = __kwargs, arg1, arg2, ...
    // _args = arg1, arg2, arg3, ... [*args, [**kwargs]]
    var _args = [];
    var __args__ = func.__args__;
    var a, aname, _idx , idx, res;
    _idx = idx = 1;
    if (obj === null) {
        if (func.__is_instance__ === false) {
            // Skip first argument in __args__
            _idx ++;
        }
    } else {
        if (obj.__is_instance__ === undefined && func.__is_instance__ !== undefined && func.__is_instance__ === false) {
            // Skip first argument in __args__
            _idx ++;
        } else if (func.__bind_type__ > 0) {
            if (args[1] === undefined || obj.__is_instance__ !== false || args[1].__is_instance__ !== true) {
                // Skip first argument in __args__
                _idx ++;
            }
        }
    }
    for (++_idx; _idx < __args__.length; _idx++, idx++) {
        aname = __args__[_idx][0];
        a = args[0][aname];
        if (args[idx] === undefined) {
            _args.push(a);
            delete args[0][aname];
        } else {
            _args.push(args[idx]);
        }
    }

    // Append the left-over args
    for (;idx < args.length;idx++) {
        _args.push(args[idx]);
    }

    if (__args__[1] === null) {
        // Check for unexpected keyword
        for (var kwname in args[0]) {
            if (args[0].hasOwnProperty(kwname)) {
                pyjs__exception_func_unexpected_keyword(func.__name__, kwname);
            }
        }
        return func.apply(obj, _args);
    }
    a = __builtin__.dict(args[0]);
    a._pyjs_is_kwarg = true;
    _args.push(a);
    res = func.apply(obj, _args);
    return res;
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
    func.__name__ = func_name;
    func.__bind_type__ = bind_type;
    func.__args__ = args;
    func.__is_method__ = true;
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
            throw __builtin__.TypeError("Cannot create a consistent method resolution order (MRO) for bases " + candidates[0].__name__ + ", "+ candidates[1].__name__);
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
