from rs274 import ArcsToSegmentsMixin
from OpenGL.GL import *

class GLCanon(ArcsToSegmentsMixin):
    def __init__(self, state, text=None):
        self.traverse = []
        self.feed = []
        self.wfeed = []
        self.dwells = []
        self.state = state
        self.choice = None
        self.ox = self.oy = self.oz = 0
        self.text = text

    def next_line(self):
        if self.text is None: return
        if self.state.filename == '<prologue>': return
        st= self.state
        state = " ".join(
            ["G%g" % i for i in st.gmodes if i is not None]
            + ["M%g" % i for i in st.mmodes if i is not None]
            + ["S%g F%g" % (st.spindle_rate, st.feed_rate)])
        self.text.insert("%d.end" % st.lineno, "\t" + state, "state")

    def set_spindle_rate(self, arg): pass
    def set_feed_rate(self, arg): pass
    def comment(self, arg): pass
    def select_plane(self, arg): pass

    def straight_traverse(self, x,y,z, a,b,c):
        if a:
            c = cos(a * pi/180); s = sin(a * pi/180)
            y, z = y * c - z * s, y*s + z*c
        self.traverse.append((self.state.lineno, self.ox, self.oy, self.oz, x,y,z))
        self.ox = x
        self.oy = y
        self.oz = z

    def straight_feed(self, x,y,z, a,b,c):
        if a:
            c = cos(a * pi/180); s = sin(a * pi/180)
            y, z = y * c - z * s, y*s + z*c
        self.feed.append((self.state.lineno, self.ox, self.oy, self.oz, x,y,z))
        self.ox = x
        self.oy = y
        self.oz = z

    def dwell(self, arg):
        if self.state.gmodes[1] <= 3:
            color = (1,1,1)
        else:
            color = (1,.5,.5)
        self.dwells.append((self.state.lineno, color, self.ox, self.oy, self.oz, self.state.gmodes[2]-17))


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


