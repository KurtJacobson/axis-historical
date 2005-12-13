#!/usr/bin/env python2
#    This is a component of AXIS, a front-end for emc
#    Copyright 2004, 2005 Jeff Epler <jepler@unpythonic.net> and
#    Chris Radek <chris@timeguy.com>
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


from __future__ import generators

import string
__version__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Jeff Epler <jepler@unpythonic.net>'

import sys, array, time, atexit, tempfile, shutil, os, errno

# This works around a bug in some BLT installations by exporting symbols
# from _tkinter.so's copy of libtcl and libtk to libblt
ldflags = sys.getdlopenflags(); sys.setdlopenflags(0x102)
import _tkinter
sys.setdlopenflags(ldflags)

# Print Tk errors to stdout. python.org/sf/639266
import Tkinter 
OldTk = Tkinter.Tk
class Tk(OldTk):
    def __init__(self, *args, **kw):
        OldTk.__init__(self, *args, **kw)
        self.tk.createcommand('tkerror', self.tkerror)

    def tkerror(self, arg):
        print "TCL error in asynchronous code:"
        print self.tk.call("set", "errorInfo")

Tkinter.Tk = Tk

from Tkinter import *
from minigl import *
from rs274.OpenGLTk import *
from rs274.glcanon import GLCanon
from hershey import Hershey
import rs274.options
root_window = Tkinter.Tk(className="Axis")
rs274.options.install(root_window)
import nf; nf.start(root_window)
import gcode

try:
    root_window.tk.call("proc", "_", "s", "set s")
    nf.source_lib_tcl(root_window,"axis.nf")
    nf.source_lib_tcl(root_window,"axis.tcl")
except TclError:
    print root_window.tk.call("set", "errorInfo")
    raise
program_start_line = 0
program_start_line_last = -1

feedrate_blackout = 0
from math import hypot, atan2, sin, cos, pi, sqrt
from rs274 import ArcsToSegmentsMixin
import _tkinter
import emc

homeicon = array.array('B', 
        [0x2, 0x00,   0x02, 0x00,   0x02, 0x00,   0x0f, 0x80,
        0x1e, 0x40,   0x3e, 0x20,   0x3e, 0x20,   0x3e, 0x20,
        0xff, 0xf8,   0x23, 0xe0,   0x23, 0xe0,   0x23, 0xe0,
        0x13, 0xc0,   0x0f, 0x80,   0x02, 0x00,   0x02, 0x00])

if sys.version_info <= (2,3):
    def enumerate(sequence):
        index = 0
        for item in sequence:
            yield index, item
            index += 1

def install_help(app):
    help1 = [
        ("F1", "Emergency stop"),
        ("F2", "Turn machine on"),
        ("", ""),
        ("X, `", "Activate first axis"),
        ("Y, 1", "Activate second axis"),
        ("Z, 2", "Activate third axis"),
        ("A, 3", "Activate fourth axis"),
        ("   4", "Activate fifth axis"),
        ("   5", "Activate sixth axis"),
        ("I", "Select jog increment"),
        ("C", "Continuous jog"),
        ("Home", "Send active axis home"),
        ("Shift-Home", "Set G54 offset for active axis"),
        ("Left, Right", "Jog first axis"),
        ("Up, Down", "Jog second axis"),
        ("Pg Up, Pg Dn", "Jog third axis"),
        ("[, ]", "Jog fourth axis"),
        ("", ""),
        ("Left Button", "Pan view or select line"),
        ("Shift+Left Button", "Rotate view"),
        ("Right Button", "Zoom view"),
        ("Wheel Button", "Rotate view"),
        ("Rotate Wheel", "Zoom view"),
    ]
    help2 = [
        ("F3", "Manual control"),
        ("F5", "Code entry (MDI)"),
        ("L", "Override Limits"),
        ("", ""),
        ("O", "Open program"),
        ("R", "Run program"),
        ("T", "Step program"),
        ("P", "Pause program"),
        ("S", "Resume program"),
        ("ESC", "Stop program"),
        ("", ""),
        ("F7", "Toggle mist"),
        ("F8", "Toggle flood"),
        ("", ""),
        ("B", "Spindle brake off"),
        ("Shift-B", "Spindle brake on"),
        ("F9", "Turn spindle clockwise"),
        ("F10", "Turn spindle counterclockwise"),
        ("F11", "Turn spindle more slowly"),
        ("F12", "Turn spindle more quickly"),
        ("", ""),
        ("Control-K", "Clear live plot"),
    ]

    assert len(help1) >= len(help2)
    app.tk.call(".keys.text", "configure", "-state", "normal")
    app.tk.call(".keys.text", "delete", "0.0", "end")
    for i in range(len(help1)):
        app.tk.call(".keys.text", "insert", "end",
                    help1[i][0], "key", "\t", "", help1[i][1], "normal")
        if i < len(help2):
            app.tk.call(".keys.text", "insert", "end", "\t")
            app.tk.call(".keys.text", "insert", "end",
                    help2[i][0], "key", "\t", "", help2[i][1], "normal")
        app.tk.call(".keys.text", "insert", "end", "\n")
    app.tk.call(".keys.text", "configure", "-state", "disabled")
    app.tk.call(".keys.text", "configure", "-height", len(help1))
install_help(root_window)

