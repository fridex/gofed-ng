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

import os
import shutil
import tarfile
from common.helpers.gitcmd import GitCmd
from common.helpers.utils import pushd
from common.helpers.output import log
from common.service.dircache import Dircache
from common.service.storageService import StorageService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action
from common.service.serviceResult import ServiceResult
from common.system.fileId import FileId

DEFAULT_REPOS_DIR = 'repos'
DEFAULT_REPOS_DIR_SIZE = '500M'


class ScmStorageService(StorageService):
    ''' Service for storing SCM repos '''

    @classmethod
    def signal_startup(cls, config):
        cls.scm_dir = config.get('repos-dir', DEFAULT_REPOS_DIR)
        cls.scm_dir_size = config.get('repos-dir-size', DEFAULT_REPOS_DIR_SIZE)

        if os.path.isdir(cls.scm_dir):
            shutil.rmtree(cls.scm_dir)
        os.mkdir(cls.scm_dir)

        cls.file_lifetime = config.get('repos-dir-size', DEFAULT_REPOS_DIR_SIZE)
        cls.dircache = Dircache(cls.scm_dir, cls.scm_dir_size)
        log.debug("Dircache size %sB " % cls.dircache.get_max_size())
        log.debug("Dircache path '%s'" % cls.dircache.get_path())

    @staticmethod
    def _get_dirname(repo_url, commit, branch):
        parts = repo_url.split('/')
        if len(parts) > 2:
            # e.g. https://github.com/user/project
            dirname = "%s-%s-%s" % (parts[-3], parts[-2], parts[-1])
        elif len(parts) == 2:
            # e.g. https://example.com/project.git
            dirname = "%s-%s" % (parts[-2], parts[-1])
        else:
            raise ValueError("Unknown repo '%s'", repo_url)

        return "%s-%s-%s" % (dirname, commit, branch)

    @staticmethod
    def _get_filename(dirname):
        return "%s.tar.gz" % dirname

    def _pack_repo(self, repo_dir, filename):
        # tarfile is not thread sage, so we have to lock whole service here
        with self.get_lock():
            with pushd(self.dircache.get_path()): # we want to avoid 'repos/' dir inside pack
                tar = tarfile.open(filename, "w:gz")
                tar.add(repo_dir)
                tar.close()

    @action
    def scm_store(self, repo_url, commit=None, branch=None):
        '''
        Store a SCM repo
        @param repo_url: repo URL
        @param commit: commit hash; if None, the latest is used
        @param branch: branch; if None, "master" is used
        @return:
        '''

        ret = ServiceResult()

        if not branch:
            branch = "master"

        if commit:
            commit = commit[:7]

        dirname = self._get_dirname(repo_url, commit, branch)
        filename = self._get_filename(dirname)
        dst_path = self.dircache.get_location(dirname)

        with self.get_lock(dirname):
            if not self.dircache.is_available(filename):
                repo = GitCmd.git_clone_repo(repo_url, dst_path)
                repo.git_checkout(branch)
                if commit:
                    repo.git_checkout(commit)
                else:
                    commit = repo.git_rev_parse_head(dst_path)[:7]

                # if user did not supplied commit, we have to check it explicitly
                filename_old = filename
                filename = self._get_filename(self._get_dirname(repo_url, commit, branch))
                # we have to move it so it will be available with specified commit and branch
                if filename_old != filename:
                    shutil.move(filename_old, filename)

                if not self.dircache.is_available(filename):
                    # if user did not supplied commit, we have to pack the repo
                    self._pack_repo(dirname, filename)
                shutil.rmtree(dst_path)

                if not self.dircache.is_available(filename):
                    self.dircache.register(filename)

        ret.result = FileId.construct(self, self.dircache.get_file_path(filename))
        ret.meta = {'origin': repo_url}
        return ret

    @action
    def download(self, file_id):
        '''
        Download a file
        @param file_id: a file to be downloaded
        @return: file content
        '''
        filename = os.path.basename(file_id.get_identifier())

        with self.get_lock(filename):
            content = self.dircache.retrieve(filename)

        return content

if __name__ == "__main__":
    ServiceEnvelope.serve(ScmStorageService)
