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
import shutil
import os
from common.service.dircache import Dircache
from common.helpers.output import log
from common.service.computationalService import ComputationalService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.serviceResult import ServiceResult
from common.service.action import action
from common.helpers.utils import runcmd

DEFAULT_SCM_DIR="repos"
DEFAULT_SCM_DIR_SIZE='500M'

REPO_TYPE_GIT = 1
REPO_TYPE_MERCURIAL = 2


class ScmService(ComputationalService):
    ''' Git repo analysis '''

    @classmethod
    def signal_startup(cls, config):
        cls.scm_dir = config.get('scm-dir', DEFAULT_SCM_DIR)
        if os.path.isdir(cls.scm_dir):
            shutil.rmtree(cls.scm_dir)
        os.mkdir(cls.scm_dir)
        cls.scm_dir_size = config.get('scm-dir-size', DEFAULT_SCM_DIR_SIZE)
        cls.dircache = Dircache(cls.scm_dir, cls.scm_dir_size)
        log.debug("Dircache size %sB " % cls.dircache.get_max_size())
        log.debug("Dircache path '%s'" % cls.dircache.get_path())

    @staticmethod
    def _get_clone_dir_name(repo_url):
        parts = repo_url.split('/')
        if len(parts) > 2:
            # e.g. https://github.com/user/project
            return "%s-%s-%s" % (parts[-3], parts[-2], parts[-1])
        elif len(parts) == 2:
            # e.g. https://example.com/project.git
            return "%s-%s" % (parts[-2], parts[-1])
        else:
            raise ValueError("Unknown repo '%s'", repo_url)

    @staticmethod
    def _git_log(repo, max_depth, since_date):
        cmd = ["git", "log", "--pretty=format:%H:%an <%ae>:%at:%s"]
        if max_depth:
            cmd.append("--max-count=%d" % max_depth)
        if since_date:
            cmd.append("--since=%s" % since_date)
        stdout, stderr, rt = runcmd(cmd, repo)
        if rt != 0:
            raise RuntimeError("Failed to run git log --pretty: %s", stderr)

        print(stdout)
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

    @action
    def scm_log(self, repo_url, max_depth=None, since_date=None, branch=None):
        '''
        Get SCM log of a repo
        @param repo_url: Git repo URL
        @param max_depth: log depth
        @param since_date: since date
        @param branch: repo branch
        @return: list of scm commits (abbreviated hash, author, author email, author time, subject)
        '''
        ret = ServiceResult()

        if branch is not None and branch != "master":
            raise NotImplementedError("Handling different branch than master is not implement")

        dirname = self._get_clone_dir_name(repo_url)
        dst_path = self.dircache.get_location(dirname)

        with self.get_lock(dirname):
            if self.dircache.is_available(dirname):
                try:
                    repo = gitapi.Repo(dst_path)
                    repo.git_pull()
                    type = REPO_TYPE_GIT
                except:
                    raise ValueError("Unable to pull repo for '%s'" % repo_url)
                    # TODO: handle mercurial
                    pass

                self.dircache.mark_used(dirname)
            else:
                try:
                    gitapi.git_clone(repo_url, dst_path)
                    type = REPO_TYPE_GIT
                except:
                    # TODO: handle mercurial
                    raise ValueError("Unable to clone repo '%s'" % repo_url)
                    pass

                self.dircache.register(dirname)

            if type == REPO_TYPE_GIT:
                ret.result = self._git_log(dst_path, max_depth, since_date)
            elif type == REPO_TYPE_MERCURIAL:
                # TODO: handle mercurial
                pass
            else:
                raise ValueError("Internal Error: Unhandled repo type")

        return ret

if __name__ == "__main__":
    ServiceEnvelope.serve(ScmService)
