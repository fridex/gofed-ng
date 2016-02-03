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
from common.helpers.output import log
from common.helpers.utils import json_pretty_format
from common.service.computationalService import ComputationalService
from common.service.serviceEnvelope import ServiceEnvelope

class ApidiffService(ComputationalService):
	''' Service for retrieving API of projects'''

	@classmethod
	def signal_startup(cls, config):
		log.info("Custom config sections: " + json_pretty_format(config))
		log.info("got startup signal")

	@classmethod
	def signal_termination(cls):
		log.info("got termination signal")

	def signal_init(self):
		log.info("got init signal")

	def signal_connect(self):
		log.info("got connect signal")

	def signal_disconnect(self):
		log.info("got disconnect signal")

	def signal_process(self):
		log.info("got process signal")

	def signal_processed(self):
		log.info("got processed signal")

	def exposed_apidiff_project(self, project1, commit1, project2, commit2):
		'''
		Make diff of API of two projects
		@param project1: the first project
		@param commit1: a commit of the first project, if None current HEAD is used
		@param project2: the second project
		@param commit2: a commit of the second project, if None current HEAD is used
		@return: list of API differences
		'''
		return "TODO"

	def exposed_apidiff_file(self, project_file_id1, project_file_id2):
		'''
		Make diff of API of two files
		@param project_file_id1: the first project file
		@param project_file_id2: the second project file
		@return: list of API differences
		'''
		return "TODO"

	def exposed_apidiff_project_file(self, project, commit, project_file_id):
		'''
		Make diff of API of two files
		@param project: the first project file
		@param commit: a commit of the project, if None current HEAD is used
		@param project_file_id: a project file id
		@return: list of API differences
		'''
		return "TODO"

	def exposed_apidiff_file_project(self, project_file_id, project, commit):
		'''
		Make diff of API of two files
		@param project_file_id: the first project file
		@param project: a project file
		@param commit: a commit of the project, if None current HEAD is used
		@return: list of API differences
		'''
		return "TODO"

if __name__ == "__main__":
	ServiceEnvelope.serve(ApidiffService)

