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
import gitapi
import shutil
from common.helpers.output import log
from common.helpers.utils import runcmd
from common.service.serviceResult import ServiceResult
from common.service.storageService import StorageService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action
from common.system.fileId import FileId

DEFAULT_PKG_DIR = 'pkgs'
DEFAULT_PKG_COUNT = 500


class SpecStorageService(StorageService):
    ''' Acessing specfiles of packages '''

    @classmethod
    def _commit2ident(cls, branch):
        # TODO: maybe it would worth it to store actual commit
        return "" if branch is None else branch

    @classmethod
    def _ident2commit(cls, ident):
        return None if ident == "" else ident

    # TODO: this will probably need a review
    def _register_pkg(self, package_name):
        def clean_up():
            while len(self._pkgs) > self.pkg_count:
                to_remove = self._pkgs[0]
                with self.get_lock(to_remove):
                    path = os.path.join(self.pkg_dir, to_remove)
                    shutil.rmtree(path)

        with self.get_lock(id(self._pkgs)):
            self._pkgs.append(package_name)

            if len(self._pkgs) > self.pkg_count:
                clean_up()

    # TODO: this will probably need a review
    def _mark_used(self, package_name):
        with self.get_lock(id(self._pkgs)):
            if package_name in self._pkgs:
                self._pkgs.remove(package_name)

            self._pkgs.append(package_name)

    @classmethod
    def signal_startup(cls, config):
        cls.pkg_dir = config.get('pkg-dir', DEFAULT_PKG_DIR)
        cls.pkg_count = int(config.get('pkg-count', DEFAULT_PKG_COUNT))

        if not os.path.isdir(cls.pkg_dir):
            os.mkdir(cls.pkg_dir)

        cls._pkgs = []

    def _git_tree_prepare(self, package_name, branch, commit=None):
        path = os.path.join(self.pkg_dir, package_name)

        if not os.path.isdir(path):
            runcmd(['fedpkg', 'clone', '-a', package_name], cwd=self.pkg_dir)
            self._register_pkg(package_name)

        path = os.path.join(self.pkg_dir, package_name)

        repo = gitapi.Repo(path)
        repo.git_checkout(branch)
        if commit is not None:
            repo.git_checkout(commit)
        else:
            repo.git_pull()

        self._mark_used(package_name)
        return path

    @action
    def spec_get(self, package_name, branch=None, commit=None):
        '''
        Get specfile of a package packaged in Fedora
        @param package_name: package name
        @param branch: branch (e.g. "f23", ...); if omitted "rawhide" is used
        @param commit: fedpkg git commit; if omitted, the latest commit is used
        @return: specfile file id
        '''
        ret = ServiceResult()

        # prevent from accessing suspicious files
        package_name = os.path.basename(package_name)

        if branch is None or branch == "rawhide":
            branch = "master"

        # we have to ensure that such package/branch/commit exist
        with self.get_lock(package_name):
            path = self._git_tree_prepare(package_name, branch, commit)
            ident = "%s/%s/%s/%s.spec" % (package_name, branch, self._commit2ident(commit), package_name)
            ret.result = FileId.construct(self, ident, float("inf"), path=os.path.join(path, "%s.spec" % package_name))
        return ret

    @action
    def spec_patch_listing(self, package_name, branch=None, commit=None):
        '''
        Get listing of downstream patches for package packaged in Fedora
        @param package_name: package name
        @param branch: branch (e.g. "f23", ...); if omitted, "rawhide" is used
        @param commit: fedpkg git commit; if omitted, the latest commit is used
        @return: list of downstream patches
        '''
        ret = ServiceResult()
        ret.result = []

        # prevent from accessing suspicious files
        package_name = os.path.basename(package_name)

        if branch is None or branch == "rawhide":
            branch = "master"

        with self.get_lock(package_name):
            self._git_tree_prepare(package_name, branch, commit)

            path = os.path.join(self.pkg_dir, package_name)

            for f in os.listdir(path):
                if f.endswith('.patch'):
                    ret.result.append(f)

        return ret

    @action
    def spec_patch_get(self, package_name, patch_name, branch=None, commit=None):
        '''
        Get file id of a downstream patch of a package packaged in Fedora
        @param package_name: package name
        @param patch_name: name of the patch file
        @param branch: branch (e.g. "f23", ...); if omitted, "rawhide" is used
        @param commit: fedpkg git commit; if omitted, the latest commit is used
        @return: file id of the patch
        '''
        ret = ServiceResult()
        ret.result = []

        # prevent from accessing suspicious files
        package_name = os.path.basename(package_name)
        patch_name = os.path.basename(patch_name)

        if branch is None or branch == "rawhide":
            branch = "master"

        with self.get_lock(package_name):
            path = self._git_tree_prepare(package_name, branch, commit)

            patch_path = os.path.join(path, patch_name)
            if not os.path.isfile(patch_path):
                raise ValueError("There is not patch %s for package %s, branch %s and commit %s"
                                 % (patch_name, package_name, branch, commit))

            ident = "%s/%s/%s/%s" % (package_name, branch, self._commit2ident(commit), patch_name),
            ret.result = FileId.construct(self, ident, float("inf"), path=patch_path)

        return ret

    @action
    def download(self, file_id):
        '''
        Retrieve file stored in the service
        @param file_id: id of the file that will be downloaded
        @return: file
        '''
        identifier = file_id.get_identifier()
        identifier = identifier.split('/')

        if len(identifier) != 4:
            raise ValueError("Unknown file to be accessed")

        package_name = os.path.basename(identifier[0])
        branch = os.path.basename(identifier[1])
        commit = self._ident2commit(os.path.basename(identifier[2]))
        f = os.path.basename(identifier[3])

        if not f.endswith('.spec') and not f.endswith('.patch'):
            raise ValueError("Unknown file to be accessed")

        path = os.path.join(self.pkg_dir, package_name)
        file_path = os.path.join(path, f)

        log.debug("downloading '%s'" % (file_path,))

        with self.get_lock(package_name):
            self._git_tree_prepare(package_name, branch, commit)

            with open(file_path, 'rb') as f:
                content = f.read()

        return content

if __name__ == "__main__":
    ServiceEnvelope.serve(SpecStorageService)

