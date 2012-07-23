# -*- coding: utf-8 -*-
from __spork__ import JS
from __builtin__ import _loaded_modules as modules

JS('console.log("init sys");')

platform = JS('navigator.userAgent.toLowerCase()')

if 'ie' in platform:
    platform = 'ie'
elif 'mozilla' in platform:
    platform = 'mozilla'
elif 'opera' in platform:
    platform = 'opera'
else:
    msg = 'browser ' + platform + ' is not supported.'
    JS('alert(msg);')
    JS('throw msg;')

