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

from rs274 import Translated, ArcsToSegmentsMixin
from OpenGL.GL import *

class GLCanon(Translated, ArcsToSegmentsMixin):
    def __init__(self, text=None):
        self.traverse = []
        self.feed = []
        self.wfeed = []
        self.dwells = []
        self.choice = None
        self.ox = self.oy = self.oz = 0
        self.text = text

    def get_external_parameter_filename(self): # XXX not used and wrong
        return "/usr/src/emc/sim.var"

    def next_line(self, st):
        self.state = st
        if self.text is None: return
        state = " ".join(
            ["G%g" % i for i in st.gcodes[1:] if i is not None]
            + ["M%g" % i for i in st.mcodes[1:] if i is not None]
            + ["S%g F%g" % (st.spindle, st.speed)])
        self.text.insert("%d.end" % st.sequence_number, "\t" + state, "state")

    def set_spindle_rate(self, arg): pass
    def set_feed_rate(self, arg): pass
    def comment(self, arg): pass
    def select_plane(self, arg): pass

    def straight_traverse_translated(self, x,y,z, a,b,c):
        if a:
            c = cos(a * pi/180); s = sin(a * pi/180)
            y, z = y * c - z * s, y*s + z*c
        self.traverse.append((self.state.sequence_number, self.ox, self.oy, self.oz, x,y,z))
        self.ox = x
        self.oy = y
        self.oz = z

    def straight_feed_translated(self, x,y,z, a,b,c):
        if a:
            c = cos(a * pi/180); s = sin(a * pi/180)
            y, z = y * c - z * s, y*s + z*c
        self.feed.append((self.state.sequence_number, self.ox, self.oy, self.oz, x,y,z))
        self.ox = x
        self.oy = y
        self.oz = z

    def dwell(self, arg):
        if self.state.feed_mode <= 30:
            color = (1,1,1)
        else:
            color = (1,.5,.5)
        self.dwells.append((self.state.sequence_number, color, self.ox, self.oy, self.oz, self.state.plane/10-17))


    def draw_lines(self, lines, for_selection):
        if for_selection:
            for lineno, x1,y1,z1, x2,y2,z2 in lines:
                glLoadName(lineno)
                glBegin(GL_LINES)
                glVertex3f(x1,y1,z1)
                glVertex3f(x2,y2,z2)
                glEnd()
        else:
            first = True
            for lineno, x1,y1,z1, x2,y2,z2 in lines:
                if first:
                    glBegin(GL_LINE_STRIP)
                    first = False
                    glVertex3f(x1,y1,z1)
                elif x1 != ox or y1 != oy or z1 != oz:
                    glEnd()
                    glBegin(GL_LINE_STRIP)
                    glVertex3f(x1,y1,z1)
                glVertex3f(x2,y2,z2)
                ox = x2; oy = y2; oz = z2
            if not first:
                glEnd()

    def highlight(self, lineno):
        glLineWidth(3)
        c = 0, 255, 255
        glColor3fv(c)
        glBegin(GL_LINES)
        for line in self.traverse:
            if line[0] != lineno: continue
            glVertex3fv(line[1:4])
            glVertex3fv(line[4:7])
        for line in self.feed:
            if line[0] != lineno: continue
            glVertex3fv(line[1:4])
            glVertex3fv(line[4:7])
        for line in self.dwells:
            if line[0] != lineno: continue
            self.draw_dwells([(line[0], c) + line[2:]], 2)
        glEnd()
        glLineWidth(1)

    def draw(self, for_selection=0):
        glEnable(GL_LINE_STIPPLE)
        glColor3f(.3,.5,.5)
        self.draw_lines(self.traverse, for_selection)
        glDisable(GL_LINE_STIPPLE)

        glColor3f(1,1,1)
        self.draw_lines(self.feed, for_selection)

        glColor3f(1,.5,.5)
        glLineWidth(2)
        self.draw_dwells(self.dwells, for_selection)
        glLineWidth(1)

    def draw_dwells(self, dwells, for_selection):
        delta = .015625
        if for_selection == 0:
            glBegin(GL_LINES)
        for l,c,x,y,z,axis in dwells:
            glColor3fv(c)
            if for_selection == 1:
                glLoadName(l)
                glBegin(GL_LINES)
            if axis == 0:
                glVertex3f(x-delta,y-delta,z)
                glVertex3f(x+delta,y+delta,z)
                glVertex3f(x-delta,y+delta,z)
                glVertex3f(x+delta,y-delta,z)

                glVertex3f(x+delta,y+delta,z)
                glVertex3f(x-delta,y-delta,z)
                glVertex3f(x+delta,y-delta,z)
                glVertex3f(x-delta,y+delta,z)
            elif axis == 1:
                glVertex3f(x-delta,y,z-delta)
                glVertex3f(x+delta,y,z+delta)
                glVertex3f(x-delta,y,z+delta)
                glVertex3f(x+delta,y,z-delta)

                glVertex3f(x+delta,y,z+delta)
                glVertex3f(x-delta,y,z-delta)
                glVertex3f(x+delta,y,z-delta)
                glVertex3f(x-delta,y,z+delta)
            else:
                glVertex3f(x,y-delta,z-delta)
                glVertex3f(x,y+delta,z+delta)
                glVertex3f(x,y+delta,z-delta)
                glVertex3f(x,y-delta,z+delta)

                glVertex3f(x,y+delta,z+delta)
                glVertex3f(x,y-delta,z-delta)
                glVertex3f(x,y-delta,z+delta)
                glVertex3f(x,y+delta,z-delta)
            if for_selection == 1:
                glEnd()
        if for_selection == 0:
            glEnd()

# vim:ts=8:sts=4:et:
