# Don't laugh -- this Python program prints a TCL script to fill out the
# key reference text widget

help = [
    ("F1", "Emergency stop"),
    ("F2", "Turn machine on"),
    ("", ""),
    ("X, `", "Select first axis"),
    ("Y, 1", "Select second axis"),
    ("Z, 2", "Select third axis"),
    ("A, 3", "Select fourth axis"),
    ("   4", "Select fifth axis"),
    ("   5", "Select sixth axis"),
    ("I", "Select jog increment"),
    ("C", "Continuous jog"),
    ("Home", "Send current axis home"),
    ("Shift-Home", "Set G54 offset for active axis"),
    ("Left, Right", "Jog first axis"),
    ("Up, Down", "Jog second axis"),
    ("Pg Up, Pg Dn", "Jog third axis"),
    ("[, ]", "Jog fourth axis"),
    ("", ""),
    ("F3", "Manual control"),
    ("F5", "Code entry"),
    ("", ""),
    ("O", "Open program"),
    ("R", "Run program"),
    ("T", "Step program"),
    ("P", "Pause program"),
    ("S", "Resume program"),
    ("ESC", "Stop program"),
    ("", ""),
    ("F7", "Toggle mist"),
    ("F8", "Toggle flood"),
    ("", ""),
    ("B", "Spindle brake off"),
    ("Shift-B", "Spindle brake on"),
    ("F9", "Turn spindle clockwise"),
    ("F10", "Turn spindle counterclockwise"),
    ("F11", "Turn spindle more slowly"),
    ("F12", "Turn spindle more quickly"),
    ("", ""),
    ("Control-K", "Clear live plot")
]

half = len(help)/2
odd = len(help)%2
form = r'.keys.text insert end {%s} key "\t" {} {%s} desc'
print ".keys.text configure -state normal"
print ".keys.text delete 0.0 end"
for i in range(half + odd):
    print form % help[i]
    if i + half < len(help): # +1 if item at 'half' is a spacer
        print r'.keys.text insert end "\t"'
        print form % help[i + half] # +1 if item at 'half' is a spacer
    print r'.keys.text insert end "\n"'
print ".keys.text configure -state disabled"
