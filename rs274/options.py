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

option add *Button.borderWidth 2 startupFile
option_nont add *Button.font $BASE_FONT

option add *Checkbutton.borderWidth 1 startupFile
option_nont add *Checkbutton.font $BASE_FONT

option add *Entry.background white startupFile
option add *Entry.borderWidth 2 startupFile
option_nont add *Entry.font $BASE_FONT
option add *Entry.selectBackground #08246b startupFile
option add *Entry.selectForeground white startupFile

option add *Frame.borderWidth 0 startupFile

option add *Hierbox.borderWidth 2 startupFile
option add *Hierbox.selectBackground #08246b startupFile
option add *Hierbox.selectForeground white startupFile

option_nont add *Label.font $BASE_FONT
option add *Label.borderWidth 1 startupFile

option add *Listbox.background white startupFile
option_nont add *Listbox.font $BASE_FONT
option add *Listbox.borderWidth 2 startupFile
option add *Listbox.selectBackground #08246b startupFile
option add *Listbox.selectForeground white startupFile

option add *Menu.activeBorderWidth 0 startupFile
option add *Menu.borderWidth 1 startupFile
option_nont add *Menu.font $BASE_FONT
option add *Menu.activeBackground #08246b startupFile
option add *Menu.activeForeground white startupFile

option add *Menubutton.borderWidth 1 startupFile
option_nont add *Menubutton.font $BASE_FONT
option add *Menubutton.indicatorOn 1 startupFile
option add *Menubutton.relief raised startupFile

option add *Message.borderWidth 1 startupFile
option_nont add *Message.font $BASE_FONT

option add *Radiobutton.borderWidth 1 startupFile
option_nont add *Radiobutton.font $BASE_FONT

option add *Scrollbar.borderWidth 2 startupFile
option add *Scrollbar.takeFocus 0 startupFile
option add *Scrollbar.troughColor #d9d9d9 startupFile
option add *Scrollbar.elementBorderWidth 2 startupFile

option add *Text.background white startupFile
option add *Text.borderWidth 2 startupFile
option_nont add *Text.font fixed
option add *Text.selectBackground #08246b startupFile
option add *Text.selectForeground white startupFile

option add *Labelframe.borderWidth 2 startupFile
option add *Labelframe.relief groove startupFile
option_nont add *Labelframe.font $BASE_FONT

option add *work.borderWidth 3 startupFile

option add *buttons*Button.default normal startupFile

option add *Vspace.height 6 startupFile

option add *Hspace.width 20 startupFile

option add *Vrule.borderWidth 1 startupFile
option add *Vrule.relief sunken startupFile
option add *Vrule.width 2 startupFile

option add *Hrule.borderWidth 1 startupFile
option add *Hrule.relief sunken startupFile
option add *Hrule.height 2 startupFile

option add *Togl.background #ffffff startupFile

option add *Togl.dwell #77cccc startupFile
option add *Togl.m1xx #cc7777 startupFile

option add *Togl.straight_feed #000000 startupFile
option add *Togl.arc_feed #330000 startupFile
option add *Togl.traverse #77cccc startupFile
option add *Togl.backplotjog yellow startupFile
option add *Togl.backplotfeed #444444 startupFile
option add *Togl.backplotarc #447777 startupFile
option add *Togl.backplottraverse #77cccc startupFile
option add *Togl.selected #0000ff startupFile

option add *Togl.overlay_foreground #000000 startupFile
option add *Togl.overlay_alpha .75 startupFile
option add *Togl.overlay_background #ffffff startupFile

option add *Togl.label_ok #555577 startupFile
option add *Togl.label_limit #cc5555 startupFile

option add *Togl.small_origin #007777 startupFile

option add *Togl.axis_x #333333 startupFile
option add *Togl.axis_y #333333 startupFile
option add *Togl.axis_z #333333 startupFile

option add *Togl.cone #cccccc startupFile
'''

def install(root = None):
    if root is None: root = Tkinter._default_root
    if hasattr(root, 'tk'): root = root.tk
    root.call('eval', options)
# vim:sw=4:sts=4:et:ts=8:
