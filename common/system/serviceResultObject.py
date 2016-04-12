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
from common.helpers.output import log
from common.helpers.utils import dict2json
from common.system.fileId import FileId
from common.system.actionCallWrap import actionCallWrap

_MAX_ARG_STORE_SIZE = 128


class ServiceResultObject(object):

    def __init__(self, service_name, action_name, connection, call, async=False):
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
        ret = self.get_client_stats()

        if self.result_ready() and not self.is_async():
            ret['response'] = json.loads(self._call_result)

        if self.result_ready() and self.is_async():
            ret['response'] = json.loads(self._call_result.value)

        return dict2json(ret)

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

    def _store_args(self, *args, **kwargs):
        if len(args) > 0:
            self._args = []
            for arg in args:
                if len(str(arg)) < _MAX_ARG_STORE_SIZE:
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
                if len(str(val)) > _MAX_ARG_STORE_SIZE:
                    self._kwargs[key] = "<BLOB>"
                else:
                    self._kwargs[key] = val

    @actionCallWrap
    def __call__(self, *args, **kwargs):
        self._store_args(*args, **kwargs)

        # now we have to serialize dicts/arrays
        new_args = []
        for arg in args:
            if isinstance(arg, dict) or isinstance(arg, list):
                try:
                    new_args.append(json.dumps(arg))
                except Exception as e:
                    raise ValueError("Failed to serialize request for call '%s': %s" % (self._action_name, str(e)))
            else:
                new_args.append(arg)

        for key, value in kwargs.iteritems():
            if isinstance(value, dict) or isinstance(value, list):
                try:
                    kwargs[key] = json.dumps(value)
                except Exception as e:
                    raise ValueError("Failed to serialize request for call '%s': %s" % (self._action_name, str(e)))

        log.debug("Calling %s, action %s, params:\nargs:%s\nkwargs%s"
                  % (self._service_name, self._action_name, self._args, self._kwargs))
        self._call_result = self._call(*tuple(new_args), **kwargs)

        # TODO: ?
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

    @property
    def result(self):
        return self.get_result()

    @property
    def meta(self):
        return self.get_raw()['meta']

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
            log.debug("Calling %s, action %s, client stats:%s\nserver stats:%s\nresult%s"
                      % (self._service_name, self._action_name, self.get_client_stats(),
                         self.get_service_stats(), self.get_raw_result()))
            return self.get_raw_result()

    def get_result_with_meta(self):
        ret = self.get_stats()
        ret['result'] = self.result
        return ret

    def get_client_stats(self):
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
            ret['error'] = self.error()
            ret['result_ready'] = self.result_ready()
            ret['async callback'] = str(
                    self._async_callback) if self._async_callback is not None else None
            ret['expiry'] = self._expiry

        return ret

    def get_service_stats(self):
        self.result_wait()
        if not self.is_async():
            ret = json.loads(self._call_result)
        else:
            ret = json.loads(self._call_result.value)

        del ret['result']
        return ret

    def get_stats(self):
        return {'client': self.get_client_stats(), 'service': self.get_service_stats()}

if __name__ == "__main__":
    sys.exit(1)
