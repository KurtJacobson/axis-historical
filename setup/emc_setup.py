__all__ = ['find_emc_root', 'find_emc_plat']

import os

def is_emc_root(f):
    return (os.path.isdir(os.path.join(f, "emc", "src"))
        and os.path.isdir(os.path.join(f, "emc", "plat"))
        and os.path.isdir(os.path.join(f, "rcslib", "src"))
        and os.path.isdir(os.path.join(f, "rcslib", "plat")))

builtin_candidates = ['/usr/local/emc','/usr/emc','/usr/src','/usr/local/src']

def find_emc_root(candidates = []):
    for c in candidates + builtin_candidates:
        if is_emc_root(c): return c

def find_emc_plat(root):
    platdir = os.path.join(root, "emc", "plat")
    for plat in ['nonrealtime'] + os.listdir(platdir):
        inivar = os.path.join(platdir, plat, "bin", "inivar")
        if os.path.exists(inivar): return plat
