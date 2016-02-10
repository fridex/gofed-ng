# Makefile for gofed-ng
# 2016 Fridolin Pokorny <fpokorny@redhat.com>

all: submodules
	python bootstrap.py

submodules:
	git submodule init
	> services/spec/specker/__init__.py

clean:
	rm -rf DOC/
	rm -f gofed.conf
	rm -f system.json
	rm -f scenarios/load_scenarios.py
	find . -name '*.pyc' -exec rm -f {} +
	find services/ -name 'common' -xtype d -exec rm -rf {} +
	find services/ -name 'service.conf' -xtype f -exec rm -rf {} +
	find services/ -name 'system.json' -xtype f -exec rm -rf {} +

pack: clean
	tar -zcvf *

update: update-system-json

update-system-json: all
	scp system.json fedora@209.132.179.123:~

update-status-json:
	gofed system --status > status.json
	scp status.json fedora@209.132.179.123:~

doc:
	@epydoc --graph all -o DOC/ common/ plugins/ scenarios/ services gofed.py registry.py system.py -v && \
		echo "Documentation created, see 'DOC/' dir..."

FORCE:

