from .internal import add_cleanup_step
import gettext

gettext.install('spork')
del gettext

class SporkError(Exception):
    '''General runtime exception of Spork lib
    
    SporkError not intend for catching, they're indicate runtime 
    validation Exceptions, like bad function parameter.
    '''
    pass
