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
import rpyc
import importlib
from common.system.serviceResultObject import ServiceResultObject

class Connection(object):
	def __init__(self, service_name, host = None, port = None):
		self._service_name = service_name
		self._connection = None
		self._instance = None

		if host:
			assert port is not None
			self._connect(host, port)
		else:
			self._instantiate()

	def _connect(self, host, port):
		self._connection = rpyc.connect(host, port)

	def _instantiate(self):
		package = 'services.%s.service' % self._service_name
		name = '%s.%s' % (package, self._service_name)

		module = importlib.import_module(name, package)
		cls = getattr(module. self._service_name)
		self._instance = cls(None) # connection is None

	def is_local(self):
		return self._connection is None

	def is_remote(self):
		return not self.is_local()

	def get_action(self, action_name, async = False):
		if self.is_local():
			# TODO: bind to object
			return ServiceResultObject(self._service_name, action_name, self, getattr(self._instance, action_name))
		else:
			action = getattr(self._connection.root, action_name)
			if async is True:
				return ServiceResultObject(self._service_name, action_name, self, rpyc.async(action), async = True)
			else:
				return ServiceResultObject(self._service_name, action_name, self, action)

if __name__ == "__main__":
	sys.exit(1)

