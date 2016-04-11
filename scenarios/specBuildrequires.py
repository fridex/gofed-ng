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
from scenario import Scenario


class SpecBuildrequires(Scenario):
    ''' get all Buildrequires from a specfile or source RPM '''

    def main(self, projectfile):
        with self.get_system() as system:

            with open(projectfile, 'r') as f:
                file_id = system.async_call.upload(f.read())

            br = system.async_call.spec_buildrequires(file_id.get_result())

            print dict2json(br.result)

        return 0

if __name__ == '__main__':
    sys.exit(1)
