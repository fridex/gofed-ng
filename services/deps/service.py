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
from common.service.computationalService import ComputationalService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action
from common.service.serviceResult import ServiceResult
from common.system.extractedRpmFile import ExtractedRpmFile
from common.system.extractedSrpmFile import ExtractedSrpmFile
from common.system.extractedTarballFile import ExtractedTarballFile

import gofedlib.gosymbolsextractor as gofedlib


class DepsService(ComputationalService):
    ''' Dependencies checks '''

    def signal_process(self):
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
    def deps_analysis(self, file_id, opts=None):
        '''
        Get deps of a file
        @param file_id: file to be analysed
        @param opts: additional analysis opts
        @return: list of dependencies
        '''
        ret = ServiceResult()
        default_opts = {'language': 'detect', 'tool': 'default', 'exclude_dirs': []}

        if opts is None:
            opts = default_opts
        else:
            default_opts.update(opts)
            opts = default_opts

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

        # TODO: handle opts
        if not 'ippath' in opts:
            raise ValueError("gofedlib's deps analyzer expects spectified 'ippath', in opts")

        ret.result = gofedlib.project_packages(src_path, opts['ippath'], opts['exclude_dirs'])
        ret.meta = {'language': 'golang', 'tool': 'gofedlib'}

        return ret

    @action
    def deps_diff(self, deps1, deps2, opts=None):
        '''
        Make a diff of dependencies
        @param deps1: the first dependency list
        @param deps2: the second dependency list
        @param opts: additional analysis opts
        @return: list of dependency differences
        '''
        default_opts = {'language': 'detect', 'tool': 'default'}
        ret = ServiceResult()

        if opts is None:
            opts = default_opts
        else:
            default_opts.update(opts)
            opts = default_opts

        # TODO: implement deps difference
        raise NotImplementedError("Currently not implemented")

        return ret

if __name__ == "__main__":
    ServiceEnvelope.serve(DepsService)
