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

from common.helpers.output import log
from common.helpers.utils import json_pretty_format
from common.service.storageService import StorageService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action

DEFAULT_RPM_DIR = 'rpms'


class RpmStorageService(StorageService):
    ''' RPMs provider '''

    @classmethod
    def signal_startup(cls, config):
        log.info("got startup signal")
        log.info("custom config sections: " + json_pretty_format(config))
        cls.rpm_dir = config.get('rpm-dir', DEFAULT_RPM_DIR)

    @classmethod
    def signal_termination(cls):
        log.info("got termination signal")

    def signal_init(self):
        log.info("got init signal")
        self.rpm_dir = self.__class__.rpm_dir

    def signal_connect(self):
        log.info("got connect signal")

    def signal_disconnect(self):
        log.info("got disconnect signal")

    def signal_process(self):
        log.info("got process signal")

    def signal_processed(self):
        log.info("got processed signal")

    @action
    def rpm_get(self, package, arch=None, fedora_release=None):
        '''
        Get an RPM file id
        @param package: package name
        @param arch: Fedora architecture identifier, if omitted "x86_64" is used
        @param fedora_release: Fedora release, if omitted "rawhide" is used
        @return: file id
        '''
        return "TODO"

    @action
    def download(self, file_id):
        '''
        Retrieve file stored in the service
        @param file_id: id of the file that will be downloaded
        @return: file content
        '''
        return "TODO"

if __name__ == "__main__":
    ServiceEnvelope.serve(RpmStorageService)
