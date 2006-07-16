#!/usr/bin/env python2
#    This is a component of AXIS, a front-end for emc
#    Copyright 2004, 2005, 2006 Jeff Epler <jepler@unpythonic.net>
#                         and Chris Radek <chris@timeguy.com>
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
BASE = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), ".."))
sys.path.insert(0, os.path.join(BASE, "lib", "python"))

import emc, time, Tkinter
if len(sys.argv) > 1 and sys.argv[1] == '-ini':
    ini = emc.ini(sys.argv[2])
    emc.nmlfile = ini.find("EMC", "NML_FILE")
    del sys.argv[1:3]

s = emc.stat()

def show_mcodes(l):
    return " ".join(["M%g" % i for i in l[1:] if i != -1])
def show_gcodes(l):
    return " ".join(["G%g" % (i/10.) for i in l[1:] if i != -1])

maps = {
'motion_mode':{emc.TRAJ_MODE_FREE: 'free', emc.TRAJ_MODE_COORD: 'coord',
                emc.TRAJ_MODE_TELEOP: 'teleop'},
'interp_state':{emc.INTERP_IDLE: 'idle', emc.INTERP_PAUSED: 'paused', 
                emc.INTERP_READING: 'reading', emc.INTERP_WAITING: 'waiting'},
'task_state':  {emc.STATE_ESTOP: 'estop', emc.STATE_ESTOP_RESET: 'estop reset',
                emc.STATE_ON: 'on', emc.STATE_OFF: 'off'},
'task_mode':   {emc.MODE_AUTO: 'auto', emc.MODE_MDI: 'mdi',
                emc.MODE_MANUAL: 'manual'},
'mcodes': show_mcodes, 'gcodes': show_gcodes, 'poll': None, 'tool_table': None,
'axis': None, 'gettaskfile': None, 'ain': None, 'aout': None, 'din': None,
'dout': None
}

root = Tkinter.Tk(className="EmcTop")
root.title("EMC Status")

t = Tkinter.Text()
sb = Tkinter.Scrollbar(command=t.yview)
t.configure(yscrollcommand=sb.set)
t.configure(tabs="150")
t.tag_configure("key", foreground="blue", font="helvetica -12")
t.tag_configure("value", foreground="black", font="fixed")
t.tag_configure("changedvalue", foreground="black", background="red", font="fixed")
t.pack(side="left", expand=1, fill="both")
sb.pack(side="left", expand=0, fill="y")

changetime = {}
oldvalues = {}
def timer():
    try:
        s.poll()
    except emc.error:
	root.destroy()
    pos = t.yview()[0]
    t.delete("0.0", "end")
    first = True
    for k in dir(s):
        if k.startswith("_"): continue
        if maps.has_key(k) and maps[k] == None: continue
        v = getattr(s, k)
        if maps.has_key(k):
            m = maps[k]
            if callable(m):
                v = m(v)
            else:
                v = m.get(v, v)
        if oldvalues.has_key(k):
            changed = oldvalues[k] != v
            if changed: changetime[k] = time.time() + 2
        oldvalues[k] = v
        if changetime.has_key(k) and changetime[k] >= time.time():
            vtag = "changedvalue"
        else:
            vtag = "value"
	if first: first = False
	else: t.insert("end", "\n")
        t.insert("end", k, "key", "\t")
        t.insert("end", v, vtag)
    t.yview_moveto(pos)
    t.after(100, timer)
timer()
t.mainloop()

# vim:sw=4:sts=4:et
