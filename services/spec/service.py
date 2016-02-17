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
import StringIO
from specker.modules.specFileParser import SpecFileParser
from specker.modules.specFileRenderer import SpecFileRenderer
from specker.modules.specModelWriter import SpecModelWriter
from common.helpers.output import log
from common.service.computationalService import ComputationalService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action

class SpecService(ComputationalService):
	''' Specfile analysing and processing '''

	def signal_init(self):
		self.tmp_file = None

	def signal_destruct(self):
		if self.tmp_file is not None:
			os.remove(self.tmp_file)

	@action
	def spec_requires(self, specfile_id):
		'''
		Get all requires for a package
		@param specfile_id: a file id of a specfile stored in the system
		@return: list of requires
		'''
		return "TODO"

	@action
	def spec_buildrequires(self, specfile_id):
		'''
		Get all buildrequires for a package
		@param specfile_id: a file id of a file stored in the system
		@return: list of buildrequires
		'''
		return "TODO"

	@action
	def spec_packages(self, specfile_id):
		'''
		Get all packages (e.g. devel, ...) of a package
		@param specfile_id: a file id of a file stored in the system
		@return: list of packages
		'''
		return "TODO"

	@action
	def spec_requires_raw(self, specfile):
		'''
		Get all requires for a package
		@param specfile: raw specfile content
		@return: list of requires
		'''
		return "TODO"

	@action
	def spec_buildrequires_raw(self, specfile):
		'''
		Get all buildrequires for a package
		@param specfile: raw specfile content
		@return: list of buildrequires
		'''
		return "TODO"

	@action
	def spec_packages_raw(self, specfile):
		'''
		Get all packages (e.g. devel, ...) of a package
		@param specfile: raw specfile content
		@return: list of packages
		'''
		return "TODO"

if __name__ == "__main__":
	ServiceEnvelope.serve(SpecService)

