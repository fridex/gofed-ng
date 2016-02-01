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

class _Logger(object):
	def __init__(self):
		self._warn_log = sys.stderr
		self._err_log = sys.stderr
		self._info_log = sys.stderr

	def set_warn_logfile(self, logfile):
		self._warn_log = logfile

	def set_err_logfile(self, logfile):
		self._err_log = logfile

	def set_info_logfile(self, logfile):
		self._info_log = logfile

	def set_logfile(self, logfile):
		self.set_warn_logfile(logfile)
		self.set_err_logfile(logfile)
		self.set_info_logfile(logfile)

	def error(self, s):
		if self._err_log.isatty():
			self._err_log.write("\033[91m!ERR:\033[0m %s\n" % s)
		else:
			self._err_log.write("!ERR: %s\n" % s)

	def warn(self, s):
		if self._warn_log.isatty():
			self._warn_log.write("\033[93mWARN:\033[0m %s\n" % s)
		else:
			self._warn_log.write("WARN: %s\n" % s)

	def info(self, s):
		if self._info_log.isatty():
			self._info_log.write("\033[92mINFO:\033[0m %s\n" % s)
		else:
			self._info_log.write("INFO: %s\n" % s)

log = _Logger()

if __name__ == '__main__':
	sys.exit(1)

