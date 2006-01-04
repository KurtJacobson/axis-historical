#    This is a component of AXIS, a front-end for emc
#    Copyright 2004, 2005, 2006 Jeff Epler <jepler@unpythonic.net> and
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

setup_menu_accel .menu.file end [_ "_Open"]

.menu.file add command \
	-accelerator Ctrl-R \
	-command reload_file \
	-label Reload \
	-underline 0

setup_menu_accel .menu.file end [_ "_Reload"]

.menu.file add separator


.menu.file add command \
	-accelerator F1 \
	-command estop_clicked \
	-label {Toggle Emergency Stop} \
	-underline 7

setup_menu_accel .menu.file end [_ "Toggle _Emergency Stop"]

.menu.file add command \
	-accelerator F2 \
	-command onoff_clicked \
	-label {Toggle Machine Power} \
	-underline 7

setup_menu_accel .menu.file end [_ "Toggle _Machine Power"]

.menu.file add separator


.menu.file add command \
	-command {destroy .} \
	-label Quit \
	-underline 0

setup_menu_accel .menu.file end [_ "_Quit"]

# Configure widget .menu.file
wm title .menu.file file
wm iconname .menu.file {}
wm resiz .menu.file 1 1
wm minsize .menu.file 1 1

menu .menu.edit \
	-tearoff 0

.menu.edit add command \
	-accelerator Ctrl-C \
	-command copy_line \
	-label Copy \
	-underline 0

setup_menu_accel .menu.edit end [_ "_Copy"]

.menu.edit add separator


.menu.edit add command \
	-command set_view_z \
	-label {Top view} \
	-underline 0 \
	-accelerator V

setup_menu_accel .menu.edit end [_ "_Top view"]

.menu.edit add command \
	-command set_view_z2 \
	-label {Rotated Top view} \
	-underline 0 \
	-accelerator V

setup_menu_accel .menu.edit end [_ "_Rotated Top view"]

.menu.edit add command \
	-command set_view_x \
	-label {Side view} \
	-underline 0 \
	-accelerator V

setup_menu_accel .menu.edit end [_ "_Side view"]

.menu.edit add command \
	-command set_view_y \
	-label {Front view} \
	-underline 0 \
	-accelerator V

setup_menu_accel .menu.edit end [_ "_Front view"]

.menu.edit add command \
	-command set_view_p \
	-label {Perspective view} \
	-underline 0 \
	-accelerator V

setup_menu_accel .menu.edit end [_ "_Perspective view"]

.menu.edit add separator


.menu.edit add radiobutton \
	-value 0 \
	-variable metric \
	-command redraw \
	-label {Display Inches} \
	-underline 8

setup_menu_accel .menu.edit end [_ "Display _Inches"]

.menu.edit add radiobutton \
	-value 1 \
	-variable metric \
	-command redraw \
	-label {Display MM} \
	-underline 8

setup_menu_accel .menu.edit end [_ "Display _MM"]

.menu.edit add separator


.menu.edit add checkbutton \
	-variable show_program \
	-command redraw \
	-label {Show program} \
	-underline 1

setup_menu_accel .menu.edit end [_ "S_how program"]

.menu.edit add checkbutton \
	-variable show_live_plot \
	-command redraw \
	-label {Show live plot} \
	-underline 3

setup_menu_accel .menu.edit end [_ "Sho_w live plot"]

.menu.edit add checkbutton \
	-variable show_tool \
	-command redraw \
	-label {Show tool} \
	-underline 8

setup_menu_accel .menu.edit end [_ "Show too_l"]

.menu.edit add checkbutton \
	-variable show_extents \
	-command redraw \
	-label {Show extents} \
	-underline 6

setup_menu_accel .menu.edit end [_ "Show e_xtents"]

.menu.edit add command \
	-accelerator Ctrl-K \
	-command clear_live_plot \
	-label {Clear live plot} \
	-underline 1

setup_menu_accel .menu.edit end [_ "C_lear live plot"]

# Configure widget .menu.edit
wm title .menu.edit edit
wm iconname .menu.edit {}
wm resiz .menu.edit 1 1
wm minsize .menu.edit 1 1

menu .menu.program \
	-tearoff 0

.menu.program add command \
	-command set_next_line \
	-label {Set next line} \
	-underline 4

setup_menu_accel .menu.program end [_ "Set _next line"]

.menu.program add command \
	-accelerator R \
	-command task_run \
	-label {Run program} \
	-underline 0

setup_menu_accel .menu.program end [_ "_Run program"]

.menu.program add command \
	-accelerator T \
	-command task_step \
	-label Step \
	-underline 0

setup_menu_accel .menu.program end [_ "_Step"]

.menu.program add command \
	-accelerator P \
	-command task_pause \
	-label Pause \
	-underline 0

setup_menu_accel .menu.program end [_ "_Pause"]

.menu.program add command \
	-accelerator S \
	-command task_resume \
	-label Resume \
	-underline 2

setup_menu_accel .menu.program end [_ "Re_sume"]

.menu.program add command \
	-accelerator ESC \
	-command task_stop \
	-label Stop \
	-underline 1

setup_menu_accel .menu.program end [_ "S_top"]

# Configure widget .menu.program
wm title .menu.program program
wm iconname .menu.program {}
wm resiz .menu.program 1 1
wm minsize .menu.program 1 1

menu .menu.help \
	-tearoff 0

