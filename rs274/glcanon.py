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

    def draw_lines(self, lines):
        for lineno, x1,y1,z1, x2,y2,z2 in lines:
            glLoadName(lineno)
            glBegin(GL_LINES)
            glVertex3f(x1,y1,z1)
            glVertex3f(x2,y2,z2)
            glEnd()

    def highlight(self, lineno):
        glLineWidth(3)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        c = 0, 255, 255
        glColor3fv(c)
        for line in self.traverse:
            if line[0] != lineno: continue
            glBegin(GL_LINES)
            glVertex3fv(line[1:4])
            glVertex3fv(line[4:7])
            glEnd()
        for line in self.feed:
            if line[0] != lineno: continue
            glBegin(GL_LINES)
            glVertex3fv(line[1:4])
            glVertex3fv(line[4:7])
            glEnd()
        for line in self.dwells:
            if line[0] != lineno: continue
            self.draw_dwells([(line[0], c) + line[2:]])
        glHint(GL_LINE_SMOOTH_HINT, GL_FASTEST)
        glLineWidth(1)

    def draw(self):
        glEnable(GL_LINE_STIPPLE)
        glColor3f(.3,.5,.5)
        self.draw_lines(self.traverse)
        glDisable(GL_LINE_STIPPLE)

        glColor3f(1,1,1)
        self.draw_lines(self.feed)

        glColor3f(1,.5,.5)
        self.draw_dwells(self.dwells)

    def draw_dwells(self, dwells):
        delta = .015625
        for l,c,x,y,z,axis in dwells:
            glColor3fv(c)
            glLineWidth(2)
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
            glEnd()
            glLineWidth(1)


