#!/usr/bin/env python2
#    This is a component of AXIS, a front-end for emc
#    Copyright 2004 Jeff Epler <jepler@unpythonic.net>
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

import sys, array, time
ldflags = sys.getdlopenflags(); sys.setdlopenflags(0x102)
import _tkinter
sys.setdlopenflags(ldflags)

from Tkinter import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.Tk import *
from OpenGL.Tk import _default_root as root_window
from _glfixes import glInterleavedArrays
from rs274.glcanon import GLCanon
import rs274.options
rs274.options.install(root_window)
import nf; nf.start(root_window)

try:
    nf.source_lib_tcl(root_window,"axis.nf")
    nf.source_lib_tcl(root_window,"axis.tcl")
except TclError:
    print root_window.tk.call("set", "errorInfo")
    raise
program_start_line = 0
program_start_line_last = -1

from math import hypot, atan2, sin, cos, pi, sqrt
from rs274 import execute_code, ArcsToSegmentsMixin, parse_lines
import _tkinter
import emc

homeicon = array.array('B', 
        [0x2, 0x00,   0x02, 0x00,   0x02, 0x00,   0x0f, 0x80,
        0x1e, 0x40,   0x3e, 0x20,   0x3e, 0x20,   0x3e, 0x20,
        0xff, 0xf8,   0x23, 0xe0,   0x23, 0xe0,   0x23, 0xe0,
        0x13, 0xc0,   0x0f, 0x80,   0x02, 0x00,   0x02, 0x00])

def makecommand(f): nf.makecommand(root_window, f.__name__, f)

GL_ALIASED_LINE_WIDTH_RANGE = 0x846E
GL_SMOOTH_LINE_WIDTH_RANGE = 0x0B22
GL_SMOOTH_LINE_WIDTH_GRANULARITY = 0x0B23

if sys.version_info <= (2,3):
    def enumerate(sequence):
        index = 0
        for item in sequence:
            yield index, item
            index += 1

