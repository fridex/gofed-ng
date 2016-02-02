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
import gitapi
import urllib2
import json
import StringIO
from specker.modules.specFileParser import SpecFileParser
from specker.modules.specFileRenderer import SpecFileRenderer
from specker.modules.specModelWriter import SpecModelWriter
from common.helpers.output import log
from common.helpers.utils import json_pretty_format, runcmd
from common.service.storageService import StorageService
from common.service.serviceEnvelope import ServiceEnvelope

DEFAULT_SPEC_TREE_DIR="specs/"
PKGDB_API_URL="https://admin.fedoraproject.org/pkgdb/api/packages/?&pattern=golang-*"

class SpecStorageService(StorageService):
	''' Golang spec files access and information retrieving '''

	@classmethod
	def _fedora_pkgdb_packages_list(cls):
		ret = []
		log.info("Querying Fedora Package DB")
		response = urllib2.urlopen(PKGDB_API_URL)

		if response.code != 200:
			raise RuntimeError("Failed to receive packages from Fedora package database (%s)"
										% str(response.code))

		packages = json.loads(response.read())

		if packages['output'] != 'ok':
			raise RuntimeError("Bad response from Fedora package database:\n%s"
										% json_pretty_format(packages))

		# TODO: handle pagination
		assert packages['page'] == 1 and packages['page_total'] == 1

		for package in packages['packages']:
			ret.append(package)

		log.info("Got %s golang packages" % len(ret))
		return ret

	@classmethod
	def _make_tree_dir(cls, tree_dir, packages):
		for package in packages:
			log.info("Clonning package '%s'" % package['name'])
			if os.path.isdir(os.path.join(tree_dir, package['name'])):
				log.info("Skipping package '%s', destination git already exists" % package['name'])
				continue
			runcmd(['fedpkg', 'clone', '-a', package['name']], cwd = tree_dir)

	@classmethod
	def signal_startup(cls, config):
		service_name = cls.get_service_name()

		if service_name in config:
			tree_dir = config[service_name].get('spec-tree-dir')

		if tree_dir is None:
			tree_dir = DEFAULT_SPEC_TREE_DIR

		if not os.path.isdir(tree_dir):
			log.info("Creating tree dir '%s'" % tree_dir)
			os.mkdir(tree_dir)
		else:
			log.info("Using tree dir '%s'" % tree_dir)

		packages = cls._fedora_pkgdb_packages_list()
		cls._make_tree_dir(tree_dir, packages)

		cls.packages = packages
		cls.tree_dir = tree_dir

	def signal_init(self):
		self.packages = self.__class__.packages
		self.tree_dir = self.__class__.tree_dir

	def _prepare_repo(self, package, branch = None):
		path = os.path.join(self.tree_dir, package)

		repo = gitapi.Repo(path)
		if branch is None or branch == 'rawhide':
			branch = "master"

		try:
			repo.git_checkout(branch)
		except Exception as e:
			raise ValueError("No such branch '%s'" % branch)

	def _get_specmodel(self, package, branch = None):
		self._prepare_repo(package, branch)

		path = os.path.join(self.tree_dir, package)
		specfile = os.path.join(path, package + '.spec')

		parser = SpecFileParser(SpecModelWriter())
		parser.init(specfile)
		renderer = SpecFileRenderer(parser.get_model_writer().get_model())

		return renderer

	def exposed_get_spec_listing(self):
		'''
		Get listing of all Golang projects packaged in Fedora
		@return list of packages in Fedora Package DB with some additional metadata (upstream, description, ...)
		'''
		return self.packages

	def exposed_get_spec_requires(self, package, branch = None):
		'''
		Get all requires for package
		@param package: golang package packaged in Fedora
		@param branch: Fedora branch (e.g. "f23", "rawhide"), if omitted, rawhide is used
		@return list of requires
		'''
		ret = StringIO.StringIO()
		model = self._get_specmodel(package, branch)
		return "TODO"
		model.requires_show(ret)
		return ret.getvalue()

	def exposed_get_spec_buildrequires(self, package, branch = None):
		'''
		Get all buildrequires for package
		@param package: golang package packaged in Fedora
		@param branch: Fedora branch (e.g. "f23", "rawhide"), if omitted, rawhide is used
		@return list of buildrequires
		'''
		ret = StringIO.StringIO()
		model = self._get_specmodel(package, branch)
		return "TODO"
		model.buildrequires_show(ret)
		return ret.getvalue()

	def exposed_get_spec_packages(self, package, branch = None):
		'''
		Get all packages (e.g. devel, ...) of a package
		@param package: golang package packaged in Fedora
		@param branch: Fedora branch (e.g. "f23", "rawhide"), if omitted, rawhide is used
		@return list of packages
		'''
		ret = StringIO.StringIO()
		model = self._get_specmodel(package, branch)
		return "TODO"
		model.package_show(ret)
		return ret.getvalue()

	def exposed_get_spec(self, package, branch = None):
		'''
		Get raw spec file of a package
		@param package: golang package packaged in Fedora
		@param branch: Fedora branch (e.g. "f23", "rawhide"), if omitted, rawhide is used
		@return raw spec file
		'''
		self._prepare_repo(package, branch)

		path = os.path.join(self.tree_dir, package)
		specfile = os.path.join(path, package + '.spec')
		with open(specfile, "r") as f:
			ret = f.read()

		return ret

	def exposed_get_spec_patch_listing(self, package, branch = None):
		'''
		Get list of downstream patches of a package
		@param package: golang package packaged in Fedora
		@param branch: Fedora branch (e.g. "f23", "rawhide"), if omitted, rawhide is used
		@return list of downstream patches
		'''
		ret = []

		self._prepare_repo(package, branch)

		path = os.path.join(self.tree_dir, package)

		for f in os.listdir(path):
			file_path = os.path.join(path, f)
			if not os.path.isfile(file_path):
				continue

			if f.endswith('.patch'):
				ret.append(f)

		return ret

	def exposed_get_spec_patch(self, package, patch_name, branch = None):
		'''
		Get a downstream patch of a package
		@param package: golang package packaged in Fedora
		@param patch_name: patch name
		@param branch: Fedora branch (e.g. "f23", "rawhide"), if omitted, rawhide is used
		@return raw downstream patch
		'''
		self._prepare_repo(package, branch)

		path = os.path.join(self.tree_dir, package)
		patch_path = os.path.join(path, patch_name)

		with open(patch_path, "r") as f:
			ret = f.read()

		return ret

if __name__ == "__main__":
	ServiceEnvelope.serve(SpecStorageService)

