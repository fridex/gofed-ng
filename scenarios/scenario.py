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
from common.system.system import System


class Flag(cli.Flag):
    pass


class SwitchAttr(cli.SwitchAttr):
    pass


class Scenario(cli.Application):

    def get_system(self):
        return System(self.parent.get_config(), self.parent.get_system_json_path())

    def prepare_file_by_args(self, system):
        '''
        Prepare file ID based on scenario arguments
        @return: file id
        '''
        file_id = None

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

        return file_id

    def prepare_files2_by_args(self, system):
        file1_id = None
        file2_id = None

        if self.file1_path:
            with open(self.file1_path, 'r') as f:
                file1_id = system.async_call.upload(f.read())
        elif self.project1:
            file1_id = system.async_call.tarball_get(self.project1, self.proj1_commit)
        elif self.package1_name:
            if self.pkg1_arch:
                file1_id = system.async_call.rpm_get(self.package1_name, self.pkg1_version,
                                                     self.pkg1_release, self.pkg1_distro, self.pkg1_arch)
            else:
                file1_id = system.async_call.rpm_src_get(self.package1_name, self.pkg1_version,
                                                         self.pkg1_release, self.pkg1_distro)
        elif self.package1:
            file1_id = system.async_call.rpm_get_by_name(self.package1)

        if self.file2_path:
            with open(self.file2_path, 'r') as f:
                file2_id = system.async_call.upload(f.read())
        elif self.project2:
            file2_id = system.async_call.tarball_get(self.project2, self.proj2_commit)
        elif self.package2_name:
            if self.pkg2_arch:
                file2_id = system.async_call.rpm_get(self.package2_name, self.pkg2_version,
                                                     self.pkg2_release, self.pkg2_distro, self.pkg2_arch)
            else:
                file2_id = system.async_call.rpm_src_get(self.package2_name, self.pkg2_version,
                                                         self.pkg2_release, self.pkg2_distro)
        elif self.package2:
            file2_id = system.async_call.rpm_get_by_name(self.package2)

        return file1_id, file2_id

if __name__ == "__main__":
    sys.exit(1)
