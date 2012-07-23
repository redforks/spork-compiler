# -*- coding: utf-8 -*-

from __builtin__ import _extract_stack as extract_stack

def format_list(tr):
    result = []
    for item in tr:
        result.append('File "%s", line %s jsline %s' % (item[1], item[2],
            item[3]))
        result.append('    ' + item[0])
    return result

def format_stack():
    return format_list(extract_stack())
