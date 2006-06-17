default: $(patsubst %.po, %.mo, $(wildcard *.po))

axis.pot: ../scripts/axis.py ../tcl/axis.tcl
	xgettext -k_ -o $@ $^

%.po: axis.pot
	if [ -f $@ ]; \
	then \
	    msgmerge --no-wrap -U $@ $< && touch $@; \
	else \
	    cp $< $@; \
	fi

%.mo: %.po
	msgfmt -o $@ $<
