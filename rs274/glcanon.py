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

from rs274 import Translated, ArcsToSegmentsMixin
from minigl import *
def glColor3fv(args): glColor3f(*args)
def glVertex3fv(args): glVertex3f(*args)

from math import sin, cos, pi

class GLCanon(Translated, ArcsToSegmentsMixin):
    def __init__(self, text=None):
        self.traverse = []; self.traverse_append = self.traverse.append
        self.feed = []; self.feed_append = self.feed.append
        self.dwells = []; self.dwells_append = self.dwells.append
        self.choice = None
        self.lo = (0,0,0)
        self.offset_x = self.offset_y = self.offset_z = 0
        self.text = text
        self.min_extents = [9e99,9e99,9e99]
        self.max_extents = [-9e99,-9e99,-9e99]

    def message(self, message): pass

    def get_external_parameter_filename(self): # XXX not used and wrong
        return "/usr/src/emc/sim.var"

    def next_line(self, st):
        self.state = st
        self.lineno = self.state.sequence_number + 1

    def calc_extents(self, p):
        for i in [0,1,2]:
            self.min_extents[i] = min(self.min_extents[i], p[i])
            self.max_extents[i] = max(self.max_extents[i], p[i])

    def set_spindle_rate(self, arg): pass
    def set_feed_rate(self, arg): pass
    def comment(self, arg): pass
    def select_plane(self, arg): pass

    def get_tool(self, tool):
        return tool, .75, .0625

    def set_origin_offsets(self, offset_x, offset_y, offset_z, offset_a, offset_b, offset_c):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.offset_z = offset_z

    def straight_traverse(self, x,y,z, a,b,c):
        l = (x + self.offset_x,y + self.offset_y,z + self.offset_z)
        self.traverse_append((self.lineno, self.lo, l))
        self.lo = l
        self.calc_extents(l)

    def straight_feed(self, x,y,z, a,b,c):
        l = (x + self.offset_x,y + self.offset_y,z + self.offset_z)
        self.feed_append((self.lineno, self.lo, l))
        self.lo = l
        self.calc_extents(l)

    def dwell(self, arg):
        if self.state.feed_mode <= 30:
            color = (1,1,1)
        else:
            color = (1,.5,.5)
        self.dwells_append((self.lineno, color, self.lo[0], self.lo[1], self.lo[2], self.state.plane/10-17))


    def draw_lines(self, lines, for_selection):
        if for_selection:
            for lineno, l1, l2 in lines:
                glLoadName(lineno)
                glBegin(GL_LINES)
                glVertex3fv(l1)
                glVertex3fv(l2)
                glEnd()
        else:
            first = True
            for lineno, l1, l2 in lines:
                if first:
                    glBegin(GL_LINE_STRIP)
                    first = False
                    glVertex3fv(l1)
                elif l1 != ol:
                    glEnd()
                    glBegin(GL_LINE_STRIP)
                    glVertex3fv(l1)
                glVertex3fv(l2)
                ol = l2
            if not first:
                glEnd()

    def highlight(self, lineno):
        glLineWidth(3)
        c = (0, 255, 255)
        glColor3f(*c)
        glBegin(GL_LINES)
        for line in self.traverse:
            if line[0] != lineno: continue
            glVertex3fv(line[1])
            glVertex3fv(line[2])
        for line in self.feed:
            if line[0] != lineno: continue
            glVertex3fv(line[1])
            glVertex3fv(line[2])
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
