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
import rpyc, importlib
import random, json
from plumbum import SshMachine
from common.helpers.output import log # TODO: use log
from common.registry.registryClient import RegistryClient
from common.system.connectionCall import ConnectionCallSync, ConnectionCallAsync
from common.system.connection import Connection

class System(object):
	def __init__(self, config, system_json_file, service = False):
		self._config = config
		self._connections = {}
		self._service = service
		with open(system_json_file, 'r') as f:
			self._system = json.load(f)

	def __getattr__(self, name):
		if name == 'async_call':
			return ConnectionCallAsync(self)
		elif name == 'call':
			return ConnectionCallSync(self)
		else:
			return getattr(System, name)

	def _get_service_location(self, service_name):
		service = RegistryClient.query(service_name)

		if len(service) < 1:
			raise Exception("Service not found in Registry")

		idx = int(random.random() * len(service)) # try to do load balancing if possible
		return service[idx]

	def _establish_connection(self, service_name):
		host = None
		port = None
		remote = True

		if self._config.get(service_name):
			remote = self._config[service_name].get("remote") == 'True'

			if remote is True:
				host = self._config[service_name].get('host')
				port = self._config[service_name].get('port')

		if remote is True:
			if not host or not port:
				reg = self._get_service_location(service_name)
				host = reg[0]
				port = reg[1]

			conn = Connection(service_name, host = host, port = port)
		else:
			conn = Connection(service_name, system = self)

		return conn

	def get_connection(self, service_name):
		conn = self._connections.get(service_name)

		if not conn:
			conn = self._establish_connection(service_name)
			self._connections[service_name] = conn

		return conn

	def is_storage(self, service_name):
		for storage in self._system['services']['storages']:
			if storage['name'] == service_name:
				return True

		return False

	def is_computational(self, service_name):
		for computational in self._system['services']['computational']:
			if computational['name'] == service_name:
				return True

		return False

	def get_service(self, action):
		for storage in self._system['services']['storages']:
			for a in storage['actions']:
				if a['name'] == action:
					return storage
		if not self._service:
			for computational in self._system['services']['computational']:
				for a in computational['actions']:
					if a['name'] == action:
						return computational
		raise ValueError("Action '%s' not found in system" % action)

	def get_config(self):
		return self._config

	def __enter__(self):
		return self
		pass

	def __exit__(self, type, value, traceback):
		# we have to call destruct explicitely to notify about correct signals
		for connection in self._connections.values():
			connection.destruct()

if __name__ == "__main__":
	sys.exit(1)

