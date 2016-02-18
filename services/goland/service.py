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
from common.helpers.output import log
from common.service.computationalService import ComputationalService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action


class GolandService(ComputationalService):
    ''' Golang specific service '''

    @action
    def golang_upstream2package(self, upstream_url):
        '''
        Convert an upstream URL to a package name packaged in Fedora
        @param upstream_url: URL of a project
        @return: package name in Fedora
        '''
        return "TODO"

    @action
    def golang_package2upstream(self, package_name):
        '''
        Convert a package name packaged in Fedora to upstream URL
        @param upstream_url: URL of a project
        @return: package name in Fedora
        '''
        return "TODO"

if __name__ == "__main__":
    ServiceEnvelope.serve(GolandService)
