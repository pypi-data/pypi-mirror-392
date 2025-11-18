from .bbi_reader import BBIReader

def open(path, **kargs):
    return BBIReader(path, **kargs)