.menu.help add command \
	-command {wm transient .about .;wm deiconify .about; focus .about.ok} \
	-label {About AXIS} \
	-underline 0

setup_menu_accel .menu.help end [_ "_About AXIS"]

.menu.help add command \
	-command {wm transient .keys .;wm deiconify .keys; focus .keys.ok} \
	-label {Quick Reference} \
	-underline 6

setup_menu_accel .menu.help end [_ "Quick _Reference"]

# Configure widget .menu.help
wm title .menu.help help
wm iconname .menu.help {}
wm resiz .menu.help 1 1
wm minsize .menu.help 1 1

menu .menu.view \
	-tearoff 0

.menu.view add radiobutton \
	-value 1 \
	-variable display_type \
	-accelerator @ \
	-label {Show commanded position} \
	-command redraw

setup_menu_accel .menu.view end [_ "Show commanded position"]

.menu.view add radiobutton \
	-value 0 \
	-variable display_type \
	-accelerator @ \
	-label {Show actual position} \
	-command redraw

setup_menu_accel .menu.view end [_ "Show actual position"]

.menu.view add separator


.menu.view add radiobutton \
	-value 0 \
	-variable coord_type \
	-accelerator # \
	-label {Show machine position} \
	-command redraw

setup_menu_accel .menu.view end [_ "Show machine position"]

.menu.view add radiobutton \
	-value 1 \
	-variable coord_type \
	-accelerator # \
	-label {Show relative position} \
	-command redraw

setup_menu_accel .menu.view end [_ "Show relative position"]

.menu.view add separator

.menu.view add command \
	-label {Show EMC Status} \
	-command {exec $emctop_command -ini $emcini &}
setup_menu_accel .menu.view end [_ "Show _EMC Status"]

# Configure widget .menu.view
wm title .menu.view view
wm iconname .menu.view {}
wm resiz .menu.view 1 1
wm minsize .menu.view 1 1

.menu add cascade \
	-menu .menu.file \
	-label File \
	-underline 0

setup_menu_accel .menu end [_ _File]

.menu add cascade \
	-menu .menu.edit \
	-label Edit \
	-underline 0

setup_menu_accel .menu end [_ _Edit]

.menu add cascade \
	-menu .menu.program \
	-label Program \
	-underline 0

setup_menu_accel .menu end [_ _Program]

.menu add cascade \
	-menu .menu.view \
	-label View \
	-underline 0

setup_menu_accel .menu end [_ _View]

.menu add cascade \
	-menu .menu.help \
	-label Help \
	-underline 0

setup_menu_accel .menu end [_ _Help]

# Configure widget .menu
wm title .menu menu
wm iconname .menu {}
wm resiz .menu 1 1
wm minsize .menu 1 1

frame .toolbar \
	-borderwidth 1 \
	-relief raised

vrule .toolbar.rule16

Button .toolbar.machine_estop \
	-helptext [_ "Toggle Emergency Stop \[F1\]"] \
	-image [load_image tool_estop] \
	-relief sunken \
	-takefocus 0
bind .toolbar.machine_estop <Button-1> { estop_clicked }
setup_widget_accel .toolbar.machine_estop {}

Button .toolbar.machine_power \
	-command onoff_clicked \
	-helptext [_ "Toggle machine power \[F2\]"] \
	-image [load_image tool_power] \
	-relief link \
	-state disabled \
	-takefocus 0
setup_widget_accel .toolbar.machine_power {}

vrule .toolbar.rule0

Button .toolbar.file_open \
	-command { open_file } \
	-helptext [_ "Open G-Code file \[O\]"] \
	-image [load_image tool_open] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.file_open {}

Button .toolbar.reload \
	-command { reload_file } \
	-helptext [_ "Reopen current file \[Control-R\]"] \
	-image [load_image tool_reload] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.reload {}

vrule .toolbar.rule4

Button .toolbar.program_run \
	-command task_run \
	-helptext [_ "Begin executing current file \[R\]"] \
	-image [load_image tool_run] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.program_run {}

Button .toolbar.program_step \
	-command task_step \
	-helptext [_ "Execute next line \[T\]"] \
	-image [load_image tool_step] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.program_step {}

Button .toolbar.program_pause \
	-command task_pauseresume \
	-helptext [_ "Pause \[P\] / resume \[S\] execution"] \
	-image [load_image tool_pause] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.program_pause {}

Button .toolbar.program_stop \
	-command task_stop \
	-helptext [_ "Stop program execution \[ESC\]"] \
	-image [load_image tool_stop] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.program_stop {}

vrule .toolbar.rule8

Button .toolbar.view_zoomin \
	-command zoomin \
	-helptext [_ "Zoom in \[+\]"] \
	-image [load_image tool_zoomin] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.view_zoomin {}

Button .toolbar.view_zoomout \
	-command zoomout \
	-helptext [_ "Zoom out \[-\]"] \
	-image [load_image tool_zoomout] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.view_zoomout {}

Button .toolbar.view_z \
	-command set_view_z \
	-helptext [_ "Top view"] \
	-image [load_image tool_axis_z] \
	-relief sunken \
	-takefocus 0
setup_widget_accel .toolbar.view_z {}

Button .toolbar.view_z2 \
	-command set_view_z2 \
	-helptext [_ "Rotated top view"] \
	-image [load_image tool_axis_z2] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.view_z2 {}

