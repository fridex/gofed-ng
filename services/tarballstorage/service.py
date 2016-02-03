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

import sys, os
import urllib2
from common.helpers.output import log
from common.service.file import file_id, blob_hash
from common.helpers.utils import json_pretty_format, package2repo
from common.service.storageService import StorageService
from common.service.serviceEnvelope import ServiceEnvelope

DEFAULT_TARBALL_DIR = 'tarballs'

class TarballStorageService(StorageService):
	''' Service for storing various files in system '''

	@classmethod
	def signal_startup(cls, config):
		cls.tarball_dir = config.get('tarball-dir', DEFAULT_TARBALL_DIR)

		if not os.path.isdir(cls.tarball_dir):
			os.mkdir(cls.tarball_dir)

	def signal_init(self):
		self.tarball_dir = self.__class__.tarball_dir

	def _get_file_name(self, package_name, commit):
		return '%s-%s.tar.gz' % (package_name, commit[:8])

	def _download_tarball(self, package_name, commit):
		upstream_url = package2repo(package_name)
		upstream_url += "/archive/%s.tar.gz" % commit[:8]

		response = urllib2.urlopen(upstream_url)
		blob = response.read()
		h = blob_hash(blob)

		dst = os.path.join(self.tarball_dir, self._get_file_name(package_name, commit))
		with open(dst, 'wb') as f:
			f.write(blob)

		return dst, h

	def _is_tarball_available(self, package_name, commit):
		for f in os.listdir(self.tarball_dir):
			name = self._get_file_name(package_name, commit)
			if f == name:
				return True

		return False

	def _get_tarball_file_id(self, package_name, commit):
		path = os.path.join(self.tarball_dir, self._get_file_name(package_name, commit))

		return file_id(self, path, -1)

	def exposed_get_tarball_file_id(self, package_name, commit):
		'''
		Get tarball file
		@param package_name: package name in Fedora
		@param commit: a commit in the project
		@return: file id
		'''
		if self._is_tarball_available(package_name, commit):
			return self._get_tarball_file_id(package_name, commit)
		else:
			file_path, h = self._download_tarball(package_name, commit)
			return file_id(self, file_path, -1, h)

	def exposed_download(self, file_id):
		'''
		Retrieve file stored in the service
		@param file_id: id of the file that will be downloaded
		@return: file
		'''
		log.info("downloading '%s'" % str(file_id))
		filename = os.path.basename(file_id['identifier'])
		file_path = os.path.join(self.tarball_dir, filename)

		with open(file_path, 'rb') as f:
			content = f.read()

		return content

if __name__ == "__main__":
	ServiceEnvelope.serve(TarballStorageService)

