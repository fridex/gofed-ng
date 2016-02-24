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
import StringIO
from common.service.serviceResult import ServiceResult
from common.service.computationalService import ComputationalService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action
from common.system.srpmFile import SrpmFile
from common.system.textFile import TextFile
from common.system.extractedSrpmFile import ExtractedSrpmFile

from specker.modules.specFileParser import SpecFileParser
from specker.modules.specFileRenderer import SpecFileRenderer
from specker.modules.specModelWriter import SpecModelWriter
from specker.modules.specModelReader import SpecModelReader
from specker.modules.specDefaultEditor import SpecDefaultEditor


class SpecService(ComputationalService):
    ''' Specfile analysing and processing '''

    def signal_init(self):
        self.tmpfile_path = None
        self.extracted1_path = None

    def signal_destruct(self):
        if self.tmpfile_path is not None:
            os.remove(self.tmpfile_path)

        if self.extracted1_path is not None:
            shutil.rmtree(self.extracted1_path)

    def _prepare_file(self, file_id):
        self.tmpfile_path = self.get_tmp_filename()
        with self.get_system() as system:
            f = system.download(file_id, self.tmpfile_path)

        if not isinstance(f, SrpmFile) and not isinstance(f, TextFile):
            raise ValueError("Unable to process filetype %s" % (f.get_type(),))

        if isinstance(f, SrpmFile):
            self.extracted1_path = self.get_tmp_dirname()
            d = f.unpack(self.extracted1_path)
            input_path = d.get_spec_path()
        else:
            # we are expecting TextFile to be SpecFile
            input_path = f.get_path()

        return input_path

    @staticmethod
    def _specker_call(method, input_path):
        output_str = StringIO.StringIO()
        parser = SpecFileParser(SpecModelWriter())
        with open(input_path, 'r') as f_in:
            parser.init(f_in)
        parser.parse()
        spec = SpecDefaultEditor(SpecModelReader(parser.get_model_writer().get_model()), parser.get_model_writer())
        spec = SpecFileRenderer(spec.get_model_reader())
        method(spec, ['*'], output_str)

        return output_str.getvalue()

    @staticmethod
    def _parse_specker_output(output):
        ret = {}
        for line in output.split('\n'):
            print line
            if len(line) == 0:
                # blank line on output
                break
            line = line.split(':')
            package = line[0]
            value = line[1]
            if package not in ret:
                ret[package] = []
            ret[package].append(value)

        return ret

    @action
    def spec_provides(self, file_id):
        '''
        Get all provides for a package
        @param file_id: a file id of a specfile/src.rpm stored in the system
        @return: list of provides per package
        '''
        ret = ServiceResult()

        input_path = self._prepare_file(file_id)
        output = self._specker_call(SpecFileRenderer.provides_show, input_path)
        ret.result = self._parse_specker_output(output)
        ret.meta = {'tool': 'specker'}

        return ret

    @action
    def spec_requires(self, file_id):
        '''
        Get all requires for a package
        @param file_id: a file id of a specfile/src.rpm stored in the system
        @return: list of requires per package
        '''
        ret = ServiceResult()

        input_path = self._prepare_file(file_id)
        output = self._specker_call(SpecFileRenderer.requires_show, input_path)
        ret.result = self._parse_specker_output(output)
        ret.meta = {'tool': 'specker'}

        return ret

    @action
    def spec_buildrequires(self, file_id):
        '''
        Get all buildrequires for a package
        @param specfile_id: a file id of a specfile/src.rpm stored in the system
        @return: list of buildrequires per package
        '''
        ret = ServiceResult()

        input_path = self._prepare_file(file_id)
        output = self._specker_call(SpecFileRenderer.buildrequires_show, input_path)
        ret.result = self._parse_specker_output(output)
        ret.meta = {'tool': 'specker'}

        return ret

if __name__ == "__main__":
    ServiceEnvelope.serve(SpecService)
