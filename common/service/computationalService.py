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

import sys, os
from threading import Lock
from service import Service
from common.system.system import System
from common.helpers.output import log

DEFAULT_TMP_DIR = 'tmp'

class ComputationalService(Service):
	@classmethod
	def on_startup(cls, config, system_json):
		# TODO: config is not accessible when local
		cls._system = System(config, system_json, service = True)
		cls._config = config
		cls._lock = Lock()

		cls.tmp_dir = config.get('tmp-dir', DEFAULT_TMP_DIR)

		if not os.path.isdir(cls.tmp_dir):
			log.info("Creating tree dir '%s'" % cls.tmp_dir)
			os.mkdir(cls.tmp_dir)
		log.info("Using temporary dir '%s'" % cls.tmp_dir)

		cls.signal_startup(config.get(cls.get_service_name()))

	def get_tmp_dir(self):
		return self.__class__.tmp_dir

if __name__ == "__main__":
	sys.exit(1)

