# -*- coding: utf-8 -*-
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

namespace eval ::nf {}
set ::nf::saveroot .
set ::nf::procs {}
set ::nf::vars {task_state_text tool offset ngcfile position}
set task_state_text {ESTOP RESET}
set tool {Tool 0, offset 0.250, radius 0.03125}
set offset {Work offset 0.000 0.000 0.000}
set position {Position: Commanded}

. configure \
	-menu .menu

menu .menu \
	-cursor {}

menu .menu.file \
	-tearoff 0

.menu.file add command \
	-accelerator O \
	-command open_file \
	-label Open \
	-underline 0

setup_menu_accel .menu.file end _Open

.menu.file add command \
	-accelerator Ctrl-R \
	-command reload_file \
	-label Reload \
	-underline 0

setup_menu_accel .menu.file end _Reload

.menu.file add separator


.menu.file add command \
	-accelerator F1 \
	-command estop_clicked \
	-label {Toggle Emergency Stop} \
	-underline 7

setup_menu_accel .menu.file end {Toggle _Emergency Stop}

.menu.file add command \
	-accelerator F2 \
	-command onoff_clicked \
	-label {Toggle Machine Power} \
	-underline 7

setup_menu_accel .menu.file end {Toggle _Machine Power}

.menu.file add separator


.menu.file add command \
	-command {destroy .} \
	-label Quit \
	-underline 0

setup_menu_accel .menu.file end _Quit

# Configure widget .menu.file
wm title .menu.file file
wm resiz .menu.file 1 1
wm minsize .menu.file 1 1
wm maxsize .menu.file 1585 1170

menu .menu.edit \
	-tearoff 0

.menu.edit add command \
	-accelerator Ctrl-C \
	-command copy_line \
	-label Copy \
	-underline 0

setup_menu_accel .menu.edit end _Copy

.menu.edit add separator


.menu.edit add command \
	-command set_view_z \
	-label {Top view} \
	-underline 0

setup_menu_accel .menu.edit end {_Top view}

.menu.edit add command \
	-command set_view_z2 \
	-label {Rotated Top view} \
	-underline 0

setup_menu_accel .menu.edit end {_Rotated Top view}

.menu.edit add command \
	-command set_view_x \
	-label {Side view} \
	-underline 0

setup_menu_accel .menu.edit end {_Side view}

.menu.edit add command \
	-command set_view_y \
	-label {Front view} \
	-underline 0

setup_menu_accel .menu.edit end {_Front view}

.menu.edit add command \
	-command set_view_p \
	-label {Perspective view} \
	-underline 0

setup_menu_accel .menu.edit end {_Perspective view}

.menu.edit add separator


.menu.edit add radiobutton \
	-value 0 \
	-variable metric \
	-command redraw \
	-label {Display Inches} \
	-underline 8

setup_menu_accel .menu.edit end {Display _Inches}

.menu.edit add radiobutton \
	-value 1 \
	-variable metric \
	-command redraw \
	-label {Display MM} \
	-underline 8

setup_menu_accel .menu.edit end {Display _MM}

.menu.edit add separator


.menu.edit add checkbutton \
	-variable show_program \
	-command redraw \
	-label {Show program} \
	-underline 1

setup_menu_accel .menu.edit end {S_how program}

.menu.edit add checkbutton \
	-variable show_live_plot \
	-command redraw \
	-label {Show live plot} \
	-underline 3

setup_menu_accel .menu.edit end {Sho_w live plot}

.menu.edit add checkbutton \
	-variable show_tool \
	-command redraw \
	-label {Show tool} \
	-underline 8

setup_menu_accel .menu.edit end {Show too_l}

.menu.edit add command \
	-accelerator Ctrl-K \
	-command clear_live_plot \
	-label {Clear live plot} \
	-underline 1

setup_menu_accel .menu.edit end {C_lear live plot}

# Configure widget .menu.edit
wm title .menu.edit edit
wm resiz .menu.edit 1 1
wm minsize .menu.edit 1 1
wm maxsize .menu.edit 1585 1170

menu .menu.program \
	-tearoff 0

.menu.program add command \
	-command set_next_line \
	-label {Set next line} \
	-underline 4

setup_menu_accel .menu.program end {Set _next line}

.menu.program add command \
	-accelerator R \
	-command task_run \
	-label {Run program} \
	-underline 0

setup_menu_accel .menu.program end {_Run program}

.menu.program add command \
	-accelerator T \
	-command task_step \
	-label Step \
	-underline 0

