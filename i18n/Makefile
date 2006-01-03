default: $(patsubst %.po, %.mo, $(wildcard *.po))

axis.pot: ../scripts/axis.py ../tcl/axis.tcl ../rs274/errorlist.py
	xgettext -k_ -o $@ $^

%.po: axis.pot
	[ -f $@ ] && msgmerge -U $@ $< || cp $< $@

%.mo: %.po
	msgfmt -o $@ $<
