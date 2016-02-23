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
import getopt
from pymongo import MongoClient
from flask import Flask, jsonify, send_from_directory, abort
from ConfigParser import ConfigParser

APP_NAME = "APIWEB"
DEFAULT_DATABASE_HOST = "localhost"
DEFAULT_DATABASE_PORT = 27017
DEFAULT_DATABASE_NAME = "gofed"
DEFAULT_DATABASE_COLLECTION_PROJECT = "project-api"
DEFAULT_DATABASE_COLLECTION_PACKAGE = "package-api"
DEFAULT_DEBUG = True

app = Flask(APP_NAME)

# TODO: handle pagination


class AppSingleton(object):
    _instance = None

    class Configuration(object):
        def __init__(self, db_host, db_port, db_name, db_collection_name_project, db_collection_name_package):
            self._host = db_host
            self._port = db_port
            self._db_name = db_name
            self._db_collection_name_project = db_collection_name_project
            self._db_collection_name_package = db_collection_name_package
            self._client = MongoClient(db_host, db_port)
            self._db = self._client[db_name]
            self._api_project = self._db[db_collection_name_project]
            self._api_package = self._db[db_collection_name_package]

        def get_api_collection_project(self):
            return self._api_project

        def get_api_collection_package(self):
            return self._api_package

    @staticmethod
    def init(db_host, db_port, db_name, db_collection_name_project, db_collection_name_package):
        assert AppSingleton._instance is None
        AppSingleton._instance = AppSingleton.Configuration(db_host, db_port, db_name,
                                                            db_collection_name_project, db_collection_name_package)

    def __getattr__(self, attr):
        if attr == 'init':
            return self.init

        if AppSingleton._instance is None:
            raise ValueError("Singleton not instantiated!")
        return getattr(self._instance, attr)

conn = AppSingleton()


@app.route('/api/project/api/<project>/<commit>', methods=['GET'])
def api_project_api(project, commit):
    ret = []
    filtering = {'_id': 0}

    cursor = conn.get_api_collection_project().find({'project': project, 'commit': commit}, filtering)
    for item in cursor:
        ret.append({'commit': item['commit'], 'commit-date': item['commit-date'],
                    'meta': item['meta'], 'api': item['api']})

    if len(ret) == 0:
        abort(404)

    return jsonify({'project': project, 'commit': commit, 'api': ret})


@app.route('/api/project/log/<project>', defaults={'page': 1}, methods=['GET'])
@app.route('/api/project/log/<project>/<int:page>', methods=['GET'])
def api_project_log(project, page):
    ret = []
    filtering = {'_id': 0, 'api': 0}

    cursor = conn.get_api_collection_project().find({'project': project}, filtering)
    for item in cursor:
        ret.append({'commit': item['commit'], 'commit-date': item['commit-date'], 'meta': item['meta']})

    if len(ret) == 0:
        abort(404)

    return jsonify({'page': page, 'pages': 1, 'project': project, 'log': ret})


@app.route('/api/project/listing', defaults={'page': 1}, methods=['GET'])
@app.route('/api/project/listing/<int:page>', methods=['GET'])
def api_project_listing(page):
    ret = []
    filtering = {'commit': 0, '_id': 0, 'api': 0, 'meta': 0, 'commit-date': 0}

    cursor = conn.get_api_collection_project().find({}, filtering)
    for item in cursor:
        if item['project'] not in ret:
            ret.append(item['project'])

    return jsonify({'page': page, 'pages': 1, 'projects': ret})


@app.route('/api/package/api/<package>/<version>/<distro>', methods=['GET'])
def api_package_api(package, version, distro):
    ret = []
    filtering = {'_id': 0, 'version': 0, 'distro': distro, 'package': 0}

    cursor = conn.get_api_collection_package().find({'package': package, 'version': version, 'distro': distro}, filtering)
    for item in cursor:
        ret.append({'meta': item['meta'], 'api': item['api']})

    if len(ret) == 0:
        abort(404)

    return jsonify({'package': package, 'version': version, 'distro': distro, 'api': ret})


@app.route('/api/package/log/<package>', defaults={'page': 1}, methods=['GET'])
@app.route('/api/package/log/<package>/<int:page>', methods=['GET'])
def api_package_log(package, page):
    ret = []
    filtering = {'_id': 0, 'api': 0}

    cursor = conn.get_api_collection_package().find({'package': package}, filtering)
    for item in cursor:
        ret.append({'version': item['version'], 'distro': item['distro'], 'meta': item['meta']})

    if len(ret) == 0:
        abort(404)

    return jsonify({'page': page, 'pages': 1, 'package': package, 'log': ret})


@app.route('/api/project/listing', defaults={'page': 1}, methods=['GET'])
@app.route('/api/project/listing/<int:page>', methods=['GET'])
def api_package_listing(page):
    ret = []
    filtering = {'_id': 0, 'api': 0, 'meta': 0, 'version': 0, 'distro': 0}

    cursor = conn.get_api_collection_package().find({}, filtering)
    for item in cursor:
        if item['package'] not in ret:
            ret.append(item['package'])

    return jsonify({'page': page, 'pages': 1, 'packages': ret})


@app.route('/api/css/<path:path>')
def css(path):
    return send_from_directory('css', path)


@app.route('/api/js/<path:path>')
def js(path):
    return send_from_directory('js', path)


@app.route('/api/html/<path:path>')
def html(path):
    return send_from_directory('html', path)


@app.route('/api')
def index():
    return send_from_directory('html', 'index.html')


def print_help(progname):
    print >> sys.stderr, "Usage: %s --config CONFIG" % progname
    print >> sys.stderr, "API REST service"

if __name__ == '__main__':
    configfile = None
    dbg = DEFAULT_DEBUG

    if len(sys.argv) != 3:
        print >> sys.stderr, "Expecting one argument"
        print_help(sys.argv[0])
        sys.exit(1)

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'c:', ['config='])
    except getopt.GetoptError as e:
        print >> sys.stderr, "Error: %s" % str(e)
        print_help(sys.argv[0])
        sys.exit(1)

    for opt, arg in opts:
        if opt in ('-c', '--config'):
            configfile = arg

    if configfile is not None:
        if not os.path.isfile(configfile):
            raise ValueError("Invalid config file %s", (configfile,))

        conf = ConfigParser({
            'database-host': DEFAULT_DATABASE_HOST,
            'database-port': DEFAULT_DATABASE_PORT,
            'database-name': DEFAULT_DATABASE_NAME,
            'database-collection-project': DEFAULT_DATABASE_COLLECTION_PROJECT,
            'database-collection-package': DEFAULT_DATABASE_COLLECTION_PACKAGE,
            'debug': DEFAULT_DEBUG
        })
        conf.read(configfile)

        if conf.has_section(APP_NAME):
            db_host = conf.get(APP_NAME, 'database-host')
            db_port = conf.getint(APP_NAME, 'database-port')
            db_name = conf.get(APP_NAME, 'database-name')
            db_collection_name_project = conf.get(APP_NAME, 'database-collection-project')
            db_collection_name_package = conf.get(APP_NAME, 'database-collection-package')
            conn.init(db_host, db_port, db_name, db_collection_name_project, db_collection_name_package)
            dbg = conf.getboolean(APP_NAME, 'debug')
        else:
            raise ValueError("No section %s in config file" % (APP_NAME,))

    app.run(debug=dbg)