setup_menu_accel .menu.program end _Step

.menu.program add command \
	-accelerator P \
	-command task_pause \
	-label Pause \
	-underline 0

setup_menu_accel .menu.program end _Pause

.menu.program add command \
	-accelerator S \
	-command task_resume \
	-label Resume \
	-underline 2

setup_menu_accel .menu.program end Re_sume

.menu.program add command \
	-accelerator ESC \
	-command task_stop \
	-label Stop \
	-underline 1

setup_menu_accel .menu.program end S_top

# Configure widget .menu.program
wm title .menu.program program
wm resiz .menu.program 1 1
wm minsize .menu.program 1 1
wm maxsize .menu.program 1905 1170

menu .menu.help \
	-tearoff 0

.menu.help add command \
	-command {wm transient .about .;wm deiconify .about} \
	-label {About AXIS} \
	-underline 0

setup_menu_accel .menu.help end {_About AXIS}

.menu.help add command \
	-command {wm transient .keys .;wm deiconify .keys} \
	-label {Key Reference} \
	-underline 0

setup_menu_accel .menu.help end {_Key Reference}

.menu.help add command \
	-command {wm transient .mouse .;wm deiconify .mouse} \
	-label Navigation \
	-underline 0

setup_menu_accel .menu.help end _Navigation

# Configure widget .menu.help
wm title .menu.help help
wm resiz .menu.help 1 1
wm minsize .menu.help 1 1
wm maxsize .menu.help 1585 1170

menu .menu.view \
	-tearoff 0

.menu.view add radiobutton \
	-value 1 \
	-variable display_type \
	-label {Show commanded position} \
	-accel {@}


setup_menu_accel .menu.view end {Show commanded position}

.menu.view add radiobutton \
	-value 0 \
	-variable display_type \
	-label {Show actual position} \
	-accel {@}


setup_menu_accel .menu.view end {Show actual position}

.menu.view add separator


