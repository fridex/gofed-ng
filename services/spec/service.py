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
import os
import gitapi
import urllib2
import json
import StringIO
from specker.modules.specFileParser import SpecFileParser
from specker.modules.specFileRenderer import SpecFileRenderer
from specker.modules.specModelWriter import SpecModelWriter
from common.helpers.output import log
from common.service.computationalService import ComputationalService
from common.service.serviceEnvelope import ServiceEnvelope

DEFAULT_TMP_DIR = 'tmp'

class SpecService(ComputationalService):
	''' Golang spec files access and information retrieving '''

	@classmethod
	def signal_startup(cls, config):
		service_name = cls.get_service_name()

		if service_name in config:
			tmp_dir = config[service_name].get('tmp-dir', DEFAULT_TMP_DIR)

		if not os.path.isdir(tmp_dir):
			log.info("Creating tree dir '%s'" % tmp_dir)
			os.mkdir(tmp_dir)
		else:
			log.info("Using temporary dir '%s'" % tmp_dir)

		cls.tmp_dir = tmp_dir

	def signal_init(self):
		self.tmp_dir = self.__class__.tmp_dir

	def signal_processed(self):
		try:
			self.tmp_file
		except:
			return

		# TODO: remove tmp_file

	def exposed_get_spec_requires(self, specfile_id):
		'''
		Get all requires for package
		@param specfile_id: a file id of a file stored in system
		@return: list of requires
		'''
		return "TODO"

	def exposed_get_spec_buildrequires(self, specfile_id):
		'''
		Get all buildrequires for package
		@param specfile_id: a file id of a file stored in system
		@return: list of buildrequires
		'''
		return "TODO"

	def exposed_get_spec_packages(self, specfile_id):
		'''
		Get all packages (e.g. devel, ...) of a package
		@param specfile_id: a file id of a file stored in system
		@return: list of packages
		'''
		return "TODO"

if __name__ == "__main__":
	ServiceEnvelope.serve(SpecService)