Button .toolbar.view_x \
	-command set_view_x \
	-helptext [_ "Side view"] \
	-image [load_image tool_axis_x] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.view_x {}

Button .toolbar.view_y \
	-command set_view_y \
	-helptext [_ "Front view"] \
	-image [load_image tool_axis_y] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.view_y {}

Button .toolbar.view_p \
	-command set_view_p \
	-helptext [_ "Perspective view"] \
	-image [load_image tool_axis_p] \
	-relief link \
	-takefocus 0
setup_widget_accel .toolbar.view_p {}

vrule .toolbar.rule12

Button .toolbar.clear_plot \
	-command clear_live_plot \
	-helptext [_ "Clear live plot \[Ctrl-K\]"] \
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

PanedWindow .pane -side left -pad 1 -width 7

set pane_top [.pane add -weight 3]
set pane_bottom [.pane add -weight 1]

NoteBook ${pane_top}.tabs \
	-borderwidth 2 \
	-arcradius 3

set _tabs_manual [${pane_top}.tabs insert end manual -text [_ "Manual Control \[F3\]"] -raisecmd {focus .}]
set _tabs_mdi [${pane_top}.tabs insert end mdi -text [_ "Code Entry \[F5\]"]]
$_tabs_manual configure -borderwidth 2
$_tabs_mdi configure -borderwidth 2

${pane_top}.tabs itemconfigure mdi -raisecmd [list focus ${_tabs_mdi}.command]
${pane_top}.tabs raise manual
after idle ${pane_top}.tabs compute_size

label $_tabs_manual.axis
setup_widget_accel $_tabs_manual.axis [_ Axis:]

frame $_tabs_manual.axes

radiobutton $_tabs_manual.axes.axisx \
	-anchor w \
	-padx 0 \
	-selectcolor #4864ab \
	-value x \
	-variable current_axis \
	-width 2
setup_widget_accel $_tabs_manual.axes.axisx [_ _X]

radiobutton $_tabs_manual.axes.axisy \
	-anchor w \
	-padx 0 \
	-selectcolor #4864ab \
	-value y \
	-variable current_axis \
	-width 2
setup_widget_accel $_tabs_manual.axes.axisy [_ _Y]

radiobutton $_tabs_manual.axes.axisz \
	-anchor w \
	-padx 0 \
	-selectcolor #4864ab \
	-value z \
	-variable current_axis \
	-width 2
setup_widget_accel $_tabs_manual.axes.axisz [_ _Z]

radiobutton $_tabs_manual.axes.axisa \
	-anchor w \
	-padx 0 \
	-selectcolor #4864ab \
	-value a \
	-variable current_axis \
	-width 2
setup_widget_accel $_tabs_manual.axes.axisa [_ _A]

radiobutton $_tabs_manual.axes.axisb \
	-anchor w \
	-padx 0 \
	-selectcolor #4864ab \
	-value b \
	-variable current_axis \
	-width 2
setup_widget_accel $_tabs_manual.axes.axisb [_ _B]

radiobutton $_tabs_manual.axes.axisc \
	-anchor w \
	-padx 0 \
	-selectcolor #4864ab \
	-value c \
	-variable current_axis \
	-width 2
setup_widget_accel $_tabs_manual.axes.axisc [_ _C]

# Grid widget $_tabs_manual.axes.axisa
grid $_tabs_manual.axes.axisa \
	-column 0 \
	-row 1 \
	-padx 4

# Grid widget $_tabs_manual.axes.axisb
grid $_tabs_manual.axes.axisb \
	-column 1 \
	-row 1 \
	-padx 4

# Grid widget $_tabs_manual.axes.axisc
grid $_tabs_manual.axes.axisc \
	-column 2 \
	-row 1 \
	-padx 4

# Grid widget $_tabs_manual.axes.axisx
grid $_tabs_manual.axes.axisx \
	-column 0 \
	-row 0 \
	-padx 4

# Grid widget $_tabs_manual.axes.axisy
grid $_tabs_manual.axes.axisy \
	-column 1 \
	-row 0 \
	-padx 4

# Grid widget $_tabs_manual.axes.axisz
grid $_tabs_manual.axes.axisz \
	-column 2 \
	-row 0 \
	-padx 4

frame $_tabs_manual.jogf

button $_tabs_manual.jogf.jogminus \
	-command {if {![is_continuous]} {jog_minus}} \
	-padx 0 \
	-pady 0 \
	-width 2
bind $_tabs_manual.jogf.jogminus <Button-1> {
    if {[is_continuous]} { jog_minus }
}
bind $_tabs_manual.jogf.jogminus <ButtonRelease-1> {
    if {[is_continuous]} { jog_stop }
}
setup_widget_accel $_tabs_manual.jogf.jogminus [_ -]

button $_tabs_manual.jogf.jogplus \
	-command {if {![is_continuous]} {jog_plus}} \
	-padx 0 \
	-pady 0 \
	-width 2
bind $_tabs_manual.jogf.jogplus <Button-1> {
    if {[is_continuous]} { jog_plus }
}
bind $_tabs_manual.jogf.jogplus <ButtonRelease-1> {
    if {[is_continuous]} { jog_stop }
}
setup_widget_accel $_tabs_manual.jogf.jogplus [_ +]

combobox $_tabs_manual.jogf.jogspeed \
	-editable 0 \
	-textvariable jogincrement \
	-value [_ Continuous] \
	-width 10
