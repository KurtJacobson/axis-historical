from distutils.command.build_py import build_py as _build_py
from distutils import sysconfig
import os
from glob import glob
import yapps

class build_py(_build_py):
    def check_package (self, package, package_dir):

        # Empty dir name means current directory, which we can probably
        # assume exists.  Also, os.path.exists and isdir don't know about
        # my "empty string means current dir" convention, so we have to
        # circumvent them.
        if package_dir != "":
            if not os.path.exists(package_dir):
                raise DistutilsFileError, \
                      "package directory '%s' does not exist" % package_dir
            if not os.path.isdir(package_dir):
                raise DistutilsFileError, \
                      ("supposed package directory '%s' exists, " +
                       "but is not a directory") % package_dir

        # Require __init__.py for all but the "root package"
        if package:
            init_py = os.path.join(package_dir, "__init__.g")
            if os.path.isfile(init_py):
                return init_py
            init_py = os.path.join(package_dir, "__init__.py")
            if os.path.isfile(init_py):
                return init_py
            log.warn(("package init file '%s' not found " +
                      "(or not a regular file)"), init_py)

        # Either not in a package at all (__init__.py not expected), or
        # __init__.py doesn't exist -- so don't return the filename.
        return None

    def find_package_modules (self, package, package_dir):
        modules = _build_py.find_package_modules(self, package, package_dir)
        yapps_module_files = glob(os.path.join(package_dir, "*.g"))
        
        for f in yapps_module_files:
            module = os.path.splitext(os.path.basename(f))[0]
            modules.append((package, module, f))
        return modules

    def build_module(self, module, module_file, package):
        if isinstance(package, str):
            package = package.split(".")
        elif isinstance(package, (list,tuple)):
            raise TypeError, \
                  "'package' must be a string (dot-separated), list, or tuple"
        
        if module_file.endswith(".g"):
            outfile = self.get_module_outfile(self.build_lib, package, module)
            yapps.generate(module_file, outfile)
            self.announce("building %s -> %s" % (module_file, outfile))
        else:
            return _build_py.build_module(self, module, module_file, package)


    def run(self):
        # XXX copy_file by default preserves atime and mtime.  IMHO this is
        # the right thing to do, but perhaps it should be an option -- in
        # particular, a site administrator might want installed files to
        # reflect the time of installation rather than the last
        # modification time before the installed release.

        # XXX copy_file by default preserves mode, which appears to be the
        # wrong thing to do: if a file is read-only in the working
        # directory, we want it to be installed read/write so that the next
        # installation of the same module distribution can overwrite it
        # without problems.  (This might be a Unix-specific issue.)  Thus
        # we turn off 'preserve_mode' when copying to the build directory,
        # since the build directory is supposed to be exactly what the
        # installation will look like (ie. we preserve mode when
        # installing).

        # Dispose of an "unusual" case first: no pure Python modules
        # at all (no problem, just return silently)
        if not self.py_modules and not self.packages:
            return

        if self.py_modules:
            self.build_modules()

        if self.packages:
            self.build_packages()

        self.byte_compile(self.get_outputs(include_bytecode=0))

# vim:ts=8:sts=4:et:
