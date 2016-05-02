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
import re
import os
from common.helpers.utils import runcmd


class GitCmd(object):
    '''
    Thread safe Python git
    '''

    def __init__(self, repo_path, url=None):
        self._repo_path = repo_path
        if url is not None:
            self.git_clone_repo(url, repo_path)

    def git_clone(self, url):
        self.git_clone_repo(url, self._repo_path)
        return self

    def git_checkout(self, what):
        return self.git_checkout_repo(self._repo_path, what)

    def git_rev_parse_head(self):
        return self.git_rev_parse_head_repo(self._repo_path)

    def git_log(self):
        return self.git_log_repo(self._repo_path)

    def git_log_repo(self, max_depth, since_date):
        return self.git_log_repo(max_depth, since_date)

    def git_pull(self):
        return self.git_pull_repo(self._repo_path)

    @staticmethod
    def git_clone_repo(url, dst_path):
        cmd = ["git", "clone", url, dst_path]
        runcmd(cmd)
        return GitCmd(dst_path)

    @staticmethod
    def git_checkout_repo(dst_path, what):
        gitdir = os.path.join(dst_path, ".git")
        cmd = ["git", "--git-dir=%s" % gitdir, "--work-tree=%s" % dst_path, "checkout", what]
        runcmd(cmd)
        return GitCmd(dst_path)

    @staticmethod
    def git_rev_parse_head_repo(dst_path):
        gitdir = os.path.join(dst_path, ".git")
        cmd = ["git", "--git-dir=%s" % gitdir, "--work-tree=%s" % dst_path, "rev-parse", "HEAD"]
        stdout, stderr, rt = runcmd(cmd)
        return stdout

    @staticmethod
    def git_pull_repo(dst_path):
        gitdir = os.path.join(dst_path, ".git")
        cmd = ["git", "--git-dir=%s" % gitdir, "--work-tree=%s" % dst_path, "pull"]
        stdout, stderr, rt = runcmd(cmd)
        return stdout

    @staticmethod
    def git_log_repo(repo_path, max_depth, since_date):
        gitdir = os.path.join(repo_path, ".git")
        cmd = ["git", "--git-dir=%s" % gitdir, "--work-tree=%s" % repo_path, "log", "--pretty=format:%H:%an <%ae>:%at:%s"]
        if max_depth:
            cmd.append("--max-count=%d" % max_depth)
        if since_date:
            cmd.append("--since=%s" % since_date)
        stdout, stderr, rt = runcmd(cmd)
        if rt != 0:
            raise RuntimeError("Failed to run git log --pretty: %s", stderr)

        lines = stdout.split('\n')
        ret = []
        for line in lines:
            if line == "":
                continue # skip no results
            # hash: author name <e-mail>:time:subject
            m = re.match("([A-Fa-f0-9]+):(.*):([0-9]+):(.*)", line)
            ret.append({
                'hash': m.group(1),
                'author': m.group(2),
                'time': m.group(3),
                'commit': m.group(4)
            })

        return ret

if __name__ == "__main__":
    sys.exit(1)
