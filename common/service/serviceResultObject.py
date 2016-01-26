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
		if type(result) is str:
			self._result = json.parse(result)
			self._local = False
		else:
			self._result = {}
			self._result['result'] = result
			self._local = True

	def get_result(self):
		return self._result.get('result')

	def get_connect_time(self):
		return self._result.get('connected')

	def get_start_time(self):
		self._result.get('started')

	def get_end_time(self):
		self._result.get('finished')

	def get_service_name(self):
		self._result.get('service')

	def get_service_aliases(self):
		self._result.get('aliases')

	def was_local_call(self):
		return self._local

	def was_remote_call(self):
		return not self.was_local_call()

if __name__ == "__main__":
	sys.exit(1)

