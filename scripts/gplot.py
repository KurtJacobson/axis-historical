#!/usr/bin/env python2
#    This is a component of AXIS, a front-end for emc
#    Copyright 2004 Jeff Epler <jepler@unpythonic.net> and
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

from Tkinter import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.Tk import *
from OpenGL.Tk import _default_root as root_window
from _glfixes import glInterleavedArrays

from math import hypot, atan2, sin, cos, pi, sqrt
from rs274 import execute_code, ArcsToSegmentsMixin, parse_lines
from rs274.glcanon import GLCanon
import rs274.options
import _tkinter
import emc

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
        self.highlight_line = None

    def select(self, event):
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
            if self.highlight_line is None:
                t.see("%d.0" % (line+2))
                t.see("%d.0" % line)
            t.tag_add("executing", "%d.0" % line, "%d.end" % line)

    def set_highlight_line(self, line):
        l = self.highlight_line = line
        t.tag_remove("sel", "0.0", "end")
        if line is not None:
            t.see("%d.0" % (l+2))
            t.see("%d.0" % l)
            t.tag_add("sel", "%d.0" % l, "%d.end" % l)
        global highlight
        if highlight is not None: glDeleteLists(highlight, 1)
        highlight = glGenLists(1)
        glNewList(highlight, GL_COMPILE)
        if line is not None:
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


def set_view_p(e):
    o.reset()
    glRotatef(35, 1., 0., 0.)
    glRotatef(105, 0., 1., 0.)

    glRotatef(-90, 0, 1, 0)
    glRotatef(-90, 1, 0, 0)
    o.perspective = True
    o.set_eyepoint(5.)
    o.tkRedraw()
    
def toggle_perspective(e):
    o.perspective = not o.perspective
    o.tkRedraw()

def set_view_x(e):
    o.reset()
    glRotatef(-90, 0, 1, 0)
    glRotatef(-90, 1, 0, 0)
    o.perspective = False
    o.set_eyepoint(5.)
    o.tkRedraw()

def set_view_y(e):
    o.reset()
    glRotatef(-90, 1, 0, 0)
    o.perspective = False
    o.set_eyepoint(5.)
    o.tkRedraw()
    
def set_view_z(e):
    o.reset()
    o.perspective = False
    o.set_eyepoint(5.)
    o.tkRedraw()

def set_view_z2(e):
    o.reset()
    o.perspective = False
    glRotatef(-90, 0, 0, 1)
    o.set_eyepoint(5.)
    o.tkRedraw()

prologue = ["g80 g17 g40 g20 g90 g94 g54 g49 g99 g64 m5 m9 m48 f60 s0\n"]

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
    glDisable(GL_LIGHTING)
    glMatrixMode(GL_MODELVIEW)

    g.draw()

    glEndList()

import array
live_plot_data = array.array('f')

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

def clear_live_plot(*ignored):
    del live_plot_data[:]

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
        self.after = self.win.after(10, self.update)
        
        self.win.set_current_line(self.stat.motion_line)

        p = array.array('f', list(self.stat.position[:3]))
        if len(self.data) > 6 and \
                colinear(self.data[-6:-3], self.data[-3:], p):
            self.data[-3:] = p
        else:
            self.data.extend(p)

        glInterleavedArrays(GL_V3F, 0, self.data.tostring())
        self.win.live_plot_size = len(self.data)/3
        self.win.redraw_soon()

    def clear(self):
        del self.data[:]
        self.win.live_plot_size = 0
        o.redraw_soon()

def set_tabs(e):
    t.configure(tabs="%d right" % (e.width - 12))

def main():
    global o,t
    import sys, getopt, _tkinter
    opts, args = getopt.getopt(sys.argv[1:], 'd:')

    for k, v in opts:
        if k == '-d': emc.nmlfile = v

    if not args:
        try:
            s = emc.stat()
            f = s.gettaskfile()
        except emc.error: pass
        else:
            if f != '':
                args = [os.path.join(os.path.dirname(emc.nmlfile), f)]
    prologue_code = parse_lines('<prologue>', prologue)
    if args:
        root_window.wm_title("gplot %s - axis" % args[0])
        code = parse_lines(args[0])
    else:
        root_window.wm_title("gplot (no file) - axis")
        code = []
    o = MyOpengl(root_window, width=600, height=400, double=1, depth=1)
    if code:
        o.last_line = code[-1].lineno
    else:
        o.last_line = 1
    o.pack(fill="both", expand=1)
    root_window.bind("q", lambda event: root_window.destroy())
    root_window.bind("<Escape>", lambda event: root_window.destroy())
    root_window.bind("x", set_view_x)
    root_window.bind("y", set_view_y)
    root_window.bind("z", set_view_z)
    root_window.bind("Z", set_view_z2)
    root_window.bind("<space>", set_view_p)
    root_window.bind("o", toggle_perspective)
    root_window.bind("c", lambda event: live_plotter.clear())
    rs274.options.install(root_window)
    init()

    f = Frame()
    t = Text(f, width=80, height=9)
    t.bind("<Configure>", set_tabs)
    s = Scrollbar(f, command=t.yview, orient="v")
    t.configure(yscrollcommand=s.set, exportselection=0)
    t.pack(side="left", fill="both", expand=1)
    s.pack(side="left", fill="y")
    f.pack(side="top", fill="both")
    t.tag_configure("lineno", foreground="#808080")
    t.tag_configure("executing", background="#804040")
    t.tag_configure("state", foreground="#408040")
    if args:
        for i, l in enumerate(open(args[0])):
            l = l.expandtabs().replace("\r", "")
            t.insert("end", "%6d: " % (i+1), "lineno", l)
    else:
        f.pack_forget()
    t.bind("<Button>", select_line)
    root_window.bind("<Up>", select_prev)
    root_window.bind("<Down>", select_next)

    interp = rs274.Interpreter(lambda state: GLCanon(state, t))
    interp.execute(prologue_code)
    g = interp.execute(code)
    make_main_list(g)
    t.configure(state="disabled")

    make_cone()

    live_plotter = LivePlotter(o)
    def redraw(self):
        if self.select_event:
            self.select(self.select_event)
            self.select_event = None
        glCallList(program)
        if highlight is not None: glCallList(highlight)
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
        glPushMatrix()
        glScalef(1/25.4, 1/25.4, 1/25.4)
        draw_axes()
        glPopMatrix()


    o.g = g
    o.redraw = redraw
    o.mainloop()

if __name__ == '__main__':
    main()
# vim:sw=4:sts=4:et:
