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

import sys, os, shutil

class Dircache(object):
	def __init__(self, path, max_size = float("inf")):
		self._path = path
		self._max_size = max_size
		# file usage - from "less used" to the "most used"
		self._fileusage = []

		if not os.path.isdir(path):
			os.mkdir(path)

	def set_max_size(self, max_size):
		self._max_size = max_size
		self._run_cleanup()

	def get_max_size(self):
		return self._max_size

	def get_path(self):
		return self._path

	def store(self, blob, filename):
		dst = os.path.join(self.get_path(), filename)

		with open(dst, 'wb') as f:
			f.write(blob)

		self._mark_used(filename)
		self._run_cleanup()

	def retrieve(self, filename):
		dst = os.path.join(self.get_path(), filename)

		with open(dst, 'rb') as f:
			ret = f.read()

		self._mark_used(filename)

		return ret

	def delete(self, filename):
		dst = os.path.join(self.get_path(), filename)

		if os.path.isfile(dst):
			os.remove(dst)
		else:
			shutil.rmtree(dst)

	def get_current_size(self):
		return sum(os.path.getsize(f) for f in os.listdir(self.get_path()) if os.path.isfile(f))

	def _run_cleanup(self):
		while self.get_current_size() > self.get_max_size():
			if len(self._fileusage) > 0:
				filename = self._fileusage.pop(0)
				dst = os.path.join(self.get_path(), filename)
				os.remove(dst)
			else:
				raise IOError("Not enough space in cache file %s" % (self.get_path(),))

	def _mark_used(self, filename):
		if filename in self._fileusage:
			self._fileusage.remove(filename)

		self._fileusage.append(filename)

if __name__ == "__main__":
	sys.exit(1)

