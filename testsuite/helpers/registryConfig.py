#!/bin/python
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
from testConfig import TestConfig

class RegistryConfig(TestConfig):
	def __init__(self):
		self._path = None
		self._conf = {
			'mode': 'UDP',
			'ipv6': 'False',
			'logfile': 'registry.log',
			'quiet': 'False',
			'port': '11920',
			'host': '::'
		}

	def _repre(self):
		return 'registry'

	# setters

	def set_mode(self, mode):
		self._conf['mode'] = str(mode)

	def set_ipv6(self, ipv6):
		self._conf['ipv6'] = str(ipv6)

	def set_logfile(self, logfile):
		self._conf['logfile'] = str(logfile)

	def set_quiet(self, quiet):
		self._conf['quiet'] = str(quiet)

	def set_port(self, port):
		self._conf['port'] = str(port)

	def set_host(self, host):
		self._conf['host'] = str(host)

	# getters

	def get_mode(self):
		return self._conf['mode']

	def get_ipv6(self):
		return self._conf['ipv6']

	def get_logfile(self):
		return self._conf['logfile']

	def get_quiet(self):
		return self._conf['quiet'] == 'True'

	def get_port(self):
		return int(self._conf['port'])

	def get_host(self):
		return self._conf['host']

if __name__ == "__main__":
	sys.exit(1)

