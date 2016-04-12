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
from common.service.serviceResult import ServiceResult
from common.helpers.output import log
from common.service.dircache import Dircache
from common.service.storageService import StorageService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action
from common.helpers.utils import remote_exists
from common.system.fileId import FileId
from common.helpers.file import blob_hash

DEFAULT_RPM_DIR = 'rpms'
DEFAULT_RPM_DIR_SIZE = '500M'


class RpmStorageService(StorageService):
    ''' RPMs provider '''

    @classmethod
    def signal_startup(cls, config):
        cls.rpm_dir = config.get('rpm-dir', DEFAULT_RPM_DIR)
        cls.rpm_dir_size = config.get('rpm-dir-size', DEFAULT_RPM_DIR_SIZE)
        cls.dircache = Dircache(cls.rpm_dir, cls.rpm_dir_size)
        log.debug("Dircache size %sB " % cls.dircache.get_max_size())
        log.debug("Dircache path '%s'" % cls.dircache.get_path())

    @staticmethod
    def _rpm_filename(name, version, release, distro, arch):
        return "%s-%s-%s.%s.%s.rpm" % (name, version, release, distro, arch)

    def _rpm_url(self, name, version, release, distro, arch):
        # example: https://kojipkgs.fedoraproject.org/packages/etcd/2.3.1/3.fc25/i686/etcd-2.3.1-3.fc25.i686.rpm
        rpm_name =self._rpm_filename(name, version, release, distro, arch)
        return "https://kojipkgs.fedoraproject.org/packages/%s/%s/%s.%s/%s/%s" \
               % (name, version, release, distro, arch, rpm_name)

    @staticmethod
    def _rpm_src_filename(name, version, release, distro):
        return "%s-%s-%s.%s.src.rpm" % (name, version, release, distro)

    def _rpm_src_url(self, name, version, release, distro):
        # example: https://kojipkgs.fedoraproject.org/packages/etcd/2.3.1/3.fc25/src/etcd-2.3.1-3.fc25.src.rpm
        src_rpm_name = self._rpm_src_filename(name, version, release, distro)
        return "https://kojipkgs.fedoraproject.org/packages/%s/%s/%s.%s/src/%s" \
               % (name, version, release, distro, src_rpm_name)

    @staticmethod
    def _rpm_parse_name(name):
        print name
        m = re.search("([a-z-_]+)-([a-z0-9_\.]+)-([a-z0-9_]+)\.([a-z0-9\.]+)\.(src|[a-z0-9_]+).rpm", name)

        if m is None:
            raise ValueError("Unable to parse package name '%s'" % name)

        ret = {
            'name': m.group(1),
            'version': m.group(2),
            'release': m.group(3),
            'distro': m.group(4),
            'arch': None if m.group(5) == 'src' else m.group(5)
        }

        return ret

    def _common_get(self, url, filename):
        ret = ServiceResult()

        with self.get_lock(filename):
            if self.dircache.is_available(filename):
                ret.result = FileId.construct(self, self.dircache.get_file_path(filename))
            elif remote_exists(url):
                log.debug("Downloading from %s" % (url,))
                response = urllib2.urlopen(url)
                blob = response.read()
                h = blob_hash(blob)

                self.dircache.store(blob, filename)

                ret.result = FileId.construct(self, self.dircache.get_file_path(filename), hash_ = h)
            else:
                raise KeyError("Desired file '%s' does not exist ( %s )" % (filename, url))

        ret.meta['origin'] = url
        return ret

    @action
    def rpm_get_by_name(self, package):
        '''
        Get an RPM file id or source RPM file id by its fully qualified name (e.g. flannel-0.5.5-5.fc24.x86_64.rpm)
        @param package:
        @return:
        '''
        info = self._rpm_parse_name(package)
        if info['arch']:
            return self.rpm_get(info['name'], info['version'], info['release'], info['distro'], info['arch'])
        else:
            return self.rpm_src_get(info['name'], info['version'], info['release'], info['distro'])

    @action
    def rpm_get(self, package_name, version, release, distro, arch):
        '''
        Get an RPM file id
        @param package_name:
        @param version:
        @param release:
        @param distro:
        @param arch:
        @return:
        '''
        url = self._rpm_url(package_name, version, release, distro, arch)
        filename = self._rpm_filename(package_name, version, release, distro, arch)
        return self._common_get(url, filename)

    @action
    def rpm_src_get(self, package_name, version, release, distro):
        '''
        Get a source RPM file id
        @param package_name:
        @param version:
        @param release:
        @param distro:
        @return:
        '''
        url = self._rpm_src_url(package_name, version, release, distro)
        filename = self._rpm_src_filename(package_name, version, release, distro)
        return self._common_get(url, filename)

    @action
    def download(self, file_id):
        '''
        Retrieve file stored in the service
        @param file_id: id of the file that will be downloaded
        @return: file content
        '''
        filename = os.path.basename(file_id.get_identifier())

        with self.get_lock(filename):
            content = self.dircache.retrieve(filename)

        return content

if __name__ == "__main__":
    ServiceEnvelope.serve(RpmStorageService)

