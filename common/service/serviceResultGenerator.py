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
import os
from time import gmtime, strftime

# TODO: this could be extended with action logging to a file

class ServiceResultGenerator(object):
	def _print_time(self):
		return strftime("%Y-%m-%d %H:%M:%S", gmtime())

	def __init__(self):
		self._stats = {'connected': None,
				'started': None,
				'finished': None,
				'result': None,
				'hostname': os.uname()[1],
				}

	def log_connect_time(self):
		self._stats['connected'] = self._print_time()

	def log_process_time(self):
		self._stats['started'] = self._print_time()

	def log_processed_time(self):
		self._stats['finished'] = self._print_time()

	def log_result(self, result):
		if type(result) is not dict:
			raise ValueError("Action should return a dict, got '%s'", type(result))

		self._stats['result'] = result

	def log_service_name(self, name):
		self._stats['service'] = name

	def log_service_aliases(self, names):
		self._stats['aliases'] = names

	def dump(self):
		return json.dumps(self._stats)

if __name__ == "__main__":
	sys.exit(1)