class MyOpengl(Opengl):
    def __init__(self, *args, **kw):
        self.after_id = None
        self.motion_after = None
        self.perspective = False
        Opengl.__init__(self, *args, **kw)
        self.bind('<Button-4>', self.zoomin)
        root_window.bind('<Key-minus>', self.zoomout)
        root_window.bind('<Key-minus>', "+puts <Key>-")
        self.bind('<Button-5>', self.zoomout)
        root_window.bind('<Key-plus>', self.zoomin)
        root_window.bind('<Key-equal>', self.zoomin)
        self.bind('<MouseWheel>', self.zoomwheel)
        self.bind('<Button-1>', self.select_prime, add=True)
        self.bind('<ButtonRelease-1>', self.select_fire, add=True)
        self.bind('<Button1-Motion>', self.select_cancel, add=True)
        self.bind("<Shift-Button-1>", self.StartRotate)
        self.bind("<Shift-B1-Motion>", self.tkRotate)
        self.highlight_line = None
        self.select_event = None
        self.select_buffer_size = 100
        self.select_primed = False
        self.last_position = None
        self.last_homed = None
        self.last_origin = None
        self.g = None
        self.set_eyepoint(5.)

    def select_prime(self, event):
        self.select_primed = event

    def select_cancel(self, event):
        self.select_primed = False

    def select_fire(self, event):
        if self.select_primed: self.queue_select(event)

    def queue_select(self, event):
        self.select_event = event
        self.tkRedraw()

    def deselect(self, event):
        self.set_highlight_line(None)

    def select(self, event):
        if self.g is None: return
        pmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        vport = glGetIntegerv(GL_VIEWPORT)
        gluPickMatrix(event.x, vport[3]-event.y, 5, 5, vport)
        glMultMatrixd(pmatrix)
        glMatrixMode(GL_MODELVIEW)

        while 1:
            glSelectBuffer(self.select_buffer_size)
            glRenderMode(GL_SELECT)
            glInitNames()
            glPushName(0)

            glCallList(select_program)

            try:
                buffer = list(glRenderMode(GL_RENDER))
            except GLerror, detail:
                if detail.errno[0] == GL_STACK_OVERFLOW:
                    self.select_buffer_size *= 2
                    continue
                raise
            break

        buffer.sort()

        if buffer:
            min_depth, max_depth, names = buffer[0]
            self.set_highlight_line(names[0])
        else:
            self.set_highlight_line(None)

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def set_current_line(self, line):
        if line == vars.running_line.get(): return
        t.tag_remove("executing", "0.0", "end")
        if line is not None and line > 0:
            vupdate(vars.running_line, line)
            if vars.highlight_line.get() <= 0:
                t.see("%d.0" % (line+2))
                t.see("%d.0" % line)
            t.tag_add("executing", "%d.0" % line, "%d.end" % line)
        else:
            vupdate(vars.running_line, -1)

    def set_highlight_line(self, line):
        if line == vars.highlight_line.get(): return
        self.highlight_line = line
        t.tag_remove("sel", "0.0", "end")
        if line is not None and line > 0:
            t.see("%d.0" % (line+2))
            t.see("%d.0" % line)
            t.tag_add("sel", "%d.0" % line, "%d.end" % line)
            vupdate(vars.highlight_line, line)
        else:
            vupdate(vars.highlight_line, -1)
        global highlight
        if highlight is not None: glDeleteLists(highlight, 1)
        highlight = glGenLists(1)
        glNewList(highlight, GL_COMPILE)
        if line is not None and self.g is not None:
            x, y, z = self.g.highlight(line)
            self.set_centerpoint(x, y, z)
        elif self.g is not None:
            x = (self.g.min_extents[0] + self.g.max_extents[0])/2
            y = (self.g.min_extents[1] + self.g.max_extents[1])/2
            z = (self.g.min_extents[2] + self.g.max_extents[2])/2
            self.set_centerpoint(x, y, z)
        glEndList()
 
    def zoomin(self, event):
        self.distance = self.distance / 1.25
        self.tkRedraw()

    def zoomout(self, event):
        self.distance = self.distance * 1.25
        self.tkRedraw()

    def zoomwheel(self, event):
        if event.delta > 0: self.zoomin(event)
        else: self.zoomout(event)

    def tkRedraw(self, *dummy):
        if self.after_id:
            # May need to upgrade to an instant redraw
            self.after_cancel(self.after_id)
        self.after_id = self.after_idle(self.actual_tkRedraw)

    def redraw_soon(self, *dummy):
        if self.after_id: return
        self.after_id = self.after(50, self.actual_tkRedraw)

    def tkRedraw_perspective(self, *dummy):
        """Cause the opengl widget to redraw itself."""

        if not self.initialised: return
        self.activate()

        glPushMatrix()                  # Protect our matrix
        self.update_idletasks()
        self.activate()
        w = self.winfo_width()
        h = self.winfo_height()
        glViewport(0, 0, w, h)

        # Clear the background and depth buffer.
        glClearColor(0.,0.,0.,0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fovy, float(w)/float(h), self.near, self.far)

        gluLookAt(0, 0, self.distance,
            0, 0, 0,
            0., 1., 0.)
        glMatrixMode(GL_MODELVIEW)

        # Call objects redraw method.
        self.redraw(self)
        glFlush()                               # Tidy up
        glPopMatrix()                   # Restore the matrix

        self.tk.call(self._w, 'swapbuffers')

    def tkRedraw_ortho(self, *dummy):
        """Cause the opengl widget to redraw itself."""

        if not self.initialised: return
        self.activate()

        glPushMatrix()                  # Protect our matrix
        self.update_idletasks()
        self.activate()
        w = self.winfo_width()
        h = self.winfo_height()
        glViewport(0, 0, w, h)

        # Clear the background and depth buffer.
        glClearColor(0.,0.,0.,0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        ztran = self.distance - self.zcenter
        k = sqrt(abs(ztran or 1))
        l = k * h / w
        glOrtho(-k, k, -l, l, -1000, 1000.)

        gluLookAt(0, 0, self.distance,
            0, 0, 0,
            0., 1., 0.)
        glMatrixMode(GL_MODELVIEW)

        # Call objects redraw method.
        self.redraw(self)
        glFlush()                               # Tidy up
        glPopMatrix()                   # Restore the matrix

        self.tk.call(self._w, 'swapbuffers')

    def tkRotate(self, event):
        Opengl.tkRotate(self, event)
        self.perspective = True
        widgets.view_z.configure(relief="link")
        widgets.view_z2.configure(relief="link")
        widgets.view_x.configure(relief="link")
        widgets.view_y.configure(relief="link")
        widgets.view_p.configure(relief="link")
        
    def actual_tkRedraw(self, *dummy):
        self.after_id = None
        if self.perspective:
            self.tkRedraw_perspective()
        else:
            self.tkRedraw_ortho()

    def set_eyepoint_from_extents(self, e1, e2):
        w = self.winfo_width()
        h = self.winfo_height()

        ztran = max(2.0, e1, e2 * w/h) ** 2
        self.set_eyepoint(ztran - self.zcenter)


def init():
    glDrawBuffer(GL_BACK)
    glDisable(GL_CULL_FACE)
    glLineStipple(2, 0x5555)
    glDisable(GL_LIGHTING)
    glClearColor(0,0,0,0)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

def draw_small_origin():
    r = 2.0/25.4;
    glColor3f(0.0,1.0,1.0)

    glBegin(GL_LINE_STRIP)
    for i in range(37):
        theta = (i*10)*math.pi/180.0
        glVertex3f(r*cos(theta),r*sin(theta),0.0)
    glEnd()
    glBegin(GL_LINE_STRIP)
    for i in range(37):
        theta = (i*10)*math.pi/180.0
        glVertex3f(0.0, r*cos(theta), r*sin(theta))
    glEnd()
    glBegin(GL_LINE_STRIP)
    for i in range(37):
        theta = (i*10)*math.pi/180.0
        glVertex3f(r*cos(theta),0.0, r*sin(theta))
    glEnd()

    glBegin(GL_LINES);
    glVertex3f(-r, -r, 0.0)
    glVertex3f( r,  r, 0.0)
    glVertex3f(-r,  r, 0.0)
    glVertex3f( r, -r, 0.0)

    glVertex3f(-r, 0.0, -r)
    glVertex3f( r, 0.0,  r)
    glVertex3f(-r, 0.0,  r)
    glVertex3f( r, 0.0, -r)

    glVertex3f(0.0, -r, -r)
    glVertex3f(0.0,  r,  r)
    glVertex3f(0.0, -r,  r)
    glVertex3f(0.0,  r, -r)
    glEnd()

def draw_axes():
    x,y,z,p = 0,1,2,3
    if str(widgets.view_x['relief']) == "sunken":
        view = x
    elif str(widgets.view_y['relief']) == "sunken":
        view = y
    elif (str(widgets.view_z['relief']) == "sunken" or
          str(widgets.view_z2['relief']) == "sunken"):
        view = z
    else:
        view = p

    glColor3f(0.2,1.0,0.2)
    glBegin(GL_LINES);
    glVertex3f(1.0,0.0,0.0)
    glVertex3f(0.0,0.0,0.0)
    glEnd();

    if view != x:
        glPushMatrix()
        glTranslatef(1.2, -0.1, 0)
        if view == y:
            glTranslatef(0, 0, -0.1)
            glRotatef(90, 1, 0, 0)
        glScalef(0.2, 0.2, 0.2)
        hershey.plot_string("X", 0.5)
        glPopMatrix()

    glColor3f(1.0,0.2,0.2)
    glBegin(GL_LINES);
    glVertex3f(0.0,0.0,0.0)
    glVertex3f(0.0,1.0,0.0)
    glEnd();

    if view != y:
        glPushMatrix()
        glTranslatef(0, 1.2, 0)
        if view == x:
            glTranslatef(0, 0, -0.1)
            glRotatef(90, 0, 1, 0)
            glRotatef(90, 0, 0, 1)
        glScalef(0.2, 0.2, 0.2)
        hershey.plot_string("Y", 0.5)
        glPopMatrix()

    glColor3f(0.2,0.2,1.0)
    glBegin(GL_LINES);
    glVertex3f(0.0,0.0,0.0)
    glVertex3f(0.0,0.0,1.0)
    glEnd();

    if view != z:
        glPushMatrix()
        glTranslatef(0, 0, 1.2)
        if view == x:
            glRotatef(90, 0, 1, 0)
            glRotatef(90, 0, 0, 1)
        elif view == y or view == p:
            glRotatef(90, 1, 0, 0)
        glScalef(0.2, 0.2, 0.2)
        hershey.plot_string("Z", 0.5)
        glPopMatrix()


def toggle_perspective(e):
    o.perspective = not o.perspective
    o.tkRedraw()

def select_line(event):
    i = t.index("@%d,%d" % (event.x, event.y))
    i = int(i.split('.')[0])
    o.set_highlight_line(i)
    o.tkRedraw()
    return "break"

def select_prev(event):
    if o.highlight_line is None:
        i = o.last_line
    else:
        i = max(1, o.highlight_line - 1)
    o.set_highlight_line(i)
    o.tkRedraw()

def select_next(event):
    if o.highlight_line is None:
        i = 1
    else:
        i = min(o.last_line, o.highlight_line + 1)
    o.set_highlight_line(i)
    o.tkRedraw()

def scroll_up(event):
    t.yview_scroll(-2, "units")

def scroll_down(event):
    t.yview_scroll(2, "units")

select_program = program = highlight = None

def make_cone():
    global cone_program
    cone_program = glGenLists(1)
    q = gluNewQuadric()
    glNewList(cone_program, GL_COMPILE)
    glEnable(GL_LIGHTING)
    glColor3f(.75,.75,.75)
    gluCylinder(q, 0, .1, .25, 32, 1)
    glPushMatrix()
    glTranslatef(0,0,.25)
    gluDisk(q, 0, .1, 32, 1)
    glPopMatrix()
    glDisable(GL_LIGHTING)
    glEndList()
    gluDeleteQuadric(q)

def make_selection_list(g):
    global select_program
    if select_program is None: select_program = glGenLists(1)
    glNewList(select_program, GL_COMPILE)
    g.draw(1)
    glEndList()

def make_main_list(g):
    global program
    if program is None: program = glGenLists(1)
    glNewList(program, GL_COMPILE)
    g.draw(0)
    glEndList()

import array

def vupdate(var, val):
    try:
        if var.get() == val: return
    except ValueError:
        pass
    var.set(val)

def colinear(p1, p2, p3):
    x, y, z = 0, 1, 2
    p = p2[x] - p1[x], p2[y] - p1[y], p2[z] - p1[z]      
    q = p3[x] - p2[x], p3[y] - p2[y], p3[z] - p2[z]     
    dp = sqrt(p[x]**2 + p[y]**2 + p[z]**2)      
    dq = sqrt(q[x]**2 + q[y]**2 + q[z]**2)      
    if dp == 0 or dq == 0:
        return True
    dot = (p[x] * q[x] + p[y] * q[y] + p[z] * q[z]) / dp / dq   
    return abs(1-dot) < 1e-8

class LivePlotter:
    def __init__(self, window):
        self.win = window
        window.live_plot_size = 0
        self.after = None
        self.running = BooleanVar(window)
        self.running.set(False)
        self.data = array.array('f')
        self.start()


    def start(self):
        if self.running.get(): return
        if not os.path.exists(emc.nmlfile):
            return False
        try:
            self.stat = emc.stat()
        except emc.error:
            return False
        self.running.set(True)
        if self.after is None:
            self.update()

    def stop(self):
        if not self.running.get(): return
        if hasattr(self, 'stat'): del self.stat
        if self.after is not None:
            self.win.after_cancel(self.after)
            self.after = None
        self.shutdown()
        self.running.set(True)

    def update(self):
        if not self.running.get():
            return
        try:
            self.stat.poll()
        except emc.error, detail:
            print "error", detail
            del self.stat
            return
        error = e.poll()
        if error: 
            kind, text = error
            if kind in (emc.NML_ERROR, emc.OPERATOR_ERROR):
                root_window.tk.call("nf_dialog", ".error",
                                    "AXIS error", text, "error",0,"OK")
            else: # TEXT, DISPLAY
                # This gives time for the "interpreter is paused" state to
                # reach us.  Typically a message is followed by a pause
                # command, as for a manual tool change.
                for i in range(4):
                    self.stat.poll()
                result = root_window.tk.call("nf_dialog", ".error",
                                    "AXIS error", text, "info", 0, "OK")
        self.after = self.win.after(20, self.update)

        if program_start_line_last == -1 or \
                self.stat.read_line < program_start_line_last:
            self.win.set_current_line(self.stat.read_line)
        else:
            self.win.set_current_line(self.stat.motion_line)

        lu = self.stat.linear_units or 1
        position = [pi / (25.4 * lu) for pi in self.stat.position[:3]]
        p = array.array('f', position)
        if not self.data or p != self.data[-3:]:
            if len(self.data) > 6 and \
                    colinear(self.data[-6:-3], self.data[-3:], p):
                self.data[-3:] = p
            else:
                self.data.extend(p)
            glInterleavedArrays(GL_V3F, 0, self.data.tostring())
            self.win.live_plot_size = len(self.data)/3
            if len(self.data) >= 6:
                glDrawBuffer(GL_FRONT)
                glLineWidth(3)
                glColor3f(1,0,0)
                glBegin(GL_LINES)
                glVertex3f(*self.data[-6:-3])
                glVertex3f(*self.data[-3:])
                glEnd()
                glLineWidth(1)
                glDrawBuffer(GL_BACK)
        if (self.stat.actual_position != o.last_position
                or self.stat.homed != o.last_homed
                or self.stat.origin != o.last_origin):
            o.redraw_soon()
            o.last_homed = self.stat.homed
            o.last_position = self.stat.actual_position
            o.last_origin = self.stat.origin

        vupdate(vars.exec_state, self.stat.exec_state)
        vupdate(vars.interp_state, self.stat.interp_state)
        vupdate(vars.task_mode, self.stat.task_mode)
        vupdate(vars.task_state, self.stat.task_state)
        vupdate(vars.taskfile, self.stat.file)
        vupdate(vars.interp_pause, self.stat.paused)
        vupdate(vars.mist, self.stat.mist)
        vupdate(vars.flood, self.stat.flood)
        vupdate(vars.brake, self.stat.spindle_brake)
        vupdate(vars.spindledir, self.stat.spindle_direction)
        if time.time() > feedrate_blackout:
            vupdate(vars.feedrate, int(100 * self.stat.feedrate + .5))
        vupdate(vars.override_limits, self.stat.axis[0]['override_limits'])
        current_tool = [i for i in self.stat.tool_table 
                            if i[0] == self.stat.tool_in_spindle]
        if self.stat.tool_in_spindle == 0:
            vupdate(vars.tool, "No tool")
        elif current_tool == []:
            vupdate(vars.tool, "Unknown tool %d" % self.stat.tool_in_spindle)
        else:
            vupdate(vars.tool,
                 "Tool %d, offset %g, radius %g" % current_tool[0])
        active_codes = []
        for i in self.stat.gcodes[1:]:
            if i == -1: continue
            if i % 10 == 0:
                active_codes.append("G%d" % (i/10))
            else:
                active_codes.append("G%d.%d" % (i/10, i%10))

        for i in self.stat.mcodes[1:]:
            if i == -1: continue
            active_codes.append("M%d" % i)

        active_codes.append("F%.0f" % self.stat.settings[1])
        active_codes.append("S%.0f" % self.stat.settings[2])

        mid = len(active_codes)/2
        a, b = active_codes[:mid], active_codes[mid:]
        codes = " ".join(a) + "\n" + " ".join(b)
        widgets.code_text.configure(state="normal")
        widgets.code_text.delete("0.0", "end")
        widgets.code_text.insert("end", codes)
        widgets.code_text.configure(state="disabled")

    def clear(self):
        del self.data[:]
        self.win.live_plot_size = 0
        o.redraw_soon()

def running(do_poll=True):
    if do_poll: s.poll()
    return s.task_mode == emc.MODE_AUTO and s.interp_state != emc.INTERP_IDLE

def manual_ok(do_poll=True):
    if do_poll: s.poll()
    if s.task_state != emc.STATE_ON: return False
    return s.interp_state == emc.INTERP_IDLE

def ensure_mode(m):
    s.poll()
    if s.task_mode == m: return True
    if running(do_poll=False): return False
    c.wait_complete()
    c.mode(m)
    c.wait_complete()
    return True

class AxisCanon(GLCanon):
    def __init__(self, text, linecount):
        GLCanon.__init__(self, text)
        self.linecount = linecount
    def next_line(self, st):
        lineno = st.sequence_number + 1
        if lineno % 100 == 0:
            width = int(t.tk.call("winfo", "width", ".info.progress"))
            height = int(t.tk.call("winfo", "height", ".info.progress"))
            t.tk.call(".info.progress", "coords", "1", (0, 0, lineno * width / self.linecount, height))
            t.tk.call("update", "idletasks")
        GLCanon.next_line(self, st)
    def get_tool(self, tool):
        for t in s.tool_table:
            if t[0] == tool:
                return t
        return tool,0.,0.

    def get_external_angular_units(self):
        return s.angular_units or 1

    def get_external_length_units(self):
        return s.linear_units or 1

loaded_file = None
def open_file_guts(f, filtered = False):
    if not filtered:
        global loaded_file
        loaded_file = f
    if program_filter and not filtered:
        tempfile = os.path.join(tempdir, os.path.basename(f))
        result = os.system("%s < %s > %s" % (program_filter, f, tempfile))
        if result:
            root_window.tk.call("nf_dialog", ".error",
                    "Program_filter %r failed" % program_filter,
                    "Exit code %d" % result,
                    "error",0,"OK")
            return
        return open_file_guts(tempfile, True)

    set_first_line(0)
    old_focus = root_window.tk.call("focus", "-lastfor", ".")
    root_window.tk.call("canvas", ".info.progress",
                "-width", 1, "-height", 1,
                "-highlightthickness", 0,
                "-borderwidth", 2, "-relief", "sunken",
                "-cursor", "watch")
    root_window.configure(cursor="watch")
    root_window.tk.call(".menu", "configure", "-cursor", "watch")
    t.configure(cursor="watch")
    root_window.tk.call("bind", ".info.progress", "<Key>", "break")
    root_window.tk.call("pack", ".info.progress", "-side", "left", "-fill", "both", "-expand", "1")
    root_window.tk.call(".info.progress", "create", "rectangle", (-10, -10, -10, -10), "-fill", "blue", "-outline", "blue")
    root_window.tk.call("focus", "-force", ".info.progress")
    root_window.tk.call("grab", ".info.progress")
    root_window.update()
    t0 = time.time()

    try:
        ensure_mode(emc.MODE_AUTO)
        c.reset_interpreter()
        c.program_open(f)
            
        t.configure(state="normal")
        t.tk.call("delete_all", t)
        code = []
        for i, l in enumerate(open(f)):
            l = l.expandtabs().replace("\r", "")
            #t.insert("end", "%6d: " % (i+1), "lineno", l)
            code.extend(["%6d: " % (i+1), "lineno", l, ""])
            if i % 1000 == 0:
                width = int(t.tk.call("winfo", "width", ".info.progress"))
                height = int(t.tk.call("winfo", "height", ".info.progress"))
                p = i/1000 % (width - 25)
                t.tk.call(".info.progress", "coords", "1", (p, 0, p+25, height))
                t.insert("end", *code)
                code = []
                t.tk.call("update", "idletasks")
        if code:
            t.insert("end", *code)
        f = os.path.abspath(f)
        o.g = canon = AxisCanon(widgets.text, i)
        canon.parameter_file = inifile.find("RS274NGC", "PARAMETER_FILE")
        result, seq = gcode.parse(f, canon)
        print "parse result", result
        if result >= rs274.RS274NGC_MIN_ERROR:
            error_str = rs274.errorlist.get(result, "Unknown error %s" % result)
            root_window.tk.call("nf_dialog", ".error",
                    "G-Code error in %s" % os.path.basename(f),
                    "On line %d of %s:\n%s" % (seq+1, f, error_str),
                    "error",0,"OK")

        t.configure(state="disabled")

        make_main_list(canon)
        make_selection_list(canon)

    finally:
        # Before unbusying, I update again, so that any keystroke events
        # that reached the program while it was busy are sent to the
        # label, not to another window in the application.  If this
        # update call is removed, the events are only handled after that
        # widget is destroyed and focus has passed to some other widget,
        # which will handle the keystrokes instead, leading to the
        # R-while-loading bug.
        print "load_time", time.time() - t0
        root_window.update()
        root_window.tk.call("destroy", ".info.progress")
        root_window.tk.call("grab", "release", ".info.progress")
        root_window.tk.call("focus", old_focus)
        root_window.configure(cursor="")
        root_window.tk.call(".menu", "configure", "-cursor", "")
        t.configure(cursor="xterm")
        o.tkRedraw()

vars = nf.Variables(root_window, 
    ("emctop_command", StringVar),
    ("emcini", StringVar),
    ("mdi_command", StringVar),
    ("taskfile", StringVar),
    ("interp_pause", IntVar),
    ("exec_state", IntVar),
    ("task_state", IntVar),
    ("interp_state", IntVar),
    ("task_mode", IntVar),
    ("current_axis", StringVar),
    ("mist", BooleanVar),
    ("flood", BooleanVar),
    ("brake", BooleanVar),
    ("spindledir", IntVar),
    ("running_line", IntVar),
    ("highlight_line", IntVar),
    ("show_program", IntVar),
    ("show_live_plot", IntVar),
    ("show_tool", IntVar),
    ("show_extents", IntVar),
    ("feedrate", IntVar),
    ("tool", IntVar),
    ("active_codes", StringVar),
    ("metric", IntVar),
    ("coord_type", IntVar),
    ("display_type", IntVar),
    ("override_limits", BooleanVar),
)
vars.emctop_command.set(os.path.join(os.path.dirname(sys.argv[0]), "emctop"))
vars.highlight_line.set(-1)
vars.running_line.set(-1)
vars.show_program.set(1)
vars.show_live_plot.set(1)
vars.show_tool.set(1)
vars.show_extents.set(1)

tabs_mdi = str(root_window.tk.call("set", "_tabs_mdi"))
tabs_manual = str(root_window.tk.call("set", "_tabs_manual"))
widgets = nf.Widgets(root_window, 
    ("menu_view", Menu, ".menu.view"),
    ("text", Text, ".t.text"),
    ("preview_frame", Frame, ".preview"),
    ("mdi_history", Text, tabs_mdi + ".history"),
    ("code_text", Text, tabs_mdi + ".gcodes"),

    ("axis_x", Radiobutton, tabs_manual + ".axes.axisx"),
    ("axis_y", Radiobutton, tabs_manual + ".axes.axisy"),
    ("axis_z", Radiobutton, tabs_manual + ".axes.axisz"),
    ("axis_a", Radiobutton, tabs_manual + ".axes.axisa"),
    ("axis_b", Radiobutton, tabs_manual + ".axes.axisb"),
    ("axis_c", Radiobutton, tabs_manual + ".axes.axisc"),

    ("jogspeed", Entry, tabs_manual + ".jogf.jogspeed"),

    ("flood", Checkbutton, tabs_manual + ".flood"),
    ("mist", Checkbutton, tabs_manual + ".mist"),

    ("brake", Checkbutton, tabs_manual + ".spindlef.brake"),

    ("spindle_ccw", Radiobutton, tabs_manual + ".spindlef.ccw"),
    ("spindle_stop", Radiobutton, tabs_manual + ".spindlef.stop"),
    ("spindle_cw", Radiobutton, tabs_manual + ".spindlef.cw"),

    ("view_z", Button, ".toolbar.view_z"),
    ("view_z2", Button, ".toolbar.view_z2"),
    ("view_x", Button, ".toolbar.view_x"),
    ("view_y", Button, ".toolbar.view_y"),
    ("view_p", Button, ".toolbar.view_p"),

    ("feedoverride", Scale, ".feedoverride.foscale"),
)

def activate_axis(i, force=0):
    if not force and not manual_ok(): return
    if i >= axiscount: return
    axis = getattr(widgets, "axis_%s" % "xyzabc"[i])
    axis.focus()
    axis.invoke()

def set_first_line(lineno):
    global program_start_line
    program_start_line = lineno

def jogspeed_continuous():
    widgets.jogspeed.configure(editable=1)
    widgets.jogspeed.delete(0, "end")
    widgets.jogspeed.insert("end", "Continuous")
    widgets.jogspeed.configure(editable=0)

def jogspeed_incremental():
    jogspeed = widgets.jogspeed.get()
    if jogspeed == "Continuous" or jogspeed == "0.0001":
        newjogspeed = 0.1
    else:
        newjogspeed = float(jogspeed) / 10
    widgets.jogspeed.configure(editable=1)
    widgets.jogspeed.delete(0, "end")
    widgets.jogspeed.insert("end", "%s" % newjogspeed)
    widgets.jogspeed.configure(editable=0)

class SelectionHandler:
    def __init__(self, win, **kw):
        self.kw = kw
        self.win = win
        self.win.selection_handle(self.handler, *kw)
        self.value = ""

    def set_value(self, value):
        self.win.selection_own(**self.kw)
        self.value = value

    def handler(self, offset, maxchars):
        offset = int(offset)
        maxchars = int(maxchars)
        return self.value[offset:offset+maxchars]

selection = SelectionHandler(root_window)

class TclCommands(nf.TclCommands):
    def launch_website(event=None):
        import webbrowser
        webbrowser.open("http://axis.unpy.net")

    def set_feedrate(newval):
        global feedrate_blackout
        try:
            value = int(newval)
        except ValueError: return
        value = value / 100.
        c.feedrate(value)
        feedrate_blackout = time.time() + 1

    def copy_line(*args):
        line = -1
        if vars.running_line.get() != -1: line = vars.running_line.get()
        if vars.highlight_line.get() != -1: line = vars.highlight_line.get()
        if line == -1: return
        selection.set_value(t.get("%d.8" % line, "%d.end" % line))

    def set_next_line(*args):
        line = vars.highlight_line.get()
        if line != -1: set_first_line(line)

    def program_verify(*args):
        set_first_line(-1)
        commands.task_run()

    def zoomin(event=None):
        o.zoomin(event)

    def zoomout(event=None):
        o.zoomout(event)

    def set_view_x(event=None):
        widgets.view_z.configure(relief="link")
        widgets.view_z2.configure(relief="link")
        widgets.view_x.configure(relief="sunken")
        widgets.view_y.configure(relief="link")
        widgets.view_p.configure(relief="link")
        o.reset()
        glRotatef(-90, 0, 1, 0)
        glRotatef(-90, 1, 0, 0)
        if o.g:
            mid = [(a+b)/2 for a, b in zip(o.g.max_extents, o.g.min_extents)]
            glTranslatef(-mid[0], -mid[1], -mid[2])
            size = [(a-b) for a, b in zip(o.g.max_extents, o.g.min_extents)]
            o.set_eyepoint_from_extents(size[1], size[2])
        else:
            o.set_eyepoint(5.)
        o.perspective = False
        o.lat = -90
        o.lon = 270
        o.tkRedraw()

    def set_view_y(event=None):
        widgets.view_z.configure(relief="link")
        widgets.view_z2.configure(relief="link")
        widgets.view_x.configure(relief="link")
        widgets.view_y.configure(relief="sunken")
        widgets.view_p.configure(relief="link")
        o.reset()
        glRotatef(-90, 1, 0, 0)
        if o.g:
            mid = [(a+b)/2 for a, b in zip(o.g.max_extents, o.g.min_extents)]
            glTranslatef(-mid[0], -mid[1], -mid[2])
            size = [(a-b) for a, b in zip(o.g.max_extents, o.g.min_extents)]
            o.set_eyepoint_from_extents(size[0], size[2])
        else:
            o.set_eyepoint(5.)
        o.perspective = False
        o.lat = -90
        o.lon = 0
        o.tkRedraw()
        
    def set_view_z(event=None):
        widgets.view_z.configure(relief="sunken")
        widgets.view_z2.configure(relief="link")
        widgets.view_x.configure(relief="link")
        widgets.view_y.configure(relief="link")
        widgets.view_p.configure(relief="link")
        o.reset()
        if o.g:
            mid = [(a+b)/2 for a, b in zip(o.g.max_extents, o.g.min_extents)]
            glTranslatef(-mid[0], -mid[1], -mid[2])
            size = [(a-b) for a, b in zip(o.g.max_extents, o.g.min_extents)]
            o.set_eyepoint_from_extents(size[0], size[1])
        else:
            o.set_eyepoint(5.)
        o.perspective = False
        o.lat = o.lon = 0
        o.tkRedraw()

    def set_view_z2(event=None):
        widgets.view_z.configure(relief="link")
        widgets.view_z2.configure(relief="sunken")
        widgets.view_x.configure(relief="link")
        widgets.view_y.configure(relief="link")
        widgets.view_p.configure(relief="link")
        o.reset()
        glRotatef(-90, 0, 0, 1)
        if o.g:
            mid = [(a+b)/2 for a, b in zip(o.g.max_extents, o.g.min_extents)]
            glTranslatef(-mid[0], -mid[1], -mid[2])
            size = [(a-b) for a, b in zip(o.g.max_extents, o.g.min_extents)]
            o.set_eyepoint_from_extents(size[1], size[0])
        else:
            o.set_eyepoint(5.)
        o.perspective = False
        o.lat = 0
        o.lon = 270
        o.tkRedraw()


    def set_view_p(event=None):
        widgets.view_z.configure(relief="link")
        widgets.view_z2.configure(relief="link")
        widgets.view_x.configure(relief="link")
        widgets.view_y.configure(relief="link")
        widgets.view_p.configure(relief="sunken")
        o.reset()
        o.perspective = True
        if o.g:
            mid = [(a+b)/2 for a, b in zip(o.g.max_extents, o.g.min_extents)]
            glTranslatef(-mid[0], -mid[1], -mid[2])

            size = [(a-b) for a, b in zip(o.g.max_extents, o.g.min_extents)]
            size = sqrt(size[0] **2 + size[1] ** 2 + size[2] ** 2)
            w = o.winfo_width()
            h = o.winfo_height()
            fovx = o.fovy * w / h
            fov = min(fovx, o.fovy)
            o.set_eyepoint(size * 1.1 / 2 / sin ( fov * pi / 180 / 2))
        else:
            o.set_eyepoint(5.)
        o.lat = -60
        o.lon = 335
        glRotateScene(o, 1.0, o.xcenter, o.ycenter, o.zcenter, 0, 0, 0, 0)
        o.tkRedraw()
        
    def estop_clicked(event=None):
        s.poll()
        if s.task_state == emc.STATE_ESTOP:
            c.state(emc.STATE_ESTOP_RESET)
        else:
            c.state(emc.STATE_ESTOP)

    def onoff_clicked(event=None):
        s.poll()
        if s.task_state == emc.STATE_ESTOP_RESET:
            c.state(emc.STATE_ON)
        else:
            c.state(emc.STATE_OFF)

    def open_file(*event):
        if running(): return
        global open_directory
        f = root_window.tk.call("tk_getOpenFile", "-initialdir", open_directory,
            "-defaultextension", ".ngc",
            "-filetypes", "{{rs274ngc files} {.ngc}} {{All files} *}")
        if not f: return
        o.set_highlight_line(None)
        f = str(f)
        open_directory = os.path.dirname(f)
        print "new open_directory", open_directory
        open_file_guts(f)
        if str(widgets.view_x['relief']) == "sunken":
            commands.set_view_x()
        elif str(widgets.view_y['relief']) == "sunken":
            commands.set_view_y()
        elif str(widgets.view_z['relief']) == "sunken":
            commands.set_view_z()
        elif  str(widgets.view_z2['relief']) == "sunken":
            commands.set_view_z2()
        else:
            commands.set_view_p()
        x = (o.g.min_extents[0] + o.g.max_extents[0])/2
        y = (o.g.min_extents[1] + o.g.max_extents[1])/2
        z = (o.g.min_extents[2] + o.g.max_extents[2])/2
        o.set_centerpoint(x, y, z)


    def reload_file(*event):
        if running(): return
        s.poll()
        if not loaded_file: return
        o.set_highlight_line(None)
        open_file_guts(loaded_file)

    def task_run(*event):
        global program_start_line, program_start_line_last
        program_start_line_last = program_start_line;
        ensure_mode(emc.MODE_AUTO)
        c.auto(emc.AUTO_RUN, program_start_line)
        program_start_line = 0

    def task_step(*event):
        ensure_mode(emc.MODE_AUTO)
        c.auto(emc.AUTO_STEP)

    def task_pause(*event):
        ensure_mode(emc.MODE_AUTO)
        c.auto(emc.AUTO_PAUSE)

    def task_resume(*event):
        ensure_mode(emc.MODE_AUTO)
        c.auto(emc.AUTO_RESUME)

    def task_pauseresume(*event):
        ensure_mode(emc.MODE_AUTO)
        s.poll()
        if s.interp_state == emc.INTERP_PAUSED:
            c.auto(emc.AUTO_RESUME)
        else:
            c.auto(emc.AUTO_PAUSE)

    def task_stop(*event):
        c.abort()

    def send_mdi(*event):
        command = vars.mdi_command.get()
        vars.mdi_command.set("")
        ensure_mode(emc.MODE_MDI)
        widgets.mdi_history.configure(state="normal")
        widgets.mdi_history.see("end")
        widgets.mdi_history.insert("end", "%s\n" % command)
        widgets.mdi_history.configure(state="disabled")
        c.mdi(command)
        o.tkRedraw()

    def redraw(*ignored):
        o.tkRedraw()

    def clear_live_plot(*ignored):
        live_plotter.clear()

    # The next three don't have 'manual_ok' because that's done in jog_on /
    # jog_off
    def jog_plus(event=None):
        jog_on(vars.current_axis.get(), jog_speed)
    def jog_minus(event=None):
        jog_on(vars.current_axis.get(), -jog_speed)
    def jog_stop(event=None):
        jog_off(vars.current_axis.get())

    def home_axis(event=None):
        if not manual_ok(): return
        ensure_mode(emc.MODE_MANUAL)
        c.home("xyzabc".index(vars.current_axis.get()))
    def set_axis_offset(event=None):
        if not manual_ok(): return
        ensure_mode(emc.MODE_MDI)
        offset_axis = "xyzabc".index(vars.current_axis.get())
        s.poll()
        lu = s.linear_units or 1
        position = s.position[offset_axis] / (25.4 * lu)
        if 210 in s.gcodes:
            position *= 25.4
        offset_command = "g10 L2 p1 %c%9.4f\n" % (vars.current_axis.get(), position)
        c.mdi(offset_command)
        ensure_mode(emc.MODE_MANUAL)
        s.poll()
        o.tkRedraw()
        commands.reload_file()
    def brake(event=None):
        if not manual_ok(): return
        ensure_mode(emc.MODE_MANUAL)
        c.brake(vars.brake.get())
    def flood(event=None):
        if not manual_ok(): return
        ensure_mode(emc.MODE_MANUAL)
        c.flood(vars.flood.get())
    def mist(event=None):
        if not manual_ok(): return
        ensure_mode(emc.MODE_MANUAL)
        c.mist(vars.mist.get())
    def spindle(event=None):
        if not manual_ok(): return
        ensure_mode(emc.MODE_MANUAL)
        c.spindle(vars.spindledir.get())
    def spindle_increase(event=None):
        if not manual_ok(): return
        ensure_mode(emc.MODE_MANUAL)
        c.spindle(emc.SPINDLE_INCREASE)
    def spindle_decrease(event=None):
        if not manual_ok(): return
        ensure_mode(emc.MODE_MANUAL)
        c.spindle(emc.SPINDLE_DECREASE)
    def spindle_constant(event=None):
        if not manual_ok(): return
        ensure_mode(emc.MODE_MANUAL)
        c.spindle(emc.SPINDLE_CONSTANT)
    def set_first_line(lineno):
        if not manual_ok(): return
        set_first_line(lineno)

    def mist_toggle(*args):
        if not manual_ok(): return
        s.poll()
        c.mist(not s.mist)
    def flood_toggle(*args):
        if not manual_ok(): return
        s.poll()
        c.flood(not s.flood)

    def spindle_forward_toggle(*args):
        if not manual_ok(): return
        s.poll()
        if s.spindle_direction == 0:
            c.spindle(1)
        else:
            c.spindle(0)

    def spindle_backward_toggle(*args):
        if not manual_ok(): return "break"
        s.poll()
        if s.spindle_direction == 0:
            c.spindle(-1)
        else:
            c.spindle(0)
        return "break" # bound to F10, don't activate menu

    def brake_on(*args):
        if not manual_ok(): return
        c.brake(1)
    def brake_off(*args):
        if not manual_ok(): return
        c.brake(0)

    def toggle_display_type(*args):
        vars.display_type.set(not vars.display_type.get())
        o.tkRedraw()

    def toggle_coord_type(*args):
        vars.coord_type.set(not vars.coord_type.get())
        o.tkRedraw()

    def toggle_override_limits(*args):
        s.poll()
        if s.interp_state != emc.INTERP_IDLE: return
        if s.axis[0]['override_limits']:
            ensure_mode(emc.MODE_AUTO)
        else:
            ensure_mode(emc.MODE_MANUAL)
            c.override_limits()
            c.wait_complete()

commands = TclCommands(root_window)
root_window.bind("<Escape>", commands.task_stop)
root_window.bind("l", commands.toggle_override_limits)
root_window.bind("o", commands.open_file)
root_window.bind("s", commands.task_resume)
root_window.bind("t", commands.task_step)
root_window.bind("p", commands.task_pause)
root_window.bind("<Alt-p>", "#nothing")
root_window.bind("r", commands.task_run)
root_window.bind("<Control-r>", commands.reload_file)
root_window.bind("<Key-F1>", commands.estop_clicked)
root_window.bind("<Key-F2>", commands.onoff_clicked)
root_window.bind("<Key-F7>", commands.mist_toggle)
root_window.bind("<Key-F8>", commands.flood_toggle)
root_window.bind("<Key-F9>", commands.spindle_forward_toggle)
root_window.bind("<Key-F10>", commands.spindle_backward_toggle)
root_window.bind("<Key-F11>", commands.spindle_decrease)
root_window.bind("<Key-F12>", commands.spindle_increase)
root_window.bind("B", commands.brake_on)
root_window.bind("b", commands.brake_off)
root_window.bind("<Control-k>", commands.clear_live_plot)
root_window.bind("x", lambda event: activate_axis(0))
root_window.bind("y", lambda event: activate_axis(1))
root_window.bind("z", lambda event: activate_axis(2))
root_window.bind("a", lambda event: activate_axis(3))
root_window.bind("`", lambda event: activate_axis(0))
root_window.bind("1", lambda event: activate_axis(1))
root_window.bind("2", lambda event: activate_axis(2))
root_window.bind("3", lambda event: activate_axis(3))
root_window.bind("4", lambda event: activate_axis(4))
root_window.bind("5", lambda event: activate_axis(5))
root_window.bind("c", lambda event: jogspeed_continuous())
root_window.bind("i", lambda event: jogspeed_incremental())
root_window.bind("@", commands.toggle_display_type)
root_window.bind("#", commands.toggle_coord_type)


# c: continuous
# i: incremental
root_window.bind("<Home>", commands.home_axis)
root_window.bind("<Shift-Home>", commands.set_axis_offset)
widgets.mdi_history.bind("<Configure>", "%W see {end - 1 lines}")

def jog(*args):
    if not manual_ok(): return
    ensure_mode(emc.MODE_MANUAL)
    c.jog(*args)

# XXX correct for machines with more than six axes
jog_after = [None] * 6
jog_cont  = [False] * 6
jogging   = [False] * 6
def jog_on(a, b):
    if not manual_ok(): return
    if isinstance(a, (str, unicode)):
        a = "xyzabc".index(a)
    if jog_after[a]:
        root_window.after_cancel(jog_after[a])
        jog_after[a] = None
        return
    jogspeed = widgets.jogspeed.get()
    if jogspeed != "Continuous":
        s.poll()
        if s.state != 1: return
        jogspeed = float(jogspeed)
        jog(emc.JOG_INCREMENT, a, b, jogspeed)
        jog_cont[a] = False
    else:
        jog(emc.JOG_CONTINUOUS, a, b)
        jog_cont[a] = True
        jogging[a] = True

def jog_off(a):
    if isinstance(a, (str, unicode)):
        a = "xyzabc".index(a)
    if jog_after[a]: return
    jog_after[a] = root_window.after_idle(lambda: jog_off_actual(a))

def jog_off_actual(a):
    if not manual_ok(): return
    activate_axis(a)
    jog_after[a] = None
    if jog_cont[a]:
        jogging[a] = False
        jog(emc.JOG_STOP, a)

def jog_off_all():
    for i in range(6):
        if jogging[i]:
            jog_off_actual(i)

def bind_axis(a, b, d):
    root_window.bind("<KeyPress-%s>" % a, lambda e: jog_on(d,-jog_speed))
    root_window.bind("<KeyPress-%s>" % b, lambda e: jog_on(d, jog_speed))
    root_window.bind("<KeyRelease-%s>" % a, lambda e: jog_off(d))
    root_window.bind("<KeyRelease-%s>" % b, lambda e: jog_off(d))

root_window.bind("<FocusOut>", lambda e: str(e.widget) == "." and jog_off_all())
bind_axis("Left", "Right", 0)
bind_axis("Down", "Up", 1)
bind_axis("Next", "Prior", 2)
bind_axis("KP_Left", "KP_Right", 0)
bind_axis("KP_Down", "KP_Up", 1)
bind_axis("KP_Next", "KP_Prior", 2)
bind_axis("bracketleft", "bracketright", 3)

def set_tabs(e):
    t.configure(tabs="%d right" % (e.width - 2))

import sys, getopt, _tkinter
axiscount = 3
axisnames = "X Y Z".split()

open_directory = "programs"

if len(sys.argv) > 1 and sys.argv[1] == '-ini':
    import ConfigParser
    inifile = emc.ini(sys.argv[2])
    vars.emcini.set(sys.argv[2])
    axiscount = int(inifile.find("TRAJ", "AXES"))
    axisnames = inifile.find("TRAJ", "COORDINATES").split()
    open_directory = inifile.find("DISPLAY", "PROGRAM_PREFIX")
    program_filter = inifile.find("EMC", "PROGRAM_FILTER")
    max_feed_override = float(inifile.find("DISPLAY", "MAX_FEED_OVERRIDE"))
    max_feed_override = int(max_feed_override * 100 + 0.5)
    jog_speed = float(inifile.find("TRAJ", "DEFAULT_VELOCITY"))
    widgets.feedoverride.configure(to=max_feed_override)
    emc.nmlfile = inifile.find("EMC", "NML_FILE")
    vars.coord_type.set(inifile.find("DISPLAY", "POSITION_OFFSET") == "RELATIVE")
    vars.display_type.set(inifile.find("DISPLAY", "POSITION_FEEDBACK") == "COMMANDED")
    coordinate_display = inifile.find("DISPLAY", "POSITION_UNITS")
    if coordinate_display:
        if coordinate_display.lower() in ("mm", "metric"): vars.metric.set(1)
        else: vars.metric.set(0)
    else:
        lu = float(inifile.find("TRAJ", "LINEAR_UNITS"))
        if lu in [.001, .01, .1, 1, 10]: vars.metric.set(1)
        else: vars.metric.set(0)
    del sys.argv[1:3]
else:
    widgets.menu_view.entryconfigure("Show EMC Status", state="disabled")

opts, args = getopt.getopt(sys.argv[1:], 'd:')
for i in range(len(axisnames), 6):
    c = getattr(widgets, "axis_%s" % ("xyzabc"[i]))
    c.grid_forget()
s = emc.stat(); s.poll()
c = emc.command()
e = emc.error_channel()

widgets.preview_frame.pack_propagate(0)
o = MyOpengl(widgets.preview_frame, width=400, height=300, double=1, depth=1)
o.last_line = 1
o.pack(fill="both", expand=1)

root_window.bind("<Key-F3>", ".tabs raise manual")
root_window.bind("<Key-F5>", ".tabs raise mdi")

init()

t = widgets.text
t.bind("<Configure>", set_tabs)
t.tag_configure("lineno", foreground="#808080")
t.tag_configure("executing", background="#804040")
t.tag_configure("state", foreground="#408040")
if args:
    for i, l in enumerate(open(args[0])):
        l = l.expandtabs().replace("\r", "")
        t.insert("end", "%6d: " % (i+1), "lineno", l)
t.bind("<Button-1>", select_line)
t.bind("<B1-Motion>", lambda e: "break")
t.bind("<B1-Leave>", lambda e: "break")
t.bind("<Button-4>", scroll_up)
t.bind("<Button-5>", scroll_down)
t.configure(state="disabled")
activate_axis(0, True)

make_cone()

# Find font for coordinate readout and get metrics
coordinate_font = o.option_get("font", "Font") or "9x15"
coordinate_font_metrics = o.tk.call("font", "metrics", coordinate_font).split()
linespace_index = coordinate_font_metrics.index("-linespace")
coordinate_linespace = int(coordinate_font_metrics[linespace_index+1])

fontbase = int(o.tk.call(o._w, "loadbitmapfont", coordinate_font))
live_plotter = LivePlotter(o)
hershey = Hershey()

def redraw(self):
    if self.select_event:
        self.select(self.select_event)
        self.select_event = None

    glDisable(GL_LIGHTING)
    glMatrixMode(GL_MODELVIEW)


    if vars.show_program.get() and program is not None:
        glCallList(program)
        if highlight is not None: glCallList(highlight)

        if vars.show_extents.get():
            # Dimensions
            x,y,z,p = 0,1,2,3
            if str(widgets.view_x['relief']) == "sunken":
                view = x
            elif str(widgets.view_y['relief']) == "sunken":
                view = y
            elif (str(widgets.view_z['relief']) == "sunken" or
                  str(widgets.view_z2['relief']) == "sunken"):
                view = z
            else:
                view = p

            g = self.g

            dimscale = vars.metric.get() and 25.4 or 1.0
            fmt = vars.metric.get() and "%.1f" or "%.2f"

            pullback = max(g.max_extents[x] - g.min_extents[x],
                           g.max_extents[y] - g.min_extents[y],
                           g.max_extents[z] - g.min_extents[z],
                           2 ) * .1

            dashwidth = pullback/4
            charsize = dashwidth * 1.5
            halfchar = charsize * .5

            if view == z or view == p:
                z_pos = g.min_extents[z]
                zdashwidth = 0
            else:
                z_pos = g.min_extents[z] - pullback
                zdashwidth = dashwidth
            # x dimension

            glColor3f(1.0, 0.51, 0.53)

            glBegin(GL_LINES)
            if view != x and g.max_extents[x] > g.min_extents[x]:
                y_pos = g.min_extents[y] - pullback;
                glVertex3f(g.min_extents[x], y_pos, z_pos)
                glVertex3f(g.max_extents[x], y_pos, z_pos)

                glVertex3f(g.min_extents[x], y_pos - dashwidth, z_pos - zdashwidth)
                glVertex3f(g.min_extents[x], y_pos + dashwidth, z_pos + zdashwidth)

                glVertex3f(g.max_extents[x], y_pos - dashwidth, z_pos - zdashwidth)
                glVertex3f(g.max_extents[x], y_pos + dashwidth, z_pos + zdashwidth)

            # y dimension
            if view != y and g.max_extents[y] > g.min_extents[y]:
                x_pos = g.min_extents[x] - pullback;
                glVertex3f(x_pos, g.min_extents[y], z_pos)
                glVertex3f(x_pos, g.max_extents[y], z_pos)

                glVertex3f(x_pos - dashwidth, g.min_extents[y], z_pos - zdashwidth)
                glVertex3f(x_pos + dashwidth, g.min_extents[y], z_pos + zdashwidth)
                                                                                  
                glVertex3f(x_pos - dashwidth, g.max_extents[y], z_pos - zdashwidth)
                glVertex3f(x_pos + dashwidth, g.max_extents[y], z_pos + zdashwidth)

            # z dimension
            if view != z and g.max_extents[z] > g.min_extents[z]:
                x_pos = g.min_extents[x] - pullback;
                y_pos = g.min_extents[y] - pullback;
                glVertex3f(x_pos, y_pos, g.min_extents[z]);
                glVertex3f(x_pos, y_pos, g.max_extents[z]);

                glVertex3f(x_pos - dashwidth, y_pos - zdashwidth, g.min_extents[z])
                glVertex3f(x_pos + dashwidth, y_pos + zdashwidth, g.min_extents[z])

                glVertex3f(x_pos - dashwidth, y_pos - zdashwidth, g.max_extents[z])
                glVertex3f(x_pos + dashwidth, y_pos + zdashwidth, g.max_extents[z])

            glEnd()

            # Labels
            if vars.coord_type.get():
                offset = s.origin
            else:
                offset = 0, 0, 0
            if view != z and g.max_extents[z] > g.min_extents[z]:
                if view == x:
                    x_pos = g.min_extents[x] - pullback;
                    y_pos = g.min_extents[y] - 6.0*dashwidth;
                else:
                    x_pos = g.min_extents[x] - 6.0*dashwidth;
                    y_pos = g.min_extents[y] - pullback;

                glPushMatrix()
                f = fmt % ((g.min_extents[z]-offset[z]) * dimscale)
                glTranslatef(x_pos, y_pos, g.min_extents[z] - halfchar)
                glScalef(charsize, charsize, charsize)
                glRotatef(-90, 0, 1, 0)
                glRotatef(-90, 0, 0, 1)
                if view != x:
                    glRotatef(-90, 0, 1, 0)
                hershey.plot_string(f, 0)
                glPopMatrix()

                glPushMatrix()
                f = fmt % ((g.max_extents[z]-offset[z]) * dimscale)
                glTranslatef(x_pos, y_pos, g.max_extents[z] - halfchar)
                glScalef(charsize, charsize, charsize)
                glRotatef(-90, 0, 1, 0)
                glRotatef(-90, 0, 0, 1)
                if view != x:
                    glRotatef(-90, 0, 1, 0)
                hershey.plot_string(f, 0)
                glPopMatrix()

                glPushMatrix()
                f = fmt % ((g.max_extents[z] - g.min_extents[z]) * dimscale)
                glTranslatef(x_pos, y_pos, (g.max_extents[z] + g.min_extents[z])/2)
                glScalef(charsize, charsize, charsize)
                if view != x:
                    glRotatef(-90, 0, 0, 1)
                glRotatef(-90, 0, 1, 0)
                hershey.plot_string(f, .5)
                glPopMatrix()

            if view != y and g.max_extents[y] > g.min_extents[y]:
                x_pos = g.min_extents[x] - 6.0*dashwidth;

                glPushMatrix()
                f = fmt % ((g.min_extents[y] - offset[y]) * dimscale)
                glTranslatef(x_pos, g.min_extents[y] + halfchar, z_pos)
                glRotatef(-90, 0, 0, 1)
                glRotatef(-90, 0, 0, 1)
                if view == x:
                    glRotatef(90, 0, 1, 0)
                    glTranslatef(dashwidth*1.5, 0, 0)
                glScalef(charsize, charsize, charsize)
                hershey.plot_string(f, 0)
                glPopMatrix()

                glPushMatrix()
                f = fmt % ((g.max_extents[y] - offset[y]) * dimscale)
                glTranslatef(x_pos, g.max_extents[y] + halfchar, z_pos)
                glRotatef(-90, 0, 0, 1)
                glRotatef(-90, 0, 0, 1)
                if view == x:
                    glRotatef(90, 0, 1, 0)
                    glTranslatef(dashwidth*1.5, 0, 0)
                glScalef(charsize, charsize, charsize)
                hershey.plot_string(f, 0)
                glPopMatrix()

                glPushMatrix()
                f = fmt % ((g.max_extents[y] - g.min_extents[y]) * dimscale)
                
                glTranslatef(x_pos, (g.max_extents[y] + g.min_extents[y])/2,
                            z_pos)
                glRotatef(-90, 0, 0, 1)
                if view == x:
                    glRotatef(-90, 1, 0, 0)
                    glTranslatef(0, halfchar, 0)
                glScalef(charsize, charsize, charsize)
                hershey.plot_string(f, .5)
                glPopMatrix()

            if view != x and g.max_extents[x] > g.min_extents[x]:
                y_pos = g.min_extents[y] - 6.0*dashwidth;

                glPushMatrix()
                f = fmt % ((g.min_extents[x] - offset[x]) * dimscale)
                glTranslatef(g.min_extents[x] - halfchar, y_pos, z_pos)
                glRotatef(-90, 0, 0, 1)
                if view == y:
                    glRotatef(90, 0, 1, 0)
                    glTranslatef(dashwidth*1.5, 0, 0)
                glScalef(charsize, charsize, charsize)
                hershey.plot_string(f, 0)
                glPopMatrix()

                glPushMatrix()
                f = fmt % ((g.max_extents[x] - offset[x]) * dimscale)
                glTranslatef(g.max_extents[x] - halfchar, y_pos, z_pos)
                glRotatef(-90, 0, 0, 1)
                if view == y:
                    glRotatef(90, 0, 1, 0)
                    glTranslatef(dashwidth*1.5, 0, 0)
                glScalef(charsize, charsize, charsize)
                hershey.plot_string(f, 0)
                glPopMatrix()

                glPushMatrix()
                f = fmt % ((g.max_extents[x] - g.min_extents[x]) * dimscale)
                
                glTranslatef((g.max_extents[x] + g.min_extents[x])/2, y_pos,
                            z_pos)
                if view == y:
                    glRotatef(-90, 1, 0, 0)
                    glTranslatef(0, halfchar, 0)
                glScalef(charsize, charsize, charsize)
                hershey.plot_string(f, .5)
                glPopMatrix()

    if vars.show_live_plot.get():
        glColor3f(1,0,0)
        glDepthFunc(GL_ALWAYS)
        glLineWidth(3)
        glDrawArrays(GL_LINE_STRIP, 0, o.live_plot_size)
        glLineWidth(1)
        glDepthFunc(GL_LESS);
        if live_plotter.running.get() and live_plotter.data and vars.show_tool.get():
            if program is not None:
                g = self.g
                x,y,z = 0,1,2
                cone_scale = max(g.max_extents[x] - g.min_extents[x],
                               g.max_extents[y] - g.min_extents[y],
                               g.max_extents[z] - g.min_extents[z],
                               2 ) * .5
            else:
                cone_scale = 1
            pos = live_plotter.data[-3:]
            glPushMatrix()
            glTranslatef(*pos)
            glScalef(cone_scale, cone_scale, cone_scale)
            glCallList(cone_program)
            glPopMatrix()
    if vars.show_live_plot.get() or vars.show_program.get():
        s.poll()
        glPushMatrix()

        lu = (s.linear_units or 1)*25.4
        if vars.coord_type.get() and (s.origin[0] or s.origin[1] or 
                                      s.origin[2]):
            draw_small_origin()
            glTranslatef(s.origin[0]/lu, s.origin[1]/lu, s.origin[2]/lu)
            draw_axes()
        else:
            draw_axes()
        glPopMatrix()


    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    ypos = self.winfo_height()
    glOrtho(0.0, self.winfo_width(), 0.0, ypos, -1.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    s.poll()

    if vars.display_type.get():
        positions = s.position
    else:
        positions = s.actual_position

    if vars.coord_type.get():
        positions = [(i-j) for i, j in zip(positions, s.origin)]

    lu = s.linear_units or 1    
    # XXX: assumes all axes are linear, which is wrong
    positions = [pi / (25.4 * lu) for pi in positions]


    if vars.metric.get():
        positions = ["%c:% 9.2f" % i for i in 
                zip(axisnames, map(lambda p: p*25.4, positions))]
    else:
        positions = ["%c:% 9.4f" % i for i in zip(axisnames, positions)]

    maxlen = max([len(p) for p in positions])
    pixel_width = max([int(o.tk.call("font", "measure", coordinate_font, p))
                    for p in positions])
    glDepthFunc(GL_ALWAYS)
    glDepthMask(GL_FALSE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0,0,0,.7)
    glBegin(GL_QUADS)
    glVertex3f(0, ypos, 1)
    glVertex3f(pixel_width+30, ypos, 1)
    glVertex3f(pixel_width+30, ypos - 20 - coordinate_linespace*axiscount, 1)
    glVertex3f(0, ypos - 20 - coordinate_linespace*axiscount, 1)
    glEnd()
    glDisable(GL_BLEND)

    maxlen = 0
    ypos -= coordinate_linespace+5
    i=0
    glColor3f(1,1,1)
    for string in positions:
        maxlen = max(maxlen, len(string))
        if s.homed[i]:
            glRasterPos2i(6, ypos)
            glBitmap(13, 16, 0, 3, 17, 0, homeicon)
        glRasterPos2i(23, ypos)
        for char in string:
            glCallList(fontbase + ord(char))
        ypos -= coordinate_linespace
        i = i + 1
    glDepthFunc(GL_LESS)
    glDepthMask(GL_TRUE)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)



o.redraw = redraw

def mkdtemp():
    try:
        return tempfile.mkdtemp()
    except AttributeError:
        while 1:
            t = tempfile.mktemp()
            try:
                os.mkdir(t)
                return t
            except os.error, detail:
                if detail.errno != errno.EEXIST: raise
                pass

def remove_tempdir(t):
    shutil.rmtree(t)
tempdir = mkdtemp()
atexit.register(remove_tempdir, tempdir)

code = []
if args:
    open_file_guts(args[0])
elif os.environ.has_key("AXIS_OPEN_FILE"):
    open_file_guts(os.environ["AXIS_OPEN_FILE"])
commands.set_view_z()
if o.g:
    x = (o.g.min_extents[0] + o.g.max_extents[0])/2
    y = (o.g.min_extents[1] + o.g.max_extents[1])/2
    z = (o.g.min_extents[2] + o.g.max_extents[2])/2
    o.set_centerpoint(x, y, z)
o.mainloop()

# vim:sw=4:sts=4:et:
