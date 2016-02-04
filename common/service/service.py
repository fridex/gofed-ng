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
from threading import Lock
from rpyc import Service as RpycService
from common.helpers.version import VERSION
from common.service.actionWrapper import ActionWrapper
from common.service.serviceResultGenerator import ServiceResultGenerator
from common.system.system import System

class Service(RpycService):
	def __init__(self, conn, system = None):
		# conn has to be always supplied because of rpyc.Service __init__
		if conn is not None: # remote service
			super(Service, self).__init__(conn)

		self._result = ServiceResultGenerator()
		self._result.log_service_name(self.get_service_name())
		self._result.log_service_aliases(self.get_service_aliases())

		if system is not None:
			# we are running local service
			assert conn is None
			self.system = system
		else:
			# in this case we are running remote service, system should be passed
			# by SystemEnvelope by calling on_startup()
			assert conn is not None
			self.system = self.__class__._system

		self.signal_init()

	def __del__(self):
		self.signal_destruct()

	@classmethod
	def on_termination(cls):
		cls.signal_termination()

	def on_connect(self):
		if self.is_remote():
			self._result.log_connect_time()
		self.signal_connect()

	def on_disconnect(self):
		self.signal_destruct()
		self.signal_disconnect()

	def _rpyc_getattr(self, name):
		return ActionWrapper(
				super(Service, self)._rpyc_getattr(name),
				self._result,
				prehook = self.signal_process,
				posthook = self.signal_processed
			)

	def __getattr__(self, name):
		if not name.startswith('exposed_'):
			exposed_name = "exposed_" + name
			if hasattr(self, exposed_name) and callable(getattr(self, exposed_name)):
				getattr(self.__class__, exposed_name)

		return getattr(self.__class__, name)

	def get_lock(self):
		return self.__class__._lock

	def acquire_lock(self):
		self.__class__._lock.acquire()

	def release_lock(self):
		self.__class__._lock.release()

	@classmethod
	def signal_startup(cls, config):
		pass

	@classmethod
	def signal_termination(cls):
		pass

	def signal_init(self):
		pass

	def signal_destruct(self):
		pass

	def signal_connect(self):
		pass

	def signal_disconnect(self):
		pass

	def signal_process(self):
		pass

	def signal_processed(self, was_error):
		pass

	def is_local(self):
		try:
			self._conn
			return False
		except NameError:
			return True

	def is_remote(self):
		return not self.is_local()

	@classmethod
	def get_service_version(cls):
		return VERSION

	@classmethod
	def get_host(cls):
		# TODO: improve - use conn?
		remote = cls._config.get('remote')

		if remote == 'False':
			return 'localhost'

		return cls._config.get('host')

	@classmethod
	def get_port(cls):
		# TODO: improve - use conn?
		remote = cls._config.get('remote')

		if remote == 'False':
			return 'localhost'

		return cls._config.get('port')

	def exposed_version(self):
		return self.__class__.get_service_version()

	def version(self):
		return self.__class__.get_service_version()

if __name__ == "__main__":
	sys.exit(1)

