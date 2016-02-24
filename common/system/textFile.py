#!/bin/python
# -*- coding: utf-8 -*-
# ####################################################################
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
from common.system.file import File


class TextFile(File):

    def __init__(self, path, file_id):
        # example output:
        #   'ASCII text'
        self._path = path
        self._file_id = file_id
        if not self.magic_match(self._get_raw_type()):
            raise ValueError("Not a text file %s" % (path,))

    @classmethod
    def magic_match(cls, m):
        # we want to cover all text files (e.g. patches, specfiles, ...), so just grep for ASCII text
        return m.find('ASCII text') != -1

    def get_rpm_version(self):
        return self._type[1]

    def get_path(self):
        return self._path

    # TODO: distinguish diff/patch/spec/...
    def get_type(self):
        return 'text'

if __name__ == "__main__":
    sys.exit(1)