#    This is a component of AXIS, a front-end for emc
#    Copyright 2004, 2005 Jeff Epler <jepler@unpythonic.net>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

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
