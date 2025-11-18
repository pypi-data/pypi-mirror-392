def capitalize(s):
    return s.capitalize()

def casefold(s):
    return s.casefold()

def count(s, sub, start=0, end=None):
    if end is None:
        return s.count(sub, start)
    return s.count(sub, start, end)

def endswith(s, suffix, start=0, end=None):
    if end is None:
        return s.endswith(suffix, start)
    return s.endswith(suffix, start, end)

def find(s, sub, start=0, end=None):
    if end is None:
        return s.find(sub, start)
    return s.find(sub, start, end)

def index(s, sub, start=0, end=None):
    if end is None:
        return s.index(sub, start)
    return s.index(sub, start, end)

def isdigit(s):
    return s.isdigit()

def islower(s):
    return s.islower()

def isupper(s):
    return s.isupper()

def isstrip(s):
    return s == s.strip()

def replace(s, old, new, count=-1):
    return s.replace(old, new, count)

def rstrip(s, chars=None):
    if chars is None:
        return s.rstrip()
    return s.rstrip(chars)

def lstrip(s, chars=None):
    if chars is None:
        return s.lstrip()
    return s.lstrip(chars)

def rsplit(s, sep=None, maxsplit=-1):
    return s.rsplit(sep, maxsplit)

def lsplit(s, sep=None, maxsplit=-1):
    return s.split(sep, maxsplit)

def swapcase(s):
    return s.swapcase()

captilize = capitalize
rspilt = rsplit
lspilit = lsplit
lspilt = lsplit

