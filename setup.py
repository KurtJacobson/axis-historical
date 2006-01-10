#!/usr/bin/env python
#    This is a component of AXIS, a front-end for emc
#    Copyright 2004, 2005, 2006 Jeff Epler <jepler@unpythonic.net>
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
from distutils.command.install_data import install_data
from distutils.util import convert_path
from distutils import log
import distutils.file_util

def copy_file (src, dst,
               preserve_mode=1,
               preserve_times=1,
               update=0,
               link=None,
               verbose=0,
               dry_run=0):

    """Copy a file 'src' to 'dst'.  If 'dst' is a directory, then 'src' is
    copied there with the same name; otherwise, it must be a filename.  (If
    the file exists, it will be ruthlessly clobbered.)  If 'preserve_mode'
    is true (the default), the file's mode (type and permission bits, or
    whatever is analogous on the current platform) is copied.  If
    'preserve_times' is true (the default), the last-modified and
    last-access times are copied as well.  If 'update' is true, 'src' will
    only be copied if 'dst' does not exist, or if 'dst' does exist but is
    older than 'src'.

    'link' allows you to make hard links (os.link) or symbolic links
    (os.symlink) instead of copying: set it to "hard" or "sym"; if it is
    None (the default), files are copied.  Don't set 'link' on systems that
    don't support it: 'copy_file()' doesn't check if hard or symbolic
    linking is available.

    Under Mac OS, uses the native file copy function in macostools; on
    other systems, uses 'distutils.file_util._copy_file_contents()' to copy
    file contents.

    Return a tuple (dest_name, copied): 'dest_name' is the actual name of
    the output file, and 'copied' is true if the file was copied (or would
    have been copied, if 'dry_run' true).
    """
    # XXX if the destination file already exists, we clobber it if
    # copying, but blow up if linking.  Hmmm.  And I don't know what
    # macostools.copyfile() does.  Should definitely be consistent, and
    # should probably blow up if destination exists and we would be
    # changing it (ie. it's not already a hard/soft link to src OR
    # (not update) and (src newer than dst).

    from distutils.dep_util import newer
    from stat import ST_ATIME, ST_MTIME, ST_MODE, S_IMODE

    if not os.path.isfile(src):
        raise DistutilsFileError, \
              "can't copy '%s': doesn't exist or not a regular file" % src

    if os.path.isdir(dst):
        dir = dst
        dst = os.path.join(dst, os.path.basename(src))
    else:
        dir = os.path.dirname(dst)

    try:
        action = distutils.file_util._copy_action[link]
    except KeyError:
        raise ValueError, \
              "invalid value '%s' for 'link' argument" % link
    if os.path.basename(dst) == os.path.basename(src):
        log.info("%s %s -> %s", action, src, dir)
    else:
        log.info("%s %s -> %s", action, src, dst)

    if dry_run:
        return (dst, 1)

    # On Mac OS, use the native file copy routine
    if os.name == 'mac':
        import macostools
        try:
            macostools.copy(src, dst, 0, preserve_times)
        except os.error, exc:
            raise DistutilsFileError, \
                  "could not copy '%s' to '%s': %s" % (src, dst, exc[-1])

    # If linking (hard or symbolic), use the appropriate system call
    # (Unix only, of course, but that's the caller's responsibility)
    elif link == 'hard':
        if not (os.path.exists(dst) and os.path.samefile(src, dst)):
            os.link(src, dst)
    elif link == 'sym':
        if not (os.path.exists(dst) and os.path.samefile(src, dst)):
            os.symlink(src, dst)

    # Otherwise (non-Mac, not linking), copy the file contents and
    # (optionally) copy the times and mode.
    else:
        distutils.file_util._copy_file_contents(src, dst)
        if preserve_mode or preserve_times:
            st = os.stat(src)

            # According to David Ascher <da@ski.org>, utime() should be done
            # before chmod() (at least under NT).
            if preserve_times:
                os.utime(dst, (st[ST_ATIME], st[ST_MTIME]))
            if preserve_mode:
                os.chmod(dst, S_IMODE(st[ST_MODE]))

    return (dst, 1)
distutils.file_util.copy_file = copy_file
# copy_file ()


name="axis"
version="1.2a0"
DOCDIR="share/doc/%s-%s" % (name, version)
SHAREDIR="share/%s" % (name)
LOCALEDIR="share/locale"

emcroot = os.path.abspath(os.getenv("EMCROOT", None) or find_emc_root())
if emcroot is None:
    print """\
setup.py failed to locate the root directory of your emc installation.
Determine the location of your emc installation and re-run setup.py with a
commandline like this:
    $ env EMCROOT=/usr/local/emc python setup.py install

See the README file for more information."""
    raise SystemExit, 1

simple_install = os.getenv("SIMPLEINSTALL", False)

