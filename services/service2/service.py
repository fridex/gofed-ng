#!/bin/python
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
from common.service.service import Service
from exposed import exposed_action2, exposed_action3
from common.service.serviceEnvelope import ServiceEnvelope

class Service2Service(Service):
	def signal_connect(self):
		pass

	def signal_disconnect(self):
		pass

	def signal_process(self):
		pass

	def signal_processed(self):
		pass

	def exposed_action2(self, project):
		return { "remote": exposed_action2(project) }

	def exposed_action3(self, project, commit):
		return { "remote:": exposed_action3(project, commit) }

if __name__ == "__main__":
	ServiceEnvelope.serve(Service2Service)

