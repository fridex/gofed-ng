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
from common.service.serviceResult import ServiceResult


class ActionWrapper(object):

    def __init__(self, action, stats_logger, prehook, posthook):
        self._action = action
        self._stats_logger = stats_logger
        self._prehook = prehook
        self._posthook = posthook

    def __call__(self, *args, **kwargs):
        self._prehook()
        self._stats_logger.log_process_time()
        try:
            ret = self._action(*args, **dict(kwargs))
        except:
            exc_info = sys.exc_info()
            self._posthook(was_error=True)
            raise exc_info[0], exc_info[1], exc_info[2]
        self._stats_logger.log_processed_time()
        self._posthook(was_error=False)

        if self._action.__name__ == 'download':
            return ret
        else:
            if not isinstance(ret, ServiceResult):
                raise ValueError("Service should always return type '%s', got '%s' instead"
                                 %(ServiceResult.__name__, type(ret)))
            self._stats_logger.log_result(ret.result)
            self._stats_logger.log_meta(ret.meta)
            return self._stats_logger.dump()

if __name__ == "__main__":
    sys.exit(1)
