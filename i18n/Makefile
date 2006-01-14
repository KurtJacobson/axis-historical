default: $(patsubst %.po, %.mo, $(wildcard *.po))

axis.pot: ../scripts/axis.py ../tcl/axis.tcl ../rs274/errorlist.py
	xgettext -k_ -o $@ $^

%.po: axis.pot
	[ -f $@ ] && (msgmerge -N --no-wrap -U $@ $< && touch $@) || cp $< $@

%.mo: %.po
	msgfmt -o $@ $<
