#!/usr/bin/env python2

import emc, sys, time, Tkinter
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
    except emc.error: raise SystemExit
    pos = t.yview()[0]
    t.delete("0.0", "end")
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
        t.insert("end", k, "key", "\t")
        t.insert("end", v, vtag, "\n")
    t.yview_moveto(pos)
    t.after(100, timer)
timer()
t.mainloop()
