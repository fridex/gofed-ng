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


class DepsStorageService(StorageService):
    ''' Retrieving API of projects and packages'''

    @classmethod
    def signal_startup(cls, config):
        cls.host = config.get('database-host', DEFAULT_DATABASE_HOST)
        cls.port = int(config.get('database-port', DEFAULT_DATABASE_PORT))
        cls.name = config.get('database-name', DEFAULT_DATABASE_NAME)
        cls.collection_name_project = config.get(
            'database-collection-project', DEFAULT_DATABASE_COLLECTION_PROJECT)
        cls.collection_name_package = config.get(
                'database-collection-package', DEFAULT_DATABASE_COLLECTION_PACKAGE)

        cls.client = MongoClient(cls.host, cls.port)
        cls.db = cls.client[cls.name]
        cls.deps_project = cls.db[cls.collection_name_project]
        cls.deps_package = cls.db[cls.collection_name_package]

    @action
    def deps_project_listing(self):
        '''
        Listing of all available projects with analyzed dependencies
        @return: list of all available projects with analyzed dependencies
        '''
        ret = ServiceResult()
        ret.result = []

        filtering = {'commit': 0, '_id': 0, 'deps': 0, 'meta': 0, 'commit-date': 0}

        cursor = self.deps_project.find({}, filtering)
        for item in cursor:
            if item['project'] not in ret.result:
                ret.result.append(item['project'])

        return ret

    @action
    def deps_project_commit_listing(self, project):
        '''
        Get all available commits of a project with analyzed dependencies
        @param project: project name
        @return: list of all available commits with analyzed dependencies
        '''
        ret = ServiceResult()
        ret.result = []

        filtering = {'_id': 0, 'deps': 0, 'project': 0, 'meta': 0, 'commit-date': 0}

        cursor = self.deps_project.find({'project': project}, filtering)
        for item in cursor:
            if item['commit'] not in ret:
                ret.result.append(item['commit'])

        return ret

    @action
    def deps_project(self, project, commit):
        '''
        Dependencies of the given project in specified commit
        @param project: project name
        @param commit: commit hash
        @return: list of deps of the project with analysis metadata
        '''
        ret = ServiceResult()
        ret.result = []

        filtering = {'commit': 0, '_id': 0, 'project': 0, 'commit-date': 0}

        cursor = self.deps_project.find({'project': project, 'commit': commit}, filtering)
        for item in cursor:
            ret.result.append({'deps': item['deps'], 'meta': item['meta'], 'commit-date': item['commit-date']})

        return ret

    @action
    def deps_package_listing(self):
        '''
        Listing of all available packages with analyzed dependencies
        @return: list of all available packages
        '''
        ret = ServiceResult()
        ret.result = []

        filtering = {'version': 0, '_id': 0, 'deps': 0, 'meta': 0}

        cursor = self.deps_package.find({}, filtering)
        for item in cursor:
            if item['package'] not in ret:
                ret.result.append(item['package'])

        return ret

    @action
    def deps_package_version_listing(self, package):
        '''
        Get all available versions of a package
        @param package: package name
        @return: list of all available versions based on distro
        '''
        ret = ServiceResult()
        ret.result = {}

        filtering = {'_id': 0, 'deps': 0, 'package': 0, 'meta': 0}

        cursor = self.deps_package.find({'package': package}, filtering)
        for item in cursor:
            if item['distro'] not in ret:
                ret[item['distro']] = []

            if item['version'] not in ret[item['distro']]:
                ret.result[item['distro']].append(item['version'])

        return ret

    def deps_package_distro_listing(self, package, distro):
        '''
        Get all available versions of a package within distro
        @param package: package name
        @param distro: distribution
        @return: list of all available versions in distribution
        '''
        ret = ServiceResult()
        ret.result = []

        filtering = {'_id': 0, 'deps': 0, 'package': 0, 'meta': 0}

        cursor = self.deps_package.find({'package': package, 'distro': distro}, filtering)
        for item in cursor:
            if item['distro'] not in ret:
                ret.result.append(item['distro'])

        return ret

    @action
    def deps_package(self, package, version, distro):
        '''
        Dependencies of the given project in specified commit
        @param package: package name
        @param version: package version
        @param distro: distribution
        @return: list of dependendencies of package with analysis metadata
        '''
        ret = ServiceResult()
        ret.result = []

        filtering = {'version': 0, '_id': 0, 'package': 0}

        cursor = self.deps_package.find({'package': package, 'version': version, 'distro': distro}, filtering)
        for item in cursor:
            ret.result.append({'deps': item['deps'], 'meta': item['meta']})

        return ret

if __name__ == "__main__":
    ServiceEnvelope.serve(DepsStorageService)