$_tabs_manual.jogf.jogspeed list insert end [_ Continuous] 0.1000 0.0100 0.0010 0.0001

frame $_tabs_manual.jogf.zerohome

button $_tabs_manual.jogf.zerohome.home \
	-command home_axis \
	-padx 2m \
	-pady 0
setup_widget_accel $_tabs_manual.jogf.zerohome.home [_ Home]

button $_tabs_manual.jogf.zerohome.zero \
	-command set_axis_offset \
	-padx 2m \
	-pady 0
setup_widget_accel $_tabs_manual.jogf.zerohome.zero [_ Offset]

checkbutton $_tabs_manual.jogf.override \
	-command toggle_override_limits \
	-variable override_limits
setup_widget_accel $_tabs_manual.jogf.override [_ "Override Limits"]

grid $_tabs_manual.jogf.zerohome \
	-column 0 \
	-row 1 \
	-columnspan 3 \
	-sticky w

# Grid widget $_tabs_manual.jogf.zerohome.home
grid $_tabs_manual.jogf.zerohome.home \
	-column 0 \
	-row 0 \
	-ipadx 2 \
	-pady 2 \
	-sticky w

# Grid widget $_tabs_manual.jogf.zerohome.zero
grid $_tabs_manual.jogf.zerohome.zero \
	-column 1 \
	-row 0 \
	-ipadx 2 \
	-pady 2 \
	-sticky w

# Grid widget $_tabs_manual.jogf.override
grid $_tabs_manual.jogf.override \
	-column 0 \
	-row 3 \
	-columnspan 3 \
	-pady 2 \
	-sticky w

# Grid widget $_tabs_manual.jogf.jogminus
grid $_tabs_manual.jogf.jogminus \
	-column 0 \
	-row 0 \
	-pady 2 \
	-sticky ns

# Grid widget $_tabs_manual.jogf.jogplus
grid $_tabs_manual.jogf.jogplus \
	-column 1 \
	-row 0 \
	-pady 2 \
	-sticky ns

# Grid widget $_tabs_manual.jogf.jogspeed
grid $_tabs_manual.jogf.jogspeed \
	-column 2 \
	-row 0 \
	-pady 2

vspace $_tabs_manual.space1 \
	-height 12

label $_tabs_manual.spindlel
setup_widget_accel $_tabs_manual.spindlel [_ Spindle:]

frame $_tabs_manual.spindlef

radiobutton $_tabs_manual.spindlef.ccw \
	-borderwidth 2 \
	-command spindle \
	-image [load_image spindle_ccw] \
	-indicatoron 0 \
	-selectcolor [systembuttonface] \
	-value -1 \
	-variable spindledir
setup_widget_accel $_tabs_manual.spindlef.ccw {}

radiobutton $_tabs_manual.spindlef.stop \
	-borderwidth 2 \
	-command spindle \
	-indicatoron 0 \
	-selectcolor [systembuttonface] \
	-value 0 \
	-variable spindledir
setup_widget_accel $_tabs_manual.spindlef.stop [_ Stop]

radiobutton $_tabs_manual.spindlef.cw \
	-borderwidth 2 \
	-command spindle \
	-image [load_image spindle_cw] \
	-indicatoron 0 \
	-selectcolor [systembuttonface] \
	-value 1 \
	-variable spindledir
setup_widget_accel $_tabs_manual.spindlef.cw {}

button $_tabs_manual.spindlef.spindleminus \
	-padx 0 \
	-pady 0 \
	-width 2
bind $_tabs_manual.spindlef.spindleminus <Button-1> {
	if {[%W cget -state] == "disabled"} { continue }
	spindle_decrease
}
bind $_tabs_manual.spindlef.spindleminus <ButtonRelease-1> {
	if {[%W cget -state] == "disabled"} { continue }
	spindle_constant
}
setup_widget_accel $_tabs_manual.spindlef.spindleminus [_ -]

button $_tabs_manual.spindlef.spindleplus \
	-padx 0 \
	-pady 0 \
	-width 2
bind $_tabs_manual.spindlef.spindleplus <Button-1> {
	if {[%W cget -state] == "disabled"} { continue }
	spindle_increase
}
bind $_tabs_manual.spindlef.spindleplus <ButtonRelease-1> {
	if {[%W cget -state] == "disabled"} { continue }
	spindle_constant
}
setup_widget_accel $_tabs_manual.spindlef.spindleplus [_ +]

checkbutton $_tabs_manual.spindlef.brake \
	-command brake \
	-variable brake
setup_widget_accel $_tabs_manual.spindlef.brake [_ Brake]

# Grid widget $_tabs_manual.spindlef.brake
grid $_tabs_manual.spindlef.brake \
	-column 0 \
	-row 2 \
	-columnspan 3 \
	-pady 2 \
	-sticky w

# Grid widget $_tabs_manual.spindlef.ccw
grid $_tabs_manual.spindlef.ccw \
	-column 0 \
	-row 0 \
	-pady 2

# Grid widget $_tabs_manual.spindlef.cw
grid $_tabs_manual.spindlef.cw \
	-column 2 \
	-row 0 \
	-sticky w

# Grid widget $_tabs_manual.spindlef.spindleminus
grid $_tabs_manual.spindlef.spindleminus \
	-column 0 \
	-row 1 \
	-pady 2 \
	-sticky ns