emc2_marker = os.path.join(emcroot, "include", "config.h")
is_emc2 = os.path.exists(emc2_marker)
bdi4_marker = os.path.join(emcroot, "src/include", "config.h")
is_bdi4 = os.path.exists(bdi4_marker)

minigl = Extension("minigl",
        ["extensions/minigl.c"],
        libraries = ["GL", "GLU"],
	library_dirs = ["/usr/X11R6/lib"])

if simple_install:
    try:
        import emc, gcode, _togl
    except ImportError, detail:
        print "%s.  SIMPLE_INSTALL won't work" % (detail.args[0])
        raise SystemExit, 1
    d1 = os.path.join(emcroot, "plat", "*", "bin")
    d2 = os.path.join(emcroot, "emc", "plat", "*", "bin")
    for bin in ['bin', 'emc/bin'] + glob(d1) + glob(d2):
        existing_script = os.path.join(emcroot, bin, "axis")
        if os.path.exists(existing_script):
            INSTALL_SCHEMES = distutils.command.install.INSTALL_SCHEMES
            INSTALL_SCHEMES['unix_prefix']['scripts'] = \
                os.path.join(emcroot, bin)
            print "SIMPLE_INSTALL bindir is", bin
            break
    else:
        print "Existing 'axis' script not found.  SIMPLE_INSTALL won't work"
        raise SystemExit, 1
elif is_emc2:
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
elif is_bdi4:
    distutils.command.install.INSTALL_SCHEMES['unix_prefix']['scripts'] = \
            "%s/plat/linux_rtai/bin" % (emcroot)
    print "Building for BDI-4 in", emcroot


    gcode = Extension("gcode", [
            "extensions/gcodemodule.cc"
        ],
        define_macros = [('AXIS_USE_EMC2', 1)],
        include_dirs=[
            os.path.join(emcroot, "src/include"),
        ],
        library_dirs = [
            os.path.join(emcroot, "plat/linux_rtai/lib")
        ],
        extra_link_args = [
            '-DNEW_INTERPRETER', 
            '-Wl,-rpath,%s' % 
            os.path.join(emcroot, "plat/linux_rtai/lib"),
            os.path.join(emcroot, "src", ".tmp", "rs274.o"),
            '-lnml', '-lm', '-lstdc++',
        ]
    )

    emc = Extension("emc", ["extensions/emcmodule.cc"],
        define_macros=[('DEFAULT_NMLFILE',
            '"%s/emc.nml"' % emcroot),
            ('AXIS_USE_EMC2', 1)],
        include_dirs=[
            os.path.join(emcroot, "src/include")
        ],
        library_dirs = [
            os.path.join(emcroot, "plat/linux_rtai/lib")
        ],
        libraries = ["emc", "nml", "m", "stdc++"]
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

    See the README file for more information."""
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

if simple_install:
    ext_modules = []
    try:
        import minigl
    except ImportError:
        ext_modules.append(minigl)
else:
    ext_modules = [emc, togl, gcode, minigl]

class install_data(install_data):
    def run(self):
        self.mkpath(self.install_dir)
        for f in self.data_files:
            dir = convert_path(f[0])
            if not os.path.isabs(dir):
                dir = os.path.join(self.install_dir, dir)
            elif self.root:
                dir = change_root(self.root, dir)
            self.mkpath(dir)

            if f[1] == []:
                # If there are no files listed, the user must be
                # trying to create an empty directory, so add the
                # directory to the list of output files.
                self.outfiles.append(dir)
            else:
                # Copy files, adding them to the list of output files.
                for data in f[1]:
                    if isinstance(data, str):
                        dest = dir
                    else:
                        dest = os.path.join(dir, data[1])
                        data = data[0]
                    dest = convert_path(dest)
                    (out, _) = self.copy_file(data, dest)
                    self.outfiles.append(out)

def lang(f): return os.path.splitext(os.path.basename(f))[0]
i18n = [(os.path.join(LOCALEDIR,lang(f),"LC_MESSAGES"), [(f, "axis.mo")])
            for f in glob("i18n/??.mo") + glob("i18n/??_??.mo")]
print i18n

setup(name=name, version=version,
    description="AXIS front-end for emc",
    author="Jeff Epler", author_email="jepler@unpythonic.net",
    package_dir={'': 'lib', 'rs274' : 'rs274'},
    packages=['', 'rs274'],
    scripts={WINDOWED('axis'): 'scripts/axis.py',
             TERMINAL('emctop'): 'scripts/emctop.py',
             TERMINAL('mdi'): 'scripts/mdi.py'},
    cmdclass = {
        'build_scripts': build_scripts,
        'install_data': install_data},
    data_files = [(os.path.join(SHAREDIR, "tcl"), glob("tcl/*.tcl")),
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
                        "thirdparty/LICENSE-Togl"])] + i18n,
    ext_modules = ext_modules,
    url="http://axis.unpythonic.net/",
    license="GPL",
)

# vim:ts=8:sts=4:et:
