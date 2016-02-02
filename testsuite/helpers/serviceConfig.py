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

class ServiceConfig(TestConfig):
	def __init__(self, service_name = None):
		self._service_name = service_name
		self._path = None
		self._config = {
			'port': '0',
			'host': 'localhost',
			'logfile': service_name + '.log',
			'register': 'True',
			'register-type': 'UDP',
			'register-host': 'localhost',
			'register-port': '18812',
			'max-client-count': '10',
			'max-requests-per-client': '5'
		}

	def _repre(self):
		return self._service_name

	# setters
	def set_service_name(self, service_name):
		self._service_name = str(service_name)

	def set_port(self, port):
		self._config['port'] = str(port)

	def set_host(self, host):
		self._config['host'] = str(host)

	def set_logfile(self, logfile):
		self._config['logfile'] = str(logfile)

	def set_register(self, register):
		self._config['register'] = str(register)

	def set_register_type(self, register_type):
		self._config['register-type'] = str(register_type)

	def set_register_host(self, host):
		self._config['register-host'] = str(host)

	def set_register_port(self, register_port):
		self._config['register-port'] = str(register_port)

	def set_max_client_count(self, max_client_count):
		self._config['max-client-count'] = str(max_client_count)

	def set_max_requests_per_client(self, max_requests_per_client):
		self._config['max-requests-per-client'] = str(max_requests_per_client)

	# getters

	def get_service_name(self):
		return self._service_name

	def get_port(self):
		return int(self._config['port'])

	def get_host(self):
		return self._config['host']

	def get_logfile(self):
		return self._config['logfile']

	def get_register(self):
		return self._config['register'] == 'True'

	def get_register_type(self):
		return self._config['register-type']

	def get_register_host(self):
		return self._config['register-host']

	def get_register_port(self):
		return int(self._config['register-port'])

	def get_max_client_count(self):
		return int(self._config['max-client-count'])

	def get_max_requests_per_client(self):
		return int(self._config['max-requests-per-client'])


if __name__ == "__main__":
	sys.exit(1)