# Grid widget $_tabs_manual.spindlef.spindleplus
grid $_tabs_manual.spindlef.spindleplus \
	-column 1 \
	-row 1 \
	-columnspan 2 \
	-pady 2 \
	-sticky nsw

# Grid widget $_tabs_manual.spindlef.stop
grid $_tabs_manual.spindlef.stop \
	-column 1 \
	-row 0 \
	-ipadx 8

vspace $_tabs_manual.space2 \
	-height 12

label $_tabs_manual.coolant
setup_widget_accel $_tabs_manual.coolant [_ Coolant:]

checkbutton $_tabs_manual.mist \
	-command mist \
	-variable mist
setup_widget_accel $_tabs_manual.mist [_ Mist]

checkbutton $_tabs_manual.flood \
	-command flood \
	-variable flood
setup_widget_accel $_tabs_manual.flood [_ Flood]

grid rowconfigure $_tabs_manual 99 -weight 1
grid columnconfigure $_tabs_manual 99 -weight 1
# Grid widget $_tabs_manual.axes
grid $_tabs_manual.axes \
	-column 1 \
	-row 0 \
	-padx 0 \
	-sticky w

# Grid widget $_tabs_manual.axis
grid $_tabs_manual.axis \
	-column 0 \
	-row 0 \
	-pady 1 \
	-sticky nw

# Grid widget $_tabs_manual.coolant
grid $_tabs_manual.coolant \
	-column 0 \
	-row 5 \
	-sticky w

# Grid widget $_tabs_manual.flood
grid $_tabs_manual.flood \
	-column 1 \
	-row 6 \
	-columnspan 2 \
	-padx 4 \
	-sticky w

# Grid widget $_tabs_manual.jogf
grid $_tabs_manual.jogf \
	-column 1 \
	-row 1 \
	-padx 4 \
	-sticky w

# Grid widget $_tabs_manual.mist
grid $_tabs_manual.mist \
	-column 1 \
	-row 5 \
	-columnspan 2 \
	-padx 4 \
	-sticky w

# Grid widget $_tabs_manual.space1
grid $_tabs_manual.space1 \
	-column 0 \
	-row 2

# Grid widget $_tabs_manual.space2
grid $_tabs_manual.space2 \
	-column 0 \
	-row 4

# Grid widget $_tabs_manual.spindlef
grid $_tabs_manual.spindlef \
	-column 1 \
	-row 3 \
	-padx 4 \
	-sticky w

# Grid widget $_tabs_manual.spindlel
grid $_tabs_manual.spindlel \
	-column 0 \
	-row 3 \
	-pady 2 \
	-sticky nw

label $_tabs_mdi.historyl
setup_widget_accel $_tabs_mdi.historyl [_ History:]

text $_tabs_mdi.history \
	-height 8 \
	-takefocus 0 \
	-width 40
$_tabs_mdi.history insert end {}
$_tabs_mdi.history configure -state disabled
grid rowconfigure $_tabs_mdi.history 0 -weight 1

vspace $_tabs_mdi.vs1 \
	-height 12

label $_tabs_mdi.commandl
setup_widget_accel $_tabs_mdi.commandl [_ "MDI Command:"]

entry $_tabs_mdi.command \
	-textvariable mdi_command
bind $_tabs_mdi.command <Key-Return> send_mdi

button $_tabs_mdi.go \
	-command send_mdi \
	-padx 1m \
	-pady 0
setup_widget_accel $_tabs_mdi.go [_ Go]

vspace $_tabs_mdi.vs2 \
	-height 12

label $_tabs_mdi.gcodel
setup_widget_accel $_tabs_mdi.gcodel [_ "Active G-Codes:"]

text $_tabs_mdi.gcodes \
	-height 2 \
	-width 20
$_tabs_mdi.gcodes insert end {}
$_tabs_mdi.gcodes configure -state disabled

vspace $_tabs_mdi.vs3 \
	-height 12

# Grid widget $_tabs_mdi.command
grid $_tabs_mdi.command \
	-column 0 \
	-row 4 \
	-sticky ew

# Grid widget $_tabs_mdi.commandl
grid $_tabs_mdi.commandl \
	-column 0 \
	-row 3 \
	-sticky w

# Grid widget $_tabs_mdi.gcodel
grid $_tabs_mdi.gcodel \
	-column 0 \
	-row 6 \
	-sticky w

# Grid widget $_tabs_mdi.gcodes
grid $_tabs_mdi.gcodes \
	-column 0 \
	-row 7 \
	-columnspan 2 \
	-sticky new

# Grid widget $_tabs_mdi.go
grid $_tabs_mdi.go \
	-column 1 \
	-row 4

# Grid widget $_tabs_mdi.history
grid $_tabs_mdi.history \
	-column 0 \
	-row 1 \
	-columnspan 2 \
	-sticky nesw

# Grid widget $_tabs_mdi.historyl
grid $_tabs_mdi.historyl \
	-column 0 \
	-row 0 \
	-sticky w

# Grid widget $_tabs_mdi.vs1
grid $_tabs_mdi.vs1 \
	-column 0 \
	-row 2

# Grid widget $_tabs_mdi.vs2
grid $_tabs_mdi.vs2 \
	-column 0 \
	-row 5

# Grid widget $_tabs_mdi.vs3
grid $_tabs_mdi.vs3 \
	-column 0 \
	-row 8
grid columnconfigure $_tabs_mdi 0 -weight 1
grid rowconfigure $_tabs_mdi 1 -weight 1

