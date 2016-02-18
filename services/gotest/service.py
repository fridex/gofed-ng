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

import os
from common.helpers.output import log
from common.service.computationalService import ComputationalService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action


class GoTestService(ComputationalService):
    ''' Golang tests '''

    @action
    def gotest_run(self, file_id):
        '''
        Run a golang test on a file
        @param file_id: a file id referencing a file with tests and sources to be tested
        @return: test statistics
        '''
        # This will be implemented using a custom tool, which needs to be designed
        # and implemented
        #  * run each test inside a docker instance (?)
        #    * a user can specify on which Fedora version
        #  * as simple tool as possible
        #  * design a configuration file, which will say how to prepare the
        #  environment for tests
        #    * it could be a parameter for gotest_run() or it can be a part of
        #    file (e.g. in root dir of fedora package git repo)
        #  * needs brainstorming...
        #  * ...
        return "TODO"

if __name__ == "__main__":
    ServiceEnvelope.serve(GoTestService)
