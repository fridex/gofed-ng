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

class ConnectionLocalCallAsync(object):
	def __init__(self, system):
		self._system = system

	def __getattr__(self, action):
		service = self._system.get_service(action)
		if not self._system.is_storage(service['name']):
			raise ValueError("Cannot run action from computational service on computational service")
		connection = self._system.get_connection(service['name'])
		return connection.get_action(action, async = True)

class ConnectionLocalCallSync(object):
	def __init__(self, system):
		self._system = system

	def __getattr__(self, action):
		service = self._system.get_service(action)
		if not self._system.is_storage(service['name']):
			raise ValueError("Cannot run action from computational service on computational service")
		connection = self._system.get_connection(service['name'])
		return connection.get_action(action, async = False)

if __name__ == "__main__":
	sys.exit(1)

