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

import math, operator

def and_(a, b): return operator.and_(int(a), int(b))
def or_(a, b): return operator.or_(int(a), int(b))
def xor(a, b): return operator.xor(int(a), int(b))

def atan2_deg(a,b): return math.atan2(a,b) * 180 / math.pi
def atan_deg(a): return math.atan(a) * 180 / math.pi
def acos_deg(a): return math.acos(a) * 180 / math.pi
def asin_deg(a): return math.asin(a) * 180 / math.pi

def tan_deg(a): return math.tan(a * math.pi / 180)
def cos_deg(a): return math.cos(a * math.pi / 180)
def sin_deg(a): return math.sin(a * math.pi / 180)

class BinOp(object):
    __slots__ = ['o', 'l', 'r']
    func = {'**': pow, 'atan': atan2_deg,
            '*': operator.mul, '/': operator.truediv, 'mod': operator.mod,
            '+':  operator.add, '-':  operator.sub,
            'and': and_, 'or': or_, 'xor': xor
    }

    def __init__(self, o, l, r):
        self.o = o
        self.l = l
        self.r = r

    def __str__(self):
        return "%s %s %s" % (self.l, self.o, self.r)

    def __repr__(self):
        return "BinOp(%r,%r,%r)" % (self.o, self.l, self.r)

    def eval(self, vars):
        l = vars.eval(self.l)
        r = vars.eval(self.r)
        o = self.func[self.o.lower()]
	return o(l,r)

class UnOp(object):
    __slots__ = ['o', 'l']
    func = {'-': operator.neg, 'abs': abs, 'acos' : acos_deg,
            'asin': asin_deg, 'cos': cos_deg, 'exp': math.exp,
            'ln': math.log, 'round': round, 'sin': sin_deg,
            'sqrt': math.sqrt, 'tan': tan_deg, 'atan': atan_deg,
            'fix': math.floor, 'fup': math.ceil }
        # fix fup

    def __init__(self, o, l):
        self.o = o
        self.l = l

    def __str__(self):
        return "%s %s" % (self.o, self.l)

    def __repr__(self):
        return "%s(%r,%r)" % (self.__class__.__name__, self.o, self.l)

    def eval(self, vars):
        l = vars.eval(self.l)
        o = self.func[self.o.lower()]
	return o(l)

class Comment(str):
    def __str__(self): return "(%s)" % str.__str__(self)
    def __repr__(self): return "Comment(%s)" % str.__repr__(self)

class Normal(object):
    def __init__(self, gcode_lineno, segments):
        self.gcode_lineno = gcode_lineno
        self.all_segments = segments

    def get_comments(self):
        return [c for c in self.all_segments if isinstance(c, Comment)]
    comments = property(get_comments)
    def get_segments(self):
        return [c for c in self.all_segments if isinstance(c, tuple)]
    segments = property(get_segments)
    def get_assignments(self):
        return [c for c in self.all_segments if isinstance(c, Let)]
    assignments = property(get_assignments)

    def __str__(self):
        s = []
        if isinstance(self, Deleted): s.append("/")
        if self.gcode_lineno is not None:
            s.append("N%d" % self.gcode_lineno)
        for c in self.comments:
            s.append(str(c))
        for k, v in self.segments:
            if isinstance(v, (BinOp, UnOp)):
                s.append("%c %s" % (k, v))
            else:
                s.append("%c%s" % (k, v))
        for a in self.assignments:
            s.append(str(a))
        return " ".join(s)

    def __repr__(self):
        return "%s(%s, %s)" % (
            self.__class__.__name__, self.gcode_lineno, self.all_segments)

class Deleted(Normal):
    def __init__(self, gcode_lineno, segments):
        Normal.__init__(self, gcode_lineno, segments)

def Expression(body): return body

class Parameter(object):
    __slots__ = ['i']
    def __init__(self, i):
        self.i = i

    def __str__(self): return "#%s" % self.i
    def __repr__(self): return "Parameter(%r)" % self.i
    def eval(self, vars):
        return vars.get(int(self.i), 0)

class Let(object):
    __slots__ = ['i', 'v']
    def __init__(self, i, v):
        self.i = i
        self.v = v

    def __str__(self): return "%s=%s" % (self.i, self.v)
    def __repr__(self): return "Let(%r,%r)" % (self.i, self.v)
    def eval(self, vars):
        i = vars.eval(self.i.i)
        v = vars.eval(self.v)
        vars.pending_set(i, v)
        return (self.i, self.v, i, v)

import rs274
def parse_lines(f, s=None):
    if s is None: s = open(f).read()
    if isinstance(s, (list,tuple)): s = "\n".join(s)
    parser = rs274.Rs274(rs274.Rs274Scanner(s))
    i = 0
    lines = []
    pos = 0
    while 1:
        try:
            l, pos = parser.line(pos)
            #print l, pos, len(parser.scanner.tokens), parser.scanner.tokens[-1]
        except rs274.SyntaxError, detail:
            print 'Syntax Error',detail.msg,'on line',1+i
            break
        except rs274.NoMoreTokens:
            print 'Ran out of input'
            break
        l.lineno = i+1
        l.filename = f
        lines.append(l)
        i += 1
        if parser.scanner.tokens[-1][1] == len(s):
            break
    return lines


# vim:sts=4:sw=4:et:
