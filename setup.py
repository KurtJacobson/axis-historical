#!/usr/bin/env python
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

import sys, os
sys.path.insert(0, "lib")
sys.path.insert(0, "setup")

from glob import glob
from distutils import sysconfig
from distutils.core import setup, Extension
from build_scripts import *
from togl_setup import get_togl_flags
from emc_setup import *
import distutils.command.install

name="axis"
version="1.0"
DOCDIR="share/doc/%s-%s" % (name, version)
SHAREDIR="share/%s" % (name)

emcroot = os.getenv("EMCROOT", find_emc_root())
if emcroot is None:
    print """\
setup.py failed to locate the root directory of your emc installation.
Determine the location of your emc installation and re-run setup.py with a
commandline like this:
    $ env EMCROOT=/usr/local/emc python setup.py install

See the README file for more information.
"""
    raise SystemExit, 1

emc2_marker = os.path.join(emcroot, "include", "emc.hh")
is_emc2 = os.path.exists(emc2_marker)
if is_emc2:
    distutils.command.install.INSTALL_SCHEMES['unix_prefix']['scripts'] = \
            "%s/bin" % (emcroot)
    print "Building for EMC2 in", emcroot


    gcode = Extension("gcode", [
            "extensions/gcodemodule.cc"
        ],
        define_macros = [('AXIS_USE_EMC2', 1)],
        include_dirs=[
            os.path.join(emcroot, "include"),
        ],
        library_dirs = [
            os.path.join(emcroot, "lib")
        ],
        extra_link_args = [
            '-DNEW_INTERPRETER', 
            '-Wl,-rpath,%s' % 
            os.path.join(emcroot, "lib"),
            os.path.join(emcroot, "src", ".tmp", "rs274.o"),
            '-lnml', '-lm', '-lstdc++',
        ]
    )

    emc = Extension("emc", ["extensions/emcmodule.cc"],
        define_macros=[('DEFAULT_NMLFILE',
            '"%s/configs/emc.nml"' % emcroot),
            ('AXIS_USE_EMC2', 1)],
        include_dirs=[
            os.path.join(emcroot, "include")
        ],
        library_dirs = [
            os.path.join(emcroot, "lib")
        ],
        libraries = ["emc", "nml", "m", "stdc++"],
        extra_link_args = ['-Wl,-rpath,%s' % 
            os.path.join(emcroot, "lib")]
    )
else:
    emcplat = os.getenv("PLAT", find_emc_plat(emcroot))
    if emcplat is None:
        print """\
    setup.py failed to locate the (non-realtime) platform of your emc
    installation.  Determine the platform name and re-run setup.py with a
    commandline like this:
        $ env PLAT=nonrealtime python setup.py install

    If you had to specify EMCROOT, the commandline would look like
        $ env EMCROOT=/usr/local/emc PLAT=nonrealtime python setup.py install

    See the README file for more information.
    """
        raise SystemExit, 1
    distutils.command.install.INSTALL_SCHEMES['unix_prefix']['scripts'] = \
            "%s/emc/plat/%s/bin" % (emcroot, emcplat)
    print "Building for EMC in", emcroot
    print "Non-realtime PLAT", emcplat

    gcode = Extension("gcode", [
            "extensions/gcodemodule.cc"
        ],
        include_dirs=[
            os.path.join(emcroot, "emc", "plat", emcplat, "include",
                 "rs274ngc_new"),
            os.path.join(emcroot, "emc", "plat", emcplat, "include"),
            os.path.join(emcroot, "rcslib", "plat", emcplat, "include")
        ],
        library_dirs = [
            os.path.join(emcroot, "emc", "plat", emcplat, "lib"),
            os.path.join(emcroot, "rcslib", "plat", emcplat, "lib")
        ],
        extra_link_args = [
            '-DNEW_INTERPRETER', 
            '-Wl,-rpath,%s' % 
                os.path.join(emcroot, "rcslib", "plat", emcplat, "lib"),
            os.path.join(emcroot, "emc", "plat", emcplat, "lib", "rs274abc.o"),
            '-lrcs', '-lm', '-lstdc++',
        ]
    )

    emc = Extension("emc", ["extensions/emcmodule.cc"],
        define_macros=[('DEFAULT_NMLFILE', '"%s/emc/emc.nml"' % emcroot)],
        include_dirs=[
            os.path.join(emcroot, "emc", "plat", emcplat, "include"),
            os.path.join(emcroot, "rcslib", "plat", emcplat, "include")
        ],
        library_dirs = [
            os.path.join(emcroot, "emc", "plat", emcplat, "lib"),
            os.path.join(emcroot, "rcslib", "plat", emcplat, "lib")
        ],
        libraries = ["emc", "rcs", "m", "stdc++"],
        extra_link_args = ['-Wl,-rpath,%s' % 
            os.path.join(emcroot, "rcslib", "plat", emcplat, "lib")]
    )

togl = Extension("_togl", ["extensions/_toglmodule.c"], **get_togl_flags())
glfixes = Extension("_glfixes", ["extensions/_glfixes.c"], libraries = ["GL"], 
	library_dirs = ["/usr/X11R6/lib"])

setup(name=name, version=version,
    description="AXIS front-end for emc",
    author="Jeff Epler", author_email="jepler@unpythonic.net",
    package_dir={'': 'lib', 'rs274' : 'rs274'},
    packages=['', 'rs274'],
    scripts={WINDOWED('axis'): 'scripts/axis.py',
             TERMINAL('mdi'): 'scripts/mdi.py'},
    cmdclass = {'build_scripts': build_scripts},
    data_files = [(os.path.join(SHAREDIR, "tcl"), glob("tcl/*.tcl")),
                  (os.path.join(SHAREDIR, "tcl"), glob("tcl/axis.nf")),
                  (os.path.join(SHAREDIR, "tcl"), glob("thirdparty/*.tcl")),
                  (os.path.join(SHAREDIR, "tcl/bwidget"),
                                       glob("thirdparty/bwidget/*.tcl")),
                  (os.path.join(SHAREDIR, "tcl/bwidget/lang"),
                                       glob("thirdparty/bwidget/lang/*.rc")),
                  (os.path.join(SHAREDIR, "tcl/bwidget/images"),
                                       glob("thirdparty/bwidget/images/*.gif")),
                  (os.path.join(SHAREDIR, "tcl/bwidget/images"),
                                       glob("thirdparty/bwidget/images/*.xbm")),
                  (os.path.join(SHAREDIR, "images"), glob("images/*.gif")),
                  (os.path.join(SHAREDIR, "images"), glob("images/*.xbm")),
                  (DOCDIR, ["COPYING", "README", "BUGS",
                        "thirdparty/bwidget/LICENSE.txt",
                        "thirdparty/LICENSE-Togl"])],
    ext_modules = [emc, glfixes, togl, gcode],
    url="http://axis.unpythonic.net/",
    license="GPL",
)

# vim:ts=8:sts=4:et:
