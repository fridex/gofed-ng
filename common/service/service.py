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
from rpyc import Service as RpycService
from common.helpers.version import VERSION
from common.service.actionWrapper import ActionWrapper
from common.service.serviceResultGenerator import ServiceResultGenerator

class Service(RpycService):
	def __init__(self, conn):
		super(Service, self).__init__(conn)
		self._result = ServiceResultGenerator()
		self._result.log_service_name(self.get_service_name())
		self._result.log_service_aliases(self.get_service_aliases())

	def on_connect(self):
		self._result.log_connect_time()
		self.signal_connect()

	def on_disconnect(self):
		self.signal_disconnect()

	def _rpyc_getattr(self, name):
		return ActionWrapper(
				super(Service, self)._rpyc_getattr(name),
				self._result,
				prehook = self.signal_process,
				posthook = self.signal_processed
			)

	@classmethod
	def signal_startup(cls, config):
		pass

	@classmethod
	def signal_termination(cls):
		pass

	def signal_connect(self):
		pass

	def signal_disconnect(self):
		pass

	def signal_process(self):
		pass

	def signal_processed(self):
		pass

	@classmethod
	def get_service_version(cls):
		return VERSION

	def exposed_version(self):
		return VERSION

if __name__ == "__main__":
	sys.exit(1)

