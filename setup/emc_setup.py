__all__ = ['find_emc_root', 'find_emc_plat']

import os

def is_emc_root(f):
    if os.path.exists(os.path.join(f, "include", "emc.hh")): return True
    return (os.path.isdir(os.path.join(f, "emc", "src"))
        and os.path.isdir(os.path.join(f, "emc", "plat"))
        and os.path.isdir(os.path.join(f, "rcslib", "src"))
        and os.path.isdir(os.path.join(f, "rcslib", "plat")))

builtin_candidates = [
        os.path.abspath(".."), os.path.abspath("../.."),
	'/usr/local/emc2', '/usr/emc2', '/usr/src/emc2', '/usr/local/src/emc2',
	'/usr/local/emc', '/usr/emc', '/usr/src', '/usr/local/src',
	'/usr/local', '/usr']

if os.environ.has_key('HOME'):
    builtin_candidates.insert(0, os.path.abspath(os.environ['HOME']))

def find_emc_root(candidates = []):
    for c in candidates + builtin_candidates:
        if is_emc_root(c): return c

def find_emc_plat(root):
    emcplatdir = os.path.join(root, "emc", "plat")
    rcsplatdir = os.path.join(root, "rcslib", "plat")
    
    for plat in ['nonrealtime'] + os.listdir(emcplatdir):
        inivar = os.path.join(emcplatdir, plat, "bin", "inivar")
        rcsinc = os.path.join(rcsplatdir, plat, "include", "rcs.hh")
        if os.path.exists(inivar) and os.path.exists(rcsinc): return plat
