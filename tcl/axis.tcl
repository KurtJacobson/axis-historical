#    This is a component of AXIS, a front-end for emc
#    Copyright 2004, 2005 Jeff Epler <jepler@unpythonic.net> and
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
    $_tabs_manual.jogf.override \
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
        wm ti . "AXIS (No file)"
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

    set ::position [list Position: [lindex {Machine Relative} $::coord_type] \
                                   [lindex {Actual Commanded} $::display_type]]

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
    expr {"[$::_tabs_manual.jogf.jogspeed get]" == "Continuous"}
}


bind . <Configure> { if {"%W" == "."} {
    wm minsize %W [winfo reqwidth %W] [expr [winfo reqheight %W]+4] }
}

wm withdraw .about
wm withdraw .keys

DynamicHelp::add $_tabs_manual.spindlef.ccw -text {Turn spindle counterclockwise [F10]}
DynamicHelp::add $_tabs_manual.spindlef.cw -text {Turn spindle clockwise [F9]}
DynamicHelp::add $_tabs_manual.spindlef.stop -text {Stop spindle [F9/F10]}
DynamicHelp::add $_tabs_manual.spindlef.spindleplus -text {Turn spindle Faster [F12]}
DynamicHelp::add $_tabs_manual.spindlef.spindleminus -text {Turn spindle Slower [F11]}
DynamicHelp::add $_tabs_manual.spindlef.brake -text {Turn spindle brake on [Shift-B] or off [B]}
DynamicHelp::add $_tabs_manual.flood -text {Turn flood on or off [F8]}
DynamicHelp::add $_tabs_manual.mist -text {Turn mist on or off [F7]}
DynamicHelp::add $_tabs_manual.jogf.zerohome.home -text {Send active axis home [Home]}
DynamicHelp::add $_tabs_manual.jogf.zerohome.zero -text {Set G54 offset for active axis [Shift-Home]}
DynamicHelp::add $_tabs_manual.axes.axisx -text {Activate axis [X]}
DynamicHelp::add $_tabs_manual.axes.axisy -text {Activate axis [Y]}
DynamicHelp::add $_tabs_manual.axes.axisz -text {Activate axis [Z]}
DynamicHelp::add $_tabs_manual.axes.axisa -text {Activate axis [A]}
DynamicHelp::add $_tabs_manual.axes.axisb -text {Activate axis [4]}
DynamicHelp::add $_tabs_manual.axes.axisc -text {Activate axis [5]}
DynamicHelp::add $_tabs_manual.jogf.jogminus -text {Jog selected axis}
DynamicHelp::add $_tabs_manual.jogf.jogplus -text {Jog selected axis}
DynamicHelp::add $_tabs_manual.jogf.jogspeed -text {Select jog ingrement}
DynamicHelp::add $_tabs_manual.jogf.override -text {Temporarily allow jogging outside machine limits [L]}

# vim:ts=8:sts=4:et:
