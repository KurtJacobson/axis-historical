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

setup_menu_accel .menu.file 0 _Open

.menu.file add command \
	-accelerator Ctrl-R \
	-command reload_file \
	-label Reload \
	-underline 0

setup_menu_accel .menu.file 1 _Reload

.menu.file add separator


.menu.file add command \
	-accelerator F1 \
	-command estop_clicked \
	-label {Emergency Stop} \
	-underline 0

setup_menu_accel .menu.file 3 {_Emergency Stop}

.menu.file add command \
	-accelerator F2 \
	-command onoff_clicked \
	-label {Machine Power} \
	-underline 0

setup_menu_accel .menu.file 4 {_Machine Power}

.menu.file add separator


.menu.file add command \
	-command {destroy .} \
	-label Quit \
	-underline 0

setup_menu_accel .menu.file 6 _Quit

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

setup_menu_accel .menu.edit 0 _Copy

.menu.edit add separator


.menu.edit add command \
	-command set_view_z \
	-label {Top view} \
	-underline 0

setup_menu_accel .menu.edit 2 {_Top view}

.menu.edit add command \
	-command set_view_z2 \
	-label {Rotated Top view} \
	-underline 0

setup_menu_accel .menu.edit 3 {_Rotated Top view}

.menu.edit add command \
	-command set_view_x \
	-label {Side view} \
	-underline 0

setup_menu_accel .menu.edit 4 {_Side view}

.menu.edit add command \
	-command set_view_y \
	-label {Front view} \
	-underline 0

setup_menu_accel .menu.edit 5 {_Front view}

.menu.edit add separator


.menu.edit add checkbutton \
	-variable show_program \
	-label {Show program} \
	-underline 1

setup_menu_accel .menu.edit 7 {S_how program}

.menu.edit add checkbutton \
	-variable show_live_plot \
	-label {Show live plot} \
	-underline 3

setup_menu_accel .menu.edit 8 {Sho_w live plot}

.menu.edit add command \
	-command clear_live_plot \
	-label {Clear live plot} \
	-underline 1

setup_menu_accel .menu.edit 9 {C_lear live plot}

# Configure widget .menu.edit
wm title .menu.edit edit
wm resiz .menu.edit 1 1
wm minsize .menu.edit 1 1
wm maxsize .menu.edit 1585 1170

menu .menu.program \
	-tearoff 0

.menu.program add command \
	-command program_verify \
	-label {Verify program} \
	-underline 0

setup_menu_accel .menu.program 0 {_Verify program}

.menu.program add command \
	-command set_next_line \
	-label {Set next line} \
	-underline 4

.menu.program add command \
	-accelerator R \
	-command task_run \
	-label {Run program} \
	-underline 0

setup_menu_accel .menu.program 2 {_Run program}

.menu.program add command \
	-command task_step \
	-label Step \
	-underline 0

setup_menu_accel .menu.program 3 _Step

.menu.program add command \
	-accelerator P \
	-command task_pause \
	-label Pause \
	-underline 0

setup_menu_accel .menu.program 4 _Pause

.menu.program add command \
	-accelerator S \
	-command task_resume \
	-label Resume \
	-underline 2

setup_menu_accel .menu.program 5 Re_sume

.menu.program add command \
	-accelerator ESC \
	-command task_stop \
	-label Stop \
	-underline 1

setup_menu_accel .menu.program 6 S_top

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

setup_menu_accel .menu.help 0 {_About AXIS}

.menu.help add command \
	-command {wm deiconfiy .keys} \
	-label {Key Reference} \
	-underline 0 -state disabled

setup_menu_accel .menu.help 1 {_Key Reference}

# Configure widget .menu.help
wm title .menu.help help
wm resiz .menu.help 1 1
wm minsize .menu.help 1 1
wm maxsize .menu.help 1585 1170

.menu add cascade \
	-menu .menu.file \
	-label File \
	-underline 0

setup_menu_accel .menu 1 _File

.menu add cascade \
	-menu .menu.edit \
	-label Edit \
	-underline 0

setup_menu_accel .menu 2 _Edit

.menu add cascade \
	-menu .menu.program \
	-label Program \
	-underline 0

setup_menu_accel .menu 3 _Program

.menu add cascade \
	-menu .menu.help \
	-label Help \
	-underline 0

setup_menu_accel .menu 4 _Help

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
	-command estop_clicked \
	-helptext {Emergency Stop [F1]} \
	-image [load_image tool_estop] \
	-relief sunken \
	-takefocus 0
setup_widget_accel .toolbar.machine_estop {}

Button .toolbar.machine_power \
	-command onoff_clicked \
	-helptext {Turn machine on/off [F2]} \
	-image [load_image tool_power] \
	-relief link \
	-state disabled \
	-takefocus 0
setup_widget_accel .toolbar.machine_power {}

vrule .toolbar.rule0

