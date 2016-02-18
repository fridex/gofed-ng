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
import signal
import time
from subprocess import Popen, PIPE


class TestProcess(object):

    def __init__(self, path_exec, config_path=None):
        self._path_exec = path_exec
        self._process = None
        self._returncode = None
        self._config_path = config_path
        self._stdout = None
        self._stderr = None
        self._returncode = None
        self._pid = None

    def is_running(self):
        return self._process is not None

    def get_path_exec(self):
        return self._path_exec

    def get_config_path(self):
        return self._config_path

    def run(self):
        if self.is_running():
            raise RuntimeError("Cannot run service already running")

        cmd = ['python', self._path_exec]

        if self._config_path:
            cmd += ['--config', self._config_path]

        self._process = Popen(cmd,
                              stdout=PIPE, stderr=PIPE, shell=False,
                              preexec_fn=os.setsid)  # do not let parent receive signals
        self._pid = self._process.pid

    def get_stdout(self):
        if self._stdout is None:
            if self._process is not None:
                self._stdout = self._process.stdout.read()
        else:
            self._stdout += self._process.stdout.read()

        return self._stdout

    def get_stderr(self):
        if self._stderr is None:
            if self._process is not None:
                self._stderr = self._process.stdout.read()
        else:
            self._stderr += self._process.stdout.read()

        return self._stderr

    def get_returncode(self):
        if self._returncode is None:
            if self._process is not None:
                self._returncode = self._process.returncode

        return self._returncode

    def get_pid(self):
        return self._pid

    def terminate(self):
        if self.is_running():
            os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
            self.get_returncode()
            self.get_stdout()
            self.get_stderr()
            self._process = None

if __name__ == "__main__":
    sys.exit(1)
