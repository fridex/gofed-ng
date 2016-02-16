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
from common.system.extractedFile import ExtractedFile

class SrpmFile(File):
	def __init__(self, path):
		# example output:
		#   'RPM v3.0 src'
		self._type = self._get_raw_type().split(' ')
		if self._type[0] != 'RPM' or self._type[2] != 'src':
			raise ValueError("Not an src.rpm file %s" % (path,))
		self._path = path

	def get_srpm_version(self):
		return self._type[1]

	def get_type(self):
		return 'src.rpm'

	def unpack(self, dst_path = "."):
		t = tarfile.open(self._path, 'r')
		t.extractall(dst_path)
		return ExtractedFile(dst_path, self)

if __name__ == "__main__":
	sys.exit(1)

