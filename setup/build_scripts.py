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

__all__ = ['build_scripts', 'WINDOWED', 'TERMINAL']

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