frame ${pane_top}.preview \
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

label .info.offset \
	-anchor w \
	-borderwidth 2 \
	-relief sunken \
	-textvariable offset \
	-width 25

label .info.position \
	-anchor w \
	-borderwidth 2 \
	-relief sunken \
	-textvariable position \
	-width 25

# Pack widget .info.task_state
pack .info.task_state \
	-side left

# Pack widget .info.tool
pack .info.tool \
	-side left

# Pack widget .info.position
pack .info.position \
	-side left

frame ${pane_bottom}.t \
	-borderwidth 2 \
	-relief sunken \
	-highlightthickness 1

text ${pane_bottom}.t.text \
	-borderwidth 0 \
	-exportselection 0 \
	-height 9 \
	-highlightthickness 0 \
	-relief flat \
	-takefocus 0 \
	-yscrollcommand [list ${pane_bottom}.t.sb set]
${pane_bottom}.t.text insert end {}

scrollbar ${pane_bottom}.t.sb \
	-borderwidth 0 \
	-command [list ${pane_bottom}.t.text yview] \
	-highlightthickness 0

# Pack widget ${pane_bottom}.t.text
pack ${pane_bottom}.t.text \
	-expand 1 \
	-fill both \
	-side left

# Pack widget ${pane_bottom}.t.sb
pack ${pane_bottom}.t.sb \
	-fill y \
	-side left

frame ${pane_top}.feedoverride

label ${pane_top}.feedoverride.foentry \
	-textvariable feedrate \
	-width 3
setup_widget_accel ${pane_top}.feedoverride.foentry [_ 0]

scale ${pane_top}.feedoverride.foscale \
	-command set_feedrate \
	-orient horizontal \
	-resolution 5.0 \
	-showvalue 0 \
	-takefocus 0 \
	-to 120.0 \
	-variable feedrate

label ${pane_top}.feedoverride.l
setup_widget_accel ${pane_top}.feedoverride.l [_ "Feed Override (%):"]

# Pack widget ${pane_top}.feedoverride.l
pack ${pane_top}.feedoverride.l \
	-side left

# Pack widget ${pane_top}.feedoverride.foentry
pack ${pane_top}.feedoverride.foentry \
	-side left

# Pack widget ${pane_top}.feedoverride.foscale
pack ${pane_top}.feedoverride.foscale \
	-expand 1 \
	-fill x \
	-side left

toplevel .about
bind .about <Key-Return> { wm wi .about }
bind .about <Key-Escape> { wm wi .about }

text .about.message \
	-background [systembuttonface] \
	-borderwidth 0 \
	-font {Helvetica -12} \
	-relief flat \
	-width 40 \
	-height 11 \
	-wrap word \
	-cursor {}

.about.message tag configure link \
	-underline 1 -foreground blue
.about.message tag bind link <Leave> {
	.about.message configure -cursor {}
	.about.message tag configure link -foreground blue}
.about.message tag bind link <Enter> {
	.about.message configure -cursor hand2
	.about.message tag configure link -foreground red}
