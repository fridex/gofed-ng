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
from exposed import exposed_action1
from common.service.service import Service
from common.service.serviceEnvelope import ServiceEnvelope

class Service1Service(Service):
	@classmethod
	def signal_startup(cls, config):
		print "got startup signal"

	@classmethod
	def signal_termination(cls):
		print "got termination signal"

	def signal_connect(self):
		print "got connect signal"

	def signal_disconnect(self):
		print "got disconnect signal"

	def signal_process(self):
		print "got process signal"

	def signal_processed(self):
		print "got processed signal"
		pass

	def exposed_action1(self):
		return { "remote": exposed_action1() }

if __name__ == "__main__":
	ServiceEnvelope.serve(Service1Service)

