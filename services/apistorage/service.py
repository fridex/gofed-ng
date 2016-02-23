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
DEFAULT_DATABASE_COLLECTION_PROJECT = 'project-api'
DEFAULT_DATABASE_COLLECTION_PACKAGE = 'package-api'


class ApiStorageService(StorageService):
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
        cls.api_project = cls.db[cls.collection_name_project]
        cls.api_package = cls.db[cls.collection_name_package]

    @action
    def api_project_listing(self):
        '''
        Listing of all available projects with analyzed API
        @return: list of all available projects with analyzed API
        '''
        ret = []
        filtering = {'commit': 0, '_id': 0, 'api': 0, 'meta': 0, 'commit-date': 0}

        cursor = self.api_project.find({}, filtering)
        for item in cursor:
            if item['project'] not in ret:
                ret.append(item['project'])

        return ret

    @action
    def api_project_commit_listing(self, project):
        '''
        Get all available commits of a project
        @param project: project name
        @return: list of all available commits
        '''
        ret = []
        filtering = {'_id': 0, 'api': 0, 'project': 0, 'meta': 0, 'commit-date': 0}

        cursor = self.api_project.find({'project': project}, filtering)
        for item in cursor:
            if item['commit'] not in ret:
                ret.append(item['commit'])

        return ret

    @action
    def api_project(self, project, commit):
        '''
        API of the given project in specified commit
        @param project: project name
        @param commit: commit hash
        @return: list of APIs of the project with analysis metadata
        '''
        ret = []
        filtering = {'commit': 0, '_id': 0, 'project': 0, 'commit-date': 0}

        cursor = self.api_project.find({'project': project, 'commit': commit}, filtering)
        for item in cursor:
            ret.append({'api': item['api'], 'meta': item['meta'], 'commit-date': item['commit-date']})

        return ret

    @action
    def api_package_listing(self):
        '''
        Listing of all available packages with analyzed API
        @return: list of all available packages
        '''
        ret = []
        filtering = {'version': 0, '_id': 0, 'api': 0, 'meta': 0}

        cursor = self.api_package.find({}, filtering)
        for item in cursor:
            if item['package'] not in ret:
                ret.append(item['package'])

        return ret

    @action
    def api_package_version_listing(self, package):
        '''
        Get all available commits of a project
        @param project: project name
        @return: list of all available versions based on distro
        '''
        ret = {}
        filtering = {'_id': 0, 'api': 0, 'package': 0, 'meta': 0}

        cursor = self.api_package.find({'package': package}, filtering)
        for item in cursor:
            if item['distro'] not in ret:
                ret[item['distro']] = []

            if item['version'] not in ret[item['distro']]:
                ret[item['distro']].append(item['version'])

        return ret

    @action
    def api_package_distro_listing(self, package, distro):
        '''
        Get all available commits of a project
        @param package: package name
        @param distro: distribution
        @return: list of all available versions based on distro
        '''
        ret = {}
        filtering = {'_id': 0, 'api': 0, 'package': 0, 'meta': 0}

        cursor = self.api_package.find({'package': package, 'distro': distro}, filtering)
        for item in cursor:
            if item['distro'] not in ret:
                ret.append(item['distro'])

        return ret

    @action
    def api_package(self, package, version):
        '''
        API of the given project in specified commit
        @param package: package name
        @param version: package version
        @return: list of APIs of the project with analysis metadata
        '''
        ret = []
        filtering = {'version': 0, '_id': 0, 'package': 0}

        cursor = self.api_package.find({'package': package, 'version': version}, filtering)
        for item in cursor:
            ret.append({'api': item['api'], 'meta': item['meta']})

        return ret

if __name__ == "__main__":
    ServiceEnvelope.serve(ApiStorageService)