.about.message tag bind link <ButtonPress-1><ButtonRelease-1> {launch_website}
.about.message insert end [_ "AXIS version 1.2a0\n\nCopyright (C) 2004, 2005, 2006 Jeff Epler and Chris Radek.\n\nThis is free software, and you are welcome to redistribute it under certain conditions.  See the file COPYING, included with AXIS.\n\nVisit the AXIS web site: "] {} {http://axis.unpy.net} link
.about.message configure -state disabled

button .about.ok \
	-command {wm wi .about} \
	-default active \
	-padx 0 \
	-pady 0 \
	-width 10
setup_widget_accel .about.ok [_ OK]

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
wm title .about [_ "About AXIS"]
wm iconname .about {}
wm resiz .about 0 0
wm minsize .about 1 1
wm protocol .about WM_DELETE_WINDOW {wm wi .about}

toplevel .keys
bind .keys <Key-Return> { wm withdraw .keys }
bind .keys <Key-Escape> { wm withdraw .keys }

text .keys.text \
	-background [systembuttonface] \
	-font {Helvetica -12} \
	-height 22 \
	-relief flat \
	-tabs {100 300 400} \
	-width 88 \
	-cursor {}

.keys.text tag configure key \
	-borderwidth {} \
	-elide {} \
	-font fixed

.keys.text configure -state disabled

button .keys.ok \
	-command {wm wi .keys} \
	-default active \
	-padx 0 \
	-pady 0 \
	-width 10
setup_widget_accel .keys.ok [_ OK]

# Pack widget .keys.text
pack .keys.text \
	-expand 1 \
	-fill y

# Pack widget .keys.ok
pack .keys.ok

# Configure widget .keys
wm title .keys [_ "AXIS Quick Reference"]
wm iconname .keys {}
wm resiz .keys 0 0
wm minsize .keys 1 1
wm protocol .keys WM_DELETE_WINDOW {wm wi .keys}

# Grid widget ${pane_top}.feedoverride
grid ${pane_top}.feedoverride \
	-column 0 \
	-row 2 \
	-sticky nw

grid .pane -column 0 -row 1 -columnspan 2 -sticky nsew
# Grid widget .info
grid .info \
	-column 0 \
	-row 4 \
	-columnspan 2 \
	-sticky ew

# Grid widget ${pane_top}.preview
grid ${pane_top}.preview \
	-column 1 \
	-row 1 \
	-columnspan 2 \
	-rowspan 2 \
	-sticky nesw

grid ${pane_top}.tabs \
	-column 0 \
	-row 1 \
	-sticky nesw \
	-padx 2 \
	-pady 2
grid rowconfigure ${pane_top} 1 -weight 1
grid columnconfigure ${pane_top} 1 -weight 1
grid ${pane_bottom}.t \
	-column 1 \
	-row 1 \
	-sticky nesw
grid rowconfigure ${pane_bottom} 1 -weight 1
grid columnconfigure ${pane_bottom} 1 -weight 1

after idle {
	Widget::setoption [winfo parent ${pane_top}] -minsize [winfo reqheight $pane_top]
	Widget::setoption [winfo parent ${pane_bottom}] -minsize [winfo reqheight $pane_bottom]
}

# Grid widget .toolbar
grid .toolbar \
	-column 0 \
	-row 0 \
	-columnspan 3 \
	-sticky nesw
grid columnconfigure . 1 -weight 1
grid rowconfigure . 1 -weight 1

# vim:ts=8:sts=8:noet:sw=8

set TASK_MODE_MANUAL 1
set TASK_MODE_AUTO 2
set TASK_MODE_MDI 3

set STATE_ESTOP 1
set STATE_ESTOP_RESET 2
set STATE_OFF 3
set STATE_ON 4

set INTERP_IDLE 1
set INTERP_READING 2
set INTERP_PAUSED 3
set INTERP_WAITING 4

set manual [concat [winfo children $_tabs_manual.axes] \
    $_tabs_manual.jogf.zerohome.home \
    $_tabs_manual.jogf.zerohome.zero \
    $_tabs_manual.jogf.jogminus \
    $_tabs_manual.jogf.jogplus \
    $_tabs_manual.jogf.jogspeed \
    $_tabs_manual.spindlef.cw $_tabs_manual.spindlef.ccw \
    $_tabs_manual.spindlef.stop $_tabs_manual.spindlef.brake \
    $_tabs_manual.flood $_tabs_manual.mist $_tabs_mdi.command \
    $_tabs_mdi.go]

proc disable_group {ws} { foreach w $ws { $w configure -state disabled } }
proc enable_group {ws} { foreach w $ws { $w configure -state normal } }

proc state {e args} {
    set e [uplevel \#0 [list expr $e]]
    if {$e} { set newstate normal } else {set newstate disabled}
    foreach w $args {
        if {[llength $w] == 2} {
            set idx [lindex $w 1]
            set w [lindex $w 0]
            # The indices are made for non-tearoff menus.  It's just
            # possible that the menus could be made to have tearoffs by
            # the X resources database.  This next line is supposed to
            # properly adjust the numbers for that case.
            if {[$w cget -tearoff]} { incr $idx }
            $w entryconfigure $idx -state $newstate
        } else {
            $w configure -state $newstate
        }
    }
}
proc relief {e args} {
    set e [uplevel \#0 [list expr $e]]
    if {$e} { set newstate sunken } else {set newstate link }
    foreach w $args { $w configure -relief $newstate }
}

proc update_title {args} {
    if {$::taskfile == ""} {
        wm ti . [_ "AXIS (No file)"]
        wm iconname . "AXIS"
    } else {
        wm ti . "[lindex [file split $::taskfile] end] - AXIS"
        wm iconname . "[lindex [file split $::taskfile] end]"
    }

}

proc update_state {args} {
    switch $::task_state \
        $::STATE_ESTOP { set ::task_state_string ESTOP } \
        $::STATE_ESTOP_RESET { set ::task_state_string {ESTOP RESET} } \
        $::STATE_ON { set ::task_state_string ON } \

    relief {$task_state == $STATE_ESTOP} .toolbar.machine_estop
    state  {$task_state != $STATE_ESTOP} .toolbar.machine_power 
    relief {$task_state == $STATE_ON}    .toolbar.machine_power 

    state  {$interp_state == $INTERP_IDLE} .toolbar.file_open {.menu.file 0}
    state  {$interp_state == $INTERP_IDLE && $taskfile != ""} \
                .toolbar.reload {.menu.file 1}

    state  {$task_state == $STATE_ON && $interp_state == $INTERP_IDLE \
            && $taskfile != ""} \
                .toolbar.program_run {.menu.program 1}
    relief {$interp_state != $INTERP_IDLE} .toolbar.program_run
    state  {$task_state == $STATE_ON && $taskfile != "" && \
      ($interp_state == $INTERP_PAUSED)} \
                .toolbar.program_step {.menu.program 2}
    state  {$task_state == $STATE_ON && \
      ($interp_state == $INTERP_READING || $interp_state == $INTERP_WAITING) } \
                {.menu.program 3}
    state  {$task_state == $STATE_ON && $interp_state == $INTERP_PAUSED } \
                {.menu.program 4}
    state  {$task_state == $STATE_ON && $interp_state != $INTERP_IDLE} \
                .toolbar.program_pause
    relief {$interp_state == $INTERP_PAUSED} \
                .toolbar.program_pause
    state  {$task_state == $STATE_ON && $interp_state != $INTERP_IDLE} \
                .toolbar.program_stop {.menu.program 5}
    relief {$interp_state == $INTERP_IDLE} \
                .toolbar.program_stop

    state {$running_line > 0 || $highlight_line > 0} {.menu.edit 0}
    state {$interp_state == $INTERP_IDLE && $highlight_line != -1} \
                {.menu.program 0}

    state {$::task_state == $::STATE_ON && $::interp_state == $::INTERP_IDLE\
            && $spindledir != 0} \
                $::_tabs_manual.spindlef.spindleminus \
                $::_tabs_manual.spindlef.spindleplus

    set coord_str [lindex [list [_ Machine] [_ Relative]] $::coord_type]
    set display_str [lindex [list [_ Actual] [_ Commanded]] $::display_type]
    set ::position [list [_ "Position:"] $coord_str $display_str]

    if {$::task_state == $::STATE_ON && $::interp_state == $::INTERP_IDLE} {
        enable_group $::manual
    } else {
        disable_group $::manual
    }
}

proc queue_update_state {args} { 
    after cancel update_state
    after idle update_state
}

set taskfile ""
set task_state -1
set task_mode -1
set interp_pause 0
set interp_state 0
set running_line -1
set highlight_line -1
set coord_type 1
set display_type 0
set spindledir {}
trace variable taskfile w update_title
trace variable taskfile w queue_update_state
trace variable task_state w queue_update_state
trace variable task_mode w queue_update_state
trace variable interp_pause w queue_update_state
trace variable interp_state w queue_update_state
trace variable running_line w queue_update_state
trace variable highlight_line w queue_update_state
trace variable spindledir w queue_update_state
trace variable coord_type w queue_update_state
trace variable display_type w queue_update_state

bind . <Control-Tab> {
    set page [.tabs raise]
    switch $page {
        mdi { .tabs raise manual }
        default { .tabs raise mdi }
    }
    break
}

# any key that causes an entry action should not continue to perform a
# binding on "."
foreach b [bind Entry] {
    switch -glob $b {
        <Shift-Key-*> - <Control-Key-*> -
        <Meta-Key-*> - <Alt-Key-*> {
            bind Entry $b {+if {[%W cget -state] == "normal"} break}
        }
    }
}
foreach b { <Key-Left> <Key-Right>
        <Key-Up> <Key-Down> <Key-Prior> <Key-Next> <Key-Home>
        <Left> <Right> <Up> <Down> <Prior> <Next> <Home> } {
    bind Entry $b {+if {[%W cget -state] == "normal"} break}
}
bind Entry <Key> {+if {[%W cget -state] == "normal" && [string length %A]} break}

proc is_continuous {} {
    expr {"[$::_tabs_manual.jogf.jogspeed get]" == [_ "Continuous"]}
}

proc delete_all text {
    set nl [lindex [split [$text index end] .] 0]
    while {$nl >= 1500} {
      puts "delete_all $nl"
      $text delete 1.0 1000.end
      incr nl -1000
    }

    $text delete 1.0 end
}

bind . <Configure> { if {"%W" == "."} {
    wm minsize %W [winfo reqwidth %W] [expr [winfo reqheight %W]+4] }
}

wm withdraw .about
wm withdraw .keys

DynamicHelp::add $_tabs_manual.spindlef.ccw -text [_ "Turn spindle counterclockwise \[F10\]"]
DynamicHelp::add $_tabs_manual.spindlef.cw -text [_ "Turn spindle clockwise \[F9\]"]
DynamicHelp::add $_tabs_manual.spindlef.stop -text [_ "Stop spindle \[F9/F10\]"]
DynamicHelp::add $_tabs_manual.spindlef.spindleplus -text [_ "Turn spindle Faster \[F12\]"]
DynamicHelp::add $_tabs_manual.spindlef.spindleminus -text [_ "Turn spindle Slower \[F11\]"]
DynamicHelp::add $_tabs_manual.spindlef.brake -text [_ "Turn spindle brake on \[Shift-B\] or off \[B\]"]
DynamicHelp::add $_tabs_manual.flood -text [_ "Turn flood on or off \[F8\]"]
DynamicHelp::add $_tabs_manual.mist -text [_ "Turn mist on or off \[F7\]"]
DynamicHelp::add $_tabs_manual.jogf.zerohome.home -text [_ "Send active axis home \[Home\]"]
DynamicHelp::add $_tabs_manual.jogf.zerohome.zero -text [_ "Set G54 offset for active axis \[Shift-Home\]"]
DynamicHelp::add $_tabs_manual.axes.axisx -text [_ "Activate axis \[X\]"]
DynamicHelp::add $_tabs_manual.axes.axisy -text [_ "Activate axis \[Y\]"]
DynamicHelp::add $_tabs_manual.axes.axisz -text [_ "Activate axis \[Z\]"]
DynamicHelp::add $_tabs_manual.axes.axisa -text [_ "Activate axis \[A\]"]
DynamicHelp::add $_tabs_manual.axes.axisb -text [_ "Activate axis \[4\]"]
DynamicHelp::add $_tabs_manual.axes.axisc -text [_ "Activate axis \[5\]"]
DynamicHelp::add $_tabs_manual.jogf.jogminus -text [_ "Jog selected axis"]
DynamicHelp::add $_tabs_manual.jogf.jogplus -text [_ "Jog selected axis"]
DynamicHelp::add $_tabs_manual.jogf.jogspeed -text [_ "Select jog ingrement"]
DynamicHelp::add $_tabs_manual.jogf.override -text [_ "Temporarily allow jogging outside machine limits \[L\]"]

# vim:ts=8:sts=4:et:
