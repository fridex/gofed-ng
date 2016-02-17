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

from pymongo import MongoClient
from common.service.storageService import StorageService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action

DEFAULT_DATABASE_HOST = 'localhost'
DEFAULT_DATABASE_PORT = 27017
DEFAULT_DATABASE_NAME = 'gofed'
DEFAULT_DATABASE_COLLECTION = 'api'

class ApiSaveStorageService(StorageService):
	''' Service for storing API of projects'''

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

	@action
	def api_store_project(self, project, commit, api, meta):
		'''
		Store API of a project
		@param project: project name
		@param commit: commit
		@param api: exported API
		@param meta: metadata from analysis
		'''
		item = {
			'project': project,
			'commit': commit,
			'api': api,
			'meta': meta
		}

		self.api.insert(item)

		return True

	@action
	def api_store_package(self, package_name, distribution, version, meta):
		pass

if __name__ == "__main__":
	ServiceEnvelope.serve(ApiSaveStorageService)

