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

import gitapi
import re
from common.service.dircache import Dircache
from common.helpers.output import log
from common.service.computationalService import ComputationalService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.serviceResult import ServiceResult
from common.service.action import action
from common.helpers.utils import runcmd

DEFAULT_GIT_DIR="repos"
DEFAULT_GIT_DIR_SIZE='500M'


class GitService(ComputationalService):
    ''' Git repo analysis '''

    @classmethod
    def signal_startup(cls, config):
        cls.git_dir = config.get('git-dir', DEFAULT_GIT_DIR)
        cls.git_dir_size = config.get('git-dir-size', DEFAULT_GIT_DIR_SIZE)
        cls.dircache = Dircache(cls.git_dir, cls.git_dir_size)
        log.debug("Dircache size %sB " % cls.dircache.get_max_size())
        log.debug("Dircache path '%s'" % cls.dircache.get_path())

    @staticmethod
    def _get_clone_dir_name(git_repo_url):
        parts = git_repo_url.split('/')
        if len(parts) > 2:
            # e.g. https://github.com/user/project
            return "%s-%s-%s" % (parts[-3], parts[-2], parts[-1])
        elif len(parts) == 2:
            # e.g. https://example.com/project.git
            return "%s-%s" % (parts[-2], parts[-1])
        else:
            raise ValueError("Unknown repo '%s'", git_repo_url)

    @staticmethod
    def _git_log_pretty(repo):
        stdout, stderr, rt = runcmd(["git", "log", "--pretty=format:%H:%an <%ae>:%at:%s"], repo)
        if rt != 0:
            raise RuntimeError("Failed to run git log --pretty: %s", stderr)

        lines = stdout.split('\n')
        ret = []
        for line in lines:
            # hash: author name <e-mail>:time:subject
            m = re.match("([A-Fa-f0-9]+):(.*):([0-9]+):(.*)", line)
            ret.append({
                'hash': m.group(1),
                'author': m.group(2),
                'time': m.group(3),
                'commit': m.group(4)
            })

        return ret

    @action
    def git_log(self, git_repo_url, branch=None):
        '''
        Get git log of a git repo
        @param git_repo_url: Git repo URL
        @param branch: repo branch
        @return: list of git (abbreviated hash, author, author email, author time, subject)
        '''
        ret = ServiceResult()

        if branch is not None and branch != "master":
            raise NotImplementedError("Handling different branch than master is not implement")

        dirname = self._get_clone_dir_name(git_repo_url)
        dst_path = self.dircache.get_location(dirname)

        with self.get_lock(dirname):
            if self.dircache.is_available(dirname):
                repo = gitapi.Repo(dst_path)
                repo.git_pull()
                self.dircache.mark_used(dirname)
            else:
                gitapi.git_clone(git_repo_url, dst_path)
                self.dircache.register(dirname)

            ret.result = self._git_log_pretty(dst_path)

        return ret

if __name__ == "__main__":
    ServiceEnvelope.serve(GitService)
