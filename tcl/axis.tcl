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
    .tabs.manual.spindlef.spindleminus .tabs.manual.spindlef.spindleplus \
    .tabs.manual.spindlef.cw .tabs.manual.spindlef.ccw \
    .tabs.manual.spindlef.stop .tabs.manual.spindlef.brake \
    .tabs.manual.flood .tabs.manual.mist .tabs.mdi.history .tabs.mdi.command \
    .tabs.mdi.go]

proc disable_group {ws} { foreach w $ws { $w configure -state disabled } }
proc enable_group {ws} { foreach w $ws { $w configure -state normal } }

proc state {e args} {
    set e [uplevel \#0 [list expr $e]]
    if {$e} { set newstate normal } else {set newstate disabled}
    foreach w $args { $w configure -state $newstate }
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

    state  {$interp_state == $INTERP_IDLE} .toolbar.file_open
    state  {$interp_state == $INTERP_IDLE && $taskfile != ""} .toolbar.reload
    state  {$task_state == $STATE_ON && $interp_state == $INTERP_IDLE \
            && $taskfile != ""} \
                .toolbar.verify

    state  {$task_state == $STATE_ON && $interp_state == $INTERP_IDLE \
            && $taskfile != ""} \
                .toolbar.program_run
    relief {$interp_state != $INTERP_IDLE} .toolbar.program_run
    state  {$task_state == $STATE_ON && $taskfile != "" && \
      ($interp_state == $INTERP_IDLE != 2 || $interp_state == $INTERP_PAUSED)} \
                .toolbar.program_step
    state  {$task_state == $STATE_ON && $interp_state != $INTERP_IDLE} \
                .toolbar.program_pause
    relief {$interp_state == $INTERP_PAUSED} \
                .toolbar.program_pause
    state  {$task_state == $STATE_ON && $interp_state != $INTERP_IDLE} \
                .toolbar.program_stop
    relief {$interp_state == $INTERP_IDLE} \
                .toolbar.program_stop

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
trace variable taskfile w queue_update_state
trace variable task_state w queue_update_state
trace variable task_mode w queue_update_state
trace variable interp_pause w queue_update_state
trace variable interp_state w queue_update_state

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
