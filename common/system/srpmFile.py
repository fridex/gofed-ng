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
import tarfile
from common.system.file import File
from common.system.extractedSrpmFile import ExtractedSrpmFile
from common.helpers.utils import runpipe


class SrpmFile(File):

    def __init__(self, path, file_id):
        # example output:
        #   'RPM v3.0 src'
        self._path = path
        self._file_id = file_id
        self._type = self._get_raw_type().split(' ')
        if self._type[0] != 'RPM' or self._type[2] != 'src':
            raise ValueError("Not an src.rpm file %s" % (path,))

    @classmethod
    def magic_match(cls, m):
        m = m.split(' ')
        return m[0] == 'RPM' and m[2] == 'src'

    def get_srpm_version(self):
        return self._type[1]

    def get_type(self):
        return 'src.rpm'

    def unpack(self, dst_path):
        cmd1 = ["rpm2cpio", self._path]
        cmd2 = ["cpio", "-idmv"]

        runpipe([cmd1, cmd2], dst_path)

        return ExtractedSrpmFile(dst_path, self)

if __name__ == "__main__":
    sys.exit(1)
