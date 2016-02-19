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


class GoTranslator(object):

    def __init__(self, mappings_json_path):
        self.__mappings_json_path = mappings_json_path
        self._mappings = self.get_mappings(mappings_json_path)

    @staticmethod
    def get_mappings(mappings_json_path):
        with open(mappings_json_path, 'r') as f:
            ret = json.loads(f.read())
        return ret

    def is_mapped_provider(self, upstream):
        return upstream in self._mappings.keys()

    def get_mapped_provider(self, upstream):
        return self._mappings[upstream]

    def is_mapped_pkgname(self, pkgname):
        return pkgname in self._mappings.values()

    def get_mapped_pkgname(self, pkgname):
        for key, val in self._mappings:
            if val == pkgname:
                return key
        raise KeyError("Package name not found in mappings")

    def _get_pkgname_by_provider(self, upstream):
        providers = [
            ('github.com/', self._get_github_pkgname),
            ('code.google.com/p/', self._get_googlecode_pkgname),
            ('golang.org/x/', self._get_golang_pkgname),
            ('gopkg.in/', self._get_gopkg_pkgname),
            ('bitbucket.org/', self._get_bitbucket_pkgname),
            ('google.golang.org/', self._get_googlegolang_pkgname)
        ]

        for provider in providers:
            if upstream.startswith(provider[0]):
                p = upstream[len(provider[0]):]
                return provider[1](p)

        return self._get_other_pkgname(upstream)

    def _get_provider_by_pkgname(self, pkg):
        package_translators = [
            ('github-', self._get_github_provider),
            ('bitbucket-', self._get_bitbucket_provider),
            ('googlecode-', self._get_googlecode_provider),
            ('google-golangorg-', self._get_googlegolang_provider),
            ('golangorg-', self._get_golang_provider),
            ('gopkg-', self._get_gopkg_provider)
        ]

        for package_translator in package_translators:
            if pkg.startswith(package_translator[0]):
                p = pkg[len(package_translator[0]):]
                return package_translator[1](p)

        return self._get_other_provider(pkg)


    def _get_github_pkgname(self, p):
        v = p.split('/')
        if len(v) != 2:
            raise ValueError("github package url not in canonical name, expected '/user/repo' value, got %s" % (p,))

        return 'golang-github-%s-%s' % (v[0], v[1])

    def _get_github_provider(self, p):
        v = p.split('-')
        if len(v) < 2:
            raise ValueError("golang github package expects 'golang-github-<user>-<repo>', got 'golang-github-%s'" % p)

        if len(v) > 2:
            # handle '-' in repo name
            v[1] = "-".join(v[1:])

        return "https://github.com/%s/%s" % (v[0], v[1])

    def _get_googlecode_pkgname(self, p):
        raise NotImplementedError()

    def _get_googlecode_provider(self, p):
        raise NotImplementedError()

    def _get_golang_pkgname(self, p):
        raise NotImplementedError()

    def _get_golang_provider(self, p):
        raise NotImplementedError()

    def _get_gopkg_pkgname(self, p):
        raise NotImplementedError()

    def _get_gopkg_provider(self, p):
        raise NotImplementedError()

    def _get_bitbucket_pkgname(self, p):
        raise NotImplementedError()

    def _get_bitbucket_provider(self, p):
        raise NotImplementedError()

    def _get_googlegolang_pkgname(self, p):
        raise NotImplementedError()

    def _get_googlegolang_provider(self, p):
        raise NotImplementedError()

    def _get_other_pkgname(self, p):
        raise NotImplementedError()

    def _get_other_provider(self, p):
        raise NotImplementedError()

    def pkgname2upstream(self, package_name):
        if self.is_mapped_pkgname(package_name):
            return self.get_mapped_pkgname(package_name)

        if not package_name.startswith("golang-"):
            raise ValueError("Not golang package")

        pkg = package_name[len("golang-"):]

        return self._get_provider_by_pkgname(pkg)


    def upstream2pkgname(self, upstram_url):
        if upstram_url.startswith("http://"):
            upstream = upstram_url[len("http://"):]
        elif upstram_url.startswith("https://"):
            upstream = upstram_url[len("https://"):]
        else:
            upstream = upstram_url

        if self.is_mapped_provider(upstream):
            return self.get_mapped_provider(upstream)

        return self._get_pkgname_by_provider(upstream)

if __name__ == "__main__":
    sys.exit(1)
