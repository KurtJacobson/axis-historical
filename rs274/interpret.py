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
import math
from rs274 import Deleted

AXIS_XY, AXIS_XZ, AXIS_YZ = range(3)

class Vars(dict):
    def __init__(self, *args, **kw):
        dict.__init__(self, *args, **kw)
        self.pending = {}

    def eval(self, k):
        if hasattr(k, 'eval'):
            return k.eval(self)
        return float(k)

    def pending_set(self, k, v):
        self.pending[int(k)] = v

    def do_pending(self):
        if self.pending:
            self.update(self.pending)
            self.pending = {}

# 3.8 Order of Execution
#
# The order of execution of items on a line is critical to safe and effective
# machine operation. Items are executed in the order shown in Table 8 if they
# occur on the same line.
#
#     1. comment (includes message).
#     2. set feed rate mode (G93, G94 - inverse time or per minute).
#     3. set feed rate (F).
#     4. set spindle speed (S).
#     5. select tool (T).
#     6. change tool (M6).
#     7. spindle on or off (M3, M4, M5).
#     8. coolant on or off (M7, M8, M9).
#     9. enable or disable overrides (M48, M49).
#     10. dwell (G4).
#     11. set active plane (G17, G18, G19).
#     12. set length units (G20, G21).
#     13. cutter radius compensation on or off (G40, G41, G42)
#     14. cutter length compensation on or off (G43, G49)
#     15. coordinate system selection (G54, G55, G56, G57, G58, G59, G59.1,
#         G59.2, G59.3).
#     16. set path control mode (G61, G61.1, G64)
#     17. set distance mode (G90, G91).
#     18. set retract mode (G98, G99).
#     19. home (G28, G30) or change coordinate system data (G10) or set axis
#         offsets (G92, G92.1, G92.2, G94).
#     20. perform motion (G0 to G3, G80 to G89), as modified (possibly) by
#         G53.
#     21. stop (M0, M1, M2, M30, M60).
#
#   Table 8. Order of Execution

modal_groups_g = {
    0:1, 1:1, 2:1, 3:1, 38.2:1, 80:1, 82:1, 83: 1, 84:1, 85:1,
    86:1, 87:1, 88:1, 89:1,

    17:2, 18:2, 19:2,

    90:3, 91:3,

    93:5, 94:5,

    20:6, 21:6,

    40:7, 41:7, 42:7,

    43:8, 49:8,

    98:10, 99:10,

    54:12, 55:12, 56:12, 58:12, 59:12, 59.1:12, 59.2:12, 59.3: 12,

    61:13, 61.1:13, 64:13,

    4:0, 10:0, 28:0, 30:0, 53:0, 92:0, 92.1:0, 92.2:0, 92.3:0,
}

modal_groups_m = {
    0:4, 1:4, 2:4, 30:4, 60:4,

    6:6,

    3:7, 4:7, 5:7,

    7:8, 8:8, 9:8,

    48:9, 49:9,
}

class Bundle(object): pass

class ArcsToSegmentsMixin:
    def arc_feed(self, x1, y1, cx, cy, rot, z1, a, b, c):
        if self.state.gmodes[2] == 17:
            f = n = [x1,y1,z1, a, b, c]
            xyz = [0,1,2]
        elif self.state.gmodes[2] == 18:
            f = n = [x1,z1,y1, a, b, c]
            xyz = [0,2,1]
        else:
            f = n = [z1,y1,x1, a, b, c]
            xyz = [2,1,0]
        o = [self.ox, self.oy, self.oz, 0, 0, 0]
        theta1 = math.atan2(o[xyz[1]]-cy, o[xyz[0]]-cx)
        theta2 = math.atan2(n[xyz[1]]-cy, n[xyz[0]]-cx)
        rad = math.hypot(o[xyz[0]]-cx, o[xyz[1]]-cy)

        if rot < 0:
            if theta2 >= theta1: theta2 -= math.pi * 2
        else:
            if theta2 <= theta1: theta2 += math.pi * 2

        def interp(low, high):
            return low + (high-low) * i / steps

        steps = 32
        p = [0] * 6
        for i in range(1, steps):
            theta = interp(theta1, theta2)
            p[xyz[0]] = math.cos(theta) * rad + cx
            p[xyz[1]] = math.sin(theta) * rad + cy
            p[xyz[2]] = interp(o[xyz[2]], n[xyz[2]])
            p[3] = interp(o[3], n[3])
            p[4] = interp(o[4], n[4])
            p[5] = interp(o[5], n[5])
            self.straight_feed(*p)
        self.straight_feed(*n)