class MyOpengl(Opengl):
    def __init__(self, *args, **kw):
        self.after_id = None
        self.motion_after = None
        self.perspective = False
        Opengl.__init__(self, *args, **kw)
        self.bind('<Button-4>', self.zoomout)
        root_window.bind('<Key>-', self.zoomout)
        self.bind('<Button-5>', self.zoomin)
        root_window.bind('<Key>+', self.zoomin)
        root_window.bind('<Key>=', self.zoomin)
        self.bind('<MouseWheel>', self.zoomwheel)
        self.bind('<Button-1>', self.select_prime, add=True)
        self.bind('<ButtonRelease-1>', self.select_fire, add=True)
        self.bind('<Button1-Motion>', self.select_cancel, add=True)
        self.bind('<Button-2>', self.mouse_rotate_view, add=True)
        self.highlight_line = None
        self.select_event = None
        self.select_buffer_size = 100
        self.select_primed = False
        self.g = None

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

            self.g.draw()

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
        t.tag_remove("executing", "0.0", "end")
        if line is not None:
            vupdate(vars.running_line, line)
            if self.highlight_line is None:
                t.see("%d.0" % (line+2))
                t.see("%d.0" % line)
            t.tag_add("executing", "%d.0" % line, "%d.end" % line)
        else:
            vupdate(vars.running_line, -1)

    def set_highlight_line(self, line):
        l = self.highlight_line = line
        t.tag_remove("sel", "0.0", "end")
        if line is not None:
            t.see("%d.0" % (l+2))
            t.see("%d.0" % l)
            t.tag_add("sel", "%d.0" % l, "%d.end" % l)
            vupdate(vars.highlight_line, line)
        else:
            vupdate(vars.highlight_line, -1)
        global highlight
        if highlight is not None: glDeleteLists(highlight, 1)
        highlight = glGenLists(1)
        glNewList(highlight, GL_COMPILE)
        if line is not None and self.g is not None:
            self.g.highlight(line)
        glEndList()
 
    def zoomin(self, event):
        self.distance = self.distance / 1.25
        self.tkRedraw()

    def zoomout(self, event):
        self.distance = self.distance * 1.25
        self.tkRedraw()

    def zoomwheel(self, event):
        if event.delta < 0: self.zoomin(event)
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

        gluLookAt(self.xcenter, self.ycenter, self.zcenter + self.distance,
            self.xcenter, self.ycenter, self.zcenter,
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

        gluLookAt(self.xcenter, self.ycenter, self.zcenter + self.distance,
            self.xcenter, self.ycenter, self.zcenter,
            0., 1., 0.)
        glMatrixMode(GL_MODELVIEW)

        # Call objects redraw method.
        self.redraw(self)
        glFlush()                               # Tidy up
        glPopMatrix()                   # Restore the matrix

        self.tk.call(self._w, 'swapbuffers')

    def mouse_rotate_view(self, event):
        self.perspective = True

    def actual_tkRedraw(self, *dummy):
        self.after_id = None
        if self.perspective:
            self.tkRedraw_perspective()
        else:
            self.tkRedraw_ortho()

def init():
    glDrawBuffer(GL_BACK)
    glDisable(GL_CULL_FACE)
    glLineStipple(2, 0x5555)
    glDisable(GL_LIGHTING)
    glClearColor(0,0,0,0)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

def draw_axes():
    glBegin(GL_LINES);

    glColor3f(0.2,1.0,0.2)
    glVertex3f(25.4,0.0,0.0)
    glVertex3f(0.0,0.0,0.0)

    glVertex3f(29.5,-1.5,0)
    glVertex3f(26.5,1.5,0)
    glVertex3f(29.5,1.5,0)
    glVertex3f(26.5,-1.5,0)

    glColor3f(1.0,0.2,0.2)
    glVertex3f(0.0,0.0,0.0)
    glVertex3f(0.0,25.4,0.0)

    glVertex3f(-1.5,29.5,0)
    glVertex3f(0.0,28,0)
    glVertex3f(1.5,29.5,0)
    glVertex3f(0.0,28,0)
    glVertex3f(0.0,28,0)
    glVertex3f(0.0,26.5,0)

    glColor3f(0.2,0.2,1.0)
    glVertex3f(0.0,0.0,0.0)
    glVertex3f(0.0,0.0,25.4)

    glVertex3f(-1.5,0.0,29.5)
    glVertex3f(1.5,0.0,29.5)
    glVertex3f(-1.5,0.0,26.5)
    glVertex3f(1.5,0.0,26.5)
    glVertex3f(1.5,0.0,29.5)
    glVertex3f(-1.5,0.0,26.5)

    glEnd();

#    Not sure I like this.
#    glColor3f(0.2,1.0,0.2)
#    glRasterPos(30,0,0)
#    glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord('X'))
#    glColor3f(1.0,0.2,0.2)
#    glRasterPos(0,30,0)
#    glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord('Y'))
#    glColor3f(0.2,0.2,1.0)
#    glRasterPos(0,0,30)
#    glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord('Z'))

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


program = highlight = None

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
    gluDeleteQuadric(q)
    glDisable(GL_LIGHTING)
    glEndList()

def make_main_list(g):
    global program
    if program is None: program = glGenLists(1)
    glNewList(program, GL_COMPILE)

    g.draw()

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
                root_window.tk.call("nf_dialog", ".error",
                                    "AXIS error", text, "info",0,"OK")
        self.after = self.win.after(20, self.update)

        if program_start_line_last == -1 or \
                self.stat.read_line < program_start_line_last:
            self.win.set_current_line(self.stat.read_line)
        else:
            self.win.set_current_line(self.stat.motion_line)

        p = array.array('f', list(self.stat.position[:3]))
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
                glColor3f(1,0,0)
                glBegin(GL_LINES)
                glVertex3f(*self.data[-6:-3])
                glVertex3f(*self.data[-3:])
                glEnd()
                glDrawBuffer(GL_BACK)
        o.redraw_soon()

        vupdate(vars.interp_state, self.stat.interp_state)
        vupdate(vars.task_mode, self.stat.task_mode)
        vupdate(vars.task_state, self.stat.task_state)
        vupdate(vars.taskfile, self.stat.file)
        vupdate(vars.interp_pause, self.stat.paused)
        vupdate(vars.mist, self.stat.mist)
        vupdate(vars.flood, self.stat.flood)
        vupdate(vars.brake, self.stat.spindle_brake)
        vupdate(vars.spindledir, self.stat.spindle_direction)
        vupdate(vars.feedrate, int(100 * self.stat.feedrate))
        current_tool = [i for i in s.tool_table if i[0] == s.tool_in_spindle]
        if s.tool_in_spindle == 0:
            vupdate(vars.tool, "No tool")
        elif current_tool == []:
            vupdate(vars.tool, "Unknown tool %d" % s.tool_in_spindle)
        else:
            vupdate(vars.tool,
                 "Tool %d, offset %g, radius %g" % current_tool[0])
        active_codes = []
        for i in s.gcodes[1:]:
            if i == -1: continue
            if i % 10 == 0:
                active_codes.append("G%d" % (i/10))
            else:
                active_codes.append("G%d.%d" % (i/10, i%10))

        for i in s.mcodes[1:]:
            if i == -1: continue
            active_codes.append("M%d" % i)

        active_codes.append("F%.0f" % s.settings[1])
        active_codes.append("S%.0f" % s.settings[2])

        mid = len(active_codes)/2
        a, b = active_codes[:mid], active_codes[mid:]
        active_codes = " ".join(a) + "\n" + " ".join(b)
        vupdate(vars.active_codes, active_codes)

    def clear(self):
        del self.data[:]
        self.win.live_plot_size = 0
        o.redraw_soon()

def ensure_mode(m):
    s.poll()
    if s.task_mode == emc.MODE_AUTO and s.interp_state!=emc.INTERP_IDLE: return
    if s.task_mode != m: c.mode(m)

def open_file_guts(f):
    ensure_mode(emc.MODE_AUTO)
    f = os.path.abspath(f)
    c.reset_interpreter()
    c.program_open(f)
    t.configure(state="normal")
    t.delete("0.0", "end")
    for i, l in enumerate(open(f)):
        l = l.expandtabs().replace("\r", "")
        t.insert("end", "%6d: " % (i+1), "lineno", l)
    code = parse_lines(f)
    interp = rs274.Interpreter(GLCanon)
    interp.execute(prologue_code)
    o.g = g = interp.execute(code)
    t.configure(state="disabled")
    make_main_list(g)

def set_feedrate(*args):
    try:
        value = vars.feedrate.get()
    except ValueError: return
    value = value / 100.
    c.feedrate(value)
    for i in range(5):
        if s.feedrate == value: break
        time.sleep(.05)
        s.poll()

vars = nf.Variables(root_window, 
    ("mdi_command", StringVar),
    ("taskfile", StringVar),
    ("interp_pause", IntVar),
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
    ("feedrate", IntVar),
    ("tool", IntVar),
    ("active_codes", StringVar),
)
vars.show_program.set(1)
vars.show_live_plot.set(1)
vars.feedrate.trace("w", set_feedrate)

widgets = nf.Widgets(root_window, 
    ("text", Text, ".t.text"),
    ("preview_frame", Frame, ".preview"),
    ("mdi_history", Text, ".tabs.mdi.history"),

    ("axis_x", Radiobutton, ".tabs.manual.axes.axisx"),
    ("axis_y", Radiobutton, ".tabs.manual.axes.axisy"),
    ("axis_z", Radiobutton, ".tabs.manual.axes.axisz"),
    ("axis_a", Radiobutton, ".tabs.manual.axes.axisa"),
    ("axis_b", Radiobutton, ".tabs.manual.axes.axisb"),
    ("axis_c", Radiobutton, ".tabs.manual.axes.axisc"),

    ("jogspeed", Entry, ".tabs.manual.jogf.jogspeed"),

    ("flood", Checkbutton, ".tabs.manual.flood"),
    ("mist", Checkbutton, ".tabs.manual.mist"),

    ("brake", Checkbutton, ".tabs.manual.spindlef.brake"),

    ("spindle_ccw", Radiobutton, ".tabs.manual.spindlef.ccw"),
    ("spindle_stop", Radiobutton, ".tabs.manual.spindlef.stop"),
    ("spindle_cw", Radiobutton, ".tabs.manual.spindlef.cw"),
)

def activate_axis(i):
    axis = getattr(widgets, "axis_%s" % "xyzabc"[i])
    axis.focus()
    axis.invoke()

def set_first_line(lineno):
    global program_start_line
    program_start_line = lineno

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
        o.reset()
        glRotatef(-90, 0, 1, 0)
        glRotatef(-90, 1, 0, 0)
        o.perspective = False
        o.set_eyepoint(5.)
        o.tkRedraw()

    def set_view_y(event=None):
        o.reset()
        glRotatef(-90, 1, 0, 0)
        o.perspective = False
        o.set_eyepoint(5.)
        o.tkRedraw()
        
    def set_view_z(event=None):
        o.reset()
        o.perspective = False
        o.set_eyepoint(5.)
        o.tkRedraw()

    def set_view_z2(event=None):
        o.reset()
        o.perspective = False
        glRotatef(-90, 0, 0, 1)
        o.set_eyepoint(5.)
        o.tkRedraw()


    def set_view_p(event=None):
        o.reset()
        glRotatef(35, 1., 0., 0.)
        glRotatef(105, 0., 1., 0.)

        glRotatef(-90, 0, 1, 0)
        glRotatef(-90, 1, 0, 0)
        o.perspective = True
        o.set_eyepoint(5.)
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
            c.state(emc.STATE_ESTOP_RESET)

    def open_file(*event):
        f = root_window.tk.call("tk_getOpenFile", "-initialdir", ".",
            "-defaultextension", ".ngc",
            "-filetypes", "{{rs274ngc files} {.ngc}} {{All files} *}")
        if not f: return
        o.set_highlight_line(None)
        f = str(f)
        open_file_guts(f)

    def reload_file(*event):
        s.poll()
        o.set_highlight_line(None)
        open_file_guts(s.file)

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
        if s.paused:
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

    def clear_live_plot(*ignored):
        live_plotter.clear()

    def jog_plus(event=None):
        jog_on(vars.current_axis.get(), 1)
    def jog_minus(event=None):
        jog_on(vars.current_axis.get(), -1)
    def jog_stop(event=None):
        jog_off(vars.current_axis.get())
    def home_axis(event=None):
        ensure_mode(emc.MODE_MANUAL)
        c.home("xyzabc".index(vars.current_axis.get()))
    def brake(event=None):
        ensure_mode(emc.MODE_MANUAL)
        c.brake(vars.brake.get())
    def flood(event=None):
        ensure_mode(emc.MODE_MANUAL)
        c.flood(vars.flood.get())
    def mist(event=None):
        ensure_mode(emc.MODE_MANUAL)
        c.mist(vars.mist.get())
    def spindle(event=None):
        ensure_mode(emc.MODE_MANUAL)
        c.spindle(vars.spindledir.get())
    def set_first_line(lineno):
        set_first_line(lineno)

commands = TclCommands(root_window)
root_window.bind("<Escape>", commands.task_stop)
root_window.bind("o", commands.open_file)
root_window.bind("s", commands.task_resume)
root_window.bind("p", commands.task_pause)
root_window.bind("<Alt-p>", "#nothing")
root_window.bind("r", commands.task_run)
root_window.bind("<Control-r>", commands.reload_file)
root_window.bind("<Key-F1>", commands.estop_clicked)
root_window.bind("<Key-F2>", commands.onoff_clicked)
root_window.bind("<Control-k>", commands.clear_live_plot)
root_window.bind("x", lambda event: activate_axis(0))
root_window.bind("y", lambda event: activate_axis(1))
root_window.bind("z", lambda event: activate_axis(2))
root_window.bind("a", lambda event: activate_axis(3))
root_window.bind("b", lambda event: activate_axis(4))
root_window.bind("c", lambda event: activate_axis(5))
root_window.bind("<Home>", commands.home_axis)
widgets.mdi_history.bind("<Configure>", "%W see {end - 1 lines}")

def jog(*args):
    ensure_mode(emc.MODE_MANUAL)
    print "jog", args
    c.jog(*args)

jog_after = [None] * 6
jog_cont  = [False] * 6
def jog_on(a, b):
    if isinstance(a, (str, unicode)):
        a = "xyzabc".index(a)
    if jog_after[a]:
        root_window.after_cancel(jog_after[a])
        jog_after[a] = None
        return
    jogspeed = widgets.jogspeed.get()
    if jogspeed != "Continuous":
        jogspeed = float(jogspeed)
        jog(emc.JOG_INCREMENT, a, b, jogspeed)
        jog_cont[a] = False
    else:
        jog(emc.JOG_CONTINUOUS, a, b)
        jog_cont[a] = True

def jog_off(a):
    if isinstance(a, (str, unicode)):
        a = "xyzabc".index(a)
    if jog_after[a]: return
    jog_after[a] = root_window.after_idle(lambda: jog_off_actual(a))

def jog_off_actual(a):
    activate_axis(a)
    jog_after[a] = None
    if jog_cont[a]:
        jog(emc.JOG_STOP, a)

def bind_axis(a, b, d):
    root_window.bind("<KeyPress-%s>" % a, lambda e: jog_on(d, -1))
    root_window.bind("<KeyPress-%s>" % b, lambda e: jog_on(d, 1))
    root_window.bind("<KeyRelease-%s>" % a, lambda e: jog_off(d))
    root_window.bind("<KeyRelease-%s>" % b, lambda e: jog_off(d))

bind_axis("Left", "Right", 0)
bind_axis("Down", "Up", 1)
bind_axis("Next", "Prior", 2)

def set_tabs(e):
    t.configure(tabs="%d right" % (e.width - 2))

import sys, getopt, _tkinter
axiscount = 3
axisnames = "X Y Z".split()

if len(sys.argv) > 1 and sys.argv[1] == '-ini':
    import ConfigParser
    inifile = emc.ini(sys.argv[2])
    axiscount = int(inifile.find("TRAJ", "AXES"))
    axisnames = inifile.find("TRAJ", "COORDINATES").split()
    emc.nmlfile = inifile.find("EMC", "NML_FILE")
    del sys.argv[1:3]
opts, args = getopt.getopt(sys.argv[1:], 'd:')
for i in range(len(axisnames), 6):
    c = getattr(widgets, "axis_%s" % ("xyzabc"[i]))
    c.grid_forget()
s = emc.stat(); s.poll()
c = emc.command()
e = emc.error_channel()

prologue = ["g80 g17 g40 g20 g90 g94 g54 g49 g99 g64 m5 m9 m48 f60 s0\n"]
prologue_code = parse_lines('<prologue>', prologue)

o = MyOpengl(widgets.preview_frame, width=60, height=40, double=1, depth=1)
o.last_line = 1
o.pack(fill="both", expand=1)

def go_manual(event=None):
    root_window.tk.call(".tabs", "select", 0)
    root_window.tk.call("focus", ".")
root_window.bind("<Key-F3>", go_manual)

def go_mdi(event=None):
    root_window.tk.call(".tabs", "select", 1)
    root_window.tk.call("focus", ".tabs.mdi.command")
root_window.bind("<Key-F5>", go_mdi)

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
t.bind("<Button>", select_line)
t.configure(state="disabled")
activate_axis(0)

make_cone()

live_plotter = LivePlotter(o)
def redraw(self):
    if self.select_event:
        self.select(self.select_event)
        self.select_event = None

    glDisable(GL_LIGHTING)
    glMatrixMode(GL_MODELVIEW)

    if vars.show_program.get():
        if program is not None: glCallList(program)
        if highlight is not None: glCallList(highlight)

    if vars.show_live_plot.get():
        glColor3f(1,0,0)
        glDepthFunc(GL_ALWAYS)
        glDrawArrays(GL_LINE_STRIP, 0, o.live_plot_size)
        glDepthFunc(GL_LESS);
        if live_plotter.running.get() and live_plotter.data:
            pos = live_plotter.data[-3:]
            glPushMatrix()
            glTranslatef(*pos)
            glCallList(cone_program)
            glPopMatrix()
    if vars.show_live_plot.get() or vars.show_program.get():
        glPushMatrix()
        glScalef(1/25.4, 1/25.4, 1/25.4)
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

    positions = ["%c:% 9.4f" % i for i in zip(axisnames, s.actual_position)]

    maxlen = max([len(p) for p in positions])

    glDepthFunc(GL_ALWAYS)
    glDepthMask(GL_FALSE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0,0,0,.7)
    glBegin(GL_QUADS)
    glVertex3f(0, ypos, 1)
    glVertex3f(9*maxlen+30, ypos, 1)
    glVertex3f(9*maxlen+30, ypos - 20 - 15*axiscount, 1)
    glVertex3f(0, ypos - 20 - 15*axiscount, 1)
    glEnd()
    glDisable(GL_BLEND)

    maxlen = 0
    ypos -= 20
    i=0
    glColor(1,1,1)
    for string in positions:
        maxlen = max(maxlen, len(string))
        if s.homed[i]:
            glRasterPos(6, ypos)
            glBitmap(13, 16, 0, 3, 17, 0, homeicon)
        else:
            glRasterPos(23, ypos)
        for char in string:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))
        ypos -= 15
        i = i + 1
    glDepthFunc(GL_LESS)
    glDepthMask(GL_TRUE)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)



o.redraw = redraw

code = []
if args:
    open_file_guts(args[0])

o.mainloop()

# vim:sw=4:sts=4:et:
