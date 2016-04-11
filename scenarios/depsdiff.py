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


class Depsdiff(Scenario):
    ''' get differences of dependencies '''

    language = cli.SwitchAttr("--language", str,
                              help="specify project language",
                              default="detect")

    tool = cli.SwitchAttr("--tool", str,
                          help="specify tool to analyse project with",
                          default="default")

    tool1 = cli.SwitchAttr("--tool1", str,
                           help="specify tool to analyse project 1 with",
                           default=None, excludes=["--tool"])

    tool2 = cli.SwitchAttr("--tool2", str,
                           help="specify tool to analyse project 2 with",
                           default=None, excludes=["--tool"])

    language1 = cli.SwitchAttr("--language1", str,
                               help="specify language of project 1",
                               default=None, excludes=["--language"])

    language2 = cli.SwitchAttr("--language2", str,
                               help="specify language of project 2",
                               default=None, excludes=["--language"])

    def construct_opts(self, first):
        opts = {}
        language = self.language1 if first else self.language2
        tool = self.tool1 if first else self.tool2

        if language:
            opts['language'] = language
        else:
            opts['language'] = self.language

        if tool:
            opts['tool'] = tool
        else:
            opts['tool'] = self.tool

        return opts

    def main(self, project_file1, project_file2):
        with self.get_system() as system:

            opts1 = self.construct_opts(first=True)
            opts2 = self.construct_opts(first=False)

            with open(project_file1, 'r') as f:
                file_id1 = system.async_call.upload(f.read())

            with open(project_file2, 'r') as f:
                file_id2 = system.async_call.upload(f.read())

            deps1 = system.async_call.deps_analysis(file_id1.result, opts1)
            deps2 = system.async_call.deps_analysis(file_id2.result, opts2)

            depsdiff = system.async_call.deps_diff(deps1.result, deps2.result)

            print dict2json(depsdiff.result)

        return 0

if __name__ == '__main__':
    sys.exit(1)
