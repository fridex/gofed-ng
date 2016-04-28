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
import json
import time
from common.helpers.version import VERSION
from common.helpers.utils import get_hostname, get_time_str

# TODO: this could be extended with action logging to a file


class ServiceResultGenerator(object):

    def __init__(self):
        self._stats = {'connected': None,
                       'started': None,
                       'finished': None,
                       'result': None,
                       'meta': {},
                       }

    def log_connect_time(self):
        self._stats['connected'] = get_time_str()

    def log_process_time(self):
        self._stats['started'] = get_time_str()

    def log_processed_time(self):
        self._stats['finished'] = get_time_str()

    def log_meta(self, meta):
        if not isinstance(meta, dict):
            raise ValueError("Unknown meta type %s" % (type(meta),))
        for key, val in meta.iteritems():
            self._stats['meta'][key] = val
        if 'error' not in self._stats['meta']:
            # If there was not error, propagate no error flag
            self._stats['meta']['error'] = False

    def log_result(self, result):
        if not isinstance(result, dict) and not isinstance(result, str)\
                and not isinstance(result, list) and not isinstance(result, bool) \
                and not isinstance(result, unicode):
            raise ValueError("Unknown result type %s" % (type(result),))
        self._stats['result'] = result

    def log_service_name(self, name):
        self._stats['meta']['service'] = name
        self._stats['meta']['service-version'] = VERSION
        self._stats['meta']['hostname'] = get_hostname()
        self._stats['meta']['created'] = time.time()

    def log_service_aliases(self, names):
        self._stats['aliases'] = names

    def dump(self):
        return json.dumps(self._stats)

if __name__ == "__main__":
    sys.exit(1)
