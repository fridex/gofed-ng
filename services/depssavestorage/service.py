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
from common.service.serviceResult import ServiceResult
from common.service.storageService import StorageService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action

DEFAULT_DATABASE_HOST = 'localhost'
DEFAULT_DATABASE_PORT = 27017
DEFAULT_DATABASE_NAME = 'gofed'
DEFAULT_DATABASE_COLLECTION_PROJECT = 'project-deps'
DEFAULT_DATABASE_COLLECTION_PACKAGE = 'package-deps'


class DepsSaveStorageService(StorageService):
    ''' Service for storing deps of projects'''

    @classmethod
    def signal_startup(cls, config):
        cls.host = config.get('database-host', DEFAULT_DATABASE_HOST)
        cls.port = int(config.get('database-port', DEFAULT_DATABASE_PORT))
        cls.name = config.get('database-name', DEFAULT_DATABASE_NAME)
        cls.collection_name_project = config.get('database-collection-project', DEFAULT_DATABASE_COLLECTION_PROJECT)
        cls.collection_name_package = config.get('database-collection-package', DEFAULT_DATABASE_COLLECTION_PACKAGE)

        cls.client = MongoClient(cls.host, cls.port)
        cls.db = cls.client[cls.name]
        cls.deps_project = cls.db[cls.collection_name_project]
        cls.deps_package = cls.db[cls.collection_name_package]

    @action
    def deps_store_project(self, project, commit, deps, meta):
        '''
        Store API of a project
        @param project: project name
        @param commit: commit
        @param deps: project deps
        @param meta: metadata from analysis
        '''
        ret = ServiceResult()
        item = {
            'project': project,
            'commit': commit,
            'deps': deps,
            'meta': meta
        }

        self.deps_project.insert(item)

        ret.result = True
        return ret

    @action
    def deps_store_package(self, package, version, distro, deps, meta):
        '''
        Store API of a package
        @param package: package name to store
        @param version: version of package
        @param distro: distribution
        @param deps: package dependencies
        @param meta: metadata from analysis
        '''
        ret = ServiceResult()
        item = {
            'package': package,
            'version': version,
            'distro': distro,
            'deps': deps,
            'meta': meta
        }

        self.deps_package.insert(item)

        ret.result = True
        return ret

if __name__ == "__main__":
    ServiceEnvelope.serve(DepsSaveStorageService)

