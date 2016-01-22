#!/bin/python
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
from common.registry.registryClient import RegistryClient
from system import System
import rpyc

try:
	from configparser import ConfigParser
except ImportError:
	from ConfigParser import ConfigParser

from rpyc.utils.registry import REGISTRY_PORT, DEFAULT_PRUNING_TIMEOUT

from scenarios.userScenario1.scenario import UserScenario1
from scenarios.userScenario2.scenario import UserScenario2

GOFED_CONFIG="gofed.conf"

class Gofed(cli.Application):
	def config(self, config = GOFED_CONFIG):
		''' Use config '''
		conf = ConfigParser()
		conf.read(config)
		self.config = conf

	def main(self):
		self.config()

		system = System(self.config)

		UserScenario1().run(system)
		UserScenario2().run(system)

if __name__ == "__main__":
	Gofed.run()

