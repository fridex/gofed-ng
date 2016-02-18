#!/bin/python
# gofed-ng - Golang system
# Copyright (C) 2016  Fridolin Pokorny, fpokorny@redhat.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# ####################################################################

import sys


class TestConfig(object):

    def __init__(self):
        raise NotImplementedError("Not implemented constructor")

    def _repre(self):
        raise NotImplementedError("Not implemented method")

    def _conf2str(self):
        ret = "[" + self._repre() + "]\n"
        for key in self._config:
            ret += key + ' = ' + self._config[key] + "\n"

    def clear(self):
        self._config = {}

    def write(self, path):
        with open(path, 'w') as f:
            f.write(self._conf2str())
        self._path = path

    def set(self, key, val):
        self._config[key] = val

    def get_path(self):
        return self._path

if __name__ == "__main__":
    sys.exit(1)
