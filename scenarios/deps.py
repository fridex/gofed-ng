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
from common.helpers.output import log
from common.helpers.utils import dict2json
from scenario import Scenario, SwitchAttr, Flag


class Deps(Scenario):
    ''' analyze dependencies of a project based on source code '''

    file_path = SwitchAttr(["--file", "-f"], str,
                           help="Local file to run dependency analysis on", excludes=["-p", "--store"])

    proj_commit = SwitchAttr(["--project-commit", "-c"], str,
                              help="Commit of the project", requires=["-p"])

    proj_commit_date = SwitchAttr(["--project-commit-date"], str,
                                  help="Commit date (needed when storing results)", requires=["--project-commit"])

    project = SwitchAttr(["--project", "-p"], str,
                         help="Remote project to run dependency analysis on", requires=["-c"])

    store = Flag(["--store"],
                 help="Save computed results to DepsStorage")

    meta = Flag(["--meta", "-m"],
                help="show meta information in output as well")

    package_name = SwitchAttr(["--package-name"], str,
                              help="Package to run dependency analysis on",
                              requires=["--package-version", "--package-release", "--package-distro"],
                              excludes=["--file", "--project", "--package"])

    pkg_version = SwitchAttr(["--package-version"], str,
                                 help="Package version to run dependency analysis on")

    pkg_release = SwitchAttr(["--package-release"], str,
                                 help="Package release to run dependency analysis on")

    pkg_distro = SwitchAttr(["--package-distro"], str,
                                 help="Package distro to run dependency analysis on")

    pkg_arch = SwitchAttr(["--package-arch"], str,
                                help="Package architecture to run dependency analysis on;" +
                                " if omitted, source RPM is used")

    package = SwitchAttr(["--package"], str,
                         help="Package name (fully qualified name) to run " +
                              "dependency analysis on (e.g. flannel-0.5.5-5.fc24.x86_64.rpm)")

    def main(self):
        with self.get_system() as system:
            if self.file_path:
                with open(self.file_path, 'r') as f:
                    file_id = system.async_call.upload(f.read())
            elif self.project:
                file_id = system.async_call.tarball_get(self.project, self.proj_commit)
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

            deps = system.async_call.deps_analysis(file_id.get_result())

            if self.store and self.project:
                if not self.proj_commit_date:
                    raise ValueError("Commit date required when storing dependency results of a project")
                system.call.deps_store_project(self.project, self.proj_commit,
                                               self.proj_commit_date, deps.result, deps.meta)
            elif self.store and self.package_name:
                system.call.deps_store_package(self.package_name, self.pkg_version, self.pkg_release,
                                               self.pkg_distro, deps.result, deps.meta)
            elif self.store:
                # TODO: when --package
                raise RuntimeError("Store Deps not supported")

            if self.meta:
                print dict2json(deps.get_result_with_meta())
            else:
                print dict2json(deps.result)

        return 0

if __name__ == '__main__':
    sys.exit(1)
