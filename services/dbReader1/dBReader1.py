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

from plumbum import cli
from rpyc import Service
from rpyc.utils.server import ThreadedServer, ForkingServer
from rpyc.utils.classic import DEFAULT_SERVER_PORT
from rpyc.utils.registry import REGISTRY_PORT
from rpyc.utils.registry import UDPRegistryClient, TCPRegistryClient
from rpyc.lib import setup_logger
from common.helpers.version import VERSION

try:
	from configparser import ConfigParser
except ImportError:
	from ConfigParser import ConfigParser

from service import DBReader1

class ServiceServer(cli.Application):
	PROGNAME = "DBReader1"
	VERSION = VERSION

	mode = cli.SwitchAttr(["-m", "--mode"], cli.Set("threaded", "forking"),
		default = "threaded", help = "The serving mode (threaded, forking, for "
		"inetd, etc.)")

	port = cli.SwitchAttr(["-p", "--port"], cli.Range(0, 65535), default = None,
		help="The TCP listener port; default = %s" %
			(DEFAULT_SERVER_PORT), group = "Socket Options")
	host = cli.SwitchAttr(["--host"], str, default = "", help = "The host to bind to. "
		"The default is INADDR_ANY", group = "Socket Options")
	ipv6 = cli.Flag(["--ipv6", "-6"], help = "Enable IPv6", group = "Socket Options")

	logfile = cli.SwitchAttr("--logfile", str, default = None, help="Specify the log file to use; "
		"the default is stderr", group = "Logging")
	quiet = cli.Flag(["-q", "--quiet"], help = "Quiet mode (only errors will be logged)",
		group = "Logging")

	auto_register = cli.Flag("--register", help = "Asks the server to attempt registering with "
		"a registry server. By default, the server will not attempt to register",
		group = "Registry")
	registry_type = cli.SwitchAttr("--registry-type", cli.Set("UDP", "TCP"),
		default = "UDP", help="Specify a UDP or TCP registry", group = "Registry")
	registry_port = cli.SwitchAttr("--registry-port", cli.Range(0, 65535), default=REGISTRY_PORT,
		help = "The registry's UDP/TCP port", group = "Registry")
	registry_host = cli.SwitchAttr("--registry-host", str, default = None,
		help = "The registry host machine. For UDP, the default is 255.255.255.255; "
		"for TCP, a value is required", group = "Registry")

	def config(self, config):
		''' Use config instead of command line arguments'''
		if config:
			conf = ConfigParser({
	 			'mode': "threaded",
	 			'ipv6': "False",
	 			'host': "localhost",
	 			'port': "118822",
	 			'logfile': "service.log",
				'register': "False",
				'registry-type': "UDP",
				'registry-port': "18811",
				'registry-host': "localhost"
				})
			conf.read(config)

		self.mode = conf.get("db", "mode").lower()
		if self.mode not in ["threaded", "forking"]:
			raise ValueError("Invalid mode %r" % self.mode)

	 	self.ipv6 = conf.getboolean('db', "ipv6")
	 	self.host = conf.get('db', "host")
	 	self.port = conf.getint('db', "port")
	 	self.logfile = conf.get('db', "logfile")
		self.auto_register = conf.getboolean('db', "register")
		self.registry_type = conf.get('db', "registry-type")
		self.registry_port = conf.getint('db', "registry-port")
		self.registry_host = conf.get('db', "registry-host")

	def main(self):
		if self.registry_type == "UDP":
			if self.registry_host is None:
				self.registry_host = "255.255.255.255"
			self.registrar = UDPRegistryClient(ip = self.registry_host, port = self.registry_port)
		else:
			if self.registry_host is None:
				raise ValueError("With TCP registry, you must specify --registry-host")
			self.registrar = TCPRegistryClient(ip = self.registry_host, port = self.registry_port)

		if self.port is None:
			self.port = default_port

		setup_logger(self.quiet, self.logfile)

		if self.mode == "threaded":
			self._serve_mode(ThreadedServer)
		elif self.mode == "forking":
			self._serve_mode(ForkingServer)

	def _serve_mode(self, factory):
		t = factory(DBReader1, hostname = self.host, port = self.port,
			reuse_addr = True, ipv6 = self.ipv6,
			registrar = self.registrar, auto_register = self.auto_register)
		t.start()

if __name__ == "__main__":
	ServiceServer.run()