class PrintCanon:
    def __init__(self, state): self.state = state

    def next_line(self): pass

    def set_feed_rate(self, arg):
        print "set feed rate", arg

    def comment(self, arg):
        print "#", arg

    def straight_traverse(self, *args):
        print "straight_traverse %.4g %.4g %.4g  %.4g %.4g %.4g" % args

    def straight_feed(self, *args):
        print "straight_feed %.4g %.4g %.4g  %.4g %.4g %.4g" % args

    def dwell(self, arg):
        if arg < .1:
            print "dwell %f ms" % (1000 * arg)
        else:
            print "dwell %f seconds" % arg

    def arc_feed(self, *args):
        print "arc_feed %.4g %.4g  %.4g %.4g %.4g  %.4g  %.4g %.4g %.4g" % args

def execute_code(lines, target_class):
    return Interpreter(target_class).execute(lines)

class Interpreter:
    def __init__(self, target_class):
        self.v = Vars()
        state = self.state = Bundle()
        state.lineno = 0
        state.feed_rate = state.spindle_rate = 0
        state.gmodes = [None] * 14
        state.mmodes = [None] * 10
        state.coords = {'x': 0, 'y': 0, 'z': 0, 'a': 0, 'b': 0, 'c': 0}
        state.vars = self.v
        state.sticky = {}
        target = self.target = target_class(state)

    def execute(self, lines):
        v = self.v
        state = self.state
        target = self.target
        for l in lines:
            if isinstance(l, Deleted): continue
            state.gmodes[0] = None
            parts = [(k.lower(), v.eval(o)) for k, o in l.segments]
            state.words = state.sticky
            state.sticky = {}
            state.lineno = getattr(l, "lineno", state.lineno+1)
            state.filename = getattr(l, "filename", "")
            last_gmodes = state.gmodes[:]
            last_mmodes = state.mmodes[:]
            last_coords = [state.coords[c] for c in "xyzabc"]
            moved = 0
            for c in l.comments:
                target.comment(c)

            if state.gmodes[6] == 21: scale = 1/25.4
            else: scale = 1
            for k, o in parts:
                if k == "g":
                    idx = modal_groups_g.get(o)
                    state.gmodes[idx] = o
                elif k == "m":
                    idx = modal_groups_m.get(o)
                    state.mmodes[idx] = o
                elif k in "ijkr":
                    state.words[k] = o * scale
                elif k in "abcxyz":
                    state.coords[k] = o * scale
                    moved = 1
                else:
                    state.words[k] = o

            target.next_line()

            if state.words.has_key('s'):
                state.spindle_rate = state.words['s']
                target.set_spindle_rate(state.words['s'])

            # 3. set feed rate
            if state.words.has_key('f'):
                state.feed_rate = state.words['f']
                target.set_feed_rate(state.words['f'])

            # 10. dwell
            if state.gmodes[0] == 4:
                target.dwell(state.words['p'])

            # 11. set active plane
            if state.gmodes[2] != last_gmodes[2]:
                target.select_plane(state.gmodes[2]-17)

            coords = [state.coords[c] for c in "xyzabc"]

            # perform motion
            if moved:
                if state.gmodes[1] == 0:
                    target.straight_traverse(*coords)
                elif state.gmodes[1] == 1:
                    target.straight_feed(*coords)
                elif state.gmodes[1] in (2,3):
                    self.execute_arc(coords, last_coords)
                elif state.gmodes[1] in (81,82,83,84,85,86,87,88,89):
                    self.execute_canned_cycle(coords, last_coords)
                elif state.gmodes[1] is None:
                    pass
                else:
                    target.comment("Unsupported cycle %s" % state.gmodes[1])

            for s in l.assignments: v.eval(s)
            v.do_pending()
        return target

    def execute_canned_cycle(self, coords, last_coords):
        state = self.state
        target = self.target
        if state.gmodes[2] == 17:
            xyz = [0,1,2]
        elif state.gmodes[2] == 18:
            xyz = [1,2,0]
        else:
            xyz = [2,0,1]

        if state.words.has_key('l'):
            target.comment("Canned cycle repeat not supported" % state.gmodes[1])

        if state.gmodes[10] == 98 and last_coords[xyz[2]] > state.words['r']:
            clear_z = last_coords[xyz[2]]
        else:
            clear_z = state.words['r']
            state.sticky['r'] = state.words['r']

        # Preliminary motion
        # 1. a straight traverse parallel to the plane
        move = coords[:]
        move[xyz[2]] = last_coords[xyz[2]]
        target.straight_traverse(*move)
        # 2. a straight traverse to the R position
        move = coords[:]
        move[xyz[2]] = state.words['r']
        target.straight_traverse(*move)

        if state.gmodes[1] == 81:
            # Move the Z-axis only at the current feed rate to the Z position
            move[xyz[2]] = coords[xyz[2]]
            target.straight_feed(*move)
        elif state.gmodes[1] == 82:
            # Move the Z-axis only at the current feed rate to the Z position
            move[xyz[2]] = coords[xyz[2]]
            target.straight_feed(*move)
            # Dwell for the P number of secionds
            target.dwell(state.words['p'])
        else:
            target.comment("Canned cycle %s not supported" % state.gmodes[1])

        # Retract the Z-axis at traverse rate to clear Z
        move[xyz[2]] = clear_z
        target.straight_traverse(*move)

        # Set the end Z to the clear Z
        state.coords["xyz"[xyz[2]]] = clear_z

    def execute_arc(self, coords, last_coords):
        state = self.state
        target = self.target
        # x y z a b c i j
        if state.gmodes[1] == 2: rotation = -1  # Clockwise
        else: rotation = 1                      # Counter-clockwise

        if state.gmodes[2] == 17:
            xyz = [0,1,2]
        elif state.gmodes[2] == 18:
            xyz = [0,2,1]
        else:
            xyz = [2,1,0]

        first_end = coords[xyz[0]]
        second_end = coords[xyz[1]]
        axis_end_point = coords[xyz[2]]
        if 'r' in state.words:
            r = state.words.get('r')
            target.comment("radius arcs not supported")
            dx = first_end - last_coords[xyz[0]]
            dy = second_end - last_coords[xyz[1]]
            theta = math.atan2(dy,dx)
            d = math.hypot(dy,dx)
            A = math.acos(d / (2 * r ))
            if rotation == 1:
                A = theta - A
            else:
                A = theta + A
            i = r * math.cos(A)
            j = r * math.sin(A)
        else:
            # XXX one of i, j may be ommitted according to the spec
            # and it is calculated so that the stance to the start and
            # end positions are the same.
            # XXX emc plots the following, but it seems underspecified
            # (more than 1 j value is possible): g0x0y0z0 / g2x0y0i.5z1

            i = state.words.get('ijk'[xyz[0]], 0)
            j = state.words.get('ijk'[xyz[1]], 0)

        first_axis = last_coords[xyz[0]] + i
        second_axis = last_coords[xyz[1]] + j

        target.arc_feed(first_end, second_end,
                        first_axis, second_axis, rotation,
                        axis_end_point, *coords[3:])

def display_code(lines):
    v = Vars()
    for l in lines:
        print l,
        for s in l.assignments: v.eval(s)
        print "\t(",
        if v.pending: print v.pending,
        for s in l.segments:
            print "%s%.4g" % (s[0], v.eval(s[1])),
        print ")"
        v.do_pending()

# vim:ts=8:sts=4:et:
