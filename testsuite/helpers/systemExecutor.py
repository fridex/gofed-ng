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
import os
from tempfile import NamedTemporaryFile
from serviceConfig import ServiceConfig
from registryConfig import RegistryConfig
from testProcess import TestProcess
from utils import service_path2service_name

REGISTRY_DEFAULT_PATH = 'registry.py'


class SystemExecutor(object):

    def __init__(self, services_list, registry=None):
        self._services_list = services_list
        self._registry = registry

        self._service_processes = []
        self._registry_process = None
        self._tmp_files = []

    def _get_tempfile(self):
        with NamedTemporaryFile(delete=False) as tmp:
            name = tmp.name
            self._tmp_files.append(name)
        return name

    def _run_services(self):
        for service in self._services_list:
            if isinstance(service, str):
                # only service path supplied
                service_name = service_path2service_name(service)
                process = TestProcess(service)
                pass
            else:
                assert isinstance(service, tuple)
                assert isinstance(service[0], str)
                assert isinstance(service[1], ServiceConfig)
                service_config_path = self._get_tempfile()
                service[1].set_service_name(
                    service_path2service_name(service[0]))
                service[1].write(service_config_path)
                process = TestProcess(service[0], service_config_path)

            process.run()
            self._service_processes.append(process)

    def _run_registry(self):
        registry_path = None
        registry_config_path = None

        if self._registry is None:
            return

        if type(self._registry) == type(True):
            if self._registry is False:
                return
            # we should run registry, but no path/config supplied
            self._registry_process = TestProcess(REGISTRY_DEFAULT_PATH)
        else:
            registry_config_path = self._get_tempfile()
            if isinstance(self._registry, tuple):
                registry_path = self._registry[0]
                self._registry[1].write(registry_config_path)
            else:
                assert isinstance(self._registry, RegistryConfig)
                self._registry.write(registry_config_path)
                self._registry_process = TestProcess(
                    registry_path, registry_config_path)

        self._registry_process.run()

    def run(self):
        if len(self._service_processes) > 0:
            raise RuntimeError("System is already running")

        self._run_services()
        self._run_registry()

    def terminate(self):
        self._registry_process.terminate()
        for service in self._service_processes:
            service.terminate()
        for tmp in self._tmp_files:
            os.unlink(tmp)

if __name__ == "__main__":
    sys.exit(1)
