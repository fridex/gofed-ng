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

import sys
import os
import time
import urllib2
from dateutil.parser import parse as datetime_parse
from common.service.file import file_id, blob_hash
from common.helpers.output import log
from common.helpers.utils import json_pretty_format, parse_timedelta
from common.service.storageService import StorageService
from common.service.serviceEnvelope import ServiceEnvelope

DEFAULT_UPLOAD_DIR = 'uploads'
DEFAULT_FILE_LIFETIME = '2h'

class FileStorageService(StorageService):
	''' Service for storing various files in system '''

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

	def exposed_store_file_url(self, url):
		'''
		Store file by URL - file will be downloaded
		@return: id of the file and time for which the file is accessible
		'''
		response = urllib2.urlopen(url)
		return self.exposed_upload(response.read())

	def exposed_upload(self, blob):
		'''
		Store a file
		@param blob: a file content to store
		@return: a file id
		'''
		h = blob_hash(blob)
		dst = os.path.join(self.upload_dir, h)
		with open(dst, 'wb') as f:
			f.write(blob)

		creation_time = datetime_parse(time.ctime(os.path.getctime(dst)))
		valid_until = creation_time + self.file_lifetime

		return file_id(self, dst, str(valid_until), h)

	def exposed_download(self, file_id):
		'''
		Download a file
		@param file_id: a file to be downloaded
		'''
		# avoid getting files from the local system
		# TODO: check if this service
		log.info("downloading '%s'" % str(file_id))
		filename = os.path.basename(file_id['identifier'])
		file_path = os.path.join(self.upload_dir, filename)

		with open(file_path, 'rb') as f:
			content = f.read()

		return content


if __name__ == "__main__":
	ServiceEnvelope.serve(FileStorageService)

