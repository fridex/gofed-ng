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
import os
import shutil
from threading import Lock


class Dircache(object):

    def __init__(self, path, max_size=float("inf")):
        self._path = os.path.join(os.getcwd(), path)
        self._max_size = self._get_setize(max_size)
        # file usage - from "less used" to the "most used"
        self._fileusage = []
        self._lock = Lock()

        if not os.path.isdir(path):
            os.mkdir(path)

    def _get_setize(self, size):
        if type(size) is int or type(size) is float:
            return size
        elif size.endswith('B'):
            return float(size[:-len('B')])
        elif size.endswith('K'):
            return float(size[:-len('K')]) * 1024
        elif size.endswith('M'):
            return float(size[:-len('M')]) * 1024 * 1024
        elif size.endswith('G'):
            return float(size[-len('G')]) * 1024 * 1024 * 1024
        else:
            return float(size)

    def set_max_size(self, max_size):
        self._max_size = max_size
        with self._lock:
            self._run_cleanup()

    def get_max_size(self):
        return self._max_size

    def get_path(self):
        return self._path

    def get_location(self, filename):
        '''
        Return location based on current settings, the file can/cannot exist
        @param filename: file name
        @return: location string
        '''
        return os.path.join(self.get_path(), filename)

    def get_file_path(self, filename):
        '''
        Return file path, the file HAS TO exist
        @param filename: file name
        @return: location string
        '''
        if not self.is_available(filename):
            raise ValueError("File '%s' is not available in dircache" % filename)

        return self.get_location(filename)

    def store(self, blob, filename):
        with self._lock:
            dst = self.get_location(filename)

            with open(dst, 'wb') as f:
                f.write(blob)

            self._register(filename)

    def _register(self, filename):
        if filename in self._fileusage:
            raise KeyError("File '%s' already in dir cache" % filename)
        self._mark_used(filename)
        self._run_cleanup()

    def register(self, filename):
        with self._lock:
            self._register(filename)

    def is_available(self, filename):
        with self._lock:
            return self._is_available(filename)

    def _is_available(self, filename):
        return filename in self._fileusage

    def retrieve(self, filename):
        with self._lock:
            dst = self.get_location(filename)

            with open(dst, 'rb') as f:
                ret = f.read()

            self._mark_used(filename)

        return ret

    def delete(self, filename):
        with self._lock:
            dst = self.get_location(filename)

            if os.path.isfile(dst):
                os.remove(dst)
            else:
                shutil.rmtree(dst)

    def _get_current_size(self):
        size = 0
        for entry in self._fileusage:
            path = self.get_location(entry)
            size += os.path.getsize(path)
        return size

    def get_current_size(self):
        with self._lock:
            return self._get_current_size()

    def _run_cleanup(self):
        while self._get_current_size() > self.get_max_size():
            if len(self._fileusage) > 0:
                filename = self._fileusage.pop(0)
                dst = self.get_location(filename)
                os.remove(dst)
            else:
                raise IOError("Not enough space in cache file %s" %
                              (self.get_path(),))

    def mark_used(self, filename):
        with self._lock:
            self._mark_used(filename)

    def _mark_used(self, filename):
        if filename in self._fileusage:
            self._fileusage.remove(filename)

        self._fileusage.append(filename)


if __name__ == "__main__":
    sys.exit(1)
