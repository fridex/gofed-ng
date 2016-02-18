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


class LicenseService(ComputationalService):
    ''' Licensing analysis '''

    @action
    def license_analysis(self, file_id):
        '''
        Analyse a file for licenses
        @param file_id: a file id of a file that needs to be analysed
        @return: list of all licenses found
        '''
        return "TODO"

    @action
    def license_diff(self, licenses1, licenses2):
        '''
        Compare licenses for changes
        @param licenses1: the first list of licenses
        @param licenses2: the second list of licenses
        '''
        return "TODO"

    @action
    def license_compatible(self, license1, license2):
        '''
        Say if two licenses are compatible
        @param license1: a first license
        @param license2: a first license
        @return: True if licenses are compatible
        '''
        return "TODO"

    @action
    def license_abbreviation(self, license):
        '''
        Get an abbrevation for a license
        @param license: a license to abbreviate
        @return: abbreviated license
        '''
        return "TODO"

    @action
    def license_summarize(self, licenses):
        '''
        Try to get the most suitable license which would cover all of the license
        @param licenses: a list of licenses
        @return: abbreviated license
        '''
        return "TODO"

if __name__ == "__main__":
    ServiceEnvelope.serve(LicenseService)
