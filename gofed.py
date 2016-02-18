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
from common.helpers.utils import config2dict
from common.helpers.version import VERSION
from subcommand.gofedSystem import GofedSystem
from ConfigParser import ConfigParser

DEFAULT_GOFED_CONFIG_PATH = "gofed.conf"


class Gofed(cli.Application):
    VERSION = VERSION
    DESCRIPTION = "gofed - golang packaging and analysis tool"

    config_path = cli.SwitchAttr("--config", str,
                                 help="gofed config path",
                                 default=DEFAULT_GOFED_CONFIG_PATH)

    def get_config(self):
        return self.config

    def main(self):
        if self.nested_command is None:
            self.help()
            return 1

        conf = ConfigParser()
        conf.read(self.config_path)
        self.config = config2dict(conf)

Gofed.subcommand("system", GofedSystem)

if __name__ == "__main__":
    Gofed.run()
