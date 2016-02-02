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
import importlib

class ServiceWrapper(object):
	def __init__(self, service_name, system):
		class_name = service_name[0] + service_name[1:].lower() + 'Service'

		name = 'services.%s.service' % service_name.lower()
		module = importlib.import_module(name)

		self._instance = None
		self._cls = getattr(module, class_name)
		self._system = system
		self._service_name = service_name

	def __getattr__(self, name):
		if self._instance is None:
			# TODO: pass config
			# conn parameter is because of local connection
			self._cls.signal_startup(self._system.get_config().get(self._service_name))
			self._instance = self._cls(conn = None, system = self._system)

		exposed_name = "exposed_" + name
		return self._instance._rpyc_getattr(exposed_name)

	def __del__(self):
		self._cls.signal_termination()

if __name__ == "__main__":
	sys.exit(1)

