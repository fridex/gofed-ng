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

import hglib
import shutil
import os
import sys
import time
from dateutil.parser import parse as date_parser
from common.helpers.gitcmd import GitCmd
from common.service.dircache import Dircache
from common.helpers.output import log
from common.service.computationalService import ComputationalService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.serviceResult import ServiceResult
from common.service.action import action

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
    def _hg_log(repo_path, max_depth, since_date):
        repo = hglib.open(repo_path)
        commits = repo.log()

        since_date = date_parser(since_date)
        since_date = time.mktime(since_date.timetuple())

        ret = []
        for i, commit in enumerate(commits):
            (rev, node, tags, branch, author, desc, date) = commit
            # lets convert time to Unix timestamp
            date = int(time.mktime(date.timetuple()))

            if i > max_depth:
                break

            if date < since_date:
                break

            ret.append({
                'hash': node,
                'author': author,
                'time': date,
                'commit': desc
            })

        return ret

    @staticmethod
    def _scm_clone(repo_url, dst_path):
        try:
            GitCmd.git_clone_repo(repo_url, dst_path)
            return REPO_TYPE_GIT
        except:
            git_exc_info = sys.exc_info()
            try:
                hglib.clone(repo_url, dst_path)
                return REPO_TYPE_MERCURIAL
            except:
                raise ValueError("Failed to clone repo '%s' to '%s':\nGIT:\n%s\nMercurial:\n%s\n",
                                 repo_url, dst_path, str(git_exc_info), str(sys.exc_info()))

    @staticmethod
    def _scm_pull(repo_dir, branch="master"):
        try:
            repo = GitCmd(repo_dir)
            repo.git_checkout(branch)
            repo.git_pull()
            return REPO_TYPE_GIT
        except:
            git_exc_info = sys.exc_info()
            try:
                repo = hglib.open(repo_dir)
                repo.pull(update=True, branch="default" if branch != "master" else branch)
                return REPO_TYPE_MERCURIAL
            except:
                raise ValueError("Failed to pull repo:\nGIT:\n%s\nMercurial:\n%s\n",
                                 str(git_exc_info), str(sys.exc_info()))

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
                repo_type = self._scm_pull(dst_path)
                self.dircache.mark_used(dirname)
            else:
                repo_type = self._scm_clone(repo_url, dst_path)
                self.dircache.register(dirname)

            if repo_type == REPO_TYPE_GIT:
                ret.result = GitCmd.git_log_repo(dst_path, max_depth, since_date)
            elif repo_type == REPO_TYPE_MERCURIAL:
                ret.result = self._hg_log(dst_path, max_depth, since_date)
            else:
                raise ValueError("Internal Error: Unhandled repo type")

        return ret

if __name__ == "__main__":
    ServiceEnvelope.serve(ScmService)
