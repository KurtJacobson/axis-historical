#!/usr/bin/env python

import sys, os
BASE = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), ".."))
sys.path.insert(0, os.path.join(BASE, "lib", "python"))

import gettext
gettext.install("axis", localedir=os.path.join(BASE, "share", "locale"), unicode=True)

import emc, hal, Tkinter, nf, rs274.options

app = Tkinter.Tk(className="AxisToolChanger")
rs274.options.install(app)
nf.start(app); nf.makecommand(app, "_", _)
app.wm_withdraw()

def do_change(n):
    if n:
        message = _("Insert tool %d and click continue when ready") % n
    else:
        message = _("Remove the tool and click continue when ready")
    app.tk.call("nf_dialog", ".tool_change",
        _("Tool change"), message, "info", 0, _("Continue"))
    h.changed = True
    app.update()

h = hal.component("hal_manualtoolchange")
h.newpin("number", hal.HAL_S32, hal.HAL_RD)
h.newpin("change", hal.HAL_BIT, hal.HAL_RD)
h.newpin("changed", hal.HAL_BIT, hal.HAL_WR)
h.ready()

last_change = True
while 1:
    change = h.change
    if change and not h.changed:
        do_change(h.number)
    elif not change:
        h.changed = False
    app.after(100)
