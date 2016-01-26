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

from scenarios.abstractScenario import AbstractScenario

class UserScenario1(AbstractScenario):
	def run(self, system):
		data = system.get_project_api("k8s", "commit")
		print "Running user scenario 1"
		out1 = system.action1()
		print "Action1 output: %s" % out1
		in1 = "(%s - %s)" % (out1, data)
		print "Action2 input: %s" % in1
		out2 = system.action2(in1)
		print "Action2 output: %s" % out2
		return out2

