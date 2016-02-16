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

import os, time, urllib2
from dateutil.parser import parse as datetime_parse
from common.helpers.file import blob_hash
from common.helpers.output import log
from common.helpers.utils import parse_timedelta
from common.service.storageService import StorageService
from common.service.serviceEnvelope import ServiceEnvelope
from common.service.action import action
from common.system.fileId import FileId

DEFAULT_UPLOAD_DIR = 'uploads'
DEFAULT_FILE_LIFETIME = '2h'

class FileStorageService(StorageService):
	''' Service for storing various files within the system '''

	@classmethod
	def signal_startup(cls, config):
		cls.upload_dir = config.get('upload-dir', DEFAULT_UPLOAD_DIR)
		cls.file_lifetime = config.get('file-lifetime', DEFAULT_FILE_LIFETIME)

		if not os.path.isdir(cls.upload_dir):
			os.mkdir(cls.upload_dir)

		cls.file_lifetime = parse_timedelta(cls.file_lifetime)

	def signal_init(self):
		self.upload_dir = self.__class__.upload_dir
		self.file_lifetime = self.__class__.file_lifetime

	@action
	def upload_url(self, url):
		'''
		Store file by URL - file will be downloaded and exposed to the system
		@return: file id
		'''
		response = urllib2.urlopen(url)
		return self.upload(response.read())

	@action
	def upload(self, blob):
		'''
		Upload file to the system
		@param blob: a file content to be store
		@return: file id
		'''
		log.info("uploading")
		h = blob_hash(blob)
		dst = os.path.join(self.upload_dir, h)

		with self.get_lock():
			with open(dst, 'wb') as f:
				f.write(blob)

		creation_time = datetime_parse(time.ctime(os.path.getctime(dst)))
		valid_until = creation_time + self.file_lifetime

		return FileId.construct(self, dst, str(valid_until), h)

	@action
	def download(self, file_id):
		'''
		Download a file
		@param file_id: a file to be downloaded
		@return: file content
		'''
		# avoid getting files from the local system
		if not file_id.get_service_name() == self.get_service_name():
			raise ValueError("File not from this service")

		filename = os.path.basename(file_id.get_raw()['identifier'])
		file_path = os.path.join(self.upload_dir, filename)

		with self.get_lock():
			log.info("downloading '%s'" % str(file_path))
			with open(file_path, 'rb') as f:
				content = f.read()

		return content

if __name__ == "__main__":
	ServiceEnvelope.serve(FileStorageService)

