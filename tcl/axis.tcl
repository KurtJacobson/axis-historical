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

set manual [concat [winfo children .tabs.manual.axes] \
    [winfo children .tabs.manual.jogf] \
    .tabs.manual.spindlef.cw .tabs.manual.spindlef.ccw \
    .tabs.manual.spindlef.stop .tabs.manual.spindlef.brake \
    .tabs.manual.flood .tabs.manual.mist .tabs.mdi.history .tabs.mdi.command \
    .tabs.mdi.go]

proc disable_group {ws} { foreach w $ws { $w configure -state disabled } }
proc enable_group {ws} { foreach w $ws { $w configure -state normal } }

proc state {e args} {
    set e [uplevel \#0 [list expr $e]]
    if {$e} { set newstate normal } else {set newstate disabled}
    foreach w $args {
        if {[llength $w] == 2} {
            set idx [lindex $w 1]
            set w [lindex $w 0]
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

proc update_state {args} {
    if {$::taskfile == ""} {
        wm ti . "AXIS (No file)"
    } else {
        wm ti . "$::taskfile - AXIS"
    }

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
                .toolbar.verify {.menu.program 0}

    state  {$task_state == $STATE_ON && $interp_state == $INTERP_IDLE \
            && $taskfile != ""} \
                .toolbar.program_run {.menu.program 2}
    relief {$interp_state != $INTERP_IDLE} .toolbar.program_run
    state  {$task_state == $STATE_ON && $taskfile != "" && \
      ($interp_state == $INTERP_PAUSED)} \
                .toolbar.program_step {.menu.program 3}
    state  {$task_state == $STATE_ON && \
      ($interp_state == $INTERP_READING || $interp_state == $INTERP_WAITING) } \
                {.menu.program 4}
    state  {$task_state == $STATE_ON && $interp_state == $INTERP_PAUSED } \
                {.menu.program 5}
    state  {$task_state == $STATE_ON && $interp_state != $INTERP_IDLE} \
                .toolbar.program_pause
    relief {$interp_state == $INTERP_PAUSED} \
                .toolbar.program_pause
    state  {$task_state == $STATE_ON && $interp_state != $INTERP_IDLE} \
                .toolbar.program_stop {.menu.program 6}
    relief {$interp_state == $INTERP_IDLE} \
                .toolbar.program_stop

    state {$running_line != -1 || $highlight_line != -1} {.menu.edit 0}
    state {$interp_state == $INTERP_IDLE && $highlight_line != -1} \
                {.menu.program 1}

    puts [list spindledir = $::spindledir [expr $::spindledir != 0]]
    state {$::task_state == $::STATE_ON && $::interp_state == $::INTERP_IDLE\
            && $spindledir != 0} .tabs.manual.spindlef.spindleminus \
        .tabs.manual.spindlef.spindleplus

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
set spindledir {}
trace variable taskfile w queue_update_state
trace variable task_state w queue_update_state
trace variable task_mode w queue_update_state
trace variable interp_pause w queue_update_state
trace variable interp_state w queue_update_state
trace variable running_line w queue_update_state
trace variable highlight_line w queue_update_state
trace variable spindledir w queue_update_state

bind . <Control-Tab> {
    set l [llength [.tabs tab names]]
    set i [.tabs index select]
    set i [expr {($i+1)%%$l}]
    .tabs select $i
    if {$i == 1} { focus .tabs.mdi.command } else { focus . }
    break
}

# any key that causes an entry action should not continue to perform a
# binding on "."
foreach b [bind Entry] {
    switch -glob $b {
        <Shift-Key-*> - <Control-Key-*> -
        <Meta-Key-*> - <Alt-Key-*> - <Left> - <Right> -
        <Up> - <Down> - <Prior> - <Next> - <Home> {
            bind Entry $b +break
        }
    }
}

proc is_continuous {} {
    expr {"[.tabs.manual.jogf.jogspeed get]" == "Continuous"}
}

bind Entry <Key> {+if {[string length %A]} break}

bind . <Configure> { if {"%W" == "."} {
    wm minsize %W [winfo reqwidth %W] [winfo reqheight %W] }
}
#after idle { wm minsize . [winfo reqwidth .] [winfo reqheight .] }
wm maxsize . [winfo screenwidth .] [winfo screenheight .]

wm withdraw .about
