#!/usr/bin/env python

import emc, sys

if len(sys.argv) > 1:
    emc.emlfile = sys.argv[1]
c = emc.command()
c.mode(emc.MODE_MDI)
s = emc.stat()

try:
    while 1:
        mdi = raw_input("MDI> ")
        if mdi == '':
            s.poll()
            print s.position
        else:
            c.mdi(mdi)
except (SystemExit, EOFError, KeyboardInterrupt): pass

# vim:sw=4:sts=4:et:
