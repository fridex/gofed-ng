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
import shutil
import json
from common.helpers.utils import runcmd
from common.service.computationalService import ComputationalService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action
from common.service.serviceResult import ServiceResult
from common.system.extractedRpmFile import ExtractedRpmFile
from common.system.extractedSrpmFile import ExtractedSrpmFile
from common.system.extractedTarballFile import ExtractedTarballFile


class LicenseService(ComputationalService):
    ''' Licensing analysis '''

    def signal_init(self):
        self.tmpfile_path = None
        self.extracted1_path = None
        self.extracted2_path = None

    def signal_processed(self, was_error):
        if self.tmpfile_path is not None:
            os.remove(self.tmpfile_path)

        if self.extracted1_path is not None:
            shutil.rmtree(self.extracted1_path)

        if self.extracted2_path is not None:
            shutil.rmtree(self.extracted2_path)

    @action
    def license_analysis(self, file_id):
        '''
        Analyse a file for licenses
        @param file_id: a file id of a file that needs to be analysed
        @return: list of all licenses found
        '''
        ret = ServiceResult()

        self.tmpfile_path = self.get_tmp_filename()
        with self.get_system() as system:
            f = system.download(file_id, self.tmpfile_path)

        self.extracted1_path = self.get_tmp_dirname()
        d = f.unpack(self.extracted1_path)

        if isinstance(d, ExtractedRpmFile):
            src_path = d.get_content_path()
        elif isinstance(d, ExtractedTarballFile):
            src_path = d.get_path()
        elif isinstance(d, ExtractedSrpmFile):
            # we have to unpack tarball first
            t = d.get_tarball()
            self.extracted2_path = self.get_tmp_dirname()
            d = f.unpack(self.extracted2_path)
            src_path = d.get_path()
        else:
            raise ValueError("Filetype %s cannot be processed" % (d.get_type(),))

        stdout, stderr, _ = runcmd(["licenselib/cucos_license_check.py", src_path])

        ret.result = json.loads(stdout)
        ret.meta['stderr'] = json.loads(stderr)
        ret.meta['tool'] = "cucos_license_check"

        return ret

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
