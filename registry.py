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
from rpyc.utils.registry import REGISTRY_PORT, DEFAULT_PRUNING_TIMEOUT
from rpyc.utils.registry import UDPRegistryServer, TCPRegistryServer
from rpyc.lib import setup_logger

try:
	from configparser import ConfigParser
except ImportError:
	from ConfigParser import ConfigParser

class RegistryServer(cli.Application):

	config = cli.SwitchAttr(["-c", "--conf"], str, default = None,
		help = "Config file")

	mode = cli.SwitchAttr(["-m", "--mode"], cli.Set("UDP", "TCP"), default = "UDP",
		help = "Serving mode")

	ipv6 = cli.Flag(["-6", "--ipv6"], help="use ipv6 instead of ipv4")

	port = cli.SwitchAttr(["-p", "--port"], cli.Range(0, 65535), default = REGISTRY_PORT,
		help = "The UDP/TCP listener port")

	logfile = cli.SwitchAttr(["--logfile"], str, default = None,
		help = "The log file to use; the default is stderr")

	quiet = cli.Flag(["-q", "--quiet"], help = "Quiet mode (only errors are logged)")

	timeout = cli.SwitchAttr(["-t", "--timeout"], int,
		default = DEFAULT_PRUNING_TIMEOUT, help = "Set a custom pruning timeout (in seconds)")

	@cli.switch("--config", str, excludes = ['-m', '-6', '-p', '--logfile', '-q', '-t'])
	def config(self, config):
		''' Use config instead of command line arguments'''
		if config:
			conf = ConfigParser({
				"mode": "UDP",
				"ipv6": False,
				"port": REGISTRY_PORT,
				"logfile": None,
				"quiet": True,
				"timeout": DEFAULT_PRUNING_TIMEOUT})
			conf.read(config)

		self.mode = conf.get("registry", "mode").upper()
		if self.mode not in ["UDP", "TCP"]:
			raise ValueError("Invalid mode %r" % mode)

		self.ipv6 = conf.getboolean("registry", "ipv6")
		self.port = conf.getint("registry", "port")
		self.logfile = conf.get("registry", "logfile")
		self.quiet = conf.getboolean("registry", "quiet")

	def main(self):
		if self.mode == "UDP":
			server = UDPRegistryServer(host = '::' if self.ipv6 else '0.0.0.0', port = self.port,
				pruning_timeout = self.timeout)
		elif self.mode == "TCP":
			server = TCPRegistryServer(port = self.port, pruning_timeout = self.timeout)
		setup_logger(self.quiet, self.logfile)
		print >> sys.stderr, "Starting registry on port %s..." % self.port
		server.start()


if __name__ == "__main__":
	RegistryServer.run()

