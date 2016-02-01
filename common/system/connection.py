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
from common.system.serviceResultObject import ServiceResultObject
from common.service.serviceWrapper import ServiceWrapper

class Connection(object):
	def __init__(self, service_name, host = None, port = None, system = None):
		self._service_name = service_name
		self._connection = None
		self._instance = None

		if host:
			assert port is not None
			self._connect(host, port)
		else:
			self._instantiate(system)

	def _connect(self, host, port):
		self._connection = rpyc.connect(host, port)

	def _instantiate(self, system):
		self._instance = ServiceWrapper(self._service_name, system)

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

	def destruct(self):
		if self._connection is not None:
			self._connection.__del__()

		if self._instance is not None:
			self._instance.__del__()

if __name__ == "__main__":
	sys.exit(1)