Button .toolbar.file_open \
	-command { open_file } \
	-helptext {Open rs274ngc file [O]} \
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

Button .toolbar.verify \
	-command { program_verify } \
	-helptext {Verify validity of file} \
	-image [load_image tool_verify] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.verify {}

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
	-helptext {Execute next line} \
	-image [load_image tool_step] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.program_step {}

Button .toolbar.program_pause \
	-command task_pauseresume \
	-helptext {Pause program execution} \
	-image [load_image tool_pause] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.program_pause {}

Button .toolbar.program_stop \
	-command task_stop \
	-helptext {Stop program execution} \
	-image [load_image tool_stop] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.program_stop {}

vrule .toolbar.rule8

Button .toolbar.view_zoomin \
	-command zoomin \
	-helptext {Zoom in} \
	-image [load_image tool_zoomin] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.view_zoomin {}

Button .toolbar.view_zoomout \
	-command zoomout \
	-helptext {Zoom out} \
	-image [load_image tool_zoomout] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.view_zoomout {}

Button .toolbar.view_z \
	-command set_view_z \
	-helptext {Top view} \
	-image [load_image tool_axis_z] \
	-relief link \
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
	-helptext {Clear live plot} \
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

# Pack widget .toolbar.verify
pack .toolbar.verify \
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
bind .tabs.manual.jogf.jogminus <Button> {
    if {[is_continuous]} { jog_minus }
}
bind .tabs.manual.jogf.jogminus <ButtonRelease> {
    if {[is_continuous]} { jog_stop }
}
setup_widget_accel .tabs.manual.jogf.jogminus -

button .tabs.manual.jogf.jogplus \
	-command {if {![is_continuous]} {jog_plus}} \
	-padx 0 \
	-pady 0 \
	-width 2
bind .tabs.manual.jogf.jogplus <Button> {
    if {[is_continuous]} { jog_plus }
}
bind .tabs.manual.jogf.jogplus <ButtonRelease> {
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

button .tabs.manual.spindlef.spindleminus \
	-padx 0 \
	-pady 0 \
	-width 2
setup_widget_accel .tabs.manual.spindlef.spindleminus -
bind .tabs.manual.spindlef.spindleminus <ButtonPress> {
	if {[%W cget -state] == "disabled"} { continue }
	spindle_decrease
}
bind .tabs.manual.spindlef.spindleminus <ButtonRelease> {
	if {[%W cget -state] == "disabled"} { continue }
	spindle_constant
}
button .tabs.manual.spindlef.spindleplus \
	-padx 0 \
	-pady 0 \
	-width 2
setup_widget_accel .tabs.manual.spindlef.spindleplus +
bind .tabs.manual.spindlef.spindleplus <ButtonPress> {
	if {[%W cget -state] == "disabled"} { continue }
	spindle_increase
}
bind .tabs.manual.spindlef.spindleplus <ButtonRelease> {
	if {[%W cget -state] == "disabled"} { continue }
	spindle_constant
}

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

label .tabs.manual.lube
setup_widget_accel .tabs.manual.lube Lubricant:

checkbutton .tabs.manual.flood \
	-command flood \
	-variable flood
setup_widget_accel .tabs.manual.flood Flood

checkbutton .tabs.manual.mist \
	-command mist \
	-variable mist
setup_widget_accel .tabs.manual.mist Mist

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

# Grid widget .tabs.manual.flood
grid .tabs.manual.flood \
	-column 1 \
	-row 5 \
	-columnspan 2 \
	-padx 4 \
	-sticky w

# Grid widget .tabs.manual.jogf
grid .tabs.manual.jogf \
	-column 1 \
	-row 1 \
	-padx 4 \
	-sticky w

# Grid widget .tabs.manual.lube
grid .tabs.manual.lube \
	-column 0 \
	-row 5 \
	-sticky w

# Grid widget .tabs.manual.mist
grid .tabs.manual.mist \
	-column 1 \
	-row 6 \
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
	-state disabled \
	-width 40
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

label .tabs.mdi.gcodes \
	-anchor w \
	-borderwidth 2 \
	-justify left \
	-relief sunken \
	-textv active_codes

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
	-width 19
setup_widget_accel .info.position {Position: Commanded}

# Pack widget .info.task_state
pack .info.task_state \
	-side left

# Pack widget .info.tool
pack .info.tool \
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

entry .feedoverride.foentry \
	-textvariable feedrate \
	-width 3

scale .feedoverride.foscale \
	-orient horizontal \
	-showvalue 0 \
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
	-text {AXIS Copyright (C) 2004 Jeff Epler and Chris Radek.

This is free software, and you are welcome to redistribute it under certain conditions.  See the file COPYING, included with AXIS.
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
wm protocol .about WM_DELETE_WINDOW {wm wi .about}
wm title .about {About AXIS}
wm resiz .about 0 0
wm minsize .about 1 1
wm maxsize .about 1905 1170

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
