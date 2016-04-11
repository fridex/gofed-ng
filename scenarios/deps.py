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

import sys
from plumbum import cli
from common.helpers.utils import dict2json
from scenario import Scenario


class Deps(Scenario):
    ''' analyze dependencies of a project '''

    language = cli.SwitchAttr("--language", str,
                            help="specify project language",
                            default="detect")

    tool = cli.SwitchAttr("--tool", str,
                              help="specify import path for golang projects",
                              default="default")

    def construct_opts(self):
        opts = {}

        if self.language:
            opts['language'] = self.language

        if self.tool:
            opts['language'] = self.language

        return opts


    def main(self, project_file):
        with self.get_system() as system:

            opts = self.construct_opts()

            with open(project_file, 'r') as f:
                file_id = system.async_call.upload(f.read())

            deps = system.async_call.deps_analysis(file_id.get_result(), opts)

            print dict2json(deps.result)

        return 0

if __name__ == '__main__':
    sys.exit(1)
