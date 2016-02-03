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
from pymongo import MongoClient
from common.helpers.output import log
from common.helpers.utils import json_pretty_format
from common.service.storageService import StorageService
from common.service.serviceEnvelope import ServiceEnvelope

DEFAULT_DATABASE_HOST = 'localhost'
DEFAULT_DATABASE_PORT = 27017
DEFAULT_DATABASE_NAME = 'gofed'
DEFAULT_DATABASE_COLLECTION = 'api'

# TODO: locking in threads

class ApiStorageService(StorageService):
	''' Service for retrieving API of projects'''

	@classmethod
	def signal_startup(cls, config):
		cls.host = config.get('database-host', DEFAULT_DATABASE_HOST)
		cls.port = int(config.get('database-port', DEFAULT_DATABASE_PORT))
		cls.name = config.get('database-name', DEFAULT_DATABASE_NAME)
		cls.collection_name = config.get('database-collection', DEFAULT_DATABASE_COLLECTION)

		cls.client = MongoClient(cls.host, cls.port)
		cls.db = cls.client[cls.name]
		cls.api = cls.db[cls.collection_name]

	def signal_init(self):
		self.api = self.__class__.api

	def exposed_get_api_project_listing(self):
		'''
		Listing of all available projects with analyzed API
		@return: list of all available projects
		'''
		ret = []
		filtering = {'commit': 0, '_id': 0, 'api': 0, 'meta': 0}

		for item in self.api.find({}, filtering):
			ret.append(item['project'])

		return ret

	def exposed_get_api_commit_listing(self, project):
		'''
		Get all available commits of a project
		@param project: project name
		@return: list of all available commits
		'''
		ret = []
		filtering = {'_id': 0, 'api': 0, 'project': 0, 'meta': 0}

		for item in self.api.find({'project': project}, filtering):
			ret.append(item['commit'])

		return ret

	def exposed_get_api_project(self, project, commit):
		'''
		API of given project in specified commit
		@param project: project name
		@param commit: commit of project, if omitted, currend HEAD is used
		@return: API of the project
		'''
		ret = []
		filtering = { 'commit': 0, '_id': 0, 'project': 0 }

		for item in self.api.find({'project': project, 'commit': commit}, filtering):
			ret.append(item['api'])

		return ret

if __name__ == "__main__":
	ServiceEnvelope.serve(ApiStorageService)

