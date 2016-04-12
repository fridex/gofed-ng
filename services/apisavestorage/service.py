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

import json
from pymongo import MongoClient
from common.service.serviceResult import ServiceResult
from common.service.storageService import StorageService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action

DEFAULT_DATABASE_HOST = 'localhost'
DEFAULT_DATABASE_PORT = 27017
DEFAULT_DATABASE_NAME = 'gofed'
DEFAULT_DATABASE_COLLECTION_PROJECT = 'project-api'
DEFAULT_DATABASE_COLLECTION_PACKAGE = 'package-api'


class ApiSaveStorageService(StorageService):
    ''' Service for storing API of projects'''

    @classmethod
    def signal_startup(cls, config):
        cls.host = config.get('database-host', DEFAULT_DATABASE_HOST)
        cls.port = int(config.get('database-port', DEFAULT_DATABASE_PORT))
        cls.name = config.get('database-name', DEFAULT_DATABASE_NAME)
        cls.collection_name_project = config.get('database-collection-project', DEFAULT_DATABASE_COLLECTION_PROJECT)
        cls.collection_name_package = config.get('database-collection-package', DEFAULT_DATABASE_COLLECTION_PACKAGE)

        cls.client = MongoClient(cls.host, cls.port)
        cls.db = cls.client[cls.name]
        cls.api_project = cls.db[cls.collection_name_project]
        cls.api_package = cls.db[cls.collection_name_package]

    @action
    def api_store_project(self, project, commit, api, meta):
        '''
        Store API of a project
        @param project: project name
        @param commit: commit
        @param api: exported API
        @param meta: metadata from analysis
        '''
        ret = ServiceResult()
        item = {
            'project': project,
            'commit': commit,
            'api': api,
            'meta': meta
        }

        self.api_project.insert(item)

        ret.result = True
        return ret

    @action
    def api_store_package(self, package, version, release, distro, api, meta):
        '''
        Store API of a package
        @param package: package name to store
        @param version: version of package
        @param release: a package release
        @param distro: distribution
        @param api: exported api
        @param meta: metadata from analysis
        '''
        ret = ServiceResult()
        item = {
            'package': package,
            'version': version,
            'release': release,
            'distro': distro,
            'api': api,
            'meta': meta
        }

        self.api_package.insert(item)

        ret.result = True
        return ret

if __name__ == "__main__":
    ServiceEnvelope.serve(ApiSaveStorageService)

