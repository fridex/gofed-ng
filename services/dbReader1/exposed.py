#!/bin/python

from common.helpers.output import log
from common.service.service import Service
from common.database.dbReaderProjectAPI import DBreaderProjectAPI

class DBreader1(Service, DBreaderProjectAPI):
	def __init__(self, config):
		log.info("instantiated with config '%s'" % config)

	def exposed_get_project_api(self, project, commit = None):
		return "local(exposed_get_project_api)"

	def exposed_get_project_dependencies(self, project, commit = None):
		return "local(exposed_get_project_dependencies)"
	pass

