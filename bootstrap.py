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
import sys
import ast
import json
import shutil
import logging
from plumbum import cli
from jinja2 import Environment, FileSystemLoader
from common.helpers.utils import get_user, get_hostname, get_time_str, json_pretty_format, get_githead
from common.helpers.version import VERSION
from shutil import copyfile

SYSTEM_JSON = 'system.json'
SERVICE_DIR = 'services/'

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


class GofedBootstrap(cli.Application):
    DESCRIPTION = "A gofed system bootstrap script"

    # TODO: configuration merge,
    output_file = cli.SwitchAttr(["--output", "-o"], str, default=SYSTEM_JSON,
                                 help="System JSON output file", group="General")

    check_only = cli.Flag(["--check-only", "-c"],
                          help="Check only, do not generate output", group="General")

    ugly_output = cli.Flag(["--ugly-output", "-u"],
                           help="Do not do pretty formatted output",
                           excludes=['-c'], group="General")

    service_dir = cli.SwitchAttr(["--service-dir"], cli.ExistingDirectory,
                                 default=SERVICE_DIR, help="Specify service root directory", group="Services")

    no_configs = cli.Flag(["--no-configs"],
                          help="Do not generate service and client configs", group="Services")

    def _get_exposed_funcs(self, node, path, method=False):
        def is_action(action):
            for dec in action.decorator_list:
                if dec.id == 'action':
                    return True
            return False

        ret = []

        funcs = [f for f in node.body if isinstance(f, ast.FunctionDef)]
        for action in funcs:
            if is_action(action) and action.name != 'download':
                log.info("Found action '%s'..." % action.name)

                item = {}
                item['name'] = action.name
                item['args'] = []
                item['doc'] = ast.get_docstring(action, clean=True)
                if not item['doc']:
                    log.warn("Function '%s' does not provide docstring in '%s'" % (
                        action.name, path))

                for arg in action.args.args:
                    item['args'].append(arg.id)

                if method is True:  # omit self in methods
                    item['args'] = item['args'][1:]

                ret.append(item)

        return ret

    def _get_service_classes(self, node, path):
        ret = []

        classes = [c for c in node.body if isinstance(c, ast.ClassDef)]
        for cls in classes:
            exposed = False
            bases = []

            for cls_base in cls.bases:
                if cls_base.id in ['StorageService', 'ComputationalService']:
                    exposed = True
                bases.append(cls_base.id)

            if not exposed:
                continue

            ret.append({
                'defs': self._get_exposed_funcs(cls, path, method=True),
                'name': cls.name,
                'doc': ast.get_docstring(cls, clean=True),
                'bases': bases,
                'path': path
            })

        return ret

    def _sanity_check(self, service_classes):
        for services in service_classes:
            if len(services['classes']) > 1:
                raise ValueError("Cannot expose more than one service per service dir in '%s'"
                                 % services['classes'][0]['path'])

            if len(services['classes']) == 0:
                raise ValueError(
                    "No service class defined in '%s'" % services['dir'])

            service = services['classes'][0]

            if not service['name'].endswith('Service'):
                raise ValueError("Service class should be named with 'Service' suffix in '%s'"
                                 % service['path'])

                if not service['name'][0].isupper():
                    raise ValueError(
                        "Service class name should start with uppercase character")

            service_dir = service['name'][:-len('Service')].lower()
            if os.path.basename(services['dir']) != service_dir:
                raise ValueError("Service class '%s' should be placed in directory named '%s' instead of '%s'"
                                 % (service['name'], service_dir, os.path.basename(services['dir'])))

            for services2 in service_classes:
                if services2['dir'] == services['dir']:
                    continue  # skip currently analyzed service

                if len(services2['classes']) == 0:
                    continue  # this will be "No service class defined" error in next round

                service2 = services2['classes'][0]

                for s_def in service['defs']:
                    for s_def2 in service2['defs']:
                        if s_def['name'] == s_def2['name'] and s_def['name'] != 'download':
                            raise ValueError("Cannot expose same action twice, action '%s' from '%s' already exposed by class '%s'"
                                             % (s_def['name'], service['name'], service2['name']))

    def _aggregate_services(self, service_classes):
        # now we know that services are valid
        ret = {'computational': [], 'storages': []}

        for service_class in service_classes:
            service = service_class['classes'][0]

            item = {}
            item['actions'] = service['defs']
            item['doc'] = service['doc']
            item['name'] = service['name'].upper()
            item['name'] = item['name'][:-len('Service')]
            item['bases'] = service['bases']

            if 'ComputationalService' in item['bases']:
                ret['computational'].append(item)
            else:
                ret['storages'].append(item)

        return ret

    def _analyse_service(self, directory):
        ret = {}
        service_file = os.path.join(directory, 'service.py')

        with open(service_file, 'r') as f:
            src = f.read()

        service_classes = {}
        service_classes['classes'] = self._get_service_classes(
            ast.parse(src), service_file)
        service_classes['dir'] = directory

        return service_classes

    def _generate_scenarios(self):
        log.info("Generating scenarios")
        content = ""

        for f in os.listdir('scenarios'):
            if f == 'scenario.py' or f == '__init__.py' or f.endswith('.pyc'):
                continue
            if not os.path.isfile(os.path.join('scenarios', f)):
                continue

            scenario_name = f[:-len('.py')]
            scenario_class = scenario_name[0].upper() + scenario_name[1:]

            content += 'from scenarios.%s import %s\n' % (
                scenario_name, scenario_class)
            content += 'GofedSystem.subcommand("%s", %s)\n' % (
                scenario_name, scenario_class)

        with open(os.path.join('subcommand', 'load_scenarios.py'), 'w') as f:
            f.write(content)

    def _make_header(self, services):
        ret = {}

        ret['gofed_version'] = VERSION
        ret['author'] = get_user()
        ret['hostname'] = get_hostname()
        ret['generated'] = get_time_str()
        ret['services'] = {}
        ret['services']['computational'] = services['computational']
        ret['services']['storages'] = services['storages']
        ret['git_head'] = get_githead()

        return ret

    def _render_template(self, in_template, out_file, render_param):
        j2_env = Environment(loader=FileSystemLoader(
            os.path.dirname(in_template)))
        out = j2_env.get_template(os.path.basename(
            in_template)).render(param=render_param)
        with open(out_file, "w") as f:
            f.write(out)

    def _append_extended_conf(self, service_dir, service_conf):
        service_conf_extended = os.path.join(
            service_dir, 'service.conf.extended')

        if not os.path.isfile(service_conf_extended):
            log.info("No extended service configuration in '%s'" %
                     service_conf_extended)

        with open(service_conf_extended, "r") as f:
            extended_conf = f.read()

        with open(service_conf, "a") as f:
            f.write(extended_conf)

    def _render_services_conf(self, services):
        for service in services['storages'] + services['computational']:
            service_dir = os.path.join(
                self.service_dir, service['name'].lower())
            service_conf_template = os.path.join(
                self.service_dir, 'service.conf.template')
            service_conf = os.path.join(service_dir, 'service.conf')

            self._render_template(service_conf_template, service_conf, {
                                  'name': service['name']})
            self._append_extended_conf(service_dir, service_conf)

    def _render_gofed_conf(self, services):
        gofed_conf_template = os.path.join(
            os.path.dirname(__file__), 'gofed.conf.template')
        gofed_conf = os.path.join(os.path.dirname(__file__), 'gofed.conf')

        copyfile(gofed_conf_template, gofed_conf)

        with open(gofed_conf, "a") as f:
            for service in services['storages'] + services['computational']:
                f.write("\n[%s]\n" % service['name'])
                f.write("remote = True\n")

                service_dir = os.path.join(
                    self.service_dir, service['name'].lower())
                service_conf_extended = os.path.join(
                    service_dir, 'service.conf.extended')
                service_dir = os.path.join(
                    self.service_dir, service['name'].lower())
                service_conf_extended = os.path.join(
                    service_dir, 'service.conf.extended')

                if not os.path.isfile(service_conf_extended):
                    continue

                with open(service_conf_extended, "r") as f_e:
                    extended = f_e.read()

                f.write(extended)

                if not os.path.isfile(service_conf_extended):
                    log.info("No extended service configuration in '%s'" %
                             service_conf_extended)

    def _make_symlinks(self, services):
        for service in services['storages'] + services['computational']:
            service_dir = os.path.join(
                self.service_dir, service['name'].lower())
            dst = os.path.join(service_dir, 'common')

            try:
                os.symlink("../../common", dst)
            except OSError as e:
                # skip if exists
                if not str(e).startswith("[Errno 17] File exists"):
                    raise e
                else:
                    log.info(
                        "Symlink to common in '%s' already exists, skipping" % dst)

    def _copy_system_json(self, system_json, services):
        log.info("Copying system.json to services")
        for service in services['storages'] + services['computational']:
            service_dir = os.path.join(
                self.service_dir, service['name'].lower())
            dst = os.path.join(service_dir, 'system.json')

            shutil.copyfile(system_json, dst)

    def main(self):
        service_classes = []

        log.info("Performing analyses for services in '%s'" % self.service_dir)
        for service in os.listdir(self.service_dir):

            path = os.path.join(self.service_dir, service)

            if not os.path.isdir(path):
                continue
            service_classes.append(self._analyse_service(path))

        self._sanity_check(service_classes)

        services = self._aggregate_services(service_classes)

        if not self.no_configs and not self.check_only:
            self._render_services_conf(services)
            self._render_gofed_conf(services)

        if not self.check_only:
            self._make_symlinks(services)

            ret = self._make_header(services)

            if not self.ugly_output:
                ret = json_pretty_format(ret)
            else:
                ret = json.dumps(ret)
            if self.output_file == '-':
                print ret
            else:
                with open(self.output_file, "w") as f:
                    f.write(ret)
                self._copy_system_json(self.output_file, services)

            self._generate_scenarios()

        return 0

if __name__ == "__main__":
    GofedBootstrap.run()
