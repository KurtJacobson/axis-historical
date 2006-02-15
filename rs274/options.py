#!/usr/bin/env python
#    This is a component of AXIS, a front-end for emc
#    Copyright 2004, 2005, 2006 Jeff Epler <jepler@unpythonic.net>
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

options = '''
set BASE_FONT {Helvetica -12}

proc option_nont {args} {
    global tcl_platform
    if {$tcl_platform(platform) != "unix"} { return }
    eval [concat option $args]
}

option add *Button.borderWidth 1
option_nont add *Button.font $BASE_FONT

option add *Checkbutton.borderWidth 1
option_nont add *Checkbutton.font $BASE_FONT

option add *Entry.background white
option add *Entry.borderWidth 1
option_nont add *Entry.font $BASE_FONT
option add *Entry.selectBackground #08246b
option add *Entry.selectForeground white

option add *Frame.borderWidth 0

option add *Hierbox.borderWidth 1
option add *Hierbox.selectBackground #08246b
option add *Hierbox.selectForeground white

option_nont add *Label.font $BASE_FONT
option add *Label.borderWidth 1

option add *Listbox.background white
option_nont add *Listbox.font $BASE_FONT
option add *Listbox.borderWidth 1
option add *Listbox.selectBackground #08246b
option add *Listbox.selectForeground white

option add *Menu.activeBorderWidth 0
option add *Menu.borderWidth 1
option_nont add *Menu.font $BASE_FONT
option add *Menu.activeBackground #08246b
option add *Menu.activeForeground white

option add *Menubutton.borderWidth 1
option_nont add *Menubutton.font $BASE_FONT
option add *Menubutton.indicatorOn 1
option add *Menubutton.relief raised

option add *Message.borderWidth 1
option_nont add *Message.font $BASE_FONT

option add *Radiobutton.borderWidth 1
option_nont add *Radiobutton.font $BASE_FONT

option add *Scrollbar.width 10
option add *Scrollbar.borderWidth 1
option add *Scrollbar.takeFocus 0
option add *Scrollbar.troughColor #d9d9d9
option add *Scrollbar.elementBorderWidth 1

option add *Text.background white
option add *Text.borderWidth 1
option_nont add *Text.font fixed
option add *Text.selectBackground #08246b
option add *Text.selectForeground white

option add *Labelframe.borderWidth 1
option add *Labelframe.relief groove
option_nont add *Labelframe.font $BASE_FONT

option add *work.borderWidth 3

option add *buttons*Button.default normal

option add *Vspace.height 6

option add *Hspace.width 20

option add *Vrule.borderWidth 1
option add *Vrule.relief sunken
option add *Vrule.width 2

option add *Hrule.borderWidth 1
option add *Hrule.relief sunken
option add *Hrule.height 2

option add *Scale.borderWidth 1

option add *Combobox.borderWidth 1
'''

def install(root = None):
    if root is None: root = Tkinter._default_root
    if hasattr(root, 'tk'): root = root.tk
    root.call('eval', options)
# vim:sw=4:sts=4:et:ts=8:
