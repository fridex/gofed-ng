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
from common.helpers.output import log
from scenario import Scenario, Flag, SwitchAttr


class Api(Scenario):
    ''' API analysis example '''

    file_path = SwitchAttr(["--file", "-f"], str,
                           help="Local file to run API on", excludes=["-p", "--store"])

    commit = SwitchAttr(["--commit", "-c"], str,
                        help="Commit of ", requires=["-p"])

    project = SwitchAttr(["--project", "-p"], str,
                         help="Remote project to run API analysis on", requires=["-c"])

    store = Flag(["--store"],
                 help="Save computed results to ApiStorage")

    meta = Flag(["--meta", "-m"],
                help="show meta information in output as well")

    package_name = SwitchAttr(["--package-name"], str,
                              help="Package to run API analysis on",
                              requires=["--package-version", "--package-release", "--package-distro"],
                              excludes=["--file", "--project", "--package"])

    pkg_version = SwitchAttr(["--package-version"], str,
                                 help="Package version to run API analysis on")

    pkg_release = SwitchAttr(["--package-release"], str,
                                 help="Package release to run API analysis on")

    pkg_distro = SwitchAttr(["--package-distro"], str,
                                 help="Package distro to run API analysis on")

    pkg_arch = SwitchAttr(["--package-arch"], str,
                                help="Package architecture to run API analysis on; if omitted, source RPM is used")

    package = SwitchAttr(["--package"], str,
                         help="Package name (fully qualified name) to run " +
                              "API analysis on (e.g. flannel-0.5.5-5.fc24.x86_64.rpm)")

    def main(self):
        with self.get_system() as system:
            if self.file_path:
                with open(self.file_path, 'r') as f:
                    file_id = system.async_call.upload(f.read())
            elif self.project:
                file_id = system.async_call.tarball_get(self.project, self.commit)
            elif self.package_name:
                if self.pkg_arch:
                    file_id = system.async_call.rpm_get(self.package_name, self.pkg_version,
                                                        self.pkg_release, self.pkg_distro, self.pkg_arch)
                else:
                    file_id = system.async_call.rpm_src_get(self.package_name, self.pkg_version,
                                                            self.pkg_release, self.pkg_distro)
            elif self.package:
                file_id = system.async_call.rpm_get_by_name(self.package)
            else:
                log.error("No action to be performed")
                return 1

            api = system.async_call.api_analysis(file_id.get_result())

            if self.store and self.project:
                system.call.api_store_project(self.project, self.commit, self.commit_date, api.result, api.meta)
            elif self.store and self.package_name:
                system.call.api_store_package(self.package, self.pkg_version, self.pkg_release,
                                              self.pkg_distro, api.result, api.meta)
            else:
                raise RuntimeError("Store API of a local file is not supported")

            if self.meta:
                print dict2json(api.get_result_with_meta())
            else:
                print dict2json(api.result)

        return 0

if __name__ == '__main__':
    sys.exit(1)
