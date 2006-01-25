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

__all__ = ['install_data', 'build_scripts', 'WINDOWED', 'TERMINAL']

# Distutils always tries to avoid copying files, and it decides when
# to be lazy by looking at timestamps.  If a developer is switching between two
# different trees (e.g., devel and stable), distutils will leave an unholy mix
# between files from each tree after a new 'setup.py install'.
import distutils.file_util
from distutils.util import convert_path

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
        print "%s %s -> %s" % (action, src, dir)
    else:
        print "%s %s -> %s" % (action, src, dst)

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

# Exhibit 2: There doesn't seem to be a way to install files with a different
# name than they have in the source tree.  Now, if an item to be copied to some
# directory is a 2-tuples, the tuple is (name in tree), (installed name).
# This is critical for correct installation of .mo files.  These are named
# <lang>.mo in the source tree, but always "axis.po" when installed.  (The
# language is determined by the directory where the file is installed)
from distutils.command.install_data import install_data
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


# Exhibit 3: Similar to Exhibit 2.

from distutils.command.build_scripts import build_scripts
from distutils.dep_util import newer
from distutils.util import convert_path
from distutils import sysconfig
import re, os, sys

# check if Python is called on the first line with this expression
first_line_re = re.compile(r'^#!.*python[0-9.]*(\s+.*)?$')
class build_scripts(build_scripts):
    def copy_scripts (self):
        """Copy each script listed in 'self.scripts'; if it's marked as a
        Python script in the Unix way (first line matches 'first_line_re',
        ie. starts with "\#!" and contains "python"), then adjust the first
        line to refer to the current Python interpreter as we copy.
        """
        self.mkpath(self.build_dir)
        scripts = []
        for install_as, script in self.scripts.items():
            adjust = 0
            script = convert_path(script)
            outfile = os.path.join(self.build_dir, install_as)

            if not self.force and not newer(script, outfile):
                self.announce("not copying %s (up-to-date)" % script)
                continue

            # Always open the file, but ignore failures in dry-run mode --
            # that way, we'll get accurate feedback if we can read the
            # script.
            try:
                f = open(script, "r")
            except IOError:
                if not self.dry_run:
                    raise
                f = None
            else:
                first_line = f.readline()
                if not first_line:
                    self.warn("%s is an empty file (skipping)" % script)
                    continue

                match = first_line_re.match(first_line)
                if match:
                    adjust = 1
                    post_interp = match.group(1) or ''

            if adjust:
                self.announce("copying and adjusting %s -> %s" %
                              (script, self.build_dir))
                if not self.dry_run:
                    outf = open(outfile, "w")
                    if not sysconfig.python_build:
                        outf.write("#!%s%s\n" %
                                   (os.path.normpath(sys.executable),
                                    post_interp))
                    else:
                        outf.write("#!%s%s" %
                                   (os.path.join(
                            sysconfig.get_config_var("BINDIR"),
                            "python" + sysconfig.get_config_var("EXE")),
                                    post_interp))
                    outf.writelines(f.readlines())
                    outf.close()
                if f:
                    f.close()
            else:
                f.close()
                self.copy_file(script, outfile)

def WINDOWED(s):
    if os.name == "nt": return "%s.pyw" % s
    return s

def TERMINAL(s):
    if os.name == "nt": return "%s.py" % s
    return s

# vim:sw=4:sts=4:et:
