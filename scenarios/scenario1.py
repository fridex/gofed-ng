#!/bin/bash
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
from common.helpers.utils import json_pretty_format
from scenario import Scenario

class Scenario1(Scenario):
	''' API diff analysis example '''
	def main(self, project_file1, project_file2):
		with self.get_system() as system:

			with open(project_file1, 'r') as f:
				file1 = system.async_call.upload(f.read())

			with open(project_file2, 'r') as f:
				file2 = system.async_call.upload(f.read())

			api1 = system.async_call.api(file1.get_result())
			api2 = system.async_call.api(file2.get_result())

			apidiff = system.call.apidiff(api1.get_result(), api2.get_result())

			print json_pretty_format(apidiff.get_result())

		return 0

if __name__ == '__main__':
	sys.exit(1)

