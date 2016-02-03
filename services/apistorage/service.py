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
from common.service.storageService import StorageService
from common.service.serviceEnvelope import ServiceEnvelope

class ApiStorageService(StorageService):
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

	def exposed_get_api_project_listing(self):
		'''
		Listing of all available projects with analyzed API
		@return: list of all available projects
		'''
		return "TODO"

	def exposed_get_api_commit_listing(self, project):
		'''
		Get all available commits of a project
		@param project: project name
		@return: list of all available commits
		'''
		return "TODO"

	def exposed_get_api_project(self, project, commit = None):
		'''
		API of given project in specified commit
		@param project: project name
		@param commit: commit of project, if omitted, currend HEAD is used
		@return: API of the project
		'''
		return "TODO"

if __name__ == "__main__":
	ServiceEnvelope.serve(ApiStorageService)

