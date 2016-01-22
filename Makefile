# Makefile for gofed-ng
# 2016 Fridolin Pokorny <fpokorny@redhat.com>

all:
	python bootstrap.py

clean:
	rm -f system.py
	rm -rf DOC/
	rm -f gofed.conf
	find . -name '*.pyc' -exec rm -f {} +
	find services/ -name '*.conf' -exec rm -f {} +
	find services/ -name '*Service.py' -exec rm -f {} +
	find services/ -name 'common' -xtype d -exec rm -rf {} +
	find services/ -name 'keys' -type d -exec rm -rf {} +

pack: clean
	tar -zcvf *

doc:
	@epydoc --graph all -o DOC/ common/ plugins/ scenarios/ services gofed.py registry.py -v && \
		echo "Documentation created, see 'DOC/' dir..."

FORCE:

