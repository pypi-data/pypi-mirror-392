from . import _core

def create_window(w=800, h=600, title="Leo 3D"):
    return _core.create_window(w, h, title)

def running():
    return not _core.window_should_close()

def clear(r=0, g=0, b=0):
    _core.clear(r, g, b)

def swap():
    _core.swap()