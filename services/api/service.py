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

import os, shutil
from common.helpers.output import log
from common.helpers.utils import json_pretty_format
from common.service.computationalService import ComputationalService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action
from common.system.extractedRpmFile import ExtractedRpmFile
from common.system.extractedSrpmFile import ExtractedSrpmFile
from common.system.extractedTarballFile import ExtractedTarballFile

from gofedlib.gosymbolsextractor import api
from gofedlib.goapidiff import apidiff

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
		self.tmpfile_path = None
		self.extracted1_path = None
		self.extracted2_path = None
		log.info("got process signal")

	def signal_processed(self, was_error):
		if self.tmpfile_path is not None:
			os.remove(self.tmpfile_path)

		if self.extracted1_path is not None:
			shutil.rmtree(self.extracted1_path)

		if self.extracted2_path is not None:
			shutil.rmtree(self.extracted2_path)

		log.info("got processed signal")

	@action
	def api_analysis(self, file_id):
		'''
		Get API of a file
		@param file_id: file to be analysed
		@return: list of exported API
		'''
		self.tmpfile_path = self.get_tmp_filename()
		with self.get_system() as system:
			f = system.download(file_id, self.tmpfile_path)

		self.extracted1_path = self.get_tmp_dirname()
		d = f.unpack(self.extracted1_path)

		if isinstance(d, ExtractedRpmFile):
			src_path = d.get_content_path()
		elif isinstance(d, ExtractedTarballFile):
			src_path = d.get_path()
		elif isinstance(d, ExtractedSrpmFile):
			# we have to unpack tarball first
			t = d.get_tarball()
			self.extracted2_path = self.get_tmp_dirname()
			d = f.unpack(self.extracted2_path)
			src_path = d.get_path()

		return api(src_path)

	@action
	def api_diff(self, api1, api2):
		'''
		Make a diff of APIs
		@param api1: the first API
		@param api2: the second API
		@return: list of API differences
		'''
		return apidiff(api1, api2)

if __name__ == "__main__":
	ServiceEnvelope.serve(ApiService)