.menu.view add radiobutton \
	-value 1 \
	-variable coord_type \
	-label {Show machine position} \
	-accel {#}

setup_menu_accel .menu.view end {Show machine position}

.menu.view add radiobutton \
	-value 0 \
	-variable coord_type \
	-label {Show relative position} \
	-accel {#}


setup_menu_accel .menu.view end {Show relative position}

# Configure widget .menu.view
wm title .menu.view view
wm resiz .menu.view 1 1
wm minsize .menu.view 1 1
wm maxsize .menu.view 1905 1170

.menu add cascade \
	-menu .menu.file \
	-label File \
	-underline 0

setup_menu_accel .menu end _File

.menu add cascade \
	-menu .menu.edit \
	-label Edit \
	-underline 0

setup_menu_accel .menu end _Edit

.menu add cascade \
	-menu .menu.program \
	-label Program \
	-underline 0

setup_menu_accel .menu end _Program

.menu add cascade \
	-menu .menu.help \
	-label Help \
	-underline 0

setup_menu_accel .menu end _Help

.menu add cascade \
	-menu .menu.view \
	-label View \
	-underline 0

setup_menu_accel .menu end _View

# Configure widget .menu
wm title .menu menu
wm resiz .menu 1 1
wm minsize .menu 1 1
wm maxsize .menu 1585 1170

frame .toolbar \
	-borderwidth 1 \
	-relief raised

vrule .toolbar.rule16

Button .toolbar.machine_estop \
	-helptext {Toggle Emergency Stop [F1]} \
	-image [load_image tool_estop] \
	-relief sunken \
	-takefocus 0
bind .toolbar.machine_estop <Button-1> { estop_clicked }
setup_widget_accel .toolbar.machine_estop {}

Button .toolbar.machine_power \
	-command onoff_clicked \
	-helptext {Toggle machine power [F2]} \
	-image [load_image tool_power] \
	-relief link \
	-state disabled \
	-takefocus 0
setup_widget_accel .toolbar.machine_power {}

vrule .toolbar.rule0

Button .toolbar.file_open \
	-command { open_file } \
	-helptext {Open G-Code file [O]} \
	-image [load_image tool_open] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.file_open {}

Button .toolbar.reload \
	-command { reload_file } \
	-helptext {Reopen current file [Control-R]} \
	-image [load_image tool_reload] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.reload {}

vrule .toolbar.rule4

Button .toolbar.program_run \
	-command task_run \
	-helptext {Begin executing current file} \
	-image [load_image tool_run] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.program_run {}

Button .toolbar.program_step \
	-command task_step \
	-helptext {Execute next line [T]} \
	-image [load_image tool_step] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.program_step {}

Button .toolbar.program_pause \
	-command task_pauseresume \
	-helptext {Pause [P] / resume [S] execution} \
	-image [load_image tool_pause] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.program_pause {}

Button .toolbar.program_stop \
	-command task_stop \
	-helptext {Stop program execution [ESC]} \
	-image [load_image tool_stop] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.program_stop {}

vrule .toolbar.rule8

Button .toolbar.view_zoomin \
	-command zoomin \
	-helptext {Zoom in [+]} \
	-image [load_image tool_zoomin] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.view_zoomin {}

Button .toolbar.view_zoomout \
	-command zoomout \
	-helptext {Zoom out [-]} \
	-image [load_image tool_zoomout] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.view_zoomout {}

Button .toolbar.view_z \
	-command set_view_z \
	-helptext {Top view} \
	-image [load_image tool_axis_z] \
	-relief sunken \
	-takefocus 0
setup_widget_accel .toolbar.view_z {}

Button .toolbar.view_z2 \
	-command set_view_z2 \
	-helptext {Rotated top view} \
	-image [load_image tool_axis_z2] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.view_z2 {}

Button .toolbar.view_x \
	-command set_view_x \
	-helptext {Side view} \
	-image [load_image tool_axis_x] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.view_x {}

Button .toolbar.view_y \
	-command set_view_y \
	-helptext {Front view} \
	-image [load_image tool_axis_y] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.view_y {}

Button .toolbar.view_p \
	-command set_view_p \
	-helptext {Perspective view} \
	-image [load_image tool_axis_p] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.view_p {}

vrule .toolbar.rule12

Button .toolbar.clear_plot \
	-command clear_live_plot \
	-helptext {Clear live plot [Ctrl-K]} \
	-image [load_image tool_clear] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.clear_plot {}

# Pack widget .toolbar.machine_estop
pack .toolbar.machine_estop \
	-side left

# Pack widget .toolbar.machine_power
pack .toolbar.machine_power \
	-side left

# Pack widget .toolbar.rule0
pack .toolbar.rule0 \
	-fill y \
	-padx 4 \
	-pady 4 \
	-side left

# Pack widget .toolbar.file_open
pack .toolbar.file_open \
	-side left

# Pack widget .toolbar.reload
pack .toolbar.reload \
	-side left

# Pack widget .toolbar.rule4
pack .toolbar.rule4 \
	-fill y \
	-padx 4 \
	-pady 4 \
	-side left

# Pack widget .toolbar.program_run
pack .toolbar.program_run \
	-side left

# Pack widget .toolbar.program_step
pack .toolbar.program_step \
	-side left

# Pack widget .toolbar.program_pause
pack .toolbar.program_pause \
	-side left

# Pack widget .toolbar.program_stop
pack .toolbar.program_stop \
	-side left

# Pack widget .toolbar.rule8
pack .toolbar.rule8 \
	-fill y \
	-padx 4 \
	-pady 4 \
	-side left

# Pack widget .toolbar.view_zoomin
pack .toolbar.view_zoomin \
	-side left

# Pack widget .toolbar.view_zoomout
pack .toolbar.view_zoomout \
	-side left

# Pack widget .toolbar.view_z
pack .toolbar.view_z \
	-side left

# Pack widget .toolbar.view_z2
pack .toolbar.view_z2 \
	-side left

# Pack widget .toolbar.view_x
pack .toolbar.view_x \
	-side left

# Pack widget .toolbar.view_y
pack .toolbar.view_y \
	-side left

# Pack widget .toolbar.view_p
pack .toolbar.view_p \
	-side left

# Pack widget .toolbar.rule12
pack .toolbar.rule12 \
	-fill y \
	-padx 4 \
	-pady 4 \
	-side left

# Pack widget .toolbar.clear_plot
pack .toolbar.clear_plot \
	-side left

tabset .tabs \
	-borderwidth 2 \
	-gap 0 \
	-highlightthickness 0 \
	-outerpad 2 \
	-perforationcommand {
	blt::Tearoff %W $bltTabset(x) $bltTabset(y) select
    } \
	-relief flat \
	-samewidth 0 \
	-scrollincrement 2 \
	-selectpad 4 \
	-takefocus 0 \
	-tearoff 0

tab .tabs.manual

label .tabs.manual.axis
setup_widget_accel .tabs.manual.axis Axis:

frame .tabs.manual.axes

radiobutton .tabs.manual.axes.axisx \
	-anchor w \
	-padx 0 \
	-selectcolor #4864ab \
	-value x \
	-variable current_axis \
	-width 2
setup_widget_accel .tabs.manual.axes.axisx _X

radiobutton .tabs.manual.axes.axisy \
	-anchor w \
	-padx 0 \
	-selectcolor #4864ab \
	-value y \
	-variable current_axis \
	-width 2
setup_widget_accel .tabs.manual.axes.axisy _Y

radiobutton .tabs.manual.axes.axisz \
	-anchor w \
	-padx 0 \
	-selectcolor #4864ab \
	-value z \
	-variable current_axis \
	-width 2
setup_widget_accel .tabs.manual.axes.axisz _Z

radiobutton .tabs.manual.axes.axisa \
	-anchor w \
	-padx 0 \
	-selectcolor #4864ab \
	-value a \
	-variable current_axis \
	-width 2
setup_widget_accel .tabs.manual.axes.axisa _A

radiobutton .tabs.manual.axes.axisb \
	-anchor w \
	-padx 0 \
	-selectcolor #4864ab \
	-value b \
	-variable current_axis \
	-width 2
setup_widget_accel .tabs.manual.axes.axisb _B

radiobutton .tabs.manual.axes.axisc \
	-anchor w \
	-padx 0 \
	-selectcolor #4864ab \
	-value c \
	-variable current_axis \
	-width 2
setup_widget_accel .tabs.manual.axes.axisc _C

# Grid widget .tabs.manual.axes.axisa
grid .tabs.manual.axes.axisa \
	-column 0 \
	-row 1 \
	-padx 4

# Grid widget .tabs.manual.axes.axisb
grid .tabs.manual.axes.axisb \
	-column 1 \
	-row 1 \
	-padx 4

# Grid widget .tabs.manual.axes.axisc
grid .tabs.manual.axes.axisc \
	-column 2 \
	-row 1 \
	-padx 4

# Grid widget .tabs.manual.axes.axisx
grid .tabs.manual.axes.axisx \
	-column 0 \
	-row 0 \
	-padx 4

# Grid widget .tabs.manual.axes.axisy
grid .tabs.manual.axes.axisy \
	-column 1 \
	-row 0 \
	-padx 4

# Grid widget .tabs.manual.axes.axisz
grid .tabs.manual.axes.axisz \
	-column 2 \
	-row 0 \
	-padx 4

frame .tabs.manual.jogf

button .tabs.manual.jogf.jogminus \
	-command {if {![is_continuous]} {jog_minus}} \
	-padx 0 \
	-pady 0 \
	-width 2
bind .tabs.manual.jogf.jogminus <Button-1> {
    if {[is_continuous]} { jog_minus }
}
bind .tabs.manual.jogf.jogminus <ButtonRelease-1> {
    if {[is_continuous]} { jog_stop }
}
setup_widget_accel .tabs.manual.jogf.jogminus -

button .tabs.manual.jogf.jogplus \
	-command {if {![is_continuous]} {jog_plus}} \
	-padx 0 \
	-pady 0 \
	-width 2
bind .tabs.manual.jogf.jogplus <Button-1> {
    if {[is_continuous]} { jog_plus }
}
bind .tabs.manual.jogf.jogplus <ButtonRelease-1> {
    if {[is_continuous]} { jog_stop }
}
setup_widget_accel .tabs.manual.jogf.jogplus +

combobox .tabs.manual.jogf.jogspeed \
	-editable 0 \
	-textvariable jogincrement \
	-value Continuous \
	-width 10
.tabs.manual.jogf.jogspeed list insert end Continuous 0.10000 0.01000 0.00100 0.00010

button .tabs.manual.jogf.button \
	-command home_axis \
	-padx 2m \
	-pady 0
setup_widget_accel .tabs.manual.jogf.button Home

# Grid widget .tabs.manual.jogf.button
grid .tabs.manual.jogf.button \
	-column 0 \
	-row 1 \
	-columnspan 3 \
	-ipadx 2 \
	-pady 2 \
	-sticky w

# Grid widget .tabs.manual.jogf.jogminus
grid .tabs.manual.jogf.jogminus \
	-column 0 \
	-row 0 \
	-pady 2 \
	-sticky ns

# Grid widget .tabs.manual.jogf.jogplus
grid .tabs.manual.jogf.jogplus \
	-column 1 \
	-row 0 \
	-pady 2 \
	-sticky ns

# Grid widget .tabs.manual.jogf.jogspeed
grid .tabs.manual.jogf.jogspeed \
	-column 2 \
	-row 0 \
	-pady 2

vspace .tabs.manual.space1 \
	-height 16

label .tabs.manual.spindlel
setup_widget_accel .tabs.manual.spindlel Spindle:

frame .tabs.manual.spindlef

radiobutton .tabs.manual.spindlef.ccw \
	-borderwidth 2 \
	-command spindle \
	-image [load_image spindle_ccw] \
	-indicatoron 0 \
	-selectcolor [systembuttonface] \
	-value -1 \
	-variable spindledir
setup_widget_accel .tabs.manual.spindlef.ccw {}

radiobutton .tabs.manual.spindlef.stop \
	-borderwidth 2 \
	-command spindle \
	-indicatoron 0 \
	-selectcolor [systembuttonface] \
	-value 0 \
	-variable spindledir
setup_widget_accel .tabs.manual.spindlef.stop Stop

radiobutton .tabs.manual.spindlef.cw \
	-borderwidth 2 \
	-command spindle \
	-image [load_image spindle_cw] \
	-indicatoron 0 \
	-selectcolor [systembuttonface] \
	-value 1 \
	-variable spindledir
setup_widget_accel .tabs.manual.spindlef.cw {}

button .tabs.manual.spindlef.spindleminus \
	-padx 0 \
	-pady 0 \
	-width 2
bind .tabs.manual.spindlef.spindleminus <Button-1> {
	if {[%W cget -state] == "disabled"} { continue }
	spindle_decrease
}
bind .tabs.manual.spindlef.spindleminus <ButtonRelease-1> {
	if {[%W cget -state] == "disabled"} { continue }
	spindle_constant
}
setup_widget_accel .tabs.manual.spindlef.spindleminus -

button .tabs.manual.spindlef.spindleplus \
	-padx 0 \
	-pady 0 \
	-width 2
bind .tabs.manual.spindlef.spindleplus <Button-1> {
	if {[%W cget -state] == "disabled"} { continue }
	spindle_increase
}
bind .tabs.manual.spindlef.spindleplus <ButtonRelease-1> {
	if {[%W cget -state] == "disabled"} { continue }
	spindle_constant
}
setup_widget_accel .tabs.manual.spindlef.spindleplus +

checkbutton .tabs.manual.spindlef.brake \
	-command brake \
	-variable brake
setup_widget_accel .tabs.manual.spindlef.brake Brake

# Grid widget .tabs.manual.spindlef.brake
grid .tabs.manual.spindlef.brake \
	-column 0 \
	-row 2 \
	-columnspan 3 \
	-pady 2 \
	-sticky w

# Grid widget .tabs.manual.spindlef.ccw
grid .tabs.manual.spindlef.ccw \
	-column 0 \
	-row 0 \
	-pady 2

# Grid widget .tabs.manual.spindlef.cw
grid .tabs.manual.spindlef.cw \
	-column 2 \
	-row 0

# Grid widget .tabs.manual.spindlef.spindleminus
grid .tabs.manual.spindlef.spindleminus \
	-column 0 \
	-row 1 \
	-pady 2 \
	-sticky ns

# Grid widget .tabs.manual.spindlef.spindleplus
grid .tabs.manual.spindlef.spindleplus \
	-column 1 \
	-row 1 \
	-columnspan 2 \
	-pady 2 \
	-sticky nsw

# Grid widget .tabs.manual.spindlef.stop
grid .tabs.manual.spindlef.stop \
	-column 1 \
	-row 0 \
	-ipadx 8

vspace .tabs.manual.space2 \
	-height 16

label .tabs.manual.coolant
setup_widget_accel .tabs.manual.coolant Coolant:

checkbutton .tabs.manual.mist \
	-command mist \
	-variable mist
setup_widget_accel .tabs.manual.mist Mist

checkbutton .tabs.manual.flood \
	-command flood \
	-variable flood
setup_widget_accel .tabs.manual.flood Flood

# Grid widget .tabs.manual.axes
grid .tabs.manual.axes \
	-column 1 \
	-row 0 \
	-padx 4 \
	-sticky w

# Grid widget .tabs.manual.axis
grid .tabs.manual.axis \
	-column 0 \
	-row 0 \
	-pady 1 \
	-sticky nw

# Grid widget .tabs.manual.coolant
grid .tabs.manual.coolant \
	-column 0 \
	-row 5 \
	-sticky w

# Grid widget .tabs.manual.flood
grid .tabs.manual.flood \
	-column 1 \
	-row 6 \
	-columnspan 2 \
	-padx 4 \
	-sticky w

# Grid widget .tabs.manual.jogf
grid .tabs.manual.jogf \
	-column 1 \
	-row 1 \
	-padx 4 \
	-sticky w

# Grid widget .tabs.manual.mist
grid .tabs.manual.mist \
	-column 1 \
	-row 5 \
	-columnspan 2 \
	-padx 4 \
	-sticky w

# Grid widget .tabs.manual.space1
grid .tabs.manual.space1 \
	-column 0 \
	-row 2

# Grid widget .tabs.manual.space2
grid .tabs.manual.space2 \
	-column 0 \
	-row 4

# Grid widget .tabs.manual.spindlef
grid .tabs.manual.spindlef \
	-column 1 \
	-row 3 \
	-padx 4 \
	-sticky w

# Grid widget .tabs.manual.spindlel
grid .tabs.manual.spindlel \
	-column 0 \
	-row 3 \
	-pady 2 \
	-sticky nw

tab .tabs.mdi

label .tabs.mdi.historyl
setup_widget_accel .tabs.mdi.historyl History:

text .tabs.mdi.history \
	-height 8 \
	-takefocus 0 \
	-width 40
.tabs.mdi.history insert end {}
.tabs.mdi.history configure -state disabled
grid rowconfigure .tabs.mdi.history 0 -weight 1

vspace .tabs.mdi.vs1 \
	-height 16

label .tabs.mdi.commandl
setup_widget_accel .tabs.mdi.commandl {MDI Command:}

entry .tabs.mdi.command \
	-textvariable mdi_command
bind .tabs.mdi.command <Key-Return> send_mdi

button .tabs.mdi.go \
	-command send_mdi \
	-padx 1m \
	-pady 0
setup_widget_accel .tabs.mdi.go Go

vspace .tabs.mdi.vs2 \
	-height 16

label .tabs.mdi.gcodel
setup_widget_accel .tabs.mdi.gcodel {Active G-Codes:}

text .tabs.mdi.gcodes \
	-borderwidth 2 \
	-relief sunken -height 2 -width 20

vspace .tabs.mdi.vs3 \
	-height 16

# Grid widget .tabs.mdi.command
grid .tabs.mdi.command \
	-column 0 \
	-row 4 \
	-sticky ew

# Grid widget .tabs.mdi.commandl
grid .tabs.mdi.commandl \
	-column 0 \
	-row 3 \
	-sticky w

# Grid widget .tabs.mdi.gcodel
grid .tabs.mdi.gcodel \
	-column 0 \
	-row 6 \
	-sticky w

# Grid widget .tabs.mdi.gcodes
grid .tabs.mdi.gcodes \
	-column 0 \
	-row 7 \
	-columnspan 2 \
	-sticky new

# Grid widget .tabs.mdi.go
grid .tabs.mdi.go \
	-column 1 \
	-row 4

# Grid widget .tabs.mdi.history
grid .tabs.mdi.history \
	-column 0 \
	-row 1 \
	-columnspan 2 \
	-sticky nesw

# Grid widget .tabs.mdi.historyl
grid .tabs.mdi.historyl \
	-column 0 \
	-row 0 \
	-sticky w

# Grid widget .tabs.mdi.vs1
grid .tabs.mdi.vs1 \
	-column 0 \
	-row 2

# Grid widget .tabs.mdi.vs2
grid .tabs.mdi.vs2 \
	-column 0 \
	-row 5

# Grid widget .tabs.mdi.vs3
grid .tabs.mdi.vs3 \
	-column 0 \
	-row 8
grid columnconfigure .tabs.mdi 0 -weight 1
grid rowconfigure .tabs.mdi 1 -weight 1

.tabs insert end manual
.tabs tab config manual \
	-anchor nw \
	-ipadx {0 0} \
	-ipady {0 0} \
	-padx {0 0} \
	-pady {0 0} \
	-text {Manual Control [F3]} \
	-window .tabs.manual


.tabs insert end mdi
.tabs tab config mdi \
	-anchor nw \
	-fill y \
	-ipadx {0 0} \
	-ipady {0 0} \
	-padx {0 0} \
	-pady {0 0} \
	-text {Code Entry [F5]} \
	-window .tabs.mdi


frame .preview \
	-background black \
	-height 300 \
	-width 400

frame .info

label .info.task_state \
	-anchor w \
	-borderwidth 2 \
	-relief sunken \
	-textvariable task_state_string \
	-width 14
setup_widget_accel .info.task_state {}

label .info.tool \
	-anchor w \
	-borderwidth 2 \
	-relief sunken \
	-textvariable tool \
	-width 30
setup_widget_accel .info.tool {Tool 0, offset 0.250, radius 0.03125}

label .info.offset \
	-anchor w \
	-borderwidth 2 \
	-relief sunken \
	-textvariable offset \
	-width 25
setup_widget_accel .info.offset {Work offset 0.000 0.000 0.000}

label .info.position \
	-anchor w \
	-borderwidth 2 \
	-relief sunken \
	-textvariable position \
	-width 25
setup_widget_accel .info.position {Position: Commanded}

# Pack widget .info.task_state
pack .info.task_state \
	-side left

# Pack widget .info.tool
pack .info.tool \
	-side left

# Pack widget .info.position
pack .info.position \
	-side left

frame .t \
	-borderwidth 2 \
	-relief sunken \
	-highlightthickness 1

text .t.text \
	-borderwidth 0 \
	-exportselection 0 \
	-height 9 \
	-highlightthickness 0 \
	-relief flat \
	-takefocus 0 \
	-yscrollcommand {.t.sb set}
.t.text insert end {}

scrollbar .t.sb \
	-borderwidth 0 \
	-command {.t.text yview} \
	-highlightthickness 0

# Pack widget .t.text
pack .t.text \
	-expand 1 \
	-fill both \
	-side left

# Pack widget .t.sb
pack .t.sb \
	-fill y \
	-side left

frame .feedoverride

label .feedoverride.foentry \
	-textvariable feedrate \
	-width 3
setup_widget_accel .feedoverride.foentry 0

scale .feedoverride.foscale \
	-command set_feedrate \
	-orient horizontal \
	-resolution 5.0 \
	-showvalue 0 \
	-takefocus 0 \
	-to 120.0 \
	-variable feedrate

label .feedoverride.l
setup_widget_accel .feedoverride.l {Feed Override (%):}

# Pack widget .feedoverride.l
pack .feedoverride.l \
	-side left

# Pack widget .feedoverride.foentry
pack .feedoverride.foentry \
	-side left

# Pack widget .feedoverride.foscale
pack .feedoverride.foscale \
	-expand 1 \
	-fill x \
	-side left

toplevel .about
bind .about <Key-Return> { wm wi .about }

message .about.message \
	-borderwidth 0 \
	-text {AXIS version 1.0b1

Copyright (C) 2004 Jeff Epler and Chris Radek.

This is free software, and you are welcome to redistribute it under certain conditions.  See the file COPYING, included with AXIS.

Visit the AXIS web site at http://axis.unpy.net
} \
	-width 300

button .about.ok \
	-command {wm wi .about} \
	-default active \
	-padx 0 \
	-pady 0 \
	-width 10
setup_widget_accel .about.ok OK

label .about.image \
	-borderwidth 0 \
	-image [load_image banner]
setup_widget_accel .about.image {}

# Pack widget .about.image
pack .about.image

# Pack widget .about.message
pack .about.message \
	-expand 1 \
	-fill both

# Pack widget .about.ok
pack .about.ok

# Configure widget .about
wm title .about {About AXIS}
wm resiz .about 0 0
wm minsize .about 1 1
wm maxsize .about 1905 1170
wm protocol .about WM_DELETE_WINDOW {wm wi .about}

toplevel .mouse
bind .mouse <Key-Return> { wm withdraw .mouse }

text .mouse.text \
	-background [systembuttonface] \
	-font {Helvetica -12} \
	-height 5 \
	-relief flat \
	-tabs 100 \
	-width 30
.mouse.text insert end {  Left Button	Pan view
Middle Button	Rotate view
 Right Button	Zoom view
}
.mouse.text tag configure key \
	-borderwidth {} \
	-elide {} \
	-font fixed

.mouse.text tag add key 1.0 1.13 2.0 2.13 3.0 3.13
.mouse.text tag configure desc \
	-borderwidth {} \
	-elide {}

.mouse.text tag add desc 1.14 1.22 2.14 2.25 3.14 3.23

button .mouse.ok \
	-command {wm wi .mouse} \
	-default active \
	-padx 0 \
	-pady 0 \
	-width 10
setup_widget_accel .mouse.ok OK

# Pack widget .mouse.text
pack .mouse.text \
	-expand 1 \
	-fill y

# Pack widget .mouse.ok
pack .mouse.ok

# Configure widget .mouse
wm title .mouse {AXIS Navigation}
wm resiz .mouse 0 0
wm minsize .mouse 1 1
wm maxsize .mouse 1905 1170
wm protocol .mouse WM_DELETE_WINDOW {wm wi .mouse}

toplevel .keys
bind .keys <Key-Return> { wm withdraw .keys }

text .keys.text \
	-background [systembuttonface] \
	-font {Helvetica -12} \
	-height 22 \
	-relief flat \
	-tabs {100 300 400} \
	-width 88
.keys.text insert end {F1	Toggle Emergency stop	O	Open program
F2	Turn machine on	R	Run program
		T	Step program
X, `	Select first axis	P	Pause program
Y, 1	Select second axis	S	Resume program
Z, 2	Select third axis	ESC	Stop program
A, 3	Select fourth axis		
   4	Select fifth axis	F7	Toggle mist
   5	Select sixth axis	F8	Toggle flood
I	Select jog increment		
C	Continuous jog	B	Spindle brake off
Home	Send current axis home	Shift-B	Spindle brake on
Left, Right	Jog first axis	F9	Turn spindle clockwise
Up, Down	Jog second axis	F10	Turn spindle counterclockwise
Pg Up, Pg Dn	Jog third axis	F11	Turn spindle more slowly
[, ]	Jog fourth axis	F12	Turn spindle more quickly
			
F3	Manual control	Control-K	Clear live plot
F5	Code entry
}
.keys.text tag configure key \
	-borderwidth {} \
	-elide {} \
	-font fixed

.keys.text tag add key 1.0 1.2 1.25 1.26 2.0 2.2 2.19 2.20 3.2 3.3 4.0 4.4 4.23 4.24 5.0 5.4 5.24 5.25 6.0 6.4 6.23 6.26 7.0 7.4 8.0 8.4 8.23 8.25 9.0 9.4 9.23 9.25 10.0 10.1 11.0 11.1 11.17 11.18 12.0 12.4 12.28 12.35 13.0 13.11 13.27 13.29 14.0 14.8 14.25 14.28 15.0 15.12 15.28 15.31 16.0 16.4 16.21 16.24 18.0 18.2 18.18 18.27 19.0 19.2
.keys.text tag configure desc \
	-borderwidth {} \
	-elide {}

.keys.text tag add desc 1.3 1.24 1.27 1.39 2.3 2.18 2.21 2.32 3.4 3.16 4.5 4.22 4.25 4.38 5.5 5.23 5.26 5.40 6.5 6.22 6.27 6.39 7.5 7.23 8.5 8.22 8.26 8.37 9.5 9.22 9.26 9.38 10.2 10.22 11.2 11.16 11.19 11.36 12.5 12.27 12.36 12.52 13.12 13.26 13.30 13.52 14.9 14.24 14.29 14.58 15.13 15.27 15.32 15.56 16.5 16.20 16.25 16.50 18.3 18.17 18.28 18.43 19.3 19.13

button .keys.ok \
	-command {wm wi .keys} \
	-default active \
	-padx 0 \
	-pady 0 \
	-width 10
setup_widget_accel .keys.ok OK

# Pack widget .keys.text
pack .keys.text \
	-expand 1 \
	-fill y

# Pack widget .keys.ok
pack .keys.ok

# Configure widget .keys
wm title .keys {AXIS key reference}
wm resiz .keys 0 0
wm minsize .keys 1 1
wm maxsize .keys 1905 1170
wm protocol .keys WM_DELETE_WINDOW {wm wi .keys}

# Grid widget .feedoverride
grid .feedoverride \
	-column 0 \
	-row 2 \
	-sticky nw

# Grid widget .info
grid .info \
	-column 0 \
	-row 4 \
	-columnspan 2 \
	-sticky w

# Grid widget .preview
grid .preview \
	-column 1 \
	-row 1 \
	-columnspan 2 \
	-rowspan 2 \
	-sticky nesw

# Grid widget .t
grid .t \
	-column 0 \
	-row 3 \
	-columnspan 2 \
	-sticky nesw

# Grid widget .tabs
grid .tabs \
	-column 0 \
	-row 1 \
	-sticky nesw

# Grid widget .toolbar
grid .toolbar \
	-column 0 \
	-row 0 \
	-columnspan 3 \
	-sticky nesw
grid columnconfigure . 1 -weight 1
grid rowconfigure . 1 -weight 1

# Configure widget .
wm title . {AXIS (no file)}
wm resiz . 1 1
wm minsize . 656 511
wm maxsize . 1009 738

# vim:ts=8:sts=8:noet:sw=8
