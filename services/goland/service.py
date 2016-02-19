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
from common.service.computationalService import ComputationalService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action
from goland.goTranslator import GoTranslator
from common.service.serviceResult import ServiceResult


class GolandService(ComputationalService):
    ''' Golang specific service '''
    # it can be periodically updated, so read it every time
    # it would worth it to add this to config file
    mappings_json = os.path.join("goland", "mappings.json")

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

if __name__ == "__main__":
    ServiceEnvelope.serve(GolandService)
