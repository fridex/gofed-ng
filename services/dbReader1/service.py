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
from common.database.dbReaderProjectAPI import DBreaderProjectAPI
from common.service.service import Service

class DBReader1Service(Service, DBreaderProjectAPI):
	def on_connect(self):
		pass

	def on_disconnect(self):
		pass

	def exposed_get_project_api(self, project, commit = None):
		return "query result of API from db for project '%s' and commint '%s'" \
				% (str(project), str(commit))

	def exposed_get_project_dependencies(self, project, commit = None):
		return "query result of DEPS from db for project '%s' and commint '%s'" \
				% (str(project), str(commit))

if __name__ == "__main__":
	sys.exit(1)

