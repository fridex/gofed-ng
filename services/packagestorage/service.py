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
from common.service.storageService import StorageService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action

DEFAULT_PACKAGES_TREE_DIR = "packages/"


class PackageStorageService(StorageService):
    '''  Fedora Git packages provider '''

    @action
    def package_get(self, package_name):
        '''
        Needs design
        '''
        return "TODO"

    @action
    def package_get_commit(self, package_name, commit):
        '''
        Needs design
        '''
        return "TODO"

if __name__ == "__main__":
    ServiceEnvelope.serve(PackageStorageService)
