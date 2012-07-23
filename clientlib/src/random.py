# -*- coding: utf-8 -*-
from __spork__ import JS

def randint(a, b):
    """Return random integer in range [a, b], including both end points.
    """

    return a + int(random() * (b - a + 1))

def choice(seq):
    """Choose a random element from a non-empty sequence."""
    return seq[int(random() * len(seq))]  # raises IndexError if seq is empty

def random():
    'Return the next random floating point number in the range [0.0, 1.0]'
    return JS('Math.random()')
