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
import json

class ServiceResultObject(object):
	def __init__(self, result):
		self._result = json.parse(result)

	def get_result(self):
		return self._result['result']

	def get_connect_time(self):
		return self._result['connected']

	def get_start_time(self):
		self._result['started']

	def get_end_time(self):
		self._stats['finished']

	def get_service_name(self):
		self._stats['service'] = name

	def get_service_aliases(self):
		self._stats['aliases'] = names

if __name__ == "__main__":
	sys.exit(1)

