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
import datetime
from dateutil.parser import parse as datetime_parse

class FileId(object):
	def __init__(self, file_id):
		self._file_id = file_id

	def get_service_name(self):
		return self._file_id['service']

	def get_service_host(self):
		return self._file_id['host']

	def get_service_port(self):
		return self._file_id['port']

	def get_valid_date(self):
		if self._file_id['valid_until'] == -1:
			return float("infinity");
		else:
			return datetime_parse(self._file_id['valid_until'])

	def get_hash(self):
		return self._file_id['sha1']

	def get_size(self):
		return self._file_id['size']

	def is_valid(self):
		valid_until = self.get_valid_date()

		if valid_until == float("infinity"):
			return True

		current_date = datetime.datetime.now()
		return valid_until > current_date

	def get_raw(self):
		return self._file_id

if __name__ == "__main__":
	sys.exit(1)

