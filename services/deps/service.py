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
from common.service.computationalService import ComputationalService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action

class DepsService(ComputationalService):
	''' Dependencies checks '''

	@action
	def deps_analysis(self, file_id):
		'''
		Get deps of a file
		@param file_id: file to be analysed
		@return: list of dependencies
		'''
		return "TODO"

	@action
	def deps_diff(self, deps1, deps2):
		'''
		Make a diff of dependencies
		@param deps1: the first dependency list
		@param deps2: the second dependency list
		@return: list of dependency differences
		'''
		return "TODO"

if __name__ == "__main__":
	ServiceEnvelope.serve(DepsService)

