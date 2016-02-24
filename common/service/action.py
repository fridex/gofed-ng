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
import functools
import json
from common.system.fileId import FileId


def action(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        new_args = []
        for arg in args:
            if isinstance(arg, str):
                # when a json was supplied, we deserialize it to dict
                try:
                    new_args.append(json.loads(arg))
                except:
                    # regular string from a user
                    new_args.append(arg)
            else:
                new_args.append(arg)

            if FileId.is_file_id(new_args[-1]):
                new_args[-1] = FileId(new_args[-1])

        for key, value in kwargs.iteritems():
            if isinstance(value, str):
                # when a json was supplied, we deserialize it to dict
                try:
                    kwargs[key] = json.loads(value)
                except:
                    pass

            if FileId.is_file_id(kwargs[key]):
                kwargs[key] = FileId(value)

        return func(*tuple(new_args), **kwargs)

    wrapper.action = True
    return wrapper

if __name__ == '__main__':
    sys.exit(1)
