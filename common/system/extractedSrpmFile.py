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

import sys, os
import tarfile
from common.system.extractedFile import ExtractedFile
from common.system.tarballFile import TarballFile

class ExtractedSrpmFile(ExtractedFile):
	def __init__(self, path, origin):
		self._path = path
		# store a ref to origin (e.g. parent) -- the file which was extracted to
		# this file
		self._origin = origin

	def get_patches(self):
		ret = []
		for f in os.listdir(self.get_path()):
			if f.endswith(".patch"):
				ret.append(os.path.join(self.get_path()), f)

		return ret

	def get_tarball(self):
		for f in os.listdir(self.get_path()):
			if f.endswith(".tar.gz") or f.endswith(".zip"):
				return TarballFile(os.path.join(self.get_path(), f), self)

		raise ValueError("No tarball found")

	def get_spec_path(self):
		for f in os.listdir(self.get_path()):
			if f.endswith(".spec"):
				return os.path.join(self.get_path(), f)

		raise ValueError("No specfile found")

	def pack(self, dst_path = None):
		# TODO: implement
		raise NotImplementedError()

if __name__ == "__main__":
	sys.exit(1)

