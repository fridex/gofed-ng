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
import re
import urllib2
from common.helpers.output import log
from common.service.dircache import Dircache
from common.helpers.file import blob_hash
from common.service.serviceResult import ServiceResult
from common.service.storageService import StorageService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action
from common.system.fileId import FileId

DEFAULT_TARBALL_DIR = 'tarballs'
DEFAULT_TARBALL_DIR_SIZE = '500M'


class TarballStorageService(StorageService):
    ''' Accessing upstream tarballs '''

    @classmethod
    def signal_startup(cls, config):
        cls.tarball_dir = config.get('tarball-dir', DEFAULT_TARBALL_DIR)
        cls.tarball_dir_size = config.get('tarball-dir-size', DEFAULT_TARBALL_DIR_SIZE)
        cls.dircache = Dircache(cls.tarball_dir, cls.tarball_dir_size)
        log.debug("Dircache size %sB " % cls.dircache.get_max_size())
        log.debug("Dircache path '%s'" % cls.dircache.get_path())

    @staticmethod
    def _get_github_file_name(user, project, commit):
        return "github-%s-%s-%s.tar.gz" % (user, project, commit[:8])

    @staticmethod
    def _get_bitbucket_file_name(user, project, commit):
        return "bitbucket-%s-%s-%s.tar.gz" % (user, project, commit[:8])

    @staticmethod
    def _get_github_tarball_url(user, project, commit):
        return 'https://github.com/%s/%s/archive/%s.tar.gz' % (user, project, commit[:8])

    @staticmethod
    def _get_bitbucket_tarball_url(user, project, commit):
        return "https://bitbucket.org/%s/%s/get/%s.tar.gz" % (user, project, commit[:8])

    def _download_tarball(self, tarball_url, filename):
        log.debug("Downloading from %s" % (tarball_url,))
        response = urllib2.urlopen(tarball_url)
        blob = response.read()
        h = blob_hash(blob)

        self.dircache.store(blob, filename)

        return FileId.construct(self, self.dircache.get_file_path(filename), hash_ = h)

    @action
    def tarball_get(self, upstream_url, commit):
        '''
        Retrieve a tarball from upstream, try to detect upstream provider
        @param upstream_url: an upstream url
        @param commit: commit of upstream file
        @return: tarball file id
        '''
        res = ServiceResult()

        if upstream_url.startswith('https://github.com'):
            m = re.search('https://github.com/([a-z]+)/([a-z-_]+)/?', upstream_url)
            if m is None:
                raise ValueError("Expected URL in form 'https://github.com/<USER>/<REPO>/, got %s", (upstream_url,))
            tarball_url = self._get_github_tarball_url(m.group(1), m.group(2), commit)
            filename = self._get_github_file_name(m.group(1), m.group(2), commit)
        elif upstream_url.startswith('https://bitbucket.org'):
            m = re.search('https://bitbucket.org/([a-z]+)/([a-z-_]+)/?', upstream_url)
            if m is None:
                raise ValueError("Expected URL in form 'https://bitbucket.org/<USER>/<REPO>/, got %s", (upstream_url,))
            tarball_url = self._get_bitbucket_tarball_url(m.group(1), m.group(2), commit)
            filename = self._get_bitbucket_file_name(m.group(1), m.group(2), commit)
        else:
            raise NotImplementedError("Unknown upstream provider %s" % (upstream_url,))

        with self.get_lock(filename):
            if self.dircache.is_available(filename):
                res.result = FileId.construct(self, self.dircache.get_file_path(filename))
            else:
                res.result = self._download_tarball(tarball_url, filename)

        return res

    @action
    def download(self, file_id):
        '''
        Retrieve file stored in the service
        @param file_id: id of the file that will be downloaded
        @return: file
        '''
        filename = os.path.basename(file_id.get_identifier())

        with self.get_lock(filename):
            content = self.dircache.retrieve(filename)

        return content


if __name__ == "__main__":
    ServiceEnvelope.serve(TarballStorageService)
