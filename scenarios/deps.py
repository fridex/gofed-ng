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
from common.helpers.utils import dict2json
from scenario import Scenario, SwitchAttr, Flag


class Deps(Scenario):
    ''' analyze dependencies of a project '''

    language = SwitchAttr(["--language"], str,
                          help="specify projects language",
                          default="detect")

    tool = SwitchAttr(["--tool"], str,
                      help="specify tool to analyse projects with",
                      default="default")

    store = Flag(["--store"],
                 help="store result in DepsStorage")

    file_path = SwitchAttr(["--file", "-f"], str,
                           help="Local file to run API on", excludes=["-p", "--store"])

    commit = SwitchAttr(["--commit", "-c"], str,
                        help="Commit of ", requires=["-p"])

    project = SwitchAttr(["--project", "-p"], str,
                         help="Remote project to run API analysis on", requires=["-c"])

    meta = Flag(["--meta", "-m"],
                help="show meta information in output as well")

    def construct_opts(self):
        opts = {}

        if self.language:
            opts['language'] = self.language

        if self.tool:
            opts['language'] = self.language

        return opts

    def main(self):

        opts = self.construct_opts()

        with self.get_system() as system:

            if self.file_path:
                with open(self.file_path, 'r') as f:
                    file_id = system.async_call.upload(f.read())
            elif self.project:
                file_id = system.async_call.tarball_get(self.project, self.commit)

            deps = system.async_call.deps_analysis(file_id.get_result(), opts)

            if self.store and self.project:
                system.call.deps_store_project(self.project, self.commit, deps.result, deps.meta)
            elif self.store:
                raise NotImplementedError("Not handled")

            if self.meta:
                print dict2json(deps.get_result_with_meta())
            else:
                print dict2json(deps.result)

        return 0

if __name__ == '__main__':
    sys.exit(1)
