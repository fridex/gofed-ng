#!/bin/python

from common.service.exposedClass import ExposedClass

class DBreader1(ExposedClass):
	def exposed_get_project_api(self, project, commit = None):
		return "local(exposed_get_project_api)"

	def exposed_get_project_dependencies(self, project, commit = None):
		return "local(exposed_get_project_dependencies)"
	pass

