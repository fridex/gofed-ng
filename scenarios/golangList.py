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
from common.helpers.utils import format_str
from scenario import Scenario, SwitchAttr


class GolangList(Scenario):
    ''' list all available golang packages packaged in Fedora '''

    format = SwitchAttr(["--format"], str,
                        help="specify output format (%a, %c, %d, %k, %m, %n, %r, %S, %s, %u)")

    def main(self):
        with self.get_system() as system:
            packages = system.async_call.goland_package_listing()

            if self.format:
                for package in packages.result:
                    fmt = {
                        '\%a': package["acls"],
                        '\%c': package["creation_date"],
                        '\%d': package["description"],
                        '\%k': package["koschei_monitor"],
                        '\%m': package["monitor"],
                        '\%n': package["name"],
                        '\%r': package["review_url"],
                        '\%S': package["status"],
                        '\%s': package["summary"],
                        '\%u': package["upstream_url"]
                    }

                    print(format_str(self.format, fmt))
            else:
                print(dict2json(packages.result))

        return 0

if __name__ == '__main__':
    sys.exit(1)
