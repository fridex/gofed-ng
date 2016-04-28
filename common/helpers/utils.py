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
import getpass
import json
import re
import urllib2
from datetime import timedelta
from subprocess import PIPE, Popen
from time import gmtime, strftime
from contextlib import contextmanager


def get_user():
    return getpass.getuser()


def get_hostname():
    return os.uname()[1]


def dict2json(o, pretty=True):
    if pretty is True:
        return json.dumps(o, sort_keys=True, separators=(',', ': '), indent = 2)
    else:
        return json.dumps(o)


def get_time_str(t=None):
    return strftime("%Y-%m-%d %H:%M:%S", t if t else gmtime())


def config2dict(config):
    ret = {}
    for section in config.sections():
        ret[section] = dict(config.items(section))

    return ret


def get_githead():
    stdout, _, _ = runcmd(["git", "rev-parse", "HEAD"])
    return stdout[:-1]


def runcmd(cmd, cwd="."):
    ''' Run command `cmd' in working directory `cwd' '''
    devnull = open(os.devnull, 'r')
    process = Popen(cmd, stderr=PIPE, stdout=PIPE, stdin=devnull, cwd=cwd, close_fds=True)
    stdout, stderr = process.communicate()
    rt = process.returncode

    if rt != 0:
        raise RuntimeError(stderr)

    return stdout, stderr, rt


def runpipe(cmds, cwd="."):
    p1 = Popen(cmds[0], stdin=None, stdout=PIPE, stderr=PIPE, cwd=cwd)
    prev = p1

    for cmd in cmds[1:]:
        p = Popen(cmd, stdin=prev.stdout, stdout=PIPE, stderr=PIPE, cwd=cwd)
        prev = p

    stdout, stderr = p.communicate()
    p.wait()
    rt = p.returncode

    if rt != 0:
        raise RuntimeError(stderr)

    return stdout, stderr, rt


def parse_timedelta(time_str):
    # thanks to
    # http://stackoverflow.com/questions/4628122/how-to-construct-a-timedelta-object-from-a-simple-string
    regex = re.compile(
        r'((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')
    parts = regex.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in parts.iteritems():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)


def remote_exists(url):
    # we will override default "GET" request, so no content is actually downloaded
    class Request(urllib2.Request):
        def get_method(self):
            return "HEAD"

    try:
        while True:
            request = Request(url)
            response = urllib2.urlopen(request)

            if response.code == 200:
                return True
            elif response.code == 301 or response.code == 302:
                # we want to handle redirection
                url = response.info().dict['Location']
    except:
        pass

    return False


def format_str(text, formats):
    for key, val in formats.iteritems():
        # Now dummy way, since it could be escaped
        text = re.sub(key, str(val), text)
    return text


@contextmanager
def pushd(new_dir):
    prev_dir = os.getcwd()
    os.chdir(new_dir)
    yield
    os.chdir(prev_dir)

if __name__ == '__main__':
    sys.exit(1)
