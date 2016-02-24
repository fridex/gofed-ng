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
import urllib2
import json
from time import time
from common.service.computationalService import ComputationalService
from common.service.serviceEnvelope import ServiceEnvelope
from common.helpers.utils import dict2json
from common.service.action import action
from goland.goTranslator import GoTranslator
from common.service.serviceResult import ServiceResult

PKGDB_API_URL = "https://admin.fedoraproject.org/pkgdb/api/packages/?&pattern=golang-*"
UPDATE_INTERVAL = 5*60


class GolandService(ComputationalService):
    ''' Golang specific service '''
    # it can be periodically updated, so read it every time
    # it would worth it to add this to config file
    mappings_json = os.path.join("goland", "mappings.json")
    packages = {'packages': None, 'updated': None}

    @classmethod
    def _fedora_pkgdb_packages_list(cls):
        ret = []
        response = urllib2.urlopen(PKGDB_API_URL)

        if response.code != 200:
            raise RuntimeError("Failed to receive packages from Fedora package database (%s)"
                               % str(response.code))

        packages = json.loads(response.read())

        if packages['output'] != 'ok':
            raise RuntimeError("Bad response from Fedora package database:\n%s"
                               % dict2json(packages))

        # TODO: handle pagination
        assert packages['page'] == 1 and packages['page_total'] == 1

        return packages['packages']

    @action
    def golang_upstream2package(self, upstream_url):
        '''
        Convert an upstream URL to a package name packaged in Fedora
        @param upstream_url: URL of a project
        @return: package name in Fedora
        '''
        ret = ServiceResult()

        with self.get_lock(self.mappings_json):
            t = GoTranslator(self.mappings_json)
            ret.result = t.upstream2pkgname(upstream_url)

        return ret

    @action
    def golang_package2upstream(self, package_name):
        '''
        Convert a package name packaged in Fedora to upstream URL
        @param upstream_url: URL of a project
        @return: package name in Fedora
        '''
        ret = ServiceResult()

        with self.get_lock(self.mappings_json):
            t = GoTranslator(self.mappings_json)
            ret.result = t.pkgname2upstream(package_name)

        return ret

    @action
    def goland_package_listing(self):
        '''
        List of all available golang packages packaged in fedora
        @return: packages packaged in fedora
        '''
        ret = ServiceResult()

        def data_cached():
            return self.packages['packages'] is not None and (time() - self.packages['updated'] < UPDATE_INTERVAL)

        if not data_cached():
            with self.get_lock(self._fedora_pkgdb_packages_list):
                if not data_cached():
                    self.packages['packages'] = self._fedora_pkgdb_packages_list()
                    self.packages['updated'] = time()

        ret.result = self.packages['packages']
        return ret

if __name__ == "__main__":
    ServiceEnvelope.serve(GolandService)
