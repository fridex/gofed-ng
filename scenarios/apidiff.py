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
from api import Api


class Apidiff(Scenario):
    ''' API diff analysis '''

    # First file

    file1_path = SwitchAttr(["--file1"], str,
                            help="Local file to run API on")

    proj1_commit = SwitchAttr(["--project1-commit"], str,
                              help="Commit of the project", requires=["--project1"])

    project1 = SwitchAttr(["--project1"], str,
                          help="Remote project to run API analysis on", requires=["--project1-commit"])

    package1_name = SwitchAttr(["--package1-name"], str,
                               help="Package to run API analysis on",
                               requires=["--package1-version", "--package1-release", "--package1-distro"],
                               excludes=["--file1", "--project1", "--package1"])

    pkg1_version = SwitchAttr(["--package1-version"], str,
                              help="Package version to run API analysis on")

    pkg1_release = SwitchAttr(["--package1-release"], str,
                              help="Package release to run API analysis on")

    pkg1_distro = SwitchAttr(["--package1-distro"], str,
                             help="Package distro to run API analysis on")

    pkg1_arch = SwitchAttr(["--package1-arch"], str,
                           help="Package architecture to run API analysis on; if omitted, source RPM is used")

    package1 = SwitchAttr(["--package1"], str,
                          help="Package name (fully qualified name) to run " +
                               "API analysis on (e.g. flannel-0.5.5-5.fc24.x86_64.rpm)")

    # Second file

    file2_path = SwitchAttr(["--file2"], str,
                            help="Local file to run API on")

    proj2_commit = SwitchAttr(["--project2-commit"], str,
                              help="Commit of the project", requires=["--project2"])

    project2 = SwitchAttr(["--project2"], str,
                          help="Remote project to run API analysis on", requires=["--project2-commit"])

    package2_name = SwitchAttr(["--package2-name"], str,
                               help="Package to run API analysis on",
                               requires=["--package2-version", "--package2-release", "--package2-distro"],
                               excludes=["--file2", "--project2", "--package2"])

    pkg2_version = SwitchAttr(["--package2-version"], str,
                              help="Package version to run API analysis on")

    pkg2_release = SwitchAttr(["--package2-release"], str,
                              help="Package release to run API analysis on")

    pkg2_distro = SwitchAttr(["--package2-distro"], str,
                             help="Package distro to run API analysis on")

    pkg2_arch = SwitchAttr(["--package2-arch"], str,
                           help="Package architecture to run API analysis on; if omitted, source RPM is used")

    package2 = SwitchAttr(["--package2"], str,
                          help="Package name (fully qualified name) to run " +
                               "API analysis on (e.g. flannel-0.5.5-5.fc24.x86_64.rpm)")

    meta = Flag(["--meta", "-m"],
                help="show meta information in output as well")

    def main(self):
        with self.get_system() as system:
            file1_id, file2_id = self.prepare_files2_by_args(system)

            if not file1_id:
                raise ValueError("First file not specified")

            if not file2_id:
                raise ValueError("Second file not specified")

            api1 = system.async_call.api_analysis(file1_id.result)
            api2 = system.async_call.api_analysis(file2_id.result)

            apidiff = system.async_call.api_diff(api1.result, api2.result)

            if self.meta:
                print dict2json(apidiff.get_result_with_meta())
            else:
                print dict2json(apidiff.result)

        return 0

if __name__ == '__main__':
    sys.exit(1)
