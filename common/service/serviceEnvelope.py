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

import os
import sys
import signal
from plumbum import cli
from rpyc.utils.server import ThreadPoolServer
from rpyc.utils.registry import UDPRegistryClient, TCPRegistryClient, REGISTRY_PORT
from rpyc.lib import setup_logger
from common.helpers.output import log
from common.helpers.utils import config2dict, get_time_str

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


class ServiceEnvelope(cli.Application):

    @classmethod
    def serve(cls, service_class):
        cls.SERVICE_CLASS = service_class
        return ServiceEnvelope.run()

    @cli.switch("--info", excludes=['--config'])
    def info(self):
        print "Service name:\t\t%s\nService version:\t%s\nService description:\n\t%s" % \
            (ServiceEnvelope.SERVICE_CLASS.get_service_name(),
             ServiceEnvelope.SERVICE_CLASS.get_service_version(),
             str(ServiceEnvelope.SERVICE_CLASS.__doc__)
             )
        sys.exit(1)

    @cli.switch("--config", str)
    def config(self, config):
        ''' Use config instead of command line arguments '''
        self.conf = ConfigParser({
            'ipv6': "False",
            'host': "localhost",
            'port': "118822",
            'quiet': "False",
            'logfile': "service.log",
            'register': "False",
            'registry-type': "UDP",
            'registry-port': "18811",
            'registry-host': "localhost",
            'max-client-count': "20",
            'max-requests-per-client': "10",
            'system-json': "system.json"
        })
        self.conf.read(config)

        name = ServiceEnvelope.SERVICE_CLASS.__name__[:-len('Service')].upper()

        if name in self.conf.sections():
            self.ipv6 = self.conf.getboolean(name, "ipv6")
            self.host = self.conf.get(name, "host")
            self.port = self.conf.getint(name, "port")
            self.logfile = self.conf.get(name, "logfile")
            self.auto_register = self.conf.getboolean(name, "register")
            self.registry_type = self.conf.get(name, "registry-type")
            self.registry_port = self.conf.getint(name, "registry-port")
            self.registry_host = self.conf.get(name, "registry-host")
            self.max_client_count = self.conf.getint(name, "max-client-count")
            self.max_requests_per_client = self.conf.getint(
                name, "max-requests-per-client")
            self.quiet = self.conf.getboolean(name, "quiet")
            self.system_json = self.conf.get(name, "system-json")

        if self.port is None:
            self.port = REGISTRY_PORT

    @staticmethod
    def signal_handler(sig, frame):
        if ServiceEnvelope.worker_pid != 0:
            os.kill(ServiceEnvelope.worker_pid, signal.SIGTERM)
            ServiceEnvelope.SERVICE_CLASS.on_termination()

    def run_worker_process(self):
        setup_logger(self.quiet, log)

        if self.registry_type == "UDP":
            if self.registry_host is None:
                self.registry_host = "255.255.255.255"
            self.registrar = UDPRegistryClient(
                ip=self.registry_host, port=self.registry_port)
        else:
            if self.registry_host is None:
                raise ValueError(
                    "With TCP registry, you must specify --registry-host")
            self.registrar = TCPRegistryClient(
                ip=self.registry_host, port=self.registry_port)

        t = ThreadPoolServer(ServiceEnvelope.SERVICE_CLASS, hostname=self.host, port=self.port,
                             reuse_addr=True, ipv6=self.ipv6,
                             registrar=self.registrar, auto_register=self.auto_register,
                             nbThreads=self.max_client_count, requestBatchSize=self.max_requests_per_client,
                             protocol_config={'exposed_prefix': '',
                                              'log_exceptions': True})
        t.start()

    def main(self):
        try:
            self.conf
        except Exception:
            log.error("config option is mandatory, see '--help'")
            sys.exit(1)

        self.conf = config2dict(self.conf)

        cls = ServiceEnvelope.SERVICE_CLASS
        logfile = self.logfile if self.logfile != '-' else None
        verbose = not self.quiet
        name = cls.get_service_name()
        version = cls.get_service_version()

        log.init(logfile, verbose, name)
        log.critical("Service starting at %s, version is %s" %
                     (get_time_str(), version))

        service_cls = ServiceEnvelope.SERVICE_CLASS
        service_cls.on_startup(self.conf, self.system_json)

        ServiceEnvelope.worker_pid = os.fork()

        if ServiceEnvelope.worker_pid == 0:
            self.run_worker_process()
        else:
            signal.signal(signal.SIGINT, ServiceEnvelope.signal_handler)
            signal.signal(signal.SIGTERM, ServiceEnvelope.signal_handler)

            try:
                while os.waitpid(ServiceEnvelope.worker_pid, 0):
                    pass
            except Exception:
                pass

            # finish logging and ensure that all messages are flushed
            log.critical("Service terminated at %s" % get_time_str())
            log.close()

if __name__ == "__main__":
    sys.exit(1)
