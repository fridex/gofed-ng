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
from tqdm import tqdm
from common.helpers.output import log
from scenario import Scenario


class GolangDepsUpdate(Scenario):
    ''' update dependencies of Golang projects packaged in Fedora '''

    def main(self):
        with self.get_system() as system:

            golang_pkgs = system.async_call.goland_package_listing()
            stored_projects = system.async_call.deps_project_listing()

            for pkg in golang_pkgs.result:

                if not pkg['name'].startswith('golang-github-'):
                    log.warning("Skipping %s" % pkg['name'])
                    # TODO: remove once support for mercurial and full package->upstream translation will be available
                    continue

                print("Inspecting '%s'" % pkg['name'])
                upstream_url = system.async_call.golang_package2upstream(pkg['name'])

                if pkg['name'] in stored_projects.result:
                    stored_commits = system.async_call.deps_project_commit_listing(pkg['name'])
                else:
                    stored_commits = None

                scm_log = system.async_call.scm_log(upstream_url.result)

                for commit in tqdm(scm_log.result):
                    log.debug("Commit %s project %s" % (commit['hash'], pkg['name']))
                    if not stored_commits or commit not in stored_commits.result:
                        file_id = system.async_call.scm_store(upstream_url.result, commit['hash'])
                        deps = system.async_call.deps_analysis(file_id.result)
                        system.async_call.deps_store_project(pkg['name'], commit['hash'], commit['time'],
                                                             deps.result, deps.meta)


if __name__ == '__main__':
    sys.exit(1)
