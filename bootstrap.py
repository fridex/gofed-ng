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

import os, sys, ast, json
from plumbum import cli
from common.helpers.output import log
from common.helpers.utils import get_user, get_hostname, get_time_str, json_pretty_format
from common.helpers.version import VERSION

SYSTEM_JSON = 'system.json'
SERVICE_DIR = 'services/'

class GofedBootstrap(cli.Application):
	# TODO: configuration merge,
	service_dir = cli.SwitchAttr(["--service-dir", "-s"], cli.ExistingDirectory,
			default = SERVICE_DIR, help="Specify service root directory",
			excludes = ["--service"])

	output_file = cli.SwitchAttr(["--output", "-o"], str, default = SYSTEM_JSON,
			help="System JSON output file")

	check_only = cli.Flag(["--check-only", "-c"],
			help="Check only, do not generate output")

	ugly_output = cli.Flag(["--ugly-output", "-u"],
			help="Do not do pretty formatted output", excludes=['-c'])

	service = cli.SwitchAttr(["--service"], cli.ExistingDirectory, default = None,
			help="Inspect only one particular service",
			excludes = ["--service-dir"])

	def _get_exposed_funcs(self, node, path, method = False):
		ret = []

		funcs = [f for f in node.body if isinstance(f, ast.FunctionDef)]
		for action in funcs:
			if action.name.startswith('exposed_') and len(action.name) > len('exposed_'):
				log.info("Found action '%s'..." % action.name)

				item = {}
				item['name'] = action.name[len('exposed_'):]
				item['args'] = []
				item['doc'] = ast.get_docstring(action, clean = True)
				if not item['doc']:
					log.warn("Exposed function '%s' does not provide docstring in '%s'" % (action.name, path))

				for arg in action.args.args:
					item['args'].append(arg.id)

				if method is True: # omit self in methods
					item['args'] = item['args'][1:]

				ret.append(item)

		return ret

	def _get_exposed_classes(self, node, path):
		ret = []
		bases = []

		classes = [c for c in node.body if isinstance(c, ast.ClassDef)]
		for cls in classes:
			exposed = False

			for cls_base in cls.bases:
				if cls_base.id == 'Service':
					exposed = True
				else:
					bases.append(cls_base.id)

				if not exposed:
					continue

			ret.append({
				'defs': self._get_exposed_funcs(cls, path, method = True),
				'name': cls.name,
				'doc': ast.get_docstring(cls, clean = True),
				'bases': bases
				})

		return ret

	def _service_sanity_check(self, service, service_file):
		# service.py
		if len(service) > 1:
			raise ValueError("Cannot expose more than one Service class per service in '%s'" % service_file)

		if len(service) == 0:
			raise ValueError("No Service class defined in '%s'" % service_file)

		if not service[0]['name'].endswith('Service'):
			raise ValueError("Service class should be named with Service suffix in '%s'" % service_file)

		# TODO: action with name: "exposed_action" and def with name "action" are
		# not allowed

	def _analyse_service(self, directory):
		ret = { }
		service_file = os.path.join(directory, 'service.py')

		with open(service_file, 'r') as f:
			src = f.read()

		service = self._get_exposed_classes(ast.parse(src), service_file)

		self._service_sanity_check(service, service_file)

		# now we know that service.py is valid after sanity check, now sum up the analysis
		ret['name'] = service[0]['name']
		ret['name'] = ret['name'][:len(ret['name']) - len('Service')].upper()
		ret['doc'] = service[0]['doc']
		ret['actions'] = service[0]['defs']

		return ret

	def _make_services_header(self, services):
		ret = { }

		ret['gofed_version'] = VERSION
		ret['author'] = get_user()
		ret['hostname'] = get_hostname()
		ret['generated'] = get_time_str()
		ret['services'] = services

		return ret

	def main(self):
		services = []
		if self.service:
			services.append(self._analyse_service(str(self.service)))
		else:
			for service in os.listdir(self.service_dir):

				path = os.path.join(self.service_dir, service)

				if not os.path.isdir(path):
					continue
				services.append(self._analyse_service(path))

		if not self.check_only:
			ret = self._make_services_header(services)
			if not self.ugly_output:
				ret = json_pretty_format(ret)
			else:
				ret = json.dumps(ret)
			if self.output_file == '-':
				print ret
			else:
				with open(self.output_file, "w") as f:
					f.write(ret)

		return 0

if __name__ == "__main__":
	GofedBootstrap.run()

