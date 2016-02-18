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
import hashlib

_BLOCKSIZE = 65535


def file_hash(path):
    h = hashlib.sha1()

    with open(path, 'rb') as f:
        buf = f.read(_BLOCKSIZE)
        while len(buf) > 0:
            h.update(buf)
            buf = f.read(_BLOCKSIZE)

    return h.hexdigest()


def blob_hash(blob):
    h = hashlib.sha1()
    h.update(blob)
    return h.hexdigest()

if __name__ == "__main__":
    sys.exit(1)
