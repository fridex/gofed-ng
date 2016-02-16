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
import json
from common.helpers.utils import json_pretty_format
from common.system.fileId import FileId
from common.system.actionCallWrap import actionCallWrap

_MAX_STORE_SIZE = 128

class ServiceResultObject(object):
	def __init__(self, service_name, action_name, connection, call, async = False):
		self._service_name = service_name
		self._action_name = action_name
		self._call_result = None
		self._parsed_response = None
		self._call = call
		self._connection = connection
		self._async = async
		self._status = {}
		self._args = None
		self._kwargs = None
		self._async_callback = None
		self._expiry = None
		self._file_id = None

	def __str__(self):
		ret = {
			"service_name": self._service_name,
			"action": str(self._action_name),
			"local": self.is_local(),
			}

		if self._args:
			ret['args'] = self._args

		if self._kwargs:
			ret['kwargs'] = self._kwargs

		if self.is_remote():
			ret['async'] = self.is_async()

		if self.is_async():
			ret['expired'] = self.is_expired()
			ret['error']   = self.error()
			ret['result_ready']  = self.result_ready()
			ret['async callback'] = str(self._async_callback) if self._async_callback is not None else None
			ret['expiry'] = self._expiry

		if self.result_ready() and not self.is_async():
			ret['response'] = json.loads(self._call_result)

		if self.result_ready() and self.is_async():
			ret['response'] = json.loads(self._call_result.value)

		return json_pretty_format(ret)

	def get_raw(self):
		self.result_wait()
		if self._parsed_response is None:
			if self.is_async():
				self._parsed_response = json.loads(self._call_result.value)
			else:
				self._parsed_response = json.loads(self._call_result)

		return self._parsed_response

	def get_raw_result(self):
		return self.get_raw()['result']

	@actionCallWrap
	def __call__(self, *args, **kwargs):
		if len(args) > 0:
			self._args = []
			for arg in args:
				if len(str(arg)) < _MAX_STORE_SIZE:
					self._args.append(str(arg))
				else:
					self._args.append("<BLOB>")
		else:
			try:
				self._args = str(args)
			except:
				self._args = "<BLOB>"

		if kwargs is not None:
			self._kwargs = {}
			for key, val in kwargs.iteritems():
				if len(str(val)) > _MAX_STORE_SIZE:
					self._kwargs[key] = "<BLOB>"
				else:
					self._kwargs[key] = val

		self._call_result = self._call(*args, **kwargs)

		if type(self._call_result).__name__ in dir(__builtins__):
			self._local_call = True

		return self

	def is_local(self):
		return self._connection.is_local()

	def is_remote(self):
		return not self.is_local()

	def is_async(self):
		return self.is_remote() and self._async

	def is_expired(self):
		return self.is_async() and self._call_result is not None and self._call_result.expired

	def error(self):
		return self.is_async() and self._call_result is not None and self._call_result.error

	def result_ready(self):
		if self.is_async():
			return self._call_result is not None and self._call_result.ready
		else:
			return self._call_result is not None

	def result_wait(self):
		if not self.is_async():
			return True

		self._call_result.wait()

	def set_expiry(self, val):
		if self.is_async():
			self._expiry = val
			self._call_result.set_expiry(val)

	def set_async_callback(self, callback):
		if self.is_async():
			self._async_callback = callback
			self._call_result.add_callback(callback)

	def get_result(self):
		self.result_wait()

		if self._file_id is None:
			if FileId.is_file_id(self.get_raw_result()):
				self._file_id = FileId(self.get_raw_result())
			else:
				self._file_id = False

		if self._file_id is not False:
			return self._file_id
		else:
			return self.get_raw_result()

if __name__ == "__main__":
	sys.exit(1)

