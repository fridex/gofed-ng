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
from rpyc.utils.registry import REGISTRY_PORT, DEFAULT_PRUNING_TIMEOUT
from rpyc.utils.registry import UDPRegistryClient, TCPRegistryClient
from rpyc.lib import setup_logger

REGISTRY_DEFAULT_HOST="localhost"
REGISTRY_DEFAULT_PORT=REGISTRY_PORT


class RegistryClient(object):

    @staticmethod
    def query(service_name, host=REGISTRY_DEFAULT_HOST, port=REGISTRY_DEFAULT_PORT,
              timeout=DEFAULT_PRUNING_TIMEOUT, logger=None, mode="UDP"):
        if logger:
            setup_logger(False, logger)

        if mode not in ["UDP", "TCP"]:
            raise ValueError("Unknown registry mode '%s', expected %s"
                             % (mode, str(["UDP", "TCP"])))

        if mode == "UDP":
            client = UDPRegistryClient
        else:
            client = TCPRegistryClient

        registrar = client(host, port, timeout)

        return registrar.discover(service_name)

if __name__ == "__main__":
    sys.exit(1)
