import commands
import _tkinter
import os

def removesuffix(s, suff):
    i = s.find(suff)
    if i == -1: return s
    return s[:i]

def add(l, c):
    if c in l: return
    l.append(c)

def add_if_exists(l, c):
    c = os.path.abspath(c)
    if c in l: return
    if c.startswith("/lib"): return
    if not os.path.exists(c): return
    l.append(c)

def get_togl_flags():

    libs = ['X11', 'GL', 'GLU', 'Xmu']
    lib_dirs = []
    include_dirs = []

    tcl_library = None
    tk_library = None
    lddinfo = commands.getoutput("ldd %s" % _tkinter.__file__)
    tkinterlibs = [line.strip().split(" => ") for line in lddinfo.split("\n")]
    for l, m in tkinterlibs:
        m = m.split("(")[0].strip()
        add_if_exists(lib_dirs, os.path.join(m, ".."))
        if l.startswith("lib"): l = l[3:]
        if l.startswith("tcl"):
            tcl_library = removesuffix(l, ".so")
            add_if_exists(include_dirs, os.path.join(m, "..", "..", "include", l[:6]))
            add_if_exists(include_dirs, os.path.join(m, "..", "..", "include"))
        if l.startswith("tk"):
            tk_library = removesuffix(l, ".so")
            add_if_exists(include_dirs, os.path.join(m, "..", "..", "include", l[:5]))
            add_if_exists(include_dirs, os.path.join(m, "..", "..", "include"))

    if not tcl_library: raise RuntimeError, "not able to find tcl library"
    if not tk_library: raise RuntimeError, "not able to find tk library"
    libs.extend([tcl_library, tk_library])
    return {'include_dirs': include_dirs, 'library_dirs': lib_dirs, 
            'libraries': libs} 

# vim:sw=4:sts=4:et:
