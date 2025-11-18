# Copyright 2005-2019 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

PYTHON = python


default: check


dist: setup.py
	$(PYTHON) setup.py sdist


check:
	tox


.PHONY: check default dist
