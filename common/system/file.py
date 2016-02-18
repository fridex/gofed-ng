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
import magic


class File(object):

    def __init__(self, path, file_id):
        self._path = path
        self._file_id = file_id
        raise NotImplementedError()

    @staticmethod
    def get_representation(path, file_id):
        m = magic.from_file(path)

        if RpmFile.magic_match(m):
            return RpmFile(path, file_id)
        elif SrpmFile.magic_match(m):
            return SrpmFile(path, file_id)
        elif TarballFile.magic_match(m):
            return TarballFile(path, file_id)
        else:
            raise ValueError("Unknown file with magic %s", (m,))

    @classmethod
    def magic_match(cls, m):
        raise NotImplementedError

    def get_path(self):
        self._path

    def get_type(self):
        raise NotImplementedError()

    def _get_raw_type(self):
        return magic.from_file(self._path)

# Fix circular deps
from common.system.rpmFile import RpmFile
from common.system.srpmFile import SrpmFile
from common.system.tarballFile import TarballFile

if __name__ == "__main__":
    sys.exit(1)
