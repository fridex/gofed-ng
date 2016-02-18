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


class ActionWrapper(object):

    def __init__(self, action, stats_logger, prehook, posthook):
        self._action = action
        self._stats_logger = stats_logger
        self._prehook = prehook
        self._posthook = posthook

    def __call__(self, *args, **kwargs):
        exception = None
        self._prehook()
        self._stats_logger.log_process_time()
        result = self._action(*args, **dict(kwargs))
        # TODO:
        # try:
        #	result = self._action(*args, **dict(kwargs))
        # except Exception as e:
        #	exception = e
        self._stats_logger.log_processed_time()
        self._posthook(exception is not None)

        # if exception is not None:
        #	raise exception
        self._stats_logger.log_result(result)

        if self._action.__name__ == 'download':
            return result
        else:
            return self._stats_logger.dump()

if __name__ == "__main__":
    sys.exit(1)
