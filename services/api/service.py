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

import os
from common.helpers.output import log
from common.helpers.utils import json_pretty_format
from common.service.computationalService import ComputationalService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.fileAction import fileAction

class ApiService(ComputationalService):
	''' API analysis '''

	@classmethod
	def signal_startup(cls, config):
		log.info("got startup signal")
		log.info("config sections: " + json_pretty_format(config))

	@classmethod
	def signal_termination(cls):
		log.info("got termination signal")

	def signal_init(self):
		log.info("got init signal")

	def signal_destruct(self):
		log.info("got destruct signal")

	def signal_connect(self):
		log.info("got connect signal")

	def signal_disconnect(self):
		log.info("got disconnect signal")

	def signal_process(self):
		log.info("got process signal")

	def signal_processed(self, was_error):
		log.info("got processed signal")

	@fileAction
	def exposed_api(self, file_id):
		'''
		Get API of a file
		@param file_id: file to be analysed
		@return: list of exported API
		'''
		with self.get_system() as system:
			system.download(file_id, self.get_tmp_filename())
		return "TODO"

	def exposed_apidiff(self, api1, api2):
		'''
		Make a diff of APIs
		@param api1: the first API
		@param api2: the second API
		@return: list of API differences
		'''
		return "TODO"

if __name__ == "__main__":
	ServiceEnvelope.serve(ApiService)

