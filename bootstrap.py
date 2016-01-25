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

from jinja2 import Environment, FileSystemLoader
from common.helpers.output import log
from common.helpers.runcmd import runcmd
import shlex
import os, sys
import shutil
import ast
from plumbum import cli

class GofedBootstrap(cli.Application):
	''' Bootstrap script for Gofed ecosystem '''

	system_directory = cli.SwitchAttr("--system-dir", str, default = None,
			help="Specify system root dir", group = "System")
	system_template = cli.SwitchAttr("--system-template", str, default = None,
			help="Specify system.py template", group = "System")
	registry_conf_template = cli.SwitchAttr("--registry-conf-template", str, default = None,
			help="Specify registry.conf template", group = "System")
	gofed_conf_template = cli.SwitchAttr("--gofed-conf", str, default = None,
			help="Specify gofed conf file template", group = "System")
	system_output_dir = cli.SwitchAttr("--system-outdir", str, default = None,
			help="Specify output dir", group = "System")

	services_directory = cli.SwitchAttr("--services-dir", str, default = None,
			help="Specify services root dir", group = "Services")
	services_py_template = cli.SwitchAttr("--services-template", str, default = None,
			help="Specify service.py template", group = "Services")
	services_conf_template = cli.SwitchAttr("--services-conf", str, default = None,
			help="Specify service.conf template", group = "Services")
	services_output_dir = cli.SwitchAttr("--services-outdir", str, default = None,
			help="Specify services output dir", group = "Services")

	system_only = cli.Flag("--system-only",
			help="Bootstrap only main system", group = "Control handling",
			excludes = ["--services-dir", "--services-template", "--services-conf",
								"--services-outdir", "--services-only"])
	services_only = cli.Flag("--services-only",
			help="Bootstrap only services", group = "Control handling",
			excludes = ["--system-dir", "--system-template", "--gofed-conf",
				"--system-outdir", "--system-only", "--registry-conf-template"])
	debug = cli.Flag(["--debug", "-d"],
			help="Run in debug mode", group = "Control handling")

	def _render_template(self, in_template, out_file, render_param):
		j2_env = Environment(loader=FileSystemLoader(os.path.dirname(in_template)))
		out = j2_env.get_template(os.path.basename(in_template)).render(param = render_param)
		with open(out_file, "w") as f:
			f.write(out)

	def _script_dir(self):
		return os.path.dirname(os.path.abspath(__file__))

	def _get_exposed_funcs(self, node, method = False):
		ret = []

		funcs = [f for f in node.body if isinstance(f, ast.FunctionDef)]
		for action in funcs:
			if action.name.startswith('exposed_') and len(action.name) > len('exposed_'):
				log.info("Found action '%s'..." % action.name)

				item = {}
				item['name'] = action.name[len('exposed_'):]
				item['args'] = []

				for arg in action.args.args:
					item['args'].append(arg.id)

				if method is True: # omit self in methods
					item['args'] = item['args'][1:]

				ret.append(item)

		return ret

	def _get_exposed_classes(self, node, base = 'Service'):
		ret = []

		classes = [c for c in node.body if isinstance(c, ast.ClassDef)]
		for cls in classes:

			exposed = False
			for cls_base in cls.bases:
				if base == cls_base.id:
					exposed = True
					break

			if not exposed:
				continue

			ret.append({ 'defs': self._get_exposed_funcs(cls, method = True), 'class': cls.name })

		return ret


	def system(self, directory = None, system_template = None, registry_conf_template = None, gofed_conf_template = None, output_dir = None):
		log.info("Running gofed system bootstrap...")

		script_dir = self._script_dir()

		if not system_template:
			system_template = os.path.join(script_dir, "system.py.template")

		if not registry_conf_template: # Now only copy, but can be extended in the future
			registry_conf_template = os.path.join(script_dir, "registry.conf.template")

		if not gofed_conf_template:
			gofed_conf_template = os.path.join(script_dir, "gofed.conf.template")

		if not directory:
			directory = os.path.join(script_dir, "services")

		if not output_dir:
			output_dir = script_dir

		exposed_services = []
		for service_name in os.listdir(directory):
			service_path = os.path.join(directory, service_name)
			if not os.path.isdir(service_path):
				continue

			log.info("Analysing file 'exposed.py'")
			src = open(os.path.join(service_path, 'exposed.py'), 'r').read()

			p = ast.parse(src)
			log.info("Looking for exposed actions of service '%s'..." % service_name)
			funcs = self._get_exposed_funcs(p)
			for f in funcs: log.info("Found exposed action '%s'..." % f['name'])
			if len(funcs) > 0:
				exposed_services.append({ 'name': service_name, 'defs': funcs, 'type': 'action' })

			log.info("Looking for exposed classes of service '%s'..." % service_name)
			classes = self._get_exposed_classes(p)

			if len(classes) > 0:
				if len(classes) > 1:
					raise ValueError("Cannot export more than one class per service...")

				classes = classes[0]

				for f in classes['defs']: log.info("Found exposed method '%s' in class '%s'..." % (f['name'], classes['class']))
				exposed_services.append({ 'name': service_name, 'defs': classes['defs'], 'type': 'class', 'class': classes['class'] })

			if len(classes) > 0 and len(funcs) > 0:
				raise ValueError("Cannot export actions and classes at the same time...")

		log.info("Generating system.py")
		self._render_template(system_template, os.path.join(output_dir, "system.py"), exposed_services)

		log.info("Generating system.conf")
		shutil.copy(registry_conf_template, os.path.join(output_dir, "registry.conf"))

		log.info("Generating gofed.conf")
		self._render_template(gofed_conf_template, os.path.join(output_dir, "gofed.conf"), exposed_services)

		return True

	def services(self, directory = None, service_py_template = None, service_conf_template = None, output_dir = None):
		log.info("Services bootstrap")

		script_dir = self._script_dir()

		error_occurred = False

		if not directory:
			directory = os.path.join(script_dir, "services")

		if not service_py_template:
			service_py_template = os.path.join(directory, "serviceEnvelope.py.template")

		if not service_conf_template:
			service_conf_template = os.path.join(directory, "service.conf.template")

		if not output_dir:
			output_dir = directory

		for service_name in os.listdir(directory):
			service_path = os.path.join(directory, service_name)
			if not os.path.isdir(service_path):
				continue

			try:
				log.info("Inspecting dir '%s'..." % service_name)

				src = open(os.path.join(service_path, "service.py")).read()
				p = ast.parse(src)

				cls = self._get_exposed_classes(p, base = 'Service')

				if len(cls) == 0:
					log.warn("Nothing to expose in service '%s'..." % service_name)
				if len(cls) > 1:
					raise ValueError("Cannot expose more than one class per service in service '%s'", service_name)
				cls = cls[0]

				log.info("Found service class '%s'..." % cls['class'])
				log.info("Generating service envelope...")

				service_ident = cls['class'][0].lower() + cls['class'][1:]
				service_envelope = os.path.join(service_name, service_ident + ".py")
				service_conf = os.path.join(service_name, service_ident + ".conf")
				service_common = os.path.join(service_name, "common")
				service_keys = os.path.join(service_name, "keys")

				render_param = {}
				render_param['str'] = service_ident
				render_param['name'] = cls['class']

				log.info("Generating service envelope...")
				self._render_template(service_py_template, os.path.join(output_dir, service_envelope), render_param)

				log.info("Generating service config file...")
				self._render_template(service_conf_template, os.path.join(output_dir, service_conf), render_param)

				log.info("Creating symlink to common files...")
				os.symlink(os.path.join(script_dir, "common"), os.path.join(output_dir, service_common))

			except Exception as e:
				error_occurred = True
				log.error("Error: %s" % e)

		if error_occurred:
			log.warn("There were errors when generating service files, application can misbehave!")

		return True

	def main(self):
		try:
			if not self.services_only:
				if not self.system(self.system_directory,
						self.system_template,
						self.registry_conf_template,
						self.gofed_conf_template,
						self.system_output_dir):
					log.errror("Servives bootstrap failed")
					sys.exit(2)

			if not self.system_only:
				if not self.services(self.services_directory,
						self.services_py_template,
						self.services_conf_template,
						self.services_output_dir):
					log.errror("System bootstrap failed")
					sys.exit(3)
		except Exception as e:
			log.error(e)
			if self.debug:
				raise e
			return 3

if __name__ == "__main__":
	GofedBootstrap.run()

